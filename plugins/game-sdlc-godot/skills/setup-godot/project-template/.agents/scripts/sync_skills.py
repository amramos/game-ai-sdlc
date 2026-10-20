"""Create deterministic Codex skill mirrors from canonical Claude skills."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys


BANNER_TEMPLATE = "> GENERATED MIRROR: edit `{source}`, then run `python3 .agents/scripts/sync_skills.py --write`.\n\n"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def inject_banner(text: str, source: str) -> str:
    if not text.startswith("---\n"):
        raise ValueError("SKILL.md must begin with YAML frontmatter")
    closing = text.find("\n---\n", 4)
    if closing < 0:
        raise ValueError("SKILL.md has no closing YAML frontmatter delimiter")
    insertion = closing + len("\n---\n")
    remainder = text[insertion:].lstrip("\n")
    return text[:insertion] + "\n" + BANNER_TEMPLATE.format(source=source) + remainder


def expected_files(root: Path) -> dict[Path, bytes]:
    source_root = root / ".claude" / "skills"
    target_root = root / ".agents" / "skills"
    expected: dict[Path, bytes] = {}
    if not source_root.is_dir():
        raise OSError(f"Missing canonical skill directory: {source_root}")
    for source in sorted(path for path in source_root.rglob("*") if path.is_file()):
        relative = source.relative_to(source_root)
        target = target_root / relative
        if source.name == "SKILL.md":
            text = source.read_text(encoding="utf-8").replace("\r\n", "\n")
            expected[target] = inject_banner(text, source.relative_to(root).as_posix()).encode("utf-8")
        else:
            expected[target] = source.read_bytes()
    return expected


def existing_files(root: Path) -> set[Path]:
    target_root = root / ".agents" / "skills"
    if not target_root.exists():
        return set()
    return {path for path in target_root.rglob("*") if path.is_file()}


def drift(root: Path, expected: dict[Path, bytes]) -> list[str]:
    problems: list[str] = []
    for path, content in expected.items():
        if not path.is_file() or path.read_bytes() != content:
            problems.append(f"stale: {path.relative_to(root).as_posix()}")
    for path in sorted(existing_files(root) - set(expected)):
        problems.append(f"unexpected: {path.relative_to(root).as_posix()}")
    return problems


def write(root: Path, expected: dict[Path, bytes]) -> None:
    target_root = root / ".agents" / "skills"
    for path in sorted(existing_files(root) - set(expected), reverse=True):
        path.unlink()
    for directory in sorted((path for path in target_root.rglob("*") if path.is_dir()), reverse=True):
        if not any(directory.iterdir()):
            directory.rmdir()
    for path, content in expected.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    args = parser.parse_args()
    root = repo_root()
    try:
        expected = expected_files(root)
        problems = drift(root, expected)
        if args.write:
            write(root, expected)
            print(f"Synchronized {len(expected)} skill file(s).")
            return 0
        if problems:
            print("Codex skill mirrors are out of sync:")
            for problem in problems:
                print(f"- {problem}")
            return 1
        print(f"Codex skill mirrors are in sync ({len(expected)} file(s)).")
        return 0
    except (UnicodeError, ValueError) as error:
        print(f"Invalid canonical skill source: {error}", file=sys.stderr)
        return 1
    except OSError as error:
        print(f"Skill synchronization could not run: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
