---
name: team-lead-handsoff
description: Run team-lead with no owner in the loop — a reviewer from another model vendor (or a fallback model) reviews each feature pull request, its verdict is posted on the PR, and once CI, the verdict and an exported-build smoke test all pass, the lead merges it to main itself, tagging main first so any merge can be reverted. It doesn't stop for setup questions: it adopts agent merges with an ADR if the project hasn't yet, and relies on the project's merge guard where GitHub branch protection isn't available. Use only when the owner explicitly asks for a fully hands-off build that merges.
argument-hint: "The epic, feature or plan to build and merge"
disable-model-invocation: true
---

# Team lead, hands-off

Load the **`team-lead`** skill (`game-sdlc:team-lead` when installed as a plugin) and follow it, with
the differences below. The owner chose to let reviewed work reach `main` without them; this skill's
job is to make that safe enough to undo, **without stopping to ask** about anything the owner's
invocation already decided.

## 0. Before building: settle it, don't ask

Invoking this skill *is* the owner's decision that agents may merge reviewed work. So:

1. **Agent merges.** If `.agents/merge-policy.json` already says `"agent_merges_to_main": true`, go on.
   If the file is missing, adopt agent merges as the first piece of work:
   - fill [agent-merges-adr-template.md](agent-merges-adr-template.md) into the next free ADR number
     (`CONTEXT`: "Adopted on <date>, when the owner first ran team-lead-handsoff."), and add its row
     to the ADR index;
   - write `.agents/merge-policy.json`: `{"agent_merges_to_main": true, "adr": "docs/adr/<file>"}`;
   - add one line to `AGENTS.md` where it forbids committing to `main`: "Agents may merge a reviewed
     pull request into `main` only through `team-lead-handsoff`'s merge checklist (ADR-<n>)";
   - commit it on `policy/agent-merges`, open it as a pull request, and merge it first, under the
     same checklist (§2) as everything else.

   Say in the report that you did this, and why. **The only reason to stop here** is a policy file that
   says `false`: that's an earlier, explicit "no" from the owner — ask once.
2. **Branch protection.** Try to protect `main` (required CI check, pull requests required, zero
   approvals). If GitHub refuses because the plan doesn't allow it on a private repository, don't
   ask: the project's merge guard covers agents' merges. Say which one is in force. A project
   without `.agents/hooks/merge_guard.py` (set up some other way) has neither: then the checklist in
   §2 is the only gate, so check CI (`gh pr checks <n>`) and the verdict yourself before every merge.
3. **The reviewer's verdict.** It goes on the pull request as a **comment** (§1). If a reviewer
   token is available (e.g. `REVIEWER_GH_TOKEN` for a GitHub App or machine account), also submit it
   as a real review with that identity; without one, the comment is enough. Don't ask.
4. **Auto-delete head branches** on, so stacked pull requests retarget as each merges.

Stop only for what can't be settled: no CI workflow at all (nothing could ever pass the guard), or
`gh` not signed in. Say exactly what's missing.

## 1. Review, verdict, and a limit

For each feature PR, the `adversarial-reviewer` reviews it as in `team-lead`; its report ends with
`VERDICT: approve` or `VERDICT: request-changes`.

Post the report on the PR **verbatim**, as one comment (`gh pr comment <n> --body-file <file>`),
ending with the machine-readable verdict for the head commit that was reviewed:

```text
<!-- game-sdlc-review: approve sha=<the PR's headRefOid at review time> -->
```

(or `request-changes`). Get the sha from `gh pr view <n> --json headRefOid`. **Never write an
`approve` marker the reviewer didn't give**, and never edit the reviewer's text. A new commit makes
the verdict stale — the merge guard checks the sha — so every fix gets a fresh review.

- **Request changes** → the owning developer fixes each finding with a test that fails first; review
  again.
- **Two rounds of disagreement** (still disagreeing after two fix rounds, or a declined finding the
  reviewer holds) → stop on that PR: leave it open, label it `needs-owner`, and comment both positions
  in a few lines. Continue with features that don't depend on it.

## 2. The merge checklist

Merge only when every line is true, and post the checklist on the PR as a comment:

- [ ] CI is green on the PR's latest commit. *(the merge guard checks)*
- [ ] The latest verdict approves the current head commit. *(the merge guard checks)*
- [ ] The **exported build** passes its smoke test, run on this branch.
- [ ] `main` is tagged `pre-merge/<feature-slug>-<yyyymmdd>`, pushed.

Then `gh pr merge <n> --merge --delete-branch`. Never `--admin`. A merge commit keeps each feature
revertable as one unit; deleting the branch lets GitHub retarget the next PR in the stack. If the
merge guard refuses, read its reason and fix that — never route around it through the API.

## 3. After each merge

Pull `main` and run the full suite. If it's red, open a revert PR for that merge commit, take it
through the same checklist, label the original PR `needs-owner`, and stop the remaining stack.

## 4. Tracking

Merging a PR that says `Closes` moves its issue to `Done` — here that's the act the owner delegated.
Say so in the report. Epics stay `In Review` until the owner has played the result: every gate is
provisional until then.

## 5. Report

The `team-lead` report and story page, plus: whether agent merges were adopted in this run (and the
ADR), which protection was in force (branch protection or the merge guard), every PR merged with its
tag, every PR left `needs-owner` and why, and any revert.
