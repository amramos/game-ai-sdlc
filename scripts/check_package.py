"""Check the package before publishing: manifests, skill frontmatter, links, and leftovers.

    python scripts/check_package.py

Exits 1 with a list of problems, 0 when clean. Standard library only.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys

PACKAGE = Path(__file__).resolve().parents[1]
TEMPLATE_MARK = "project-template"
# Words that only made sense in the project this package was extracted from.
LEFTOVERS = re.compile(
    r"Skeleton Crew|skeleton-crew|Old Finn|\bSK-\d|voyage|Voyage|Shanty|ADR-00(?:[6-9]\d)|gpt-6|gpt-5|"
    r"murph|opencode",
)
LINK = re.compile(r"\]\(([^)#\s]+)\)")
KNOWN_KEYS = {"name", "description", "argument-hint", "disable-model-invocation", "user-invocable",
              "allowed-tools", "model", "tools", "effort"}


def frontmatter(text: str) -> dict[str, str] | None:
    text = text.replace("\r\n", "\n")
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end < 0:
        return None
    fields: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" in line and not line.startswith(" "):
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
    return fields


def main() -> int:
    problems: list[str] = []

    marketplace = json.loads((PACKAGE / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    for plugin in marketplace["plugins"]:
        root = PACKAGE / plugin["source"]
        manifest = root / ".claude-plugin" / "plugin.json"
        if not manifest.is_file():
            problems.append(f"{plugin['name']}: missing {manifest.relative_to(PACKAGE)}")
            continue
        data = json.loads(manifest.read_text(encoding="utf-8"))
        if data.get("name") != plugin["name"]:
            problems.append(f"{plugin['name']}: plugin.json name is {data.get('name')!r}")
        if data.get("version") != plugin.get("version"):
            problems.append(f"{plugin['name']}: version differs between marketplace and plugin.json")

    names: set[str] = set()
    for skill_md in sorted(PACKAGE.glob("plugins/*/skills/*/SKILL.md")):
        rel = skill_md.relative_to(PACKAGE).as_posix()
        fields = frontmatter(skill_md.read_text(encoding="utf-8"))
        if fields is None:
            problems.append(f"{rel}: no frontmatter")
            continue
        if fields.get("name") != skill_md.parent.name:
            problems.append(f"{rel}: name {fields.get('name')!r} doesn't match its folder")
        if fields.get("name") in names:
            problems.append(f"{rel}: duplicate skill name")
        names.add(fields.get("name", ""))
        description = fields.get("description", "")
        if not description or len(description) > 1024:
            problems.append(f"{rel}: description missing or over 1024 characters ({len(description)})")
        for key in set(fields) - KNOWN_KEYS:
            problems.append(f"{rel}: unknown frontmatter key {key!r}")

    for agent in sorted(PACKAGE.glob("plugins/*/agents/*.md")):
        fields = frontmatter(agent.read_text(encoding="utf-8"))
        if not fields or fields.get("name") != agent.stem or not fields.get("description"):
            problems.append(f"{agent.relative_to(PACKAGE).as_posix()}: bad agent frontmatter")

    for path in sorted(PACKAGE.rglob("*")):
        if not path.is_file() or ".git" in path.parts or "__pycache__" in path.parts:
            continue
        if path.suffix not in {".md", ".json", ".yml", ".py", ".toml", ".html", ".gd", ".tscn", ".sh"}:
            continue
        rel = path.relative_to(PACKAGE).as_posix()
        text = path.read_text(encoding="utf-8")
        if path.name != "check_package.py":
            for match in LEFTOVERS.finditer(text):
                problems.append(f"{rel}: leftover from the source project: {match.group(0)!r}")
        mentions_placeholders = "{{" in text.replace("{{PLACEHOLDERS}}", "")
        if TEMPLATE_MARK not in path.parts and mentions_placeholders and path.suffix in {".md", ".json"}:
            if "gdd-template" not in rel and "ledger-template" not in rel:
                problems.append(f"{rel}: unfilled {{{{placeholder}}}} outside the project template")
        if path.suffix == ".md" and TEMPLATE_MARK not in path.parts:
            for target in LINK.findall(text):
                if "://" in target or target.startswith("mailto:"):
                    continue
                if not (path.parent / target).exists():
                    problems.append(f"{rel}: broken link {target}")

    for line in problems:
        print(line)
    print(f"{len(names)} skills checked; {len(problems)} problem(s).")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
