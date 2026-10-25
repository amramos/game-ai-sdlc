---
name: gdd-handsoff
description: Design a game with almost no input — the user gives a one-line idea (or "surprise me"), a few games they love and one they find boring, and a scope; picks one of three concepts; and an agent panel writes the GDD, checked by quality gates and by blind AI playtesters on a quick prototype, ending with a one-page summary of what the panel assumed. Use when the user wants a GDD without answering a design interview.
argument-hint: "A one-line game idea, or \"surprise me\""
disable-model-invocation: true
---

# GDD (hands-off)

Load the **`gdd-core`** skill (`game-sdlc:gdd-core` when installed as a plugin) and follow it in
**hands-off mode**: a panel of agents answers the rounds instead of the user.

The risk of a design nobody steered is the *average* game: competent and forgettable. Agents write
well; what they lack is taste. So this skill collects the few inputs that carry taste as cheaply as
possible, lets the user **react rather than answer**, and replaces opinion with **evidence from
play** wherever it can.

Tell the user up front what it costs: several agents, web research and a prototype loop — roughly
30–60 minutes of agent time.

## 1. Intake: one message

Ask for all of it at once, in one message or one multiple-choice call, with defaults:

1. **The idea** in one line — or "surprise me".
2. **Two or three games they love**, and **one they find boring**. The boring one tells as much
   about taste as the favourites.
3. **Scope**: game jam, small release, or commercial. Default: small release.
4. *(Optional)* platform. Default: desktop and web, through itch.io.

## 2. Three concepts; the user picks

Draft **three deliberately different concepts**, each built from the intake. Each has:

- a pitch (two sentences) and the hook;
- three pillars, each a name, one line and a test question, written by gdd-core's pillar rules
  (plain, for the whole game, no interface rules, no plot);
- the core loop in three lines;
- three comparables, each with the one thing borrowed;
- one line on how it reflects the games they love and avoids the one they find boring.

"Different" means a different core verb or structure (e.g. one about routing, one about
deck-building, one about real-time juggling), not three tunings of one idea. Run a quick market search
first so no concept is a known game in disguise.

Ask the user to **pick one**, or to say "you pick". Picking a concept picks its pillars too. If they
pick, record both as `owner`. If they don't, the panel (§3) votes, and the concept and its pillars
are recorded as `panel — assumed`.

## 3. The panel works the tree

Four panelists, each a separate agent with its own brief, answering every round of gdd-core's design
tree independently:

| Panelist | Point of view | Model |
|---|---|---|
| **Designer** | the chosen concept and its pillars; consistency | the session's model |
| **Player advocate** | a first-time player: clarity, fun, frustration | a different model from the designer's |
| **Market analyst** | comparables, prices, what sells in this niche; backed by research agents (gdd-core §3) | any |
| **Skeptic** | what fails, what's too big, what's a copy | a model from another vendor when available (e.g. Codex through its Claude Code plugin); otherwise another model |

Every panelist's model is set explicitly, and none is more expensive than the session's: "a
different model" means a cheaper one here.

Resolve each question: **unanimous** → take it; **split** → you decide, with one line naming the
dissent. Decisions that shape the game's identity — the pillars, tone, art style, the interface
choices (gdd-core's interface branch), the hook, anything left open by the intake — are recorded as
`panel — assumed` even when unanimous. Keep a
running list of every decision with who made it; the summary (§6) draws on it.

## 4. Quality gates

These stand in for the missing owner. Apply each before writing the final GDD, and fix or cut what
fails:

- **The pillars.** Every mechanic serves at least one pillar, or it's cut.
- **Grounded in research.** Each mechanic names a shipped game that does something similar. A
  mechanic with none is flagged as a novelty risk — possibly the good kind — and becomes the first
  thing the prototype tests.
- **A scope budget.** Count systems and content against the intake's scope (a jam game has one core
  system and minutes of content; a small release, two or three systems and a few hours). Hands-off
  design over-reaches; cut to fit and move the rest to *parked*.
- **The hook is real.** The market analyst confirms the concept isn't a reskin of its first
  comparable.
- **The skeptic's kill list.** The three most likely reasons this game fails, each with a mitigation
  in the design or an `[OPEN]` question.

## 5. Proof by play

Run the **`prototype`** skill in its hands-off form on the core loop: two variations of the chosen
core mechanic, played by **blind AI playtesters only** (no user play), compared on their reports.

The bar: the playtesters can state the goal correctly, and their median "want another round" is at
least 6/10. If neither variation clears it, the panel revises the core loop using the reports and
tries again — **at most twice**. If it still fails, say so plainly in the summary and recommend the
user try the prototype themselves before going further; don't paper over it.

Write the winning variation's lessons about the mechanic into the GDD (never its web layout); throw
the prototypes away.

## 6. Output

1. **The GDD** (gdd-core §5), with this under the title: "**Provisional** — written by an agent
   panel from a short intake; the decisions marked *assumed* in the appendix are the owner's to
   confirm." Add an appendix, **Assumed by the panel**, listing every `panel — assumed` decision.
2. **A one-page summary**, `GDD-summary.md` next to the GDD, for a user who won't read the GDD:
   - the pitch;
   - **the three pillars**, each with its test question, first, since every later skill judges work
     against them;
   - **the five other assumed decisions that shape the game most**, each with its runner-up
     alternative;
   - the playtesters' verdict in two lines (including any failed bar);
   - the skeptic's kill list, one line each;
   - one closing question: *change any of these, or continue to setup?*

Show the summary in the conversation as well. Any assumption the user overturns is edited straight
into the GDD — it's still provisional, so no `design-change` is needed yet. Then offer
`setup-godot` with its "use every recommendation" fast path (gdd-core §6); setup records the
hands-off working style, so the first feature will be offered as `feature-planning-handsoff`.
