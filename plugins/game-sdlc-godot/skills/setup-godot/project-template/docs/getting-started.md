# Getting started

Setting up a machine to work on {{GAME_TITLE}}. Day-to-day rules live in `AGENTS.md`; what's true
right now is `docs/current-status.md`.

## 1. Prerequisites

| Tool | For | Get it |
|---|---|---|
| **Godot {{GODOT_VERSION}}** (standard, not .NET) | Running and editing the game; parse checks | [godotengine.org/download](https://godotengine.org/download) |
| **Git** and **GitHub CLI** (`gh`) | Version control, pull requests | [git-scm.com](https://git-scm.com/), [cli.github.com](https://cli.github.com/) |
| **Python 3.10+** | The agent hooks, skill mirroring, gdtoolkit | [python.org](https://python.org/) |
| **Node.js** | `npx`, which runs the Godot MCP | [nodejs.org](https://nodejs.org/) |
| **Claude Code** and/or **Codex** | The agents | [claude.com/claude-code](https://claude.com/claude-code) |

## 2. Make `godot` reachable

The hooks and tests call `godot`. Either put the Godot executable's folder on `PATH`, or set
`GODOT_BIN` to the executable's full path. Without it, the hooks skip the parse check and say so.

## 3. Install gdtoolkit

```bash
pip install "gdtoolkit==4.*"
gdformat --version && gdlint --version
```

## 4. Open the project in Godot once

Import `project.godot`. This builds `.godot/` (the editor cache, never committed).

**Export presets** (once per project, by a human — agents don't open the editor): Project → Export →
add the platforms you ship (Windows Desktop, Linux, macOS, Web). Leave export paths empty or under
`build/`; CI passes its own. For the Web preset on itch.io, turn **Thread Support** off unless you
enable SharedArrayBuffer on the itch page. Save, and commit `export_presets.cfg` (signing secrets
live in `.godot/export_credentials.cfg`, which is ignored).

## 5. Agents

- **Claude Code:** install the plugins (`/plugin marketplace add <owner>/game-ai-sdlc`, then
  `/plugin install game-sdlc@game-ai-sdlc` and `game-sdlc-godot@game-ai-sdlc`). Open the project,
  approve the `godot` MCP server when asked, and check `/hooks` shows four entry points.
- **Codex:** run the package's `scripts/install_codex.py` once to copy the skills into
  `~/.codex/skills/`. Codex reads `AGENTS.md` and `.codex/` from the project.

## 6. GitHub (once per repository, by the owner)

- Protect `main`: pull requests only, require the CI `test` job.
- Turn on *Automatically delete head branches* (stacked pull requests retarget on their own).
- For releases: secret `BUTLER_API_KEY`; variables `ITCH_USER`, `ITCH_GAME`, `ITCH_PLAYTEST_GAME`
  (the `release` skill walks through it).

## 7. Check

- [ ] `godot --version` (or `GODOT_BIN`) works.
- [ ] `godot --headless -s addons/gut/gut_cmdln.gd -gexit` passes.
- [ ] `python3 -m unittest discover -s .agents/tests` passes.
- [ ] `/hooks` (Claude) shows the four shared hooks; the `godot` MCP is connected.
