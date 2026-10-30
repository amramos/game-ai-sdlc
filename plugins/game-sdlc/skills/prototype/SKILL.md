---
name: prototype
description: Build two or three throwaway web prototypes of a game's core mechanic from its GDD, each taking a different approach, so the user and blind AI playtesters can try them before committing to one design. Use after a GDD exists and before setting up the real project, or when the user asks to prototype, try out or compare versions of a mechanic.
argument-hint: "The question the prototypes should answer, or nothing to derive it from the GDD"
---

# Prototype: try the core before building the game

A prototype answers **one question** — usually "is this core loop fun?" — as cheaply as possible.
Two or three variations that take different approaches to the core mechanic let the user compare
by playing instead of imagining. Everything here is throwaway.

A prototype the user can't follow answers nothing. Each one says what it tests, teaches its goal
and verbs in a few guided steps, and looks like a game: the state on a board, not in a paragraph.

This runs between `gdd` and `setup-godot`: a prototype can change the design or kill the idea, and
a repository set up first would be wasted work.

**Hands-off form** (when `gdd-handsoff` runs it): the panel settles §1 instead of the user, the
variations are played by blind AI playtesters only, and the pick in §4 is made from their reports
against the bar `gdd-handsoff` sets. Everything else is the same, the card included: the user may
play the winner later.

## 1. Settle the question and the variations

Read the GDD's pitch, pillars, core loop and camera and medium. Then agree with the user, in one
short round:

- **The question.** One sentence the prototypes must answer, e.g. "Does choosing what to leave
  unhandled feel tense rather than unfair?"
- **What it doesn't test.** Usually feel, art, sound, balance and content volume. Naming them tells
  the user what not to judge. When feel *is* the question, say so, and the prototype spends on it.
- **The variations.** Two or three, each a **different approach to the core mechanic** — e.g.
  real-time versus turn-based triage, or hidden versus visible odds. Not the same loop at different
  tuning, and not different art or framing. When the GDD leaves the camera or space open
  (first-person 3D against a top-down grid, say), the same mechanic in two cameras is a fair pair:
  otherwise the prototype quietly decides the camera. Recommend a set, and say in one line how each
  differs from the others.
- **Done means.** How long a session lasts (aim for 3–5 minutes) and what "fun" would look like.

## 2. Build each variation as one HTML file

Each prototype is a **single self-contained `.html` file** that opens in a browser with no build step.

