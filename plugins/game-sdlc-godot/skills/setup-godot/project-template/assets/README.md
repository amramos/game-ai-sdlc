# assets/

Imported art, audio and fonts, by type (`art/`, `audio/`, `fonts/`…), each folder created with its
first real file.

- `themes/ui_theme.tres` — the project theme (`project.godot`, `gui/theme/custom`) and its type
  roles: `Display`, `Body` and `Caption`, variations of `Label`. A label picks one with
  `theme_type_variation`; other controls inherit the theme's defaults. Faces and sizes are set here
  and nowhere else. The sizes from setup are placeholders on the engine's default font, until
  `art-direction` chooses the faces, sizes and treatments (its Interface section).
