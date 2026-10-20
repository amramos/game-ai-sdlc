"""Copy this package's skills into Codex's user skill folder (~/.codex/skills by default).

Codex doesn't install Claude Code plugins, so this mirrors every plugins/*/skills/<name>/ folder into
<target>/<name>/, adds a generated banner after each SKILL.md's frontmatter, and drops a marker file so
later runs only ever update or remove folders this script created.

    python scripts/install_codex.py            # install or update
    python scripts/install_codex.py --check    # exit 1 if anything is missing or stale
    python scripts/install_codex.py --remove   # remove what this script installed
    python scripts/install_codex.py --dry-run  # show what would change

Standard library only.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys

PACKAGE = Path(__file__).resolve().parents[1]
MARKER = ".installed-by-game-sdlc"
BANNER = "> Installed from the game-sdlc package (`{source}`); re-run `scripts/install_codex.py` to update.\n\n"


def with_banner(text: str, source: str) -> str:
    text = text.replace("\r\n", "\n")
    if not text.startswith("---\n"):
        raise ValueError(f"{source}: SKILL.md must begin with YAML frontmatter")
    closing = text.find("\n---\n", 4)
    if closing < 0:
        raise ValueError(f"{source}: no closing frontmatter delimiter")
    cut = closing + len("\n---\n")
    return text[:cut] + "\n" + BANNER.format(source=source) + text[cut:].lstrip("\n")


def skill_sources() -> dict[str, Path]:
    sources: dict[str, Path] = {}
    for skill_md in sorted(PACKAGE.glob("plugins/*/skills/*/SKILL.md")):
        folder = skill_md.parent
        if folder.name in sources:
            raise ValueError(f"two skills named {folder.name}: {sources[folder.name]} and {folder}")
        sources[folder.name] = folder
    return sources


def expected_files(name: str, folder: Path) -> dict[Path, bytes]:
    files: dict[Path, bytes] = {}
    for path in sorted(p for p in folder.rglob("*") if p.is_file() and "__pycache__" not in p.parts):
        relative = path.relative_to(folder)
        if path.name == "SKILL.md" and len(relative.parts) == 1:
            source = path.relative_to(PACKAGE).as_posix()
            files[relative] = with_banner(path.read_text(encoding="utf-8"), source).encode("utf-8")
        else:
            files[relative] = path.read_bytes()
    files[Path(MARKER)] = f"{name}\n".encode("utf-8")
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--target", type=Path, default=Path.home() / ".codex" / "skills")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--remove", action="store_true")
    mode.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    sources = skill_sources()
    problems: list[str] = []
    for name, folder in sources.items():
        destination = args.target / name
        if destination.exists() and not (destination / MARKER).exists():
            problems.append(f"skip {name}: {destination} exists and wasn't installed by this script")
            continue
        if args.remove:
            if destination.exists():
                print(f"remove {destination}")
                if not args.dry_run:
                    shutil.rmtree(destination)
            continue
        wanted = expected_files(name, folder)
        stale = [rel for rel, data in wanted.items() if not (destination / rel).is_file() or (destination / rel).read_bytes() != data]
        extra = []
        if destination.exists():
            present = {p.relative_to(destination) for p in destination.rglob("*") if p.is_file()}
            extra = sorted(present - set(wanted))
        if not stale and not extra:
            continue
        if args.check:
            problems.append(f"out of date: {name} ({len(stale)} changed, {len(extra)} extra)")
            continue
        print(f"{'would update' if args.dry_run else 'update'} {name}")
        if args.dry_run:
            continue
        for rel in extra:
            (destination / rel).unlink()
        for rel, data in wanted.items():
            (destination / rel).parent.mkdir(parents=True, exist_ok=True)
            (destination / rel).write_bytes(data)

    for line in problems:
        print(line)
    if args.check:
        if problems:
            return 1
        print(f"{len(sources)} skills in sync under {args.target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
