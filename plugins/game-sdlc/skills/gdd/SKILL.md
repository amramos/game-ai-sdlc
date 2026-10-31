---
name: gdd
description: Interview the user to design a game and write its Game Design Document (GDD), with research subagents finding comparable games, inspiration and market data along the way. Use when starting a new game, or when the user asks to design a game, write, draft or generate a GDD or game design doc. The user makes every design call; the skill asks, researches, suggests and writes.
argument-hint: "A one-line game idea, or nothing to start from scratch"
---

# GDD (interactive)

Load the **`gdd-core`** skill (`game-sdlc:gdd-core` when installed as a plugin) and follow it in
**interactive mode**: you run the design interview, research agents look things up while it runs,
and **the user makes every design decision**. Your job is to make each decision easy to make.

## Make answering cheap

- If a multiple-choice question tool is available (such as `AskUserQuestion`), use it for rounds of
  up to four questions, your recommendation first and labelled "(Recommended)". Otherwise write the
  round as numbered markdown, so the user can answer "yes to all except 3".
- Settle the **pillars** with the user's own words (gdd-core §2, "Pillars"): offer six to eight
  candidates, let them pick three or write their own, and keep their meaning when you tidy the
  wording. Push for concrete art references too; vague answers here cost the most later.
- When the user has no answer, offer suggestions (gdd-core §4). If they still don't decide, it
  becomes `[OPEN]`, not a guess.

## Finish

Write the GDD (gdd-core §5) and run the builder's read (gdd-core §6); what it finds on the first
playable's path goes to the user as one more round. Then show a short summary: the pitch, the three
pillars with their test questions, the core loop in three lines, the first playable, and the
`[OPEN]` items. Ask the user to confirm it reads right, fix what doesn't, and offer the next steps
(gdd-core §7).

If the user would rather not answer rounds at all, offer `gdd-handsoff` instead.
