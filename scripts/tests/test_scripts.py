"""Unit tests for the package's own scripts: python -m unittest discover -s scripts/tests"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parents[2]
TEMPLATE = PACKAGE / "plugins" / "game-sdlc-godot" / "skills" / "setup-godot"


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


export_all = load("export_all", TEMPLATE / "project-template" / "tools" / "ci" / "export_all.py")
install_codex = load("install_codex", PACKAGE / "scripts" / "install_codex.py")

PRESETS = """[preset.0]

name="Windows Desktop"
platform="Windows Desktop"
runnable=true
export_path=""

[preset.0.options]

custom_template/debug=""

[preset.1]

name="My Web Build"
platform="Web"
runnable=true

[preset.1.options]

html/export_icon=true
"""


class ExportAllTests(unittest.TestCase):
    def test_reads_every_preset_name_and_platform_in_order(self) -> None:
        self.assertEqual(
            export_all.presets(PRESETS),
            [("Windows Desktop", "Windows Desktop"), ("My Web Build", "Web")],
        )

    def test_slug_comes_from_the_project_name(self) -> None:
        self.assertEqual(export_all.project_slug('config/name="The Lost Fleet!"\n'), "the_lost_fleet")
        self.assertEqual(export_all.project_slug("no name here\n"), "game")


class InstallCodexTests(unittest.TestCase):
    def test_banner_goes_after_the_frontmatter(self) -> None:
        text = install_codex.with_banner("---\nname: x\n---\n\n# Title\n", "plugins/p/skills/x/SKILL.md")
        self.assertTrue(text.startswith("---\nname: x\n---\n\n> Installed from the game-sdlc package"))
        self.assertTrue(text.endswith("# Title\n"))

    def test_every_skill_name_is_unique_across_plugins(self) -> None:
        names = list(install_codex.skill_sources())
        self.assertEqual(len(names), len(set(names)))
        self.assertIn("gdd", names)
        self.assertIn("setup-godot", names)

    def test_install_check_and_remove_round_trip(self) -> None:
        script = PACKAGE / "scripts" / "install_codex.py"
        with tempfile.TemporaryDirectory() as target:
            run = lambda *extra: subprocess.run(  # noqa: E731
                [sys.executable, str(script), "--target", target, *extra], capture_output=True, text=True
            )
            self.assertEqual(run("--check").returncode, 1)
            self.assertEqual(run().returncode, 0)
            self.assertEqual(run("--check").returncode, 0)
            foreign = Path(target) / "someone-elses-skill"
            foreign.mkdir()
            self.assertEqual(run("--remove").returncode, 0)
            self.assertEqual(sorted(p.name for p in Path(target).iterdir()), ["someone-elses-skill"])


class InstantiateTests(unittest.TestCase):
    def test_refuses_to_write_when_a_value_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as work:
            values = Path(work) / "values.json"
            values.write_text(json.dumps({"GAME_TITLE": "Only this"}), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(TEMPLATE / "scripts" / "instantiate.py"), "--target", str(Path(work) / "out"),
                 "--values", str(values)],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("Missing values for", result.stdout)
            self.assertFalse((Path(work) / "out").exists())


if __name__ == "__main__":
    unittest.main()
