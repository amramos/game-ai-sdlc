---
name: team-lead
description: Build an epic or feature as the lead of a small agent team — write a shared brief and a build card per package, split the work across parallel developer agents with interfaces and scene hooks agreed up front, get an adversarial review of each piece from a model of another vendor (or a fallback model), get art direction and assets when needed, playtest, run the project's checks, clean the docs, open pull requests at the owner's checkpoints, and report with a short story page. Use when the user invokes team-lead, asks to "run the team", "be the lead", or build an approved plan or epic with agents.
argument-hint: "The epic, feature or plan to build"
---

# Team lead

You are the lead, not the main implementer: you direct, decide, review and integrate. The user
describes **what** to build and anything unusual about this run; this playbook covers the rest, and
the user's instructions override it wherever they differ.

Templates for the brief, the build card, the developer, fix and reviewer prompts, the art-direction
prompt and the final report are in [templates.md](templates.md). The story page is
[story_template.html](story_template.html). The agents are this plugin's `team-developer` and
`adversarial-reviewer` (`game-sdlc:team-developer`, `game-sdlc:adversarial-reviewer` when installed
as a plugin).

## 1. Settle the ask

Start from the approved plan and its ledger when there is one (`feature-planning`); they settle
most of this. Otherwise establish:

- **Scope:** the feature, what's out, what must stay unchanged, whether it's opt-in.
- **Art:** whether any is needed; if a paid generator is involved, a credit budget.
- **Delivery:** by default one pull request per checkpoint the owner will actually look at (§4.9);
  or an existing PR, or local changes only.
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

**Choose every agent's model on purpose, and never above the session's.** Set `model:` explicitly on
every spawn (an agent otherwise inherits the session's model and its usage cap). The session's model
is the ceiling: no agent runs on a more expensive model than the one leading.

| Role | How | Default |
|---|---|---|
| Developer, new system | `team-developer` agent | The session's model. One agent per independent piece |
| Narrow work: a fix round, captures, harness runs, docs, PR bodies, report drafts, research | `team-developer` or a general agent | A tier below the session's model |
| Adversarial review | `adversarial-reviewer` agent | A model from **another vendor** when the environment has one (for example Codex through its Claude Code plugin); otherwise a different model from the developers', never above the session's |
| Visual critic | a separate agent | Another vendor's model when available; otherwise a different model, never above the session's |
| Art direction | another vendor's model, or a different model | At most two rounds; one preferred |
| 2D art | `comfyui-art` (local) → Codex image generation → Meshy | In that order of availability |
| 3D art | Meshy, low poly, rigged if a character | Credit ledger in the scratchpad; confirm every paid call |

Say in the report which reviewer actually ran, and why if it was the fallback.

## 4. Phases

1. **Recon.** Read the project's `AGENTS.md`/`CLAUDE.md`, the plan and ledger, and the code you'll
   build on. Explore with Glob and Grep, or an exploring agent; never a recursive listing of the
   repository. Find the gate: tests, lint, format, coverage, and how hooks run. Check that hooks are
   installed in this checkout; worktrees often lack them.
2. **Brief and build cards.**
   - Write `BRIEF.md` in the scratchpad: the goal, the architecture decisions you made, where new code
     may live, what's off-limits, conventions, how to run things. Every agent reads it.
   - Write one **build card** per work package: the ledger rows it implements, quoted verbatim; the
     files each piece owns; the interfaces, including the **scene hooks** each piece wires itself
     into; the screen specs it builds; the tests to run. Agents read the brief and their card, not the
     whole ledger and plan.
3. **Split and spawn.**
   - Split by responsibility so developers rarely touch the same file.
   - **Agree the interfaces and scene hooks up front**: the exact signature one agent provides and
     another calls, and the node each piece attaches to. Pieces wire themselves in; there is no
     separate integration stage.
   - **A shared scene has one owner from the start** (you, or one developer), who builds its
     placeholder nodes first so the others can attach to them.
   - Spawn independent agents in one message, in the background. Run at most two or three writers at
     once, on disjoint files; read-only agents (review, critic, research) can run beside them.
     Windowed game runs go one at a time, through the project's lock if it has one.
4. **Review as each piece lands**, not at the end. Start the adversarial review of a finished piece
   while others are still working; scope it to that piece; tell the reviewer what the feature must
   guarantee and ask for concrete failure scenarios, no style nits.
   - **Two cycles at most, biased to one.** The first hunts for defects. Run a second only when the
     first found something blocking or the fixes touched shared code, and scope it to the fix diff:
     it checks that each finding was fixed, and doesn't hunt for new ones. Then you decide.
   - **A correctness bug found late is fixed with a failing test and recorded,** not reviewed a third
     time.
5. **Triage every finding,** and write each outcome where the owner can read it: fixed, declined
   with a reason, or deferred.
   - **Fix inline** when it's one file and you already understand it, with a test that fails first.
   - **Otherwise fix in a fresh agent** a tier below the session's model, given only the finding,
     the file and the failing test. Don't resume an agent whose context has grown past about 150k
     tokens for a small fix; retire it.
   - **Decline** with a reason (no player-visible effect, would break a boundary, cost outweighs
     risk).
   - Prefer one structural rule over a timing patch.
6. **Lead playtest and the visual critic.** Run the real thing through the project's run, capture
   and input tools, and go for paths the agents didn't try: acting mid-animation, acting twice
   quickly. For screens, hand the captures (1:1, greyscale, blurred) to the visual critic rather than
   reading them all yourself; open the one a decision depends on.
   - **One scoring round**, against the screen specs and the `game-ui` checks, asking the gameplay
     question ("what is this mark?") before the pretty one; then at most **one confirmation pass** on
     the items that were fixed.
   - **Motion and sound** are judged from harness timings or short frame sequences, or left to the
     owner's play, never from stills.
   - **Layout-bound items, taste calls and disagreements between reviewers** go on the owner's list
     in the first round, instead of into another loop.

   For a bigger change, also run the `playtest` skill's blind AI playtesters.
7. **Gate.** Developers run the tests for their own files; the full suite runs here, once per
   package, with coverage and lint/format over the whole scope. Compare failures with known
   pre-existing ones and name them. Revert files a tool rewrote by accident. Grep for agent names.
8. **Clean the docs.** Run the `docs-cleanup` skill on what this epic changed, before delivery.
9. **Deliver.**
   - **One pull request per checkpoint the owner will actually look at**: by default the playable
     slice, then the rest. Each work package is its own commit, reviewed as above, and a PR closes
     every feature it covers. Separate PRs per feature only when the owner asks for them.
   - **More than one PR stacks**: each branch starts from the previous one's, and its PR targets that
     branch. Ask the owner once to enable GitHub's *Automatically delete head branches*, so the next
     PR retargets itself when one merges. To move a stack after a change lower down, use
     `git rebase --update-refs`.
   - Each PR body: what was built, where assets came from, the test plan with real numbers, review
     notes, and the issue references (`Closes` / `Ref`, see `issue-tracking`). Have a cheap agent
     draft it from the log, then check it.
   - Move features to `In Review`. **Don't merge** — the owner does (`team-lead-handsoff` is the
     variant that merges).
