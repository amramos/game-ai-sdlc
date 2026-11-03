# The lifecycle, and why each practice exists

This process was extracted from about two months of building a Godot roguelite almost entirely with
agents (Claude Code and Codex), with one person as designer, owner and playtester. Almost every
practice in it exists because something went wrong without it. This page walks the phases in order:
what each one produces, and the failure that taught it.

---

## 1. Design — `gdd` or `gdd-handsoff`

**Produces:** a GDD with a pitch, comparables, three pillars, the core loop, mechanics with their
values, a worked example, an interface section, a glossary, a first playable, a scope boundary and
open questions.

The original GDD came out of a long conversation with an AI. `gdd` turns that into an interview with
research agents on the side. `gdd-handsoff` is for people who won't sit through an interview. Its
design starts from a weakness: a design nobody steered tends to be the *average* game. So it collects
the few inputs that carry taste (games you love, one you find boring, a pick between three concepts),
and checks the rest with gates and blind playtesters instead of opinions. Everything it assumes is
listed for the owner on one page.

- **Design before code.** The GDD was the second commit, before any game code. Agents build from
  documents; without one, each session invents its own version of the game.
- **Three pillars, not a governing rule.** The first version had one rule that decided every cut.
  Written as an absolute ("every verdict is a contradiction"), agents applied it literally and cut
  variety the game needed. Pillars replaced it: the three feelings the whole game is built to give,
  each with a test question, written plainly and never as interface or plot. When two pull apart,
  the owner decides at that moment.
- **The interface is designed, not defaulted.** A game that played well still looked like a web page,
  because nothing before the build said how information reaches the player. The GDD now has an
  interface section, the style guide covers the interface, and the `game-ui` skill holds ten
  commandments distilled from thirteen talks on game UI (the literature is in `research/game-ui/`).
- **`[OPEN]` instead of a guess.** An agent that meets a gap fills it with something plausible, and
  plausible is how a game drifts from what you meant. Marking undecided things as decisions made
  agents ask instead of invent.
- **A glossary with one meaning per word.** Agents use terms literally in code. Two meanings for one
  word turned into two systems.
- **The current design, not its history; every value stated or marked.** Blind reviewers building
  from an early SDLC GDD found prototype history in the mechanics and the scoring values in a file
  they didn't have. The unmarked gaps read as settled. The GDD now states rules with one sentence of
  why, and calls a missing value a mistake to report.
- **A taste profile, kept apart from the generators.** Games built hands-on and hands-off came out
  very differently: the hands-off ones needed more correction and felt more generic, because the
  owner's opinions only reached a run through a short intake. `taste-profile` writes those opinions
  down once, for every project. Its first test shaped it. Choosing between two things the owner
  liked mostly got "both", and the real answer was in the conditions; dealbreakers said more than any
  other round. In playback the owner kept the inferred *reasons* and cut every inferred *genre or
  aesthetic*. So the profile holds reasons only, asks before every addition, and only the agents that
  judge see all of it: an agent that drafts options puts whatever it's shown into every option.
- **A builder's read before handover.** Sections written one at a time can contradict each other in
  ways no single section shows. One blind agent builds from the GDD alone and logs every decision it
  had to invent; nothing on the first playable's path may stay open.

## 2. Try it cheaply — `prototype` (optional)

**Produces:** a chosen core mechanic, written back into the GDD.

The first real code in the original project was the core resolution rule plus a small harness to try
it. Prototypes make that step deliberate: two or three versions of the core, compared by playing them
rather than by imagining them, before any repository exists to be wasted.

- **Legible to the owner, not just to agents.** Early prototypes printed their text interface onto
  the page; agents could play them, and the owner clicked at random. Each now states what it tests,
  teaches itself in 3–5 guided steps, and draws the state where it lives in the GDD's camera.
- **The values come back, not the story.** The write-back copies the tuned numbers and the rules the
  code decided without saying, rewrites the affected sections whole, and leaves the history in a
  prototype report.

