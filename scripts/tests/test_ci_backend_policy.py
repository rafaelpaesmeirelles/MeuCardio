from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "scripts" / "ci_backend_policy.py"
SPEC = importlib.util.spec_from_file_location("ci_backend_policy", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
POLICY = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = POLICY
SPEC.loader.exec_module(POLICY)

REUSE_PATH = ROOT / "scripts" / "ci_backend_reuse.py"
REUSE_SPEC = importlib.util.spec_from_file_location("ci_backend_reuse", REUSE_PATH)
assert REUSE_SPEC is not None and REUSE_SPEC.loader is not None
REUSE = importlib.util.module_from_spec(REUSE_SPEC)
sys.modules[REUSE_SPEC.name] = REUSE
REUSE_SPEC.loader.exec_module(REUSE)


class BackendRiskPolicyTests(unittest.TestCase):
    def classify(self, *paths: str):
        return POLICY.classify_paths(paths, repo_root=ROOT)

    def test_frontend_only_skips_backend(self):
        decision = self.classify(
            "frontend/src/pages/Agenda.tsx",
            "frontend/src/styles/shell.css",
        )
        self.assertEqual(decision.backend_mode, "skip")
        self.assertEqual(decision.focused_tests, ())

    def test_frontend_and_docs_still_skip_backend(self):
        decision = self.classify("frontend/src/App.tsx", "docs/release.md", "README.md")
        self.assertEqual(decision.backend_mode, "skip")

    def test_low_risk_backend_with_related_test_is_focused(self):
        decision = self.classify("backend/app/services/mail360.py")
        self.assertEqual(decision.backend_mode, "focused")
        self.assertIn("tests/test_mail360_client.py", decision.focused_tests)
        self.assertIn("tests/test_readiness.py", decision.focused_tests)
        self.assertIn("-focused-", decision.suite_key)

    def test_direct_backend_test_change_is_focused(self):
        decision = self.classify("backend/tests/test_mail360_client.py")
        self.assertEqual(decision.backend_mode, "focused")
        self.assertIn("tests/test_mail360_client.py", decision.focused_tests)

    def test_migration_forces_full_backend(self):
        decision = self.classify(
            "backend/migrations/versions/f93s20260901_disable_reserved_smoke_agenda.py"
        )
        self.assertEqual(decision.backend_mode, "full")
        self.assertTrue(any(reason.startswith("infra:") for reason in decision.reasons))

    def test_auth_and_security_force_full_backend(self):
        for path in (
            "backend/app/api/auth.py",
            "backend/app/core/security.py",
            "backend/tests/test_password_reset_flow.py",
        ):
            with self.subTest(path=path):
                self.assertEqual(self.classify(path).backend_mode, "full")

    def test_clinical_data_and_models_force_full_backend(self):
        for path in (
            "content/Hipertensao/item.md",
            "doencas/metadados.json",
            "backend/app/models/patient.py",
            "backend/app/api/agenda_integrada.py",
            "backend/app/api/search.py",
            "backend/app/services/clinical_text.py",
            "backend/app/api/cardiovascular_exam_ai.py",
            "backend/app/commands/reconcile_content.py",
        ):
            with self.subTest(path=path):
                self.assertEqual(self.classify(path).backend_mode, "full")

    def test_infrastructure_and_policy_force_full_backend(self):
        for path in (
            ".github/workflows/ci.yml",
            "docker-compose.prod.yml",
            "deploy.sh",
            "ops/remote-deploy-entrypoint.sh",
            "scripts/ci_backend_policy.py",
            "backend/requirements.txt",
        ):
            with self.subTest(path=path):
                self.assertEqual(self.classify(path).backend_mode, "full")

    def test_unknown_path_fails_closed(self):
        decision = self.classify("native-release.config")
        self.assertEqual(decision.backend_mode, "full")
        self.assertIn("unknown-path:native-release.config", decision.reasons)

    def test_empty_change_set_fails_closed(self):
        self.assertEqual(self.classify().backend_mode, "full")

    def test_unmapped_backend_module_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "backend" / "tests").mkdir(parents=True)
            (root / "backend" / "tests" / "test_readiness.py").write_text(
                "def test_ready(): assert True\n", encoding="utf-8"
            )
            decision = POLICY.classify_paths(
                ["backend/app/services/sem_teste_relacionado.py"], repo_root=root
            )
        self.assertEqual(decision.backend_mode, "full")
        self.assertTrue(any(reason.startswith("unmapped-backend:") for reason in decision.reasons))

    def test_deleted_or_renamed_backend_source_fails_closed_even_if_a_test_mentions_it(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tests = root / "backend" / "tests"
            tests.mkdir(parents=True)
            (tests / "test_readiness.py").write_text(
                "def test_ready(): assert True\n", encoding="utf-8"
            )
            (tests / "test_removed_service.py").write_text(
                "from app.services import removed_service\n", encoding="utf-8"
            )
            decision = POLICY.classify_paths(
                ["backend/app/services/removed_service.py"], repo_root=root
            )
        self.assertEqual(decision.backend_mode, "full")
        self.assertIn(
            "unmapped-backend:backend/app/services/removed_service.py",
            decision.reasons,
        )

    def test_suite_key_is_deterministic_and_test_set_sensitive(self):
        first = self.classify("backend/app/services/mail360.py")
        second = self.classify("backend/app/services/mail360.py")
        other = self.classify("backend/tests/test_corvia_mail.py")
        self.assertEqual(first.suite_key, second.suite_key)
        self.assertNotEqual(first.suite_key, other.suite_key)

    def test_github_outputs_are_single_line(self):
        decision = self.classify("backend/app/services/mail360.py")
        for value in decision.github_outputs().values():
            self.assertNotIn("\n", value)
            self.assertNotIn("\r", value)


class WorkflowPolicyContractTests(unittest.TestCase):
    def test_ci_has_risk_gate_and_exact_suite_certificate(self):
        workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        self.assertIn("backend-risk-policy:", workflow)
        self.assertIn("backend-focused:", workflow)
        self.assertIn("backend-risk-gate:", workflow)
        self.assertIn("Backend suite certificate", workflow)
        self.assertIn("group: corvia-ci-${{ github.event.pull_request.head.sha || github.sha }}", workflow)
        self.assertIn("reuse_backend", workflow)
        self.assertNotIn("single-use agenda", workflow.casefold())
        for critical_full_gate in (
            "Verify migration command is idempotent",
            "Run pytest",
            "Exercise live HTTP release flow",
            "Prove PostgreSQL backup and restore",
        ):
            self.assertIn(critical_full_gate, workflow)

    def test_deploy_requires_backend_risk_gate_from_ci(self):
        workflow = (ROOT / ".github" / "workflows" / "deploy-production.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("Backend risk gate", workflow)
        self.assertIn("ci_run_marker", workflow)
        for mandatory_workflow in (
            "CI",
            "RC2 Acceptance — Canonical CorVIA",
            "Visual QA — Clinical OS",
            "Corpus database reconciliation",
            "Corpus inventory",
            "Deep functional inventory and public apps",
        ):
            self.assertIn(mandatory_workflow, workflow)
        for public_certificate in (
            "/api/version",
            "/api/health",
            "/api/ready",
            "validate_public_app_artifacts.py",
            "--retired android windows",
        ):
            self.assertIn(public_certificate, workflow)


class BackendSuiteReuseTests(unittest.TestCase):
    sha = "1" * 40
    suite = "backend-risk-v1-focused-deadbeef"

    def payload(
        self,
        *,
        sha: str | None = None,
        job_name: str = "Backend focused tests",
        job_status: str = "completed",
        job_conclusion: str = "success",
        step_name: str | None = None,
        step_status: str = "completed",
        step_conclusion: str = "success",
    ):
        return {
            "jobs": [
                {
                    "name": job_name,
                    "head_sha": sha or self.sha,
                    "status": job_status,
                    "conclusion": job_conclusion,
                    "steps": [
                        {
                            "name": step_name or f"Backend suite certificate {self.suite}",
                            "status": step_status,
                            "conclusion": step_conclusion,
                        }
                    ],
                }
            ]
        }

    def reusable(self, payload, *, job_name="Backend focused tests"):
        return REUSE.has_reusable_suite(
            payload,
            candidate_sha=self.sha,
            job_name=job_name,
            suite_key=self.suite,
        )

    def test_exact_sha_job_and_suite_certificate_are_reusable(self):
        self.assertTrue(self.reusable(self.payload()))

    def test_different_sha_is_not_reusable(self):
        self.assertFalse(self.reusable(self.payload(sha="2" * 40)))

    def test_skipped_or_failed_backend_job_is_not_reusable(self):
        for status, conclusion in (
            ("completed", "skipped"),
            ("completed", "failure"),
            ("in_progress", None),
        ):
            with self.subTest(status=status, conclusion=conclusion):
                self.assertFalse(
                    self.reusable(
                        self.payload(job_status=status, job_conclusion=conclusion)
                    )
                )

    def test_wrong_suite_or_job_class_is_not_reusable(self):
        wrong_step = f"Backend suite certificate {self.suite}-other"
        self.assertFalse(self.reusable(self.payload(step_name=wrong_step)))
        self.assertFalse(self.reusable(self.payload(job_name="Backend tests")))

    def test_green_ci_without_backend_certificate_is_not_reusable(self):
        payload = {
            "jobs": [
                {
                    "name": "Frontend build",
                    "head_sha": self.sha,
                    "status": "completed",
                    "conclusion": "success",
                    "steps": [],
                }
            ]
        }
        self.assertFalse(self.reusable(payload))

    def test_certificate_step_must_itself_be_green(self):
        self.assertFalse(
            self.reusable(self.payload(step_conclusion="failure"))
        )


class AuthorizedFollowupTests(unittest.TestCase):
    def setUp(self):
        import json
        self.manifest = json.loads((ROOT / "docs/ci/pr918-authorized-backend-followup.json").read_text())
        self.job = {"id": self.manifest["baseline_job_id"], "run_id": self.manifest["baseline_run_id"],
                    "head_sha": self.manifest["baseline_sha"], "name": "Backend tests", "status": "completed",
                    "conclusion": "failure", "steps": [{"name": "Run pytest", "status": "completed"}]}
        self.log = ("================ short test summary info ================\n"
                    "FAILED tests/test_readiness.py::test_probe - AssertionError\n"
                    "============= 1 failed, 30 passed in 5.20s =============\n")

    def decide(self, paths=None, **kwargs):
        return POLICY.classify_authorized_followup(paths or ["backend/tests/test_readiness.py"],
            repo_root=ROOT, manifest=self.manifest, baseline_job=kwargs.get("job", self.job),
            baseline_log=kwargs.get("log", self.log))

    def test_all_failed_modules_impacts_and_money_regressions_are_mandatory(self):
        result = self.decide(["deploy.sh"])
        self.assertEqual(result.backend_mode, "authorized-followup")
        self.assertIn("backend/tests/test_readiness.py", result.focused_tests)
        self.assertIn("backend/tests/test_deploy_rollback_window.py", result.focused_tests)
        for required in POLICY.REQUIRED_FOLLOWUP_FINANCIAL_TESTS:
            self.assertIn(required, result.focused_tests)
        self.assertIn("not-a-passing-full-suite-certificate", result.reasons)
        self.assertNotEqual(result.suite_key, "backend-risk-v1-full")

    def test_real_actions_timestamps_and_plain_pytest_summary_are_supported(self):
        log = ("2026-09-10T00:25:41.1Z = short test summary info =\n"
               "2026-09-10T00:25:41.2Z FAILED tests/test_readiness.py::test_probe - AssertionError\n"
               "2026-09-10T00:25:41.3Z 1 failed, 30 passed, 3 skipped, 3 warnings in 1821.92s (0:30:21)\n")
        result = self.decide(log=log)
        self.assertIn("baseline-failed-module:backend/tests/test_readiness.py", result.reasons)

    def test_pending_cancelled_wrong_sha_and_wrong_job_cannot_authorize_followup(self):
        for change in [{"status": "in_progress"}, {"conclusion": "cancelled"}, {"head_sha": "0"*40},
                       {"id": 1}, {"run_id": 1}, {"steps": []}]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.decide(job={**self.job, **change})

    def test_interrupted_or_incompletely_reported_failure_inventory_is_rejected(self):
        for log in ["tests interrupted", self.log.replace("1 failed", "2 failed"),
                    self.log.replace("tests/test_readiness.py", "../unsafe.py")]:
            with self.subTest(log=log), self.assertRaises(ValueError):
                self.decide(log=log)

    def test_every_failed_module_and_collection_error_is_selected(self):
        log = self.log.replace("1 failed, 30 passed", "1 failed, 1 error, 30 passed").replace(
            "============= 1 failed", "ERROR tests/test_billing_portal.py - ImportError\n============= 1 failed")
        result = self.decide(log=log)
        self.assertIn("baseline-failed-module:backend/tests/test_billing_portal.py", result.reasons)

    def test_unmapped_path_or_missing_failed_test_blocks_without_running_full(self):
        for paths, log in [(["ops/unknown-new-release.sh"], self.log),
                           (["backend/tests/test_readiness.py"], self.log.replace("test_readiness", "test_deleted_failure"))]:
            with self.subTest(paths=paths), self.assertRaises(ValueError):
                self.decide(paths, log=log)

    def test_exact_pr_head_or_associated_identical_main_tree_only(self):
        spec = importlib.util.spec_from_file_location("ci_backend_followup", ROOT / "scripts/ci_backend_followup.py")
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        pr = {"number": 918, "base": {"ref": "main"}, "head": {"sha": "a"*40},
              "merged": True, "merge_commit_sha": "b"*40}
        common = dict(manifest=self.manifest, pr=pr, candidate_tree="tree", pr_tree="tree")
        self.assertTrue(module.authorized_context(**common, event="pull_request", number="918", candidate="a"*40, associated=[]))
        self.assertFalse(module.authorized_context(**common, event="pull_request", number="919", candidate="a"*40, associated=[]))
        self.assertTrue(module.authorized_context(**common, event="push", number="", candidate="b"*40, associated=[{"number":918}]))
        self.assertFalse(module.authorized_context(**common, event="push", number="", candidate="b"*40, associated=[]))
        self.assertFalse(module.authorized_context(**{**common,"candidate_tree":"later-tree"}, event="push", number="", candidate="b"*40, associated=[{"number":918}]))
        self.assertFalse(module.authorized_context(**common, event="push", number="", candidate="c"*40, associated=[{"number":918}]))

    def test_exact_squash_tree_keeps_pr_baseline_ancestry_without_requiring_merge_ancestry(self):
        import os
        import subprocess
        spec = importlib.util.spec_from_file_location("ci_backend_followup_squash", ROOT / "scripts/ci_backend_followup.py")
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        original = os.getcwd()
        with tempfile.TemporaryDirectory() as directory:
            try:
                os.chdir(directory)
                def command(*args):
                    return subprocess.check_output(["git", *args], text=True, stderr=subprocess.DEVNULL).strip()
                command("init", "-q", "-b", "main")
                command("config", "user.name", "CI fixture")
                command("config", "user.email", "ci-fixture@example.invalid")
                Path("base.txt").write_text("base")
                command("add", "."); command("commit", "-qm", "base")
                command("checkout", "-qb", "pr918")
                Path("app.txt").write_text("initial full candidate")
                command("add", "."); command("commit", "-qm", "full baseline")
                baseline = command("rev-parse", "HEAD")
                Path("app.txt").write_text("focused fix")
                command("commit", "-qam", "follow-up")
                head = command("rev-parse", "HEAD")
                command("checkout", "-q", "main")
                command("merge", "--squash", "pr918")
                command("commit", "-qm", "squashed integration")
                candidate = command("rev-parse", "HEAD")
                self.assertEqual(command("rev-parse", "HEAD^{tree}"), command("rev-parse", f"{head}^{{tree}}"))
                self.assertEqual(subprocess.run(["git", "merge-base", "--is-ancestor", baseline, candidate]).returncode, 1)
                self.assertEqual(module.changed_followup_paths(baseline, head, candidate), ["app.txt"])
            finally:
                os.chdir(original)

    def test_workflow_keeps_operational_gates_and_never_reuses_full_for_followup(self):
        workflow = (ROOT / ".github/workflows/ci.yml").read_text()
        self.assertIn('[[ "$BACKEND_MODE" != "authorized-followup" ]] || exit 0', workflow)
        self.assertIn('PYTHONPATH=backend python -m pytest -q --tb=short "${tests[@]}"', workflow)
        self.assertIn("Backend suite certificate ${{ needs.backend-risk-policy.outputs.suite_key }}", workflow)
        for gate in ["Verify migration command is idempotent", "Exercise live HTTP release flow", "Prove PostgreSQL backup and restore"]:
            self.assertIn(gate, workflow)


class AuthorizedNoBackendCITests(unittest.TestCase):
    def setUp(self):
        import json
        self.manifest = json.loads((ROOT / "docs/ci/pr918-authorized-backend-followup.json").read_text())
        self.job = {"id":102689862687, "run_id":34418893616,
                    "head_sha":"eddcb80d3fc99e7c25b330c943637f49691826fa",
                    "name":"Backend tests", "status":"completed", "conclusion":"failure"}

    def decide(self, manifest=None, job=None):
        return POLICY.classify_authorized_no_backend_ci(["backend/app/core/config.py"],
            repo_root=ROOT, manifest=manifest or self.manifest, baseline_job=job or self.job)

    def test_owner_decision_selects_no_tests_and_preserves_failed_full(self):
        decision = self.decide()
        self.assertEqual(decision.backend_mode, "authorized-no-backend-ci")
        self.assertEqual(decision.focused_tests, ())
        self.assertIn("not-a-full-or-focused-test-certificate", decision.reasons)
        self.assertIn("backend CI não executado por decisão do responsável", decision.reasons)
        self.assertNotEqual(decision.suite_key, "backend-risk-v1-full")

    def test_missing_instruction_wrong_origin_or_changed_result_are_rejected(self):
        import copy
        for change in ["instruction", "origin", "result", "evidence"]:
            manifest=copy.deepcopy(self.manifest)
            if change == "instruction": manifest["authorization"]["instruction"]=""
            if change == "origin": manifest["functional_baseline_sha"]="0"*40
            if change == "result": manifest["initial_full_result"]["conclusion"]="success"
            if change == "evidence": manifest["local_evidence"]=["docs/missing-owner-evidence.md"]
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.decide(manifest=manifest)

    def test_baseline_metadata_cannot_claim_success_or_another_job(self):
        for change in [{"conclusion":"success"},{"status":"in_progress"},{"id":1},{"run_id":1},{"head_sha":"0"*40}]:
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.decide(job={**self.job,**change})

    def test_metadata_only_entrypoint_never_downloads_logs_or_starts_tests(self):
        import json,os
        from unittest.mock import patch
        spec=importlib.util.spec_from_file_location("ci_no_backend_entrypoint",ROOT/"scripts/ci_backend_followup.py")
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        candidate="a"*40
        pr={"number":918,"base":{"ref":"main"},"head":{"sha":candidate}}
        calls=[]
        def github(path, **kwargs):
            calls.append(path)
            if path.endswith("/pulls/918"): return pr
            if path.endswith("/actions/jobs/102689862687"): return self.job
            self.fail(f"Unexpected remote evidence call: {path}")
        def git(*args):
            if args == ("rev-parse","HEAD"): return candidate
            if args[0] == "rev-parse": return "same-tree"
            if args[0] == "diff": return "docs/ci/pr918-no-backend-ci-owner-decision.md"
            self.fail(f"Unexpected git call: {args}")
        original=os.getcwd()
        with tempfile.TemporaryDirectory() as directory:
            paths=Path(directory)/"paths";paths.write_text("backend/app/core/config.py\n")
            output=Path(directory)/"output"
            argv=["ci_backend_followup.py","--paths-file",str(paths),"--repo-root",str(ROOT),
                  "--manifest",str(ROOT/"docs/ci/pr918-authorized-backend-followup.json"),"--github-output",str(output)]
            try:
                with patch.object(sys,"argv",argv), patch.dict(os.environ,{"EVENT_NAME":"pull_request","PR_NUMBER":"918","REPOSITORY":"rafaelpaesmeirelles/MeuCardio","RUNNER_TEMP":directory}), \
                     patch.object(module,"github",github), patch.object(module,"git",git), patch.object(module.subprocess,"run") as commands, patch("builtins.print"):
                    self.assertEqual(module.main(),0)
                    for call in commands.call_args_list:
                        self.assertEqual(call.args[0][0],"git")
                self.assertIn("backend_mode=authorized-no-backend-ci",output.read_text())
                evidence=json.loads((Path(directory)/"backend-no-ci-owner-decision.json").read_text())
                self.assertFalse(evidence["backend_ci_executed"])
                self.assertIsNone(evidence["test_certificate"])
                self.assertEqual(evidence["baseline_conclusion"],"failure")
                self.assertFalse(any("/logs" in call for call in calls))
            finally:
                os.chdir(original)

    def test_incomplete_main_association_never_falls_back_to_backend_tests(self):
        import os
        from unittest.mock import patch
        spec = importlib.util.spec_from_file_location("ci_no_backend_integration", ROOT / "scripts/ci_backend_followup.py")
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        candidate, head = "b" * 40, "a" * 40
        original = os.getcwd()
        with tempfile.TemporaryDirectory() as directory:
            paths = Path(directory) / "paths"; paths.write_text("backend/app/core/config.py\n")
            output = Path(directory) / "output"
            argv = ["ci_backend_followup.py", "--paths-file", str(paths), "--repo-root", str(ROOT),
                    "--manifest", str(ROOT / "docs/ci/pr918-authorized-backend-followup.json"),
                    "--github-output", str(output)]
            try:
                for merge_sha, candidate_tree in [(candidate, "different-tree"), ("c" * 40, "pr-tree")]:
                    pr = {"number": 918, "base": {"ref": "main"}, "head": {"sha": head},
                          "merged": True, "merge_commit_sha": merge_sha}
                    def github(path, **kwargs):
                        if path.endswith("/pulls/918"): return pr
                        if path.endswith(f"/commits/{candidate}/pulls"): return []
                        self.fail(f"Unexpected GitHub request: {path}")
                    def git(*args):
                        if args == ("rev-parse", "HEAD"): return candidate
                        if args == ("rev-parse", "HEAD^{tree}"): return candidate_tree
                        if args == ("rev-parse", f"{head}^{{tree}}"): return "pr-tree"
                        self.fail(f"Unexpected git request: {args}")
                    # This fixture exercises PR918 only. New scoped decisions
                    # have independent owner-decision and real-gate-shell tests.
                    with self.subTest(merge_sha=merge_sha, candidate_tree=candidate_tree), \
                         patch.object(sys, "argv", argv), \
                         patch.dict(os.environ, {"EVENT_NAME": "push", "PR_NUMBER": "", "REPOSITORY": "rafaelpaesmeirelles/MeuCardio"}), \
                         patch.object(module, "github", github), patch.object(module, "git", git), \
                         patch.object(module.subprocess, "run"), patch.object(module, "classify_paths") as fallback, \
                         patch.object(module, "scoped_owner_decision", return_value=None), \
                         patch.object(module, "section_visibility_owner_decision", return_value=None), \
                         patch.object(module, "editorial_classification_owner_decision", return_value=None), \
                         patch.object(module, "feature_discovery_owner_decision", return_value=None), \
                         patch.object(module, "universal_favorites_owner_decision", return_value=None), \
                         patch.object(module, "publication_http_retry_owner_decision", return_value=None), \
                         patch.object(module, "classify_authorized_no_backend_ci") as waiver:
                        with self.assertRaisesRegex(ValueError, "integration evidence is incomplete"):
                            module.main()
                        fallback.assert_not_called()
                        waiver.assert_not_called()
                        self.assertFalse(output.exists())
            finally:
                os.chdir(original)

    def test_workflow_requires_both_backend_jobs_skipped_and_skips_ci_policy_tests(self):
        workflow=(ROOT/".github/workflows/ci.yml").read_text()
        self.assertIn("if: steps.classify.outputs.backend_mode != 'authorized-no-backend-ci'",workflow)
        section=workflow.split("authorized-no-backend-ci)",1)[1].split(";;",1)[0]
        self.assertIn('"$FULL_RESULT" == "skipped"',section)
        self.assertIn('"$FOCUSED_RESULT" == "skipped"',section)
        self.assertIn('"$REUSE_BACKEND" != "true"',section)
        self.assertIn("backend CI não executado por decisão do responsável",section)
        self.assertIn("pull-requests: read",workflow)


if __name__ == "__main__":
    unittest.main()
