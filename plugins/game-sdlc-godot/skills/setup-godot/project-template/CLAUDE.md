# CLAUDE.md

@AGENTS.md
@docs/current-status.md

## Claude Code adapter

The imported files are the shared contract and the current snapshot. Claude-specific pieces wrap them:

- Process skills: the `game-sdlc` plugin. Godot skills: the `game-sdlc-godot` plugin. Project skills:
  `.claude/skills/`.
- Agents: `.claude/agents/`, each executing its shared workflow in `.agents/roles/`.
- Godot MCP: `.mcp.json`.
- When dispatching implementation agents, pass an explicit `model:` on every call; an agent otherwise
  inherits the session's model and its usage cap.
- Hook registrations live in owner-managed `.claude/settings.json`; never edit it as an agent —
  prepare the exact change and ask.
- Hook changes may not reach a running session: open `/hooks`, and restart if behavior is stale.