## 3. Foundations — `setup-godot`

**Produces:** a repository an agent can work in safely from the first commit.

- **Day-one ADRs** for folder structure, test framework, text-only scenes and no global event bus.
  Without written decisions, every new session re-opened them.
- **Hooks before code.** No commits to `main`, protected vendor and config files, every script
  checked as it's edited. A rule that depends on remembering it gets forgotten; a hook that runs on
  every edit doesn't.
- **Two clients, one contract.** Claude Code and Codex share `AGENTS.md`, the hooks and the roles,
  so switching tools never means switching rules.

## 4. Look — `art-direction` (optional)

**Produces:** style frames, a palette, size rules and the exact prompt that made them, in `docs/art/`.

Generated art drifts one asset at a time. A fixed reference that every generation starts from, chosen
once by you, is what keeps fifty assets looking like one game.

The first test of the hands-off route produced three directions that were all pixel art: the panel had
assumed the medium from the GDD's main reference, and art direction only varied the palette. Now
directions must differ in medium when the style was assumed, so the first time you see the game's
look, you also see what else it could have been.

## 5. Plan — `feature-planning`

**Produces:** a decisions ledger (yours) and a plan (the agents').

This is the phase with the clearest origin story. A boss system was planned, built and fully tested.
Every test passed, and the owner rejected it the first time they played it. The plan had been
technically sound, but it described a different experience from the one the owner had in mind, and
nothing in the process had checked that the two matched.

So planning now approves the **experience first**: a walkthrough of what the player sees and does,
including a failure path, before any file list. For layout decisions, the options are drawn over real
screenshots next to examples from shipped games, because prose can't be judged by eye. Every plan
lists how it could pass its tests and still be wrong. Risky work starts with a playable slice that the
owner plays before anything else gets built.

Two refinements came later:

- **Rounds with recommendations.** The questions were often worth answering but tiring. Asking every
  question that's ready in one round, each with a recommended answer that "yes" accepts (borrowed from
  [Matt Pocock's grilling skill](https://github.com/mattpocock/skills)), made a round take a minute.
- **The ledger.** The owner read the questions and answers, not the long plan, and trusted the plan
  to match. The ledger makes that trust checkable: the plan cites each decision, and a reviewer checks
  that every decision is in the plan and that the plan invents none.
- **One outside reviewer, not a panel.** Hands-off planning used to put three or four agents on every
  round: a designer, a player advocate, a skeptic and, for the GDD, a market analyst. A before/after
  test on two invented games and two model tiers showed that nearly all the disagreement came from the
  skeptic on another vendor's model. The same-model designer re-derived the lead's answers, and the
  panel's splits were buried where the owner didn't read them. Now the lead answers, one reviewer from
  another vendor checks each round, and every assumed decision carries the reviewer's answer as its
  runner-up. The first version lost a taste-profile opening on the mid-size model, because the
  reviewer put it in a note the lead never read; it now goes among the reviewer's answers. The test
  is in `research/agent-usage/`.

## 6. Track — `issue-tracking`

**Produces:** an epic with one feature per work package.

- **Two levels, no stories.** Story tickets once made up about 70% of the board and were almost never
  read. A story-sized piece of work is a checklist line now.
- **Rulings live in issue comments,** and agents read them before writing code. That's how a decision
  made on a Tuesday survives into Friday's session.
- **Agents stop at `In Review`.** "Done" means the owner looked at it. An agent marking its own work
  done is reviewing itself.

## 7. Build — `team-lead`

**Produces:** a pull request per owner checkpoint, a short report and a story page.

- **The lead decides, developers build.** Architecture is settled in the brief, interfaces are agreed
  before anyone starts, and each developer owns its files.
- **Review from another vendor.** A model reviewing code written by its own kind tends to share its
  blind spots. Reviews by a different vendor's model found real bugs that same-model review missed.
- **Fix with a failing test first, or decline with a reason.** Both are recorded.
- **Explicit models on every agent, never above the session's.** An agent inherits the session's
  model and its usage cap; three agents on one capped model died mid-run. Narrow work runs a tier
  down.
- **Most of a run's cost is context, not output.** One UI overhaul (15 hours, 6 of them
  stopped at usage limits) showed where it went: a lead re-reading about 500k tokens on every call,
  small fixes made inside agents resumed at 200k tokens, an integrator stage every package waited
  on, critic loops that couldn't converge on stills, five PRs for an owner who merged them at once.
  Hence build cards, brief reports, fresh small agents for fixes, scene hooks instead of an
  integrator, capped review and critic rounds, and a PR per checkpoint.
- **Whole epics overnight.** Several epics were built unattended, each piece reviewed. Every gate
  stayed provisional until the owner played the result.
- **Hands-off means no setup questions mid-run.** The first hands-off test stopped on three questions:
  an ADR to allow agent merges, no branch protection on a free private repo, and no second account for
  the reviewer. Each is now settled ahead of time or by default:
  - setup records agent merges on day one;
  - the reviewer's verdict is a PR comment carrying the commit it approved;
  - a merge guard hook stands in for branch protection.
- **The review cap ends the review, not the run.** A later run stopped its whole epic on its first
  package because the reviewer still requested changes after two cycles, and the guard accepted only
  the reviewer's approval. Now the lead rules on what's left and merges on a ruling marker the guard
  accepts after two reviewer verdicts; a PR stops only for data, security or repository rules.
- **A second agent has to see something different.** An audit of every place the package spawned
  agents kept the ones that see differently: blind playtesters, the builder's read, another vendor's
  reviewer, research that keeps web pages out of the lead's context. It trimmed the ones that only
  played a role on the same model. Rules that relied on an agent's obedience became scripts (the
  Codex review runner, which can't fall back silently; the blind-playtest folder; the GDD and ledger
  checks), because a script holds on every model and the users' models vary.

