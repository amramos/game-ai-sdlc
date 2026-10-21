# ADR-{{NUMBER}}: Agents may merge reviewed pull requests into main

**Status:** Accepted
**Date:** {{DATE}}

## Context

This project's rule is that agents never land work on `main`: they branch, open a pull request, and
the owner merges. The owner wants some work built with no one in the loop (`team-lead-handsoff`),
which only finishes if an agent can merge. {{CONTEXT}}

## Decision

An agent may merge a pull request into `main` only through `team-lead-handsoff`'s merge checklist:

- every CI check on the pull request passed;
- a reviewer from another model vendor (or a fallback model) reviewed it, and its latest verdict
  approves the pull request's current head commit — posted on the pull request as
  `<!-- game-sdlc-review: approve sha=<head sha> -->`;
- the exported build passed its smoke test;
- `main` was tagged `pre-merge/<feature>-<yyyymmdd>` before the merge, so it can be reverted.

`.agents/merge-policy.json` (`"agent_merges_to_main": true`) records this for the hooks. The merge
guard (`.agents/hooks/merge_guard.py`, called by `guard_bash.py`) refuses an agent's `gh pr merge`
into `main` unless the policy, the checks and the verdict all allow it, and always refuses `--admin`.
Committing or pushing to `main` directly stays forbidden.

## Alternatives considered

- **The owner merges everything** — the default before this ADR. It keeps a human on every change to
  `main`, but a hands-off run can't finish.
- **Rely on GitHub branch protection alone** — the right control where it's available, but GitHub
  offers it on private repositories only on paid plans. The merge guard covers the agent's side
  either way.

## Consequences

- Hands-off runs reach `main` without the owner. Every gate is still provisional until the owner plays
  the result; a merge that turns out wrong is reverted from its `pre-merge/` tag.
- The guard is a safety net against mistakes, not a security boundary: a merge through the GitHub
  website or API doesn't pass through it.
- Setting `"agent_merges_to_main": false` turns agent merges off without deleting this record.

**Revisit when:** a bad merge reaches `main` despite the checklist, or the project gets branch
protection with required reviews and a separate reviewer account.
