---
name: issue-tracking
description: Keep the issue board (Linear first; GitHub Issues as an adapter) in step with the work — turn an approved plan into an epic with one feature per work package, read owner rulings from issue comments before writing code, move status as work lands (In Review, never Done), and reference issues in pull requests. Use at the start of any session that names an epic or feature, when a plan is approved, and whenever tracked work changes state.
---

# Issue tracking

The **repository holds the specification** (the GDD, the approved plan and its ledger). The
**board is where the work is tracked**. When they disagree about scope, the repository wins and the
board gets corrected — never the reverse.

The tracker is usually a client-level connector (for example Linear's), so no session is guaranteed
to have it. Everything below degrades gracefully (§8).

## 1. Two levels: Epic → Feature

- **Epic** — one approved plan.
- **Feature** — one work package from that plan. The smallest thing that gets a status change, and
  one commit in the delivery. A pull request covers one of the owner's checkpoints, so it may close
  several features at once (`Closes` for each).
- **No story level.** A story-sized piece of work is a **checklist line** in its feature's
  description, ticked in the same edit that lands it. A checklist line big enough to want its own
  review should have been its own feature: say so and offer the split.

Why: a ticket that is never scheduled, assigned or commented on by itself is a line of acceptance
criteria wearing a ticket costume. Story tickets crowd the board (Linear's free plan caps active
issues) and nobody reads them.

## 2. From an approved plan to an epic

Approving a plan authorizes creating its epic. Then:

1. Create the epic. Its **description is the plan's approval record**; link the ledger and the plan.
2. Post the **decisions ledger** (or its decisions table) as the epic's first comment.
3. Create **one feature per work package**, in the plan's order, each with its checklist and its
   checkpoint, and with dependencies noted.
4. Mirror the issue ids back into the plan's work-package table.

Any other restructuring — renaming epics, deleting issues, changing labels — is the owner's call:
report the gap and offer, don't act.

## 3. Read the issue before writing code

When a session names an epic or feature, find it **before reading code**, and read its comments.
Comments carry **owner rulings from earlier sessions**: deferrals, scope splits, decisions that are
requirements. They are often newer than the plan. Search by the identifier or title in the plan;
never guess an issue id.

## 4. Branch, and confirm the branch before each commit

Starting an epic means a branch cut from a freshly pulled `main`. Agents never commit to `main`
(unless the project's own rules allow it, as `team-lead-handsoff` does for merges). A session can be
moved onto `main` by a merge or a pull between two commands, so **confirm the current branch right
before every commit**, not once at the start.

## 5. Status moves when work lands

| Level | When it moves |
|---|---|
| Feature | `In Progress` when work starts; `In Review` the moment it lands and validates |
| Epic | `In Progress` at kickoff; `In Review` once every feature is |

**Never move anything to `Done`.** `Done` means the owner reviewed and accepted it, which no amount of
self-checking replaces. Merging a pull request that says `Closes` is the owner's act (or, under
`team-lead-handsoff`, the act the owner delegated), and that's what moves an issue to `Done`.

> **Linear's auto-close-parent setting cascades.** Closing or cancelling the last open child closes
> the parent, and then the parent's parent. Snapshot statuses before any bulk change and compare
> afterwards; the per-issue result only reports the child you edited.

## 6. Pull requests name their issues

End every pull request body for tracked work with one line each:

```text
Closes ABC-12, ABC-13
Ref ABC-10
```

- `Closes` for issues this merge completes;
- `Ref` for issues it only advances (an epic still open on other features, a feature this sets up).

A wrongly-closed issue looks reviewed, so when in doubt, `Ref`. The keywords only work if the
tracker's GitHub integration is connected; check after a merge and update by hand if nothing moved.

## 7. Comment with reasons, not diff summaries

The diff is in git. A comment earns its place by recording what git can't show: owner rulings
(verbatim, with reasons), findings (with numbers), deferrals (with the issue that now owns the work,
commented on both ends), and resizes. Name the checklist line the comment is about.

## 8. When the tracker is unreachable or has no match

Both are normal; neither blocks the work.

- **No connector** — say so once, continue against the plan in the repository, and list at the end
  which issues would have been updated so the owner can apply them.
- **No match** — say what was searched, offer to create it, never invent an id.

Silently skipping tracking looks identical to tracking that worked; say which happened.

## 9. Concurrent writers

When another agent or client writes the same board (for example Claude and Codex working in parallel),
re-query right before creating anything, and use ownership labels on epics (`claude`, `codex`) so
neither takes the other's work. Filter work by traversing parents, not by those labels: they sit on
epics only and hide every feature underneath.

## GitHub Issues adapter

Without Linear, the same model maps onto GitHub:

| Concept | GitHub Issues |
|---|---|
| Epic | an issue labelled `epic`, with features as **sub-issues** |
| Feature | a sub-issue labelled `feature`, with its checklist as task list items |
| In Progress / In Review | labels `in-progress` / `in-review`, or a Projects board column |
| Done | closed by the merged PR's `Closes #n` |
| Rulings | comments on the issue, as in §7 |

`gh issue create`, `gh issue edit --add-label` and `gh api` for sub-issues cover every step.
