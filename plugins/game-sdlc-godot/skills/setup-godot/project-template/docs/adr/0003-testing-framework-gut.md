# ADR-0003: Testing framework — GUT (Godot Unit Test)

**Status:** Accepted
**Date:** {{DATE}}

## Context

Godot 4 has no built-in testing framework. The community options are essentially **GUT (Godot Unit
Test)** and **GdUnit4**. Agents write most of this project's code, so a test suite that runs headless
from the command line is what turns "the agent says it works" into evidence.

## Decision

Adopt **GUT**, installed at setup under `addons/gut/`, with tests in `tests/unit/` and
`tests/integration/` and the `*_test.gd` suffix.

- It has the largest body of examples and documentation in the GDScript community, which agents
  have learned from.
- It runs headless (`-gdir`, `-ginclude_subdirs`, `-gexit`), so the validation hooks and CI can run it.
- Its assertion API (`assert_eq`, `assert_true`, signal watching) covers what game logic needs.

GUT's defaults (`res://test/unit`, a `test_` prefix) match neither the folder nor the naming
convention. `.gutconfig.json` sets both; a first run that silently finds zero tests means it doesn't.

## Alternatives considered

- **GdUnit4** — more modern Godot 4 support and a `SceneRunner` for input simulation. Not chosen:
  community volume matters more here than simulation features. Revisit if input-level tests become
  common.

## Consequences

- `docs/plugins.md` and `tests/README.md` reference GUT; CI runs it on every pull request.
- A GUT release must track the Godot version in `project.godot`; upgrading one means checking the other.

**Revisit when:** GUT stops tracking Godot releases, or the suite's headless runtime grows long
enough that a run per pull request stops being practical.
