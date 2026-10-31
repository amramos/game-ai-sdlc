---
name: gdd-core
description: The shared method behind gdd and gdd-handsoff — the design tree a GDD has to cover, rounds over its frontier, research agents for comparables and the market, suggestions versus decisions, the GDD template with its markers, glossary, worked example and first playable, and a blind builder's read before handover. Loaded by those two skills; not called directly by the user.
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
6. **Mechanics** — each system, what the player decides in it, its values and its exact terms. Every
   term goes in the glossary with one meaning. Where rules can act at the same moment, the order they
   apply in, and how the conflicts a builder would otherwise guess resolve: something used up, how
   long a temporary effect lasts, an effect whose target is gone, a loss during a reward, ties. Each
   mechanic earns its place (see below).
7. **Progression and economy** — how the player's means grow: what they gain within a session and
   across sessions, where each gain comes from, what they spend or give up for it, how often gains
   arrive, and what carries over and what never does. A game with no economy says so in one line.
8. **Content** — what is authored and roughly how much (levels, events, cards, characters), with two
   or three of each kind described in full. If content is generated, its contract: the inputs, the
   invariants it keeps, and what guarantees each result works (completable, fair, solvable: whatever
   the game needs).
9. **Story and tone** — if any; how it is delivered; the writing rules for each voice. Plot lives
   here, never in the pillars.
10. **Art and audio direction** — style, camera and resolution, 2–5 reference games or images with
    what each contributes, palette mood, audio mood and what music and sound do as play changes.
    This feeds `art-direction` later. **Camera and
    medium are their own question,** asked early, since everything downstream inherits them: offer
    the options the user's references suggest (count their cameras and media; if most share one,
    start there), and when scope argues against an option, state its actual cost (the assets, tools
    and time a first-person 3D version adds, say), not a rule of thumb.
11. **Interface** — how information reaches the player: density (minimal unless the genre or a pillar
    asks for more); where words live (in the world or on a HUD); how much reading the game asks,
    which pillar wants it and in whose voice; what the player is never told, including how summaries
    treat their choices; the loudest moment and the space kept for it; the feedback for each key
    moment (what the player sees and hears, how big and how long); accessibility options, and a
    second cue for anything colour carries alone; the smallest readable size; how the comparables
    present information. This decides what reaches the player and why; how it
    looks is `art-direction`'s job. The `game-ui` skill holds the defaults these choices confirm or
    override.
12. **Platform and business** — engine, platforms, input devices, session length, price model and
    store (itch.io, Steam…).
13. **Scope boundary** — the first playable: the least content that lets someone judge the core loop,
    with one go/no-go sentence, and a temporary rule written out wherever it stands in for an open
    one. Then what is explicitly out, and ideas parked for later.
14. **Risks and open questions** — what could make this not fun, how long the content plan takes,
    and what is still undecided.

### Pillars

Suggest them; don't impose them. In interactive mode, draft **six to eight candidates** from the
concept, the comparables and the games the user loves, and let the user pick three, edit them, or
write their own. In hands-off mode, each of `gdd-handsoff`'s concepts carries three pillars, so
picking a concept picks its pillars.

- **A name, one line and a test question.** The line says the feeling and where the player gets it;
  the question is what any feature, screen or sound is tested against.
- **Plain, not pretty.** Pillars guide decisions; a line that adds meaning to sound better is cut.
- **For the whole game.** A pillar never prescribes the interface, art or audio ("the interface does
  X" never appears in one); each discipline derives its own rules from the pillars.
- **Not plot.** Story beats go in the story branch.
- **Specific to this game.** A candidate that would fit any game ("fun", "immersive") is dropped.
- **Refining keeps the meaning.** When the user's own words become a pillar, flag any premise you
  added, and keep their words beside it when the line loses a nuance they carry.

For example: **Scarcity forces choices.** There's never enough fuel for everyone, so every trip
leaves someone behind. *Test: could the player do everything here without giving something up?*

When two pillars pull apart later, the owner decides at that moment, in the feature's ledger; no rule
is written in advance. Changing a pillar after the GDD exists goes through `design-change`.

### Each mechanic earns its place

A mechanic belongs in the game only if it enables a move or a decision the player wouldn't have
without it. Discussion rarely catches one that doesn't (a hazard that can only ever be an obstacle, a
resource nobody needs), so check it with the cheapest evidence the genre allows:

