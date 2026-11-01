"""Regression fixtures for shared hooks, registration, and skill synchronization."""

from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[3]
HOOKS = REPO_ROOT / ".agents" / "hooks"
SCRIPTS = REPO_ROOT / ".agents" / "scripts"
sys.path.insert(0, str(HOOKS))
sys.path.insert(0, str(SCRIPTS))

import guard_bash
import hook_common
import merge_guard
import pre_commit_lint
import protect_paths
import sync_skills
import validate_gdscript


class PathExtractionTests(unittest.TestCase):
    def test_extracts_all_apply_patch_targets_and_deduplicates(self) -> None:
        payload = {
            "tool_name": "apply_patch",
            "tool_input": {
                "command": "*** Begin Patch\n*** Update File: core/a.gd\n*** Move to: core/b.gd\n*** Add File: docs/x.md\n*** End Patch"
            },
        }
        self.assertEqual(
            hook_common.touched_path_strings(payload),
            ["core/a.gd", "core/b.gd", "docs/x.md"],
        )

    def test_direct_and_response_paths_are_combined(self) -> None:
        payload = {
            "tool_input": {"file_path": "core/a.gd"},
            "tool_response": {"filePaths": ["core/b.gd", "core/a.gd"]},
        }
        self.assertEqual(hook_common.touched_path_strings(payload), ["core/a.gd", "core/b.gd"])

    def test_notebook_path_is_extracted_for_claude_notebook_edit(self) -> None:
        payload = {"tool_name": "NotebookEdit", "tool_input": {"notebook_path": "addons/probe.ipynb"}}
        self.assertEqual(hook_common.touched_path_strings(payload), ["addons/probe.ipynb"])

    def test_relative_paths_use_payload_cwd(self) -> None:
        root = REPO_ROOT
        payload = {"cwd": str(root / "docs")}
        base = hook_common.payload_cwd(payload, root)
        self.assertEqual(hook_common.relative_posix(root, "../addons/probe.txt", base), "addons/probe.txt")


class ProtectionTests(unittest.TestCase):
    def test_protected_path_matrix(self) -> None:
        protected = {
            ".git/config",
            "addons/gut/file.gd",
            "addons/nested/README.md",
            ".claude/settings.json",
            ".codex/hooks.json",
            ".codex/config.toml",
            ".agents/skills/godot-debug/SKILL.md",
            ".godot/editor/state",
            "assets/image.png.import",
        }
        for path in protected:
            with self.subTest(path=path):
                self.assertIsNotNone(protect_paths.protection_reason(path))

    def test_only_root_addons_readme_is_editable(self) -> None:
        self.assertIsNone(protect_paths.protection_reason("addons/README.md"))
        self.assertIsNone(protect_paths.protection_reason("docs/README.md"))

    @staticmethod
    def _decide(payload: dict) -> str:
        stream = io.StringIO()
        with mock.patch.object(sys, "stdin", io.StringIO(json.dumps(payload))), redirect_stdout(stream):
            protect_paths.main()
        return stream.getvalue().strip()

    def test_targets_outside_the_repository_are_left_to_the_client(self) -> None:
        """Scratch and temp files resolve cleanly but hold nothing protected."""
        with tempfile.TemporaryDirectory() as directory:
            outside = Path(directory).resolve() / "scratchpad" / "probe.py"
            payload = {
                "cwd": str(REPO_ROOT),
                "tool_name": "Write",
                "tool_input": {"file_path": str(outside)},
            }
            self.assertEqual(self._decide(payload), "")

    @mock.patch.object(protect_paths, "resolved_path", return_value=None)
    def test_unresolvable_target_is_still_denied(self, _resolved: mock.Mock) -> None:
        """Outside-the-repo must fall through, but genuinely unparseable must deny."""
        payload = {
            "cwd": str(REPO_ROOT),
            "tool_name": "Write",
            "tool_input": {"file_path": "core/turn_processor.gd"},
        }
        self.assertIn("cannot be resolved", self._decide(payload))

    def test_protected_target_is_denied_from_an_absolute_path(self) -> None:
        payload = {
            "cwd": str(REPO_ROOT),
            "tool_name": "Write",
            "tool_input": {"file_path": str(REPO_ROOT / ".claude" / "settings.json")},
        }
        self.assertIn("owner-managed", self._decide(payload))


class ShellGuardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp()).resolve()
        self.temp = Path(tempfile.mkdtemp()).resolve()
        self.env = mock.patch.dict(os.environ, {"TEMP": str(self.temp), "TMP": str(self.temp)})
        self.env.start()

    def tearDown(self) -> None:
        self.env.stop()

    def assert_allowed(self, command: str) -> None:
        self.assertIsNone(guard_bash.reason_for(command, self.root), command)

    def assert_denied(self, command: str) -> None:
        self.assertIsNotNone(guard_bash.reason_for(command, self.root), command)

    def test_allowed_commands(self) -> None:
        commands = [
            "rm -rf .godot",
            "rm -f -r build/",
            "Remove-Item -Force -Recurse .godot",
            "Remove-Item -Recurse -ErrorAction SilentlyContinue -Force export",
            f'Remove-Item -LiteralPath "{self.temp / "probe"}" -Recurse -Force',
            "git push origin feature/test",
            "git push --force-with-lease origin feature/test",
            "git push --force-if-includes origin feature/test",
            "git reset --soft HEAD~1",
            "godot --headless --import",
            "godot --headless -s addons/gut/gut_cmdln.gd -gexit",
        ]
        for command in commands:
            with self.subTest(command=command):
                self.assert_allowed(command)

    def test_denied_commands(self) -> None:
        commands = [
            "git reset --hard HEAD~1",
            "git push --force origin main",
            "git push origin master -f",
            "git -c safe.directory=* push --force origin main",
            "git status && git push --force origin main",
            "git push --force",
            "git push -f origin",
            "git push --force-with-lease=stale origin HEAD",
            "rm -rf .",
            "rm -rf *",
            "rm -rf ../elsewhere",
            "rm -rf build other",
            "rm -rf $TARGET",
            "rm -rf build && echo done",
            "Remove-Item -Recurse -Force C:\\",
            f'Remove-Item -Recurse -Force "{self.temp}"',
        ]
        for command in commands:
            with self.subTest(command=command):
                self.assert_denied(command)

    def test_subdirectory_target_resolves_from_payload_cwd(self) -> None:
        docs = self.root / "docs"
        docs.mkdir()
        self.assertIsNotNone(guard_bash.reason_for("rm -rf build", self.root, docs))

    def test_powershell_parameter_abbreviations_are_recognized(self) -> None:
        """PowerShell accepts any unambiguous prefix, so -Rec/-For must not slip past."""
        for flags in ("-Rec -For", "-R -F", "-Recur -Forc", "-For -Rec"):
            with self.subTest(flags=flags):
                self.assert_denied(f"Remove-Item {flags} {self.root}")
                self.assert_allowed(f"Remove-Item {flags} .godot")

    def test_value_flags_are_not_mistaken_for_recurse_or_force(self) -> None:
        self.assert_allowed("Remove-Item -ErrorAction SilentlyContinue -Recurse -Force .godot")

    def test_branch_name_containing_a_protected_word_is_allowed(self) -> None:
        """\\bmain\\b once matched inside any branch name; only the destination counts."""
        self.assert_allowed("git push --force origin feature/main-game-hud")
        self.assert_allowed("git push --force origin fix/remaster-audio")
        self.assert_denied("git push --force origin main")
        self.assert_denied("git push --force origin HEAD:refs/heads/master")

    def test_quoted_or_echoed_policy_text_is_not_a_command(self) -> None:
        self.assert_allowed('python -c "print(\'git push --force origin main\')"')
        self.assert_allowed("echo git push --force origin main")
        self.assert_allowed("echo git reset --hard HEAD~1")
        self.assert_allowed("cat <<'POLICY'\ngit push --force origin main\ngit reset --hard HEAD~1\nPOLICY")

    def test_top_level_multiline_git_commands_are_still_guarded(self) -> None:
        self.assert_denied("Write-Output ok\ngit push --force origin main")
        self.assert_denied("echo ok\ngit reset --hard HEAD~1")
        self.assert_denied("cat <<'TEXT'\nsafe text\nTEXT\ngit push --force origin main")

    def test_forced_refspec_and_multi_ref_options_are_denied(self) -> None:
        self.assert_denied("git push origin +HEAD:main")
        self.assert_denied("git push origin +HEAD:refs/heads/master")
        self.assert_denied("git push --mirror origin")
        self.assert_denied("git push --force --all origin")

    def test_forced_feature_refspec_is_allowed(self) -> None:
        self.assert_allowed("git push origin +HEAD:feature/route-map")


