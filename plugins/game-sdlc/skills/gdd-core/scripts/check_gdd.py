"""Check a GDD's markers against the GDD template: the mechanical half of a GDD review.

    python check_gdd.py <GDD.md> [--template <gdd-template.md>]

Reads the template next to this skill for the rules, so the two never drift:
- the known markers are the bracketed words the template uses (`[BUILT]`, `[DESIGNED]`, `[OPEN]`);
- a top-level section (`## `) must carry a known marker in its heading when the template's section
  of the same number does. Sections the template leaves unmarked (the pitch, the glossary…) are
  matched by number, or by title when unnumbered, so a GDD in another language still checks;
- any other bracketed capital word (`[TBD]`, `[TODO]`) is an unknown marker.

It also lists every `[OPEN]` item with its section, and names the ones written inside the first
playable's section. The template doesn't mark the rest of the first playable's path, so which other
`[OPEN]` items sit on it stays the reviewer's call.

Exits 1 when a marker is missing or unknown, 0 otherwise. Standard library only.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from pathlib import Path
import re
import sys

TEMPLATE = Path(__file__).resolve().parents[1] / "gdd-template.md"
HEADING = re.compile(r"^##\s+(?:(\d+)\.\s*)?(.*?)\s*$")
BRACKETED = re.compile(r"\[([A-Z][A-Z_-]*[A-Z])\](?![(\[:])")
INLINE_CODE = re.compile(r"`[^`]*`")
FIRST_PLAYABLE = "first playable"


@dataclass
class Section:
    number: str | None
    title: str  # the heading without its number and markers
    line: int
    markers: list[str]
    body: list[tuple[int, str]] = field(default_factory=list)


def sections(text: str) -> list[Section]:
    found: list[Section] = []
    fenced = False
    for number, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith(("```", "~~~")):
            fenced = not fenced
            continue
        if fenced:
            continue
        match = HEADING.match(line) if line.startswith("## ") else None
        if match:
            heading = match.group(2)
            title = BRACKETED.sub("", heading).replace("**", "").strip(" *")
            found.append(Section(match.group(1), title, number, BRACKETED.findall(heading)))
        elif found:
            found[-1].body.append((number, line))
    return found


def template_rules(text: str) -> tuple[set[str], set[str], set[str]]:
    """The known markers, the section numbers that need one, and the titles of those that don't."""
    known = set(BRACKETED.findall(INLINE_CODE.sub("", text)))
    marked, unmarked_titles = set(), set()
    for section in sections(text):
        if section.markers:
            if section.number:
                marked.add(section.number)
        else:
            unmarked_titles.add(section.title.lower())
    return known, marked, unmarked_titles


def check(gdd: str, template: str) -> tuple[list[str], list[str]]:
    """Returns (problems, open items)."""
    known, marked, unmarked_titles = template_rules(template)
    problems: list[str] = []
    open_items: list[str] = []
    for section in sections(gdd):
        name = f"§{section.number} {section.title}" if section.number else section.title
        needs_marker = section.number in marked if section.number else section.title.lower() not in unmarked_titles
        for marker in section.markers:
            if marker not in known:
                problems.append(f"line {section.line}: {name}: unknown marker [{marker}]")
        if needs_marker and not any(m in known for m in section.markers):
            problems.append(f"line {section.line}: {name}: no marker; use one of "
                            + ", ".join(f"[{m}]" for m in sorted(known)))
        in_first_playable = FIRST_PLAYABLE in section.title.lower()
        heading_open = "OPEN" in section.markers
        for number, line in section.body:
            words = BRACKETED.findall(line)
            for marker in words:
                if marker not in known:
                    problems.append(f"line {number}: {name}: unknown marker [{marker}]")
            item = re.match(r"^\s*(?:\d+\.|[-*])\s+(.*)", line)
            if "OPEN" in words or (heading_open and item):
                where = " (in the first playable's section)" if in_first_playable else ""
                open_items.append(f"line {number}: {name}{where}: {line.strip()[:160]}")
    return problems, open_items


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("gdd", type=Path)
    parser.add_argument("--template", type=Path, default=TEMPLATE)
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # agents read it; Windows pipes default to a code page
    problems, open_items = check(args.gdd.read_text(encoding="utf-8"), args.template.read_text(encoding="utf-8"))
    for line in problems:
        print(f"PROBLEM: {line}")
    for line in open_items:
        print(f"OPEN: {line}")
    print(f"{len(problems)} marker problem(s), {len(open_items)} [OPEN] item(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
