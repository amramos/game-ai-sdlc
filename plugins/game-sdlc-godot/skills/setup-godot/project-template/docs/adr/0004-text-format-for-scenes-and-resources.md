# ADR-0004: Scenes and resources always in text format

**Status:** Accepted
**Date:** {{DATE}}

## Context

Godot allows saving scenes and resources in either text format (`.tscn`, `.tres`) or binary (`.scn`, `.res`). Text format is the editor's default when saving normally, but binary can be chosen manually, and Godot also has a project option (`editor/export/convert_text_resources_to_binary`) that converts to binary — **only at the final game's export step**, not in the source files.

## Decision

Every scene and resource file versioned in the repository is `.tscn`/`.tres` (text). Binary `.scn`/`.res` is never committed. No project setting forces binary in source files; converting to binary at final export (for performance) is a build decision, not a source-code one, and can stay enabled without violating this rule.

## Alternatives considered

- **Binary format in source code** — discarded: it makes scenes and resources unreadable by text tools (including an AI agent using Read/Edit/Grep) and eliminates the possibility of a reviewable Git diff, which is precisely one of the foundation's explicit priorities.

## Consequences

- `.tscn`/`.tres` diffs are reviewable in any standard Git tool.
- An AI agent can read, understand, and edit an entire scene as text, without needing to open the Godot editor for it (though the MCP — ADR-0002 — also allows inspection/editing via the editor when needed).
- Merge conflicts in `.tscn` can still occur if two changes touch the same scene in parallel; no automatic merge driver is configured — see `docs/git-workflow.md` for how to avoid/resolve this.

**Revisit when:** text resources measurably cost export performance, or Godot changes how it merges and diffs them.

