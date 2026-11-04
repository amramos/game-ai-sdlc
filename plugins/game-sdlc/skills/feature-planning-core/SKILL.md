---
name: feature-planning-core
description: The shared method behind feature-planning and feature-planning-handsoff — rounds of questions over a design tree, a player walkthrough, sketches for layout decisions, a decisions ledger the owner approves, the plan agents build from, and a two-way check that the plan holds every decision and invents none. Loaded by those two skills; not called directly by the user.
user-invocable: false
---

# Feature planning: the shared method

This closes the gap between "the plan contains the decision" and "the owner understood and approved
the result". A plan can be technically sound and still describe a different game from the one the
owner has in mind; a fully built, fully tested feature rejected on first play is the failure this
exists to prevent.

The method is the same in both modes. Only **who answers the rounds** differs:

- **interactive** (`feature-planning`): the owner answers;
- **hands-off** (`feature-planning-handsoff`): you answer with one outside reviewer per round, and
  the owner reads the result later.

Two documents come out of it, for two readers:

- the **decisions ledger** — short, for the owner: every decision, who made it, and the walkthrough,
  sketches and approval record. **This is what the owner approves.**
- the **plan** — long, for agents: requirements, architecture, work packages, traceability.

**The owner's taste profile.** Before the first round, read it by `taste-profile` §1
(`game-sdlc:taste-profile` when installed as a plugin):

- **Never open `taste.md` yourself; run §1's command**, which prints only the Never lines. You write
  the rounds, so the Never lines are all you keep.
- If it prints `MISSING`, offer the profile (its §5).
- Interactive: before a round that holds a question the owner's by nature (the pillars, tone, art
  style, the hook, interface identity) goes out, a judge with the whole profile checks its
  recommendations. Other rounds go out without it.
- Hands-off: the round reviewer judges with it, every round.
- The ledger and the plan never quote it (its §3).
- Rulings that look like taste rather than this game are handled in §10, step 2.

## 1. Planning state

The plan is always in one of three states, written at its top:

- **DISCOVERY** — consequential questions remain;
- **READY FOR APPROVAL** — complete, but not authorized;
- **APPROVED** (interactive) or **PROVISIONALLY APPROVED** (hands-off).

"Looks good" or agreement with a principle is not approval. A new consequential question found during
the build sends the affected part back to DISCOVERY; never invent the answer.

## 2. Intent before mechanism

Before any question about how, write a short intent record into the ledger:

- the problem observed, and the player promise after the change;
- what must stay familiar, and what is deliberately replaced or removed;
- non-goals and parked work;
- the cost: decisions, specs, tests, content and code this invalidates.

**Reversals.** If the request reverses an accepted decision or a parked item, use the
`design-change` skill's stance: past documents are evidence about the past, not constraints on the
owner.

- When the owner's request itself asks for the reversal, the reversal is the owner's ruling: record
  it as `owner`.
- Whatever the request leaves open about it is a question for the rounds, and the owner's by nature.

**Pillars first.** Read the GDD's pillars. If it has none, the first round settles them, under
`gdd-core`'s pillar rules:

- three, each a name, one line and a test question;
- plain; for the whole game; no interface rules and no plot;
- the owner's own words kept beside any tidied wording.

The owner decides; in hands-off mode, the panel decides and marks them assumed. No other skill
rewrites them.

## 3. Rounds over the frontier

Model the feature as a **design tree**: each decision unlocks the ones that depend on it.

- A round asks the **frontier**: every question whose prerequisites are settled. A question that
  depends on one still open waits for the next round.
- Number every question, and give a **recommended answer phrased so "yes" accepts it**.
- Ask only what changes the result: what the player sees, does, predicts or learns; success,
  failure, timing, cancellation; what is preserved; architecture, migration, authored data, scope;
  an acceptance test. Ask outcomes and trade-offs, never implementation details the answerer can't
  judge.
- **Facts are found, never asked.** Send an agent to read the code or docs for anything checkable,
  and keep asking the rest of the frontier while it runs.
- When a broad principle comes up ("it should feel fair"), test it on two or three concrete
  scenarios before turning it into a requirement.
- **Test every recommendation against the pillars.** Under each recommendation, write `Pillar
  test:` and the pillar's test question it passes, so the check can be read later.
- When two pillars pull apart, that is its own question in the round, and the owner's by nature.
- Stop when the frontier is empty: every branch visited, nothing silently assumed.

For example:

```
**Q3. Where does the next wave's preview appear?** In a side panel, or at the path's entrance?
→ Recommended: at the path's entrance, three seconds before the wave, so planning happens on the map.
  Pillar test: "Can the player plan before the pressure arrives?" — yes.
```

Every answer becomes a ledger row the moment it is given (§7).

## 4. The experience, before the implementation

For player-facing work, write a **walkthrough** of the smallest complete loop, screen by screen or
turn by turn. It covers:

