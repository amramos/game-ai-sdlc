"""Find a working Codex and run one read-only review with it, so a fallback is never silent.

    python codex_review.py --probe
    python codex_review.py --repo <dir> --prompt-file <file> --out <file> [--model <id>] [--effort <level>]
                    [--timeout <s>]

--probe prints `ROUTE: <companion|cli> <path>` for the first route that works and exits 0, or
exits 2 when there is none.

A review runs from <dir> without write access, writes the full findings to <out>, prints
`ROUTE: <kind> <path>` and then the last `VERDICT: approve|request-changes` line of the findings.
When a route runs but fails, the next route is tried, and each failure is printed as
`FAILED: <kind> <path>: <reason>`. Exit codes: 0 a verdict was found, 2 no route, 3 every route
that ran failed or returned no verdict. It never exits 0 without an other-vendor verdict.

Routes, in order:
1. the Codex plugin's companion, `codex-companion.mjs`: the newest version at any depth under
   ~/.claude/plugins/cache/openai-codex/, else the marketplace copy; run as `node <script> task`;
2. a `codex` CLI on PATH, run as `codex exec --skip-git-repo-check -s read-only -o <out>`;
3. on Windows, the Codex desktop app's bundled CLI under %LOCALAPPDATA%\\OpenAI\\Codex\\bin\\.

Standard library only.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Callable

NO_ROUTE, FAILED = 2, 3
VERDICT = re.compile(r"^[\s>*_`#-]*VERDICT:\s*[*_`]*\s*(approve|request-changes)\b", re.IGNORECASE | re.MULTILINE)
VERSION = re.compile(r"^\d+(?:\.\d+)+$")


@dataclass
class Route:
    kind: str  # "companion" or "cli"
    path: Path
    launcher: list[str] = field(default_factory=list)  # argv that runs it, before its own arguments

    def label(self) -> str:
        return f"{self.kind} {self.path}"


def version_key(path: Path) -> tuple:
    """Sort key: the highest dotted version in the path's folders, then the file's age."""
    versions = [tuple(int(n) for n in part.split(".")) for part in path.parts if VERSION.match(part)]
    try:
        mtime = path.stat().st_mtime
    except OSError:
        mtime = 0.0
    return (max(versions) if versions else (), mtime)


def newest(paths: list[Path]) -> Path | None:
    return max(paths, key=version_key) if paths else None


def find_companion(home: Path) -> Path | None:
    plugins = home / ".claude" / "plugins"
    cache = plugins / "cache" / "openai-codex"
    # At any depth: the cache nests it by plugin and version, and a fixed-depth glob misses it.
    found = newest(sorted(cache.rglob("codex-companion.mjs"))) if cache.is_dir() else None
    if found:
        return found
    marketplace = plugins / "marketplaces" / "openai-codex" / "plugins" / "codex" / "scripts" / "codex-companion.mjs"
    return marketplace if marketplace.is_file() else None


def find_desktop_cli(local_app_data: str | None) -> Path | None:
    if not local_app_data:
        return None
    root = Path(local_app_data) / "OpenAI" / "Codex" / "bin"
    return newest(sorted(root.rglob("codex.exe"))) if root.is_dir() else None


def discover(
    home: Path | None = None,
    which: Callable[[str], str | None] = shutil.which,
    local_app_data: str | None = None,
    windows: bool = os.name == "nt",
) -> list[Route]:
    """Every route that exists here, in the order they are tried. Nothing is run."""
    home = home or Path.home()
    if local_app_data is None:
        local_app_data = os.environ.get("LOCALAPPDATA")
    routes: list[Route] = []
    companion, node = find_companion(home), which("node")
    if companion and node:
        routes.append(Route("companion", companion, [node, str(companion)]))
    seen: set[str] = set()
    cli = which("codex")
    if cli:
        routes.append(Route("cli", Path(cli), [cli]))
        seen.add(os.path.normcase(os.path.realpath(cli)))
    desktop = find_desktop_cli(local_app_data) if windows else None
    if desktop and os.path.normcase(os.path.realpath(desktop)) not in seen:
        routes.append(Route("cli", desktop, [str(desktop)]))
    return routes


def responds(route: Route, timeout: float = 60) -> bool:
    """A CLI route works if `--version` answers; a companion needs only its file and node."""
    if route.kind == "companion":
        return route.path.is_file()
    try:
        return subprocess.run(route.launcher + ["--version"], capture_output=True, timeout=timeout).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def last_verdict(text: str) -> str | None:
    found = VERDICT.findall(text)
    return f"VERDICT: {found[-1].lower()}" if found else None


def tail(text: str, limit: int = 400) -> str:
    text = " ".join(text.split())
    return text if len(text) <= limit else "..." + text[-limit:]


def run_route(
    route: Route, repo: Path, prompt_file: Path, out: Path, model: str | None, timeout: float, effort: str | None = None,
) -> str | None:
    """Run one review. Returns None on success (the findings are in `out`), else the reason it failed."""
    if out.exists():
        out.unlink()
    if route.kind == "companion":
        # Read-only: never --write. --fresh so it never resumes an earlier thread.
        argv = route.launcher + ["task", "--fresh", "--cwd", str(repo), "--prompt-file", str(prompt_file)]
        if model:
            argv += ["--model", model]
        if effort:
            argv += ["--effort", effort]
        stdin = None
    else:
        argv = route.launcher + ["exec", "--skip-git-repo-check", "-s", "read-only", "-o", str(out)]
        if model:
            argv += ["-m", model]
        if effort:
            argv += ["-c", f"model_reasoning_effort={effort}"]
        stdin = prompt_file.read_text(encoding="utf-8")  # the prompt goes on stdin
    try:
        result = subprocess.run(
            argv, cwd=repo, input=stdin, capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=timeout, stdin=None if stdin is not None else subprocess.DEVNULL,
        )
    except subprocess.TimeoutExpired:
        return f"timed out after {timeout:g}s"
    except OSError as error:
        return f"could not start: {error}"
    if route.kind == "companion":
        out.write_text(result.stdout, encoding="utf-8")
    findings = out.read_text(encoding="utf-8", errors="replace") if out.exists() else ""
    if result.returncode != 0:
        return f"exit {result.returncode}: {tail(result.stderr or result.stdout) or 'no output'}"
    if not findings.strip():
        return f"empty result: {tail(result.stderr) or 'no output'}"
    if not last_verdict(findings):
        return "no VERDICT line in the findings"
    return None


def review(
    routes: list[Route], repo: Path, prompt_file: Path, out: Path, model: str | None, timeout: float,
    effort: str | None = None,
) -> int:
    if not routes:
        print("NO ROUTE: no Codex companion with node, no codex on PATH, no Codex desktop CLI")
        return NO_ROUTE
    for route in routes:
        reason = run_route(route, repo, prompt_file, out, model, timeout, effort)
        if reason is None:
            print(f"ROUTE: {route.label()}")
            print(last_verdict(out.read_text(encoding="utf-8", errors="replace")))
            return 0
        print(f"FAILED: {route.label()}: {reason}")
    return FAILED


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--probe", action="store_true", help="only find a working route")
    parser.add_argument("--repo", type=Path, help="checkout to review, run read-only from here")
    parser.add_argument("--prompt-file", type=Path, help="the review prompt")
    parser.add_argument("--out", type=Path, help="where the full findings go")
    parser.add_argument("--model", help="model id to pass to Codex")
    parser.add_argument("--effort", help="reasoning effort to pass to Codex (low, medium, high…)")
    parser.add_argument("--timeout", type=float, default=1800, help="seconds per route (default 1800)")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # agents read it; Windows pipes default to a code page

    if args.probe:
        for route in discover():
            if responds(route):
                print(f"ROUTE: {route.label()}")
                return 0
        print("NO ROUTE: no Codex companion with node, no codex on PATH, no Codex desktop CLI")
        return NO_ROUTE

    if not (args.repo and args.prompt_file and args.out):
        parser.error("a review needs --repo, --prompt-file and --out (or use --probe)")
    if not args.repo.is_dir():
        parser.error(f"--repo is not a folder: {args.repo}")
    if not args.prompt_file.is_file():
        parser.error(f"--prompt-file is not a file: {args.prompt_file}")
    out = args.out.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    return review(discover(), args.repo.resolve(), args.prompt_file.resolve(), out, args.model, args.timeout, args.effort)


if __name__ == "__main__":
    sys.exit(main())
