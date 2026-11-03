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
  - Labels only above the line; explanations go below it.
  - Where an option has room for a Signature item, it writes the addition **among its answers**:
    the change in game terms (what is added, where, how often), then `(profile)` and the label.
- For every question: **agree**, or **a different answer** with one line of reason. It never sees
  your reasoning beyond the one line per recommendation.
- **The reply's format**, given in the brief word for word:

  ```
  Q<n>: agree — <one line of reason from the game>
  Q<n>: different: <answer> — <one line of reason from the game>
  Q<n>: agree | different: <answer> — (profile) <label>
  Player (Q<n>): sees <…> / misreads <…> / frustrated by <…>
  Q<n> addition: <the change in game terms> (profile) <label>
  Skeptic: <what fails, what's missing, what's expensive>
  VERDICT: approve | request-changes
  === EXPLANATION (owner only) ===
  <which entry, and why, for each (profile) line>
  ```

  - One `Q<n>` line per question. The `(profile)` form is only for an answer whose sole reason is
    the profile; its explanation goes below the line.
  - `VERDICT: approve` when it agrees with every recommendation, `request-changes` otherwise.

  A `Q<n>` line ending in `(profile)` and a label is recorded as `panel — assumed (profile)` (§3).

**Read the reply only up to the `=== EXPLANATION (owner only) ===` line**, never by opening the
whole file:

- check that the line is there: `grep -c "^=== EXPLANATION (owner only) ===" <out>`;
- read up to it: `sed -n '1,/^=== EXPLANATION (owner only) ===/p' <out>`;
- the rest goes into the report to the owner unread.

**A reply with no such line**: don't read it. Run the reviewer once more with the same round and the
format repeated. If the second reply has no line either, decide the round yourself, record its
answers as `panel — assumed`, and say in the report that the round had no usable review.

An example of the part you read, for a round about a cooking game's new order board:

```
Q1: agree — the board already reads left to right, as the GDD's kitchen layout does
Q2: different: show three orders, not five — five orders cover the stove at 1280×720
Player (Q2): sees the timer before the dish / misreads the colour bar as heat / frustrated by an order expiring off-screen
Q3 addition: the regular customer's order returns on the third day with a changed side dish, unannounced (profile) Signature 1
Skeptic: Q4's queue rule has no case for two orders that expire on the same tick
VERDICT: request-changes
```

**Its model.**

- Another vendor's model when one is available. Run it with `team-lead/scripts/codex_review.py`:
  `--probe` first, then `--repo <project> --prompt-file <round> --out <file>`.
- Otherwise a Claude model set explicitly: a tier below the session's.
  - Use the same model when there's none below, or when the one below is smaller than mid-size.
    Then say in the report that the review had no independence of model.
  - A Claude subagent is never above the session's model; another vendor's model may be stronger.

## 3. Resolving a round

For each question:

- **The reviewer agrees** → take it; `Decided by: panel`.
- **It disagrees** → you decide, with a one-line reason; `Decided by: panel`. The rejected answer is
  the **dissent**, written in the row's Dissent column:
  - when you keep your recommendation, the dissent is the reviewer's answer;
  - when you adopt the reviewer's answer, the dissent is your original recommendation.
- **It proposes a `(profile)` addition** → take it when the game has room for it.
  - Record it as `panel — assumed (profile)`, written as the concrete game change (`taste-profile`
    §3, "What gets recorded").
  - Leaving it out is a dissent like any other: the addition goes in the Dissent column, by its game
    change and label.
- **Its only reason is the profile** (a `Q<n>` line ending in `(profile)` and a label) → whichever
  way you decide, the row is `panel — assumed (profile)` when you take that answer, or carries the
  answer in its Dissent column when you don't.
- **Its answer carries profile text** (a quote or a paraphrase above the line) → take only the
  decision and the label, word the row yourself, and note the slip in the report.
- **The owner's by nature** → still answered by the steps above, but recorded as `Decided by:
  panel — assumed` (or `panel — assumed (profile)` when a profile entry settled it: that label
  always wins). It is listed in the ledger's "Assumed by the panel" section **with a runner-up**,
  the answer you didn't take:
  - when the reviewer disagreed, its answer if you kept yours, or your original recommendation if
    you adopted its answer;
  - when it agreed, the strongest option you rejected.

  The owner's by nature means:
  - taste;
  - scope;
  - reversing a past decision;
  - the GDD's pillars: setting them when missing, or choosing between two that pull apart;
  - anything `AGENTS.md` reserves to the owner.

  **When the owner's request itself asks for a reversal**, the reversal is the owner's (`owner`);
  whatever the request leaves open about it is assumed.

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
