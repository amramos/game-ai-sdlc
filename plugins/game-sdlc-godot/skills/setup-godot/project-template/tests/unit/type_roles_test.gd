extends GutTest

## Text takes its look from the project theme's type roles, never from a font or size set in a scene
## or script (`game-ui`, commandment 10), so a change of face or size is one edit to the theme.

const ROLES: Array[StringName] = [&"Display", &"Body", &"Caption"]
## Third-party code is not ours to fix; hidden folders (.godot, .git) are skipped too.
const SKIPPED_FOLDERS: Array[String] = ["res://addons"]
## Split in two so this file doesn't match its own scan.
const FORBIDDEN: Array[String] = [
	"theme_override_" + "fonts/",
	"theme_override_" + "font_sizes/",
	"add_theme_" + "font_override",
	"add_theme_" + "font_size_override",
]


func test_project_theme_defines_the_type_roles() -> void:
	var path: String = ProjectSettings.get_setting("gui/theme/custom", "")
	var theme: Theme = load(path) as Theme if ResourceLoader.exists(path) else null
	assert_not_null(theme, "project.godot names a theme (gui/theme/custom) that loads")
	if theme == null:
		return
	var problems: Array[String] = []
	for role: StringName in ROLES:
		if theme.get_type_variation_base(role) != &"Label":
			problems.append("%s is not a variation of Label" % role)
		elif not theme.has_font_size(&"font_size", role):
			problems.append("%s sets no font size" % role)
	assert_true(problems.is_empty(), "\n".join(PackedStringArray(problems)))


func test_no_scene_or_script_sets_a_font_directly() -> void:
	var offenders: Array[String] = []
	_scan("res://", offenders)
	var advice: String = "Pick a type role (theme_type_variation); the theme holds faces and sizes:"
	assert_true(offenders.is_empty(), "\n".join(PackedStringArray([advice] + offenders)))


func _scan(folder: String, offenders: Array[String]) -> void:
	for child: String in DirAccess.get_directories_at(folder):
		var child_path: String = folder.path_join(child)
		if not child.begins_with(".") and child_path not in SKIPPED_FOLDERS:
			_scan(child_path, offenders)
	for file: String in DirAccess.get_files_at(folder):
		if file.get_extension() in ["gd", "tscn"]:
			_check_file(folder.path_join(file), offenders)


func _check_file(path: String, offenders: Array[String]) -> void:
	var lines: PackedStringArray = FileAccess.get_file_as_string(path).split("\n")
	for index: int in lines.size():
		for token: String in FORBIDDEN:
			if token in lines[index]:
				offenders.append("%s:%d: %s" % [path, index + 1, token])
