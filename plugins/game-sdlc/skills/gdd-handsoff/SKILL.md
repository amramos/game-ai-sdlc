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

**The cost, in your first reply.** Tell the user what this costs: several agents, web research and
a prototype loop, roughly 30–60 minutes of agent time. Say it in your first reply, together with the
intake questions, or with the concepts when the intake came complete in the first message.

## 1. Intake: one message

Ask for all of it at once, in one message or one multiple-choice call, with defaults:

1. **The idea** in one line — or "surprise me".
2. **Two or three games they love**, and **one they find boring**. The boring one tells as much
   about taste as the favourites.
3. **Scope**: game jam, prototype, small release, or commercial. Default: small release. It also
   decides the housekeeping baseline (gdd-core §2), so nothing more is asked about it.
4. *(Optional)* platform. Default: desktop and web, through itch.io, built in Godot.

**The taste profile, now.** Read it by gdd-core, "The owner's taste profile": **never open
`taste.md`; run `taste-profile` §1's command**, which prints only the Never lines.

- If it prints `MISSING`, offer the profile in this same message: the user is here now and may not
  be later.
- With a profile, still ask for the loved games: they say what *this* game is reaching for, which
  the profile doesn't.

## 2. Three concepts; the user picks

**First, a quick market search**, so no concept is a known game in disguise.

**Count the loved games' camera and medium**, not only their mechanics: they carry the user's taste.
Count the two separately:

- camera: top-down, side view, isometric, third-person, first-person;
- medium: pixel art, vector, painted 2D, low-poly 3D, realistic 3D, text.

When most of the loved games share one camera (three first-person games out of four, say), at least
one concept uses it. The same goes for the medium. Another concept may depart, saying why and what
that saves or costs. Never take the camera from the nearest mechanical comparable alone.

Then draft **three deliberately different concepts**, each built from the intake. "Different" means
a different core verb or structure (e.g. one about routing, one about deck-building, one about
real-time juggling), not three tunings of one idea. Each has:

- a pitch (two sentences) and the hook;
- three pillars, each a name, one line and a test question, written by gdd-core's pillar rules
  (plain, for the whole game, no interface rules, no plot);
- the core loop in three lines;
- a camera and medium (for example first-person low-poly 3D, top-down pixel art, side-view painted);
- three comparables, each with the one thing borrowed;
- one line on how it reflects the games they love and avoids the one they find boring.

**Who drafts.** The concepts come from the intake, the market search and the profile's Never lines
only (`taste-profile` §3).

- When the Never lines are all this session has read of the profile, draft them yourself.
- When it has read more (it just ran the taste-profile interview, say), spawn a separate drafter
  with only those inputs.

**The judge, before the user sees them.** With a taste profile, a judge with the whole profile reads
the finished concepts. It adds one line to each concept that has room for a Signature item, written
as the change in game terms, with `(profile)` and the label. It doesn't rewrite them. Run it before
showing the concepts; the round reviewer that may help you pick later doesn't replace it.

**The pick.** Ask the user to **pick one**, or to say "you pick". Picking a concept picks its pillars
too.

- If they pick, record the concept as `owner`: its pitch, hook, pillars, camera and medium.
- If they don't, you pick with the round reviewer (§3). Record the concept and its pillars as
  `panel — assumed`, with the runner-up concept.

## 3. You and the round reviewer work the tree

**You are the designer.** Work gdd-core's design tree in rounds, with a recommendation per question
grounded in the chosen concept and its pillars, and consistent with the rest of the game.

**Start research before round 1.** Dispatch the after-pitch and after-pillars searches (gdd-core §3)
in the background before round 1 goes to the reviewer, and keep working while they run.

Two kinds of question go to what measures them better than an opinion:

- **The market.** When a question turns on comparables, prices or what sells in this niche,
  dispatch a research agent on it (gdd-core §3) and recommend from its findings: decisions, never
  facts.
- **The first-time player.** Clarity, fun and frustration are measured by the blind playtesters of
  §5, not guessed; what a round can't settle without them goes to the prototype as a question.

Then **one round reviewer**, a fresh agent per round, answers it.

- Its brief: the round, the GDD so far, and two roles. As a skeptic: what fails, what's too big,
  what's a copy. As the profile judge (`taste-profile` §3): it reads the whole taste profile itself.
- It agrees with each recommendation or gives a different answer with one line of reason.
- **Run it** with `team-lead/scripts/codex_review.py --probe`, then `--round gdd --repo <folder>
  --prompt-file <round> --out <file>`. The script adds the reply format, kill list included (§4).
