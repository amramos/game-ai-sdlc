# Agent tooling

Claude Code, Codex and omp share one contract and one set of safeguards. Client-specific files only
adapt them.

| Concern | Shared source | Claude | Codex | omp |
|---|---|---|---|---|
| Rules | `AGENTS.md` | `CLAUDE.md` imports it | read natively | reads `AGENTS.md` and `CLAUDE.md` natively |
| Snapshot | `docs/current-status.md` | `CLAUDE.md` imports it | required by `AGENTS.md` | `CLAUDE.md` imports it |
| Process skills | the `game-sdlc` plugins | installed as plugins; `.claude/settings.json` registers their marketplace with auto-update on | copied to `~/.codex/skills/` by the package's `install_codex.py` | installed from the same marketplace (`omp plugin install`); updated with `omp plugin upgrade` |
| Project skills | `.claude/skills/` | native | generated mirrors in `.agents/skills/` | reads `.claude/skills/`; `.omp/config.yml` turns off `.agents/skills/` so no skill is listed twice |
| Roles | `.agents/roles/` | `.claude/agents/*.md` | `.codex/agents/*.toml` | `.omp/agents/*.md` (no model set: they run on the session's model unless the owner's omp config routes them) |
| Hooks | `.agents/hooks/` | `.claude/settings.json` (owner-managed) | `.codex/hooks.json` | `.omp/hooks/pre/project-safeguards.ts` (owner-managed) |
| Godot MCP | ADR-0002 | `.mcp.json` | `.codex/config.toml` | `.mcp.json` |

## Hooks

| Hook | When | What it does |
|---|---|---|
| `protect_paths.py` | before an edit | blocks `.git/`, `addons/`, generated mirrors, `.godot/`, `*.import`, and the hook registrations |
| `guard_bash.py` | before a shell command | blocks commits and pushes to `main`, force-pushes, hard resets, broad recursive deletes, and — through `merge_guard.py` — any `gh pr merge` into `main` without the merge policy, green CI, and the reviewer's approval (or, after two review cycles, the lead's ruling) |
| `pre_commit_lint.py` | before `git commit` | checks skill mirrors and staged GDScript |
| `validate_gdscript.py` | after an edit | runs gdformat, gdlint and a Godot parse check on touched scripts |

Each runs through `.agents/hooks/run.sh`, which finds a working Python on its own (skipping the Windows
Store stub) and caches it in `.agents/local/python`. They find gdtoolkit through `python -m` when its
commands aren't on `PATH`, and Godot through `GODOT_BIN` or `.agents/local/godot`. They fail open when a
tool is missing (and say so), and fail closed on ambiguous dangerous commands.
Their tests: `python3 -m unittest discover -s .agents/tests -v`.

omp ignores the Claude and Codex hook registrations and their agent folders, so
`.omp/hooks/pre/project-safeguards.ts` runs the same four hooks with the payload those clients send:
`protect_paths.py` before `edit`/`write`, `guard_bash.py` and `pre_commit_lint.py` before `bash`, and
`validate_gdscript.py` after `edit`/`write` (its failure reaches the agent as context). On Windows it
runs `run.sh` with Git's `bash.exe`, not WSL's.

## Reload and recovery

Hook changes may not reach a running session: open `/hooks` in Claude Code, and restart any client
if behavior is stale. If a broken hook blocks its own repair, fix it from a separate terminal at the
repository root, then restart. Never disable a safeguard through personal settings.

## Ownership

`.claude/settings.json`, `.codex/hooks.json`/`config.toml`, `.omp/config.yml` and `.omp/hooks/` are
owner-managed: agents prepare the exact change and ask. Skill mirrors are generated: edit `.claude/skills/`, then run
`python3 .agents/scripts/sync_skills.py --write`.
