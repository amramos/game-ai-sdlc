"""Copy the Godot project template into a target folder, filling its {{PLACEHOLDERS}}.

    python instantiate.py --target <folder> --values values.json [--force]

values.json maps placeholder names (without braces) to text. Every placeholder found in the template
must have a value; the script lists the missing ones and stops before writing anything. Existing files
in the target are never overwritten unless --force is given; they are listed as skipped instead.
Standard library only.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

TEMPLATE = Path(__file__).resolve().parents[1] / "project-template"
PLACEHOLDER = re.compile(r"\{\{([A-Z0-9_]+)\}\}")
TEXT_SUFFIXES = {".md", ".gd", ".tscn", ".tres", ".godot", ".json", ".toml", ".yml", ".yaml", ".py", ".sh", ".cfg", ""}


def template_files() -> list[Path]:
    return sorted(
        path
        for path in TEMPLATE.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    )


def is_text(path: Path) -> bool:
    return path.suffix in TEXT_SUFFIXES or path.name.startswith(".")


def placeholders_in(files: list[Path]) -> set[str]:
    found: set[str] = set()
    for path in files:
        if is_text(path):
            found.update(PLACEHOLDER.findall(path.read_text(encoding="utf-8")))
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--target", required=True, type=Path)
    parser.add_argument("--values", required=True, type=Path)
    parser.add_argument("--force", action="store_true", help="overwrite files that already exist")
    args = parser.parse_args()

    values: dict[str, str] = json.loads(args.values.read_text(encoding="utf-8"))
    files = template_files()
    missing = sorted(placeholders_in(files) - set(values))
    if missing:
        print("Missing values for: " + ", ".join(missing))
        return 2

    written: list[str] = []
    skipped: list[str] = []
    for source in files:
        relative = source.relative_to(TEMPLATE)
        target = args.target / relative
        if target.exists() and not args.force:
            skipped.append(relative.as_posix())
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        if is_text(source):
            text = source.read_text(encoding="utf-8")
            text = PLACEHOLDER.sub(lambda match: values[match.group(1)], text)
            target.write_text(text, encoding="utf-8", newline="\n")
        else:
            target.write_bytes(source.read_bytes())
        written.append(relative.as_posix())

    print(f"written: {len(written)}")
    for name in skipped:
        print(f"skipped (exists): {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
