---
name: gdd-handsoff
description: Design a game with almost no input — the user gives a one-line idea (or "surprise me"), a few games they love and one they find boring, and a scope; picks one of three concepts; and the session writes the GDD with one outside reviewer per round, checked by quality gates and by blind AI playtesters on a quick prototype, ending with a one-page summary of what the panel assumed. Use when the user wants a GDD without answering a design interview — when they invoke it, or ask for one in their own words. Never pick it on your own initiative.
argument-hint: "A one-line game idea, or \"surprise me\""
---

# GDD (hands-off)

Load the **`gdd-core`** skill (`game-sdlc:gdd-core` when installed as a plugin) and follow it in
**hands-off mode**: you and one round reviewer answer the rounds instead of the user.

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
3. **Scope**: game jam, prototype, small release, or commercial. Default: small release. It also
   decides the housekeeping baseline (gdd-core §2), so nothing more is asked about it.
4. *(Optional)* platform. Default: desktop and web, through itch.io.

This is also the moment to offer the taste profile if there isn't one (gdd-core, "The owner's taste
profile"): the user is here now and may not be later. With a profile, still ask for the loved games:
they say what *this* game is reaching for, which the profile doesn't.

## 2. Three concepts; the user picks

Draft **three deliberately different concepts**, each built from the intake. Each has:

- a pitch (two sentences) and the hook;
- three pillars, each a name, one line and a test question, written by gdd-core's pillar rules
  (plain, for the whole game, no interface rules, no plot);
- the core loop in three lines;
- a camera and medium (for example first-person low-poly 3D, top-down pixel art, side-view painted);
- three comparables, each with the one thing borrowed;
- one line on how it reflects the games they love and avoids the one they find boring.

With a taste profile, the three concepts are drafted from the intake, the market search and the
profile's Never lines only (`taste-profile` §3). When that is all this session has read of the
profile, draft them yourself. When it has read more (it just ran the taste-profile interview, say),
spawn a separate drafter with only those inputs. Then a judge with the whole profile reads the
finished concepts and adds one line to each concept that has room for a Signature item. The judge
doesn't rewrite them.

"Different" means a different core verb or structure (e.g. one about routing, one about
deck-building, one about real-time juggling), not three tunings of one idea. Run a quick market search
first so no concept is a known game in disguise.

**Read the loved games' camera and medium too, not only their mechanics.** They carry the user's
taste. When most of them share one (three first-person 3D games out of four, say), at least one
concept uses it; another may depart, saying why and what that saves or costs. Never take the camera
from the nearest mechanical comparable alone.

Ask the user to **pick one**, or to say "you pick". Picking a concept picks its pillars too. If they
pick, record both as `owner`. If they don't, you pick with the round reviewer (§3), and the concept
and its pillars are recorded as `panel — assumed`, with the runner-up concept.

## 3. You and the round reviewer work the tree

**You are the designer.** Work gdd-core's design tree in rounds, with a recommendation per question
grounded in the chosen concept and its pillars, and consistent with the rest of the game. Two
questions go to what measures them better than an opinion:

- **The market.** When a question turns on comparables, prices or what sells in this niche,
  dispatch a research agent on it (gdd-core §3) and recommend from its findings: decisions, never
  facts.
- **The first-time player.** Clarity, fun and frustration are measured by the blind playtesters of
  §5, not guessed; what a round can't settle without them goes to the prototype as a question.

Then **one round reviewer**, a fresh agent per round, answers it, briefed as
`feature-planning-handsoff` §2 describes: a skeptic (what fails, what's too big, what's a copy) and
the profile judge, reading the whole taste profile itself. It agrees with each recommendation or
gives a different answer with one line of reason. **Its model:** another vendor's model when one
is available, run with `team-lead/scripts/codex_review.py`; otherwise a Claude model chosen as
`feature-planning-handsoff` §2 says. A Claude subagent is never above the session's model; another
vendor's model may be stronger.

