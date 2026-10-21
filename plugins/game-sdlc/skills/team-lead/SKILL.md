---
name: team-lead
description: Build an epic or feature as the lead of a small agent team — write a shared brief, split the work across parallel developer agents with interfaces agreed up front, get an adversarial review of each piece from a model of another vendor (or a fallback model), get art direction and assets when needed, playtest, run the project's checks, clean the docs, open stacked pull requests for the owner to merge, and report with a short story page. Use when the user invokes team-lead, asks to "run the team", "be the lead", or build an approved plan or epic with agents.
argument-hint: "The epic, feature or plan to build"
---

# Team lead

You are the lead, not the main implementer: you direct, decide, review and integrate. The user
describes **what** to build and anything unusual about this run; this playbook covers the rest, and
the user's instructions override it wherever they differ.

Templates for the brief, the developer and reviewer prompts, the art-direction prompt and the final
report are in [templates.md](templates.md). The story page is [story_template.html](story_template.html).
The agents are this plugin's `team-developer` and `adversarial-reviewer`
(`game-sdlc:team-developer`, `game-sdlc:adversarial-reviewer` when installed as a plugin).

## 1. Settle the ask

Start from the approved plan and its ledger when there is one (`feature-planning`); they settle
most of this. Otherwise establish:

- **Scope:** the feature, what's out, what must stay unchanged, whether it's opt-in.
- **Art:** whether any is needed; if a paid generator is involved, a credit budget.
- **Delivery:** new pull requests, an existing one, or local changes only.
- **Overrides:** models, number of review rounds, steps to skip.

Ask only about real forks that the plan, the code or a sensible default can't settle; ask them
together, each with your recommendation first. Never spend paid credits without an approved budget.

## 2. Names

Give every agent a name from **famous video game characters**, mixed across series, and keep the
mapping for the session. You pick yours too. For example: lead **Link**; developers **Samus**,
**Lara**, **Geralt**, **Aloy**; reviewer **GLaDOS**; art director **Tifa**. Codex or other external
models get names as well. If the user gives a theme, use it.

**Names are session-only.** Never put them in code, comments, tests, docs, scene files, commit
messages or PR text. Agents tend to credit each other in comments ("Samus's numbers"); tell every
developer this rule, and grep the staged diff for every name before each commit.

## 3. Roles and models

| Role | How | Default |
|---|---|---|
| Developer | `team-developer` agent | The strongest model available; set `model:` explicitly on every spawn, since an agent otherwise inherits the session's model and its usage cap. One agent per independent piece |
| Adversarial review | `adversarial-reviewer` agent | A model from **another vendor** when the environment has one (for example Codex through its Claude Code plugin); otherwise a different model from the developers' |
| Art direction | another vendor's model, or a second model | At most two rounds; one preferred |
| 2D art | `comfyui-art` (local) → Codex image generation → Meshy | In that order of availability |
| 3D art | Meshy, low poly, rigged if a character | Credit ledger in the scratchpad; confirm every paid call |

Say in the report which reviewer actually ran, and why if it was the fallback.

## 4. Phases

1. **Recon.** Read the project's `AGENTS.md`/`CLAUDE.md`, the plan and ledger, and the code you'll
   build on. Find the gate: tests, lint, format, coverage, and how hooks run. Check that hooks are
   installed in this checkout; worktrees often lack them.
2. **Brief.** Write `BRIEF.md` in the scratchpad: the goal, the architecture decisions you made,
   where new code may live, what's off-limits, conventions, how to run things. Every agent reads it.
3. **Split and spawn.**
   - Split by responsibility so developers rarely touch the same file.
   - **Agree the interfaces up front**: the exact signature one agent provides and another calls.
     Each agent owns its files; a shared file needs surgical edits and a re-read before editing.
   - Spawn independent agents in one message, in the background. Run at most two or three at once.
4. **Review as each piece lands**, not at the end. Start the adversarial review of a finished piece
   while others are still working; scope it to that piece; tell the reviewer what the feature must
   guarantee and ask for concrete failure scenarios, no style nits.
