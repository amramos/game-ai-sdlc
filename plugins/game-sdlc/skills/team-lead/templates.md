# Team-lead templates

Fill the `<…>` parts. Cut what doesn't apply.

## BRIEF.md (scratchpad)

```markdown
# <Feature> — brief (session-only)

Lead: <lead name>. Checkout: `<absolute path>`. Scratchpad: `<absolute path>`.
Plan: `<plan path>` · Ledger: `<ledger path>` · Epic: <issue id>.

## What we are building
<2–5 sentences of player experience. What's opt-in, what stays unchanged.>

## Architecture (decided by the lead — don't change without asking)
- Reused as-is: <modules>.
- Off-limits: <files/dirs no one edits>.
- New code lives only in: <dirs>. The only allowed edits outside them: <list, with owner>.
- Pieces: <piece → owner → responsibility → interface it exposes>.

## Art direction
<Decisions from the art-direction round and docs/art/, or "no new art".>

## Conventions
- Read `AGENTS.md` / `CLAUDE.md` and <skills/docs> before writing code.
- Tests: <command>. Lint/format: <commands>. Run the game: <command>; stop only your own instance.
- Don't commit. Don't put agent names in the repo. Don't open GUI editors.
- Report: files, how to see it, evidence (tests and results, screenshots looked at), gaps.
```

## Developer task (spawn `team-developer` in the background, with an explicit `model:`)

```text
You are **<Name>**, a developer on a small team led by <Lead> (the main session).
<One line on what the game/feature is.> Your job: **<the piece>**.

Checkout: `<path>` (run everything from here). Read first: AGENTS.md / CLAUDE.md, <docs>, the brief
`<scratchpad>/BRIEF.md`.

## Decisions already made (by the owner — don't change)
<numbered list, citing ledger ids>

## Design (the lead's — follow it; if something truly blocks you, say so in your report)
<the shape: classes, where they live, what's pure and testable, what's off-limits>

## Interface with <Other agent> (working in parallel in the same checkout)
<exact signature, who calls it, when, which files belong to whom>

## Quality bar
<typing/lint rules, what the tests must cover, coverage floor, how to run tests and the game>

## Report back
Files created/changed, how to try it, what you verified with evidence, honest gaps, anything you need.
```

## Fix request (SendMessage to the owning agent)

```text
<Lead> here. <One specific line of credit for what worked.> The review of <piece> found <n> issues.
Fix each with a test that fails before the fix:

1. **<Severity> — <file:line> — <what goes wrong>.** <Concrete scenario.> Preferred shape: <direction>.

Declined (don't fix): <finding> — <reason>.
Re-run <tests/lint>. Don't commit. Report briefly.
```

## Adversarial review (spawn `adversarial-reviewer`)

```text
Adversarial code review, READ-ONLY (don't edit files). Repo: <stack>. Review ONLY <files / diff scope>.
<Already-reviewed neighbours: only check how they're called.>
Feature: <what it must guarantee — invariants, state rules, what must never happen>.
Find concrete bugs: <the risky areas: races, lost state, hidden information leaking, input leaks,
cleanup after exit, tests that can't fail>.
For each finding: file:line, a concrete failure scenario, severity. No style nits. Be concise.
```

## Art direction (another model, at most two rounds)

```text
You are the art director for <game>. Style guide: docs/art/art-direction.md and its frames.
Constraints: <renderer, platform, resolution, poly or palette budget, readability, tools available>.
Give decisions, not options: <characters / environment / lighting / UI / biggest risk>, each with a
short reason.
```

## Final report (to the owner)

```markdown
<One-paragraph verdict: what's in, which PRs, whether it was played end to end.>

**Story of this run:** <link or path>

**Try it yourself:** <entry point, steps, what to look for>

**How it went:**
- **<Name> (<role>, <model>):** <what they built, what review found, how it was fixed>
- **<Reviewer name> (<model; other vendor or fallback>):** <findings, which were real, which declined and why>
- **Art:** <rounds, credits spent of budget — or none>
- **My playtest:** <what I found and what changed>

**Checks:** <tests pass/fail with known failures named, coverage, lint>

**Things to know:** <untested platforms, choices to revisit, follow-ups>
```
