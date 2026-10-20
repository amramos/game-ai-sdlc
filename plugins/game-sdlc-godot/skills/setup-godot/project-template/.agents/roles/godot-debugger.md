# Godot debugger workflow

Read root `AGENTS.md`, `docs/current-status.md`, `docs/architecture.md`, and relevant ADRs before diagnosing.

1. Reproduce the reported behavior and capture exact errors/output.
2. Isolate it through the dependency direction: core → data → components → entities → systems → levels/scenes.
3. Form a falsifiable root-cause hypothesis before editing.
4. Apply the smallest root-cause fix that preserves typing and architectural boundaries.
5. Re-run the original reproduction and relevant automated checks.
6. Record a larger pre-existing architectural issue in the backlog instead of expanding the bug fix.

Do not mask a reachable cause with defensive handling. A debugger adapter without file-creation authority must report and hand off when the correct fix requires a new file.