class ProtectedBranchTests(unittest.TestCase):
    """A push with no refspec targets the checked-out branch, so resolve it."""

    def _repo(self, branch: str) -> Path:
        root = Path(tempfile.mkdtemp()).resolve()
        commands = [
            ["git", "init", "-q"],
            ["git", "config", "user.email", "test@example.com"],
            ["git", "config", "user.name", "test"],
            ["git", "commit", "-q", "--allow-empty", "-m", "base"],
        ]
        if branch != "master":
            commands.append(["git", "checkout", "-q", "-b", branch])
        for command in commands:
            result = subprocess.run(command, cwd=root, capture_output=True)
            if result.returncode != 0:
                self.skipTest(f"git unavailable: {' '.join(command)}")
        return root

    def test_bare_force_push_is_denied_on_a_protected_branch(self) -> None:
        for branch in ("main", "master"):
            with self.subTest(branch=branch):
                self.assertIsNotNone(guard_bash.reason_for("git push --force", self._repo(branch)))

    def test_bare_force_push_is_allowed_on_a_feature_branch(self) -> None:
        self.assertIsNone(guard_bash.reason_for("git push --force", self._repo("feature/route-map")))

    def test_head_refspec_follows_the_checked_out_branch(self) -> None:
        self.assertIsNotNone(guard_bash.reason_for("git push -f origin HEAD", self._repo("main")))
        self.assertIsNone(guard_bash.reason_for("git push -f origin HEAD", self._repo("feature/x")))

    def test_unresolvable_branch_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            self.assertIsNotNone(guard_bash.reason_for("git push --force", Path(directory)))

    # --- Agents never commit to main -----------------------------------

    def test_committing_on_a_protected_branch_is_denied(self) -> None:
        for branch in ("main", "master"):
            with self.subTest(branch=branch):
                self.assertIsNotNone(guard_bash.reason_for('git commit -m "x"', self._repo(branch)))

    def test_committing_on_a_feature_branch_is_allowed(self) -> None:
        self.assertIsNone(
            guard_bash.reason_for('git commit -m "x"', self._repo("feature/crew-generator"))
        )

    # --- Worktrees: the branch that matters is the session's, not the root's ---
    #
    # `root` comes from repo_root(), which prefers CLAUDE_PROJECT_DIR -- the
    # primary checkout. A worktree session runs somewhere else entirely, and the
    # primary checkout is usually sitting on main while it does. Resolving HEAD
    # from `root` denied every commit a worktree session tried to make, which is
    # what these two pin: the branch that decides is the one the command will
    # actually run on.

    def test_a_worktree_on_a_feature_branch_may_commit_while_the_root_is_on_main(self) -> None:
        self.assertIsNone(
            guard_bash.reason_for(
                'git commit -m "x"', self._repo("main"), self._repo("feature/spyglass")
            )
        )

    def test_a_worktree_on_main_is_still_denied_however_the_root_sits(self) -> None:
        self.assertIsNotNone(
            guard_bash.reason_for(
                'git commit -m "x"', self._repo("feature/spyglass"), self._repo("main")
            )
        )

    def test_every_commit_authoring_subcommand_is_denied_on_main(self) -> None:
        root = self._repo("main")
        for command in (
            "git commit --amend --no-edit",
            "git merge origin/feature/x",
            "git revert 073f389",
            "git cherry-pick 073f389",
            "git rebase origin/main",
            "git am patch.mbox",
        ):
            with self.subTest(command=command):
                self.assertIsNotNone(guard_bash.reason_for(command, root))

    def test_pull_stays_allowed_on_main(self) -> None:
        """Pulling is how main stays current before an agent branches off it."""
        root = self._repo("main")
        self.assertIsNone(guard_bash.reason_for("git pull --ff-only origin main", root))
        self.assertIsNone(guard_bash.reason_for("git fetch origin", root))

    def test_the_bare_push_that_slipped_through_is_now_denied(self) -> None:
        """Regression: an ordinary `git push` while on main was allowed, because
        only *force*-pushing a protected branch was ever checked. That is how
        073f389 reached origin/main without a branch or a pull request."""
        self.assertIsNotNone(guard_bash.reason_for("git push", self._repo("main")))

    def test_pushing_a_protected_destination_is_denied_from_anywhere(self) -> None:
        root = self._repo("feature/x")
        for command in (
            "git push origin main",
            "git push origin HEAD:main",
            "git push origin feature/x:refs/heads/master",
            "git push --all origin",
            "git push --mirror origin",
        ):
            with self.subTest(command=command):
                self.assertIsNotNone(guard_bash.reason_for(command, root))

    def test_pushing_a_feature_branch_stays_allowed(self) -> None:
        root = self._repo("feature/crew-generator")
        for command in (
            "git push",
            "git push -u origin feature/crew-generator",
            "git push origin HEAD",
        ):
            with self.subTest(command=command):
                self.assertIsNone(guard_bash.reason_for(command, root))

    def test_pushing_a_feature_branch_while_sitting_on_main_stays_allowed(self) -> None:
        """The destination is what matters, not where HEAD happens to be."""
        self.assertIsNone(
            guard_bash.reason_for("git push origin feature/crew-generator", self._repo("main"))
        )


