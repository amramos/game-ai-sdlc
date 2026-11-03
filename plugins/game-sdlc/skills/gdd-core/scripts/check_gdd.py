"""Check a GDD against the GDD template: the mechanical half of a GDD review.

    python check_gdd.py <GDD.md> [--template <gdd-template.md>]
    python check_gdd.py <GDD.md> --handsoff [--owner-picked] [--summary <GDD-summary.md>]

Reads the template next to this skill for the rules, so the two never drift:
- the known markers are the bracketed words the template uses (`[BUILT]`, `[DESIGNED]`, `[OPEN]`);
- a top-level section (`## `) must carry a known marker in its heading when the template's section
  of the same number does. Sections the template leaves unmarked (the pitch, the glossary…) are
  matched by number, or by title when unnumbered, so a GDD in another language still checks;
- any other bracketed capital word (`[TBD]`, `[TODO]`) is an unknown marker;
- every numbered section of the template is there and not empty;
- an `[OPEN]` written outside the open-questions section points at its item there (`§14`), and each
  item there gives options and a recommendation;
- every subsection of the mechanics section has a `*Check:*` line, except the ones the template
  gives none (when rules meet).

It also lists every `[OPEN]` item with its section, and names the ones written inside the first
playable's section. Which other `[OPEN]` items sit on the first playable's path stays the reviewer's
call.

--handsoff adds what gdd-handsoff §6 asks of a provisional GDD:
- the Provisional line above the first section;
- the appendix of assumed decisions lists only `panel — assumed` and `panel — assumed (profile)`
  decisions, each as `**A<n>**` with its section and a runner-up;
- the identity decisions are among them: tone (§7) and the interface (§9), and the pitch, hook and
  pillars (§1) and the art, camera and medium (§8) unless the owner picked the concept
  (--owner-picked);
- no pillar line carries a `(profile)` addition;
- the platform and business section cites the research behind its price model (a link).

--summary also checks GDD-summary.md: its eight parts in order, up to five other assumed decisions
cited by appendix id with their runner-ups (fewer only when the appendix has no more), three kill
list items, and the closing question word for word.

Exits 1 on any problem, 0 otherwise. Standard library only.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from pathlib import Path
import re
import sys

TEMPLATE = Path(__file__).resolve().parents[1] / "gdd-template.md"
HEADING = re.compile(r"^##\s+(?:(\d+)\.\s*)?(.*?)\s*$")
SUBHEADING = re.compile(r"^###\s+(?:[\d.<>N]+\s+)?(.*?)\s*$")
BRACKETED = re.compile(r"\[([A-Z][A-Z_-]*[A-Z])\](?![(\[:])")
INLINE_CODE = re.compile(r"`[^`]*`")
COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
CHECK = re.compile(r"\*Check:\*")
ITEM = re.compile(r"^\s*(?:\d+\.|[-*])\s+(.*)")
SECTION_REF = re.compile(r"§\s*(\d+)")
ASSUMED = re.compile(r"panel\s*[—–-]+\s*assumed", re.IGNORECASE)
RUNNER_UP = re.compile(r"runner-up:?\**\s*\S", re.IGNORECASE)
APPENDIX_ID = re.compile(r"\*\*(A\d+)\*\*")
CITED_ID = re.compile(r"\bA\d+\b")
OPTIONS = re.compile(r"\boption|\bopci|\bopç", re.IGNORECASE)
RECOMMENDATION = re.compile(r"recom", re.IGNORECASE)
FIRST_PLAYABLE = "first playable"
CLOSING_QUESTION = ("Change any of these, or continue to setup-godot with every recommendation (the project "
                    "will run hands-off)?")
SUMMARY_PARTS = ("the pitch", "the pillars", "the camera and medium", "the other assumed decisions",
                 "the housekeeping baseline", "the playtesters' verdict", "the reviewer's kill list",
                 "the closing question")
# Identity decisions (gdd-handsoff §3) by the template section that holds them; the first two are the
# concept's, which the owner settles by picking it.
CONCEPT_IDENTITY = {"1": "the pitch, hook and pillars", "8": "the art, camera and medium"}
OTHER_IDENTITY = {"7": "tone", "9": "the interface"}


@dataclass
class Section:
    number: str | None
    title: str  # the heading without its number and markers
    line: int
    markers: list[str]
    body: list[tuple[int, str]] = field(default_factory=list)

    @property
    def name(self) -> str:
        return f"§{self.number} {self.title}" if self.number else self.title

    def text(self) -> str:
        return COMMENT.sub("", "\n".join(line for _, line in self.body))

    def subsections(self) -> list[tuple[int, str, list[tuple[int, str]]]]:
        """(line, title, body) for each `### ` heading in the section."""
        found: list[tuple[int, str, list[tuple[int, str]]]] = []
        for number, line in self.body:
            match = SUBHEADING.match(line) if line.startswith("### ") else None
            if match:
                found.append((number, match.group(1), []))
            elif found:
                found[-1][2].append((number, line))
        return found


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


@dataclass
class Rules:
    known: set[str]  # the markers
    marked: set[str]  # section numbers whose heading needs a marker
    unmarked_titles: set[str]  # titles of the unnumbered sections that need none
    numbered: dict[str, str]  # every numbered section: number -> title
    open_section: str | None  # the open-questions section's number
    mechanics: str | None  # the section whose subsections need a check line
    unchecked: set[str]  # titles of the subsections there that need none


def template_rules(text: str) -> Rules:
    rules = Rules(set(BRACKETED.findall(INLINE_CODE.sub("", text))), set(), set(), {}, None, None, set())
    for section in sections(text):
        if section.number:
            rules.numbered[section.number] = section.title
        if section.markers:
            if section.number:
                rules.marked.add(section.number)
            if "OPEN" in section.markers:
                rules.open_section = section.number
        else:
            rules.unmarked_titles.add(section.title.lower())
        subs = section.subsections()
        if any(CHECK.search(line) for _, _, body in subs for _, line in body):
            rules.mechanics = section.number
            rules.unchecked = {title.lower() for _, title, body in subs
                               if not any(CHECK.search(line) for _, line in body)}
    return rules


def is_empty(section: Section) -> bool:
    return not any(line.strip() and line.strip() != "---" for line in section.text().splitlines())


def check(gdd: str, template: str, handsoff: bool = False, owner_picked: bool = False) -> tuple[list[str], list[str]]:
    """Returns (problems, open items)."""
    rules = template_rules(template)
    known = rules.known
    problems: list[str] = []
    open_items: list[str] = []
    found = sections(gdd)
    by_number = {s.number: s for s in found if s.number}
    for number, title in rules.numbered.items():
        if number not in by_number:
            problems.append(f"§{number} {title}: missing; every section of the template is written")
    for section in found:
        name = section.name
        needs_marker = (section.number in rules.marked if section.number
                        else section.title.lower() not in rules.unmarked_titles)
        for marker in section.markers:
            if marker not in known:
                problems.append(f"line {section.line}: {name}: unknown marker [{marker}]")
        if needs_marker and not any(m in known for m in section.markers):
            problems.append(f"line {section.line}: {name}: no marker; use one of "
                            + ", ".join(f"[{m}]" for m in sorted(known)))
        if section.number in rules.numbered and is_empty(section):
            problems.append(f"line {section.line}: {name}: empty")
        in_first_playable = FIRST_PLAYABLE in section.title.lower()
        heading_open = "OPEN" in section.markers
        in_open_section = section.number is not None and section.number == rules.open_section
        for number, line in section.body:
            words = BRACKETED.findall(line)
            for marker in words:
                if marker not in known:
                    problems.append(f"line {number}: {name}: unknown marker [{marker}]")
            item = ITEM.match(line)
            if "OPEN" in words or (heading_open and item):
                where = " (in the first playable's section)" if in_first_playable else ""
                open_items.append(f"line {number}: {name}{where}: {line.strip()[:160]}")
            if "OPEN" in words and not in_open_section and rules.open_section and \
                    f"§{rules.open_section}" not in line.replace("§ ", "§"):
                problems.append(f"line {number}: {name}: [OPEN] with no item in §{rules.open_section}; add it there "
                                f"with options and a recommendation, and point at it here (§{rules.open_section}, item n)")
            if in_open_section and item and line[:1].isdigit() and not (OPTIONS.search(line) and RECOMMENDATION.search(line)):
                problems.append(f"line {number}: {name}: an open question gives its options and a recommendation")
        if section.number and section.number == rules.mechanics:
            for line, title, body in section.subsections():
                if title.lower() not in rules.unchecked and not any(CHECK.search(text) for _, text in body):
                    problems.append(f"line {line}: {name}: {title}: no *Check:* line; say the move or decision it "
                                    "adds and the test that shows it")
    if handsoff:
        problems += check_handsoff(gdd, found, rules, owner_picked)
    return problems, open_items


def appendix_of(found: list[Section]) -> Section | None:
    for section in found:
        if not section.number and ("assumed" in section.title.lower() or section.title.lower().startswith("appendix")):
            return section
    return None


def appendix_entries(appendix: Section) -> list[tuple[int, str]]:
    return [(number, line) for number, line in appendix.body if ITEM.match(COMMENT.sub("", line))]


def check_handsoff(gdd: str, found: list[Section], rules: Rules, owner_picked: bool) -> list[str]:
    problems: list[str] = []
    before_first = gdd.split("\n## ", 1)[0]
    if not re.search(r"\*\*Provisional", COMMENT.sub("", before_first), re.IGNORECASE):
        problems.append("no **Provisional** line under the title (gdd-handsoff §6)")
    appendix = appendix_of(found)
    cited_sections: set[str] = set()
    if appendix is None:
        problems.append("no Appendix: Assumed by the panel (gdd-handsoff §6)")
    else:
        seen: set[str] = set()
        no_id: list[str] = []
        for number, line in appendix_entries(appendix):
            where = f"line {number}: appendix"
            ids = APPENDIX_ID.findall(line)
            if not ids:
                no_id.append(str(number))
            elif ids[0] in seen:
                problems.append(f"{where}: {ids[0]} is used twice")
            seen.update(ids[:1])
            if not ASSUMED.search(line):
                problems.append(f"{where}: not an assumed decision; the appendix lists only `panel — assumed` ones, "
                                "so a plain `panel` decision stays in its section only")
                continue
            if not RUNNER_UP.search(line):
                problems.append(f"{where}: no runner-up")
            cited_sections.update(SECTION_REF.findall(line))
        if no_id:
            problems.append(f"appendix: start each line with its id, **A1**, **A2**… (lines {', '.join(no_id)})")
        identity = dict(OTHER_IDENTITY) if owner_picked else {**CONCEPT_IDENTITY, **OTHER_IDENTITY}
        for number, what in sorted(identity.items(), key=lambda item: int(item[0])):
            if number in rules.numbered and number not in cited_sections:
                problems.append(f"appendix: no assumed decision on {what} (§{number}); it's an identity decision "
                                "(gdd-handsoff §3)")
    by_number = {s.number: s for s in found if s.number}
    pitch = by_number.get("1")
    if pitch:
        for line, title, body in pitch.subsections():
            for number, text in body:
                if "(profile)" in text:
                    problems.append(f"line {number}: §1 {title}: a `(profile)` addition never edits a pillar; "
                                    "put it in its own section as a game change")
    business = by_number.get("10")
    if business and "http" not in business.text():
        problems.append(f"line {business.line}: {business.name}: the price model is a market question; cite the "
                        "research that set it (a link)")
    return problems


def normalized(text: str) -> str:
    return " ".join(re.sub(r"[*_`]", "", text).split())


def check_summary(summary: str, gdd: str) -> list[str]:
    problems: list[str] = []
    parts = sections(summary)
    appendix = appendix_of(sections(gdd))
    known_ids = set()
    if appendix is not None:
        for _, line in appendix_entries(appendix):
            if ASSUMED.search(line):
                known_ids.update(APPENDIX_ID.findall(line)[:1])
    if len(parts) < len(SUMMARY_PARTS):
        problems.append(f"summary: {len(parts)} part(s) (## headings); gdd-handsoff §6 lists eight, in order: "
                        + "; ".join(SUMMARY_PARTS))
        return problems
    assumed = parts[3]
    cited = CITED_ID.findall(assumed.text())
    for item_line, line in assumed.body:
        if ITEM.match(line) and not CITED_ID.search(line):
            problems.append(f"summary line {item_line}: {assumed.title}: cite the decision's appendix id (A<n>)")
        if ITEM.match(line) and not RUNNER_UP.search(line):
            problems.append(f"summary line {item_line}: {assumed.title}: no runner-up")
    for unknown in sorted(set(cited) - known_ids, key=lambda i: int(i[1:])):
        problems.append(f"summary: {assumed.title}: {unknown} is not an assumed decision in the GDD's appendix")
    if len(set(cited)) > 5:
        problems.append(f"summary: {assumed.title}: {len(set(cited))} decisions; list the five that shape the game most")
    elif len(set(cited)) < 5:
        left = sorted(known_ids - set(CITED_ID.findall(summary)), key=lambda i: int(i[1:]))
        if left:
            problems.append(f"summary: {assumed.title}: {len(set(cited))} decision(s), but the appendix also has "
                            + ", ".join(left) + "; list up to five")
    kill_list = parts[6]
    if sum(1 for _, line in kill_list.body if ITEM.match(line)) < 3:
        problems.append(f"summary: {kill_list.title}: three items, one line each")
    if is_empty(parts[5]):
        problems.append(f"summary: {parts[5].title}: empty; say what the playtesters found, or that they didn't run")
    if normalized(CLOSING_QUESTION) not in normalized(summary):
        problems.append(f"summary: the closing question isn't word for word: \"{CLOSING_QUESTION}\"")
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("gdd", type=Path)
    parser.add_argument("--template", type=Path, default=TEMPLATE)
    parser.add_argument("--handsoff", action="store_true", help="also check what gdd-handsoff §6 asks")
    parser.add_argument("--owner-picked", action="store_true", help="the owner picked the concept")
    parser.add_argument("--summary", type=Path, help="GDD-summary.md to check too (implies --handsoff)")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # agents read it; Windows pipes default to a code page
    gdd = args.gdd.read_text(encoding="utf-8")
    problems, open_items = check(gdd, args.template.read_text(encoding="utf-8"),
                                 args.handsoff or bool(args.summary), args.owner_picked)
    if args.summary:
        problems += check_summary(args.summary.read_text(encoding="utf-8"), gdd)
    for line in problems:
        print(f"PROBLEM: {line}")
    for line in open_items:
        print(f"OPEN: {line}")
    print(f"{len(problems)} problem(s), {len(open_items)} [OPEN] item(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
