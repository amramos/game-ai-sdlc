---
name: feature-planning-handsoff
description: Plan a feature without the owner in the loop — a panel of agents (a designer, a player advocate and a skeptic from another model vendor) answers every round of questions, decisions that belong to the owner are marked as assumed, and the plan comes out provisionally approved, optionally going straight on to be built. Use when the owner wants a feature planned (and possibly built) while they are away: when they invoke it, ask for hands-off planning in their own words, or accept it as the next step offered in the project's hands-off working style. Never pick it on your own initiative.
argument-hint: "The feature or change to plan"
---

# Feature planning (hands-off)

Load the **`feature-planning-core`** skill (`game-sdlc:feature-planning-core` when installed as a
plugin) and follow it in **hands-off mode**: a panel answers the rounds instead of the owner.

## 1. The one question asked up front

Before the owner leaves, ask a single question — what happens after the plan:

1. **Stop at the plan** — the owner reads the ledger and decides.
2. **Build it with `team-lead`** (recommended) — PRs wait for the owner to merge.
3. **Build it with `team-lead-handsoff`** — reviewed PRs merge to `main` without the owner.

Everything after that runs without asking. If the owner is already gone, take option 1.

## 2. The panel

Three panelists, each a separate agent with its own brief, so their views stay independent:

| Panelist | Answers from the point of view of | Model |
|---|---|---|
| **Designer** | the GDD, its pillars (every answer tested against them), and consistency with the rest of the game | the session's model |
| **Player advocate** | a player meeting this for the first time: clarity, fun, frustration | a different model from the designer's |
| **Skeptic** | what fails, what's missing, what's expensive, what contradicts a past decision | a model from another vendor when available (e.g. Codex through its Claude Code plugin); otherwise a third model |

Every panelist's model is set explicitly, and none is more expensive than the session's: "a
different model" means a cheaper one here.

Each panelist gets the same round (the frontier, with your recommendation per question), the
relevant GDD sections and docs, and answers every question with a choice and one line of reason.
They don't see each other's answers.

## 3. Resolving a round

For each question:
- **unanimous** → take it; `Decided by: panel`;
- **split** → you decide, with a one-line reason that names the dissent; `Decided by: panel`;
- **the owner's by nature** — taste, scope, reversing a past decision, the GDD's pillars (setting
  them when missing, or choosing between two that pull apart), anything `AGENTS.md` reserves to the
  owner → still answered by the steps above, but recorded as
  `Decided by: panel — assumed`, and listed in the ledger's "Assumed by the panel" section.

Never stall on an owner-only question, and never quietly drop it: answer it, mark it assumed, move on.

## 4. What stays the same as interactive mode

The walkthrough, sketches for layout forks (saved as files the owner can open later), the "pass
and still fail" check, the playable slice, the plan, and the two-way ledger review all still happen.
The skeptic panelist does not double as the two-way reviewer; use a fresh agent for that.

## 5. The result

- State: **PROVISIONALLY APPROVED** — every gate is provisional until the owner reads the assumed
  decisions and plays the result.
- Then take the path chosen in step 1. If building, create the epic with `issue-tracking` and run
  the chosen team-lead skill; its report links the ledger.
- The owner's first read when back: the "Assumed by the panel" list. Any assumption they overturn
  is a `design-change` on whatever was built from it.
