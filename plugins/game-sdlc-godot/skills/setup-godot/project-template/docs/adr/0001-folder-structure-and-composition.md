# ADR-0001: Folder structure by layer and creation on demand

**Status:** Accepted
**Date:** {{DATE}}

## Context

The project needs a folder structure that favors composition over inheritance, low coupling, and predictable navigation for an AI agent. While assembling the initial structure, a question came up: should folders tied to gameplay content (`entities/`, `levels/`, `components/`, `systems/`, `scenes/`, `autoload/`, `assets/`, `data/`) be pre-created empty (with a README explaining each one), or should they exist only as a documented convention until the first real content needs them?

## Decision

Two categories of folders:

1. **Pure infrastructure** (`.claude/`, `addons/`, `core/`, `docs/`, `tests/`, `tools/`) — pre-created from the start, since they're independent of any design/gameplay decision.
2. **Shaped by content** (`entities/`, `levels/`, `components/`, `systems/`, `scenes/`, `autoload/`, `assets/`, `data/`) — **not** pre-created. Each one's convention (purpose, rules, when to create) is documented in `docs/architecture.md`. The folder is physically created, with its own `README.md`, only when the first real file belonging to it is written.

## Alternatives considered

- **Pre-create everything empty with a README** — this was the initial approach. Discarded: it produces ~10 folders whose only content is "empty, nothing here yet," which is speculative scaffolding for a game whose design doesn't exist yet, and is technically already a form of "implementing gameplay" (even if only the shape, not the content).
- **Document nothing until the folder exists** — discarded: without the convention written ahead of time, the first agent/session to create real content would invent the structure without the context of the composition/coupling rules already decided for the project.

## Consequences

- `docs/architecture.md` is the source of truth for the planned structure; any future session should consult it before creating one of these folders for the first time, instead of improvising a different layout.
- If the planned structure turns out to be wrong once the first real content arrives (e.g., a missing layer, or a planned layer that doesn't make sense), adjust `docs/architecture.md` and record the change as a new ADR — there's no need to migrate empty folders, since they never existed.

**Revisit when:** a content folder is genuinely needed by two features at once before either writes its first real file, or `docs/architecture.md`'s layer list changes.