1. entry and the first chance to act;
2. discovering information;
3. choosing and committing;
4. anticipation and timing;
5. success;
6. **at least one failure**;
7. the visible consequence;
8. cancellation or an unavailable action;
9. the return to the ordinary loop.

For a system with no screen, write the equivalent operational scenario with a failure and its
recovery.

For a high-impact or novel feature, ask the owner (interactive) to describe one sequence in their own
words and compare it with the walkthrough. A mismatch returns the plan to DISCOVERY.

The walkthrough also says **where each pillar is felt**. Every mechanic gets a line on **how the
player sees it**, with a sketch: a mechanic the interface can't show clearly is simplified, not
patched with UI.

**Screen specs.** A screen needs a spec when it is new, or when its elements, layout, look (colour,
type, size) or motion change. New lines in an existing text element, with nothing else changed,
don't count. Write each from the `game-ui` skill's
template:

- the player's activity and its moments, from the walkthrough;
- each element with its pillar or the decision it supports, and the moments it's shown in;
- the actions and their controls;
- what's deliberately absent and why;
- the word budget;
- the earlier rulings it overturns;
- the words the player doesn't know yet;
- its motion.

The plan links each spec. When no screen needs one, say so in one line in the ledger, with the
reason.

### Show it, don't describe it — layout decisions only

A **layout fork** is any question whose options differ in what appears on screen, where, or how it
looks (colour, type, size, motion). Prose
can't be judged for these, so every layout fork gets one sketch, with "no change" among the options.
Before asking:

- state the pain with a number where there is one (presses, seconds, words, items);
- capture the real game and draw the options over the capture, in the game's palette and fonts, as
  an HTML page or a generated image — never a described layout;
  - include the cheapest fix as one of them;
  - for a first feature, with no game to capture yet, draw over the art direction's style frames or
    the prototype's screens;
  - say on the sketch where it simplifies the approved art, so the simplification isn't read as a
    proposal;
- judge each option at the full content (the longest text, the most items) and for the real input
  devices;
- if an option overturns an earlier design, find out why that design was chosen first;
- show **two or three options side by side**, each with a short *for / against*;
- pair them with **screenshots from shipped games**, each captioned with the one thing borrowed
  (with no way to fetch screenshots, name the game and the exact screen instead);
- then ask which.

One sketch per layout fork, not per answer. When the feature has no layout fork, say so in one line
in the ledger.

**The housekeeping baseline holds.** When the feature adds something a baseline item protects, that
item's *done when* ([housekeeping-baseline.md](../gdd-core/housekeeping-baseline.md)) is a
requirement, not a question. Examples:

- the first progress that carries over is saved by the game's rules;
- a new action is rebindable;
- a new setting persists;
- a new line of dialogue or a cutscene can be skipped.

Which items apply:

- **The GDD has a Housekeeping baseline line**: only the items it includes.
- **The GDD has no such line**: every baseline item the feature touches.

How they look stays the round's to decide.

## 5. How it could pass and still fail

List the most plausible ways the build could meet every written requirement and still be wrong:

- familiar mechanics redone in a different interaction language;
- feedback that exists but isn't perceptible in play;
- tutorials covering for unclear affordances;
- timing that starts before the player can act;
- prose explaining what the interface should show;
- a screen that tells the player what the pillars want withheld;
- a pillar never felt anywhere in the walkthrough;
- a new mode where an extension of the existing loop was meant.

Turn each real one into a requirement, an acceptance check or an early checkpoint.

## 6. A playable slice first

For risky interaction or gameplay changes, the first work package is the **smallest playable slice**
that proves the core experience — real input, timing, resolution and feedback. An owner-played
checkpoint follows it, and the plan says which work pauses until then. Tests don't replace this gate.

A feature that adds a mechanic also shows it **earns its place** (`gdd-core` §2): it enables a move
or a decision the player wouldn't have without it. Name the check: a solver, a simulation with a bot,
or blind playtesters, whichever is cheapest for the genre.

- Give the two-way reviewer (§9) that evidence, not just the documents.
- Before a build, there is no evidence yet: give the reviewer the planned check and its pass
  threshold (for example, "the bot's win rate drops by at least 10 points without the mechanic").

## 7. The decisions ledger

Keep [ledger-template.md](ledger-template.md) current during the rounds, not reconstructed at the
end. Each row: id (D1, D2…), the question, the answer, **who decided**, the dissent (hands-off), and
the date. Who decided is one of:

- `owner` — the owner chose;
- `owner (rec)` — the owner accepted the recommendation;
- `panel` — hands-off: the lead and the round reviewer decided something within the plan's latitude;
- `panel — assumed` — hands-off: they answered a question that is **the owner's by nature** (taste,
  scope, reversing a past decision, the pillars, anything the project's `AGENTS.md` reserves to the
  owner);
