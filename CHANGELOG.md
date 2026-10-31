# Changelog

What changed in each version of the `game-sdlc` and `game-sdlc-godot` plugins, newest first. Both
plugins are released together under one version.

## 0.7.0 — 2026-10-31

GDDs that hand off better: shorter, and more buildable. Blind reviewers who built from an SDLC GDD
found it long on history and short on the values and rules they needed, with gaps that read as
settled and sections that disagreed. A revision following these rules was ranked first by all six
blind reviewers, from four model vendors, and was 13% shorter.

- **gdd-core:** the GDD states the current design, with one sentence of why for any rule a builder
  might simplify away; how it got there stays in reports. Every value a rule needs is stated, marked
  *(tune)*, or marked `[OPEN]`. Win, loss, grades and named states mean the same in every section,
  and a summary or table never adds or drops a rule. Glossary entries are one line.
- **gdd-core:** the design tree asks:
  - how rules resolve when they meet;
  - how the player's means grow;
  - full content examples, and a generator contract for generated content;
  - feedback for each key moment, accessibility options, and a second cue besides colour;
  - what the music does during play;
  - writing rules for each voice;
  - how long the content plan takes.

  Each of these is skipped when the game has none.
- **gdd-core:** the template gains a Worked example section and a First playable section, decided
  and with a go/no-go line. Each mechanic gets a *Check:* line, kept as a test still to run.
- **gdd-core:** a **builder's read** runs before handover. One blind agent with only the GDD writes
  the data model, one pass through the core loop and the first playable's tasks, and logs every
  decision it had to invent. It is done when no blocker sits on the first playable's path and the
  worked example recomputes exactly. `gdd` asks the user about what it finds; `gdd-handsoff`'s panel
  settles it.
- **prototype:** the write-back copies the tuned values and the rules the code decided implicitly. It
  rewrites the affected sections whole, then sweeps the rest and redoes the worked example. History
  and evidence go in `prototype-report.md`, and the write-back ends with the builder's read.
- **docs-cleanup:** the GDD check also covers values neither stated nor marked, glossary collisions
  and sections that disagree.
- **setup-godot:** `prototype-report.md` moves into `docs/`. `AGENTS.md` now says the GDD beats an
  older ADR and that design changes go through `design-change`, and the GDD keeps only two lines on
  authority.

## 0.6.0 — 2026-10-30

Prototypes the owner can play, not only agents. Prototypes printed their text interface onto the
page as paragraphs of rules with a row of buttons; AI playtesters coped, and the owner clicked at
random without knowing the goal.

- **prototype:** each variation opens with a card for the owner (what it tests, what to ignore, how
  it differs), hidden from playtesters with `?blind`. A 3–5 step tutorial on a scripted deal replaces
  the rules text, one new term per step, teaching the goal and the verbs but never the best move;
  then a free round with no coach. A core that can't be taught in five steps is reported, not given
  a sixth step.
- **prototype:** the page draws the GDD's camera and medium at greybox quality (three.js only for a
  3D game), with state where it lives and input on the world, and is never `describe()` in a box.
  Feel stays out unless the question is about feel.
- **prototype:** the page itself is tested: a ten-second check on one screenshot, and a playtester
  on the real page. At least one playtester per variation plays cold, without the tutorial, and the
  comparison reads the two arms against each other. `window.proto` gains `restart({ tutorial })`,
  and the headless runner `--no-tutorial`.
- **gdd-handsoff:** the prototype bar counts the playtesters who had the tutorial; the cold one's
  misreadings go in the summary.

## 0.5.1 — 2026-10-25

The camera and the medium follow the owner's taste, not the toolchain. A test game whose references
were mostly first-person 3D came out as top-down pixel art, decided before art direction ran.

- **gdd-handsoff:** each concept states its camera and medium. When most of the games the owner loves
  share one, at least one concept uses it, and a departure is shown in the summary with its reason
  and the alternative's cost.
- **gdd-core:** camera and medium are their own early question, with options taken from the
  references; a scope argument states the actual cost instead of a rule of thumb. "Each mechanic
  earns its place" adds: never change the game to make it easier to check.
