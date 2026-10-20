# tests/

GUT tests (ADR-0003), mirroring the source tree.

- `unit/` — pure logic (`core/`, `Resource` classes, components without a scene).
- `integration/` — real scenes and composed behavior.

A test file mirrors its subject (`core/turn.gd` → `tests/unit/core/turn_test.gd`) and ends in
`_test.gd`; `.gutconfig.json` sets both, because GUT's defaults match neither.

```bash
godot --headless -s addons/gut/gut_cmdln.gd -gexit
```

The live baseline is in `docs/current-status.md`.
