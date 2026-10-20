---
name: setup-godot
description: Turn a GDD into a Godot 4 repository that agents can work in safely — list every tool to install and ask once, guide the user through what only they can install, then create the project with its agent contract (AGENTS.md from the GDD's glossary), day-one ADRs, docs, GUT, shared Claude and Codex hooks and agents, CI on every pull request, and an itch.io release workflow. Use after the gdd (and optional prototype) step, or when the user asks to set up, bootstrap or scaffold a Godot project or repo.
argument-hint: "Optional: the folder for the new project"
---

# Set up a Godot project from a GDD

The result is a repository where an agent can start building on day one without inventing
conventions: the rules come from the GDD, the safeguards are on from the first commit, and CI already
tests every pull request.

Template: [project-template/](project-template/) (copied by
[scripts/instantiate.py](scripts/instantiate.py), which fills its `{{PLACEHOLDERS}}`).

## 1. Read the GDD and ask one round

Find the GDD (`docs/GDD.md` or `GDD.md`). From it take the title, pitch, glossary, platforms, input
devices, art style and resolution. Then ask **one round** — every question with a recommendation,
so "yes" accepts it:

1. **Where:** the folder (recommend a sibling of the current one, named after the game's slug) and
   the GitHub repository name, private by default.
2. **Godot version:** the latest stable 4.x that a current GUT release supports — check both release
   pages first and recommend that pair.
3. **Renderer:** Compatibility for 2D and web (recommended for pixel art and itch.io web builds),
   Forward+ for 3D desktop, Mobile otherwise.
4. **Display:** base resolution and stretch. For pixel art: a small base (e.g. 640×360), stretch
   mode `viewport`, integer scaling, nearest filtering.
5. **Input rule** for `AGENTS.md`: mouse and keyboard; or mouse, keyboard and gamepad (then:
   "everything clickable also takes focus and answers `ui_accept` through the same method its click
   calls").
6. **Clients:** Claude Code and Codex (recommended), or Claude only.
7. **First commit:** create `main` with the GDD as its only commit, then open the scaffold as the
   first pull request (recommended) — so `main` is never written by an agent after that.

If the folder already holds a Godot project, say so: setup **adds what's missing** and lists every
file it would replace instead of replacing it.

## 2. Check, list, then install after one yes

Check what's present: `git`, `gh`, `python` (3.10+), `node`/`npx`, `godot` (or `GODOT_BIN`),
`gdformat`/`gdlint`, `claude`, `codex`. Then show **one list**, each line with name, version, source
and size, split in two:

- **Agent installs** (after the user's single yes): the Godot editor zip from
  `github.com/godotengine/godot-builds` releases (into a tools folder the user names, then
  `GODOT_BIN`); gdtoolkit (`pip install "gdtoolkit==4.*"`); GUT from its GitHub release
  (`github.com/bitwes/Gut`) into `addons/gut/`; for pixel art, `pixelforge`
  (`pip install git+https://github.com/amramos/pixelforge`).
- **The user installs** (the agent can't or shouldn't): Git, GitHub CLI and `gh auth login`,
  Python, Node.js, Claude Code / Codex and their sign-ins. Link each and wait.

Download only from those official sources. Nothing is installed before the yes.

## 3. Create the project

1. Write a values file (in the scratchpad) for every placeholder — `GAME_TITLE`, `PITCH`,
   `GLOSSARY` (the GDD glossary as a markdown table), `PLATFORMS`, `INPUT_RULE`,
   `INPUT_RULE_DETAIL`, `GODOT_VERSION` (e.g. `4.5.1`), `GODOT_FEATURE` (e.g. `4.5`),
   `RENDERER_FEATURE` / `RENDERING_METHOD` (`GL Compatibility`/`gl_compatibility`,
   `Forward Plus`/`forward_plus`, `Mobile`/`mobile`), `DATE`, `NEXT_STEP`, `GUT_BASELINE`,
   `GUT_VERSION`. The script refuses to run while any is missing.
2. Run `python <skill>/scripts/instantiate.py --target <folder> --values <values.json>`.
3. Move the GDD to `docs/GDD.md`.
4. Add the display settings from §1 to `project.godot` (`[display]` window size and stretch;
   for pixel art also `textures/canvas_textures/default_texture_filter=0` under `[rendering]`).
5. Install GUT into `addons/gut/` (its plugin is already enabled in `project.godot`).
6. If Claude only: delete `.codex/` and the Codex parts of `docs/agent-tooling.md`.
7. Run `python3 .agents/scripts/sync_skills.py --write` once so the mirrors exist.
8. Codex: run the package's `scripts/install_codex.py` to copy the plugin skills into
   `~/.codex/skills/` (show the list and ask first; it touches the user's home folder).

## 4. Validate

All must pass before the first commit; report each with its real output:

```bash
godot --headless --import
godot --headless -s addons/gut/gut_cmdln.gd -gexit        # 1 test, from tests/unit/project_setup_test.gd
python3 -m unittest discover -s .agents/tests -v          # the hooks' own tests
python3 .agents/scripts/sync_skills.py --check
gdformat --check tests && gdlint tests
```

The very first import of a freshly copied GUT can log "invalid UID" and "failed loading resource"
errors for GUT's own fonts and icons; import a second time — that one must be clean. Then boot the
game once headless (`godot --headless --quit-after 60`) and check it logs no errors.

Write the real GUT count into `docs/current-status.md`.

## 5. Commit and publish (with the user's go-ahead)

1. `git init`, the GDD as the first commit on `main`, then a `setup/project-foundation` branch with
   everything else. Commit messages follow `docs/git-workflow.md`.
2. If the user agreed to a GitHub repository: `gh repo create <name> --private --source . --push`,
   then push the branch and open the pull request. Creating a repository is outward-facing: confirm
   the name and visibility right before doing it.

## 6. The owner's checklist

End with what only the owner can do, as a checklist:

- [ ] Open the project in Godot once; add export presets (Project → Export) for the platforms in the
      GDD; commit `export_presets.cfg` (see `docs/getting-started.md` §4).
- [ ] Protect `main` (pull requests only, require the CI `test` job); enable *Automatically delete
      head branches*.
- [ ] For releases: the itch.io pages, `BUTLER_API_KEY` secret and `ITCH_*` variables (the `release`
      skill has the details).
- [ ] In Claude Code, approve the `godot` MCP server and check `/hooks`.

## 7. Next

Offer: `art-direction` (set the style before any art), then `feature-planning` for the first feature
— usually the core loop from the GDD as a playable slice. Optionally `bug-intake`.