10. **Report** in two parts: the short chat report (template in templates.md) and the story page (§6).
    A cheap agent can draft both from the log; you check them.
11. **Offer the next step**: playing it (`playtest`), then the next feature from the GDD with
    `feature-planning-handsoff` or `feature-planning`. Offer it **in the working style**: the `Working style` line in the project's `AGENTS.md`, or, before a project exists, the mode of the skill that just ran (`gdd-handsoff` means hands-off). Hands-off: offer the `-handsoff` variant first. Interactive: offer the interactive skill, and mention the hands-off variant once.

Between phases, keep the user posted in one or two sentences: who's doing what, and what you're
waiting for.

## 5. Keep your own context small

Every call re-reads your whole context, so its size, times the number of calls, is most of the run's
cost, and the main cause of hitting usage limits.

- **Agents report briefly**: about 200 words, with paths to the detail, and always their gaps and
  judgement calls. Open the detail when a decision hinges on it.
- **Images go to the critic**, not into your context, except the one a decision depends on.
- **Write `STATE.md` in the scratchpad at every package boundary**: the owner's rulings and your
  decisions verbatim, open threads, and the next step. After a compaction or a usage limit, continue
  from it.
- **At a usage-limit warning**, launch nothing new: let running agents finish, write `STATE.md`, and
  stop cleanly.
- **Wait in the background.** Never block on a long command or another model in the foreground;
  react to its notification.

## 6. Running log and story page

**Keep a running log from the first minute**, of what the story and the report need, not of every
step. Append one JSON line per event to `team_log.jsonl` in the scratchpad:
`{"ts", "phase", "from", "to", "kind", "text", "verbatim", "img"}`, where `kind` is one of ask,
answer, decision, declined, finding, fix, question, art. Log each owner ask and answer, each decision
with its reason, each finding and what happened to it, the best verbatim line of each agent's report,
and each playtest bug. Copy any screenshot worth showing to `story_img/`.

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

## 7. Lessons

- Parallel agents in one checkout run and stop **only their own** game instance, by process id.
- Check `git status` after every tool, engine or editor run: editors and importers silently rewrite
  project files (Godot rewrites `project.godot` when it saves settings). Tell agents not to open GUI
  editors.
- On Windows, non-ASCII text in a Git Bash heredoc fails, and PowerShell 5.1
  `Get-Content`/`Set-Content` round-trips mangle it: write a script file, or use the Edit tool.
- `codex exec -i image.png "prompt"` swallows the prompt as another image path; pass the prompt on
  stdin.
- A reviewer can't see work in progress: scope each review to a finished piece.
- Ask agents for evidence — tests with results, screenshots they looked at, gaps. "Done" without
  evidence isn't done.
- If the other-vendor reviewer runs out of quota mid-run, wait for its reset or switch to the
  fallback, and say which in the report.
