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
# What must never ship in a public package: personal email addresses and absolute paths into a
# user's folders. Private words (names from the project this was extracted from, for example) go in
# scripts/leftovers.local.txt, one regex per line; that file is git-ignored, so the list stays private.
LEFTOVERS = [
    re.compile(
        # Not GitHub's no-reply addresses, the commit trailers' address, or the reserved example domains.
        r"[A-Za-z0-9._%+-]+@(?!users\.noreply\.github\.com\b|anthropic\.com\b|example\.(?:com|org|net)\b)"
        r"[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}"
    ),
    re.compile(r"\b[A-Za-z]:[\\/]+Users[\\/]+[^\\/\s]+|/(?:c/Users|home|Users)/[A-Za-z0-9._-]+/"),
]
LOCAL_LEFTOVERS = PACKAGE / "scripts" / "leftovers.local.txt"
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
    leftovers = list(LEFTOVERS)
    if LOCAL_LEFTOVERS.is_file():
        for line in LOCAL_LEFTOVERS.read_text(encoding="utf-8").splitlines():
            if line.strip() and not line.startswith("#"):
                leftovers.append(re.compile(line.strip()))

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
        # The version lives in plugin.json only: if the marketplace entry also sets one, plugin.json
        # wins silently, and the two drift.
        if "version" in plugin:
            problems.append(f"{plugin['name']}: set version in plugin.json only, not in the marketplace entry")
        if not data.get("version"):
            problems.append(f"{plugin['name']}: plugin.json has no version, so users only update by commit")
        elif data["version"] != marketplace.get("metadata", {}).get("version"):
            problems.append(f"{plugin['name']}: plugin.json version differs from the marketplace's metadata.version")

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
        if path.name != "check_package.py" and path.name != LOCAL_LEFTOVERS.name:
            for pattern in leftovers:
                for match in pattern.finditer(text):
                    problems.append(f"{rel}: must not be published: {match.group(0)!r}")
        mentions_placeholders = "{{" in text.replace("{{PLACEHOLDERS}}", "")
        if TEMPLATE_MARK not in path.parts and mentions_placeholders and path.suffix in {".md", ".json"}:
            if "template" not in path.name and "agent-merges/" not in rel:
                problems.append(f"{rel}: unfilled {{{{placeholder}}}} outside the project template")
        if path.suffix == ".md" and TEMPLATE_MARK not in path.parts:
            for target in LINK.findall(text):
                if "://" in target or target.startswith("mailto:"):
                    continue
                if not (path.parent / target).exists():
                    problems.append(f"{rel}: broken link {target}")

    # The agent-merges ADR ships in two plugins (setup-godot writes it on day one, team-lead-handsoff
    # when it's missing); the two copies must stay identical.
    copies = [
        PACKAGE / "plugins/game-sdlc/skills/team-lead-handsoff/agent-merges-adr-template.md",
        PACKAGE / "plugins/game-sdlc-godot/skills/setup-godot/agent-merges/agent-merges-adr-template.md",
    ]
    if len({copy.read_bytes() for copy in copies if copy.is_file()}) != 1 or not all(c.is_file() for c in copies):
        problems.append("the two agent-merges ADR templates are missing or differ; keep them identical")

    for line in problems:
        print(line)
    print(f"{len(names)} skills checked; {len(problems)} problem(s).")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