- `panel — assumed (profile)` — hands-off: an entry in the owner's taste profile settled it, whatever
  kind of question it was. The row holds the concrete game change and the entry's label at most; the
  entry itself goes only in the report to the owner.

The ledger also holds the intent record, the walkthrough, the sketches (or links to them) and, at
the end, the approval record.

## 8. The plan

Write [plan-template.md](plan-template.md) once the frontier is empty:

- goals and non-goals;
- requirements as observable behavior;
- architecture placement and a concrete existing pattern to follow;
- a **preserve / adapt / replace / remove** inventory;
- data and content migration;
- ordered work packages with dependencies;
- validation;
- checkpoints;
- parked questions.

The traceability table cites **decision ids** from the ledger, so every requirement can be traced
to the decision behind it.

Acceptance criteria describe evidence a player, owner, test, log or artifact can show — never "the
component exists" or "the signal fires". Interface criteria come from the `game-ui` checks.

**Visual acceptance is never an open-ended pass bar.** A plan doesn't invent one ("every item at least
4 out of 5"); judging how screens look follows this pattern:

- one scoring round by a critic that didn't build it (a model from another vendor when available),
  then at most one confirmation pass on the items that were fixed;
- motion and sound are judged from harness timings or short frame sequences, or left to the owner's
  play, never from stills;
- layout-bound items, taste calls and disagreements between reviewers go on the owner's list in the
  first round, instead of into another loop.

## 9. The two-way check (big plans)

A plan is **big** when it adds a new system, reverses a past decision, has more than three work
packages, or the owner says so. Before approval:

1. **The mechanical half.** Run `python <feature-planning-core>/scripts/check_ledger.py <ledger.md>
   <plan.md>` (`py -3` on Windows when `python` isn't found). It exits non-zero and lists the
   decision ids that appear on only one side. Fix those first.
2. **The meaning, in both directions**, checked by a fresh reviewer (never the round reviewer):
   - a model from another vendor when one is available (for example Codex through its Claude Code
     plugin);
   - otherwise a Claude model a tier below the session's, or the same model when there's none below.

   It checks:
   - **every decision in the ledger appears in the plan**, with the same meaning;
   - **the plan contains no decision missing from the ledger.**

   Also ask it to challenge the plan itself (what would fail first, what is missing), and answer
   each point in the ledger.
3. **Invented decisions.** A choice the plan makes that nobody decided goes one of two ways, and the
   ledger's Review section says which for each:
   - **back to the rounds** as a question, when it changes what the player sees or does, or anything
     §3 says to ask about;
   - **removed from the plan** and left to the builder, when it is an implementation detail inside
     the plan's latitude.
4. **One confirmation pass, then stop.** After the fixes, rerun `check_ledger.py` until it exits 0,
   and give the same reviewer one pass on the changed rows only.
   - Points it still raises go in the Review section with your answer.
   - Don't run a third pass.

## 10. Approval record and the hand-off

End the ledger with a compact approval record:

- the experience authorized;
- what is preserved and what is removed;
- the cost;
- the slice checkpoint;
- the open questions, which must be **empty**. In hands-off mode, assumed decisions are answered, not
  open: they are listed under "Assumed by the panel".

Save both documents in the repository, e.g. `docs/plans/<feature>-ledger.md` and
`docs/plans/<feature>-plan.md`. Then hand off, in this order:

1. **Record the rulings where they live**: the GDD for mechanics, an ADR for a new rule or reversal.
   - Interactive, or hands-off going on to a build: edit them now, before the build. In hands-off
     mode, mark the GDD edits and ADRs from assumed decisions as assumed, so the owner's read finds
     them.
   - Hands-off stopping at the plan: don't edit the GDD or write ADRs; they wait for the owner's
     read. The plan carries them as a work package ("Record D3 and D7 in the GDD; ADR for the
     reversal in D5").
2. **Taste rulings.** Look through the rulings for any that would hold for the owner's other games
   too (`taste-profile` §6).
   - Interactive: ask about them now.
   - Hands-off: handle them by `taste-profile` §6, "Owner away" (`proposals.md`, or the report for
     a snapshot run), or say in the report that there are none.
3. **Stop here when the owner chose to stop at the plan** (hands-off option 1): no epic, no build,
   nothing pushed.
4. Turn the plan into an **epic** with the `issue-tracking` skill:
   - one feature per work package;
   - the approval record as the epic's description;
   - the ledger as its first comment.
5. **Build it** with `team-lead` (or `team-lead-handsoff`). Offer it **in the working style**:
   - the `Working style` line in the project's `AGENTS.md`, or, before a project exists, the mode of
     the skill that just ran (`gdd-handsoff` means hands-off);
   - hands-off: offer the `-handsoff` variant first;
   - interactive: offer the interactive skill, and mention the hands-off variant once.

   Start the build fresh: it needs only the plan, the ledger and the GDD, not this planning
   conversation. Where the client can start a new session, hand it over with a short brief, or ask
   the owner for a compaction when they're present.