- **Exit 0:** read `<file>`, which holds only the answers. Never open `<file stem>.owner.md`; the
  report to the user links it.
- **Exit 4:** no usable reply, even after a retry. Decide the round yourself, record its answers as
  `panel — assumed`, and say so in the summary.
- **Exit 2 or 3:** no other vendor's model. Use a Claude model a tier below the session's (the same
  model when there's none below, or the one below is smaller than mid-size, and say so). End its
  brief with `--print-format gdd`'s output and "Write your reply to `<reply file>` and return only
  the word `written`", then run `codex_review.py --split <reply file> --need-verdict --out <file>`.
  On exit 4, ask it once more with the format before deciding the round yourself.

**Resolve each question:**

- **it agrees** → take it;
- **it disagrees** → you decide, with one line naming the dissent;
- **it proposes a `(profile)` addition** → take it when the game has room for it, as
  `panel — assumed (profile)`, written as the concrete game change;
- **its answer carries profile text** → take only the decision and the label, and note the slip in
  the report (`taste-profile` §3).

**Identity decisions** are recorded as `panel — assumed` even when the reviewer agrees. They are:

- the pillars, the hook, and the camera and medium, unless the user picked the concept that carries
  them;
- tone;
- the art style beyond the camera and medium;
- the interface choices (gdd-core's interface branch);
- anything the intake left open.

Each identity decision has a **runner-up**: the answer you didn't take. When the reviewer disagreed,
that is its answer if you kept yours, or your original recommendation if you adopted its answer.
When it agreed, it is the strongest option you rejected.

Every other decision is recorded as `panel`, with two exceptions that are always assumed:

- a decision a profile entry settled is always `panel — assumed (profile)`, identity or not;
- a decision the panel settles after the builder's read (§6) is `panel — assumed`.

Keep a running list of every decision with who made it; the summary (§6) draws on it. ("The panel" in
markers and summaries means you and the reviewer together.)

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
toward it; what it misread goes in the summary.

- If neither variation clears it, the panel revises the core loop using the reports and tries
  again — **at most twice**.
- A retry re-tests only the revised variation; the other keeps its reports from the pass before.
- If it still fails, say so plainly in the summary and recommend the user try the prototype
  themselves before going further; don't paper over it.

Write the winning variation back into the GDD as `prototype` §4 describes (never its web layout);
throw the prototypes away.

## 6. Output

**First, the builder's read** (gdd-core §6) on the written GDD. The panel settles what it finds on
the first playable's path. Record every such settlement as `panel — assumed` (§3's exceptions), with
a runner-up, so it reaches the appendix.

1. **The GDD** (gdd-core §5).
   - Under the title, the template's Provisional line: "**Provisional** — written by agents from a
     short intake; the decisions marked *assumed* in the appendix are the owner's to confirm."
   - The template's appendix, **Appendix: Assumed by the panel**, lists only the `panel — assumed`
     and `panel — assumed (profile)` decisions, numbered **A1**, **A2**…, each with its runner-up.
2. **A one-page summary**, `GDD-summary.md` next to the GDD, for a user who won't read the GDD.
   In this order:
   1. the pitch;
   2. **the three pillars**, each with its test question, since every later skill judges work
      against them;
   3. **the camera and medium**. When they depart from what most of the loved games share, say why,
      and what the alternative would cost, so a one-word swap is still possible;
   4. **the five other assumed decisions that shape the game most**, each citing its appendix id
      `(A<n>)`, with its runner-up. Fewer only when the appendix has no more;
   5. **the housekeeping baseline** the scope gave (gdd-core §2), with its one-word swap: "backlog"
      or "build" after a jam or prototype, "strike <item>" after a release;
   6. the playtesters' verdict in two lines (including any failed bar);
   7. the reviewer's kill list, one line each;
   8. the closing question, word for word: *"Change any of these, or continue to `setup-godot` with
      every recommendation (the project will run hands-off)?"*

**Then check both:** `python <gdd-core>/scripts/check_gdd.py <GDD> --summary GDD-summary.md`, adding
`--owner-picked` when the user picked the concept. Fix what it lists until it exits 0.

**In the conversation only, never in a file:**

- which taste-profile entry settled each `panel — assumed (profile)` decision;
- the rulings proposed for the profile (`taste-profile` §6);
- with no profile, one line offering to set one up, under that skill's §5 check.

Show the summary in the conversation as well. Any assumption the user overturns is edited straight
into the GDD — it's still provisional, so no `design-change` is needed yet.

**Then offer `setup-godot`** with its "use every recommendation" fast path (gdd-core §7). Setup
records the hands-off working style, so the first feature will be offered as
`feature-planning-handsoff`.
