"""Block writes to repository metadata, generated files, and vendor state."""

from __future__ import annotations

import sys

sys.dont_write_bytecode = True

from hook_common import emit_pretool_deny, payload_cwd, read_payload, relative_posix, repo_root, resolved_path, tool_input, tool_name, touched_path_strings


def protection_reason(path: str) -> str | None:
    normalized = path.casefold().strip("/")
    if normalized == ".git" or normalized.startswith(".git/"):
        return "Git metadata is protected."
    if normalized == "addons":
        return "Third-party addons are protected."
    if normalized.startswith("addons/") and normalized != "addons/readme.md":
        return "Third-party addons are protected; only addons/README.md may be edited directly."
    if normalized == ".claude/settings.json":
        return ".claude/settings.json is owner-managed. Prepare the exact patch for the owner."
    if normalized == ".codex/hooks.json" or normalized == ".codex/config.toml":
        return "Codex project hook/config registration is protected after bootstrap."
    if normalized == ".agents/skills" or normalized.startswith(".agents/skills/"):
        return "Codex skill mirrors are generated; edit .claude/skills and run the synchronizer."
    if normalized == ".godot" or normalized.startswith(".godot/"):
        return "Godot import/cache state is protected."
    if normalized.endswith(".import"):
        return "Godot .import metadata is protected."
    return None


def main() -> int:
    payload = read_payload()
    if payload is None:
        return 0
    root = repo_root(payload)
    if root is None:
        return 0
    base = payload_cwd(payload, root)

    raw_paths = touched_path_strings(payload)
    input_command = tool_input(payload).get("command")
    looks_like_patch = tool_name(payload).casefold() == "apply_patch" or (
        isinstance(input_command, str) and "*** Begin Patch" in input_command
    )
    if looks_like_patch and not raw_paths:
        emit_pretool_deny("Could not determine every target path in an apply_patch request.")
        return 0

    for raw_path in raw_paths:
        if resolved_path(root, raw_path, base) is None:
            emit_pretool_deny(f"Write target cannot be resolved safely: {raw_path}")
            return 0
        relative = relative_posix(root, raw_path, base)
        if relative is None:
            # Resolves cleanly but sits outside the repository (scratch dirs, temp
            # files). Nothing here is protected, so leave it to the client.
            continue
        reason = protection_reason(relative)
        if reason:
            emit_pretool_deny(f"{reason} Target: {relative}")
            return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
