---
name: docs-cleanup
description: Keep a game project's documents true and short so they guide agents without blocking ideas — after an epic, check the status snapshot, GDD markers, ADRs and agent instructions against the code and the owner's rulings, delete stale text instead of appending beside it, and flag rules that police creative calls rather than protect the repository. Run at the end of every epic (team-lead calls it before its report), or when the user asks to clean, reconcile or tidy the docs.
argument-hint: "Optional: the epic or area that just changed"
---

# Docs cleanup

Documents written for agents decay in a particular way: they grow, they keep describing things that
no longer exist, and old sentences start acting as rules nobody decided. Agents then cite them to
narrow or refuse what the owner asks. This skill is the regular sweep that stops that.

Two principles decide every edit:

- **The owner beats the docs.** A direct instruction from the owner is the approval; a document that
  says otherwise is out of date, not a reason to resist.
- **Mechanism, not taste.** A rule may protect the repository (branch discipline, typing, file
  formats, data shapes, tests). A rule that decides a creative call — which scenes exist, who speaks,
  what the player may learn when, what a screen must look like — is a design note at most, and gets
  flagged.

## 1. Scope it

Start from what the epic changed: `git diff <epic base>...HEAD --stat`, the plan and ledger, and the
epic's issue comments (owner rulings live there). Clean what that work touched, not the whole
repository, unless the owner asks for a full sweep.

## 2. Check each document against the code and the rulings

| Document | What to check | What to do |
|---|---|---|
| Status snapshot (`docs/current-status.md`) | Every sentence about what exists, what's open, test counts | Correct it; **delete** what no longer exists. Never append a second narrative beside an old one |
| GDD | `[BUILT]` / `[DESIGNED]` / `[OPEN]` markers; mechanics the epic changed; the amendments header | Move markers to the truth; a reversal not yet recorded goes to `design-change` |
| ADRs | Decisions this epic contradicted or superseded; missing **Revisit when** lines | A contradiction is either a bug in the code or an unrecorded reversal: ask which, don't guess |
| `AGENTS.md` / instructions | Rules that are stale, duplicated elsewhere, or police taste | Fix stale ones; replace duplicates with a link; **flag** taste rules (§3) |
| Architecture doc | New folders, layers, coordinators | Add what exists; remove what was deleted |
| Gotchas | Traps this epic hit | Add a short entry for any trap that cost real time |

**The code wins** when a document disagrees with it about what exists; fix the document in the same
change. When a document disagrees with an owner ruling, the ruling wins.

## 3. Flag, don't silently delete, rules that police taste

For each rule that decides a creative call, quote it, say why it reads as taste rather than
protection, and propose a rewrite that keeps only the mechanism (e.g. "scenes are typed data with
text keys" instead of "the story must be missable on first play"). The owner decides; list these in
the report.

## 4. Keep it short

- Prefer deleting over rewording. A paragraph about a removed system goes, not "formerly…".
- One fact, one place. Elsewhere, link to it.
- Volatile facts (test counts, what's in review) live only in the status snapshot.

## 5. Report

A few lines: what was corrected, what was deleted, which taste rules are flagged for the owner, and
any contradiction between code and an ADR that needs a decision. Commit the cleanup on the epic's
branch, as its own commit.
