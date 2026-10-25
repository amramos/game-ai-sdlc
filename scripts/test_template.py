"""Instantiate the Godot project template into a temporary folder and run its own checks.

    python scripts/test_template.py [--keep]

Proves that setup-godot's template fills every placeholder, that its hooks' tests pass in a fresh
project, that its Codex skill mirrors are in sync, and that its windowed-run lock holds a second run
back. Godot itself isn't needed (GUT is installed by the setup skill, not shipped in the template).
Standard library only.
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
import time

PACKAGE = Path(__file__).resolve().parents[1]
SETUP = PACKAGE / "plugins" / "game-sdlc-godot" / "skills" / "setup-godot"
# Same shape instantiate.py fills; GitHub Actions expressions (${{ ... }}) are not placeholders.
PLACEHOLDER = re.compile(r"\{\{[A-Z0-9_]+\}\}")

SAMPLE_VALUES = {
    "GAME_TITLE": "Sample Game",
    "PITCH": "A sample game used to test the setup template.",
    "PILLARS": (
        "1. **Every turn costs something.** Each action spends a resource the player needs later."
        " *Test: could the player do this without giving something up?*\n"
        "2. **The sea remembers.** What the player leaves behind comes back. *Test: does this outlast"
        " the moment it happens in?*\n"
        "3. **Read at a glance.** The board shows its state without opening anything. *Test: can a"
        " player see this without reading?*"
    ),
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
    "GUT_BASELINE": "6/6 across 3 scripts",
    "GUT_VERSION": "9.x",
    "PROJECT_SLUG": "sample_game",
    "WORKING_STYLE": "The owner works **hands-off**.",
    "AGENT_MERGES_RULE": "Only the owner merges into `main`.",
}


def run(command: list[str], cwd: Path) -> None:
    print("$ " + " ".join(command), flush=True)
    result = subprocess.run(command, cwd=cwd)
    if result.returncode != 0:
        raise SystemExit(f"failed ({result.returncode}): {' '.join(command)}")


def check_window_lock(project: Path) -> None:
    """A second windowed run waits for the first, and gives up with 75 when its timeout runs out."""
    wrapper = [sys.executable, "tools/windowed_run.py"]
    lock = project / ".agents" / "local" / "windowed-run.lock"
    run([*wrapper, "--", sys.executable, "-c", "pass"], project)
    holder = subprocess.Popen([*wrapper, "--", sys.executable, "-c", "import time; time.sleep(5)"], cwd=project)
    try:
        deadline = time.monotonic() + 10
        while not (lock.is_file() and lock.read_text(encoding="utf-8").strip()):
            if time.monotonic() > deadline or holder.poll() is not None:
                raise SystemExit("the windowed-run lock was never taken")
            time.sleep(0.1)
        waiter = subprocess.run([*wrapper, "--timeout", "0.5", "--", sys.executable, "-c", "pass"], cwd=project)
        if waiter.returncode != 75:
            raise SystemExit(f"a second windowed run got through while the lock was held ({waiter.returncode})")
    finally:
        holder.wait()
    run([*wrapper, "--timeout", "5", "--", sys.executable, "-c", "pass"], project)
    print("window lock OK")


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
        run([sys.executable, "-m", "py_compile", "tools/ci/export_all.py", "tools/windowed_run.py"], project)
        check_window_lock(project)
        print(f"template OK ({sum(1 for p in project.rglob('*') if p.is_file())} files)")
        if args.keep:
            print(f"kept: {project}")
        return 0
    finally:
        if not args.keep:
            shutil.rmtree(workdir, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
