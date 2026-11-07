# Changelog

What changed in each version of the `game-sdlc` and `game-sdlc-godot` plugins, newest first. Both
plugins are released together under one version.

## 0.13.0 — 2026-11-07

Start from a tested look. Art direction used to invent every game's look from scratch, and image
generation assumed a graphics card with about 11 GB of video memory. Now a game can pick one of ten
ready-made looks, each with a web demo and a Godot port rendered to match, and ComfyUI picks a model
that fits the user's card.

- **style-catalog (new):** ten looks across pixel art, low-poly and cel-shaded 3D, ink, paper and
  neon vector. Each has a style sheet, a recipe, framings, an example palette, and engine files for
  web and Godot. `art-direction` matches the GDD against the catalog before building a look. With
  the owner present it asks one question: a recommendation, two more looks, "create a new look" or
  something else, with previews and a link to the catalog site. Hands-off, the critic picks from the
  shortlist. The chosen entry is copied into the game's style guide and made the game's own
  (palette, fonts, setting, cast). A new look is built from scratch only when nothing fits.
- **Catalog site:** the whole entries (gallery, frames, demos with their example art and models, and
  each Godot port's full project) live at the catalog's GitHub Pages site. The plugin ships only the
  text and a 640 px WebP preview per look, 740 KB in all. Reference frames are downloaded once, when
  a look is picked.
- **Checks:** `check_entries.py` checks entries, frames and demo safety, and that each Godot port was
  matched against the current web frame. A web demo changed after its Godot render fails the check.
  `--plugin` checks the shipped text and previews against a 1.5 MB budget. `export_plugin.py` writes
  the plugin's catalog from the site's.
- **comfyui-art:** model profiles by video memory: `zimage-bf16` (16 GB+), `zimage-int8` (12 GB+, the
  default and the only one tested), `zimage-gguf` (6–11 GB) and `sdxl-fast` (4 GB+). `comfy.py
  hardware` lists the profiles that fit the user's cards and RAM, with the files each still needs. A
  project records its profile in its style guide and never switches by itself, since another model
  draws another look. Released profiles never change; a better one is added beside them.
- **game-ui:** a list of banned looks, starting with dark boxes, panels and buttons with yellow or
  gold borders or text. Only the user can lift a ban by asking for that look in their own words.
  Hands-off agents never propose or pick one. `art-direction` regenerates frames that show one, and
  its style-guide template carries the ban.

**Existing projects:** nothing to change. A game with a style guide keeps its look; the catalog is
offered only when there's no style guide yet. A style guide without a ComfyUI profile is offered one
the next time art is made with the owner there. Codex users re-run `python scripts/install_codex.py`
to get the new skill and scripts.

## 0.12.0 — 2026-11-04

Design each moment of the loop, not one screen for all of them. In a planning run, the sketches of a
game's main view started out strong, then drifted round by round into one composite screen. Every
mechanic got its own always-visible panel, scores were shown as spelled-out formulas, nothing
committed a selection, and two colour codes shared one set of colours. `game-ui` already said to
build each screen from the moment, but nothing made the agent list a view's moments or say when each
element is shown.

- **game-ui:** a view that serves several moments of the loop is designed per moment: each element
  is shown only in the moments that need it, and the sketch shows each moment that looks different.
  Things the player can act on look actionable, and a selection shows the control that commits it.
  Results are shown, and the working plays out as motion; a formula is spelled out only when the
  player plans with its parts. A number sits on what it measures, and recurring kinds get an icon
  before a word. A new check catches two colour codes on one screen that reuse colours for
  different meanings.
- **Screen-spec template:** the activity's moments, a **Shown in** column for each element ("all"
  only when every moment needs it; what the player looks up is opened on request), and an
  **Actions** row.
- **feature-planning-core:** the spec list follows the template, and a sketch says where it
  simplifies the approved art.

**Existing projects:** nothing to change. Screen specs written before this keep working; add the new
fields when a screen is next changed.

## 0.11.0 — 2026-11-04

Use the image generators that are already there. Art direction used to pick generators in a fixed
order, local ComfyUI first, without checking what the agent running it could already do, and offered
a ComfyUI install without saying what ComfyUI is. An agent with a built-in image tool, or a user with
an image service already connected, was pointed at a local install anyway.

- **art-direction:** before choosing a generator, the agent reads its own tool list for image tools
  (built-in, like Codex's, or from an MCP server) and runs the new `scripts/image_sources.py`, which
  reports ComfyUI's state and missing model files, image CLIs on PATH and image-service API keys by
  name, without installing or starting anything. It says what it found, uses what's set up (free or
  already-paid sources first, paid ones with a budget), and offers installs only when nothing fits,
  each explained in plain words with what it costs. Hands-off runs never install. The chosen
  generator goes into the style guide, and later assets keep it. Inside Codex, the skill no longer
  tells Codex to call the Codex CLI.
