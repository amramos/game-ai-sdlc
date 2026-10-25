# Changelog

What changed in each version of the `game-sdlc` and `game-sdlc-godot` plugins, newest first. Both
plugins are released together under one version.

## Unreleased (planned 0.5.0)

Game interfaces designed from the start, not defaulted to web-page layouts. Built and awaiting a test
on a held-out game before release.

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
