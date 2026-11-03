"""Check that a plan and its decisions ledger cite the same decision ids: the mechanical half of the
two-way check.

    python check_ledger.py <ledger.md> <plan.md>

A decision is a row of the ledger's Decisions table whose first cell is an id (D1, D2…). Every one
must be cited somewhere in the plan, and the plan must cite no id the ledger lacks; an id cited
elsewhere in the ledger (its list of assumed decisions, say) must be in the table too. Whether each
decision keeps its meaning in the plan stays the reviewer's job.

Exits 1 on any mismatch or when the ledger has no decision rows, 0 otherwise. Standard library only.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys

ROW = re.compile(r"^\s*\|\s*\**(D\d+)\**\s*\|")
CITED = re.compile(r"\bD\d+\b")


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
