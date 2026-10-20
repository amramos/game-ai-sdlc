---
name: godot-architecture
description: Use when deciding where new code should live, whether a planned content folder should be created now, whether a technical decision deserves an ADR, or when evaluating whether one of the project's architectural rules should have an exception for a specific case. Also use to evaluate coupling between existing parts of the project.
---

# Architecture decisions

This skill doesn't implement anything — it produces a decision (and, when applicable, the ADR that records it) for another skill (`godot-feature-dev`, `godot-refactor`) to execute.

## Deciding the layer for new code

Follow the dependency tree from `docs/architecture.md` (core → data → components → entities → systems → levels), always "downward": a layer never references a layer above it in the list.

If the answer isn't obvious, the tiebreaker is: **which layer minimizes the number of other files that need to know about this change?** The layer with the least resulting coupling wins.

## Deciding whether a planned folder should be created now

Only create `entities/`, `levels/`, `components/`, `systems/`, `scenes/`, `autoload/`, `assets/`, or `data/` when the real file that will live there is already being written in this task — never ahead of time. See ADR-0001. When creating it, copy the convention already written in `docs/architecture.md` into the new folder's `README.md`, don't write it from scratch.

## Deciding whether something needs an ADR

It needs an ADR when at least one of these is true:

- an external dependency (addon, MCP, library) is being adopted;
- more than one technically valid option exists and the one chosen isn't obvious from the code;
- a rule in `CLAUDE.md`/`docs/architecture.md` is being changed or a one-off exception is being opened;
- a previous decision is being reversed (mark the old ADR as superseded, don't delete it).

It doesn't need an ADR for a trivial, freely reversible decision (a variable name, formatting).

## Evaluating an exception to an existing rule

Before opening an exception (e.g., a new autoload, a direct `get_node` for performance reasons): confirm the "correct" alternative was genuinely considered and has a real, specific cost in this case — not "seemed faster to write right now." Record the exception as an ADR, including why the general case doesn't apply here.

## Evaluating coupling in existing code

Signs of improper coupling to look for: a node accessing another via a long relative path; logic that changes behavior based on `is` / a concrete type check of another class; an autoload being read/written by many unrelated parts of the code (a candidate for a disguised EventBus — see ADR-0005); a scene that instantiates and configures other unrelated scenes in detail, beyond its own purpose.
