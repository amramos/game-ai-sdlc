"""Backstop for destructive shell commands from either supported agent client."""

from __future__ import annotations

import os
from pathlib import Path
import re
import shlex
import sys

sys.dont_write_bytecode = True

from hook_common import emit_pretool_deny, git_invocations, payload_cwd, read_payload, repo_root, run, tool_input


_SHELL_META = re.compile(r"(?:&&|\|\||[;|`]|\$\()")
_UNRESOLVED = re.compile(r"(?:\$\{?[A-Za-z_][A-Za-z0-9_]*\}?|%[A-Za-z_][A-Za-z0-9_]*%)")
_PROTECTED_BRANCHES = {"main", "master"}

# Subcommands that author a commit on the checked-out branch. `pull` is
# deliberately absent: it is how a protected branch stays current before an
# agent branches off it, and blocking it would break the very workflow this
# rule exists to enforce. A `pull` that would create a merge commit on main is
# accepted as the residual gap; `--ff-only` authors nothing.
_COMMIT_AUTHORING_SUBCOMMANDS = {"am", "cherry-pick", "commit", "merge", "rebase", "revert"}

_COMMIT_ON_PROTECTED_REASON = (
    "Committing to main/master is blocked by project policy. Create a branch first"
    " (git checkout -b feature/<slug>), then commit there and open a pull request."
)
_PUSH_TO_PROTECTED_REASON = (
    "Pushing to main/master is blocked by project policy. Push a branch instead"
    " and open a pull request."
)


def _branch_name(refspec: str) -> str:
    """Reduce a refspec such as HEAD:refs/heads/main to its destination branch."""
    destination = refspec.split(":")[-1].lstrip("+").casefold()
    for prefix in ("refs/heads/", "heads/"):
        if destination.startswith(prefix):
            return destination[len(prefix) :]
    return destination


def _current_branch_is_protected(root: Path | None) -> bool:
    """A push with no refspec targets the checked-out branch; resolve which one."""
    if root is None:
        return True
    result = run(["git", "-c", "safe.directory=*", "rev-parse", "--abbrev-ref", "HEAD"], root)
    if result.returncode != 0:
        return True
    return result.stdout.strip().casefold() in _PROTECTED_BRANCHES


_PUSH_OPTIONS_WITH_VALUES = {
    "--exec",
    "--push-option",
    "--receive-pack",
    "--repo",
}


def _push_positionals(arguments: list[str]) -> list[str]:
    positional: list[str] = []
    index = 0
    options_finished = False
    while index < len(arguments):
        token = arguments[index]
        option = token.split("=", 1)[0]
        if not options_finished and token == "--":
            options_finished = True
        elif not options_finished and option in _PUSH_OPTIONS_WITH_VALUES:
            if "=" not in token:
                index += 1
        elif not options_finished and token.startswith("-"):
            pass
        else:
            positional.append(token)
        index += 1
    return positional


def _force_push_reason(arguments: list[str], root: Path | None) -> str | None:
    lowered = [token.casefold() for token in arguments]
    mirror = "--mirror" in lowered
    force_option = any(
        token == "-f"
        or (token.startswith("-") and not token.startswith("--") and "f" in token[1:])
        or token == "--force"
        or token.startswith("--force=")
        or token == "--force-with-lease"
        or token.startswith("--force-with-lease=")
        for token in lowered
    )
    positionals = _push_positionals(arguments)
    refspecs = positionals[1:]
    forced_refspecs = [refspec for refspec in refspecs if refspec.startswith("+")]
    if not mirror and not force_option and not forced_refspecs:
        return None
    if mirror or (force_option and "--all" in lowered):
        return "Force-pushing main/master is blocked by project policy."

    relevant_refspecs = refspecs if force_option else forced_refspecs
    if not relevant_refspecs:
        if _current_branch_is_protected(root):
            return "Force-pushing main/master is blocked by project policy."
        return None
    for refspec in relevant_refspecs:
        destination = _branch_name(refspec)
        if destination in _PROTECTED_BRANCHES:
            return "Force-pushing main/master is blocked by project policy."
        if destination in {"head", "@"} and _current_branch_is_protected(root):
            return "Force-pushing main/master is blocked by project policy."
    return None


def _push_to_protected_reason(arguments: list[str], root: Path | None) -> str | None:
    """Deny any push whose destination is main/master, forced or not.

    Separate from _force_push_reason because the two answer different questions:
    that one asks "is this rewriting protected history", this one asks "does
    this land commits on a protected branch at all". Force-pushing main was
    already blocked while an ordinary push to it sailed through, which is the
    exact gap this closes.
    """
    lowered = [token.casefold() for token in arguments]
    if "--mirror" in lowered or "--all" in lowered:
        return _PUSH_TO_PROTECTED_REASON

    refspecs = _push_positionals(arguments)[1:]
    if not refspecs:
        # No refspec pushes the checked-out branch.
        return _PUSH_TO_PROTECTED_REASON if _current_branch_is_protected(root) else None

    for refspec in refspecs:
        destination = _branch_name(refspec)
        if destination in _PROTECTED_BRANCHES:
            return _PUSH_TO_PROTECTED_REASON
        if destination in {"head", "@"} and _current_branch_is_protected(root):
            return _PUSH_TO_PROTECTED_REASON
    return None


