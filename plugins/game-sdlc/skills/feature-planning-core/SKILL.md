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
- **hands-off** (`feature-planning-handsoff`): a panel of agents answers, and the owner reads the
  result later.

Two documents come out of it, for two readers:

- the **decisions ledger** — short, for the owner: every decision, who made it, and the walkthrough,
  sketches and approval record. **This is what the owner approves.**
- the **plan** — long, for agents: requirements, architecture, work packages, traceability.

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

If the request reverses an accepted decision, use the `design-change` skill's stance: past documents
are evidence about the past, not constraints on the owner.

**Pillars first.** Read the GDD's pillars. If it has none, the first round settles them, under
`gdd-core`'s pillar rules: three, each a name, one line and a test question; plain; for the whole
game, with no interface rules and no plot; the owner's own words kept beside any tidied wording. The
owner decides (in hands-off mode, the panel decides and marks them assumed). No other skill rewrites
them.

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
- **Test every recommendation against the pillars**, using their test questions. When two pillars
  pull apart, that is its own question in the round, and the owner's by nature.
- Stop when the frontier is empty: every branch visited, nothing silently assumed.

Every answer becomes a ledger row the moment it is given (§7).

## 4. The experience, before the implementation

For player-facing work, write a **walkthrough** of the smallest complete loop, screen by screen or
turn by turn: entry and first chance to act; discovering information; choosing and committing;
anticipation and timing; success; **at least one failure**; the visible consequence; cancellation
or an unavailable action; and the return to the ordinary loop. For a system with no screen, write
the equivalent operational scenario with a failure and its recovery.

For a high-impact or novel feature, ask the owner (interactive) to describe one sequence in their own
words and compare it with the walkthrough. A mismatch returns the plan to DISCOVERY.

The walkthrough also says **where each pillar is felt**, and every mechanic gets a line on **how the
player sees it**, with a sketch: a mechanic the interface can't show clearly is simplified, not
patched with UI.

**Every new or changed screen gets a screen spec**, from the `game-ui` skill's template: the player's
activity, each element with its pillar or the decision it supports, what's deliberately absent and
why, the word budget, the earlier rulings it overturns, the words the player doesn't know yet, and
its motion. The plan links each spec.

### Show it, don't describe it — layout decisions only

When a decision is about **how something looks or is laid out**, prose can't be judged. Before asking:

- state the pain with a number where there is one (presses, seconds, words, items);
- capture the real game and draw the options over the capture, in the game's palette and fonts, as
  an HTML page or a generated image — never a described layout; include the cheapest fix as one of
  them;
- judge each option at the full content (the longest text, the most items) and for the real input
  devices;
- if an option overturns an earlier design, find out why that design was chosen first;
- show **two or three options side by side**, each with a short *for / against*;
- pair them with **screenshots from shipped games**, each captioned with the one thing borrowed;
- then ask which.

One sketch per material fork, not per answer.

## 5. How it could pass and still fail

List the most plausible ways the build could meet every written requirement and still be wrong:
familiar mechanics redone in a different interaction language; feedback that exists but isn't
perceptible in play; tutorials covering for unclear affordances; timing that starts before the
player can act; prose explaining what the interface should show; a screen that tells the player what
the pillars want withheld; a pillar never felt anywhere in the walkthrough; a new mode where an
extension of the existing loop was meant. Turn each real one into a requirement, an acceptance check
or an early checkpoint.

## 6. A playable slice first

For risky interaction or gameplay changes, the first work package is the **smallest playable slice**
that proves the core experience — real input, timing, resolution and feedback. An owner-played
checkpoint follows it, and the plan says which work pauses until then. Tests don't replace this gate.

## 7. The decisions ledger

Keep [ledger-template.md](ledger-template.md) current during the rounds, not reconstructed at the
end. Each row: id (D1, D2…), the question, the answer, **who decided**, and the date. Who decided is
one of:

- `owner` — the owner chose;
- `owner (rec)` — the owner accepted the recommendation;
- `panel` — hands-off panel decided something within the plan's latitude;
- `panel — assumed` — hands-off panel answered a question that is **the owner's by nature** (taste,
  scope, reversing a past decision, the pillars, anything the project's `AGENTS.md` reserves to the
  owner).

The ledger also holds the intent record, the walkthrough, the sketches (or links to them) and, at
the end, the approval record.

## 8. The plan

Write [plan-template.md](plan-template.md) once the frontier is empty: goals and non-goals;
requirements as observable behavior; architecture placement and a concrete existing pattern to
follow; a **preserve / adapt / replace / remove** inventory; data and content migration; ordered work
packages with dependencies; validation; checkpoints; parked questions. The traceability table cites
**decision ids** from the ledger, so every requirement can be traced to the decision behind it.

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
packages, or the owner says so. Before approval, a reviewer — a model from another vendor when one
is available (for example Codex through its Claude Code plugin), otherwise a different model from
the one that wrote the plan — checks both directions:

1. **Every decision in the ledger appears in the plan**, with the same meaning.
2. **The plan contains no decision missing from the ledger.** A choice the plan makes that nobody
   decided is an invented decision: it goes back into the rounds as a question.

Also ask the reviewer to challenge the plan itself (what would fail first, what is missing), and
answer each point in the ledger.

## 10. Approval record and the hand-off

End the ledger with a compact approval record: the experience authorized; what is preserved and
what is removed; the cost; the slice checkpoint; and the open questions, which must be **empty**.

Then hand off, in this order:

1. record the rulings where they live (the GDD for mechanics, an ADR for a new rule or reversal);
2. turn the plan into an **epic** with the `issue-tracking` skill: one feature per work package, the
   approval record as the epic's description, the ledger as its first comment;
3. build it with `team-lead` (or `team-lead-handsoff`). Offer it **in the working style**: the `Working style` line in the project's `AGENTS.md`, or, before a project exists, the mode of the skill that just ran (`gdd-handsoff` means hands-off). Hands-off: offer the `-handsoff` variant first. Interactive: offer the interactive skill, and mention the hands-off variant once.

Save both documents in the repository, e.g. `docs/plans/<feature>-ledger.md` and
`docs/plans/<feature>-plan.md`.
