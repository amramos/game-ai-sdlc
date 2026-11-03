# Validating R1: one round reviewer instead of the planning panel

A cheap before/after check of [R1](README.md#r1-hands-off-feature-planning-one-reviewer-instead-of-a-three-agent-panel-conditional)
(and, by extension, R2) before shipping it, as §6 asks. **Verdict: the gate failed on the mid-size
model, so R1 and R2 are held back.** A one-paragraph fix restored the lost signal in one re-run; the
owner rules on whether that is enough to ship.

## Setup

| | |
|---|---|
| Fixture | An invented small GDD: a turn-based puzzle game where the player places relay masts on a hex valley to connect villages to a radio station in 12 turns. Three pillars ("every mast is a trade-off", "read the land", "quiet tension", the last with *no timers*). The GDD parks "a weather system". |
| Feature request | "Add weather. Storms roll across the valley and knock out masts they pass over, so the network has to be rebuilt. Not sure whether it should feel ominous or cozy, you pick. Not sure if the first release should have storms only or storms plus fog and wind." Owner-only by nature: **tone** (ominous/cozy), **scope** (storms only or more), and **reversing a parked item**. |
| Taste profile | Five entries (two Values, one Signature, two Nevers, one Leaning), in a scratch folder named by `GAME_SDLC_TASTE`. The Signature ("losses stay visible afterwards") and Never 1 ("random punishment the player couldn't see coming") both bear on storms; a good judge should find them. |
| Skill | `feature-planning-handsoff`, option 1 (stop at the plan). |
| Before | The skill as on `main` (0.8.1): designer, player advocate and skeptic each answer every round. |
| After | The R1 draft from this branch: the session is the designer; one round reviewer per round with the skeptic's brief, the player advocate's questions as a checklist, and the whole profile as judge. |
| Tiers | Frontier: Opus 5.5. Mid-size: Sonnet 5.5. Codex (other vendor) reachable in every run, through the runner `team-lead/scripts/codex_review.py` from the scripts pull request. |

**Method.** Headless `claude -p --plugin-dir` couldn't authenticate from inside the desktop app's
session (OAuth refresh is host-side), so each run was a subagent of the given model, told to read
the skill files from a "before" or "after" copy of the plugin rather than the installed one, in its
own git-initialised copy of the fixture. The runs went in parallel. The lead's own subagents
(panelists) and Codex calls were counted from each run's log. One run each, as the owner chose:
treat every difference below as a pointer, not a measurement.

## Results

| Run | Wall-clock | Claude spawns | Codex calls | Rounds | Decisions | Assumed | Runner-ups recorded |
|---|---|---|---|---|---|---|---|
| Before, Opus | 16.2 min | 12 (6 Opus designers, 6 Sonnet advocates) | 8 (6 skeptic, 2 two-way) | 6 | 33 | 4 | no |
| After, Opus | 9.7 min | 0 | 5 (3 reviewer, 2 two-way) | 3 | 28 | 7 | yes, all 7 |
| Before, Sonnet | 6.4 min ¹ | 2 (+2 discarded) | 2 (+1 abandoned) | 1 | 16 | 5 | no |
| After, Sonnet | 4.9 min | 0 | 2 (1 reviewer, 1 two-way) | 1 | 12 | 4 | yes, all 4 |
| After + fix, Sonnet | 4.4 min | 0 | 3 (2 reviewer, 1 two-way) | 2 | 15 | 6 | yes, all 6 |

¹ The before-Sonnet run shared a working-folder name with the after-Sonnet run; its first panel
round read the other run's brief and was thrown away and redone. Its time includes the wasted round.

### Owner-only questions

Every run marked both of the request's owner questions as `panel — assumed`: tone (all five chose
"quietly ominous", never cozy) and scope (all five chose storms only, fog and wind parked). Every
run also marked un-parking weather as assumed. "After" runs marked more as assumed (7 vs 4 on Opus): the reviewer treated the forecast horizon and
determinism as profile-settled, and they were recorded `panel — assumed (profile)`.

### Dissent

- **Before:** dissent appears as "(Split: …)" inside the answer cell (before-Opus: 9 rows; before-
  Sonnet: 1). The assumed list has no runner-ups, so the owner can't see what the alternative was.
