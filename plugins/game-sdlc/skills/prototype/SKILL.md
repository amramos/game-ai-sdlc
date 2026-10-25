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

Read the GDD's pitch, pillars and core loop. Then agree with the user, in one short round:

- **The question.** One sentence the prototypes must answer, e.g. "Does choosing what to leave
  unhandled feel tense rather than unfair?"
- **The variations.** Two or three, each a **different approach to the core mechanic** — e.g.
  real-time versus turn-based triage, or hidden versus visible odds. Not the same loop at different
  tuning, and not different art. When the GDD leaves the camera or space open (first-person 3D
  against a top-down grid, say), the same mechanic in two cameras is a fair pair: otherwise the
  prototype quietly decides the camera. Recommend a set and say what each one tests.
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
- the rules and `window.proto` in one `<script id="proto-rules">` block that never touches the page
  (no `document`, no timers that draw); the drawing and input code goes in a second block that reads
  from it. Then [scripts/proto_cli.mjs](scripts/proto_cli.mjs) plays the rules headless, with Node 18
  or later, for playtesters and solvers without a browser:
  `node <this skill>/scripts/proto_cli.mjs prototypes/<variation>.html` starts a session (`describe`,
  `actions`, `act <name>`, `quit`); commands given after the file run in order and exit.
- a **3D variation** stays one file too: load three.js from a CDN at an exact version (for example
  `https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js`) in the drawing block, with
  flat-coloured boxes for the world. The rules block stays the same as a 2D variation's, so the
  headless runner and solvers work on either.

Put the files in a `prototypes/` folder outside any game repository (or the scratchpad), named
`<variation>.html`. If an artifact or page publishing tool is available, publish each one as a
private page so it can be played from a link.

## 3. Playtest: the user and blind AI playtesters

**The user** plays each variation. Afterwards, ask three questions per variation: what was the goal,
when was it most interesting, and would you play another round (1–10)?

**AI playtesters** play each variation **blind**: they get the page, or the headless runner on it,
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
line each, **which pillars the playtesters felt without being told** (compare their reports with the
GDD's pillars; never show the pillars to them), **whether each mechanic earned its place**
(`gdd-core` §2; where the rules can be searched, run a solver over the runner, since it catches what
discussion misses), and your read of what the question's answer is. The
**user picks one**, or a merge of two.

Then:
- update the GDD's core loop and mechanics to the chosen approach, and add a dated line to its
  amendments header ("<date> — core loop chosen by prototype: <one line>");
- move any new uncertainty into the GDD's open questions;
- **take only the mechanic's lessons into the GDD.** The prototype's page layout is a web page by
  necessity; it never becomes the game's interface, which the GDD's interface section and
  `art-direction` decide;
- **throw the other variations away.** Don't keep them, don't record them as rejected directions.

## 5. Next

Offer `setup-godot` (or the setup for the chosen engine) to create the real project — with its
"use every recommendation" fast path when this came from `gdd-handsoff`.
