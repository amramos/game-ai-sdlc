---
name: team-lead-handsoff
description: Run team-lead with no owner in the loop — a reviewer from another model vendor (or a fallback model) reviews each feature pull request, and once CI, the review and an exported-build smoke test all pass, the lead merges it to main itself, tagging main first so any merge can be reverted. Disagreements that survive two rounds are left open for the owner. Use only when the owner explicitly asks for a fully hands-off build that merges.
argument-hint: "The epic, feature or plan to build and merge"
disable-model-invocation: true
---

# Team lead, hands-off

Load the **`team-lead`** skill (`game-sdlc:team-lead` when installed as a plugin) and follow it, with
the differences below. The owner chose to let reviewed work reach `main` without them; this skill's
job is to make that safe enough to undo.

## 0. Preconditions — check before building anything

1. **The project allows it.** If the project's `AGENTS.md` says agents never land work on `main`, stop:
   that rule needs its own decision (an ADR changing it) before this skill may run. Offer to draft it.
2. **Branch protection on `main` requires CI.** Check with
   `gh api repos/<owner>/<repo>/branches/main/protection`. If it's missing, stop and give the owner
   the exact settings to enable (required status checks: the CI test job). Agents never change
   repository settings.
3. **A separate reviewer identity.** GitHub won't let a PR's author approve their own PR, so a
   review posted with the owner's account is only a comment. Look for a reviewer token (for example
   `REVIEWER_GH_TOKEN` for a GitHub App or machine account with write access). If there is none,
   ask the owner one question: set one up, or proceed with the reviewer's verdict posted as a PR
   comment and the merge checklist (§2) as the only gate.
4. **Auto-delete head branches is on**, so stacked PRs retarget as each one merges.

## 1. Review, with a limit

For each feature PR, the reviewer reviews it as in `team-lead`, then posts its verdict on the PR —
as a real review (approve / request changes) with the reviewer identity, or as a comment.

- **Request changes** → the owning developer fixes each finding with a test that fails first; the
  reviewer reviews again.
- **Two rounds of disagreement** (the lead and the reviewer still disagree after two fix rounds,
  or a finding is declined and the reviewer holds it) → **stop on that PR**: leave it open, label it
  `needs-owner`, and comment both positions in a few lines each. Continue with features that don't
  depend on it; the ones that do wait.

## 2. The merge checklist

Merge a PR only when every line is true, and write the checklist into the PR as a comment:

- [ ] CI is green on the PR's latest commit.
- [ ] The reviewer's verdict is approve, with no unresolved blocking finding.
- [ ] The **exported build** passes its smoke test (the engine pack's export check, run on this
      branch) — the editor and the export can disagree.
- [ ] `main` is tagged before the merge: `pre-merge/<feature-slug>-<yyyymmdd>`, pushed.

Then merge with a merge commit and delete the branch: `gh pr merge <n> --merge --delete-branch`.
A merge commit keeps each feature revertable as one unit, and deleting the branch lets GitHub
retarget the next PR in the stack.

## 3. After each merge

Pull `main` and run the full suite. If it's red, open a revert PR for that merge commit, merge it
once CI is green, label the original PR `needs-owner`, and stop the remaining stack.

## 4. What changes in tracking

Merging a PR that says `Closes` moves its issue to `Done` — here that's the act the owner delegated.
Say so in the report. Epics still stay `In Review` until the owner has played the result: every
gate is provisional until then.

## 5. Report

The `team-lead` report and story page, plus: every PR merged with its tag, every PR left
`needs-owner` and why, any revert, and which reviewer identity was used (bot or comment-only).
