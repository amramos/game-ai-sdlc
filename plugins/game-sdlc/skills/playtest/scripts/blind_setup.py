#!/usr/bin/env python3
"""Set up a folder for one blind playtester: only the build and a save, no project instructions.

An agent started inside a repository loads its instruction files and knows the design before it
plays. Run this once per playtester, start the playtester with the printed folder as its working
directory, and give it the printed launch command.

    python blind_setup.py prototypes/turn-based.html
    python blind_setup.py build/windows --save saves/fresh.cfg
    python blind_setup.py build/web --base D:/playtests

It makes an empty temporary folder, copies in only the build (a file or a folder) and the save,
then checks that no instruction file or folder (AGENTS.md, CLAUDE.md, .claude/, .codex/, .github/,
docs/) is inside it or in any folder above it. It prints `folder:` and `launch:` lines, exits 1 and
deletes the folder if a check fails. Standard library only.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import sys
import tempfile

# Names an agent client loads instructions or project context from. Compared case-insensitively,
# since Windows and macOS file systems are.
FORBIDDEN = ("agents.md", "claude.md", ".claude", ".codex", ".github", "docs")
# The clients' user-level config folders live in the home folder and load from anywhere, so moving
# the playtester can't avoid them; they're not a project's. Instruction files in them only warn.
USER_CONFIG = (".claude", ".codex")
USER_INSTRUCTIONS = (Path(".claude") / "CLAUDE.md", Path(".codex") / "AGENTS.md")
EXECUTABLE_SUFFIXES = {".exe", ".x86_64", ".x86_32", ".arm64", ".app", ".sh", ".bat", ".cmd"}
PROTO_CLI = Path(__file__).resolve().parents[2] / "prototype" / "scripts" / "proto_cli.mjs"


def problems_inside(folder: Path) -> list[str]:
    """Every forbidden name anywhere under the folder."""
    found = []
    for path in sorted(folder.rglob("*")):
        if path.name.lower() in FORBIDDEN:
            found.append(f"{path} is inside the playtest folder")
    return found


def problems_above(folder: Path, home: Path | None) -> list[str]:
    """Every forbidden name in a folder above, except the home folder's user-level config."""
    found = []
    for parent in folder.resolve().parents:
        try:
            entries = list(parent.iterdir())
        except OSError:
            continue
        for entry in entries:
            name = entry.name.lower()
            if name not in FORBIDDEN:
                continue
            if home is not None and parent == home and name in USER_CONFIG:
                continue
            found.append(f"{entry} is above the playtest folder")
    return found


def user_warnings(home: Path | None) -> list[str]:
    if home is None:
        return []
    return [
        f"{home / rel} loads in every folder; check it says nothing about this game"
        for rel in USER_INSTRUCTIONS
        if (home / rel).is_file()
    ]


def copy_in(source: Path, folder: Path) -> Path:
    target = folder / source.name
    if source.is_dir():
        shutil.copytree(source, target)
    else:
        shutil.copy2(source, target)
    return target


def quote(path: Path | str) -> str:
    return f'"{path}"'


def launch_lines(build: Path) -> list[str]:
    """How to start the build from the playtest folder, by kind of build."""
    if build.is_file() and build.suffix.lower() in {".html", ".htm"}:
        lines = [
            f"launch: {build.resolve().as_uri()}?blind",
            f"cold: {build.resolve().as_uri()}?blind&tutorial=off",
        ]
        if PROTO_CLI.is_file():
            lines += [
                f"headless: node {quote(PROTO_CLI)} {quote(build.name)}",
                f"headless-cold: node {quote(PROTO_CLI)} --no-tutorial {quote(build.name)}",
            ]
        return lines
    if build.is_dir() and (build / "index.html").is_file():
        # Web exports usually need to be served, not opened as a file.
        return [
            f"serve: {Path(sys.executable).name} -m http.server 8000 --directory {quote(build)}",
            "launch: http://localhost:8000/index.html",
        ]
    if build.is_dir():
        entries = [p for p in sorted(build.iterdir()) if is_executable(p)]
        if len(entries) == 1:
            return [f"launch: {quote(entries[0])}"]
        names = ", ".join(p.name for p in entries) or "none found"
        return [f"launch: run the game's executable in {quote(build)} (candidates: {names})"]
    return [f"launch: {quote(build)}"]


def is_executable(path: Path) -> bool:
    if not path.is_file() and path.suffix.lower() != ".app":
        return False
    if path.suffix.lower() in EXECUTABLE_SUFFIXES:
        return True
    return os.name != "nt" and path.suffix == "" and os.access(path, os.X_OK)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("build", type=Path, help="the build: a page, an executable or an export folder")
    parser.add_argument("--save", type=Path, help="a fresh save file or folder for this playtester")
    parser.add_argument("--base", type=Path, help="make the folder under this one instead of the system temp")
    args = parser.parse_args(argv)

    for given in (args.build, args.save):
        if given is not None and not given.exists():
            parser.error(f"{given} does not exist")
    if args.base is not None:
        args.base.mkdir(parents=True, exist_ok=True)

    folder = Path(tempfile.mkdtemp(prefix="blind-playtest-", dir=args.base)).resolve()
    build = copy_in(args.build, folder)
    save = copy_in(args.save, folder) if args.save is not None else None

    try:
        home: Path | None = Path.home().resolve()
    except RuntimeError:
        home = None
    problems = problems_inside(folder) + problems_above(folder, home)
    if problems:
        shutil.rmtree(folder, ignore_errors=True)
        for line in problems:
            print(f"blocked: {line}", file=sys.stderr)
        print("No playtest folder was left. Copy only the build, or pass --base to a folder outside "
              "any project.", file=sys.stderr)
        return 1

    print(f"folder: {folder}")
    for line in launch_lines(build):
        print(line)
    if save is not None:
        print(f"save: {save}")
    for line in user_warnings(home):
        print(f"warning: {line}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