- **art-direction:** generators are listed by what each renders well, and the generator never
  chooses the medium. When most references share a medium the GDD didn't choose, one direction uses
  it. The critic no longer scores how easily a generator repeats a style: production cost is a
  separate, unscored line.
- **prototype:** when the camera is open, the same mechanic in two cameras is a fair pair, and a 3D
  variation stays one file with three.js from a CDN.
- **setup-godot:** renderer and display recommendations come from the GDD's medium, with 3D and
  painted examples beside the pixel-art one.

## 0.5.0 — 2026-10-25

Game interfaces designed from the start, not defaulted to web-page layouts; and agent teams that run
leaner and faster. Tested before release on a new game, from GDD to a playable slice.

**Leaner runs:**
- **Hands-off skills can be started by agents:** `feature-planning-handsoff` and `team-lead-handsoff`
  run when the owner chose them, including from an up-front question, instead of only from a typed
  command.
- **Models on purpose, never above the session's:** every agent's model is set explicitly, the
  session's model is the ceiling, and narrow work runs a tier down. Panels' "different model" means a
  cheaper one.
- **A small lead context:** agents report in about 200 words with paths to the detail, screenshots go
  to a critic agent, the lead writes `STATE.md` at each package boundary, and at a usage-limit
  warning it launches nothing new.
- **Build cards** quote each package's ledger rows, so agents don't each read the whole ledger and
  plan; **scene hooks** agreed up front replace the integrator stage; a shared scene has one owner
  who builds its placeholders first.
- **Fixes inline or in a fresh small agent,** never inside an agent resumed at a large context; the
  full test suite runs once per package, at the gate.
- **Capped loops:** code review at most two cycles, biased to one, the second only checking the
  fixes; the visual critic one scoring round plus one confirmation, with motion judged in play and
  layout or taste calls sent to the owner.
- **One pull request per owner checkpoint,** one commit per feature; a PR may close several features.
- **A lighter log,** with PR bodies and reports drafted by a cheap agent; and lessons for the lead
  (background waits, Glob and Grep instead of recursive listings, Windows heredocs, Codex prompts on
  stdin).

**From the held-out test** (a new game, GDD to playable slice in 2.9 hours, no usage-limit stops):
- **A fresh lead context at each phase boundary:** each phase hands the next a short brief pointing
  at its documents, in a new session where the client allows it, since one session running every
  phase let the lead's context grow from 78k to 630k tokens.
- **The reviewer is checked before the first review,** and a Codex path that works is passed to every
  review; the reviewer agent tries other installed Codex CLIs and never falls back silently.
- **Each mechanic earns its place:** a gate in the GDD, planning and prototype skills, checked by a
  solver, a simulation with a bot, or blind playtesters, whichever the genre allows.
- **prototype** ships a headless runner (`scripts/proto_cli.mjs`) for playtesters and solvers without
  a browser; the template's `export_all.py` uses the Godot the hooks use.
- Agents can start `gdd-handsoff` and `feature-planning`; the pillar wording agrees between
  `gdd-core` and `gdd-handsoff`; words on a gameplay asset are proved as live text in the engine;
  first-feature sketches draw over the style frames or the prototype.

**Designed interfaces:**

- **New skill, `game-ui`:** ten commandments for game interfaces, each with a check, plus a screen
  spec template and a review procedure (`/game-sdlc:game-ui` on a screen or capture). Agents load it
  for anything the player sees. The research behind it is in `research/game-ui/`.
- **Pillars replace the governing rule** everywhere. `gdd` and `gdd-handsoff` suggest six to eight
  candidates and the owner picks three; they're written plainly, for the whole game, with no interface
  rules and no plot. `feature-planning` settles them first when a GDD has none and tests every answer
  against them; `prototype` and the art critic judge against them.
- **The GDD gains an interface section:** density, where words live, how much reading and in whose
  voice, what the player is never told, the loudest moment, the smallest readable size, and how the
  comparables present information.
- **art-direction:** the text-heavy screen becomes a style frame (from worst-case content), the
  chosen direction adds the hardest-to-read gameplay asset and the loudest moment, and
  `art-direction.md` gains an interface section (materials, type roles with licences, colour jobs,
  minimum size, motion). Assets must be rebuildable from the repository.
- **comfyui-art:** batch checks for generator habits, pixel-art transform and signal-colour rules,
  and a critic that asks what an asset reads as before whether it's pretty.
