---
name: godot-feature-dev
description: Use when implementing a new feature, system, component, or infrastructure change in this Godot project. Covers the mandatory context-reading workflow, deciding where the code should live, implementing it following the project's typed/composition conventions, and validating before finishing the task.
---

# Feature development

This is the standard workflow for any non-trivial change (more than one file, or any structural scene change). For pure bugfixes, use the `godot-debug` skill first to diagnose; this skill kicks in when implementing the fix.

## 1. Context before code

- Read `CLAUDE.md` (if not already fresh in the session) and the relevant section of `docs/architecture.md`.
- If the change touches a "planned" content folder (`entities/`, `components/`, `systems/`, `levels/`, `scenes/`, `data/`, `assets/`, `autoload/`) that doesn't physically exist yet, re-read its convention in `docs/architecture.md` before creating it — don't improvise a new layout.
- Run `git log --oneline -5 -- docs/adr/` to check whether there's a recent relevant decision you haven't seen yet this session.

## 2. Where the code should live

Use the dependency tree from `docs/architecture.md` (core → data → components → entities → systems → levels) to decide the layer. If unsure between two layers, use the `godot-architecture` skill.

Quick questions:

- Is it pure logic, with no node/scene involved? → `core/`
- Is it structured/tunable data? → `data/` (`Resource` class + `.tres` instance)
- Is it a behavior that could serve more than one entity, or is it isolable even if it only serves one? → `components/`
- Is it a concrete game object, composed of components? → `entities/`
- Does it coordinate several entities within a level? → `systems/` (never `autoload/`, unless it's genuinely transversal to the whole game — that requires an ADR)

## 3. Implement

- GDScript always typed. `class_name` when the script will be referenced by type elsewhere.
- Composition, not inheritance; typed signals, not `get_node` for unrelated nodes.
- If the file goes past ~250 lines before the task is done, stop and extract a component/utility instead of letting it keep growing.
- When creating/editing a `.tscn` scene, see the specific rules in the "How to modify scenes" section of `CLAUDE.md` — never manually edit `uid=`.
- Follow the input rule in `AGENTS.md`. If the game supports keyboard or pad, route those paths through the same method the click calls, and make every new verb an InputMap action.

## 4. Validate before finishing

- `gdformat --check` and `gdlint` on every touched `.gd` (automated by the pre-commit hook, if `gdtoolkit` is installed).
- Project parsing: `godot --headless --check-only --script <file>` per touched script; for a structural scene change, load the project (MCP or `godot --headless --quit-after 1`) and check the output for errors.
- Existing tests, if any, still pass.
- A new interactive surface has a pad test: what holds focus on open, Cross acts as the click, Circle as the cancel. Where the change is visible, play it once with the playtest bridge's `pad` commands.
- `git diff` reviewed before considering the task done.

## 5. Document if needed

Non-obvious decision (new dependency, exception to a rule, choice between equivalent technical alternatives) → new ADR in `docs/adr/`, copying `docs/adr/0000-template.md`. Change to folder structure → update `docs/architecture.md`.