**The card.** Before play, the page shows the user three lines: *Tests* (the question), *Ignore*
(what it doesn't test) and *This variation* (how it differs from the others). It lives in the page
markup, never in the rules block, and is hidden when the URL has `?blind`, so playtesters never
see it: a playtester told what's under test reports what it was told.

**A tutorial, then a free round.** The tutorial replaces any rules text: 3–5 steps on a fixed,
scripted first deal, so every step is sure to work.

- Step one shows the goal and how you lose, before any other term.
- Each step gives one instruction, the player does it, and one line says what happened and why.
  During a step `actions()` offers only that step's action, and the page highlights its target.
- At most one new term per step, introduced when the player first touches what it names.
- Teach the goal and the verbs, never the best move. Strategy is the free round's to discover.
- Then a full round with no coach. A `?` key shows the step texts again; the restart key starts a
  round without the tutorial. `?tutorial=off` in the URL starts without it too.

If the core can't be taught in five steps, don't add a sixth: note how many steps and terms it
needed, and report it in §4. That's a finding about the mechanic, not a page to fix.

**Looks like the game, at greybox quality.**

- Draw in the GDD's camera and medium: a 2D canvas for a 2D game, three.js only when the game is 3D
  (loaded from a CDN at an exact version, for example
  `https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js`). Flat-coloured shapes are
  enough; no art and no sound unless the question is about feel.
- State is drawn where it lives — cards in a hand, seats around a table, a bar over whoever it
  belongs to — and the player acts on the world (clicks the card, presses the key), not on a list of
  buttons.
- Every action answers with feedback where it happened: something moves, flashes or changes.
- Words follow `game-ui`'s "show before telling": a label names and doesn't explain, and each
  screen has a word budget.

**The rules, and a text interface for AI playtesters.**

- Plain JavaScript; tuning numbers grouped at the top so they're easy to change.
- The same session length and the same win/loss framing across variations, so they compare fairly.
- `window.proto` gives the text interface:
  - `describe()` returns the visible state as plain text, with the current tutorial step's text;
  - `actions()` returns the actions legal right now;
  - `act(name)` performs one and returns what happened;
  - `restart({ tutorial })` starts again, with or without the tutorial.

  The page and this interface show the same facts; never expose hidden state. They don't share a
  layout: the page is never `describe()` printed into a box with `actions()` as buttons.
- The rules, the tutorial's steps and `window.proto` go in one `<script id="proto-rules">` block that
  never touches the page (no `document`, no timers that draw); the drawing and input code goes in a
  second block that reads from it. Then [scripts/proto_cli.mjs](scripts/proto_cli.mjs) plays the
  rules headless, with Node 18 or later, for playtesters and solvers without a browser:
  `node <this skill>/scripts/proto_cli.mjs [--no-tutorial] prototypes/<variation>.html` starts a
  session (`describe`, `actions`, `act <name>`, `quit`); commands given after the file run in order
  and exit.

Put the files in a `prototypes/` folder outside any game repository (or the scratchpad), named
`<variation>.html`. If an artifact or page publishing tool is available, publish each one as a
private page so it can be played from a link.

## 3. Playtest: the user and blind AI playtesters

**The user** plays each variation: the tutorial, then a free round. Afterwards, ask three questions
per variation: what was the goal, when was it most interesting, and would you play another round
(1–10)?

**The ten-second check** comes first. A fresh agent that knows nothing about the game gets one
screenshot of a variation's first screen with no tutorial (`?blind&tutorial=off`) and says what the
goal is and what it would do first. It tests what the screen teaches on its own.

**AI playtesters** play each variation **blind**: they get the page, or the headless runner on it,
never the GDD or this conversation. Start each one in a separate agent whose prompt contains only
that, ideally from a folder with no project instruction files — an agent that has read the design
plays like its author, not like a player. Each variation gets a panel of at least three:

- **two with the tutorial**: one on the real page through screenshots and input (`?blind`), with a
  browser tool if the session has one, and one headless on the runner;
- **at least one cold**, with no tutorial (`?blind&tutorial=off`, or the runner's `--no-tutorial`)
  and nothing but the screen.

With no browser tool, all of them play headless, and the comparison says the page went unplayed.
Ask each one to play until the session ends, then report:

- what they think the goal is and what the best strategy was;
- the most and least interesting decision they made;
- where they got stuck or confused, and where the screen misled them;
- how much they'd want another round (1–10), with one line of why.

Run playtesters for different variations in parallel. Quote them in the comparison; don't summarise
away disagreement.

**Reading the tutorial arms against the cold one:**

- Both state the goal correctly: the screen already teaches. Keep the tutorial short.
- The tutorial arm gets it and the cold one doesn't: the tutorial carries it, which is fine. What
  the cold one misread is what the real game's interface will have to teach.
- The tutorial arm gets it wrong: the tutorial fails, or the core is too complex to teach in five
  steps. That's a finding about the mechanic as much as the page.
- The cold one enjoys it more: the tutorial gives away the discovery. Cut it to the goal and verbs.

One playtester per arm is a pointer, not a measurement; say so when quoting them.

## 4. Pick, record, discard

Show a short comparison: for each variation, the user's verdict, the playtesters' verdicts in one
line each, **the steps and terms it needed before its first real choice**, the ten-second check and
the reading of the tutorial arms, **which pillars the playtesters felt without being told** (compare
their reports with the GDD's pillars; never show the pillars to them), **whether each mechanic
earned its place** (`gdd-core` §2; where the rules can be searched, run a solver over the runner,
since it catches what discussion misses), and your read of what the question's answer is. The
**user picks one**, or a merge of two.

Then:
- update the GDD's core loop and mechanics to the chosen approach, and add a dated line to its
  amendments header ("<date> — core loop chosen by prototype: <one line>");
- move any new uncertainty into the GDD's open questions, including what the cold playtester
  misread, for the game's first-time experience;
- **take only the mechanic's lessons into the GDD.** The prototype's screen is a greybox built to
  make the mechanic legible; it never becomes the game's interface, which the GDD's interface
  section and `art-direction` decide;
- **throw the other variations away.** Don't keep them, don't record them as rejected directions.

## 5. Next

Offer `setup-godot` (or the setup for the chosen engine) to create the real project — with its
"use every recommendation" fast path when this came from `gdd-handsoff`.