- **comfyui-art:** triggers when ComfyUI is the chosen generator, not on every art request. Its setup
  section says what ComfyUI is before asking anyone to install it; when the user declines, it goes
  back to the sources art direction found.
- **team-lead:** 2D art uses the style guide's generator and never installs one mid-build.
- **Style-guide template, taste-profile, README:** no longer name a fixed list of generators.

**Existing projects:** nothing to change. A style guide written before this keeps its generator.
Codex users re-run `python scripts/install_codex.py` to get the new script.

## 0.10.0 — 2026-11-04

Hands-off rules that hold on smaller models. An adherence test ran both hands-off planning skills
on three model tiers and found two kinds of miss: rules that were unclear, contradictory or silent,
which every model tripped on, and clear rules buried in trailing clauses, which smaller models
skipped. The first kind got clearer text; the second, where a script can check the result, got a
script.

- **feature-planning-core, feature-planning-handsoff, gdd-core, gdd-handsoff:** 18 unclear or silent
  rules fixed, among them what an invented decision becomes, saving rulings before stopping at the
  plan, the housekeeping baseline when the GDD has none, a stopping rule for the builder's read, and
  worked examples with exact values. Rules buried in clauses became their own bullets or steps. The
  ledger has a Dissent column; the runner-up is always the answer not taken.
- **codex_review.py:** `--round plan|gdd` adds the round reviewer's reply format (the GDD one with
  the kill list), splits the reply at the owner-only explanation line and retries once. Exit 4 means
  there was no usable reply. The session only ever opens the answers: the raw reply waits in a
  separate file until it's split, and a failed or timed-out round never prints it. `--print-format`
  and `--split` give a Claude reviewer, or any taste-profile judge, the same handling.
- **check_gdd.py:** also checks for missing or empty sections, unfilled template placeholders,
  mechanics without a `*Check:*` line, and `[OPEN]` items that don't point at an open question.
  `--handsoff` checks the Provisional line, an appendix that lists only assumed decisions (numbered
  A1, A2…) with runner-ups, the identity decisions, and pillars without profile additions.
  `--summary` checks `GDD-summary.md`. The labels it reads stay in English in a GDD of any language.
- **check_ledger.py:** a hands-off ledger's labels, Dissent cells, assumed list and runner-ups, and
  its open questions.
- **Shorter where scripts took over:** `feature-planning-handsoff` lost the reply format and the
  steps for reading it. `gdd-handsoff` carries its own reviewer steps, so a GDD run no longer loads
  `feature-planning-handsoff`.
- **taste-profile:** split into a short `SKILL.md` (the command that reads the profile, who sees
  what, the offer) and `references/interview.md` and `references/updates.md`, which only the
  interview and updates read. Every skill that uses the profile says, where it first needs it, to
  run the command rather than open `taste.md`. A judge on a session below mid-size, with no other
  vendor's model, uses the same model and says so.
- **gdd-handsoff:** the camera count lists viewpoints only, the default engine is Godot, the price
  model is always researched, and picking a concept settles its pitch, hook, pillars, camera and
  medium.

## 0.9.0 — 2026-11-03

Fewer agents where they didn't see anything different, and rules that hold on any model. An audit
of every place the plugins spawn agents (`research/agent-usage/`) kept the ones that see something
different (blind playtesters, the builder's read, another vendor's reviewer, research) and trimmed
the ones that only played a role on the same model.

- **feature-planning-handsoff, gdd-handsoff:** one outside reviewer per round replaces the panels
  (designer, player advocate, skeptic, and the market analyst for the GDD). The lead answers. The
  reviewer is another vendor's model when one is available, and it carries the skeptic's brief, the
  player advocate's questions and the taste-profile judge. Every assumed decision now has a runner-up,
  the reviewer's answer where they disagreed, and a taste-profile Signature opening goes among the
  reviewer's answers so the lead can't miss it. Market questions go to research agents. Tested before
  and after on two invented games and two model tiers: no Claude panelists, every assumption with a
  runner-up, and it caught an owner-only reversal the panel missed.
- **feature-planning-core, gdd-core, taste-profile:** the interactive taste-profile judge runs only on
  rounds with a question that's the owner's by nature. The separate concept drafter runs only when the
  session has read more than the Never lines. `check_gdd.py` and `check_ledger.py` check GDD markers
  and ledger ↔ plan decision ids before the builder's read and the two-way review, which keep the
  meaning half.
- **team-lead, team-lead-handsoff:** the art director runs only for asset types the style guide
  doesn't cover. Coupled packages go to developers one after another, never split into feature, test
  and review agents. Report and PR drafters are optional. Every role has a capability floor, the
  report names the model that filled it, and a hands-off run with no reviewer at or above the floor
  leaves its PRs for the owner instead of merging.
- **adversarial-reviewer, team-lead:** `codex_review.py` finds a working Codex route, runs the review
  read-only and prints the verdict. It exits non-zero instead of falling back silently.
