# Shared agent hooks

These four stdlib-only Python entry points implement the same policies for Claude Code and Codex:

| Entry point | Event | Policy |
|---|---|---|
| `protect_paths.py` | PreToolUse Edit/Write | Deny protected/generated/vendor paths. |
| `guard_bash.py` | PreToolUse Bash | Deny hard reset, any commit or push that lands on main/master, force-push, and unapproved recursive deletion. |
| `pre_commit_lint.py` | PreToolUse Bash | On `git commit`, check generated skill drift and staged GDScript. |
| `validate_gdscript.py` | PostToolUse Edit/Write | Validate every touched `.gd` path with available tools. |

`hook_common.py` is shared plumbing and `merge_guard.py` is the part of `guard_bash.py` that checks `gh pr merge` (policy file, CI, reviewer verdict or lead ruling); neither is a registered entry point. All scripts accept the client's JSON payload on stdin and exit successfully. Pre-tool denials use the native structured `permissionDecision: deny` response; PostToolUse reports `decision: block`, which feeds a validation failure back to the agent but cannot undo an edit.

## Root resolution

Every registration runs a hook through `run.sh`, which finds a working Python 3.9+ (trying `$PYTHON`, `python3`, `python`, then `py -3`, and skipping the Windows Store stub by actually running each one) and caches it in the git-ignored `.agents/local/python`. Registrations resolve this directory from Git's top level. The scripts independently verify the repository through, in order, `CLAUDE_PROJECT_DIR`, payload `cwd`, and their process cwd. Subprocesses always run with the repository root as cwd. This is necessary because a session may remain inside a subdirectory after `cd`.

If a registration path is broken, Claude can block matching tool calls as a hook execution failure. Recover outside that client: open a fresh shell at the repository root, repair the registration or script, then open `/hooks` or restart. Codex may also require a new session after hook/config changes.

## Fail-open boundaries

- Malformed, empty, unknown, or targetless non-patch payloads allow the operation.
- Missing `gdformat`, `gdlint`, Godot, or the sync checker warns and allows.
- A recognized patch whose complete targets cannot be parsed denies.
- A recognized recursive deletion with ambiguous, broad, unresolved, chained, wildcard, traversal, or mixed targets denies.

Recursive deletion is allowed only for the exact repository `.godot`, `build`, or `export` directory, or a specific child beneath the OS temp directory. Tests never delete these paths; they exercise parsing only.

## Protection set

- `.git/**`
- `addons/**`, except exactly `addons/README.md`
- exact `.claude/settings.json`
- `.codex/hooks.json` and `.codex/config.toml` after bootstrap
- generated `.agents/skills/**`
- `*.import` and `.godot/**`

Shared hook implementation remains deliberately unsealed during stabilization. See `docs/agent-tooling.md`.

## Validation

```bash
python3 -m unittest discover -s .agents/tests -v
python3 .agents/scripts/sync_skills.py --check
```

Godot is found through `GODOT_BIN`, then the path in `.agents/local/godot` (written by setup, so no restart is needed), then `godot` on `PATH`; `GODOT_BIN` may be a command name or an absolute executable. gdformat and gdlint fall back to `python -m gdtoolkit.formatter` / `.linter` when they aren't on `PATH`. Parse checks use `--headless --path <repository-root> --check-only --script <absolute-file>` for every touched script.
