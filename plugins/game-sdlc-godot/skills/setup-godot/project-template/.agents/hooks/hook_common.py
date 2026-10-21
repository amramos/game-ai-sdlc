"""Shared, stdlib-only helpers for Claude Code and Codex hooks."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
from typing import Any


_ENV_ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
_HEREDOC = re.compile(r"<<(-?)\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\2")
_GIT_GLOBAL_OPTIONS_WITH_VALUES = {
    "-c",
    "-C",
    "--config-env",
    "--exec-path",
    "--git-dir",
    "--namespace",
    "--super-prefix",
    "--work-tree",
}
_ENV_OPTIONS_WITH_VALUES = {"-C", "-S", "-u", "--argv0", "--chdir", "--split-string", "--unset"}


def read_payload() -> dict[str, Any] | None:
    try:
        value: Any = json.load(sys.stdin)
    except (EOFError, json.JSONDecodeError, OSError):
        return None
    return value if isinstance(value, dict) else None


def emit_pretool_deny(reason: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))


def emit_posttool_block(reason: str) -> None:
    print(json.dumps({"decision": "block", "reason": reason}))


def warn(message: str) -> None:
    print(message, file=sys.stderr)


def repo_root(payload: dict[str, Any] | None = None) -> Path | None:
    candidates: list[Path] = []
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR")
    if project_dir:
        candidates.append(Path(project_dir))
    if payload:
        cwd = payload.get("cwd")
        if isinstance(cwd, str) and cwd:
            candidates.append(Path(cwd))
    candidates.append(Path.cwd())

    for candidate in candidates:
        try:
            resolved = candidate.expanduser().resolve()
        except OSError:
            continue
        if (resolved / "project.godot").is_file():
            return resolved
        try:
            result = subprocess.run(
                ["git", "-c", "safe.directory=*", "rev-parse", "--show-toplevel"],
                cwd=resolved,
                capture_output=True,
                text=True,
                check=False,
            )
        except OSError:
            continue
        if result.returncode == 0:
            root = Path(result.stdout.strip()).resolve()
            if (root / "project.godot").is_file():
                return root
    return None


def tool_input(payload: dict[str, Any]) -> dict[str, Any]:
    value = payload.get("tool_input")
    return value if isinstance(value, dict) else {}


def tool_name(payload: dict[str, Any]) -> str:
    value = payload.get("tool_name")
    return value if isinstance(value, str) else ""


def _without_heredoc_bodies(command: str) -> str:
    """Mask Bash heredoc bodies so policy examples are not parsed as commands."""
    active: list[tuple[str, bool]] = []
    kept: list[str] = []
    for line in command.splitlines():
        if active:
            delimiter, strip_tabs = active[0]
            candidate = line.lstrip("\t") if strip_tabs else line
            if candidate == delimiter:
                active.pop(0)
            kept.append("")
            continue
        kept.append(line)
        active.extend((match.group(3), bool(match.group(1))) for match in _HEREDOC.finditer(line))
    return "\n".join(kept)


def _shell_segments(command: str) -> list[list[str]]:
    """Tokenize top-level shell command segments without inspecting quoted text."""
    try:
        normalized = _without_heredoc_bodies(command).replace("\r", "").replace("\n", ";")
        lexer = shlex.shlex(normalized, posix=True, punctuation_chars="();&|{}")
        lexer.whitespace_split = True
        lexer.commenters = ""
        tokens = list(lexer)
    except ValueError:
        return []

    segments: list[list[str]] = []
    current: list[str] = []
    for token in tokens:
        if token and all(character in "();&|{}" for character in token):
            if current:
                segments.append(current)
                current = []
        else:
            current.append(token)
    if current:
        segments.append(current)
    return segments


def shell_segments(command: str) -> list[list[str]]:
    """Public name for the segment tokenizer, for policies outside this module."""
    return _shell_segments(command)


def _git_command_index(segment: list[str]) -> int | None:
    """Find git when it is the command word, allowing environment prefixes."""
    index = 0
    if segment and segment[0].casefold() == "env":
        index = 1
        while index < len(segment):
            token = segment[index]
            option = token.split("=", 1)[0]
            if _ENV_ASSIGNMENT.match(token):
                index += 1
            elif token.startswith("-"):
                index += 1 if "=" in token or option not in _ENV_OPTIONS_WITH_VALUES else 2
            else:
                break
    else:
        while index < len(segment) and _ENV_ASSIGNMENT.match(segment[index]):
            index += 1
    if index < len(segment) and segment[index].casefold() in {"git", "git.exe"}:
        return index
    return None


def git_invocations(command: str) -> list[tuple[str, list[str]]]:
    """Return actual top-level git subcommands and arguments from shell text."""
    invocations: list[tuple[str, list[str]]] = []
    for segment in _shell_segments(command):
        git_index = _git_command_index(segment)
        if git_index is None:
            continue
        rest = segment[git_index + 1 :]
        index = 0
        while index < len(rest):
            token = rest[index]
            option = token.split("=", 1)[0]
            if token == "--":
                index += 1
                break
            if option in _GIT_GLOBAL_OPTIONS_WITH_VALUES:
                index += 1 if "=" in token else 2
                continue
            if token.startswith("-"):
                index += 1
                continue
            break
        if index < len(rest):
            invocations.append((rest[index].casefold(), rest[index + 1 :]))
    return invocations


_PATCH_PATH_PATTERN = re.compile(
    r"^\*\*\* (?:Add|Update|Delete) File:\s*(.+?)\s*$|"
    r"^\*\*\* Move to:\s*(.+?)\s*$|"
    r"^\+\+\+\s+b/(.+?)\s*$",
    re.MULTILINE,
)


def touched_path_strings(payload: dict[str, Any]) -> list[str]:
    """Return every path exposed by direct edit and apply_patch payloads."""
    found: list[str] = []
    values: list[Any] = []
    values.append(tool_input(payload))
    response = payload.get("tool_response")
    if isinstance(response, dict):
        values.append(response)

    for container in values:
        for key in ("file_path", "filePath", "notebook_path", "notebookPath", "path"):
            value = container.get(key)
            if isinstance(value, str) and value.strip():
                found.append(value.strip())
        for key in ("file_paths", "filePaths", "paths"):
            value = container.get(key)
            if isinstance(value, list):
                found.extend(str(item).strip() for item in value if str(item).strip())

    command = tool_input(payload).get("command")
    if isinstance(command, str):
        for match in _PATCH_PATH_PATTERN.finditer(command):
            path = next((group for group in match.groups() if group is not None), "")
            if path:
                found.append(path.strip().strip('"'))

    unique: list[str] = []
    seen: set[str] = set()
    for item in found:
        key = item.casefold()
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return unique


def payload_cwd(payload: dict[str, Any], root: Path) -> Path:
    value = payload.get("cwd")
    if not isinstance(value, str) or not value:
        return root
    try:
        candidate = Path(value).resolve()
        candidate.relative_to(root.resolve())
        return candidate
    except (OSError, RuntimeError, ValueError):
        return root


def resolved_path(root: Path, raw_path: str, base: Path | None = None) -> Path | None:
    try:
        candidate = Path(raw_path)
        if not candidate.is_absolute():
            candidate = (base or root) / candidate
        return candidate.resolve(strict=False)
    except (OSError, RuntimeError, ValueError):
        return None


def relative_posix(root: Path, raw_path: str, base: Path | None = None) -> str | None:
    resolved = resolved_path(root, raw_path, base)
    if resolved is None:
        return None
    try:
        return resolved.relative_to(root.resolve()).as_posix()
    except ValueError:
        return None


def executable_available(command: str) -> bool:
    if Path(command).is_absolute():
        return Path(command).is_file()
    from shutil import which

    return which(command) is not None


def local_setting(root: Path, name: str) -> str | None:
    """One line from .agents/local/<name>: a machine-specific, git-ignored setting written by setup."""
    try:
        value = (root / ".agents" / "local" / name).read_text(encoding="utf-8").strip()
    except OSError:
        return None
    return value or None


_GDTOOLKIT_MODULES = {"gdformat": "gdtoolkit.formatter", "gdlint": "gdtoolkit.linter"}


def gdtoolkit_command(tool: str) -> list[str] | None:
    """`gdformat`/`gdlint` from PATH, else the same tool as `python -m gdtoolkit.…`.

    pip often installs gdtoolkit's scripts into a folder that isn't on PATH; the module still works
    through the interpreter running this hook.
    """
    if executable_available(tool):
        return [tool]
    from importlib.util import find_spec

    module = _GDTOOLKIT_MODULES[tool]
    try:
        found = find_spec(module) is not None
    except (ImportError, ValueError):
        found = False
    return [sys.executable, "-m", module] if found else None


def godot_command(root: Path) -> str | None:
    """Godot from GODOT_BIN, then .agents/local/godot (written by setup, so no restart is needed),
    then `godot` on PATH."""
    for candidate in (os.environ.get("GODOT_BIN"), local_setting(root, "godot"), "godot"):
        if candidate and executable_available(candidate):
            return candidate
    return None


def run(command: list[str], root: Path) -> subprocess.CompletedProcess[str]:
    # Explicit UTF-8: on Windows the default would be the ANSI code page, and output with any
    # non-ASCII text (a PR comment, a file name) would fail to decode.
    return subprocess.run(
        command,
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
