# Architecture Decision Records (ADR)

An ADR records **one non-obvious decision**, the context that motivated it, and the alternatives that
were discarded, so a future session (human or AI) understands the "why", not just the "what". The
"what" is already in the code; the ADR exists for what the code can't say on its own.

## What an ADR binds

An ADR records **what was decided and why**. It is not a law, and it does not outrank the owner.

- **The owner can reverse any ADR at any time.** A direct instruction from the owner *is* the
  approval (`AGENTS.md`, "Who the owner is"). An agent states the cost once, builds the change, and
  records the reversal here. The `design-change` skill is the procedure.
- **An ADR's "never" binds agents acting on their own, not the owner acting deliberately.** Strong
  language exists to stop a decision being re-derived by accident months later.
- **Every ADR names what would make it wrong**, in a `**Revisit when:**` line.
- **Age is evidence, not authority.** Read an old ADR as "this was right then", and check whether its
  conditions still hold.

## When to write one

- an external dependency is adopted (addon, MCP, library);
- one of two or more valid options is chosen, and the choice isn't obvious from the code;
- a rule in `AGENTS.md` or `docs/architecture.md` changes, or an exception to one is opened;
- a decision is reversed: the old ADR is marked "Superseded by ADR-XXXX", never deleted.

Don't write one for a trivial, freely reversible decision (a variable name, formatting).

## How

Copy `0000-template.md`, give it the next number and a short slug, fill it in, and add a row below.

## Index

| ADR | Decision | Status |
|---|---|---|
| [0001](0001-folder-structure-and-composition.md) | Folders by layer; content folders created on demand | Accepted |
| [0002](0002-mcp-godot-coding-solo.md) | Godot MCP: Coding-Solo/godot-mcp | Accepted |
| [0003](0003-testing-framework-gut.md) | Testing framework: GUT | Accepted |
| [0004](0004-text-format-for-scenes-and-resources.md) | Scenes and resources always in text format | Accepted |
| [0005](0005-avoid-global-event-bus-and-autoloads.md) | No global EventBus; autoloads minimized | Accepted |
