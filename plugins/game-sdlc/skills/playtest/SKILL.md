---
name: playtest
description: Playtest a game build — run a panel of blind AI playtesters (playing the real window through screenshots and input, or the game's rules as text), and turn the owner's own playtest into a findings document that maps each finding to its fix and its test. Use after a feature lands, before a release, or when the user asks for a playtest, playtesters, a play session or feedback on how the game plays.
argument-hint: "What to playtest, and optionally: owner | ai | both"
---

# Playtest

Automated tests say the code does what it was told. Only play says whether it was told the right
thing. **A green suite is not acceptance**, and every gate stays provisional until the owner has
played the build. AI playtesters are cheap and fast; they find confusion and broken flows early,
but they don't replace the owner's verdict.

## 1. Two ways an agent can play

| Mode | What the agent does | Good for | Cost |
|---|---|---|---|
| **Real window** | plays the actual build: takes screenshots with numbered click targets, sends input | onboarding, readability, "can a newcomer find the button" | minutes per turn, a screenshot per step |
| **Headless text** | plays the game's rules through a text interface (state as text, legal actions, act) | balance, learning curves, long sessions, many runs | seconds per action |

Both need support in the game:

- **Real window** needs a dev-only bridge in the build: it lists clickable targets with numbers,
  writes a screenshot with those numbers drawn on it, and accepts "click 7", "press ui_accept",
  "wait". Keep it behind a debug flag; never ship it.
- **Headless text** needs the game's rules runnable without the scene tree, plus a small text layer:
  `describe()` (what a player can see — never hidden state), `actions()`, `act(name)`.

If the game has neither yet, say so and offer to add the one that fits the question being asked.

## 2. The AI panel is blind by default

An agent that has read the design plays like its author. AI playtesters therefore get **only** the
build (or the text interface) and the instructions a player would see.

- **Run [scripts/blind_setup.py](scripts/blind_setup.py) once per playtester** and start it in
  the folder it prints. A subagent started inside the repository loads `AGENTS.md`, `CLAUDE.md` and
  the rest automatically, and knows every secret before it plays.

  ```bash
  python <this skill>/scripts/blind_setup.py <build or page> [--save <fresh save>] [--base <folder>]
  ```

  It copies only the build and the save into a new empty folder, so each playtester has its own
  progress. Then it checks that no `AGENTS.md`, `CLAUDE.md`, `.claude/`, `.codex/`, `.github/` or
  `docs/` is inside the folder or above it, and prints `folder:` and `launch:` lines. If a check
  fails it exits non-zero and leaves no folder. Don't start that playtester anywhere else: rerun
  with `--base` pointing outside every project. A `warning:` line names a user-level instruction
  file that loads in every folder; read it and make sure it says nothing about this game.
- Their prompt: the game's name, the launch command and how to send input, a goal like "play one
  full session as a new player would", and the report format below. Nothing about mechanics or
  intent.

Run two to four in parallel, with at least one **cold**: no tutorial and no instructions beyond the
screen. Before its first input, the cold playtester writes its **ten-second read**: from the first
screen alone, what it thinks the goal is and what it would do first. That read is the check of what
the screen teaches on its own; no separate agent makes it.

**Which mode each plays.** Real-window play costs the most and needs the strongest model (vision
and a long horizon), so spend it where the question needs it:

- When several builds or variations are compared, the real-window playtester plays the **leading**
  one, and headless playtesters play the others, unless the question is readability (what the
  screen shows, whether a newcomer finds the button). Then every one gets a real-window playtester.
- When the model available to playtesters is below mid-size, prefer headless playtesters: small
  models play a real window badly and their reports blur what the build did with what they misread.
  Say in the report that the window went unplayed.

Each reports:

- the cold playtester only: its ten-second read, unchanged since it wrote it;
- what they think the goal is, and the strategy they ended up using;
- the most and least interesting decision;
- where they got stuck or confused, with the screenshot or state at that moment;
- where the game guided them (a tutorial, a scripted sequence, a forced move): whether they knew
  they were being guided, and any guided moment they took for a free choice;
- bugs (anything that looked broken);
- what they skipped reading;
- what they understood without reading;
- which words they didn't understand, and whether they wanted to find out what they meant;
- how much they'd want another session (1–10), with one line of why.

The three reading questions catch walls of text and restated information, show what the screens
carry on their own, and separate intrigue that works (they wanted to find out) from confusion that
blocks (they needed the word and didn't have it).

Then write a short panel report: what several playtesters agree on first, single-player findings
after, quotes kept verbatim, and disagreement left visible rather than averaged. End it with
**Pillars, felt or not**: for each of the GDD's pillars, where playtesters described that feeling
without being told, or that nobody did. The playtesters never see the pillars.

If the interface is still placeholder (grey boxes, unstyled text), say so at the top of the report:
players judge whatever they see as final, so their reading findings mean less.

An informed playtester (one that has read the GDD) is useful for one different question — "does
this match the design?" — and must be labelled as informed in the report.

## 3. The owner's playtest is the gate

When the owner plays, capture their findings in a document from
[findings-template.md](findings-template.md), in the repository next to the plan
(`docs/playtests/<date>-<what>.md`):

1. **The owner's findings, enriched.** For each: what they saw, the expected behavior, the likely
   cause found in the code, and a severity. Keep the owner's own words.
2. **A second reviewer's additions** — a model from another vendor when available — marked as such.
3. **The iteration record.** After fixing, map **every finding to its fix and to the test that now
   pins it**. Look for shared causes first: several findings are often one bug in a shared
   abstraction, and fixing it there fixes ordinary play too.

The feature stays `In Review` until the owner plays the fixed build and says it's accepted.

## 4. Honest numbers

When a playtest or simulation measures something against a target (win rate, session length), report
the miss as a miss. Never fold a missed target into a passing summary.
