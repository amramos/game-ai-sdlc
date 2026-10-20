---
name: godot-debug
description: Use when investigating an error, exception, unexpected behavior, or crash in this Godot project. Covers reproduction, reading error/debug output via MCP or logs, isolating by architectural layer, and forming a verifiable hypothesis before changing any code.
---

# Debugging

Diagnosis before fix. Don't edit code to "see if it helps" before completing steps 1–3.

## 1. Reproduce

- Confirm the exact step-by-step that causes the problem. If it's not deterministically reproducible, that's already information — note the conditions under which it appears/disappears.
- Run the project via MCP (the run/debug output tool) or `godot --headless --quit-after 1` to capture the full error output, not just the symptom reported by the user.

## 2. Isolate by layer

Use the dependency tree from `docs/architecture.md` to narrow down where the bug can be:

- Type/value error with no node involved → probably `core/` or `data/`.
- Wrong behavior of a specific object but the rest of the game is normal → the responsible component, not the whole entity (the entity only composes).
- Several objects affected at the same time within a level → probably that level's `systems/`.
- Behavior that's "impossible to trace who affects what" → the first suspect is improper coupling (an autoload being used as global state, or a signal connected somewhere non-obvious) — see ADR-0005.

## 3. Form a verifiable hypothesis

Before editing: write down (mentally or in text) what the hypothesis is and how it would be falsified. Use Grep to find every point that touches the suspect state before assuming you already know where the problem is.

## 4. Fix

- Fix the root cause in the layer isolated in step 2, not a symptom in the layer above.
- Follow the same code rules from `CLAUDE.md` (typing, file size) even for a small fix.
- If the fix reveals that an architectural rule was violated in existing code (e.g., direct coupling that should be a signal), fix that as part of the bugfix if it's small, or record it as an item in `docs/backlog.md` if it's larger than the current task's scope.

## 5. Verify

- Reproduce the original scenario from step 1 and confirm it no longer occurs.
- Run the standard validation (parsing, lint, existing tests — see the `godot-feature-dev` skill, section 4).
- If the bug didn't have a test covering the scenario and a testing framework is already installed (see `docs/plugins.md`), consider adding a regression test.
