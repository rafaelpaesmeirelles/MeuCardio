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


if __name__ == "__main__":
    unittest.main()
