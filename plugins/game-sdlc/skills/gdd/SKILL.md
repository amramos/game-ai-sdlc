---
name: gdd
description: Interview the user to design a game and write its Game Design Document (GDD), with research subagents finding comparable games, inspiration and market data along the way. Use when starting a new game, or when the user asks to design a game, write, draft or generate a GDD or game design doc. The user makes every design call; the skill asks, researches, suggests and writes.
argument-hint: "A one-line game idea, or nothing to start from scratch"
---

# GDD: from an idea to a design agents can build from

You run a design interview, send research agents to look things up while it runs, offer suggestions
where the user has a gap, and write the GDD once nothing important is left unasked. **Every design
decision is the user's.** Your job is to make each decision easy to make.

## 1. How the interview runs: rounds over the frontier

Think of the design as a tree: each decision unlocks the ones that depend on it. Work it in **rounds**.

- A round asks the **frontier**: every question whose prerequisites are already settled. A question
  that depends on an answer you haven't heard yet waits for a later round.
- Number every question and give **your recommended answer**, phrased so that "yes" accepts it. A
  tired user should be able to answer a round with "yes to all except 3".
- Ask **decisions**, never facts. If the answer can be looked up (what a comparable game does, how a
  genre usually prices), send a research agent instead of asking.
- After each round, recompute the frontier. Stop when it's empty: every branch visited, nothing
  silently assumed.

If a multiple-choice question tool is available (such as `AskUserQuestion`), use it for rounds of up
to four questions, recommended option first. Otherwise write the round as markdown:

```
**Q1. <title>.** <question, with the options if there are any>
→ Recommended: <answer and one line of why>
```

## 2. The tree to cover

Roughly in this order, though the frontier decides. Skip what doesn't apply to this game.

1. **Seed** — the idea in one line; why the user wants to make it; who the player is; ambition (jam,
   small release, commercial); team size; rough timeline.
2. **Genre and comparables** — genre(s) and 3–5 comparable games, each with *the one thing borrowed*.
3. **Pitch** — two sentences a stranger understands; the fantasy; the hook.
4. **Governing rule** — the one or two rules that decide every cut later, e.g. "theme and mechanic
   are the same idea". Ask for it explicitly; it's the most useful line in the document.
5. **Core loop** — the moment-to-moment loop, the session loop, the long loop. How a session ends;
   win and loss.
6. **Mechanics** — each system, what the player decides in it, and its exact terms. Every term goes
   in the glossary with one meaning.
7. **Progression and economy** — what carries over between sessions, what never does.
8. **Content** — what is authored and roughly how much (levels, events, cards, characters).
9. **Story and tone** — if there is any; how it is delivered.
10. **Art and audio direction** — style (pixel art, low poly, painterly…), camera and resolution, 2–5
    reference games or images with what each contributes, palette mood, audio mood. This feeds the
    `art-direction` skill later, so get concrete references.
11. **Platform and business** — engine, platforms, input devices, session length, price model and
    store (itch.io, Steam…).
12. **Scope boundary** — what is explicitly out, and ideas parked for later.
13. **Risks and open questions** — what could make this not fun, and what is still undecided.

## 3. Research agents

Dispatch research in the background as soon as a branch needs facts, and keep interviewing on the
rest of the frontier while they run. Only questions downstream of a running search wait for it.

Typical moments:
- after **genre and comparables**: how each comparable handles its core loop, what players praise and
  complain about in reviews;
- after the **pitch**: the market — similar titles on Steam and itch.io, their prices, tags, review
  counts, release years, and what made the successful ones stand out;
- on a **mechanic**: how two or three shipped games solved the same design problem.

Brief each agent with: the exact question; sources to prefer (store pages, reviews, postmortems,
GDC talks, wikis); and the return format — at most 300 words, each finding with a link and phrased
as "borrow …" or "avoid …". If the session has no web access, say so once, and mark any finding
from memory as unverified.

Bring findings into the next round as context for a question or as the reason for a
recommendation, never as a wall of text.

## 4. Suggestions fill gaps; they don't make decisions

When the user has no answer, offer one or two concrete suggestions grounded in research, labelled as
suggestions. Write a suggestion into the GDD only once the user accepts it. A question the user
leaves unanswered becomes an `[OPEN]` item with the options and your recommendation, never a quiet
default.

## 5. Write the GDD

Use [gdd-template.md](gdd-template.md). Put it at `docs/GDD.md` if a repository exists, otherwise at
`GDD.md` in the current folder (`setup-godot` moves it into place).

- Every section carries a marker: `[DESIGNED]` (specified, not built) or `[OPEN]` (needs a
  decision). `[BUILT]` appears later, as features ship.
- The **amendments** line under the title starts empty. Later reversals are dated there, each with
  its ADR, so the document keeps a visible design changelog.
- The **glossary** holds every game term with exactly one meaning. Agents will use these words
  literally in code and docs.
- No file paths, class names or code. The GDD says what the game is, not how it is built.
- Write in the language the user is writing in, unless they ask otherwise.

Then show a short summary: the pitch, the governing rule, the core loop in three lines, and the
`[OPEN]` items. Ask the user to confirm it reads right, and fix what doesn't.

## 6. Offer the next step

- **`prototype`** (optional) — try two or three versions of the core mechanic as quick web
  prototypes before committing to one. Recommend it when the core loop is novel or the user is
  unsure it's fun.
- **`setup-godot`** — create the repository, tools and agent rules for a Godot game. (Only Godot has
  a setup skill so far; for another engine, say so and offer to write the GDD-derived contract by hand.)

## Later ideas don't come back here

Once the GDD exists, new ideas (from playing the build, other games, playtesters, conversations)
enter through `feature-planning`, or through `design-change` when they reverse a decision. Don't re-run
this interview over a living GDD.