- **Model tiers:** "a tier below" means the same model when there's none below. "Never above the
  session's model" still holds for Claude subagents, but roles with a floor (reviewers, critics) may
  use another vendor's stronger model.
- **prototype, playtest:** the ten-second check is part of the cold playtester, and real-window play
  covers the leading variation only. Hands-off retries re-test only the revised variation.
  `blind_setup.py` builds the playtester's folder and refuses one with project instructions in or
  above it.
- **art-direction, comfyui-art:** the separate seed critic runs only when a stronger or
  other-vendor model is there to judge; otherwise seeds are picked by the critic brief as a strict
  rubric.

## 0.8.1 — 2026-11-03

The hands-off skills load in GitHub Copilot, and reading the taste profile costs no extra agent.

- **taste-profile:** the session gets the profile's Never lines from one command (bash or
  PowerShell) that prints only that section, instead of spawning a reader agent. It's cheaper, and
  the rest of the file never enters the session's context.
- **gdd-handsoff, feature-planning, feature-planning-handsoff, team-lead-handsoff:** their
  descriptions had an unquoted `: `, which is invalid YAML. Claude Code reads it anyway; Copilot CLI
  parses frontmatter strictly and dropped all four skills without a word. They're reworded.
- **check_package.py:** flags an unquoted `: ` or ` #` in skill and agent frontmatter, so this can't
  come back.
- **README:** installing with GitHub Copilot CLI, and what it doesn't run (the project hooks, the
  merge guard included).

## 0.8.0 — 2026-11-03

Your taste, carried between games, and the housekeeping every shipped game needs, decided by scope.

- **taste-profile (new):** a 15–25 minute interview writes one short file in your home folder
  (`~/.game-sdlc/taste.md`, or the folder in `GAME_SDLC_TASTE`) that every project reads. The
  interview covers games and other media you love, moments that got you, your own game ideas and
  your dealbreakers, then you correct a playback. The file has four sections: values, signature,
  never and leanings. It holds reasons, not genres or content. Agents that draft options see only
  your hard limits; only agents that judge finished options read all of it, and committed files
  never quote it. A decision it settled is recorded as `panel — assumed (profile)`. It changes only
  when you answer *add* to a proposal, and proposals from runs you weren't there for wait in
  `proposals.md` until you're back.
- **gdd, gdd-handsoff, feature-planning, feature-planning-handsoff, art-direction:** offer the taste
  profile once when you have none (*set it up now*, *not now*, *don't ask again*), and use it under
  those rules when you do. `gdd-handsoff` drafts its three concepts with a separate agent. `docs-cleanup`
  asks about rulings from an epic that look like taste.
- **gdd-core:** a housekeeping baseline: save and continue, no silent progress loss, a main menu,
  persistent settings, control rebinding, pause, and skipping dialogue and cutscenes. The GDD's scope
  decides how strict it is: offered for jams and prototypes, recommended for small releases, built
  for commercial projects. The GDD template gains *Scope* and *Housekeeping baseline* lines;
  `issue-tracking` and `setup-godot` turn the line into an epic, `feature-planning-core` treats an
  item as a requirement, and `game-ui` checks prompts after rebinding, text at every size, and
  skippable text and cutscenes.
- **adversarial-reviewer:** finds Codex on a real install. The companion lookup searched one folder
  too shallow and every review silently fell back to the agent's own model. It now searches the
  plugin cache at any depth, then the marketplace copy, then tries a `codex` on PATH before
  reviewing by itself.

Existing projects: their GDDs don't have the new lines, since project files don't auto-update. Add
*Scope* and *Housekeeping baseline* by hand to get the baseline epic.

## 0.7.1 — 2026-11-01

Hands-off builds no longer stop at the review cap. The lead decides after two cycles, as `team-lead`
always said.

- **team-lead-handsoff:** the two-cycle review cap ends the review, not the run. A hands-off run
  stopped a whole epic on its foundation package: the reviewer still requested changes after the
  second cycle, the skill said to stop, and the merge guard accepted only the reviewer's approval.
  Now the lead rules on each finding still held (fix with a failing test, decline with a reason, or
  defer to an issue), posts the ruling with `<!-- game-sdlc-lead-ruling: merge sha=… -->` and
  merges. A PR stops only for a finding that risks the player's data, security or the repository's
  own rules. The report lists every ruling merge with what it declined or deferred.
- **setup-godot:** the merge guard accepts a lead ruling on the head commit once the pull request
  has two reviewer verdicts, and never accepts a reviewer `merge` or a lead `approve`. A project set
  up earlier gets the new guard from `team-lead-handsoff`'s setup step, since project files don't
  auto-update.

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
- **setup-godot:** new projects turn on auto-update for this marketplace. Their `.claude/settings.json`
  registers `game-ai-sdlc` with `"autoUpdate": true`, which applies once the folder is trusted.
  Claude Code auto-updates only Anthropic's own marketplaces by default, and a marketplace can't
  change that itself.

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
