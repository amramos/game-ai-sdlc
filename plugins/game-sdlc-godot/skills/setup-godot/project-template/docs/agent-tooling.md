# Agent tooling

Claude Code and Codex share one contract and one set of safeguards. Client-specific files only adapt
them.

| Concern | Shared source | Claude | Codex |
|---|---|---|---|
| Rules | `AGENTS.md` | `CLAUDE.md` imports it | read natively |
| Snapshot | `docs/current-status.md` | `CLAUDE.md` imports it | required by `AGENTS.md` |
| Process skills | the `game-sdlc` plugins | installed as plugins | copied to `~/.codex/skills/` by the package's `install_codex.py` |
| Project skills | `.claude/skills/` | native | generated mirrors in `.agents/skills/` |
| Roles | `.agents/roles/` | `.claude/agents/*.md` | `.codex/agents/*.toml` |
| Hooks | `.agents/hooks/` | `.claude/settings.json` (owner-managed) | `.codex/hooks.json` |
| Godot MCP | ADR-0002 | `.mcp.json` | `.codex/config.toml` |

## Hooks

| Hook | When | What it does |
|---|---|---|
| `protect_paths.py` | before an edit | blocks `.git/`, `addons/`, generated mirrors, `.godot/`, `*.import`, and the hook registrations |
| `guard_bash.py` | before a shell command | blocks commits and pushes to `main`, force-pushes, hard resets, broad recursive deletes |
| `pre_commit_lint.py` | before `git commit` | checks skill mirrors and staged GDScript |
| `validate_gdscript.py` | after an edit | runs gdformat, gdlint and a Godot parse check on touched scripts |

Each runs through `.agents/hooks/run.sh`, which finds a working Python on its own (skipping the Windows
Store stub) and caches it in `.agents/local/python`. They find gdtoolkit through `python -m` when its
commands aren't on `PATH`, and Godot through `GODOT_BIN` or `.agents/local/godot`. They fail open when a
tool is missing (and say so), and fail closed on ambiguous dangerous commands.
Their tests: `python3 -m unittest discover -s .agents/tests -v`.

## Reload and recovery

Hook changes may not reach a running session: open `/hooks` in Claude Code, and restart either client
if behavior is stale. If a broken hook blocks its own repair, fix it from a separate terminal at the
repository root, then restart. Never disable a safeguard through personal settings.

## Ownership

`.claude/settings.json` and `.codex/hooks.json`/`config.toml` are owner-managed: agents prepare the
exact change and ask. Skill mirrors are generated: edit `.claude/skills/`, then run
`python3 .agents/scripts/sync_skills.py --write`.
