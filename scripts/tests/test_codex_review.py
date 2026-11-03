"""Tests for team-lead's codex_review.py, with fake Codex routes in a temporary folder (no real Codex)."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parents[2]
SCRIPT = PACKAGE / "plugins" / "game-sdlc" / "skills" / "team-lead" / "scripts" / "codex_review.py"

spec = importlib.util.spec_from_file_location("codex_review", SCRIPT)
codex_review = importlib.util.module_from_spec(spec)
sys.modules["codex_review"] = codex_review  # dataclasses look their module up here
assert spec.loader is not None
spec.loader.exec_module(codex_review)

# Plays the companion (`task ...`, findings on stdout) or the CLI (`exec ... -o <out>`, prompt on
# stdin). FAKE_CODEX picks the behavior; every call's argv and prompt go to FAKE_CODEX_LOG.
FAKE = r'''
import json, os, sys
args = sys.argv[1:]
mode = os.environ.get("FAKE_CODEX", "approve")
if args == ["--version"]:
    sys.exit(0 if mode != "broken" else 1)
if args[0] == "task":
    prompt = open(args[args.index("--prompt-file") + 1], encoding="utf-8").read()
else:
    prompt = sys.stdin.read()
with open(os.environ["FAKE_CODEX_LOG"], "a", encoding="utf-8") as log:
    log.write(json.dumps({"argv": args, "prompt": prompt, "cwd": os.getcwd()}) + "\n")
if mode == "auth-error":
    sys.stderr.write("401 Unauthorized: not logged in\n")
    sys.exit(1)
body = {
    "approve": "- a.py:3 minor nit\n\n**VERDICT: approve**\n",
    "changes": "VERDICT: approve\n- a.py:9 crash on empty list, blocking\nVERDICT: request-changes\n",
    "no-verdict": "Looks fine to me.\n",
    "empty": "",
}[mode]
if args[0] == "task":
    sys.stdout.write(body)
else:
    with open(args[args.index("-o") + 1], "w", encoding="utf-8") as out:
        out.write(body)
'''


class Routes(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        self.fake = self.tmp / "fake_codex.py"
        self.fake.write_text(FAKE, encoding="utf-8")
        self.log = self.tmp / "calls.jsonl"
        self.repo = self.tmp / "repo"
        self.repo.mkdir()
        self.prompt = self.tmp / "prompt.md"
        self.prompt.write_text("Review a.py. End with a VERDICT line.", encoding="utf-8")
        self.out = self.tmp / "out" / "review.md"
        self.out.parent.mkdir()
        os.environ["FAKE_CODEX_LOG"] = str(self.log)

    def tearDown(self) -> None:
        os.environ.pop("FAKE_CODEX", None)
        os.environ.pop("FAKE_CODEX_LOG", None)

    def touch(self, *parts: str) -> Path:
        path = self.tmp.joinpath(*parts)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")
        return path

    def route(self, kind: str) -> codex_review.Route:
        return codex_review.Route(kind, self.fake, [sys.executable, str(self.fake)])

    def run_review(self, routes, mode: str = "approve") -> tuple[int, str]:
        os.environ["FAKE_CODEX"] = mode
        printed = io.StringIO()
        with contextlib.redirect_stdout(printed):
            code = codex_review.review(routes, self.repo, self.prompt, self.out, "some-model", 60, "medium")
        return code, printed.getvalue()

    def calls(self) -> list[dict]:
        if not self.log.exists():
            return []
        return [json.loads(line) for line in self.log.read_text(encoding="utf-8").splitlines()]


class DiscoverTests(Routes):
    def which(self, found: dict[str, str]):
        return lambda name: found.get(name)

    def test_takes_the_newest_companion_at_any_depth(self) -> None:
        cache = ("home", ".claude", "plugins", "cache", "openai-codex", "codex")
        self.touch(*cache, "1.0.9", "scripts", "codex-companion.mjs")
        newest = self.touch(*cache, "1.0.10", "scripts", "codex-companion.mjs")
        self.touch("home", ".claude", "plugins", "marketplaces", "openai-codex", "plugins", "codex", "scripts",
                   "codex-companion.mjs")
        routes = codex_review.discover(self.tmp / "home", self.which({"node": "node"}), "", windows=False)
        self.assertEqual([(r.kind, r.path) for r in routes], [("companion", newest)])
        self.assertEqual(routes[0].launcher, ["node", str(newest)])

    def test_falls_back_to_the_marketplace_companion(self) -> None:
        market = self.touch("home", ".claude", "plugins", "marketplaces", "openai-codex", "plugins", "codex",
                            "scripts", "codex-companion.mjs")
        routes = codex_review.discover(self.tmp / "home", self.which({"node": "node"}), "", windows=False)
        self.assertEqual([r.path for r in routes], [market])

    def test_a_companion_without_node_is_no_route(self) -> None:
        self.touch("home", ".claude", "plugins", "cache", "openai-codex", "codex", "1.0.0", "scripts",
                   "codex-companion.mjs")
        self.assertEqual(codex_review.discover(self.tmp / "home", self.which({}), "", windows=False), [])

    def test_cli_on_path_then_the_desktop_cli_on_windows(self) -> None:
        cli = self.touch("npm", "codex.cmd")
        desktop = self.touch("local", "OpenAI", "Codex", "bin", "0a1b2c3d", "codex.exe")
        found = self.which({"codex": str(cli)})
        routes = codex_review.discover(self.tmp / "home", found, str(self.tmp / "local"), windows=True)
        self.assertEqual([(r.kind, r.path) for r in routes], [("cli", cli), ("cli", desktop)])
        routes = codex_review.discover(self.tmp / "home", found, str(self.tmp / "local"), windows=False)
        self.assertEqual([r.path for r in routes], [cli])

    def test_the_same_cli_is_listed_once(self) -> None:
        desktop = self.touch("local", "OpenAI", "Codex", "bin", "0a1b2c3d", "codex.exe")
        routes = codex_review.discover(self.tmp / "home", self.which({"codex": str(desktop)}),
                                       str(self.tmp / "local"), windows=True)
        self.assertEqual(len(routes), 1)

    def test_a_cli_works_only_if_it_answers(self) -> None:
        os.environ["FAKE_CODEX"] = "approve"
        self.assertTrue(codex_review.responds(self.route("cli")))
        os.environ["FAKE_CODEX"] = "broken"
        self.assertFalse(codex_review.responds(self.route("cli")))


class ReviewTests(Routes):
    def test_companion_review_writes_findings_and_prints_route_and_verdict(self) -> None:
        code, printed = self.run_review([self.route("companion")])
        self.assertEqual(code, 0)
        self.assertEqual(printed.splitlines(), [f"ROUTE: companion {self.fake}", "VERDICT: approve"])
        self.assertIn("a.py:3", self.out.read_text(encoding="utf-8"))
        call = self.calls()[0]
        self.assertEqual(call["argv"][:2], ["task", "--fresh"])
        self.assertNotIn("--write", call["argv"])
        self.assertEqual(call["argv"][call["argv"].index("--model") + 1], "some-model")
        self.assertEqual(call["argv"][call["argv"].index("--effort") + 1], "medium")
        self.assertEqual(call["argv"][call["argv"].index("--cwd") + 1], str(self.repo))
        self.assertEqual(Path(call["cwd"]).resolve(), self.repo.resolve())

    def test_cli_review_is_read_only_with_the_prompt_on_stdin(self) -> None:
        code, printed = self.run_review([self.route("cli")], "changes")
        self.assertEqual(code, 0)
        self.assertEqual(printed.splitlines()[-1], "VERDICT: request-changes")  # the last one wins
        call = self.calls()[0]
        self.assertEqual(call["argv"][:4], ["exec", "--skip-git-repo-check", "-s", "read-only"])
        self.assertEqual(call["argv"][call["argv"].index("-o") + 1], str(self.out))
        self.assertEqual(call["argv"][call["argv"].index("-m") + 1], "some-model")
        self.assertEqual(call["argv"][call["argv"].index("-c") + 1], "model_reasoning_effort=medium")
        self.assertEqual(call["prompt"], "Review a.py. End with a VERDICT line.")

    def test_a_failed_route_is_reported_and_the_next_one_tried(self) -> None:
        failing = codex_review.Route("companion", self.tmp / "gone.mjs", [sys.executable, str(self.tmp / "gone.py")])
        code, printed = self.run_review([failing, self.route("cli")])
        self.assertEqual(code, 0)
        lines = printed.splitlines()
        self.assertTrue(lines[0].startswith(f"FAILED: companion {self.tmp / 'gone.mjs'}: exit "))
        self.assertEqual(lines[1:], [f"ROUTE: cli {self.fake}", "VERDICT: approve"])

    def test_every_route_failing_exits_3_with_each_reason(self) -> None:
        code, printed = self.run_review([self.route("companion"), self.route("cli")], "auth-error")
        self.assertEqual(code, codex_review.FAILED)
        self.assertEqual(len(printed.splitlines()), 2)
        self.assertIn("401 Unauthorized", printed)
        self.assertNotIn("ROUTE:", printed)
        self.assertNotIn("VERDICT:", printed)

    def test_no_verdict_or_empty_result_is_a_failure(self) -> None:
        for mode, reason in (("no-verdict", "no VERDICT line"), ("empty", "empty result")):
            with self.subTest(mode=mode):
                code, printed = self.run_review([self.route("cli")], mode)
                self.assertEqual(code, codex_review.FAILED)
                self.assertIn(reason, printed)

    def test_a_stale_findings_file_is_never_read_as_this_review(self) -> None:
        self.out.write_text("old review\nVERDICT: approve\n", encoding="utf-8")
        code, _ = self.run_review([self.route("cli")], "no-verdict")
        self.assertEqual(code, codex_review.FAILED)

    def test_no_route_exits_2(self) -> None:
        code, printed = self.run_review([])
        self.assertEqual(code, codex_review.NO_ROUTE)
        self.assertIn("NO ROUTE", printed)


class CommandLineTests(unittest.TestCase):
    def test_probe_with_nothing_installed_exits_2(self) -> None:
        with tempfile.TemporaryDirectory() as empty:
            env = dict(os.environ, HOME=empty, USERPROFILE=empty, LOCALAPPDATA=empty, PATH=empty)
            result = subprocess.run([sys.executable, str(SCRIPT), "--probe"], capture_output=True, text=True, env=env)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("NO ROUTE", result.stdout)
        self.assertNotIn("ROUTE: ", result.stdout.replace("NO ROUTE: ", ""))


if __name__ == "__main__":
    unittest.main()
