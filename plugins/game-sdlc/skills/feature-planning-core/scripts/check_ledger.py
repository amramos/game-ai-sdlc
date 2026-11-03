"""Check that a plan and its decisions ledger cite the same decision ids: the mechanical half of the
two-way check.

    python check_ledger.py <ledger.md> <plan.md>

A decision is a row of the ledger's Decisions table whose first cell is an id (D1, D2…). Every one
must be cited somewhere in the plan, and the plan must cite no id the ledger lacks; an id cited
elsewhere in the ledger (its list of assumed decisions, say) must be in the table too. Whether each
decision keeps its meaning in the plan stays the reviewer's job.

In a hands-off ledger (`**Mode:** hands-off`) it also checks what feature-planning-handsoff §3 asks:
- every row's Decided by is one of the template's labels, and its Dissent cell is filled (the
  rejected answer, or `—` when the reviewer agreed);
- every `panel — assumed` row is in the "Assumed by the panel" list with a runner-up, and the list
  holds only those rows;
- the approval record's open questions are `none`.

Exits 1 on any mismatch or when the ledger has no decision rows, 0 otherwise. Standard library only.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

ROW = re.compile(r"^\s*\|\s*\**(D\d+)\**\s*\|")
CITED = re.compile(r"\bD\d+\b")
HANDSOFF = re.compile(r"^\*\*Mode:\*\*\s*hands-off\b", re.MULTILINE)
LABELS = {"owner", "owner (rec)", "panel", "panel — assumed", "panel — assumed (profile)"}
ASSUMED_LIST = re.compile(r"^\*\*Assumed by the panel\*\*")
RUNNER_UP = re.compile(r"runner-up:?\**\s*\S", re.IGNORECASE)
OPEN_QUESTIONS = re.compile(r"^\s*-\s*\*\*Open questions:\*\*\s*(.*)$", re.MULTILINE)


def without_comments(text: str) -> str:
    return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)


def decisions(ledger: str) -> dict[str, int]:
    """Decision id -> the ledger line that defines it."""
    rows: dict[str, int] = {}
    for number, line in enumerate(without_comments(ledger).splitlines(), 1):
        match = ROW.match(line)
        if match:
            rows.setdefault(match.group(1), number)
    return rows


def citations(text: str) -> dict[str, int]:
    """Cited id -> the first line that cites it."""
    cited: dict[str, int] = {}
    for number, line in enumerate(without_comments(text).splitlines(), 1):
        for found in CITED.findall(line):
            cited.setdefault(found, number)
    return cited


def cells(line: str) -> list[str]:
    return [cell.strip().strip("*`").strip() for cell in line.strip().strip("|").split("|")]


def check_handsoff(ledger: str) -> list[str]:
    """What feature-planning-handsoff §3 asks of a hands-off ledger."""
    problems: list[str] = []
    lines = without_comments(ledger).splitlines()
    header = next((cells(line) for line in lines if line.lstrip().startswith("|") and "Decided by" in line), None)
    if header is None or "Dissent" not in header:
        return ["the Decisions table has no Dissent column (ledger-template.md)"]
    decided, dissent = header.index("Decided by"), header.index("Dissent")
    assumed: dict[str, int] = {}
    for number, line in enumerate(lines, 1):
        match = ROW.match(line)
        if not match:
            continue
        row = cells(line)
        label = " ".join(row[decided].replace(" - ", " — ").split()) if len(row) > decided else ""
        if label not in LABELS:
            problems.append(f"line {number}: {match.group(1)}: Decided by is {label!r}; use one of "
                            + ", ".join(sorted(LABELS)))
        if len(row) <= dissent or not row[dissent]:
            problems.append(f"line {number}: {match.group(1)}: empty Dissent; the rejected answer, or — when the "
                            "reviewer agreed")
        if "assumed" in label:
            assumed.setdefault(match.group(1), number)
    listed: dict[str, tuple[int, str]] = {}
    in_list = False
    for number, line in enumerate(lines, 1):
        if ASSUMED_LIST.match(line):
            in_list = True
            continue
        if in_list and (line.startswith("#") or (line.strip() and not line.lstrip().startswith(("-", "*"))
                                                 and not line.startswith(" "))):
            in_list = False
        if in_list and line.lstrip().startswith("-"):
            ids = CITED.findall(line)
            if ids:
                listed.setdefault(ids[0], (number, line))
    for missing in by_number(set(assumed) - set(listed)):
        problems.append(f"{missing} (line {assumed[missing]}) is assumed but not in the \"Assumed by the panel\" list")
    for extra in by_number(set(listed) - set(assumed)):
        problems.append(f"line {listed[extra][0]}: {extra} is in the \"Assumed by the panel\" list but its row isn't "
                        "assumed")
    for found in by_number(set(listed) & set(assumed)):
        if not RUNNER_UP.search(listed[found][1]):
            problems.append(f"line {listed[found][0]}: {found}: no runner-up")
    match = OPEN_QUESTIONS.search(without_comments(ledger))
    if match and match.group(1).strip().rstrip(".").lower() != "none":
        problems.append("the approval record's open questions must be none: an owner's question is answered and "
                        "assumed, never left open")
    return problems


def by_number(ids) -> list[str]:
    return sorted(ids, key=lambda i: int(i[1:]))


def check(ledger: str, plan: str) -> list[str]:
    defined = decisions(ledger)
    if not defined:
        return ["the ledger has no decision rows (| D1 | … |) in its Decisions table"]
    problems = []
    in_plan = citations(plan)
    for missing in by_number(set(defined) - set(in_plan)):
        problems.append(f"{missing} (ledger line {defined[missing]}) is not cited in the plan")
    for invented in by_number(set(in_plan) - set(defined)):
        problems.append(f"plan line {in_plan[invented]} cites {invented}, which the ledger doesn't have")
    for stray in by_number(set(citations(ledger)) - set(defined)):
        problems.append(f"ledger line {citations(ledger)[stray]} cites {stray}, which has no row in its Decisions table")
    if HANDSOFF.search(ledger):
        problems += check_handsoff(ledger)
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("ledger", type=Path)
    parser.add_argument("plan", type=Path)
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # agents read it; Windows pipes default to a code page
    ledger = args.ledger.read_text(encoding="utf-8")
    problems = check(ledger, args.plan.read_text(encoding="utf-8"))
    for line in problems:
        print(f"PROBLEM: {line}")
    print(f"{len(decisions(ledger))} decision(s), {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