- **After:** every assumed decision has a runner-up, and adopted dissent is named in the row
  ("reviewer's dissent adopted" or "reviewer's addition", 8 rows on Opus). After-Sonnet adds a "reviewer dissent kept"
  paragraph. On this measure "after" is better than "before": the owner sees the alternative in
  the place they read first.

### Who disagreed with the lead

In before-Opus, the same-model **designer** agreed with the lead on every question in three of six
rounds and differed on one question in each of the other three; the **player advocate** (Sonnet)
agreed with everything in five of six rounds. The Codex skeptic asked for changes in five of six rounds. This is the premise
of R1 seen directly: almost all the disagreement came from the other vendor.

### What "after" missed that "before" caught

- **Sonnet: the taste profile's Signature.** Before-Sonnet recorded "the hex keeps a faint scar
  where a mast was knocked out" as `panel — assumed (profile)`. In after-Sonnet, the reviewer saw
  the same opening, but wrote it only in its owner-only explanation ("as a possible signature
  opportunity, show the aftermath of a knocked-out mast"); the lead reads answers, not
  explanations, and the plan has no lasting trace. This is a signal the owner set up the profile
  to get, and the cheap tier lost it. **This fails the gate.**
- **Sonnet: thinner coverage.** After-Sonnet has 12 decisions to before-Sonnet's 16. Missing: a
  sound-off cue for a lost link, whether a mast can be protected, the placement-preview warning on
  a doomed hex. None is owner-only; `game-ui` checks and the two-way reviewer would likely catch
  the first and third at build time.
- **Opus: nothing material.** After-Opus kept the Signature (a fallen mast leaves a trace for the
  rest of the level, reviewer's dissent adopted), teaching, reduced motion and colour hierarchy.
  Before-Opus had a few extra presentation decisions (an end-of-season view keeping losses on the
  map, a "lean" warning on the next step, no undo); after-Opus covered the same ground with
  different decisions. Before-Opus ran twice as many rounds and asked more, finer questions.

### Cost

Per round, "before" spent two Claude spawns and one Codex call; "after" one Codex call. On Opus,
"after" took 60% of the wall-clock with no Claude spawns at all. Rounds waited on the slowest
panelist before; now they wait on Codex alone.

## The gate

**Failed on Sonnet**: "after" lost the profile's Signature, a decision-quality signal the owner
cares about. Following the brief, **R1 and R2 are not shipped** in the accompanying pull request.

**Why it was lost.** It's a brief problem, not a model problem. `taste-profile` §3 sends the
judge's explanations only to the owner's report. A judge that is one of three panelists can still
put a profile-driven option in its *answer* (before-Sonnet's did, with a label). The R1 reviewer's
brief didn't say where a Signature opening goes, so the reviewer filed it under explanation, out of
the lead's sight.

**Smallest fix** (two sentences in `feature-planning-handsoff` §2–3, applied on the held branch):
the reviewer states a Signature opening *among its answers*, as an addition with `(profile)` and the
label, never only in the explanation; the lead takes such an addition when the game has room for it,
as `panel — assumed (profile)`, and leaving it out is a dissent like any other.

**Re-run with the fix** (after + fix, Sonnet, once): the reviewer raised "(profile) Signature 1" in
its answers, and the lead recorded "a nonblocking trace marks the loss" as `panel — assumed
(profile)` with a runner-up. It also ran a second round for dependent questions, and coverage rose
to 15 decisions. One run is weak evidence; it shows the fix works as intended, not that it always
will.

**Recommendation to the owner:** ship R1 with the fix, and R2 with the same brief, if one re-run is
enough; otherwise run the fixed version on a second fixture of a different genre (§6 asks for two
or three) on Sonnet first. The fixed R1/R2 text is one commit on the branch `feat/single-round-reviewer`, so either
ruling is one step.

## Limits

- One fixture, one run per arm. Model variance alone could explain the decision counts.
- Subagents, not fresh CLI sessions: each lead ran with the general-purpose agent's system prompt,
  the same in both arms.
- The two arms ran in parallel on one machine and shared one Codex quota; none fell back.
- Wall-clock includes Codex latency, which varies by load.
