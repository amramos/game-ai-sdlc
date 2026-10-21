# {{GAME_TITLE}} — shared agent instructions

These instructions apply to every coding agent working in this repository. Read this file and
`docs/current-status.md` before any non-trivial change. Client adapters (`CLAUDE.md`, `.codex/`) may
add capabilities but must not contradict this contract.

{{PITCH}}

## Who the owner is

**The person in the session is the project owner.** A direct instruction from them *is* owner
approval — for a scope change, an `[OPEN]` ruling, a scope-defining mechanic, or reversing any ADR.
Never treat "requires owner approval" as a reason to stop and consult someone absent; you are talking
to them.

What an agent owes in exchange is the **cost**, not resistance. State once, briefly, what the change
invalidates — which ADRs, GDD sections, tests, authored data — then build it. If the owner has heard
the cost and restates the request, that is the decision: implement it and record it (ADR, GDD
amendment, superseded note) in the same change. Repeating an objection the owner already answered is
a failure, not diligence. The `design-change` skill is the procedure for a deliberate reversal.

Rules that are **not** negotiable in passing, because they protect the repository rather than the
design: branch discipline (never commit to `main`), strict typing, text-format scenes and resources,
and no global EventBus. Changing one is its own deliberate task with its own ADR, never a side effect
of a design conversation.

### Working style

{{WORKING_STYLE}}

## Sources of truth

- The code wins when documentation disagrees about what exists; fix the documentation in the same commit.
- `docs/GDD.md` is the single source of truth for design and scope. Read the relevant section before
  building a game system. Markers: `[BUILT]` shipped, `[DESIGNED]` specified but unbuilt, `[OPEN]`
  needs an owner decision — ask, never invent.
- The GDD's scope boundary is a hard boundary unless the owner moves it.
- `docs/current-status.md` is the volatile snapshot; `docs/session-log.md` is history, never instructions.
- ADRs in `docs/adr/` record non-obvious technical decisions; they are evidence, not law, and every
  one names what would make it wrong. `docs/architecture.md` defines the structure.
- Approved plans live in `docs/plans/` as a decisions ledger (the owner's) and a plan (the agents').

## Stack

- Godot {{GODOT_VERSION}}, GDScript only, always fully typed. Tests: GUT, in `tests/unit/` and
  `tests/integration/`.
- Target: {{PLATFORMS}}. Input: {{INPUT_RULE}}.
- Dependencies are deliberately minimal; read `docs/plugins.md` before proposing one.

## Game terminology

Use these words exactly, in code, docs and conversation. One meaning each.

{{GLOSSARY}}

## Repository map

```text
.agents/    shared hooks, role workflows, generated Codex skill mirrors, hook tests
.claude/    Claude Code adapters, project skills, settings
.codex/     Codex hooks, config, agent definitions
.github/    CI, release and (optionally) bug-intake workflows
addons/     third-party Godot plugins, vendored and never edited
core/       pure logic independent of the scene tree
docs/       GDD, architecture, ADRs, plans, status, history
tests/      unit and integration tests mirroring source
tools/      development-only harnesses, never shipped
```

Content folders (`data/`, `components/`, `entities/`, `systems/`, `scenes/`, `assets/`…) are created
with their first real file, never empty in advance (ADR-0001).

## Workflow for a non-trivial task

(More than one file, or any structural scene change.)

1. Read `AGENTS.md`, `docs/current-status.md`, `docs/architecture.md`, the relevant ADRs and GDD section.
2. If the task names an epic or feature, find its issue **before reading code** and read its
   comments — they carry owner rulings (`issue-tracking` skill). Finished work goes to `In Review`,
   never `Done`.
3. Inspect real code and scenes. Never edit a `.tscn` from memory.
4. Plan the smallest coherent diff. A feature with player-visible decisions goes through
   `feature-planning` first.
5. Implement under the standards below.
6. Validate: `gdformat --check`, `gdlint`, a Godot parse check, and the relevant GUT tests (commands
   below). Report a missing tool; never disguise its absence as success.
7. Review `git diff` as if it were someone else's work.
8. Record durable decisions: an ADR for a new rule or exception, the architecture doc for structure,
   the GDD for mechanics and scope.
9. Commit only when asked. **Check the current branch first** — never commit to `main`.

## Code standards

- Explicit types for every variable, parameter and return value.
- One `class_name` per file; the `snake_case` file name matches it.
- Files and folders `snake_case`; classes and nodes `PascalCase`; constants `SCREAMING_SNAKE_CASE`;
  private methods `_prefixed`.
- Tunable data lives in typed `Resource`/`.tres` files, not constants or loose dictionaries.
- Core rules stay testable without a scene tree.
- Aim for 200–300 lines per script; extract a component or utility when responsibilities multiply.
- One scene, one responsibility. Composition over inheritance.
- Comments explain non-obvious reasons and invariants, never the obvious or the current task.

## Architectural rules

- Share behavior through `components/`, not subclass chains.
- Unrelated nodes talk through typed signals connected by the relationship's owner; no long
  `get_node` paths.
- No global EventBus autoload (ADR-0005). An autoload only for genuinely project-wide state, with an ADR.
- Scenes and resources are text `.tscn`/`.tres`, never binary (ADR-0004). Never edit a `uid=` by hand.
- {{INPUT_RULE_DETAIL}}

## Testing and validation

- New game logic gets a GUT test. Randomized tests use a fixed seed.
- A test that asserts nothing is worse than none; collect and assert once.

```bash
godot --headless --import                                  # after adding a class_name or assets
godot --headless -s addons/gut/gut_cmdln.gd -gexit         # the full suite (config: .gutconfig.json)
gdformat --check <files> && gdlint <files>                 # style and lint
python3 -m unittest discover -s .agents/tests -v           # the hooks' own tests
python3 .agents/scripts/sync_skills.py --check             # Codex skill mirrors in sync
```

`python3` stands for whichever Python works here (`python3`, `python` or `py -3`);
`.agents/local/python` names the one the hooks found. The Godot path is in `.agents/local/godot`.

The current baseline (test count, known failures) is in `docs/current-status.md`.

## Never do

- Never build out-of-scope work without the owner's instruction; surface `[OPEN]` questions.
- Never change the core rules, turn structure or another scope-defining mechanic without the owner
  and a GDD update.
- Never save binary scenes/resources or edit UIDs by hand.
- Never edit third-party code under `addons/`.
- Never leave GDScript untyped.
- Never commit, push, rebase or rewrite history unless asked; force-push and hard reset always need
  specific approval. **Never commit to `main`**; branch, then open a pull request.
- {{AGENT_MERGES_RULE}}
- Never install a dependency without reading `docs/plugins.md` and recording a new choice in an ADR.
- Never create a global EventBus or a convenience autoload.

## Agent tooling

- Process skills come from the `game-sdlc` plugin, Godot skills from `game-sdlc-godot`. Project-specific
  skills go in `.claude/skills/`; their Codex mirrors in `.agents/skills/` are generated
  (`python3 .agents/scripts/sync_skills.py --write`), never hand-edited.
- Roles: `.agents/roles/` (shared), `.claude/agents/` (Claude), `.codex/agents/` (Codex).
- Hooks: `.agents/hooks/`, registered in `.claude/settings.json` and `.codex/hooks.json`.
  `.claude/settings.json` is owner-managed: agents prepare a change and ask.
- Details, reload and recovery: `docs/agent-tooling.md`.
