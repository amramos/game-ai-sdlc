---
name: gdd-core
description: The shared method behind gdd and gdd-handsoff — the design tree a GDD has to cover, rounds over its frontier, research agents for comparables and the market, suggestions versus decisions, and the GDD template with its markers, glossary and scope boundary. Loaded by those two skills; not called directly by the user.
user-invocable: false
---

# GDD: the shared method

Turns an idea into a GDD that agents can build from. The method is the same in both modes; only
**who answers the rounds** differs:

- **interactive** (`gdd`): the user answers every round;
- **hands-off** (`gdd-handsoff`): a panel of agents answers, and the user reacts to a short summary.

Either way, decisions are made by whoever answers the round. Facts are looked up by research agents,
never asked.

## 1. Rounds over the frontier

Think of the design as a tree: each decision unlocks the ones that depend on it. Work it in **rounds**.

- A round asks the **frontier**: every question whose prerequisites are already settled. A question
  that depends on an answer not yet given waits for a later round.
- Number every question and give **a recommended answer**, phrased so that "yes" accepts it.
- Ask **decisions**, never facts. If the answer can be looked up (what a comparable game does, how a
  genre usually prices), send a research agent instead (§3).
- After each round, recompute the frontier. Stop when it's empty: every branch visited, nothing
  silently assumed.

Round format when written as markdown:

```
**Q1. <title>.** <question, with the options if there are any>
→ Recommended: <answer and one line of why>
```

## 2. The tree to cover

Roughly in this order, though the frontier decides. Skip what doesn't apply.

1. **Seed** — the idea in one line; why make it; who the player is; ambition (jam, small release,
   commercial); team size; rough timeline.
2. **Genre and comparables** — genre(s) and 3–5 comparable games, each with *the one thing borrowed*.
3. **Pitch** — two sentences a stranger understands; the fantasy; the hook.
4. **Pillars** — the three feelings the whole game is built to give, settled right after the pitch
   (see "Pillars" below). Every later skill judges work against them.
5. **Core loop** — the moment-to-moment loop, the session loop, the long loop; how a session ends;
   win and loss.
6. **Mechanics** — each system, what the player decides in it, and its exact terms. Every term goes
   in the glossary with one meaning.
7. **Progression and economy** — what carries over between sessions, what never does.
8. **Content** — what is authored and roughly how much (levels, events, cards, characters).
9. **Story and tone** — if any; how it is delivered. Plot lives here, never in the pillars.
10. **Art and audio direction** — style, camera and resolution, 2–5 reference games or images with
    what each contributes, palette mood, audio mood. This feeds `art-direction` later.
11. **Interface** — how information reaches the player: density (minimal unless the genre or a pillar
    asks for more); where words live (in the world or on a HUD); how much reading the game asks,
    which pillar wants it and in whose voice; what the player is never told, including how summaries
    treat their choices; the loudest moment and the space kept for it; the smallest readable size;
    how the comparables present information. This decides what reaches the player and why; how it
    looks is `art-direction`'s job. The `game-ui` skill holds the defaults these choices confirm or
    override.
12. **Platform and business** — engine, platforms, input devices, session length, price model and
    store (itch.io, Steam…).
13. **Scope boundary** — what is explicitly out, and ideas parked for later.
14. **Risks and open questions** — what could make this not fun, and what is still undecided.

### Pillars

Suggest them; don't impose them. Draft **six to eight candidates** from the concept, the comparables
and the games the user loves, and let the one answering pick three, edit them, or write their own.

- **A name, one line and a test question.** The line says the feeling and where the player gets it;
  the question is what any feature, screen or sound is tested against.
- **Plain, not pretty.** Pillars guide decisions; a line that adds meaning to sound better is cut.
- **For the whole game.** A pillar never prescribes the interface, art or audio ("the interface does
  X" never appears in one); each discipline derives its own rules from the pillars.
- **Not plot.** Story beats go in the story branch.
- **Specific to this game.** A candidate that would fit any game ("fun", "immersive") is dropped.
- **Refining keeps the meaning.** When the user's own words become a pillar, keep their words beside
  it and flag any premise you added.

For example: **Scarcity forces choices.** There's never enough fuel for everyone, so every trip
leaves someone behind. *Test: could the player do everything here without giving something up?*

When two pillars pull apart later, the owner decides at that moment, in the feature's ledger; no rule
is written in advance. Changing a pillar after the GDD exists goes through `design-change`.

## 3. Research agents

Dispatch research in the background as soon as a branch needs facts, and keep working the rest of the
frontier while it runs. Only questions downstream of a running search wait for it.

Typical moments:
- after **genre and comparables**: how each comparable handles its core loop, what players praise
  and complain about in reviews;
- after the **pitch**: the market — similar titles on Steam and itch.io, their prices, tags, review
  counts, release years, and what made the successful ones stand out;
- after the **pillars**: how two or three comparables present information — screenshots of their main
  screen and their between-session or summary screens, each with the one thing to borrow. This feeds
  the interface branch;
- on a **mechanic**: how two or three shipped games solved the same design problem.

Brief each agent with the exact question, sources to prefer (store pages, reviews, postmortems, GDC
talks, wikis), and the return format: at most 300 words, each finding with a link and phrased as
"borrow …" or "avoid …". Without web access, say so once and mark findings from memory as unverified.

Bring findings into the next round as context or as the reason for a recommendation, never as a wall
of text.

## 4. Suggestions fill gaps; they don't make decisions

When the one answering has no answer, offer one or two concrete suggestions grounded in research,
labelled as suggestions. A suggestion enters the GDD only once it's accepted. A question left
unanswered becomes an `[OPEN]` item with the options and the recommendation, never a quiet default.

## 5. Write the GDD

Use [gdd-template.md](gdd-template.md). Put it at `docs/GDD.md` if a repository exists, otherwise
`GDD.md` in the current folder (`setup-godot` moves it into place).

- Every section carries a marker: `[DESIGNED]` (specified, not built) or `[OPEN]` (needs a decision).
  `[BUILT]` appears later, as features ship.
- The **amendments** line under the title starts empty. Later reversals are dated there, each with
  its ADR, so the document keeps a visible design changelog.
- The **glossary** holds every game term with exactly one meaning; agents use these words literally.
- No file paths, class names or code. The GDD says what the game is, not how it is built.
- Write in the language the user writes in, unless they ask otherwise.

## 6. Next steps to offer

- **`prototype`** (optional) — try versions of the core mechanic as quick web prototypes before
  committing. Recommend it when the core loop is novel or nobody is sure it's fun.
- **`setup-godot`** — create the repository, tools and agent rules for a Godot game. (Only Godot has
  a setup skill so far; for another engine, say so.)

**Carry the mode forward.** After `gdd-handsoff`, recommend `setup-godot`'s "use every
recommendation" fast path and say the project will be set to work hands-off, so every later skill
offers its hands-off variant first. After `gdd`, recommend the normal round.

## Later ideas don't come back here

Once the GDD exists, new ideas enter through `feature-planning`, or `design-change` when they reverse
a decision. Don't re-run this over a living GDD.
