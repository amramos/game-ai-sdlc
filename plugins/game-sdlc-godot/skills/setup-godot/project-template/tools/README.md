# tools/

Development-only scripts and harnesses, **never shipped** and never referenced by game code.

- `ci/export_all.py` — exports every preset into `build/<channel>/` (used by the release workflow).
- `ci/export_smoke_test.sh` — boots the exported Linux build headless and fails on errors.
- `windowed_run.py` — the window lock. Two game windows in one checkout steal each other's focus,
  which pauses the game, so every windowed run goes through it: it holds
  `.agents/local/windowed-run.lock`, waits up to `--timeout` seconds (default 600) while another run
  holds it, and exits with the command's code (75 if the wait timed out). A command starting with
  `godot` runs the project's Godot (`GODOT_BIN`, then `.agents/local/godot`, then `PATH`). Headless
  runs don't need it.
- `capture/` — a screenshot of one scene at the project's native resolution, for judging a screen
  by eye (`game-ui` skill). It needs a window, so it runs through the lock:

  ```bash
  python3 tools/windowed_run.py godot --path . -s res://tools/capture/capture.gd -- \
      --scene=res://scenes/main.tscn
  ```

  It writes four PNGs to `captures/` (git-ignored): `main.png` at 1:1, the one to judge;
  `main_x3.png`, enlarged without smoothing, for reading detail; `main_grey.png` and
  `main_blur.png`, which must still show the key objects and their roles. Options:
  `--state=res://<path>.gd` (a script extending `CaptureState` that sets the scene up first: the
  longest text, the most items), `--out=<folder>`, `--name=<file name>`, `--frames=<n>` (frames to
  wait before the shot, default 10).
