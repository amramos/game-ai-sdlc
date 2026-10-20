---
name: feature-planning
description: Plan a feature with the owner answering every question — rounds of questions with recommendations, a player walkthrough, sketches for layout decisions, and a short decisions ledger to approve — then turn the approved plan into an epic. Use when the owner wants to plan a feature, mechanic or change themselves.
argument-hint: "The feature or change to plan"
disable-model-invocation: true
---

# Feature planning (interactive)

Load the **`feature-planning-core`** skill (`game-sdlc:feature-planning-core` when installed as a
plugin) and follow it in **interactive mode**: the owner answers every round.

What this mode adds to the core:

## Make answering cheap

- If a multiple-choice question tool is available (such as `AskUserQuestion`), use it: up to four
  questions per call, your recommendation as the first option and labelled "(Recommended)". Put
  anything longer — the walkthrough, a sketch — in the message before the questions.
- Otherwise write the round as numbered markdown, each with "→ Recommended: …", so the owner can
  answer "yes to all except 2".
- Keep each round to the frontier. If a round would run past about six questions, split it by what
  the owner cares about most first (what the player sees), then the rest.
- The owner reads the ledger, not the plan. Write every answer into the ledger as it's given, so the
  approval at the end is a re-read, not a reconstruction.

## Before asking for approval

1. Show the ledger's decisions table, the walkthrough and the sketches — the three things the owner
   will actually judge.
2. For a big plan, report the two-way review in two lines: decisions missing from the plan (and how
   they were fixed), and invented decisions found (and the questions they became).
3. Ask for approval of the **ledger** explicitly, as one yes/no question. Anything other than a clear
   yes keeps the state at READY FOR APPROVAL.

## After approval

Offer the hand-off from the core skill's last step: record rulings, create the epic with
`issue-tracking`, and build it with `team-lead`.
