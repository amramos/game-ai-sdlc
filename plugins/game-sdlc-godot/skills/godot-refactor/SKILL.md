---
name: godot-refactor
description: Use when extracting a component from existing code, splitting an oversized file or scene, renaming a widely-referenced class/signal/file, or moving code between layers (core/components/entities/systems). Preserves behavior and references (UIDs, scene paths, signal connections) during the change.
---

# Refactoring

Refactoring changes structure without changing observable behavior. If the task also changes behavior, it's not just a refactor — split it into two commits (refactor, then change behavior), never mix them in the same diff.

## Before starting

- Inspect the current state with the `godot-scene-inspector` skill (if a scene is involved) and Grep (if renaming/moving something referenced across several files) — list every point that will be affected before touching the first one.
- Confirm the destination layer with the `godot-architecture` skill, if the refactor moves code between folders.

## Extracting a component

1. Create the new file in `components/` (creating the folder with its README if it doesn't exist yet — see ADR-0001) with the isolated responsibility.
2. Replace the original code with a reference to the component (a child node in the scene + a signal connection), not a direct method call.
3. Verify no reference to the old code is left orphaned (`Grep` for the old name).

## Splitting a large file or scene

1. Identify the cut by responsibility, not by arbitrary size — each resulting piece should make sense on its own.
2. Move first, then simplify — don't rewrite logic in the same step that it changes files, to keep the diff reviewable.

## Renaming something widely referenced

1. `Grep` for every occurrence of the old name (class, signal, node, file path) before changing any of them.
2. Rename the file/`class_name` first; let Godot update UIDs automatically (never manually edit `uid=`).
3. Update each reference found in step 1. Don't rely on a blind find-and-replace — confirm each occurrence is really the same thing (generic names can collide).

## Moving code between layers

Only move it if the layer decision (`godot-architecture` skill) changed — don't move it "to make it more organized" without a specific, recorded reason.

## Validate at the end

Same checklist as the `godot-feature-dev` skill (section 4: lint, parsing, tests) plus a refactor-specific check: **is observable behavior before and after identical?** If the answer isn't a clear "yes," the change wasn't just a refactor — go back and split it into two commits.