Resolve each question: **it agrees** → take it; **it disagrees** → you decide, with one line naming
the dissent; **it proposes a `(profile)` addition** → take it when the game has room for it, as
`panel — assumed (profile)`. Decisions that shape the game's identity — the pillars, tone, art style, the interface
choices (gdd-core's interface branch), the hook, anything left open by the intake — are recorded as
`panel — assumed` even when it agrees, each **with a runner-up**: the reviewer's answer when it
disagreed, otherwise the strongest option you rejected. Keep a running list of every decision with
who made it; the summary (§6) draws on it. ("The panel" in markers and summaries means you and
the reviewer together.)

## 4. Quality gates

These stand in for the missing owner. Apply each before writing the final GDD, and fix or cut what
fails:

- **The pillars.** Every mechanic serves at least one pillar, or it's cut.
- **Each mechanic earns its place** (gdd-core §2): it enables a move or a decision the player
  wouldn't have without it, checked with the cheapest evidence the genre allows — a solver, a
  simulation with a bot, or the blind playtesters of §5. Give the plan's later reviewers that evidence,
  not just the documents.
- **Grounded in research.** Each mechanic names a shipped game that does something similar. A
  mechanic with none is flagged as a novelty risk — possibly the good kind — and becomes the first
  thing the prototype tests.
- **A scope budget.** Count systems and content against the intake's scope (a jam game has one core
  system and minutes of content; a small release, two or three systems and a few hours). Hands-off
  design over-reaches; cut to fit and move the rest to *parked*.
- **The hook is real.** A research agent compares the concept with its first comparable and
  confirms it isn't a reskin.
- **The reviewer's kill list.** The three most likely reasons this game fails, each with a
  mitigation in the design or an `[OPEN]` question.

## 5. Proof by play

Run the **`prototype`** skill in its hands-off form on the core loop: two variations of the chosen
core mechanic, played by **blind AI playtesters only** (no user play), compared on their reports.

The bar: the playtesters who had the tutorial can state the goal correctly, and their median "want
another round" is at least 6/10. The cold playtester (and its ten-second read) doesn't count
toward it; what it misread goes in the summary. If neither variation clears it, the panel revises
the core loop using the reports and tries again — **at most twice**. A retry re-tests only the
revised variation; the other keeps its reports from the pass before. If it still fails, say so
plainly in the summary and recommend the user try the prototype themselves before going further;
don't paper over it.

Write the winning variation back into the GDD as `prototype` §4 describes (never its web layout);
throw the prototypes away.

## 6. Output

First run the builder's read (gdd-core §6) on the written GDD. The panel settles what it finds on the
first playable's path, recorded as `panel — assumed`.

1. **The GDD** (gdd-core §5), with this under the title: "**Provisional** — written by agents
   from a short intake; the decisions marked *assumed* in the appendix are the owner's to
   confirm." Add an appendix, **Assumed by the panel**, listing every `panel — assumed` decision.
2. **A one-page summary**, `GDD-summary.md` next to the GDD, for a user who won't read the GDD:
   - the pitch;
   - **the three pillars**, each with its test question, first, since every later skill judges work
     against them;
   - **the camera and medium**, and, when they depart from what most of the loved games share, why,
     and what the alternative would cost, so a one-word swap is still possible;
   - **the five other assumed decisions that shape the game most**, each with its runner-up
     alternative;
   - **the housekeeping baseline** the scope gave (gdd-core §2), with its one-word swap: "backlog"
     or "build" after a jam or prototype, "strike <item>" after a release;
   - the playtesters' verdict in two lines (including any failed bar);
   - the reviewer's kill list, one line each;
   - **in the conversation only, never in the file**: which taste-profile entry settled each
     `panel — assumed (profile)` decision, and the rulings proposed for the profile
     (`taste-profile` §6). With no profile, one line offering to set one up, under that skill's
     §5 check;
   - one closing question: *change any of these, or continue to setup?*

Show the summary in the conversation as well. Any assumption the user overturns is edited straight
into the GDD — it's still provisional, so no `design-change` is needed yet. Then offer
`setup-godot` with its "use every recommendation" fast path (gdd-core §7); setup records the
hands-off working style, so the first feature will be offered as `feature-planning-handsoff`.
