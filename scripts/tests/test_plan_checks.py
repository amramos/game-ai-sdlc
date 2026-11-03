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

**Provisional** — written by agents from a short intake.

## 1. Pitch

Grow a reef between tides.

### Pillars

1. **Slow growth.** Every tide adds one coral. *Test: does the reef change each tide?*

## 2. Core loop **[DESIGNED]**

- **Moment to moment:** place one coral per tide.

## 3. Mechanics **[DESIGNED]**

### 3.1 Currents
Currents push larvae one tile a tide. Strength is **[OPEN]** (§14, item 1): one tile or two.

*Check:* reading the current lets the player seed a far tile; a bot that ignores currents scores lower.

### 3.2 When rules meet
Currents move before coral grows.

## 4. Progression and economy **[DESIGNED]**

One reef per run.

## 5. Worked example **[DESIGNED]**

Tide 1: a coral on B2; the current carries larvae to B3.

## 6. Content **[DESIGNED]**

One reef map.

## 7. Story and tone **[DESIGNED]**

Quiet and patient.

## 8. Art and audio direction **[DESIGNED]**

Top-down, painted 2D.

## 9. Interface **[DESIGNED]**

The tide clock sits top right.

## 10. Platform and business **[DESIGNED]**

Godot, desktop and web; pay what you want ([itch.io survey](https://example.com/survey)).

## 11. Glossary

| Term | Meaning |
|---|---|

## 12. First playable **[DESIGNED]**

One reef, ten tides. Current strength stays one tile while [OPEN] (§14, item 1).

## 13. Scope boundary

**Scope:** game jam.

## 14. Open questions **[OPEN]**

1. **How strong are currents?** — options: one tile, two. Recommendation: one.

## 15. Risks

- Ten tides may be too short to see a reef grow.

## Appendix: Assumed by the panel

- **A1** The concept and its pillars (§1) — `panel — assumed` — runner-up: the kelp concept.
- **A2** Top-down painted 2D (§8) — `panel — assumed` — runner-up: side view.
- **A3** Quiet and patient (§7) — `panel — assumed` — runner-up: playful.
- **A4** The tide clock top right (§9) — `panel — assumed (profile)` — runner-up: a tide bar.
"""

SUMMARY = """# Tide Gardener — GDD summary

## Pitch
Grow a reef between tides.

## Pillars
1. **Slow growth.** *Test: does the reef change each tide?* (A1)
2. **Wide currents.** *Test: does a current carry larvae?*
3. **One map.** *Test: is the reef the same each run?*

## Camera and medium
Top-down, painted 2D (A2).

## Other assumed decisions
- (A3) Quiet and patient — runner-up: playful.
- (A4) The tide clock — runner-up: a tide bar.

## Housekeeping baseline
Game jam: not built. Swap: "backlog".

## Playtesters' verdict
Not run.

## Reviewer's kill list
1. Too slow. — a faster tide.
2. Currents unreadable. — arrows.
3. Too short. — twenty tides.

## Closing question
Change any of these, or continue to `setup-godot` with every recommendation (the project will run hands-off)?
"""


class CheckGddTests(unittest.TestCase):
    def test_the_unfilled_template_fails_only_on_its_placeholders(self) -> None:
        problems, _ = check_gdd.check(TEMPLATE, TEMPLATE)
        self.assertTrue(problems)
        self.assertEqual([p for p in problems if "unfilled template placeholder" not in p], [])

    def test_placeholders_count_but_comments_code_and_tags_dont(self) -> None:
        gdd = GDD.replace("Quiet and patient.", "Quiet <!-- <tone> --> and `<b>` patient,<br> <what it feels like>.")
        problems, _ = check_gdd.check(gdd, TEMPLATE)
        self.assertEqual(problems, [problems[0]])
        self.assertIn("unfilled template placeholder <what it feels like>", problems[0])

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

    def test_a_missing_or_empty_section_is_a_problem(self) -> None:
        gdd = GDD.replace("## 15. Risks\n\n- Ten tides may be too short to see a reef grow.\n", "")
        gdd = gdd.replace("Quiet and patient.\n", "<!-- tone -->\n")
        problems, _ = check_gdd.check(gdd, TEMPLATE)
        self.assertEqual(sorted(p.split(": ")[-1] for p in problems),
                         ["empty", "missing; every section of the template is written"])

    def test_an_open_item_points_at_the_open_questions(self) -> None:
        problems, _ = check_gdd.check(GDD.replace(" (§14, item 1): one tile", ": one tile"), TEMPLATE)
        self.assertEqual(len(problems), 1)
        self.assertIn("[OPEN] with no item in §14", problems[0])
        problems, _ = check_gdd.check(GDD.replace(" — options: one tile, two. Recommendation: one.", ""), TEMPLATE)
        self.assertEqual(len(problems), 1)
        self.assertIn("options and a recommendation", problems[0])
        problems, _ = check_gdd.check(GDD.replace("(§14, item 1): one tile", "(§14, item 3): one tile"), TEMPLATE)
        self.assertEqual(len(problems), 1)
        self.assertIn("§14 has no item 3", problems[0])

    def test_every_mechanic_but_when_rules_meet_has_a_check_line(self) -> None:
        problems, _ = check_gdd.check(GDD.replace("*Check:* reading", "Reading"), TEMPLATE)
        self.assertEqual(len(problems), 1)
        self.assertIn("Currents: no *Check:* line", problems[0])

    def test_a_handsoff_gdd_and_summary_pass(self) -> None:
        problems, _ = check_gdd.check(GDD, TEMPLATE, handsoff=True)
        self.assertEqual(problems, [])
        self.assertEqual(check_gdd.check_summary(SUMMARY, GDD), [])

    def test_handsoff_needs_the_provisional_line_and_a_researched_price(self) -> None:
        gdd = GDD.replace("**Provisional**", "Provisional").replace("https://example.com/survey", "survey")
        problems, _ = check_gdd.check(gdd, TEMPLATE, handsoff=True)
        self.assertEqual(len(problems), 2)
        self.assertIn("**Provisional**", problems[0])
        self.assertIn("price model", problems[1])

    def test_the_appendix_lists_only_assumed_decisions_with_ids_and_runner_ups(self) -> None:
        gdd = GDD.replace("- **A3** Quiet and patient (§7) — `panel — assumed` — runner-up: playful.",
                          "- **A3** Quiet and patient (§7) — `panel` — runner-up: playful.\n"
                          "- Water is blue (§8) — `panel — assumed`.")
        problems, _ = check_gdd.check(gdd, TEMPLATE, handsoff=True)
        self.assertEqual(sorted(p.split(": ", 2)[-1][:30] for p in problems),
                         ["no assumed decision on tone (§", "no runner-up", "not an assumed decision; the a",
                          "start each line with its id, *"])

    def test_identity_decisions_are_assumed_unless_the_owner_picked_the_concept(self) -> None:
        gdd = GDD.replace(" (§1) —", " —")
        problems, _ = check_gdd.check(gdd, TEMPLATE, handsoff=True)
        self.assertEqual(len(problems), 1)
        problems, _ = check_gdd.check(gdd, TEMPLATE, handsoff=True, owner_picked=True)
        self.assertEqual(problems, [])
        problems, _ = check_gdd.check(gdd.replace(" (§8) —", " —"), TEMPLATE, handsoff=True, owner_picked=True)
        self.assertEqual(len(problems), 1)
        self.assertIn("the art style (§8)", problems[0])

    def test_a_profile_addition_outside_the_pillars_is_fine(self) -> None:
        gdd = GDD.replace("### Pillars", "### Hook\n\nTides bring back an old shell (profile) Signature 1.\n\n### Pillars")
        problems, _ = check_gdd.check(gdd, TEMPLATE, handsoff=True)
        self.assertEqual(problems, [])

    def test_the_summary_lists_three_pillars_with_tests(self) -> None:
        problems = check_gdd.check_summary(SUMMARY.replace("3. **One map.** *Test: is the reef the same each run?*\n",
                                                           ""), GDD)
        self.assertEqual(len(problems), 1)
        self.assertIn("three pillars", problems[0])

    def test_a_profile_addition_never_edits_a_pillar(self) -> None:
        problems, _ = check_gdd.check(GDD.replace("one coral. *Test", "one coral (profile) Signature 1. *Test"),
                                      TEMPLATE, handsoff=True)
        self.assertEqual(len(problems), 1)
        self.assertIn("never edits a pillar", problems[0])

    def test_the_summary_cites_assumed_decisions_and_closes_word_for_word(self) -> None:
        summary = SUMMARY.replace("- (A4) The tide clock — runner-up: a tide bar.\n", "- (A9) Gulls — wild.\n")
        summary = summary.replace("(the project will run hands-off)", "(hands-off)").replace("3. Too short. — twenty tides.\n", "")
        problems = check_gdd.check_summary(summary, GDD)
        self.assertEqual(len(problems), 5, problems)
        joined = "\n".join(problems)
        for expected in ("no runner-up", "A9 is not an assumed decision", "also has A4", "three items",
                         "word for word"):
            self.assertIn(expected, joined)

    def test_an_empty_runner_up_fails(self) -> None:
        problems, _ = check_gdd.check(GDD.replace("runner-up: playful.", "runner-up:"), TEMPLATE, handsoff=True)
        self.assertEqual(len(problems), 1)
        self.assertIn("no runner-up", problems[0])

    def test_a_commented_out_question_is_no_item(self) -> None:
        gdd = GDD.replace("1. **How strong are currents?** — options: one tile, two. Recommendation: one.",
                          "<!--\n1. **How strong are currents?** — options: one tile, two. Recommendation: one.\n-->\nNone.")
        problems, _ = check_gdd.check(gdd, TEMPLATE)
        self.assertEqual(len(problems), 2)
        self.assertTrue(all("§14 has no item 1" in p for p in problems))

    def test_the_closing_question_belongs_in_the_last_part(self) -> None:
        summary = SUMMARY.replace("Not run.", "Not run. Change any of these, or continue to `setup-godot` with every "
                                  "recommendation (the project will run hands-off)?")
        summary = summary.rsplit("## Closing question", 1)[0] + "## Closing question\n"
        problems = check_gdd.check_summary(summary, GDD)
        self.assertEqual(len(problems), 2)
        self.assertIn("empty", problems[0])
        self.assertIn("word for word", problems[1])

    def test_an_empty_summary_part_fails(self) -> None:
        problems = check_gdd.check_summary(SUMMARY.replace("Not run.\n", ""), GDD)
        self.assertEqual(len(problems), 1)
        self.assertIn("the playtesters' verdict", problems[0])

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

HANDSOFF_LEDGER = """# Night market — decisions ledger

**State:** PROVISIONALLY APPROVED
**Mode:** hands-off · **Plan:** `plan.md`

## Decisions

| Id | Question | Answer | Decided by | Dissent | Date |
|---|---|---|---|---|---|
| D1 | When does the market open? | After the second boss | owner | — | 2026-10-01 |
| D2 | Can prices change? | Once a night | panel — assumed | Never (the reviewer's answer) | 2026-10-01 |
| D3 | Haggling? | No | `panel` | — | 2026-10-02 |

**Assumed by the panel** (hands-off only — the owner skims these first):
- D2: prices change once a night — runner-up: never.

## Approval record

- **Open questions:** none
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

    def test_a_handsoff_ledger_passes(self) -> None:
        self.assertEqual(check_ledger.check(HANDSOFF_LEDGER, PLAN), [])

    def test_handsoff_rows_need_a_label_and_a_dissent(self) -> None:
        ledger = HANDSOFF_LEDGER.replace("| owner | — |", "| me | |")
        problems = check_ledger.check(ledger, PLAN)
        self.assertEqual(len(problems), 2)
        self.assertIn("Decided by is 'me'", problems[0])
        self.assertIn("empty Dissent", problems[1])

    def test_the_assumed_list_matches_the_assumed_rows_with_runner_ups(self) -> None:
        ledger = HANDSOFF_LEDGER.replace("- D2: prices change once a night — runner-up: never.\n",
                                         "- D3: no haggling.\n")
        problems = check_ledger.check(ledger, PLAN)
        self.assertEqual(len(problems), 2)
        self.assertIn("D2 (line", problems[0])
        self.assertIn("D3 is in the", problems[1])
        problems = check_ledger.check(HANDSOFF_LEDGER.replace(" — runner-up: never", ""), PLAN)
        self.assertEqual(problems, [problems[0]])
        self.assertIn("no runner-up", problems[0])

    def test_an_empty_ledger_runner_up_fails(self) -> None:
        problems = check_ledger.check(HANDSOFF_LEDGER.replace("runner-up: never", "runner-up:"), PLAN)
        self.assertEqual(len(problems), 1)
        self.assertIn("no runner-up", problems[0])

    def test_handsoff_open_questions_stay_none(self) -> None:
        problems = check_ledger.check(HANDSOFF_LEDGER.replace("**Open questions:** none", "**Open questions:** D2?"), PLAN)
        self.assertEqual(len(problems), 1)
        self.assertIn("open questions must be none", problems[0])

    def test_a_handsoff_ledger_needs_its_open_questions_line(self) -> None:
        problems = check_ledger.check(HANDSOFF_LEDGER.replace("- **Open questions:** none\n", ""), PLAN)
        self.assertEqual(len(problems), 1)
        self.assertIn("no **Open questions:** line", problems[0])

    def test_a_handsoff_ledger_without_a_dissent_column_fails(self) -> None:
        self.assertEqual(len(check_ledger.check(LEDGER.replace("# Night market", "**Mode:** hands-off\n# N"), PLAN)), 1)

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
