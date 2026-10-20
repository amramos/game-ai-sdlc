# ADR-0005: Avoid a global EventBus and minimize autoloads

**Status:** Accepted
**Date:** {{DATE}}

## Context

A common pattern in Godot tutorials is to create a global (`EventBus`/`Signals`) autoload that centralizes signals for the whole game, letting any node emit/listen to any event with no direct reference. It's a popular form of "decoupling." It's also common to pile up autoloads as the default way to share state between scenes.

## Decision

The project will **not** have a global `EventBus`/`Signals` autoload. Communication between nodes uses typed signals connected by the node that owns the relationship (the parent connects the child's signal; a node in `systems/` connects the signals of the entities it manages, scoped to the level). Autoloads in general are minimized: they're only justified for state/service genuinely transversal to the whole game (e.g., a scene-switch manager), never as a shortcut to "share this between two scenes."

## Alternatives considered

- **A single global EventBus** — discarded. It reduces *syntactic* coupling (no direct reference between nodes) but doesn't reduce *real* coupling — any part of the game can end up depending on any event, without that showing up in the scene tree or being discoverable by structural search. For a new AI session (or a human) trying to understand "what reacts to this event," the only way to find out is to search the whole project for the event's string — the opposite of the low-coupling, navigable goal that motivates this document.
- **One autoload per system, freely** — discarded as a free-for-all pattern; each autoload still needs to pass the "is this transversal to the whole game?" test before it exists, recorded in its own ADR when it happens.

## Consequences

- Tracing "who emits and who listens to a signal" is always possible by reading the scene and the script of the node that makes the connection — without relying on a project-wide text search.
- Cases that would seem to call for an EventBus (e.g., an event that several decoupled entities within the same level need to hear) are solved with a signal on a `Resource` or node scoped to that level (inside `systems/`), not a game-wide singleton.
- If, in practice, this pattern generates too many repetitive manual connections in a concrete case, the exception must be justified in a new ADR before being adopted — it shouldn't become the default out of one-off convenience.

**Revisit when:** a signal genuinely needs more than a handful of unrelated listeners and explicit wiring becomes the bug source rather than the cure.

