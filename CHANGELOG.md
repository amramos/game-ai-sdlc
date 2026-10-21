# Changelog

What changed in each version of the `game-sdlc` and `game-sdlc-godot` plugins, newest first. Both
plugins are released together under one version.

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
