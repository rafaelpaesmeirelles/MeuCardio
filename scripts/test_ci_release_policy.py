from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import ci_release_policy as policy


SHA = {
    "merge": "a" * 40,
    "base": "b" * 40,
    "head": "c" * 40,
    "tree": "d" * 40,
}


class ClassificationTests(unittest.TestCase):
    def classify(self, *changes: policy.Change) -> policy.Classification:
        return policy.classify_changes(list(changes))

    def test_only_docs_skip_backend(self):
        result = self.classify(
            policy.Change("added", "docs/release.md"),
            policy.Change("modified", "README.md"),
        )
        self.assertEqual(result.mode, "skip")
        self.assertEqual(result.targeted_tests, ())

    def test_frontend_changes_run_every_discovered_backend_contract(self):
        result = self.classify(
            policy.Change("modified", "frontend/src/App.tsx"),
            policy.Change("added", "docs/release.md"),
        )
        expected = policy.discover_frontend_contract_tests(Path.cwd())
        self.assertEqual(result.mode, "targeted")
        self.assertEqual(result.targeted_tests, expected)
        self.assertEqual(expected, policy.FRONTEND_CONTRACT_TESTS)
        self.assertEqual(len(expected), 32)
        self.assertIn("backend/tests/test_home_visual_contract.py", result.targeted_tests)
        self.assertGreater(len(result.targeted_tests), 20)

    def test_frontend_delete_and_rename_are_targeted(self):
        cases = (
            policy.Change("removed", "frontend/src/legacy.tsx"),
            policy.Change("renamed", "frontend/src/new.tsx", "frontend/src/old.tsx"),
        )
        for change in cases:
            with self.subTest(change=change):
                self.assertEqual(self.classify(change).mode, "targeted")

    def test_frontend_without_provable_contract_discovery_is_full(self):
        with tempfile.TemporaryDirectory() as directory:
            result = policy.classify_changes(
                [policy.Change("modified", "frontend/src/App.tsx")],
                repository_root=Path(directory),
            )
        self.assertEqual(result.mode, "full")
        self.assertIn("not provable", result.reason)

    def test_isolated_test_modules_are_targeted(self):
        result = self.classify(
            policy.Change("modified", "backend/tests/test_health.py"),
            policy.Change("added", "backend/tests/api/test_login.py"),
            policy.Change("modified", "docs/testing.md"),
        )
        self.assertEqual(result.mode, "targeted")
        self.assertEqual(
            result.targeted_tests,
            ("backend/tests/api/test_login.py", "backend/tests/test_health.py"),
        )

    def test_runtime_scientific_and_operational_paths_are_full(self):
        paths = (
            "backend/app/main.py",
            "backend/migrations/versions/new.py",
            "backend/data/apresentacoes_comerciais.json",
            "content/evidencia.json",
            "doencas/metadados.json",
            "scripts/feature_inventory.py",
            "scripts/audit_tudo_com_tudo.py",
            "ops/remote-deploy-entrypoint.sh",
            "infra/Caddyfile",
            ".github/workflows/ci.yml",
        )
        for path in paths:
            with self.subTest(path=path):
                self.assertEqual(self.classify(policy.Change("modified", path)).mode, "full")

    def test_deletions_and_non_benign_renames_are_full(self):
        cases = (
            policy.Change("removed", "backend/tests/test_removed.py"),
            policy.Change(
                "renamed", "backend/tests/test_new.py", "backend/tests/test_old.py"
            ),
            policy.Change("removed", "backend/app/legacy.py"),
        )
        for change in cases:
            with self.subTest(change=change):
                self.assertEqual(self.classify(change).mode, "full")

    def test_conftest_fixtures_and_helpers_are_full(self):
        paths = (
            "backend/conftest.py",
            "backend/tests/conftest.py",
            "backend/tests/fixtures/case.json",
            "backend/tests/helpers.py",
            "backend/tests/test_data.json",
        )
        for path in paths:
            with self.subTest(path=path):
                self.assertEqual(self.classify(policy.Change("modified", path)).mode, "full")

    def test_benign_rename_remains_skip(self):
        result = self.classify(
            policy.Change("renamed", "docs/current.md", "docs/legacy.md")
        )
        self.assertEqual(result.mode, "skip")

    def test_empty_diff_fails_closed(self):
        self.assertEqual(self.classify().mode, "full")

    def test_git_name_status_parser_preserves_rename_and_delete(self):
        raw = (
            b"M\0backend/tests/test_a.py\0"
            b"D\0backend/tests/test_old.py\0"
            b"R100\0frontend/old.tsx\0frontend/new.tsx\0"
        )
        self.assertEqual(
            policy.parse_git_changes(raw),
            [
                policy.Change("modified", "backend/tests/test_a.py"),
                policy.Change("removed", "backend/tests/test_old.py"),
                policy.Change("renamed", "frontend/new.tsx", "frontend/old.tsx"),
            ],
        )

    def test_git_and_github_change_records_have_same_digest(self):
        git_changes = policy.parse_git_changes(
            b"M\0backend/tests/test_a.py\0R100\0frontend/a.tsx\0frontend/b.tsx\0"
        )
        github_changes = policy.parse_github_changes(
            [
                {"status": "modified", "filename": "backend/tests/test_a.py"},
                {
                    "status": "renamed",
                    "filename": "frontend/b.tsx",
                    "previous_filename": "frontend/a.tsx",
                },
            ]
        )
        self.assertEqual(policy.changes_digest(git_changes), policy.changes_digest(github_changes))