## 8. Play — `playtest`

**Produces:** blind AI playtest reports and the owner's findings, mapped to fixes and tests.

- **"A green suite is not acceptance."** The rejected boss system passed every test.
- **Blind means blind.** On the first AI playtest panel, playtesters were started inside the
  repository and loaded its instructions automatically, so they knew every boss trick before playing.
  Blind playtesters now start from an empty folder.
- **Findings to fixes to tests.** After one playtest, fifteen findings went into a document and each
  was mapped to its fix and the test that pins it. Four of them turned out to be one bug each in a
  shared piece of code. Fixing them there fixed ordinary play too.

## 9. Ship — `release`

**Produces:** a build on a restricted (playtest) or public itch.io page.

The original project shipped one bug that only existed in the exported build: the export silently
dropped settings that the editor showed and the tests never noticed. So the release pipeline boots the
**exported** build before uploading it.

## 10. Keep it true — `docs-cleanup` and `design-change`

**Produces:** documents that guide agents without blocking ideas.

Agent instructions decay. The status file once grew to 11,000 words. Worse, old sentences started
acting as rules: a session read outdated lines as "no dialogue system" and built a proposal around
that limit, which the owner threw away. Two principles came out of it:

- **The owner beats the docs.** A direct instruction is the approval; a document that disagrees is out
  of date.
- **Mechanism, not taste.** Rules may protect the repository, but never decide creative calls.

`docs-cleanup` runs at the end of every epic to delete stale text and flag rules that police taste.
`design-change` is the procedure for reversing a decision on purpose: state the cost once, build it,
and close the record (a new ADR, superseded notes, a dated GDD amendment).

## 11. Bugs — `bug-intake`

**Produces:** triaged bugs and fix pull requests that start from a failing test.

The newest piece, and the least tested. Issue text is untrusted input, so agents only act on labels
that only maintainers can apply, with a daily cap and nothing but the model key in reach.
