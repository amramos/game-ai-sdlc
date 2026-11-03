"""Tests for gdd-core's check_gdd.py and feature-planning-core's check_ledger.py."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parents[2]
SKILLS = PACKAGE / "plugins" / "game-sdlc" / "skills"


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # dataclasses look their module up here
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


check_gdd = load("check_gdd", SKILLS / "gdd-core" / "scripts" / "check_gdd.py")
check_ledger = load("check_ledger", SKILLS / "feature-planning-core" / "scripts" / "check_ledger.py")
TEMPLATE = (SKILLS / "gdd-core" / "gdd-template.md").read_text(encoding="utf-8")

GDD = """# Tide Gardener — Game Design Document

## 1. Pitch

Grow a reef between tides.

## 2. Core loop **[DESIGNED]**

- **Moment to moment:** place one coral per tide.

## 3. Mechanics **[DESIGNED]**

### 3.1 Currents
Currents push larvae one tile a tide. Strength is **[OPEN]**: one tile or two.

## 11. Glossary

| Term | Meaning |
|---|---|

## 12. First playable **[DESIGNED]**

One reef, ten tides. Current strength stays one tile while [OPEN].

## 14. Open questions **[OPEN]**

1. **How strong are currents?** — options: one tile, two. Recommendation: one.
"""


class CheckGddTests(unittest.TestCase):
    def test_the_template_itself_passes(self) -> None:
        problems, _ = check_gdd.check(TEMPLATE, TEMPLATE)
        self.assertEqual(problems, [])

    def test_a_marked_gdd_passes_and_lists_its_open_items(self) -> None:
        problems, open_items = check_gdd.check(GDD, TEMPLATE)
        self.assertEqual(problems, [])
        self.assertEqual(len(open_items), 3)
        self.assertIn("§3 Mechanics", open_items[0])
        self.assertIn("in the first playable's section", open_items[1])
        self.assertIn("How strong are currents?", open_items[2])

    def test_a_section_the_template_marks_needs_a_marker(self) -> None:
        problems, _ = check_gdd.check(GDD.replace("## 3. Mechanics **[DESIGNED]**", "## 3. Mechanics"), TEMPLATE)
        self.assertEqual(len(problems), 1)
        self.assertIn("§3 Mechanics: no marker", problems[0])

    def test_sections_match_by_number_so_a_translated_gdd_checks(self) -> None:
        gdd = GDD.replace("## 1. Pitch", "## 1. Argumento").replace("## 2. Core loop **[DESIGNED]**", "## 2. Bucle")
        problems, _ = check_gdd.check(gdd, TEMPLATE)
        self.assertEqual(len(problems), 1)
        self.assertIn("§2 Bucle: no marker", problems[0])

    def test_unknown_markers_are_reported_wherever_they_are(self) -> None:
        gdd = GDD.replace("**[DESIGNED]**\n\n- **Moment", "**[TBD]**\n\n- **Moment").replace(
            "One reef, ten tides.", "One reef, ten tides [TODO].")
        problems, _ = check_gdd.check(gdd, TEMPLATE)
        self.assertEqual(sorted(p.split(": ")[-1] for p in problems),
                         ["no marker; use one of [BUILT], [DESIGNED], [OPEN]", "unknown marker [TBD]",
                          "unknown marker [TODO]"])

    def test_an_unnumbered_extra_section_needs_a_marker_and_links_are_not_markers(self) -> None:
        problems, _ = check_gdd.check(GDD + "\n## Appendix\n\nSee [HUD](hud.md).\n", TEMPLATE)
        self.assertEqual(len(problems), 1)
        self.assertIn("Appendix: no marker", problems[0])

    def test_headings_inside_code_fences_are_ignored(self) -> None:
        problems, _ = check_gdd.check(GDD + "\n```\n## 9. Not a section\n```\n", TEMPLATE)
        self.assertEqual(problems, [])

    def test_exits_1_on_problems(self) -> None:
        with tempfile.TemporaryDirectory() as work:
            path = Path(work) / "GDD.md"
            script = SKILLS / "gdd-core" / "scripts" / "check_gdd.py"
            path.write_text(GDD, encoding="utf-8")
            self.assertEqual(subprocess.run([sys.executable, str(script), str(path)], capture_output=True).returncode, 0)
            path.write_text(GDD.replace("## 12. First playable **[DESIGNED]**", "## 12. First playable"),
                            encoding="utf-8")
            result = subprocess.run([sys.executable, str(script), str(path)], capture_output=True, text=True,
                                    encoding="utf-8")
            self.assertEqual(result.returncode, 1)
            self.assertIn("PROBLEM: line ", result.stdout)


LEDGER = """# Night market — decisions ledger

## Decisions

| Id | Question | Answer | Decided by | Date |
|---|---|---|---|---|
| D1 | When does the market open? | After the second boss | owner | 2026-10-01 |
| D2 | Can prices change? | Once a night | panel — assumed | 2026-10-01 |
| **D3** | Haggling? | No | owner | 2026-10-02 |

**Assumed by the panel:**
- D2: prices change once a night.
"""

PLAN = """# Night market — implementation plan

## 2. Requirements

1. The market opens after the second boss. (D1)
2. Prices reroll at dusk (D2); no haggling button (D3).

<!-- D9 was dropped in review -->
"""


class CheckLedgerTests(unittest.TestCase):
    def test_matching_ids_pass(self) -> None:
        self.assertEqual(check_ledger.check(LEDGER, PLAN), [])

    def test_the_templates_pass(self) -> None:
        core = SKILLS / "feature-planning-core"
        self.assertEqual(check_ledger.check((core / "ledger-template.md").read_text(encoding="utf-8"),
                                            (core / "plan-template.md").read_text(encoding="utf-8")), [])

    def test_a_decision_missing_from_the_plan(self) -> None:
        problems = check_ledger.check(LEDGER, PLAN.replace(" (D1)", ""))
        self.assertEqual(problems, ["D1 (ledger line 7) is not cited in the plan"])

    def test_an_invented_decision_in_the_plan(self) -> None:
        problems = check_ledger.check(LEDGER, PLAN + "3. Stalls glow. (D4)\n")
        self.assertEqual(len(problems), 1)
        self.assertIn("cites D4, which the ledger doesn't have", problems[0])

    def test_ids_are_whole_words(self) -> None:
        problems = check_ledger.check(LEDGER, PLAN + "Uses the DD10 renderer and HD1080 output.\n")
        self.assertEqual(problems, [])

    def test_a_ledger_citing_an_id_without_a_row(self) -> None:
        problems = check_ledger.check(LEDGER + "- D7: something\n", PLAN)
        self.assertEqual(len(problems), 1)
        self.assertIn("cites D7, which has no row", problems[0])

    def test_a_ledger_with_no_decisions_fails(self) -> None:
        self.assertEqual(len(check_ledger.check("# Ledger\n\nNothing yet.\n", PLAN)), 1)

    def test_exit_codes(self) -> None:
        script = SKILLS / "feature-planning-core" / "scripts" / "check_ledger.py"
        with tempfile.TemporaryDirectory() as work:
            ledger, plan = Path(work) / "ledger.md", Path(work) / "plan.md"
            ledger.write_text(LEDGER, encoding="utf-8")
            plan.write_text(PLAN, encoding="utf-8")
            run = lambda: subprocess.run([sys.executable, str(script), str(ledger), str(plan)],  # noqa: E731
                                         capture_output=True).returncode
            self.assertEqual(run(), 0)
            plan.write_text(PLAN + "(D5)\n", encoding="utf-8")
            self.assertEqual(run(), 1)


if __name__ == "__main__":
    unittest.main()
