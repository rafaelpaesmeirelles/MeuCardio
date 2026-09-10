"""Local policy contracts only: no backend, database, API or CI execution."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
with patch.object(sys, "path", [str(ROOT / "scripts"), *sys.path]):
    SPEC = importlib.util.spec_from_file_location("ci_section_owner_policy", ROOT / "scripts/ci_backend_followup.py")
    POLICY = importlib.util.module_from_spec(SPEC)
    SPEC.loader.exec_module(POLICY)


class SectionOwnerDecisionTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.manifest = json.loads((ROOT / POLICY.SECTION_MANIFEST).read_text())
        self.manifest["pull_request"] = 999
        self.write_manifest()
        for path in ["docs/tct-section-visibility-20260910.md", "docs/ci/tct-section-visibility-owner-decision.md"]:
            target = self.root / path; target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("Local test fixture; not a test certificate.")
        self.head, self.candidate = "a" * 40, "a" * 40
        self.tree, self.pr_tree = "same-tree", "same-tree"
        self.pr = {"number": 999, "base": {"ref": "main", "repo": {"full_name": POLICY.SECTION_REPOSITORY}},
            "head": {"ref": POLICY.SECTION_BRANCH, "sha": self.head,
                     "repo": {"full_name": POLICY.SECTION_REPOSITORY}},
            "merged": False, "merge_commit_sha": None}
        self.associated = []
        self.calls = []

    def write_manifest(self):
        path = self.root / POLICY.SECTION_MANIFEST
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.manifest))

    def github(self, path):
        self.calls.append(path)
        if path.endswith("/pulls/999"): return self.pr
        if path.endswith(f"/commits/{self.candidate}/pulls"): return self.associated
        self.fail(f"Unexpected API request: {path}")

    def git(self, *args):
        if args == ("rev-parse", "HEAD"): return self.candidate
        if args == ("rev-parse", "HEAD^{tree}"): return self.tree
        if args == ("rev-parse", f"{self.head}^{{tree}}"): return self.pr_tree
        if args[0] == "diff": return "backend/app/api/knowledge_graph.py"
        self.fail(f"Unexpected git command: {args}")

    def decide(self, *, event="pull_request", number="999", head_ref=None):
        with patch.object(POLICY, "github", self.github), patch.object(POLICY, "git", self.git), \
             patch.object(POLICY.subprocess, "run") as commands, \
             patch.dict(os.environ, {"RUNNER_TEMP": str(self.root)}):
            result = POLICY.section_visibility_owner_decision(self.root, event=event, number=number,
                head_ref=POLICY.SECTION_BRANCH if head_ref is None else head_ref,
                repository=POLICY.SECTION_REPOSITORY)
            for call in commands.call_args_list:
                self.assertEqual(call.args[0][0], "git")
            return result

    def test_bootstrap_blocks_entrypoint_before_any_fallback_or_suite(self):
        self.manifest["pull_request"] = None; self.write_manifest()
        paths = self.root / "paths"; paths.write_text("backend/app/api/knowledge_graph.py\n")
        original = os.getcwd()
        try:
            with patch.object(sys, "argv", ["ci_backend_followup.py", "--repo-root", str(self.root),
                    "--paths-file", str(paths), "--manifest", "unused-pr918.json"]), \
                 patch.dict(os.environ, {"EVENT_NAME": "pull_request", "PR_NUMBER": "999",
                    "PR_HEAD_REF": POLICY.SECTION_BRANCH, "REPOSITORY": POLICY.SECTION_REPOSITORY}), \
                 patch.object(POLICY, "classify_paths") as fallback, patch.object(POLICY, "github") as api:
                with self.assertRaisesRegex(ValueError, "bootstrap awaits"):
                    POLICY.main()
                fallback.assert_not_called(); api.assert_not_called()
                self.assertFalse((self.root / "backend-no-ci-owner-decision.json").exists())
        finally:
            os.chdir(original)

    def test_sealed_pr_records_owner_decision_without_tests_or_certificate(self):
        result = self.decide()
        self.assertEqual(result.backend_mode, "authorized-no-backend-ci")
        self.assertEqual(result.focused_tests, ())
        self.assertNotIn("pr918", result.suite_key)
        artifact = json.loads((self.root / "backend-no-ci-owner-decision.json").read_text())
        self.assertEqual(artifact["pull_request"], 999)
        self.assertFalse(artifact["backend_ci_executed"])
        self.assertIsNone(artifact["test_certificate"])
        self.assertFalse(any("logs" in path or "actions/jobs" in path for path in self.calls))

    def test_sealed_exact_main_integration_including_squash_is_accepted(self):
        self.candidate = "b" * 40
        self.pr.update(merged=True, merge_commit_sha=self.candidate)
        self.associated = [{"number": 999}]
        result = self.decide(event="push", number="", head_ref="")
        self.assertEqual(result.backend_mode, "authorized-no-backend-ci")
        self.assertEqual(result.focused_tests, ())

    def test_missing_integration_association_blocks_by_merge_sha_or_exact_tree(self):
        self.candidate = "b" * 40
        self.pr.update(merged=True, merge_commit_sha=self.candidate)
        for merge_sha, tree in [(self.candidate, "different"), ("c" * 40, self.pr_tree)]:
            self.pr["merge_commit_sha"], self.tree = merge_sha, tree
            with self.subTest(merge_sha=merge_sha), self.assertRaisesRegex(ValueError, "evidence incomplete"):
                self.decide(event="push", number="", head_ref="")

    def test_api_failure_propagates_without_selecting_suite(self):
        with patch.object(POLICY, "git", self.git), \
             patch.object(POLICY, "github", side_effect=subprocess.CalledProcessError(1, ["gh", "api"])), \
             patch.object(POLICY, "classify_paths") as fallback:
            with self.assertRaises(subprocess.CalledProcessError):
                POLICY.section_visibility_owner_decision(self.root, event="pull_request", number="999",
                    head_ref=POLICY.SECTION_BRANCH, repository=POLICY.SECTION_REPOSITORY)
            fallback.assert_not_called()

    def test_identity_origin_and_missing_authorization_fail_closed(self):
        for field, value in [("base_sha", "0" * 40), ("repository", "other/repo"),
                             ("head_branch", "other-branch"), ("pull_request", 918)]:
            previous = self.manifest[field]; self.manifest[field] = value; self.write_manifest()
            with self.subTest(field=field), self.assertRaises(ValueError): self.decide()
            self.manifest[field] = previous
        self.manifest["authorization"]["instruction"] = ""; self.write_manifest()
        with self.assertRaises(ValueError): self.decide()

    def test_wrong_head_repo_or_stale_head_never_authorizes(self):
        self.pr["head"]["repo"]["full_name"] = "other/repo"
        with self.assertRaises(ValueError): self.decide()
        self.pr["head"]["repo"]["full_name"] = POLICY.SECTION_REPOSITORY
        self.candidate = "b" * 40
        with self.assertRaises(ValueError): self.decide()

    def test_unrelated_pr_and_future_different_main_tree_do_not_inherit(self):
        self.assertIsNone(self.decide(number="1000", head_ref="another-branch"))
        self.candidate = "c" * 40; self.tree = "future-tree"
        self.pr.update(merged=True, merge_commit_sha="b" * 40)
        self.assertIsNone(self.decide(event="push", number="", head_ref=""))

    def test_workflow_skips_both_test_jobs_and_keeps_explicit_gate_label(self):
        workflow = (ROOT / ".github/workflows/ci.yml").read_text()
        full = workflow.split("  backend:\n", 1)[1].split("runs-on:", 1)[0]
        focused = workflow.split("  backend-focused:\n", 1)[1].split("runs-on:", 1)[0]
        self.assertNotIn("authorized-no-backend-ci", full)
        self.assertNotIn("authorized-no-backend-ci", focused)
        self.assertIn("PR_HEAD_REF: ${{ github.event.pull_request.head.ref }}", workflow)
        self.assertIn("backend-risk-v1-authorized-no-backend-ci-tct-section-visibility-20260910", workflow)
        self.assertIn("backend CI não executado por decisão do responsável", workflow)


if __name__ == "__main__":
    unittest.main()