class ReuseProofTests(unittest.TestCase):
    def fixtures(self, *, completed_at: str = "2026-09-01T11:59:00Z"):
        repository = "rafaelpaesmeirelles/MeuCardio"
        pull = {
            "number": 797,
            "merged_at": "2026-09-01T12:00:00Z",
            "merge_commit_sha": SHA["merge"],
            "base": {
                "ref": "main",
                "sha": SHA["base"],
                "repo": {"full_name": repository},
            },
            "head": {
                "ref": "feature",
                "sha": SHA["head"],
                "repo": {"id": 123},
            },
        }
        merge = {
            "parents": [{"sha": SHA["base"]}, {"sha": SHA["head"]}],
            "commit": {"tree": {"sha": SHA["tree"]}},
        }
        head = {"commit": {"tree": {"sha": SHA["tree"]}}}
        workflow = {
            "id": 42,
            "name": "CI",
            "path": ".github/workflows/ci.yml",
            "state": "active",
        }
        run = {
            "id": 99,
            "run_attempt": 1,
            "created_at": "2026-09-01T11:30:00Z",
            "completed_at": completed_at,
            "status": "completed",
            "conclusion": "success",
            "name": "CI",
            "path": ".github/workflows/ci.yml",
            "workflow_id": 42,
            "event": "pull_request",
            "head_sha": SHA["head"],
            "head_branch": "feature",
            "head_repository": {"id": 123},
        }
        return repository, pull, merge, head, workflow, run

    def test_ci_must_finish_before_merge(self):
        repository, pull, merge, head, workflow, run = self.fixtures()
        selected_pull, selected_run = policy.select_reusable_ci_run(
            merge=merge,
            pulls=[pull],
            head=head,
            runs=[run],
            workflow=workflow,
            repository=repository,
            merge_sha=SHA["merge"],
        )
        self.assertEqual(selected_pull["number"], 797)
        self.assertEqual(selected_run["id"], 99)

    def test_ci_completed_after_merge_is_rejected(self):
        repository, pull, merge, head, workflow, run = self.fixtures(
            completed_at="2026-09-01T12:01:00Z"
        )
        with self.assertRaisesRegex(policy.PolicyError, "completed after merge"):
            policy.select_reusable_ci_run(
                merge=merge,
                pulls=[pull],
                head=head,
                runs=[run],
                workflow=workflow,
                repository=repository,
                merge_sha=SHA["merge"],
            )

    def test_wrong_workflow_id_is_rejected(self):
        repository, pull, merge, head, workflow, run = self.fixtures()
        run["workflow_id"] = 999
        with self.assertRaises(policy.TransientPolicyError):
            policy.select_reusable_ci_run(
                merge=merge,
                pulls=[pull],
                head=head,
                runs=[run],
                workflow=workflow,
                repository=repository,
                merge_sha=SHA["merge"],
            )

    def test_attestation_recomputes_targeted_policy(self):
        repository, pull, _merge, head, _workflow, run = self.fixtures()
        changes = [policy.Change("modified", "backend/tests/test_health.py")]
        classification = policy.classify_changes(changes)
        attestation = {
            "schema": policy.ATTESTATION_SCHEMA,
            "repository": repository,
            "pr_number": 797,
            "base_sha": SHA["base"],
            "head_sha": SHA["head"],
            "tested_tree": SHA["tree"],
            "backend_mode": "targeted",
            "targeted_tests": ["backend/tests/test_health.py"],
            "changes_digest": classification.changes_digest,
            "backend_result": "success",
            "frontend_result": "success",
            "run_id": 99,
            "run_attempt": 1,
        }
        jobs = [
            {"name": "Detect backend risk", "conclusion": "success"},
            {"name": "Backend tests", "conclusion": "success"},
            {"name": "Frontend build", "conclusion": "success"},
            {"name": "CI policy", "conclusion": "success"},
        ]
        verified = policy.verify_attestation(
            attestation=attestation,
            pull=pull,
            head=head,
            run=run,
            jobs=jobs,
            changes=changes,
            repository=repository,
        )
        self.assertEqual(verified.mode, "targeted")


