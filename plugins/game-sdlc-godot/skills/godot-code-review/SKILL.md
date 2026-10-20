---
name: godot-code-review
description: Use before finishing or committing a change in this Godot project, or when explicitly asked to review a diff/branch. Checks adherence to the rules in CLAUDE.md and docs/architecture.md — typing, composition vs. inheritance, signals vs. direct coupling, misuse of autoload/EventBus, file/scene size, text format for scenes and resources.
---

# Code review

Review against the project's rules, not personal style preferences. Each item below references the corresponding rule in `CLAUDE.md`/`docs/architecture.md` — if an item fails, cite the rule when reporting.

## Review scope

`git diff` (or `git diff <base>...HEAD` for a whole branch) against `main`. Review only what changed, but read neighboring code when needed to judge coupling.

## Checklist

**Typing and style**
- [ ] Every new or modified variable/parameter/return is typed.
- [ ] `gdformat --check` and `gdlint` pass (if `gdtoolkit` is available).
- [ ] Naming follows convention (`snake_case` files, `PascalCase` classes/nodes, `SCREAMING_SNAKE_CASE` constants).

**Architecture**
- [ ] No new inheritance chain between entities — shared behavior should be a component.
- [ ] No `get_node()` with a relative path between nodes that aren't directly related — should be a signal.
- [ ] No new autoload without a justifying ADR, and no use of an existing autoload as a generic EventBus.
- [ ] New structured/tunable data is a typed `Resource`, not a loose `Dictionary` or scattered constant.
- [ ] No scene/resource committed in binary format (`.scn`/`.res`).
- [ ] No manual edit of a `uid=` field.

**Input**
- [ ] The change follows the input rule in `AGENTS.md` (for example: anything clickable also takes focus and acts on `ui_accept` through the same method as its click).
- [ ] A new global verb is an InputMap action, never a hard-coded key.

**Size and responsibility**
- [ ] No new/modified `.gd` file went past ~250–300 lines without justification; if it did, it should have been split.
- [ ] Each new `.tscn` scene has a single responsibility.

**Structure**
- [ ] If a "planned" content folder was created, it follows the convention described in `docs/architecture.md`, and came with its `README.md`.
- [ ] No code in `addons/` was manually edited.

**Documentation**
- [ ] Non-obvious decision in the diff has a corresponding ADR.
- [ ] Relevant structural change is reflected in `docs/architecture.md`.

## How to report

List findings by severity (blocking vs. suggestion), each with the file/line and the rule violated. Don't approve a change with a blocking item pending — send it back for a fix before considering the task ready to commit.
