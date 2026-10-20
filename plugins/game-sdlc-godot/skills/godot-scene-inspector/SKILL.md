---
name: godot-scene-inspector
description: Use to understand the node tree, attached scripts, connected signals, and referenced resources of a .tscn scene in this project, without needing to manually open the Godot editor. Use before editing any scene you haven't read yet this session.
---

# Scene inspection

Never edit a `.tscn` "from memory" or assuming the structure from a previous task — scenes change outside the current session (editor, another branch, MCP). Inspect first.

## Via direct reading (fast, no editor state needed)

A `.tscn` is text structured into blocks:

- `[gd_scene load_steps=N format=3 uid="..."]` — header.
- `[ext_resource ...]` — referenced external resources (scripts, other scenes, textures).
- `[sub_resource ...]` — resources embedded in the scene itself.
- `[node name="..." type="..." parent="..."]` — each node in the tree; `parent="."` is the root, the rest use the parent's relative path.

To summarize a scene, extract: the list of `[node]`s (name, type, parent → reconstructs the hierarchy), which ones have `script = ExtResource(...)` attached, and which `[ext_resource]`s are instanced scenes (`type="PackedScene"`) vs. other assets. That's usually enough to understand the scene's purpose without needing the editor.

## Via MCP (when editor state matters)

Use the MCP tools (`docs/mcp.md`) when you need something the text doesn't show directly: signal connections made via the editor (they show up in the `.tscn` as `[connection]` blocks — also readable as text, but easy to miss in large scenes), or the current state of a scene open and not yet saved in the editor.

## What to report when finishing an inspection

- Node tree (hierarchy + type of each one).
- Attached scripts, per node.
- Connected signals (`[connection signal="..." from="..." to="..." method="..."]`).
- Referenced external resources (instanced scenes, `data/` `Resource`s, assets).
- Any apparent violation of `docs/architecture.md`'s rules found during inspection (e.g., an oversized scene, a sign of improper coupling) — report it, don't automatically fix it unless the task is to fix exactly that.
