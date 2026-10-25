extends SceneTree

## Captures one scene at the project's native resolution, for judging a screen by eye (`game-ui`):
## `<name>.png` at 1:1, `<name>_x3.png` enlarged without smoothing for reading detail, and
## `<name>_grey.png` and `<name>_blur.png` for the greyscale and squint checks.
##
## It needs a window (the headless renderer draws nothing), so run it through the lock:
##   python3 tools/windowed_run.py godot --path . -s res://tools/capture/capture.gd --
##       --scene=res://scenes/main.tscn [--state=res://<path>.gd] [--out=captures] [--name=main]
##       [--frames=10]
## A `--state` script extends CaptureState and sets the scene up before the shot.

const DEFAULT_OUT: String = "captures"
const DEFAULT_FRAMES: int = 10
const ENLARGE: int = 3
## The blur shrinks the image to about this many rows and back, so text turns to smudges at any
## native height while the large shapes and their contrast survive.
const BLUR_ROWS: int = 90


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var options: Dictionary[String, String] = _options()
	if DisplayServer.get_name() == "headless":
		_fail("needs a window: run it through tools/windowed_run.py, without --headless")
		return
	var scene_path: String = options.get("scene", "")
	if scene_path.is_empty() or not ResourceLoader.exists(scene_path):
		_fail("give an existing scene: --scene=res://<path>.tscn (got '%s')" % scene_path)
		return
	var native: Vector2i = Vector2i(
		ProjectSettings.get_setting("display/window/size/viewport_width"),
		ProjectSettings.get_setting("display/window/size/viewport_height")
	)
	# At exactly the base size, every stretch mode draws the root viewport at 1:1.
	root.mode = Window.MODE_WINDOWED
	root.size = native

	var scene: Node = (load(scene_path) as PackedScene).instantiate()
	root.add_child(scene)
	current_scene = scene
	var state_path: String = options.get("state", "")
	if not state_path.is_empty():
		var state: CaptureState = _load_state(state_path)
		if state == null:
			return
		await state.apply(scene)
	var frames: String = options.get("frames", str(DEFAULT_FRAMES))
	for frame: int in frames.to_int():
		await process_frame
	await RenderingServer.frame_post_draw

	var image: Image = root.get_texture().get_image()
	if image.get_size() != native:
		var got: Vector2i = image.get_size()
		_fail("captured %s, not the native %s: is the screen too small?" % [got, native])
		return
	image.convert(Image.FORMAT_RGB8)
	var base_name: String = options.get("name", _default_name(scene_path, state_path))
	var stem: String = _output_folder(options.get("out", DEFAULT_OUT)).path_join(base_name)
	var copies: Dictionary[String, Image] = {
		stem + ".png": image,
		stem + "_x3.png": _enlarged(image),
		stem + "_grey.png": _greyscale(image),
		stem + "_blur.png": _blurred(image),
	}
	for path: String in copies:
		var error: Error = copies[path].save_png(path)
		if error != OK:
			_fail("could not write %s (%s)" % [path, error_string(error)])
			return
	print("capture: %s at %dx%d -> %s*.png" % [scene_path, native.x, native.y, stem])
	quit(0)


func _options() -> Dictionary[String, String]:
	var options: Dictionary[String, String] = {}
	for argument: String in OS.get_cmdline_user_args():
		if argument.begins_with("--") and "=" in argument:
			options[argument.substr(2).get_slice("=", 0)] = argument.get_slice("=", 1)
	return options


func _load_state(path: String) -> CaptureState:
	var script: GDScript = load(path) as GDScript if ResourceLoader.exists(path) else null
	var state: CaptureState = script.new() as CaptureState if script != null else null
	if state == null:
		_fail("--state=%s must be a script that extends CaptureState" % path)
	return state


func _default_name(scene_path: String, state_path: String) -> String:
	var base_name: String = scene_path.get_file().get_basename()
	if not state_path.is_empty():
		base_name += "_" + state_path.get_file().get_basename()
	return base_name


func _output_folder(out: String) -> String:
	var folder: String = out
	if folder.is_relative_path():
		folder = ProjectSettings.globalize_path("res://").path_join(out)
	DirAccess.make_dir_recursive_absolute(folder)
	return folder


func _enlarged(image: Image) -> Image:
	var copy: Image = image.duplicate() as Image
	var enlarged: Vector2i = image.get_size() * ENLARGE
	copy.resize(enlarged.x, enlarged.y, Image.INTERPOLATE_NEAREST)
	return copy


## Perceived brightness (Rec. 709 weights), so colours that differ only in hue turn the same grey.
func _greyscale(image: Image) -> Image:
	var rgb: PackedByteArray = image.get_data()
	var grey: PackedByteArray = PackedByteArray()
	grey.resize(image.get_width() * image.get_height())
	for pixel: int in grey.size():
		var red: float = rgb[pixel * 3]
		var green: float = rgb[pixel * 3 + 1]
		var blue: float = rgb[pixel * 3 + 2]
		grey[pixel] = roundi(0.2126 * red + 0.7152 * green + 0.0722 * blue)
	return Image.create_from_data(
		image.get_width(), image.get_height(), false, Image.FORMAT_L8, grey
	)


func _blurred(image: Image) -> Image:
	var copy: Image = image.duplicate() as Image
	var factor: float = maxf(2.0, floorf(image.get_height() / float(BLUR_ROWS)))
	var small: Vector2i = Vector2i((Vector2(image.get_size()) / factor).max(Vector2.ONE))
	copy.resize(small.x, small.y, Image.INTERPOLATE_LANCZOS)
	copy.resize(image.get_width(), image.get_height(), Image.INTERPOLATE_CUBIC)
	return copy


func _fail(message: String) -> void:
	push_error("capture: " + message)
	quit(1)
