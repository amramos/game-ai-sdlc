---
name: godot-plan
description: Use before starting any non-trivial task (more than one file, or any structural scene change) in this Godot project. Classifies the task, resolves the architecture/layer decision up front, and decides whether to dispatch a single godot-developer/godot-debugger call or several in parallel. Runs in the orchestrating session itself, never as a subagent.
---

# Planning and dispatch

This skill is how the orchestrating session decides *before* touching code — it doesn't implement anything itself. The orchestrator is the project's one "thinking" role: it resolves ambiguity here so `godot-developer`, `godot-debugger` and `godot-reviewer` receive an unambiguous brief and can stay narrowly scoped, cheap, and fast. It stays in the orchestrating session on purpose: the agent that talks to the owner is the one that holds the context to decide.

**Only applies when subagents are actually being dispatched.** Working directly in the main session is normal and often correct; this skill has nothing to say about that case beyond step 2, which is worth doing either way.

## 1. Classify the task

- Single coherent change (one responsibility, even if it touches a few files) → one dispatch.
- Genuinely independent pieces (different files/systems, no shared state, fixing one doesn't affect the other) → candidate for parallel dispatch (step 3).
- Not sure whether it's independent → treat as single/sequential. A wrong guess at parallelism causes conflicts and wasted subagent turns, which costs more than doing it sequentially would have.

## 2. Resolve the architecture decision yourself, before dispatching

Use the `godot-architecture` skill's rules (dependency-tree tiebreaker, when a folder is created, when an ADR is needed) to decide: which layer, which existing pattern to follow (name a concrete reference file), and whether an ADR is needed. Write the answer into the dispatch brief as a stated fact, not an open question — `godot-developer` should not have to make this call itself. If an agent reports mid-task that the resolved layer was wrong, that's new information the orchestrator missed: take the task back, decide again, and re-dispatch; don't let the developer improvise a second decision on its own.

## 3. Decide single vs. parallel dispatch

Parallelize only when every one of these holds for the candidate pieces:

- different files — no two pieces write the same script or scene;
- no shared interface/signal contract still being decided (if piece B's shape depends on what piece A produces, they're sequential, not parallel — resolve the contract in step 2 first, then both sides can implement in parallel);
- each piece is independently testable/validatable on its own.

Examples in this project: fixing two unrelated pre-existing GUT failures in different test files; building two independent `components/` that don't reference each other. Not parallel: two changes to the same `.tscn`; a new `system` and the `component` it coordinates, while the signal contract between them is still undecided.

To dispatch in parallel, issue multiple `Agent` calls in the same response. Never dispatch more than one `godot-developer`/`godot-debugger` against the same file at the same time.

## 4. Write the dispatch brief

Each dispatch is self-contained — the subagent has no memory of this conversation. Include:

- the task, scoped to exactly this piece;
- the resolved layer/pattern/target file path from step 2;
- any constraint that matters here (don't touch file X, this is a bugfix not a refactor);
- the report contract: a short structured summary only (see the agent's own "Report contract" section) — never expect a full diff pasted back.

## 5. After dispatch: consolidate, don't dump

Read each agent's summary, run the shared validation (lint/parse/tests) once across all the changes together, and relay the user a short synthesis — not the agents' raw output concatenated. If two parallel pieces touched adjacent code, re-check the integration by hand before calling the task done.

## Bigger work

For a whole epic built by several agents with review and a playtest, use the `team-lead` skill from the `game-sdlc` plugin; it applies this skill's dispatch rules to each piece.