class GateContractTests(unittest.TestCase):
    def test_gate_run_requires_exact_path_and_workflow_id(self):
        spec = policy.RELEASE_GATES[1]
        workflow = {
            "id": 55,
            "name": spec["name"],
            "path": spec["path"],
            "state": "active",
        }
        run = {
            "id": 88,
            "created_at": "2026-09-01T12:00:00Z",
            "name": spec["name"],
            "path": spec["path"],
            "workflow_id": 55,
            "event": "workflow_dispatch",
            "head_sha": SHA["merge"],
            "head_branch": "main",
            "status": "completed",
            "conclusion": "success",
        }
        self.assertEqual(
            policy._select_gate_run([run], spec, workflow, SHA["merge"])["id"], 88
        )
        run["path"] = ".github/workflows/lookalike.yml"
        with self.assertRaises(policy.PolicyError):
            policy._select_gate_run([run], spec, workflow, SHA["merge"])

    def test_final_post_merge_gates_do_not_run_pytest(self):
        repository_root = Path(__file__).resolve().parents[1]
        gate_paths = [spec["path"] for spec in policy.RELEASE_GATES[1:]]
        for relative in gate_paths:
            text = (repository_root / relative).read_text(encoding="utf-8").lower()
            with self.subTest(path=relative):
                self.assertNotIn("pytest", text)

    def test_ci_has_no_main_push_trigger(self):
        repository_root = Path(__file__).resolve().parents[1]
        text = (repository_root / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        trigger_block = text.split("permissions:", 1)[0]
        self.assertIn("pull_request:", trigger_block)
        self.assertNotIn("push:", trigger_block)

    def test_targeted_backend_mode_applies_migrations_twice(self):
        repository_root = Path(__file__).resolve().parents[1]
        text = (repository_root / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        self.assertEqual(
            text.count("if: needs.backend_scope.outputs.backend_mode != 'skip'"), 3
        )
        self.assertIn("- name: Apply migrations through the operational command", text)
        self.assertIn("- name: Verify migration command is idempotent", text)

    def test_deploy_claim_uses_serial_lock_and_skips_certification(self):
        repository_root = Path(__file__).resolve().parents[1]
        text = (repository_root / ".github/workflows/deploy-production.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("group: corvia-production-deploy", text)
        self.assertIn("cancel-in-progress: false", text)
        self.assertIn("check-deploy-claim", text)
        self.assertIn("claimed: ${{ steps.claim.outputs.claimed }}", text)
        self.assertIn('remote_command="verify-release $TARGET_SHA $cert"', text)
        self.assertNotIn("verify-public-claim", text)
        self.assertEqual(text.count("steps.claim.outputs.claimed != 'true'"), 2)


class ReleaseReceiptTests(unittest.TestCase):
    def test_apk_and_sidecar_replacement_cannot_override_receipt_digest(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            apk = root / "corvia.apk"
            sidecar = root / "corvia.apk.sha256"
            receipt = root / "release.json"
            certificate = "e" * 64

            apk.write_bytes(b"PK\x03\x04original-certified-apk")
            original_digest = hashlib.sha256(apk.read_bytes()).hexdigest()
            sidecar.write_text(f"{original_digest}  {apk.name}\n", encoding="utf-8")
            receipt.write_text(
                json.dumps(
                    {
                        "schema": 1,
                        "sha": SHA["merge"],
                        "android_name": apk.name,
                        "android_sha256": original_digest,
                        "android_cert_sha256": certificate,
                        "windows_sha256": None,
                    }
                ),
                encoding="utf-8",
            )
            self.assertEqual(
                policy.verify_release_receipt(
                    receipt_path=receipt,
                    apk_path=apk,
                    apk_sidecar_path=sidecar,
                    expected_sha=SHA["merge"],
                    expected_cert=certificate,
                ),
                original_digest,
            )
            with self.assertRaisesRegex(
                policy.PolicyError, "release receipt mismatch: android_cert_sha256"
            ):
                policy.verify_release_receipt(
                    receipt_path=receipt,
                    apk_path=apk,
                    apk_sidecar_path=sidecar,
                    expected_sha=SHA["merge"],
                    expected_cert="f" * 64,
                )

            apk.write_bytes(b"PK\x03\x04replacement-apk")
            replacement_digest = hashlib.sha256(apk.read_bytes()).hexdigest()
            sidecar.write_text(f"{replacement_digest}  {apk.name}\n", encoding="utf-8")
            with self.assertRaisesRegex(
                policy.PolicyError, "release receipt APK digest mismatch"
            ):
                policy.verify_release_receipt(
                    receipt_path=receipt,
                    apk_path=apk,
                    apk_sidecar_path=sidecar,
                    expected_sha=SHA["merge"],
                    expected_cert=certificate,
                )


class DeployClaimTests(unittest.TestCase):
    def fixtures(self):
        workflow = {
            "id": 77,
            "name": policy.DEPLOY_WORKFLOW["name"],
            "path": policy.DEPLOY_WORKFLOW["path"],
            "state": "active",
        }
        run = {
            "id": 900,
            "name": policy.DEPLOY_WORKFLOW["name"],
            "path": policy.DEPLOY_WORKFLOW["path"],
            "workflow_id": 77,
            "event": "workflow_run",
            "head_sha": SHA["merge"],
            "head_branch": "main",
        }
        job = {
            "name": policy.DEPLOY_JOB_NAME,
            "conclusion": "success",
            "run_attempt": 1,
        }
        return workflow, run, job

    def test_previous_successful_run_claims_sha(self):
        workflow, run, job = self.fixtures()
        claim = policy.find_successful_deploy_claim(
            runs=[run],
            jobs_by_run={900: [job]},
            workflow=workflow,
            sha=SHA["merge"],
            current_run_id=901,
            current_run_attempt=1,
        )
        self.assertEqual(claim, (900, 1))

    def test_prior_attempt_of_same_rerun_claims_sha(self):
        workflow, run, job = self.fixtures()
        claim = policy.find_successful_deploy_claim(
            runs=[run],
            jobs_by_run={900: [job]},
            workflow=workflow,
            sha=SHA["merge"],
            current_run_id=900,
            current_run_attempt=2,
        )
        self.assertEqual(claim, (900, 1))

    def test_current_attempt_cannot_self_claim(self):
        workflow, run, job = self.fixtures()
        claim = policy.find_successful_deploy_claim(
            runs=[run],
            jobs_by_run={900: [job]},
            workflow=workflow,
            sha=SHA["merge"],
            current_run_id=900,
            current_run_attempt=1,
        )
        self.assertIsNone(claim)

    def test_lookalike_workflow_cannot_claim(self):
        workflow, run, job = self.fixtures()
        run["path"] = ".github/workflows/lookalike.yml"
        claim = policy.find_successful_deploy_claim(
            runs=[run],
            jobs_by_run={900: [job]},
            workflow=workflow,
            sha=SHA["merge"],
            current_run_id=901,
            current_run_attempt=1,
        )
        self.assertIsNone(claim)

    def test_deploy_and_remote_entrypoint_recheck_current_main(self):
        repository_root = Path(__file__).resolve().parents[1]
        deploy = (repository_root / ".github/workflows/deploy-production.yml").read_text(
            encoding="utf-8"
        )
        release_step = deploy.split(
            "- name: Revalidate current main and deploy the certified release", 1
        )[1]
        self.assertGreaterEqual(release_step.count("git/ref/heads/main"), 2)
        self.assertLess(
            release_step.index("git/ref/heads/main"),
            release_step.index('timeout "$remote_timeout" ssh'),
        )

        remote = (repository_root / "ops/remote-deploy-entrypoint.sh").read_text(
            encoding="utf-8"
        )
        self.assertEqual(remote.count("require_current_remote_main"), 4)
        self.assertLess(
            remote.index("require_current_remote_main", remote.index("Android compilation")),
            remote.index("git checkout main"),
        )
        self.assertGreater(
            remote.rindex("require_current_remote_main"), remote.index("bash ./deploy.sh")
        )

    def test_remote_release_boundary_is_locked_and_idempotent_by_sha(self):
        repository_root = Path(__file__).resolve().parents[1]
        remote = (repository_root / "ops/remote-deploy-entrypoint.sh").read_text(
            encoding="utf-8"
        )
        lock_index = remote.index('flock -w 30 9')
        no_op_index = remote.index('existing_android_sha="$(completed_release_digest)"')
        build_index = remote.index("build-android-apk.sh")
        receipt_index = remote.index('mv -f "$receipt_candidate" "$RELEASE_RECEIPT"')
        self.assertLess(lock_index, no_op_index)
        self.assertLess(no_op_index, build_index)
        self.assertLess(
            remote.index('if [[ "$REQUEST_KIND" == "verify-release" ]]'), build_index
        )
        verify_block = remote.split(
            'if [[ "$REQUEST_KIND" == "verify-release" ]]', 1
        )[1].split(
            'if [[ "$REQUEST_KIND" == "deploy-release" || '
            '"$REQUEST_KIND" == "deploy-web-android" ]]',
            1,
        )[0]
        self.assertIn("completed_release_digest", verify_block)
        self.assertIn("exit 0", verify_block)
        self.assertNotIn("deploy.sh", verify_block)
        self.assertNotIn("build-android-apk.sh", verify_block)
        self.assertIn("receipt, digest, certificate or runtime state", remote)
        self.assertGreater(receipt_index, remote.index("bash ./deploy.sh"))
        self.assertGreater(receipt_index, remote.index("release_artifacts"))
        self.assertIn("ALREADY_DEPLOYED=1", remote)
        self.assertIn("completion receipt or runtime state is incomplete", remote)

if __name__ == "__main__":
    unittest.main()