class ValidationTests(unittest.TestCase):
    def test_gdscript_paths_are_deterministic_and_existing_only(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "b.gd").write_text("extends Node\n", encoding="utf-8")
            (root / "a.gd").write_text("extends Node\n", encoding="utf-8")
            payload = {"tool_response": {"filePaths": ["b.gd", "missing.gd", "a.gd", "a.gd", "note.md"]}}
            self.assertEqual(validate_gdscript.gdscript_paths(payload, root), [root / "a.gd", root / "b.gd"])

    @mock.patch.object(validate_gdscript, "godot_command", return_value=None)
    @mock.patch.object(validate_gdscript, "gdtoolkit_command", return_value=None)
    def test_missing_optional_tools_fail_open(self, _gdtoolkit: mock.Mock, _godot: mock.Mock) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            script = root / "a.gd"
            script.write_text("extends Node\n", encoding="utf-8")
            self.assertEqual(validate_gdscript.validate([script], root), [])


class ToolDiscoveryTests(unittest.TestCase):
    def test_local_setting_is_one_trimmed_line_or_none(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertIsNone(hook_common.local_setting(root, "godot"))
            (root / ".agents" / "local").mkdir(parents=True)
            (root / ".agents" / "local" / "godot").write_text("  /opt/godot \n", encoding="utf-8")
            self.assertEqual(hook_common.local_setting(root, "godot"), "/opt/godot")

    def test_godot_comes_from_env_then_the_local_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            local_godot = root / "local-godot"
            env_godot = root / "env-godot"
            local_godot.write_text("", encoding="utf-8")
            env_godot.write_text("", encoding="utf-8")
            (root / ".agents" / "local").mkdir(parents=True)
            (root / ".agents" / "local" / "godot").write_text(str(local_godot), encoding="utf-8")
            with mock.patch.dict(os.environ, {"GODOT_BIN": ""}):
                self.assertEqual(hook_common.godot_command(root), str(local_godot))
            with mock.patch.dict(os.environ, {"GODOT_BIN": str(env_godot)}):
                self.assertEqual(hook_common.godot_command(root), str(env_godot))

    @mock.patch.object(hook_common, "executable_available", return_value=False)
    def test_gdtoolkit_falls_back_to_the_python_module(self, _available: mock.Mock) -> None:
        with mock.patch("importlib.util.find_spec", return_value=object()):
            self.assertEqual(
                hook_common.gdtoolkit_command("gdlint"), [sys.executable, "-m", "gdtoolkit.linter"]
            )
        with mock.patch("importlib.util.find_spec", return_value=None):
            self.assertIsNone(hook_common.gdtoolkit_command("gdformat"))


@unittest.skipIf(shutil.which("bash") is None, "bash is not available")
class RunnerTests(unittest.TestCase):
    """run.sh picks a working Python, caches it, and passes the hook's stdin through."""

    def _project(self, directory: str) -> Path:
        hooks = Path(directory) / ".agents" / "hooks"
        hooks.mkdir(parents=True)
        shutil.copy(HOOKS / "run.sh", hooks / "run.sh")
        (hooks / "echo_hook.py").write_text(
            "import sys\nsys.stdout.write('ran:' + sys.stdin.read())\n", encoding="utf-8"
        )
        return hooks

    def _run(self, hooks: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            # The resolved path: on Windows, a bare "bash" from Python starts WSL's bash in System32.
            [str(shutil.which("bash")), (hooks / "run.sh").as_posix(), "echo_hook.py"],
            input="payload", capture_output=True, text=True, env={**os.environ, **env},
        )

    def test_runs_the_hook_with_stdin_and_caches_the_interpreter(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            hooks = self._project(directory)
            result = self._run(hooks, {"PYTHON": Path(sys.executable).as_posix()})
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, "ran:payload")
            self.assertTrue((hooks.parent / "local" / "python").read_text(encoding="utf-8").strip())

    def test_a_cached_interpreter_is_used_first(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            hooks = self._project(directory)
            (hooks.parent / "local").mkdir()
            (hooks.parent / "local" / "python").write_text(Path(sys.executable).as_posix() + "\n", encoding="utf-8")
            result = self._run(hooks, {"PYTHON": "definitely-not-a-python"})
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, "ran:payload")


HEAD = "a" * 40
GREEN = [{"__typename": "CheckRun", "name": "test", "status": "COMPLETED", "conclusion": "SUCCESS"}]


def _verdict(verdict: str = "approve", sha: str = HEAD, when: str = "2026-01-01T00:00:00Z") -> dict:
    return {"createdAt": when, "body": f"Review notes.\n<!-- game-sdlc-review: {verdict} sha={sha} -->"}


def _ruling(sha: str = HEAD, when: str = "2026-01-03T00:00:00Z", verdict: str = "merge") -> dict:
    return {"createdAt": when, "body": f"Lead ruling.\n<!-- game-sdlc-lead-ruling: {verdict} sha={sha} -->"}


def _two_cycles(sha: str = "b" * 40) -> list[dict]:
    return [
        _verdict("request-changes", sha=sha, when="2026-01-01T00:00:00Z"),
        _verdict("request-changes", sha=sha, when="2026-01-02T00:00:00Z"),
    ]


class MergeGuardTests(unittest.TestCase):
    """`gh pr merge` into main needs the policy, green CI and an approving verdict on the head."""

    def _root(self, directory: str, allowed: bool | None) -> Path:
        root = Path(directory)
        if allowed is not None:
            (root / ".agents").mkdir()
            (root / ".agents" / "merge-policy.json").write_text(
                json.dumps({"agent_merges_to_main": allowed}), encoding="utf-8"
            )
        return root

    def _reason(self, command: str, allowed: bool | None, pr: dict | None) -> str | None:
        with tempfile.TemporaryDirectory() as directory:
            root = self._root(directory, allowed)
            result = mock.Mock(returncode=1 if pr is None else 0, stdout=json.dumps(pr or {}), stderr="")
            with mock.patch.object(merge_guard, "run", return_value=result) as run_mock:
                reason = merge_guard.merge_reason(command, root)
                self.last_command = run_mock.call_args[0][0] if run_mock.call_args else None
                return reason

    def _pr(self, **changes: object) -> dict:
        pr = {"baseRefName": "main", "headRefOid": HEAD, "statusCheckRollup": GREEN,
              "comments": [_verdict()], "reviews": []}
        pr.update(changes)
        return pr

    def test_finds_gh_pr_merge_with_env_prefixes_and_chains(self) -> None:
        self.assertEqual(merge_guard.gh_pr_merges("GH_TOKEN=x gh pr merge 12 --merge && echo ok"), [["12", "--merge"]])
        self.assertEqual(merge_guard.gh_pr_merges("gh pr view 12; git status"), [])
        self.assertEqual(merge_guard.gh_pr_merges("echo 'gh pr merge 3'"), [])

    def test_target_skips_option_values(self) -> None:
        self.assertEqual(merge_guard.merge_target(["--body", "x", "-R", "o/r", "42", "--merge"]), ("42", "o/r"))
        self.assertEqual(merge_guard.merge_target(["--repo=o/r", "--squash"]), (None, "o/r"))

    def test_allows_a_green_approved_merge_under_the_policy(self) -> None:
        self.assertIsNone(self._reason("gh pr merge 7 --merge --delete-branch", True, self._pr()))
        self.assertEqual(self.last_command[:4], ["gh", "pr", "view", "7"])

    def test_refuses_merges_to_main_without_the_policy(self) -> None:
        for allowed in (None, False):
            with self.subTest(allowed=allowed):
                self.assertIn("owner's job", self._reason("gh pr merge 7", allowed, self._pr()))

    def test_allows_merges_into_another_branch_without_the_policy(self) -> None:
        self.assertIsNone(self._reason("gh pr merge 7", None, self._pr(baseRefName="feature/x")))

    def test_refuses_failing_pending_or_missing_checks(self) -> None:
        cases = {
            "failure": [{"__typename": "CheckRun", "name": "test", "status": "COMPLETED", "conclusion": "FAILURE"}],
            "running": [{"__typename": "CheckRun", "name": "test", "status": "IN_PROGRESS", "conclusion": ""}],
            "pending status": [{"__typename": "StatusContext", "context": "ci", "state": "PENDING"}],
            "none": [],
        }
        for label, rollup in cases.items():
            with self.subTest(label):
                self.assertIn("CI", self._reason("gh pr merge 7", True, self._pr(statusCheckRollup=rollup)))

    def test_refuses_a_missing_stale_or_negative_verdict(self) -> None:
        cases = {
            "missing": [],
            "stale": [_verdict(sha="b" * 40)],
            "changes": [_verdict(), _verdict("request-changes", when="2026-01-02T00:00:00Z")],
        }
        for label, comments in cases.items():
            with self.subTest(label):
                self.assertIsNotNone(self._reason("gh pr merge 7", True, self._pr(comments=comments)))

    def test_a_later_approval_in_a_review_counts(self) -> None:
        pr = self._pr(
            comments=[_verdict("request-changes")],
            reviews=[{"submittedAt": "2026-01-03T00:00:00Z", "body": _verdict()["body"]}],
        )
        self.assertIsNone(self._reason("gh pr merge 7", True, pr))

    def test_a_lead_ruling_on_the_head_merges_after_two_cycles(self) -> None:
        """After the cap the lead decides; the fixes it pushed need no third review."""
        pr = self._pr(comments=[*_two_cycles(), _ruling()])
        self.assertIsNone(self._reason("gh pr merge 7", True, pr))

    def test_a_lead_ruling_needs_two_cycles_a_fresh_sha_and_the_right_word(self) -> None:
        cases = {
            "no review": [_ruling()],
            "one cycle": [_verdict("request-changes", sha="b" * 40), _ruling()],
            "stale ruling": [*_two_cycles(), _ruling(sha="c" * 40)],
            "lead approves": [*_two_cycles(), _ruling(verdict="approve")],
            "reviewer rules": [*_two_cycles(), _verdict("merge", when="2026-01-03T00:00:00Z")],
        }
        for label, comments in cases.items():
            with self.subTest(label):
                self.assertIsNotNone(self._reason("gh pr merge 7", True, self._pr(comments=comments)))

    def test_a_later_reviewer_verdict_overrides_a_ruling(self) -> None:
        later = _verdict("request-changes", when="2026-01-04T00:00:00Z")
        pr = self._pr(comments=[*_two_cycles(), _ruling(), later])
        self.assertIn("requests changes", self._reason("gh pr merge 7", True, pr))

    def test_admin_and_unreadable_pull_requests_are_refused(self) -> None:
        self.assertIn("--admin", self._reason("gh pr merge 7 --admin", True, self._pr()))
        self.assertIn("couldn't read", self._reason("gh pr merge 7", True, None))

    def test_commands_without_a_merge_never_call_gh(self) -> None:
        self.assertIsNone(self._reason("git status && gh pr list", True, self._pr()))
        self.assertIsNone(self.last_command)


class PreCommitTests(unittest.TestCase):
    def test_only_git_commit_is_selected(self) -> None:
        self.assertTrue(pre_commit_lint.is_git_commit("git commit -m test"))
        self.assertTrue(pre_commit_lint.is_git_commit("echo ok && git.exe commit"))
        self.assertFalse(pre_commit_lint.is_git_commit("git status"))
        self.assertFalse(pre_commit_lint.is_git_commit("echo 'git commit'"))
        self.assertFalse(pre_commit_lint.is_git_commit("echo git commit"))
        self.assertFalse(pre_commit_lint.is_git_commit('python -c "print(\'git commit\')"'))

    def test_environment_prefixed_and_indented_commits_are_selected(self) -> None:
        """The gate is the only thing enforcing lint and mirror freshness."""
        for command in (
            "GIT_EDITOR=true git commit -m test",
            "env FOO=1 git commit",
            "env -u GIT_EDITOR git commit",
            "git -c safe.directory=* commit -m test",
            "  git commit -m test",
            "\tgit commit --amend",
            "Write-Output ok\ngit commit -m test",
        ):
            with self.subTest(command=command):
                self.assertTrue(pre_commit_lint.is_git_commit(command))

    @mock.patch.object(pre_commit_lint, "run")
    def test_skill_check_operational_error_fails_open(self, run_mock: mock.Mock) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            script = root / ".agents" / "scripts" / "sync_skills.py"
            script.parent.mkdir(parents=True)
            script.write_text("", encoding="utf-8")
            run_mock.return_value = mock.Mock(returncode=2, stdout="", stderr="unavailable")
            self.assertIsNone(pre_commit_lint.check_skill_sync(root))

    @mock.patch.object(pre_commit_lint, "run")
    def test_skill_drift_blocks(self, run_mock: mock.Mock) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            script = root / ".agents" / "scripts" / "sync_skills.py"
            script.parent.mkdir(parents=True)
            script.write_text("", encoding="utf-8")
            run_mock.return_value = mock.Mock(returncode=1, stdout="stale", stderr="")
            self.assertEqual(pre_commit_lint.check_skill_sync(root), "stale")


class SkillSyncTests(unittest.TestCase):
    def test_banner_is_after_frontmatter(self) -> None:
        generated = sync_skills.inject_banner("---\nname: sample\n---\n\n# Title\n", ".claude/skills/sample/SKILL.md")
        self.assertIn("---\n\n> GENERATED MIRROR", generated)
        self.assertTrue(generated.endswith("# Title\n"))

    def test_invalid_source_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            sync_skills.inject_banner("# Missing frontmatter\n", "source")

    def test_invalid_source_returns_drift_exit_code(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / ".claude" / "skills" / "invalid" / "SKILL.md"
            source.parent.mkdir(parents=True)
            source.write_text("# Missing frontmatter\n", encoding="utf-8")
            with mock.patch.object(sync_skills, "repo_root", return_value=root), mock.patch.object(
                sys, "argv", ["sync_skills.py", "--check"]
            ):
                self.assertEqual(sync_skills.main(), 1)

    def test_missing_source_returns_operational_exit_code(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with mock.patch.object(sync_skills, "repo_root", return_value=root), mock.patch.object(
                sys, "argv", ["sync_skills.py", "--check"]
            ):
                self.assertEqual(sync_skills.main(), 2)


class RegistrationTests(unittest.TestCase):
    def test_codex_registration_has_exact_shared_entrypoints(self) -> None:
        hooks_path = REPO_ROOT / ".codex" / "hooks.json"
        data = json.loads(hooks_path.read_text(encoding="utf-8"))
        commands = [
            hook["command"]
            for groups in data["hooks"].values()
            for group in groups
            for hook in group["hooks"]
        ]
        entrypoints = [command.split()[-1] for command in commands]
        self.assertCountEqual(entrypoints, [
            "protect_paths.py",
            "guard_bash.py",
            "pre_commit_lint.py",
            "validate_gdscript.py",
        ])
        for command in commands:
            self.assertIn("safe.directory=*", command)
            self.assertIn("/.agents/hooks/run.sh", command)

    def test_claude_registration_has_exact_shared_entrypoints(self) -> None:
        settings_path = REPO_ROOT / ".claude" / "settings.json"
        data = json.loads(settings_path.read_text(encoding="utf-8"))
        hooks = [
            hook
            for groups in data["hooks"].values()
            for group in groups
            for hook in group["hooks"]
        ]
        commands = [hook["command"] for hook in hooks]
        entrypoints = [command.split()[-1] for command in commands]
        self.assertCountEqual(entrypoints, [
            "protect_paths.py",
            "guard_bash.py",
            "pre_commit_lint.py",
            "validate_gdscript.py",
        ])
        for hook in hooks:
            self.assertEqual(hook["shell"], "bash")
            self.assertIn('$CLAUDE_PROJECT_DIR/.agents/hooks/run.sh', hook["command"])

    def test_legacy_claude_hook_scripts_are_removed(self) -> None:
        legacy_root = REPO_ROOT / ".claude" / "hooks"
        for name in ("protect_paths.py", "guard_bash.py", "pre_commit_lint.py", "validate_gdscript.py"):
            self.assertFalse((legacy_root / name).exists())

    def test_three_roles_preserve_client_permission_boundaries(self) -> None:
        claude_tools = {
            "godot-developer.md": "tools: Read, Write, Edit, Glob, Grep, Bash",
            "godot-debugger.md": "tools: Read, Grep, Glob, Bash, Edit",
            "godot-reviewer.md": "tools: Read, Grep, Glob, Bash",
        }
        for filename, expected in claude_tools.items():
            text = (REPO_ROOT / ".claude" / "agents" / filename).read_text(encoding="utf-8")
            self.assertIn(expected, text)

        codex_sandboxes = {
            "godot-developer.toml": "workspace-write",
            "godot-debugger.toml": "workspace-write",
            "godot-reviewer.toml": "read-only",
        }
        for filename, expected in codex_sandboxes.items():
            text = (REPO_ROOT / ".codex" / "agents" / filename).read_text(encoding="utf-8")
            self.assertIn(f'sandbox_mode = "{expected}"', text)
            self.assertNotIn("model =", text)


if __name__ == "__main__":
    unittest.main()
