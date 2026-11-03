# Validating R1: one round reviewer instead of the planning panel

A cheap before/after check of [R1](README.md#r1-hands-off-feature-planning-one-reviewer-instead-of-a-three-agent-panel-conditional)
(and, by extension, R2) before shipping it, as §6 asks. **Verdict: the first draft failed the gate
on the mid-size model** (it lost the taste profile's Signature). A two-sentence fix restored it in a
re-run, and on the owner's ruling it was checked on a second fixture of another genre, where it held.
**R1 and R2 ship with the fix.**

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
cares about. Following the brief, R1 and R2 were held back until the owner ruled (see "Second
fixture").

**Why it was lost.** It's a brief problem, not a model problem. `taste-profile` §3 sends the
judge's explanations only to the owner's report. A judge that is one of three panelists can still
put a profile-driven option in its *answer* (before-Sonnet's did, with a label). The R1 reviewer's
brief didn't say where a Signature opening goes, so the reviewer filed it under explanation, out of
the lead's sight.

**Smallest fix** (two sentences in `feature-planning-handsoff` §2–3, now part of R1):
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
or three) on Sonnet first. The owner chose the second fixture; see below.

## Second fixture

The owner's ruling: before shipping, run the fixed R1 on a second fixture of a clearly different
genre, on the mid-size model only, against the current skill.

| | |
|---|---|
| Fixture | An invented narrative game about conversation: a night clerk talks with visitors over seven nights and decides which of their records go into the one crate that will be kept. Pillars: "listening is the verb", "every record is someone's", "hushed and late". No fail state. The GDD parks "characters remembering earlier conversations". |
| Feature request | "Let visitors remember what the clerk told them on earlier nights and bring it back later. Not sure whether that should feel warm or a little unsettling, you pick. Should the first release have it for all six visitors, or just the two main ones?" Owner-only: **tone**, **scope**, and **un-parking** a parked item. |
| Taste profile | Signature: small acts that pay off much later, without being pointed out. Never 1: telling the player a choice mattered instead of showing it. Never 2: choices that sort into good and evil. |
| Runs | Sonnet only: the current skill (`main`) and fixed R1. Each with its own project and working folder, so last time's collision couldn't repeat; neither touched the other's files. |

| Run | Wall-clock | Claude spawns | Codex calls | Rounds | Decisions | Assumed | Runner-ups recorded |
|---|---|---|---|---|---|---|---|
| Before, Sonnet | 3.3 min | 2 (Sonnet designer, Haiku advocate) | 2 (1 skeptic, 1 two-way) | 1 | 9 | 2 | no |
| Fixed R1, Sonnet | 4.5 min | 0 | 3 (2 reviewer, 1 two-way) | 2 | 15 | 5 | yes, all 5 |

**The Signature is carried into the plan.** The reviewer raised "Signature 1" among its answers in
both rounds (round 1 on how a callback comes back, round 2 on pacing). The lead recorded it as D9,
`panel — assumed (profile)`: at least one full night between the telling and the callback, "an
understated payoff well after the telling", with a runner-up (a callback the very next night,
rejected because it reads as an echo, not memory). D4 adds that nothing on screen signals a line
will be remembered. Before's plan has the "never announced" part (from its designer, who cited the
profile) but nothing on spacing the payoff, and records no decision as profile-settled.

**Every assumed decision has a runner-up** in fixed R1 (tone, scope, un-parking, the epilogue
effect, pacing), each saying whether the reviewer agreed. Before's two assumed decisions have none.

**Owner-only questions.** Both runs assumed tone (both chose warm; fixed R1 adds "a quiet edge from
accuracy") and scope (both: the two main visitors). **Before didn't mark un-parking the GDD's
parked item as assumed**, though reversing a past decision is the owner's by nature; fixed R1 did
(D5), with "keep it parked" as runner-up.

**Coverage.** Fixed R1: 15 decisions to before's 9. It decided what before left implicit or to the
build: no misremembering (so listening stays reliable), what happens when nothing qualifies, which
callback wins when several are eligible, save and skip rules from the housekeeping baseline, and
no good/evil sorting of what the clerk said (Never 2, stated on game grounds). Before decided one
thing fixed R1 didn't: a visitor may remark once, obliquely, when the clerk told them different
things on different nights. It's a nice touch, not a gap the build would trip on.

**Cost.** Fixed R1 ran a second round for dependent questions, so it took 72 s longer, with no
Claude spawns. Before ran one round and folded the skeptic's extra points in without re-asking.

**Verdict: holds.** The fixed reviewer kept the Signature, recorded runners-up for every
assumption, caught an owner-only reversal the panel missed, and covered more. With the first
fixture's Opus result, the fix holds on two genres and both tiers tested. R1 and R2 ship with it.

## Limits

- Two fixtures, one run per arm, and the second on Sonnet only. Model variance alone could explain
  the decision counts.
- Subagents, not fresh CLI sessions: each lead ran with the general-purpose agent's system prompt,
  the same in both arms.
- The two arms ran in parallel on one machine and shared one Codex quota; none fell back.
- Wall-clock includes Codex latency, which varies by load.
