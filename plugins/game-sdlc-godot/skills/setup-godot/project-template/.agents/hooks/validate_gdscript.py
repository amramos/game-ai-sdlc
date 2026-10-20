"""Validate every GDScript path touched by an edit; optional tools fail open."""

from __future__ import annotations

import os
from pathlib import Path
import sys

sys.dont_write_bytecode = True

from hook_common import emit_posttool_block, executable_available, payload_cwd, read_payload, relative_posix, repo_root, run, touched_path_strings, warn


def gdscript_paths(payload: dict, root: Path) -> list[Path]:
    paths: list[Path] = []
    seen: set[str] = set()
    base = payload_cwd(payload, root)
    for raw_path in touched_path_strings(payload):
        relative = relative_posix(root, raw_path, base)
        if relative is None or not relative.casefold().endswith(".gd"):
            continue
        path = (root / relative).resolve(strict=False)
        key = os.path.normcase(str(path))
        if key not in seen and path.is_file():
            seen.add(key)
            paths.append(path)
    return sorted(paths, key=lambda path: os.path.normcase(str(path)))


def _record_failure(label: str, result, failures: list[str]) -> None:
    if result.returncode != 0:
        detail = (result.stdout + result.stderr).strip()
        failures.append(f"{label}:\n{detail or f'exited {result.returncode}'}")


def validate(paths: list[Path], root: Path) -> list[str]:
    failures: list[str] = []
    if not paths:
        return failures

    if executable_available("gdformat"):
        result = run(["gdformat", "--check", *[str(path) for path in paths]], root)
        _record_failure("gdformat", result, failures)
    else:
        warn("validate_gdscript: gdformat is unavailable; skipping format validation.")

    if executable_available("gdlint"):
        result = run(["gdlint", *[str(path) for path in paths]], root)
        _record_failure("gdlint", result, failures)
    else:
        warn("validate_gdscript: gdlint is unavailable; skipping lint validation.")

    godot = os.environ.get("GODOT_BIN", "godot")
    if executable_available(godot):
        for path in paths:
            result = run(
                [godot, "--headless", "--path", str(root), "--check-only", "--script", str(path)],
                root,
            )
            _record_failure(f"Godot parse check ({path.relative_to(root).as_posix()})", result, failures)
    else:
        warn(f"validate_gdscript: {godot!r} is unavailable; skipping Godot parse validation.")
    return failures


def main() -> int:
    payload = read_payload()
    if payload is None:
        return 0
    root = repo_root(payload)
    if root is None:
        return 0
    failures = validate(gdscript_paths(payload, root), root)
    if failures:
        emit_posttool_block("GDScript validation failed. Fix before continuing.\n\n" + "\n\n".join(failures))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
