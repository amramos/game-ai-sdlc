# ADR-0002: MCP for Claude ↔ Godot integration — Coding-Solo/godot-mcp

**Status:** Accepted
**Date:** {{DATE}}

## Context

Claude Code benefits from an MCP (Model Context Protocol) server that gives the agent tools to operate the Godot editor directly (open the editor, run the project, read error/debug output, inspect and edit scenes/nodes), instead of relying solely on text editing and manual execution by the user. There's no official MCP maintained by the Godot Foundation — the ecosystem is entirely community-driven. The decision calls for **a single** MCP, evaluated on stability, breadth of tools, active maintenance, Claude Code integration, and ease of installation.

Candidates as evaluated in 2026-08 (the setup skill re-checks that the choice is still maintained before installing it):

| Project | Adoption | Activity | License | Notes |
|---|---|---|---|---|
| **Coding-Solo/godot-mcp** | ~5,000+ stars, ~450 forks | Active (commits in Apr/2026) | MIT | Reference implementation; a reported RCE vulnerability was fixed within days — a sign of responsive maintenance |
| ee0pdt/Godot-MCP | ~600 stars | Stalled since Mar/2025 (~17 months) | MIT | Effectively abandoned |
| 3ddelano/gdai-mcp-plugin-godot | ~95 stars | Active | Proprietary, paid (US$19) | Better UX (automatic screenshots), but closed and paid |
| tomyud1/godot-mcp | ~400 stars | Active, but recent (since Jan/2026) | MIT | Promising, but no long track record |
| Forks with 150+ tools ("Godot MCP Pro" etc.) | Variable | Variable | Mixed | Large surface, little tested in production |

## Decision

Adopt **Coding-Solo/godot-mcp** (MIT) as the project's single MCP.

Installation (Claude Code):

```
claude mcp add godot -- npx -y @coding-solo/godot-mcp
```

## Alternatives considered

- **GDAI MCP** — better visual experience (automatic editor/game screenshots, live property editing), but it's proprietary, paid, and closed — not auditable or versionable as part of the project's infrastructure. Re-evaluate only if the visual workflow becomes a real bottleneck.
- **ee0pdt/Godot-MCP** — discarded for being abandoned (~17 months with no activity).
- **Forks with hundreds of tools** — discarded: more tools exposed to the agent increases the error surface/choice ambiguity, with no clear gain over the set already covered by Coding-Solo (editor, execution, debug, scenes, nodes, UID).

## Consequences

- No Godot-side addon needs to be installed — the MCP runs via `npx`, outside the Godot project itself.
- The agent can now run the project and read error/debug output directly, cutting down the "ask the user to run it and paste the error" cycle.
- Requires Node.js available in the environment where Claude Code runs (for `npx`), and the Godot editor/executable installed locally.
- If the project ever migrates to Godot 3.x (not planned), this choice should be revisited — Coding-Solo/godot-mcp assumes Godot 4.x.

**Revisit when:** the chosen MCP stops being maintained, or the project needs editor capabilities it lacks.
