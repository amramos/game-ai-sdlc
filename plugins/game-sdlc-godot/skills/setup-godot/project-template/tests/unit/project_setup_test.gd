extends GutTest

## Proves the suite runs and finds tests from day one. Keep it: a run that reports zero tests means
## GUT's configuration (.gutconfig.json) stopped matching the test folders.


func test_project_names_a_main_scene_that_loads() -> void:
	var main_scene: String = ProjectSettings.get_setting("application/run/main_scene", "")
	assert_ne(main_scene, "", "project.godot names a main scene")
	assert_true(ResourceLoader.exists(main_scene), "the main scene exists")
