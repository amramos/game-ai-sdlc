"""Unit tests for playtest's blind_setup.py: python -m unittest discover -s scripts/tests"""

from __future__ import annotations

import contextlib
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
from unittest import mock

PACKAGE = Path(__file__).resolve().parents[2]
SCRIPT = PACKAGE / "plugins" / "game-sdlc" / "skills" / "playtest" / "scripts" / "blind_setup.py"

spec = importlib.util.spec_from_file_location("blind_setup", SCRIPT)
blind_setup = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(blind_setup)


class BlindSetupTests(unittest.TestCase):
    def setUp(self) -> None:
        work = tempfile.TemporaryDirectory()
        self.addCleanup(work.cleanup)
        self.root = Path(work.name).resolve()
        self.home = self.root / "home"
        (self.home / ".claude").mkdir(parents=True)
        (self.home / ".codex").mkdir()
        self.base = self.home / "playtests"
        self.build = self.root / "source" / "game.html"
        self.build.parent.mkdir()
        self.build.write_text("<p>game</p>", encoding="utf-8")
        # Only judge what this test put under its own root: the machine's real folders above the
        # system temp folder are not the test's to control.
        original = blind_setup.problems_above
        local = mock.patch.object(
            blind_setup, "problems_above",
            lambda folder, home: [p for p in original(folder, self.home) if str(self.root) in p],
        )
        local.start()
        self.addCleanup(local.stop)

    def run_main(self, *argv: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = blind_setup.main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def folder_from(self, out: str) -> Path:
        line = next(l for l in out.splitlines() if l.startswith("folder: "))
        return Path(line[len("folder: "):])

    def test_copies_only_the_build_and_the_save(self) -> None:
        save = self.root / "source" / "fresh.sav"
        save.write_text("{}", encoding="utf-8")
        (self.root / "source" / "AGENTS.md").write_text("secret design", encoding="utf-8")
        code, out, err = self.run_main(str(self.build), "--save", str(save), "--base", str(self.base))
        self.assertEqual(code, 0, err)
        folder = self.folder_from(out)
        self.assertEqual(sorted(p.name for p in folder.iterdir()), ["fresh.sav", "game.html"])
        self.assertIn("?blind", out)
        self.assertIn("tutorial=off", out)
        self.assertIn(f"save: {folder / 'fresh.sav'}", out)

    def test_page_gets_the_headless_runner_command(self) -> None:
        code, out, _ = self.run_main(str(self.build), "--base", str(self.base))
        self.assertEqual(code, 0)
        self.assertIn("proto_cli.mjs", out)
        self.assertIn("--no-tutorial", out)

    def test_fails_and_cleans_up_when_a_build_folder_carries_instructions(self) -> None:
        build = self.root / "export"
        (build / "docs").mkdir(parents=True)
        (build / "game.exe").write_bytes(b"")
        code, out, err = self.run_main(str(build), "--base", str(self.base))
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("docs", err)
        self.assertEqual(list(self.base.iterdir()), [])

    def test_fails_when_an_instruction_file_sits_above(self) -> None:
        project = self.home / "project"
        (project / "work").mkdir(parents=True)
        (project / "CLAUDE.md").write_text("design", encoding="utf-8")
        code, _, err = self.run_main(str(self.build), "--base", str(project / "work"))
        self.assertEqual(code, 1)
        self.assertIn("CLAUDE.md", err)
        self.assertEqual(list((project / "work").iterdir()), [])

    def test_names_are_matched_case_insensitively(self) -> None:
        folder = self.root / "inside"
        (folder / "build" / "Agents.MD").parent.mkdir(parents=True)
        (folder / "build" / "Agents.MD").write_text("", encoding="utf-8")
        self.assertEqual(len(blind_setup.problems_inside(folder)), 1)

    def test_home_config_folders_are_exempt_but_a_project_one_is_not(self) -> None:
        project = self.home / "project"
        (project / ".codex").mkdir(parents=True)
        (project / "work").mkdir()
        problems = blind_setup.problems_above(project / "work", self.home)
        self.assertEqual(len(problems), 1)
        self.assertIn(str(project / ".codex"), problems[0])

    def test_user_level_instructions_only_warn(self) -> None:
        (self.home / ".claude" / "CLAUDE.md").write_text("", encoding="utf-8")
        warnings = blind_setup.user_warnings(self.home)
        self.assertEqual(len(warnings), 1)
        self.assertIn("CLAUDE.md", warnings[0])

    def test_export_folder_with_one_executable_launches_it(self) -> None:
        build = self.root / "export"
        build.mkdir()
        (build / "game.exe").write_bytes(b"")
        (build / "game.pck").write_bytes(b"")
        code, out, _ = self.run_main(str(build), "--base", str(self.base))
        self.assertEqual(code, 0)
        folder = self.folder_from(out)
        self.assertIn(f'launch: "{folder / "export" / "game.exe"}"', out)

    def test_web_export_is_served(self) -> None:
        build = self.root / "web"
        build.mkdir()
        (build / "index.html").write_text("", encoding="utf-8")
        code, out, _ = self.run_main(str(build), "--base", str(self.base))
        self.assertEqual(code, 0)
        self.assertIn("http.server", out)
        self.assertIn("launch: http://localhost:8000/index.html", out)

    def test_missing_build_is_a_usage_error(self) -> None:
        with self.assertRaises(SystemExit) as raised, contextlib.redirect_stderr(io.StringIO()):
            blind_setup.main([str(self.root / "nope.html")])
        self.assertEqual(raised.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
