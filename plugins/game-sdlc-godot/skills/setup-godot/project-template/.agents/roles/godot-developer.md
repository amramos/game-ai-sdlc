# Godot developer workflow

Read root `AGENTS.md`, `docs/current-status.md`, `docs/architecture.md`, the relevant GDD section, and relevant ADRs before implementation.

1. Translate the request into the smallest coherent responsibility.
2. Choose the correct layer; use the architecture skill when unclear.
3. Inspect real scenes before structural edits; use the scene-inspector skill or Godot MCP.
4. Implement typed, data-driven GDScript with composition, signals, and small responsibilities. Follow the input rule in `AGENTS.md`.
5. Validate formatting, lint, Godot parsing/import, and relevant GUT tests with currently available tools.
6. Review the diff and update ADR/architecture/GDD/status documentation where the durable truth changed.

Do not cross GDD scope boundaries, alter a scope-defining mechanic, or produce final art/audio without owner approval. A new architectural exception requires an ADR. If the task is diagnosis without a known fix, use the debugger workflow first.
