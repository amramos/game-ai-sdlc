"""The merge guard: when an agent may merge a pull request into main.

Branch protection is the real control, but GitHub offers it on private repositories only on paid
plans. This stands in for it on the agent's side. A `gh pr merge` whose base is main/master is refused
unless:

- `.agents/merge-policy.json` says agents may merge to main (adopted by an ADR);
- every CI check on the pull request passed;
- the reviewer's latest verdict approves the pull request's current head commit.

The verdict is a marker in a PR comment or review, written by the team lead from the reviewer's
report: `<!-- game-sdlc-review: approve sha=<head sha> -->` (or `request-changes`).

It is a safety net against mistakes, not a security boundary: a merge through another path (the
GitHub API or website) doesn't pass through it. `gh pr merge --admin` is always refused.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any

from hook_common import run, shell_segments

POLICY_PATH = Path(".agents") / "merge-policy.json"
VERDICT = re.compile(
    r"<!--\s*game-sdlc-review:\s*(approve|request-changes)\s+sha=([0-9a-fA-F]{7,40})\s*-->"
)
_PROTECTED = {"main", "master"}
_PASSING = {"SUCCESS", "NEUTRAL", "SKIPPED"}
_ENV_ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
_VALUE_OPTIONS = {
    "-b", "--body", "-F", "--body-file", "-t", "--subject", "-A", "--author-email",
    "--match-head-commit", "-R", "--repo",
}


def gh_pr_merges(command: str) -> list[list[str]]:
    """The arguments of every `gh pr merge` in a shell command."""
    found: list[list[str]] = []
    for segment in shell_segments(command):
        index = 0
        while index < len(segment) and _ENV_ASSIGNMENT.match(segment[index]):
            index += 1
        words = [token.casefold() for token in segment[index : index + 3]]
        if len(words) == 3 and words[0] in {"gh", "gh.exe"} and words[1:] == ["pr", "merge"]:
            found.append(segment[index + 3 :])
    return found


def merge_target(arguments: list[str]) -> tuple[str | None, str | None]:
    """The pull request selector (number, URL or branch) and the --repo value, if given."""
    selector: str | None = None
    repo: str | None = None
    index = 0
    while index < len(arguments):
        token = arguments[index]
        option = token.split("=", 1)[0]
        if option in {"-R", "--repo"}:
            if "=" in token:
                repo = token.split("=", 1)[1]
                index += 1
            else:
                repo = arguments[index + 1] if index + 1 < len(arguments) else None
                index += 2
            continue
        if option in _VALUE_OPTIONS:
            index += 1 if "=" in token else 2
            continue
        if not token.startswith("-") and selector is None:
            selector = token
        index += 1
    return selector, repo


def agent_merges_allowed(root: Path) -> bool:
    try:
        data = json.loads((root / POLICY_PATH).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    return isinstance(data, dict) and data.get("agent_merges_to_main") is True


def pull_request(root: Path, selector: str | None, repo: str | None) -> dict[str, Any] | None:
    command = ["gh", "pr", "view"]
    if selector:
        command.append(selector)
    if repo:
        command += ["--repo", repo]
    command += ["--json", "baseRefName,headRefOid,statusCheckRollup,comments,reviews"]
    result = run(command, root)
    if result.returncode != 0:
        return None
    try:
        data = json.loads(result.stdout or "")
    except ValueError:
        return None
    return data if isinstance(data, dict) else None


def checks_problem(rollup: list[dict[str, Any]]) -> str | None:
    if not rollup:
        return "the pull request has no CI checks yet"
    for check in rollup:
        name = check.get("name") or check.get("context") or "a check"
        if check.get("__typename") == "CheckRun" and str(check.get("status", "")).upper() != "COMPLETED":
            return f"CI check '{name}' hasn't finished"
        state = str(check.get("conclusion") or check.get("state") or "").upper()
        if state not in _PASSING:
            return f"CI check '{name}' is {state.lower() or 'pending'}"
    return None


def verdict_problem(pr: dict[str, Any]) -> str | None:
    """The latest verdict marker, across comments and reviews, must approve the current head."""
    posts = [(item.get("createdAt") or "", item.get("body") or "") for item in pr.get("comments") or []]
    posts += [(item.get("submittedAt") or "", item.get("body") or "") for item in pr.get("reviews") or []]
    latest: tuple[str, str] | None = None
    for _when, body in sorted(posts, key=lambda post: post[0]):
        for match in VERDICT.finditer(body):
            latest = (match.group(1).casefold(), match.group(2).casefold())
    if latest is None:
        return "there is no reviewer verdict on the pull request (<!-- game-sdlc-review: approve sha=... -->)"
    verdict, sha = latest
    head = str(pr.get("headRefOid") or "").casefold()
    if not head.startswith(sha):
        return f"the latest verdict is for commit {sha[:12]}, not the current head {head[:12]}; review it again"
    if verdict != "approve":
        return "the reviewer's latest verdict requests changes"
    return None


def merge_reason(command: str, root: Path, base: Path | None = None) -> str | None:
    for arguments in gh_pr_merges(command):
        if "--admin" in [token.casefold() for token in arguments]:
            return "gh pr merge --admin bypasses the repository's rules and is blocked by project policy."
        selector, repo = merge_target(arguments)
        pr = pull_request(base or root, selector, repo)
        if pr is None:
            return (
                "The merge guard couldn't read the pull request with `gh pr view` (is gh installed and"
                " signed in?), so the merge is blocked."
            )
        if str(pr.get("baseRefName") or "").casefold() not in _PROTECTED:
            continue
        if not agent_merges_allowed(root):
            return (
                "Merging into main is the owner's job in this project. Ask the owner to merge, or adopt"
                " agent merges with an ADR and .agents/merge-policy.json (team-lead-handsoff does this)."
            )
        problem = checks_problem(pr.get("statusCheckRollup") or []) or verdict_problem(pr)
        if problem:
            return f"Merge blocked by the merge guard: {problem}."
    return None
