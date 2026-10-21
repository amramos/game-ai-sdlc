"""Check generated skill mirrors and staged GDScript before git commit."""

from __future__ import annotations

from pathlib import Path
import sys

sys.dont_write_bytecode = True

from hook_common import emit_pretool_deny, gdtoolkit_command, git_invocations, read_payload, repo_root, run, tool_input, warn


def is_git_commit(command: str) -> bool:
    return any(subcommand == "commit" for subcommand, _arguments in git_invocations(command))


def check_skill_sync(root: Path) -> str | None:
    script = root / ".agents" / "scripts" / "sync_skills.py"
    if not script.is_file():
        warn("pre_commit_lint: skill synchronizer is unavailable; skipping mirror check.")
        return None
    result = run([sys.executable, str(script), "--check"], root)
    if result.returncode == 1:
        return (result.stdout + result.stderr).strip() or "Generated Codex skills are stale."
    if result.returncode not in (0, 1):
        warn((result.stdout + result.stderr).strip() or "Skill mirror check could not run; allowing commit.")
    return None


def staged_gdscript_paths(root: Path) -> list[str]:
    result = run(["git", "-c", "safe.directory=*", "diff", "--cached", "--name-only", "--diff-filter=ACM"], root)
    if result.returncode != 0:
        warn("pre_commit_lint: could not inspect staged files; allowing commit.")
        return []
    return sorted(line for line in result.stdout.splitlines() if line.casefold().endswith(".gd"))


def check_staged_gdscript(root: Path) -> str | None:
    paths = staged_gdscript_paths(root)
    if not paths:
        return None
    gdformat = gdtoolkit_command("gdformat")
    gdlint = gdtoolkit_command("gdlint")
    if not gdformat or not gdlint:
        warn("pre_commit_lint: gdformat/gdlint unavailable; skipping staged GDScript lint.")
        return None
    format_result = run([*gdformat, "--check", *paths], root)
    lint_result = run([*gdlint, *paths], root)
    failures: list[str] = []
    if format_result.returncode != 0:
        failures.append((format_result.stdout + format_result.stderr).strip())
    if lint_result.returncode != 0:
        failures.append((lint_result.stdout + lint_result.stderr).strip())
    return "\n".join(failure for failure in failures if failure) or None


def main() -> int:
    payload = read_payload()
    if payload is None:
        return 0
    command = tool_input(payload).get("command")
    if not isinstance(command, str) or not is_git_commit(command):
        return 0
    root = repo_root(payload)
    if root is None:
        return 0
    failures = [failure for failure in (check_skill_sync(root), check_staged_gdscript(root)) if failure]
    if failures:
        emit_pretool_deny("Pre-commit validation failed:\n\n" + "\n\n".join(failures))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
