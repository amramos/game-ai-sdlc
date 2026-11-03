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

Everything after that runs without asking. If the owner is already gone, take option 1. If there's no
taste profile, offer it with this question, while the owner is still there (`taste-profile` §5).

## 2. You and the round reviewer

**You are the designer.** Write each round as you would for the owner (core §3): the frontier, a
recommendation per question tested against the pillars and consistent with the rest of the game.

Then **one round reviewer**, a fresh agent per round, answers it. It gets the round, the relevant
GDD sections and docs, and this brief:

- **As a skeptic:** what fails, what's missing, what's expensive, what contradicts a past decision.
- **As a first-time player**, a checklist answered for every question that changes what the player
  sees or does, one line each: what a player meeting this for the first time *sees*; what they
  could *misread*; what would *frustrate* them.
- **As the profile judge** (`taste-profile` §3): it reads the whole taste profile itself, in its own
  context, and returns its decisions under that section's rules (labels only; the explanations go
  only in the report to the owner). Where an option has room for a Signature item, it says so
  **among its answers**, as an addition to that question with `(profile)` and the label, never only
  in the explanation: you read the answers, not the explanation.
- For every question: **agree**, or **a different answer** with one line of reason. It never sees
  your reasoning beyond the one line per recommendation.

**Its model.** Another vendor's model when one is available. Run it with
`team-lead/scripts/codex_review.py` (`--probe` first; then `--repo <project> --prompt-file <round>
--out <file>`), asking it to end with `VERDICT: approve` when it agrees with every recommendation
and `VERDICT: request-changes` otherwise, and read only its answers from the file. Otherwise a
Claude model set explicitly: a tier below the session's, or the same model when there's none below
or the one below is smaller than mid-size (then say in the report that the review had no
independence of model). A Claude subagent is never
above the session's model; another vendor's model may be stronger.

## 3. Resolving a round

For each question:
- **the reviewer agrees** → take it; `Decided by: panel`;
- **it disagrees** → you decide, with a one-line reason that names the dissent; `Decided by: panel`.
  The reviewer's answer is the dissent, kept in the ledger row;
- **it proposes a `(profile)` addition** → take it when the game has room for it, recorded as
  `panel — assumed (profile)`; leaving it out is a dissent like any other;
- **the owner's by nature** — taste, scope, reversing a past decision, the GDD's pillars (setting
  them when missing, or choosing between two that pull apart), anything `AGENTS.md` reserves to the
  owner → still answered by the steps above, but recorded as `Decided by: panel — assumed`, and
  listed in the ledger's "Assumed by the panel" section **with the reviewer's answer as the
  runner-up** (when it agreed, the runner-up is the strongest option you rejected).

The first-time-player lines that point at something real become requirements, acceptance checks
or "pass and still fail" items (core §5), not just notes.

Never stall on an owner-only question, and never quietly drop it: answer it, mark it assumed, move on.

## 4. What stays the same as interactive mode

The walkthrough, sketches for layout forks (saved as files the owner can open later), the "pass
and still fail" check, the playable slice, the plan, and the two-way ledger review all still happen.
The round reviewer does not double as the two-way reviewer; use a fresh agent for that.

## 5. The result

- State: **PROVISIONALLY APPROVED** — every gate is provisional until the owner reads the assumed
  decisions and plays the result.
- Then take the path chosen in step 1. If building, create the epic with `issue-tracking` and run
  the chosen team-lead skill; its report links the ledger.
- The owner's first read when back: the "Assumed by the panel" list. Any assumption they overturn
  is a `design-change` on whatever was built from it.
