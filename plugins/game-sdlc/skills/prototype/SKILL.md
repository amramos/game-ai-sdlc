---
name: prototype
description: Build two or three throwaway web prototypes of a game's core mechanic from its GDD, each taking a different approach, so the user and blind AI playtesters can try them before committing to one design. Use after a GDD exists and before setting up the real project, or when the user asks to prototype, try out or compare versions of a mechanic.
argument-hint: "The question the prototypes should answer, or nothing to derive it from the GDD"
---

# Prototype: try the core before building the game

A prototype answers **one question** — usually "is this core loop fun?" — as cheaply as possible.
Two or three variations that take different approaches to the core mechanic let the user compare
by playing instead of imagining. Everything here is throwaway.

This runs between `gdd` and `setup-godot`: a prototype can change the design or kill the idea, and
a repository set up first would be wasted work.

**Hands-off form** (when `gdd-handsoff` runs it): the panel settles §1 instead of the user, the
variations are played by blind AI playtesters only, and the pick in §4 is made from their reports
against the bar `gdd-handsoff` sets. Everything else is the same.

## 1. Settle the question and the variations

Read the GDD's pitch, governing rule and core loop. Then agree with the user, in one short round:

- **The question.** One sentence the prototypes must answer, e.g. "Does choosing what to leave
  unhandled feel tense rather than unfair?"
- **The variations.** Two or three, each a **different approach to the core mechanic** — e.g.
  real-time versus turn-based triage, or hidden versus visible odds. Not the same loop at different
  tuning, and not different art. Recommend a set and say what each one tests.
- **Done means.** How long a session lasts (aim for 3–5 minutes) and what "fun" would look like.

## 2. Build each variation as one HTML file

Each prototype is a **single self-contained `.html` file** that opens in a browser with no build step:

- shapes and text only — no art, no sound, no menus beyond a one-line instruction and a restart key;
- a few hundred lines of plain JavaScript; tuning numbers grouped at the top so they're easy to change;
- the same session length and the same win/loss framing across variations, so they compare fairly;
- a **text interface for AI playtesters** on `window.proto`:
  - `describe()` returns the visible state as plain text;
  - `actions()` returns the actions legal right now;
  - `act(name)` performs one and returns what happened.

  The visible page and this interface show the same information; never expose hidden state.

Put the files in a `prototypes/` folder outside any game repository (or the scratchpad), named
`<variation>.html`. If an artifact or page publishing tool is available, publish each one as a
private page so it can be played from a link.

## 3. Playtest: the user and blind AI playtesters

**The user** plays each variation. Afterwards, ask three questions per variation: what was the goal,
when was it most interesting, and would you play another round (1–10)?

**AI playtesters** play each variation **blind**: they get the page or its `window.proto` interface
and the one-line instruction, never the GDD or this conversation. Start each one in a separate
agent whose prompt contains only that, ideally from a folder with no project instruction files —
an agent that has read the design plays like its author, not like a player. Ask each one to play
until the session ends, then report:

- what they think the goal is and what the best strategy was;
- the most and least interesting decision they made;
- where they got stuck or confused;
- how much they'd want another round (1–10), with one line of why.

Run playtesters for different variations in parallel. Quote them in the comparison; don't summarise
away disagreement.

## 4. Pick, record, discard

Show a short comparison: for each variation, the user's verdict, the playtesters' verdicts in one
line each, and your read of what the question's answer is. The **user picks one**, or a merge of two.

Then:
- update the GDD's core loop and mechanics to the chosen approach, and add a dated line to its
  amendments header ("<date> — core loop chosen by prototype: <one line>");
- move any new uncertainty into the GDD's open questions;
- **throw the other variations away.** Don't keep them, don't record them as rejected directions.

## 5. Next

Offer `setup-godot` (or the setup for the chosen engine) to create the real project — with its
"use every recommendation" fast path when this came from `gdd-handsoff`.