- **feature-planning:** a screen spec for every new or changed screen, "how the player sees it" for
  every mechanic, a fix-a-screen method for layout decisions, and visual acceptance that is never an
  open-ended pass bar.
- **playtest:** blind playtesters report what they skipped reading, what they understood without
  reading and which words they didn't know; the panel report says which pillars were felt.
- **setup-godot:** new projects get their pillars in `AGENTS.md`, a capture script (1:1, ×3,
  greyscale, blurred), a lock for windowed runs, theme type roles with a guard test, and a text-fit
  helper.

## 0.3.1 — 2026-10-23

- **setup-godot and bug-intake:** the workflow templates use current GitHub Actions versions
  (`actions/checkout` v7, `actions/setup-python` v7, `actions/cache` v6). New projects no longer start
  behind.
- **setup-godot:** new projects get a `dependabot.yml` that keeps their workflows' action versions
  current, including the `setup-engine` composite action.

Projects created with an earlier version keep their old workflow files; copy the new ones in, or bump
the versions by hand, to catch up.

## 0.3.0 — 2026-10-21

Hands-off builds no longer stop for setup questions.

- **setup-godot:** asks once whether agents may merge reviewed pull requests into `main`
  (recommended in hands-off projects) and, if so, records it on day one: ADR-0006,
  `.agents/merge-policy.json`, and a line in `AGENTS.md`.
- **team-lead-handsoff:** adopts agent merges itself (ADR, policy file, its own pull request merged
  first) when a project hasn't yet; your invoking it is the decision. Branch protection is used where
  the GitHub plan allows it; otherwise the merge guard covers it. The reviewer's verdict is a PR
  comment by default; a bot account is optional.
- **New merge guard** in the project's hooks (`merge_guard.py`, called by `guard_bash.py`): an
  agent's `gh pr merge` into `main` is refused unless the merge policy allows it, every CI check
  passed, and the latest verdict approves the pull request's current head commit. `--admin` is
  always refused.
- **adversarial-reviewer** ends every review with `VERDICT: approve` or `VERDICT: request-changes`.
- **Fix:** the hooks now decode command output as UTF-8. On Windows, output containing any non-ASCII
  character (a PR comment, a file name) used to fail to decode.

## 0.2.2 — 2026-10-21

- **art-direction:** directions must differ in medium or rendering, never only in colour. When the
  GDD's style was only assumed (as `gdd-handsoff` does), one direction keeps it and the others use
  different media (pixel art, vector, low-poly 3D, painterly, ink), each with why it fits and what it
  costs to produce. When you chose the style, directions stay in it and differ in rendering.
- **art-direction:** if a different medium wins, the same run amends the GDD's art section, updates
  the project's display settings and palette tooling, and validates.
- The marketplace entries no longer repeat each plugin's version; it lives in `plugin.json` only.
- README: how to turn on auto-update, how to update by hand, and how to hear about new versions.

## 0.2.1 — 2026-10-21

- **art-direction:** a hands-off mode. In a hands-off project a critic agent picks the direction, the
  pick is recorded as *assumed*, and the run ends by showing it beside the runners-up so you can
  swap with one word.

## 0.2.0 — 2026-10-21

- **setup-godot:** one round of questions with a "use every recommendation" fast path, and one
  approval that covers installs, export templates, a verified export, merging the scaffold and
  creating the private GitHub repository. No more end-of-setup chore list.
- **setup-godot:** the project's hooks find Python (skipping the Windows Store stub), gdtoolkit and
  Godot on their own: no `PATH` edits, no restart.
- **setup-godot:** export presets ship in the template (Windows, Linux, Web without threads).
- **setup-godot:** records the owner's working style in `AGENTS.md`; later skills offer their next
  step in that style.
- **release:** sets up the itch.io pages, butler key and variables on the first release instead of
  during setup.

## 0.1.0 — 2026-10-21

- First release: the `game-sdlc` process plugin (GDD interview with `gdd` and `gdd-handsoff`,
  prototypes, art direction, feature planning, tracking, agent teams, playtests, releases, bug intake,
  design changes, docs cleanup) and the `game-sdlc-godot` engine pack (`setup-godot` and seven Godot
  workflow skills).
