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
as a plugin). The Codex runner for reviews is `scripts/codex_review.py` in this skill's folder
(`<skill>` below).

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

**Choose every agent's model on purpose.** Set `model:` explicitly on every spawn (an agent otherwise
inherits the session's model and its usage cap).

- **The session's model is the ceiling for Claude subagents:** none runs on a more expensive model
  than the one leading.
- **"A tier below"** means a tier below the session's model, or the same model when there's none
  below.
- **A role with a floor may go above the ceiling through another vendor.** When the session is below
  a role's floor, give that role another vendor's stronger model if the environment has one (Codex,
  for example). If nothing at or above the floor is available, run the role on the best model you
  have and say so in the report.

The floor is the weakest model a role can be trusted on. **Strong:** a frontier model preferred,
mid-size at minimum. **Mid-size:** a vendor's middle tier (Sonnet-class). **Small:** its smallest
tier (Haiku-class).

| Role | How | Default | Floor |
|---|---|---|---|
| Lead (you) | the session | — | Strong when ruling on merges (`team-lead-handsoff`); otherwise as the session is |
| Developer, new system | `team-developer` agent | The session's model. One agent per package (§4.3) | Mid-size |
| Fix round | `team-developer` or a general agent, given the finding, the file and a failing test | A tier below | Small |
| Narrow work: captures, harness runs, docs, research | `team-developer` or a general agent | A tier below | Small (research findings carry links) |
| PR, report and story drafts (optional, §4.9–10) | a general agent | A tier below | Small |
| Adversarial review | the Codex runner (§4.1, §4.4); the `adversarial-reviewer` agent as fallback | A model from **another vendor** when the environment has one; otherwise a different model from the developers' | Strong |
| Visual critic | a separate agent | Another vendor's model when available; otherwise a different model | Mid-size |
| Art direction | another vendor's model, or a different model; only for asset kinds the style guide doesn't cover (§4.2) | At most two rounds; one preferred | Mid-size |
| 2D art | `comfyui-art` (local) → Codex image generation → Meshy | In that order of availability | — |
| 3D art | Meshy, low poly, rigged if a character | Credit ledger in the scratchpad; confirm every paid call | — |

**Say in the report which model filled each role**, which reviewer actually ran (and why, if it was
the fallback), and any role that ran below its floor.

## 4. Phases

1. **Recon.** Read the project's `AGENTS.md`/`CLAUDE.md`, the plan and ledger, and the code you'll
   build on. Explore with Glob and Grep, or an exploring agent; never a recursive listing of the
   repository. Find the gate: tests, lint, format, coverage, and how hooks run. Check that hooks are
   installed in this checkout; worktrees often lack them.

   **Check the reviewer route once, before the first review**, with the Codex runner that ships with
   this skill: `python <skill>/scripts/codex_review.py --probe`. Exit 0 means a route works; it
   prints `ROUTE: …`, which you record in `STATE.md`. Exit 2 means there is none: say so before
   building (in a hands-off run, in `STATE.md` and the report) and use the fallback reviewer
   knowingly; cross-vendor review is the point of the step.
2. **Brief and build cards.**
   - Write `BRIEF.md` in the scratchpad: the goal, the architecture decisions you made, where new code
     may live, what's off-limits, conventions, how to run things. Every agent reads it.
   - **Art direction:** when `docs/art/art-direction.md` covers every kind of asset the epic needs,
     the brief's art-direction section points to it, and no art director is spawned. Spawn one
     (template in templates.md) only for a kind the guide doesn't cover, such as a new character
     class or a new screen type, and put its decisions in the brief. The visual critic still judges
     the results (§4.6).
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
   - **One developer builds a whole package**: its feature and its tests. Never split a package into
     feature, tests and review agents; review is §4.4's job.
   - **Packages that are sequential or share state run one after another**, a fresh developer per
     package so each context stays small. The next one starts from the code and its card, not from
     the previous developer's history.
   - **Only independent packages run in parallel.** Spawn them in one message, in the background.
     Run at most two or three writers at once, on disjoint files; read-only agents (review, critic,
     research) can run beside them. Windowed game runs go one at a time, through the project's lock
     if it has one.
4. **Review as each piece lands**, not at the end. Start the adversarial review of a finished piece
   while others are still working; scope it to that piece; tell the reviewer what the feature must
   guarantee and ask for concrete failure scenarios, no style nits.
   - **Run it through the Codex runner** when recon found a route: write the review prompt
     (templates.md) to a file in the scratchpad, then run in the background `python
     <skill>/scripts/codex_review.py --repo <checkout> --prompt-file <prompt file> --out
     <scratchpad>/review-<n>.md`. Read only the verdict it prints and the tail of the out file; open
     more of the file only when a finding needs it.
   - **Exit 2 or 3** (no route, or the Codex run failed) means the fallback: spawn the
     `adversarial-reviewer` agent with the same prompt, telling it the runner's exit and message so
     it reviews the code itself. With no route at recon, use the agent from the first review.
   - **Two cycles at most, biased to one.** The first hunts for defects. Run a second only when the
     first found something blocking or the fixes touched shared code, and scope it to the fix diff:
     it checks that each finding was fixed, and doesn't hunt for new ones. Then you decide.
   - **A correctness bug found late is fixed with a failing test and recorded,** not reviewed a third
     time.
5. **Triage every finding,** and write each outcome where the owner can read it: fixed, declined
   with a reason, or deferred.
   - **Fix inline** when it's one file and you already understand it, with a test that fails first.
   - **Otherwise fix in a fresh agent** a tier below (§3), given only the finding,
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
     notes, and the issue references (`Closes` / `Ref`, see `issue-tracking`). Write it from the
     log yourself; when the log is long, you may have a cheap agent draft it, then check it.
   - Move features to `In Review`. **Don't merge** — the owner does (`team-lead-handsoff` is the
     variant that merges).
10. **Report** in two parts: the short chat report (template in templates.md) and the story page (§6).
    Write both yourself when the log is short; otherwise you may have a cheap agent draft them from
    the log, and you check them.
11. **Offer the next step**: playing it (`playtest`), then the next feature from the GDD with
    `feature-planning-handsoff` or `feature-planning`. Offer it **in the working style**: the `Working style` line in the project's `AGENTS.md`, or, before a project exists, the mode of the skill that just ran (`gdd-handsoff` means hands-off). Hands-off: offer the `-handsoff` variant first. Interactive: offer the interactive skill, and mention the hands-off variant once.

Between phases, keep the user posted in one or two sentences: who's doing what, and what you're
waiting for.

## 5. Keep your own context small

Every call re-reads your whole context, so its size, times the number of calls, is most of the run's
cost, and the main cause of hitting usage limits.

- **Start fresh at phase boundaries.** When this build follows other phases in the same session (the
  GDD, art direction, planning), their conversation is history the build doesn't need, and every call
  pays to re-read it. Before the build, and at a package boundary once your context has grown large,
  continue in a fresh context from the documents (the plan, the ledger, `BRIEF.md`, the build cards,
  `STATE.md`): hand the next phase to a new session where the client can start one, or ask the owner
  for a compaction when they're present. Automatic compaction alone comes late and loses detail.

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
