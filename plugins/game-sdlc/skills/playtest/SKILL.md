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

- Start each playtester **from a folder with no project instruction files** (`AGENTS.md`,
  `CLAUDE.md`, memory). A subagent started inside the repository loads them automatically and knows
  every secret before it plays.
- Give each its own copy of the game's save data or profile, so playtesters don't share progress.
- Their prompt: the game's name, how to start and send input, a goal like "play one full session
  as a new player would", and the report format below. Nothing about mechanics or intent.

Run two to four in parallel. Each reports:

- what they think the goal is, and the strategy they ended up using;
- the most and least interesting decision;
- where they got stuck or confused, with the screenshot or state at that moment;
- bugs (anything that looked broken);
- how much they'd want another session (1–10), with one line of why.

Then write a short panel report: what several playtesters agree on first, single-player findings
after, quotes kept verbatim, and disagreement left visible rather than averaged.

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
