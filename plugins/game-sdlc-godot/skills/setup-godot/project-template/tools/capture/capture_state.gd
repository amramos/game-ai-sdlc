class_name CaptureState
extends RefCounted

## Puts a scene into the state a capture should show: its worst real state, with the longest text,
## the most items, the busiest moment (`game-ui`, "Reviewing a screen"). Extend it, override
## `apply`, and pass the script to `tools/capture/capture.gd` with `--state=`.


## Called once the scene is in the tree, before the shot. It may await (a tween, a few frames); the
## capture waits for it.
func apply(_scene: Node) -> void:
	pass
