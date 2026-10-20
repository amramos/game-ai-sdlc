# tools/

Development-only scripts and harnesses, **never shipped** and never referenced by game code.

- `ci/export_all.py` — exports every preset into `build/<channel>/` (used by the release workflow).
- `ci/export_smoke_test.sh` — boots the exported Linux build headless and fails on errors.
