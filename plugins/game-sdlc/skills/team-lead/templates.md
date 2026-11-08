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
<"Follow docs/art/art-direction.md" when it covers every asset this epic needs; the art director's
decisions only for the kinds it doesn't cover; or "no new art".>

## Conventions
- Read `AGENTS.md` / `CLAUDE.md` and <skills/docs> before writing code.
- Tests: <command>. Lint/format: <commands>. Run the game: <command>; stop only your own instance.
- Don't commit. Don't put agent names in the repo. Don't open GUI editors.
- Report: files, how to see it, evidence (tests and results, screenshots looked at), gaps.
```

## Build card (one per work package, scratchpad `CARD-<n>.md`)

```markdown
# Package <n>: <name> — build card

**Ledger rows it implements** (verbatim):
- D<n>: "<the answer, exactly as the ledger has it>"

**Pieces and files:** <piece> → <owner> → <files it owns>.
**Shared scene:** `<scene>`, owned by <owner>, who builds its placeholder nodes first.
**Interfaces and scene hooks:** <signature or node path> — provided by <piece>, used by <piece>.
**Screen specs:** <links, or "none">.
**GDD sections:** §<n> <heading>, … (read these, not the whole GDD).
**Tests:** each piece runs <its own test files>; the full suite runs at the gate.
```

## Developer task (spawn `team-developer` in the background, with an explicit `model:`)

```text
You are **<Name>**, a developer on a small team led by <Lead> (the main session).
<One line on what the game/feature is.> Your job: **<the piece>**.

Checkout: `<path>` (run everything from here). Read first: AGENTS.md / CLAUDE.md, <docs>, the brief
`<scratchpad>/BRIEF.md`, your build card `<scratchpad>/CARD-<n>.md` and the GDD sections it cites.
You don't need the whole ledger, plan or GDD; the card quotes the rows you implement.

## Decisions already made (by the owner — don't change)
<numbered list, citing ledger ids>

## Design (the lead's — follow it; if something truly blocks you, say so in your report)
<the shape: classes, where they live, what's pure and testable, what's off-limits>

## Interface with <Other agent> (working in parallel in the same checkout)
<exact signature, who calls it, when, which files belong to whom>

## Quality bar
<typing/lint rules, what the tests must cover, coverage floor, how to run tests and the game>

## Report back
About 200 words, with paths to the detail: files created/changed, how to try it, what you verified
with evidence, honest gaps and judgement calls, anything you need.
```

## Fix request (a fresh agent, a tier below the session's model, or the same model when there's none below)

The default for a fix the lead won't do inline. The fresh agent gets only what the fix needs.

```text
Fix one finding in <checkout path>. Read AGENTS.md / CLAUDE.md first; don't read anything else
beyond the files below.

Finding: **<severity> — <file:line> — <what goes wrong>.** <Concrete scenario.>
Preferred shape: <direction>.
The test that must fail before the fix and pass after: <test file and name, or "write one in <file>">.
Files you may edit: <list>.

Run <that test, then the tests for these files> and <lint>. Don't commit. Report in under 100 words.
```

Resume the original developer instead (SendMessage) only when its context is still small and the fix
needs what it knows.

## Adversarial review (a prompt file for the Codex runner; the same text for the fallback agent)

Write it to a file and pass it to `codex_review.py --prompt-file`. When the runner exits 2 or 3,
spawn `adversarial-reviewer` with the same text, preceded by this line:
`Codex runner: exit <code>, "<its message>". Review it yourself (your fallback).`

```text
Adversarial code review, READ-ONLY (don't edit files). Repo: <stack>. Review ONLY <files / diff scope>.
<Already-reviewed neighbours: only check how they're called.>
Feature: <what it must guarantee — invariants, state rules, what must never happen>.
Find concrete bugs: <the risky areas: races, lost state, hidden information leaking, input leaks,
cleanup after exit, tests that can't fail>.
For each finding: file:line, a concrete failure scenario, severity. No style nits. Be concise.
```

## Art direction (another model, at most two rounds; only for asset kinds the guide doesn't cover)

```text
You are the art director for <game>. Style guide: docs/art/art-direction.md and its frames.
New kinds of asset this epic needs, which the guide doesn't cover: <list>.
Constraints: <renderer, platform, resolution, poly or palette budget, readability, tools available>.
Give decisions for those kinds only, not options: <characters / environment / lighting / UI / biggest risk>, each with a
short reason.
```

## Final report (to the owner)

```markdown
<One-paragraph verdict: what's in, which PRs, whether it was played end to end.>

**Story of this run:** <link or path>

**Try it yourself:** <entry point, steps, what to look for>

**How it went:**
- **<Name> (<role>, <model>):** <what they built, what review found, how it was fixed>
- **<Reviewer name> (<model; Codex runner or fallback, and why>):** <findings, which were real, which declined and why>
- **Art:** <guide only, or art-director rounds and why; credits spent of budget — or none>
- **Models:** <each role that ran → its model; any role below its floor, and why>
- **My playtest:** <what I found and what changed>

**Checks:** <tests pass/fail with known failures named, coverage, lint>

**Things to know:** <untested platforms, choices to revisit, follow-ups>
```
