---
name: setup-godot
description: Turn a GDD into a Godot 4 repository that agents can work in safely, with as little for the user to do as possible — one round of questions (or "use every recommendation"), one approval, and then it installs the tools, creates the project with its agent contract, day-one ADRs, docs, GUT, shared Claude and Codex hooks and agents, CI and an itch.io release workflow, proves the export presets with a real export, merges the scaffold and creates the GitHub repository. Use after gdd or gdd-handsoff (and the optional prototype), or when the user asks to set up, bootstrap or scaffold a Godot project or repo.
argument-hint: "Optional: the folder for the new project"
---

# Set up a Godot project from a GDD

The result is a repository where an agent can start building on day one without inventing
conventions: the rules come from the GDD, the safeguards are on from the first commit, CI tests every
pull request, and the export presets are already proven.

**The rule for this skill: do it, defer it, or hand over a one-liner — never a chore list.** Every
step the agent can take, it takes after the single approval. Steps that belong to a later skill
(itch.io pages and keys belong to `release`) are not mentioned here. What is left for the user at
the end should fit in one sentence.

Template: [project-template/](project-template/), copied by
[scripts/instantiate.py](scripts/instantiate.py), which fills its `{{PLACEHOLDERS}}`.

## 1. One round — or none

Find the GDD (`docs/GDD.md` or `GDD.md`) and take from it the title, pitch, pillars, glossary,
platforms, input devices, art style and resolution. Check the machine (§2's list) while preparing the
round, so the recommendations already fit it.

Then ask **one round**, every question with a recommendation, and offer **"Use every
recommendation"** as the first answer. Recommend that fast path when the GDD is marked
*Provisional* (it came from `gdd-handsoff`) or the user has said they want to be hands-off.

1. **Where:** the folder (a sibling of the current one, named after the game's slug) and the GitHub
   repository name, private.
2. **Godot version:** the latest stable 4.x that a current GUT release supports; check both release
   pages and recommend that pair (prefer a Godot already installed on the machine if it qualifies).
3. **Renderer**, from the GDD's camera, medium and platforms: Compatibility for any game with a web
   build, 2D or 3D (recommended for itch.io); Forward+ for desktop-only 3D that needs its lighting;
   Mobile otherwise.
4. **Display:** base resolution and stretch, from the GDD's medium:
   - pixel art: a small base (e.g. 640×360), stretch mode `viewport`, integer scaling, nearest
     filtering;
   - painted, vector or 3D: a 1920×1080 base (1280×720 for a jam), stretch mode `canvas_items`,
     aspect `expand`, linear filtering.
5. **Input rule** for `AGENTS.md`: mouse and keyboard; or mouse, keyboard and gamepad (then:
   "everything clickable also takes focus and answers `ui_accept` through the same method its click
   calls").
6. **Clients:** Claude Code and Codex (recommended), or Claude only.
7. **Working style:** hands-off (recommended when the GDD came from `gdd-handsoff`) or interactive.
   It's written into `AGENTS.md`, and every later skill offers its next step in that style.
8. **Agent merges:** may agents merge reviewed pull requests into `main` on their own
   (`team-lead-handsoff`)? Recommend **yes** with a hands-off working style, **no** otherwise. A yes
   is recorded on day one as ADR-0006, so a hands-off build never stops to ask; agents still never
   commit or push to `main` directly.

If the folder already holds a Godot project, say so: setup **adds what's missing** and lists every
file it would replace instead of replacing it.

## 2. One approval

Show **one list** and ask once. It has two parts.

**What I'll do** (each line with source and size where something is downloaded):
- install what's missing: the Godot editor from `github.com/godotengine/godot-builds` releases into
  a tools folder; gdtoolkit (`pip install "gdtoolkit==4.*"`); GUT from its GitHub release
  (`github.com/bitwes/Gut`) into `addons/gut/`; for pixel art, `pixelforge`
  (`pip install git+https://github.com/amramos/pixelforge`);
- download the **export templates** for that Godot version (read the exact size from the release:
  `gh release view <version>-stable -R godotengine/godot-builds --json assets`; about 1.2 GB for 4.7)
  and install them where Godot looks (`%APPDATA%\Godot\export_templates\<version>.stable\` on
  Windows, `~/.local/share/godot/export_templates/…` on Linux,
  `~/Library/Application Support/Godot/export_templates/…` on macOS);
- create the project, validate it, and **prove the export presets with a real export** (§4);
- if agent merges were chosen: record them (ADR-0006 and `.agents/merge-policy.json`, §3);
- if every check passes: **merge the scaffold into `main`**, **create the private GitHub repository**
  and push, turn on *automatically delete head branches*, and protect `main` (require pull requests
  and the CI `test` job) — when the account's plan allows it;
- for Codex: copy the plugin skills into `~/.codex/skills/` with the package's `scripts/install_codex.py`.

**Only you** — whatever the agent can't do on this machine, usually just: install Git or Python if
either is missing, and `gh auth login` if GitHub CLI isn't signed in. Give the exact command or link.

The user can answer "yes", or "yes except 3". Nothing is downloaded or created before that answer.
Download only from the sources named above. Never change system settings or the user's `PATH`: the
project's hooks find Python, gdtoolkit and Godot by themselves (§3).

## 3. Create the project

Start the history first, so nothing else is ever written on `main`: `git init -b main` in the
folder, commit the GDD alone (`docs: add the GDD`), then `git checkout -b setup/project-foundation`.

1. Write a values file (in the scratchpad) for every placeholder: `GAME_TITLE`, `PROJECT_SLUG`,
   `PITCH`, `PILLARS` (the GDD's three pillars copied word for word, each its name, line and test
   question, as the GDD's numbered list; for a GDD without pillars: "None yet: the first
   `feature-planning` round settles them in the GDD, then they're copied here."), `GLOSSARY` (the
   GDD glossary as a markdown table), `PLATFORMS`, `INPUT_RULE`,
   `INPUT_RULE_DETAIL`, `WORKING_STYLE` (one of the two texts below), `GODOT_VERSION` (e.g. `4.7.1`),
   `GODOT_FEATURE` (e.g. `4.7`), `RENDERER_FEATURE` / `RENDERING_METHOD` (`GL Compatibility` /
   `gl_compatibility`, `Forward Plus` / `forward_plus`, `Mobile` / `mobile`), `DATE`, `NEXT_STEP`,
   `GUT_BASELINE`, `GUT_VERSION`. The script refuses to run while any is missing.
   - Hands-off: "The owner works **hands-off**. When a skill has a `-handsoff` variant
     (`feature-planning-handsoff`, `team-lead-handsoff`), offer it first, and ask only what the owner
     alone can decide."
   - Interactive: "The owner works **interactively**. Offer the interactive skill first and mention
     the `-handsoff` variant once."

   `AGENT_MERGES_RULE`, from §1's question 8:
   - Yes: "Agents may merge a reviewed pull request into `main` only through `team-lead-handsoff`'s
     merge checklist (ADR-0006). The merge guard (`.agents/hooks/merge_guard.py`) refuses any other
     agent merge."
   - No: "Only the owner merges into `main`. The merge guard (`.agents/hooks/merge_guard.py`)
     refuses an agent's `gh pr merge` into `main`."
2. Run `python <skill>/scripts/instantiate.py --target <folder> --values <values.json>`.
3. Move the GDD to `docs/GDD.md`, and `prototype-report.md`, if there is one, to `docs/`.
4. Add the display settings from §1 to `project.godot` (`[display]` window size and stretch; for pixel
   art also `textures/canvas_textures/default_texture_filter=0` under `[rendering]`).
5. `export_presets.cfg` comes with Windows Desktop, Linux and Web presets (Web with thread support
   off, which itch.io needs). Delete the presets for platforms the GDD doesn't ship; a macOS preset
   needs signing options, so it's added later in the editor if wanted.
6. Install GUT into `addons/gut/` (its plugin is already enabled in `project.godot`).
7. **Tell the hooks where Godot is**: write its full path, with forward slashes, to
   `.agents/local/godot` (git-ignored). The hooks read it, so no environment variable and no restart
   are needed. They find Python on their own (`.agents/hooks/run.sh` skips the Windows Store stub and
   caches the interpreter in `.agents/local/python`), and run gdtoolkit through `python -m` when its
   commands aren't on `PATH`.
8. **If agent merges were chosen**: fill [agent-merges/agent-merges-adr-template.md](agent-merges/agent-merges-adr-template.md)
   into `docs/adr/0006-agents-merge-reviewed-prs.md` (`NUMBER` 0006, `DATE`, and `CONTEXT`: "Chosen
   at setup, with the owner working hands-off."), copy
   [agent-merges/merge-policy.json](agent-merges/merge-policy.json) to `.agents/merge-policy.json`
   (`ADR_FILE`: that file name), and add the ADR's row to `docs/adr/README.md`.
9. If Claude only: delete `.codex/` and the Codex parts of `docs/agent-tooling.md`.
10. Run `python .agents/scripts/sync_skills.py --write` once so the Codex mirrors exist.

## 4. Validate, including a real export

All must pass before anything is committed; report each with its real output. Use whichever
Python works on this machine (`python`, `python3` or `py -3`); once a hook has run,
`.agents/local/python` names the one it found.

```bash
godot --headless --import            # twice on the first run, see below
godot --headless -s addons/gut/gut_cmdln.gd -gexit        # 6 tests in 3 scripts (setup, type roles, text fit)
python -m unittest discover -s .agents/tests -v           # the hooks' own tests
python .agents/scripts/sync_skills.py --check
godot --headless --quit-after 60                          # the game boots without errors
python tools/windowed_run.py godot --path . -s res://tools/capture/capture.gd -- --scene=res://scenes/main.tscn
```

The very first import of a freshly copied GUT can log "invalid UID" and "failed loading resource"
for GUT's own fonts and icons; import a second time — that one must be clean.

The last line opens a window briefly, through the window lock, and writes four PNGs to `captures/`
(git-ignored). Look at `captures/main.png`: the title, centred, at the native resolution from §3's
display settings, and `main_x3.png`, `main_grey.png` and `main_blur.png` beside it. A machine with
no display can't capture; say so and move on.

Then **export every preset** (`python tools/ci/export_all.py --out build`) and boot the build for
this machine headless (`build/windows/<slug>.exe --headless --quit-after 60`, or
`bash tools/ci/export_smoke_test.sh build/linux`): no errors, exit code 0. A preset whose templates
aren't installed fails with "No export template found"; that's an installation gap, not a preset
problem — say which. Delete `build/` afterwards. Write the real GUT count into `docs/current-status.md`.

## 5. Finish — what the approval covered

1. Commit everything on `setup/project-foundation` (the GDD is already on `main`, §3).
2. **Merge** it: `git merge --ff-only setup/project-foundation` from `main` (it fast-forwards, since
   `main` is the branch's parent), then delete the branch.
3. **GitHub**: `gh repo create <name> --private --source . --push`, then
   `gh repo edit --delete-branch-on-merge`. Protect `main` with
   `gh api -X PUT repos/<owner>/<repo>/branches/main/protection` (required status check `test`, pull
   requests required with zero approvals, admins not enforced). GitHub allows branch protection on
   private repositories only on paid plans: if the call is refused for that reason, say in one line
   that the project's merge guard covers agents' merges instead, and move on.
4. **Codex**: run `scripts/install_codex.py` from the package if the user kept that line.

Skip any line the user excluded, and say which were skipped.

## 6. What's left for the user

At most one sentence, for example: "Open the project in Claude Code once: approve the `godot` MCP
server, and `/hooks` should list four hooks." Nothing about itch.io — the `release` skill sets that
up on the first release.

## 7. Next

Offer the next step **in the working style** from §1:

- `art-direction` first if the game will need art;
- then the first feature — usually the core loop from the GDD as a playable slice — with
  **`feature-planning-handsoff`** (hands-off) or **`feature-planning`** (interactive);
- optionally `bug-intake`.

Start the next phase fresh: it needs only the repository and its documents. Where the client can
start a new session in the project, hand it over there with a short brief, or ask the owner for a
compaction when they're present, rather than carrying this setup's conversation into every later
call.