- **a solver**, where the rules can be searched exhaustively (puzzles, turn-based logic): every
  mechanic is needed for at least one solution, and no level has an unintended bypass;
- **a simulation with a bot**, where the game can be played automatically (strategy, roguelites,
  economies): removing the mechanic changes the outcomes or the choices;
- **blind playtesters** otherwise (real-time and action games): they use it, and miss it when it's
  gone.

A mechanic that fails is reworked, given a partner that makes it matter, or cut. **Never change the
game to make it easier to check**: a grid is easy to search, but that's no reason to choose one; when
the game can't be searched, use the bot or the playtesters.

The GDD keeps each mechanic's check as a test still to run, one line beside the mechanic. Results of
checks already run go in the prototype report, not the GDD.

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

- **The current design, with its reasons.** Rules and values as they stand, with one sentence of why
  for any rule a builder might "simplify" away. How the design got here (the rounds, prototype
  history, tester quotes, research findings) stays in its own reports: comparables appear as the one
  thing borrowed, and the market as one paragraph of positioning.
- **No silent gaps.** Every value or rule a mechanic needs is stated, marked *(tune)* when
  provisional, or marked `[OPEN]`. A mechanic's values sit in a table beside its rules.
- **One meaning, everywhere.** Win, loss, any grade or rating, and every named state a rule depends
  on are defined once and read the same in every section. A summary, table, diagram or interface row
  restates the rules: it never adds one, drops an exception, or settles an `[OPEN]` value.
- Every section carries a marker: `[DESIGNED]` (specified, not built) or `[OPEN]` (needs a decision).
  `[BUILT]` appears later, as features ship.
- The **amendments** line under the title starts empty. Later reversals are dated there, one line
  each with its ADR, so the document keeps a visible design changelog.
- The **glossary** holds every game term, one line each: what the word means, never its rules again.
  Each term has exactly one meaning, and no content name (an item, ability, level or enemy) reuses
  one; agents use these words literally.
- The **worked example** plays one short stretch of the core loop concretely: what the player sees
  and knows, a choice, how the game resolves it (every value, when the rules use numbers), and the
  consequence. It names any `[OPEN]` rule it leaves out. Writing it is a check: a gap it runs into
  becomes a value or an `[OPEN]` item.
- No file paths, class names or code. The GDD says what the game is, not how it is built.
- Write in the language the user writes in, unless they ask otherwise.

## 6. The builder's read

A GDD written section by section hides what only shows when someone builds from the whole: a gap
that reads as settled, two sections that disagree. Before handing it over, start **one fresh agent
with only the GDD** (no conversation, no research, ideally from a folder with no project instruction
files) and ask it to write, as a technical lead would before building:

- the data model;
- one pass through the core loop, step by step, recomputing the worked example from the rules;
- the first playable's tasks;
- a log of every decision it had to invent, each marked blocker, design-changing or minor, with its
  section, and every contradiction it found.

Then fix the GDD: rewrite what the agent misread, resolve each contradiction, and take each missing
decision to a round (§1) or mark it `[OPEN]`. A decision on the first playable's path can't stay
`[OPEN]`: the user settles it in interactive mode, and the panel in hands-off mode, recorded as
`panel — assumed`. When the fixes were large, run a second read. Done when a read logs no blocker on
the first playable's path and recomputes the worked example exactly.

## 7. Next steps to offer

- **`prototype`** (optional) — try versions of the core mechanic as quick web prototypes before
  committing. Recommend it when the core loop is novel or nobody is sure it's fun.
- **`setup-godot`** — create the repository, tools and agent rules for a Godot game. (Only Godot has
  a setup skill so far; for another engine, say so.)

**Carry the mode forward.** After `gdd-handsoff`, recommend `setup-godot`'s "use every
recommendation" fast path and say the project will be set to work hands-off, so every later skill
offers its hands-off variant first. After `gdd`, recommend the normal round.

**Start the next phase fresh.** It needs only the documents this one wrote (the GDD, its summary).
Where the client can start a new session, hand the next phase over with a short brief pointing at
them, or ask the user for a compaction when they're present, rather than carrying this phase's
conversation into every later call.

## Later ideas don't come back here

Once the GDD exists, new ideas enter through `feature-planning`, or `design-change` when they reverse
a decision. Don't re-run this over a living GDD.