5. **Triage every finding.**
   - **Fix:** send it back to the owning agent, asking for a test that fails before the fix.
   - **Decline:** state the reason (no player-visible effect, would break a boundary, cost outweighs
     risk) and record it for the report.
   - Prefer one structural rule over a timing patch.
6. **Lead playtest.** Run the real thing through the project's run, screenshot and input tools, and
   go for paths the agents didn't try: acting mid-animation, acting twice quickly. Look at the
   screenshots. For a bigger change, also run the `playtest` skill's blind AI playtesters.
7. **Gate.** Run the full suite, coverage and lint/format over the whole scope. Compare failures with
   known pre-existing ones and name them. Revert files a tool rewrote by accident. Grep for agent names.
8. **Clean the docs.** Run the `docs-cleanup` skill on what this epic changed, before delivery.
9. **Deliver.**
   - **One pull request per feature, stacked**: each feature's branch starts from the previous one's,
     and its PR targets that branch. Ask the owner once to enable GitHub's *Automatically delete head
     branches*: when a PR in the stack merges and its branch is deleted, GitHub retargets the next PR
     on its own. To move the whole stack after a change lower down, use `git rebase --update-refs`.
   - Each PR body: what was built, where assets came from, the test plan with real numbers, review
     notes, and the issue references (`Closes` / `Ref`, see `issue-tracking`).
   - Move features to `In Review`. **Don't merge** — the owner does (`team-lead-handsoff` is the
     variant that merges).
10. **Report** in two parts: the short chat report (template in templates.md) and the story page (§5).
11. **Offer the next step**: playing it (`playtest`), then the next feature from the GDD with
    `feature-planning-handsoff` or `feature-planning`. Offer it **in the working style**: the `Working style` line in the project's `AGENTS.md`, or, before a project exists, the mode of the skill that just ran (`gdd-handsoff` means hands-off). Hands-off: offer the `-handsoff` variant first. Interactive: offer the interactive skill, and mention the hands-off variant once.

Between phases, keep the user posted in one or two sentences: who's doing what, and what you're
waiting for.

## 5. Running log and story page

**Keep a running log from the first minute.** Append one JSON line per event to `team_log.jsonl`
in the scratchpad: `{"ts", "phase", "from", "to", "kind", "text", "verbatim", "img"}`, where `kind` is
one of ask, brief, report, finding, fix, decision, declined, question, answer, art, status. Log each
user ask and answer, each brief in a line, the best verbatim line of each agent's report, each
finding and what happened to it, each decision with its reason, and each playtest bug. Copy any
screenshot worth showing to `story_img/`.

**The story page is short.** It is not a changelog; it tells the run in **four to six chapters**:

1. **Who did what** — how the work was split and delegated.
2. **Pushback** — where an agent or the reviewer pushed back on the brief or a decision.
3. **Disagreements** — where the reviewer and a developer disagreed, and how it was settled.
4. **Tests and result** — the real numbers, what passed, what didn't, what was declined.
5. **Try it yourself** — how the owner can test it by hand: entry point, steps, what to look for.

Use quotes from agents throughout (verbatim from the log, at most 30 words, trimmed with […]);
everything else is narrative. Never invent dialogue, opinions or numbers. Agents don't talk to each
other; say how work actually connected (through the lead, the brief, an interface).

Build it from [story_template.html](story_template.html) by replacing `__TITLE__` and `__DATA__`
(the data shape is in its script). Convert screenshots to JPEG around 1400 px wide. Publish it as a
private page if an artifact or page tool is available, otherwise save it next to the report, and
give the owner the link or path.

## 6. Lessons

- Parallel agents in one checkout run and stop **only their own** game instance, by process id.
- Check `git status` after every tool or editor run: editors and importers silently rewrite project
  files. Tell agents not to open GUI editors.
- On Windows PowerShell 5.1, `Get-Content`/`Set-Content` round-trips mangle non-ASCII characters;
  edit with the Edit tool or bash.
- A reviewer can't see work in progress: scope each review to a finished piece.
- Ask agents for evidence — tests with results, screenshots they looked at, gaps. "Done" without
  evidence isn't done.
- If the other-vendor reviewer runs out of quota mid-run, switch to the fallback and say so.