def git_reason(command: str, root: Path | None = None) -> str | None:
    for subcommand, arguments in git_invocations(command):
        if subcommand == "reset" and "--hard" in [token.casefold() for token in arguments]:
            return "git reset --hard is blocked by project policy."
        if subcommand in _COMMIT_AUTHORING_SUBCOMMANDS and _current_branch_is_protected(root):
            return _COMMIT_ON_PROTECTED_REASON
        if subcommand == "push":
            reason = _force_push_reason(arguments, root)
            if reason:
                return reason
            reason = _push_to_protected_reason(arguments, root)
            if reason:
                return reason
    return None


def _is_ps_flag(item: str, name: str) -> bool:
    """PowerShell accepts any unambiguous parameter prefix, so -Rec means -Recurse."""
    if not item.startswith("-"):
        return False
    token = item.casefold().lstrip("-").split(":")[0]
    return bool(token) and name.startswith(token)


def _tokens(command: str, *, posix: bool = True) -> list[str]:
    try:
        return shlex.split(command, posix=posix)
    except ValueError:
        return []


def recursive_delete_targets(command: str) -> tuple[bool, list[str]]:
    powershell = re.search(r"\b(?:Remove-Item|del|erase)\b", command, re.IGNORECASE) is not None
    tokens = _tokens(command, posix=not powershell)
    if not tokens:
        return False, []
    lowered = [token.casefold() for token in tokens]

    for index, token in enumerate(lowered):
        if token in {"rm", "unlink"}:
            rest = tokens[index + 1 :]
            flags = [item for item in rest if item.startswith("-")]
            recursive = any("r" in item.casefold().lstrip("-") for item in flags)
            force = any("f" in item.casefold().lstrip("-") for item in flags)
            targets = [item for item in rest if not item.startswith("-")]
            return recursive and force, targets

    for index, token in enumerate(lowered):
        if token in {"remove-item", "del", "erase"}:
            rest = tokens[index + 1 :]
            recursive = any(_is_ps_flag(item, "recurse") for item in rest)
            force = any(_is_ps_flag(item, "force") for item in rest)
            targets: list[str] = []
            skip_value = False
            value_flags = {"-erroraction", "-ea", "-path", "-literalpath"}
            for position, item in enumerate(rest):
                if skip_value:
                    skip_value = False
                    continue
                lower = item.casefold()
                if lower in {"-path", "-literalpath"} and position + 1 < len(rest):
                    targets.append(rest[position + 1])
                    skip_value = True
                elif lower in value_flags:
                    skip_value = True
                elif not item.startswith("-"):
                    targets.append(item)
            return recursive and force, targets
    return False, []


def _same_path(left: Path, right: Path) -> bool:
    return os.path.normcase(str(left)) == os.path.normcase(str(right))


def delete_reason(command: str, root: Path, base: Path | None = None) -> str | None:
    recursive, targets = recursive_delete_targets(command)
    if not recursive:
        return None
    if _SHELL_META.search(command) or _UNRESOLVED.search(command):
        return "Recursive deletion with chaining, substitution, or unresolved variables is blocked."
    if not targets:
        return "Recursive deletion without a concrete target is blocked."

    approved_exact = [(root / name).resolve() for name in (".godot", "build", "export")]
    temp_root = Path(os.environ.get("TEMP") or os.environ.get("TMP") or root.parent / "__no_temp__").resolve()
    for raw_target in targets:
        clean = raw_target.strip('"\'')
        if any(character in clean for character in "*?") or ".." in Path(clean).parts:
            return f"Recursive deletion target is ambiguous: {raw_target}"
        try:
            target = Path(clean)
            if not target.is_absolute():
                target = (base or root) / target
            target = target.resolve(strict=False)
        except (OSError, RuntimeError, ValueError):
            return f"Recursive deletion target cannot be resolved: {raw_target}"
        if any(_same_path(target, allowed) for allowed in approved_exact):
            continue
        try:
            relative_temp = target.relative_to(temp_root)
        except ValueError:
            relative_temp = None
        if relative_temp is not None and relative_temp.parts:
            continue
        return f"Recursive deletion is allowed only for .godot, build, export, or a specific temp child: {raw_target}"
    return None


def reason_for(command: str, root: Path, base: Path | None = None) -> str | None:
    return git_reason(command, base or root) or delete_reason(command, root, base)


def main() -> int:
    payload = read_payload()
    if payload is None:
        return 0
    command = tool_input(payload).get("command")
    if not isinstance(command, str) or not command.strip():
        return 0
    root = repo_root(payload)
    if root is None:
        return 0
    reason = reason_for(command, root, payload_cwd(payload, root))
    if reason:
        emit_pretool_deny(reason)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
