---
name: feature-planning-handsoff
description: Plan a feature without the owner in the loop — you answer every round of questions as the designer and one outside reviewer (another vendor's model when available) checks each round, decisions that belong to the owner are marked as assumed, and the plan comes out provisionally approved, optionally going straight on to be built. Use when the owner wants a feature planned (and possibly built) while they are away — when they invoke it, ask for hands-off planning in their own words, or accept it as the next step offered in the project's hands-off working style. Never pick it on your own initiative.
argument-hint: "The feature or change to plan"
---

# Feature planning (hands-off)

Load the **`feature-planning-core`** skill (`game-sdlc:feature-planning-core` when installed as a
plugin) and follow it in **hands-off mode**: you and one round reviewer answer the rounds instead
of the owner. The ledger still calls the two of you "the panel".

## 1. The one question asked up front

Before the owner leaves, ask a single question — what happens after the plan:

1. **Stop at the plan** — the owner reads the ledger and decides.
2. **Build it with `team-lead`** (recommended) — PRs wait for the owner to merge.
3. **Build it with `team-lead-handsoff`** — reviewed PRs merge to `main` without the owner.

Everything after that runs without asking.

- If the owner is already gone, take option 1.
- If there's no taste profile, offer it with this question, while the owner is still there
  (`taste-profile` §5).

## 2. You and the round reviewer

**You are the designer.** Write each round as you would for the owner (core §3): the frontier, and a
recommendation per question, consistent with the rest of the game. Under each recommendation, write
`Pillar test:` and the pillar test question it passes.

Then **one round reviewer**, a fresh agent per round, answers it. It gets the round, the relevant
GDD sections and docs, and this brief:

- **As a skeptic:** what fails, what's missing, what's expensive, what contradicts a past decision.
- **As a first-time player**, a checklist for every question that changes what the player sees or
  does, one line each:
  - what a player meeting this for the first time *sees*;
  - what they could *misread*;
  - what would *frustrate* them.
- **As the profile judge** (`taste-profile` §3): it reads the whole taste profile itself, in its own
  context, and returns its decisions under that section's rules.
- For every question: **agree**, or **a different answer** with one line of reason. It never sees
  your reasoning beyond the one line per recommendation.

**The reply's format comes from the script, not from you.** `codex_review.py --round plan` appends
it to the round; `--print-format plan` prints it for a Claude reviewer's brief. You read lines like
these: `Q<n>: agree`, `Q<n>: different: <answer>`, `Player (Q<n>)`, `Q<n> addition`, `Skeptic`,
`VERDICT`. A line ending in `(profile)` and a label is an answer whose only reason is the profile.

**Run it.**

- Another vendor's model when one is available: `team-lead/scripts/codex_review.py --probe`, then
  `--round plan --repo <project> --prompt-file <round> --out <file>`.
- Otherwise a Claude model set explicitly: a tier below the session's.
  - Use the same model when there's none below, or when the one below is smaller than mid-size.
    Then say in the report that the review had no independence of model.
  - A Claude subagent is never above the session's model; another vendor's model may be stronger.
  - End its brief with the printed format and: "Write your reply to `<reply file>` and return only
    the word `written`." Then run `codex_review.py --split <reply file> --need-verdict --out <file>`.
    On exit 4, ask the reviewer once more with the format before taking exit 4 below.

**What the exit code means.**

- **0**: read `<file>`. It holds only the answers. The owner-only explanation is in
  `<file stem>.owner.md`: never open it; the report to the owner links it.
- **4**: no usable reply, even after one retry. Decide the round yourself, record its answers as
  `panel — assumed`, and say in the report that the round had no usable review.
- **2 or 3**: no other vendor's model; use a Claude reviewer as above.

## 3. Resolving a round

For each question:

- **The reviewer agrees** → take it; `Decided by: panel`; Dissent `—`.
- **It disagrees** → you decide, with a one-line reason; `Decided by: panel`. The Dissent cell holds
  the answer you didn't take:
  - the reviewer's answer, when you keep your recommendation;
  - your recommendation, when you adopt the reviewer's answer.
- **A `(profile)` line** (an addition, or an answer whose only reason is the profile) → take it when
  the game has room for it.
  - Record it as `panel — assumed (profile)`, written as the game change (`taste-profile` §3).
  - Left out, it goes in the Dissent cell like any other answer.
- **Profile text above the line** (a quote or a paraphrase) → take only the decision and the label,
  word the row yourself, and note the slip in the report.
- **The owner's by nature** → decided as above, but recorded as `panel — assumed`, or
  `panel — assumed (profile)` when a profile entry settled it. It goes in the "Assumed by the panel"
  list with a runner-up: its Dissent cell, or the strongest option you rejected when the reviewer
  agreed. The owner's by nature means:
  - taste;
  - scope;
  - reversing a past decision;
  - the GDD's pillars: setting them when missing, or choosing between two that pull apart;
  - anything `AGENTS.md` reserves to the owner.

  **When the owner's request itself asks for a reversal**, the reversal is `owner`; whatever the
  request leaves open about it is assumed.

`check_ledger.py` (core §9) checks these labels, the Dissent cells, the assumed list and its
runner-ups in a hands-off ledger; fix what it lists.

The first-time-player lines that point at something real become requirements, acceptance checks
or "pass and still fail" items (core §5), not just notes.

Never stall on an owner-only question, and never quietly drop it: answer it, mark it assumed, move on.

## 4. What stays the same as interactive mode

- The walkthrough, sketches for layout forks (saved as files the owner can open later), the "pass
  and still fail" check, the playable slice, the plan, and the two-way ledger review all still
  happen.
- The round reviewer does not double as the two-way reviewer; use a fresh agent for that (core §9).

## 5. The result

- State: **PROVISIONALLY APPROVED** — every gate is provisional until the owner reads the assumed
  decisions and plays the result.
- Assumed decisions are answered, not open: they go under "Assumed by the panel", and the approval
  record's open questions stay empty.
- Then take the path chosen in step 1, after core §10's hand-off steps for hands-off mode.
  - Stop at the plan: nothing is built, no issue is created, nothing is pushed.
  - Building: create the epic with `issue-tracking` and run the chosen team-lead skill; its report
    links the ledger.
- The owner's first read when back: the "Assumed by the panel" list. Any assumption they overturn
  is a `design-change` on whatever was built from it.
