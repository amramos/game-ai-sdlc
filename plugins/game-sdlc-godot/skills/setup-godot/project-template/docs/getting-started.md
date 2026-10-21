# Getting started

Setting up a machine to work on {{GAME_TITLE}}. Day-to-day rules live in `AGENTS.md`; what's true
right now is `docs/current-status.md`. The machine that ran `setup-godot` is already set up; this
page is for the next one.

## 1. Prerequisites

| Tool | For | Get it |
|---|---|---|
| **Godot {{GODOT_VERSION}}** (standard, not .NET) and its export templates | Running, editing and exporting the game | [godotengine.org/download](https://godotengine.org/download) |
| **Git** and **GitHub CLI** (`gh`, signed in) | Version control, pull requests | [git-scm.com](https://git-scm.com/), [cli.github.com](https://cli.github.com/) |
| **Python 3.9+** | The agent hooks, skill mirroring, gdtoolkit | [python.org](https://python.org/) |
| **gdtoolkit** | Lint and format | `pip install "gdtoolkit==4.*"` |
| **Node.js** | `npx`, which runs the Godot MCP | [nodejs.org](https://nodejs.org/) |
| **Claude Code** and/or **Codex** | The agents | [claude.com/claude-code](https://claude.com/claude-code) |

Nothing needs to go on `PATH` by hand:

- the hooks find a working Python themselves, skipping the Windows Store stub, and cache it in
  `.agents/local/python`;
- they run gdtoolkit through `python -m gdtoolkit…` when `gdformat`/`gdlint` aren't on `PATH`;
- they find Godot through `GODOT_BIN`, then `.agents/local/godot`, then `godot` on `PATH`. On a new
  machine, write the Godot executable's full path (forward slashes) into `.agents/local/godot`.

`.agents/local/` is git-ignored: it describes this machine only.

## 2. Open the project once

Import `project.godot` in Godot (or run `godot --headless --import` twice). This builds `.godot/`,
the editor cache, which is never committed.

`export_presets.cfg` is committed and already exports Windows, Linux and Web; signing secrets, if you
ever add any, live in `.godot/export_credentials.cfg`, which is ignored. To export locally you need
the export templates for {{GODOT_VERSION}} (Editor → Manage Export Templates).

## 3. Agents

- **Claude Code:** install the plugins (`/plugin marketplace add amramos/game-ai-sdlc`, then
  `/plugin install game-sdlc@game-ai-sdlc` and `game-sdlc-godot@game-ai-sdlc`). Open the project,
  approve the `godot` MCP server when asked, and check `/hooks` lists four hooks.
- **Codex:** run the package's `scripts/install_codex.py` once to copy the skills into
  `~/.codex/skills/`. Codex reads `AGENTS.md` and `.codex/` from the project.

## 4. Releases

Nothing to do until the first release: the `release` skill sets up the itch.io pages, the butler key
and the repository variables when you first need them.

## 5. Check

- [ ] `godot --headless -s addons/gut/gut_cmdln.gd -gexit` passes.
- [ ] `python -m unittest discover -s .agents/tests` passes (use `py -3` or `python3` if that's what works).
- [ ] `/hooks` (Claude) shows the four shared hooks; the `godot` MCP is connected.
