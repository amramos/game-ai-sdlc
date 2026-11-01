---
name: team-lead-handsoff
description: Run team-lead with no owner in the loop — a reviewer from another model vendor (or a fallback model) reviews each pull request, its verdict is posted on the PR, and once CI, the verdict and an exported-build smoke test all pass, the lead merges it to main itself, tagging main first so any merge can be reverted. It doesn't stop for setup questions: it adopts agent merges with an ADR if the project hasn't yet, and relies on the project's merge guard where GitHub branch protection isn't available. Use only when the owner chose a hands-off build that merges: by invoking it, by picking it in feature-planning-handsoff's up-front question, or by asking for it in their own words. Never pick it on your own initiative.
argument-hint: "The epic, feature or plan to build and merge"
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
5. **A merge guard that knows lead rulings.** If `.agents/hooks/merge_guard.py` exists but doesn't
   mention `game-sdlc-lead-ruling` (a project set up before 0.7.1), copy `merge_guard.py` and
   `.agents/tests/hooks/test_hooks.py` from `setup-godot`'s `project-template`, run the hook tests,
   and land them in the first pull request with the policy, or in one of their own.

Stop only for what can't be settled: no CI workflow at all (nothing could ever pass the guard), or
`gh` not signed in. Say exactly what's missing.

## 1. Review, verdict, and a limit

For each pull request (one per checkpoint, as `team-lead` delivers them), the `adversarial-reviewer`
reviews it as in `team-lead`; its report ends with `VERDICT: approve` or `VERDICT: request-changes`.

Post the report on the PR **verbatim**, as one comment (`gh pr comment <n> --body-file <file>`),
ending with the machine-readable verdict for the head commit that was reviewed:

```text
<!-- game-sdlc-review: approve sha=<the PR's headRefOid at review time> -->
```

(or `request-changes`). Get the sha from `gh pr view <n> --json headRefOid`. **Never write an
`approve` marker the reviewer didn't give**, and never edit the reviewer's text. A new commit makes
the verdict stale — the merge guard checks the sha — so a fix needs a fresh verdict, or, once the
two cycles are spent, your ruling on the new head.

- **Request changes** → each finding is fixed with a test that fails first (inline, or by a fresh
  agent, as in `team-lead`). A PR with fixes always gets the second cycle: a verification scoped to
  the fix diff, not a new hunt.
- **Two cycles, then you decide.** The cap ends the review, not the work. Still `request-changes`
  after the second cycle is the normal case, not a stop: rule on each finding the reviewer still
  holds, as the owner's stand-in:
  - **fix** it with a test that fails first (no third review; CI and the smoke test cover the fix);
  - **decline** it, with a reason (no player-visible effect, would break a boundary, cost outweighs
    risk);
  - or **defer** it to an issue linked from the PR.

  Then post one comment listing each finding and its ruling, ending with the marker for the head
  commit you're merging:

  ```text
  <!-- game-sdlc-lead-ruling: merge sha=<the PR's headRefOid now> -->
  ```

  The merge guard accepts it only after two reviewer verdicts on the PR. It's your ruling, under your
  name: it never stands in for the reviewer's verdict, and the reviewer's comments stay as they are.
- **Stop on a PR only** when a finding you can't fix now could lose the player's save or data, open
  a security hole, or break a rule that protects the repository (`AGENTS.md`), or when you can't
  judge it at all. Then leave the PR open, label it `needs-owner`, comment both positions in a few
  lines, and go on with work that doesn't depend on it. If later packages do depend on it, the epic
  stops there; say so in the report. Disagreeing with the reviewer is not a reason to stop.

## 2. The merge checklist

Merge only when every line is true, and post the checklist on the PR as a comment:

- [ ] CI is green on the PR's latest commit. *(the merge guard checks)*
- [ ] The latest verdict approves the current head commit, or, after two cycles, your ruling
      covers it. *(the merge guard checks)*
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
tag, every PR merged on your ruling with the findings you declined or deferred (the owner checks
those first when playing), every PR left `needs-owner` and why, and any revert.
