"""Instantiate the Godot project template into a temporary folder and run its own checks.

    python scripts/test_template.py [--keep]

Proves that setup-godot's template fills every placeholder, that its hooks' tests pass in a fresh
project, and that its Codex skill mirrors are in sync. Godot itself isn't needed (GUT is installed by
the setup skill, not shipped in the template). Standard library only.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

PACKAGE = Path(__file__).resolve().parents[1]
SETUP = PACKAGE / "plugins" / "game-sdlc-godot" / "skills" / "setup-godot"
# Same shape instantiate.py fills; GitHub Actions expressions (${{ ... }}) are not placeholders.
PLACEHOLDER = re.compile(r"\{\{[A-Z0-9_]+\}\}")

SAMPLE_VALUES = {
    "GAME_TITLE": "Sample Game",
    "PITCH": "A sample game used to test the setup template.",
    "GLOSSARY": "| Term | Meaning |\n|---|---|\n| **Turn** | One step of play. |",
    "PLATFORMS": "desktop (Windows, Linux, macOS) and web, through itch.io",
    "INPUT_RULE": "mouse and keyboard",
    "INPUT_RULE_DETAIL": "Every interaction works with mouse and keyboard.",
    "GODOT_VERSION": "4.5.1",
    "GODOT_FEATURE": "4.5",
    "RENDERER_FEATURE": "GL Compatibility",
    "RENDERING_METHOD": "gl_compatibility",
    "DATE": "2026-10-20",
    "NEXT_STEP": "art-direction, then feature-planning for the core loop",
    "GUT_BASELINE": "1/1 across 1 script",
    "GUT_VERSION": "9.x",
    "PROJECT_SLUG": "sample_game",
    "WORKING_STYLE": "The owner works **hands-off**.",
}


def run(command: list[str], cwd: Path) -> None:
    print("$ " + " ".join(command), flush=True)
    result = subprocess.run(command, cwd=cwd)
    if result.returncode != 0:
        raise SystemExit(f"failed ({result.returncode}): {' '.join(command)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--keep", action="store_true", help="keep the generated project and print its path")
    args = parser.parse_args()

    workdir = Path(tempfile.mkdtemp(prefix="game-sdlc-template-"))
    try:
        values = workdir / "values.json"
        values.write_text(json.dumps(SAMPLE_VALUES), encoding="utf-8")
        project = workdir / "project"
        run([sys.executable, str(SETUP / "scripts" / "instantiate.py"), "--target", str(project), "--values", str(values)], PACKAGE)

        leftovers = [
            p.relative_to(project).as_posix()
            for p in project.rglob("*")
            if p.is_file() and p.suffix != ".pyc" and PLACEHOLDER.search(p.read_text(encoding="utf-8", errors="ignore"))
        ]
        if leftovers:
            raise SystemExit("unfilled placeholders in: " + ", ".join(leftovers))

        run(["git", "init", "-q", "-b", "setup/project-foundation"], project)
        run([sys.executable, "-m", "unittest", "discover", "-s", ".agents/tests"], project)
        run([sys.executable, ".agents/scripts/sync_skills.py", "--check"], project)
        run([sys.executable, "-m", "py_compile", "tools/ci/export_all.py"], project)
        print(f"template OK ({sum(1 for p in project.rglob('*') if p.is_file())} files)")
        if args.keep:
            print(f"kept: {project}")
        return 0
    finally:
        if not args.keep:
            shutil.rmtree(workdir, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
