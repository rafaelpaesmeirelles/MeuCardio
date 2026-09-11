"""Pure, offline guards for the single failed-test continuation of PR932."""
from __future__ import annotations

from copy import deepcopy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET
import zipfile


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
SPEC = importlib.util.spec_from_file_location(
    "ci_backend_failed_test_followup", SCRIPTS / "ci_backend_failed_test_followup.py"
)
assert SPEC is not None and SPEC.loader is not None
FOLLOWUP = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = FOLLOWUP
SPEC.loader.exec_module(FOLLOWUP)


def baseline_evidence():
    run = {
        "id": FOLLOWUP.RUN_ID,
        "head_sha": FOLLOWUP.BASELINE_SHA,
        "head_branch": FOLLOWUP.BRANCH,
        "path": ".github/workflows/ci.yml",
        "event": "pull_request",
        "status": "completed",
        "conclusion": "failure",
        "run_attempt": 1,
        "repository": {"full_name": FOLLOWUP.REPOSITORY},
        "pull_requests": [{
            "number": FOLLOWUP.PR_NUMBER,
            "head": {"sha": FOLLOWUP.BASELINE_SHA, "ref": FOLLOWUP.BRANCH},
            "base": {"ref": "main"},
        }],
    }
    steps = [
        {"name": name, "status": "completed", "conclusion": "success"}
        for name in FOLLOWUP.RETAINED_SUCCESS_STEPS
    ]
    steps += [
        {"name": "Run pytest", "status": "completed", "conclusion": "failure"},
        {"name": "Exercise live HTTP release flow", "status": "completed", "conclusion": "skipped"},
        {"name": "Prove PostgreSQL backup and restore", "status": "completed", "conclusion": "skipped"},
    ]
    job = {
        "id": FOLLOWUP.JOB_ID, "run_id": FOLLOWUP.RUN_ID,
        "head_sha": FOLLOWUP.BASELINE_SHA, "name": "Backend tests",
        "status": "completed", "conclusion": "failure", "steps": steps,
    }
    log = (
        "=========================== short test summary info ============================\n"
        f"FAILED {FOLLOWUP.TEST_NODE.removeprefix('backend/')} - ValueError: synthetic fixture\n"
        "1 failed, 3673 passed, 4 skipped, 1 warning in 2331.57s (0:38:51)\n"
    )
    return run, job, log


def completed_release_evidence():
    run, _, _ = baseline_evidence()
    run.update(id=FOLLOWUP.CERTIFIED_RUN_ID, head_sha=FOLLOWUP.CERTIFIED_SHA,
               conclusion="success", pull_requests=[])
    backend = {
        "id": FOLLOWUP.CERTIFIED_JOB_ID, "run_id": FOLLOWUP.CERTIFIED_RUN_ID,
        "head_sha": FOLLOWUP.CERTIFIED_SHA, "name": "Backend tests",
        "status": "completed", "conclusion": "success",
        "steps": [{"name": name, "status": "completed", "conclusion": "success"}
                  for name in ("Run pytest", "Exercise live HTTP release flow",
                               "Prove PostgreSQL backup and restore",
                               "Backend suite certificate " + FOLLOWUP.REPAIRED_SUITE_KEY)],
    }
    gate = {
        "id": FOLLOWUP.CERTIFIED_GATE_JOB_ID, "run_id": FOLLOWUP.CERTIFIED_RUN_ID,
        "head_sha": FOLLOWUP.CERTIFIED_SHA, "name": "Backend risk gate",
        "status": "completed", "conclusion": "success",
    }
    return run, [backend, gate]


def zip_report(*members):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for name, data in members:
            bundle.writestr(name, data)
    return buffer.getvalue()


def artifact_evidence(archive):
    return {
        "id": FOLLOWUP.ARTIFACT_ID, "name": "backend-pytest-failure", "expired": False,
        "digest": "sha256:" + hashlib.sha256(archive).hexdigest(),
        "size_in_bytes": len(archive),
        "workflow_run": {"id": FOLLOWUP.RUN_ID, "head_sha": FOLLOWUP.BASELINE_SHA,
                         "head_branch": FOLLOWUP.BRANCH, "repository_id": 1312508910,
                         "head_repository_id": 1312508910},
    }


class ArtifactProvenanceTests(unittest.TestCase):
    def validate(self, archive, artifact=None):
        with patch.object(FOLLOWUP, "ARTIFACT_SHA256", hashlib.sha256(archive).hexdigest()):
            return FOLLOWUP.validate_artifact(artifact or artifact_evidence(archive), archive)

    def test_exact_single_report_is_read_only_in_memory(self):
        _, _, log = baseline_evidence()
        archive = zip_report(("pytest-output.txt", log))
        with patch.object(zipfile.ZipFile, "extract") as extract, patch.object(zipfile.ZipFile, "extractall") as extractall:
            self.assertEqual(self.validate(archive), log)
        extract.assert_not_called()
        extractall.assert_not_called()

    def test_artifact_identity_digest_expiry_and_origin_are_required(self):
        archive = zip_report(("pytest-output.txt", "synthetic"))
        original = artifact_evidence(archive)
        changes = ({"id": FOLLOWUP.ARTIFACT_ID + 1}, {"name": "other"}, {"expired": True},
                   {"digest": "sha256:" + "0" * 64})
        for change in changes:
            artifact = deepcopy(original)
            artifact.update(change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.validate(archive, artifact)
        for key, value in {"id": FOLLOWUP.RUN_ID + 1, "head_sha": "0" * 40,
                           "head_branch": "other", "repository_id": 1, "head_repository_id": 2}.items():
            artifact = deepcopy(original)
            artifact["workflow_run"][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.validate(archive, artifact)

    def test_archive_bytes_must_match_pinned_digest(self):
        archive = zip_report(("pytest-output.txt", "synthetic"))
        with patch.object(FOLLOWUP, "ARTIFACT_SHA256", hashlib.sha256(archive).hexdigest()):
            with self.assertRaises(ValueError):
                FOLLOWUP.validate_artifact(artifact_evidence(archive), archive + b"changed")

    def test_empty_extra_or_wrong_members_are_rejected(self):
        for members in ((), (("other.txt", "text"),), (("../pytest-output.txt", "text"),),
                        (("pytest-output.txt", "text"), ("extra.txt", "text"))):
            with self.subTest(members=members), self.assertRaises(ValueError):
                self.validate(zip_report(*members))

    def test_oversized_corrupt_or_non_utf8_archives_fail_closed(self):
        oversized = b"x" * (2 * 1024 * 1024 + 1)
        for archive in (oversized, zip_report(("pytest-output.txt", oversized))):
            with self.subTest(archive_bytes=len(archive)), self.assertRaises(ValueError):
                self.validate(archive)

        with self.assertRaises(zipfile.BadZipFile):
            self.validate(b"not a zip archive")
        with self.assertRaises(UnicodeDecodeError):
            self.validate(zip_report(("pytest-output.txt", b"\xff\xfe")))


class BaselineProvenanceTests(unittest.TestCase):
    def test_exact_failed_baseline_returns_its_log_digest(self):
        run, job, log = baseline_evidence()
        self.assertEqual(FOLLOWUP.validate_baseline(run, job, log), hashlib.sha256(log.encode()).hexdigest())

    def test_timestamped_ansi_github_log_is_supported(self):
        run, job, log = baseline_evidence()
        encoded = "\n".join(
            f"2026-09-11T11:56:00.1234567Z \x1b[31m{line}\x1b[0m"
            for line in log.splitlines()
        )
        self.assertEqual(FOLLOWUP.validate_baseline(run, job, encoded), hashlib.sha256(encoded.encode()).hexdigest())

    def test_run_identity_and_attempt_must_match(self):
        for key, value in {
            "id": FOLLOWUP.RUN_ID + 1, "head_sha": "a" * 40,
            "head_branch": "unrelated", "path": ".github/workflows/other.yml",
            "event": "push", "status": "in_progress", "conclusion": "cancelled",
            "run_attempt": 2, "repository": {"full_name": "fork/MeuCardio"},
        }.items():
            with self.subTest(key=key):
                run, job, log = baseline_evidence()
                run[key] = value
                with self.assertRaises(ValueError):
                    FOLLOWUP.validate_baseline(run, job, log)

    def test_baseline_pr_identity_cannot_be_missing_or_borrowed(self):
        for requests in ([], [{"number": 918}], [{
            "number": FOLLOWUP.PR_NUMBER,
            "head": {"sha": FOLLOWUP.BASELINE_SHA, "ref": "another-branch"}, "base": {"ref": "main"},
        }], [{
            "number": FOLLOWUP.PR_NUMBER,
            "head": {"sha": FOLLOWUP.BASELINE_SHA, "ref": FOLLOWUP.BRANCH}, "base": {"ref": "develop"},
        }]):
            with self.subTest(requests=requests):
                run, job, log = baseline_evidence()
                run["pull_requests"] = requests
                with self.assertRaises(ValueError):
                    FOLLOWUP.validate_baseline(run, job, log)

    def test_pr_association_head_can_advance_without_changing_baseline_identity(self):
        run, job, log = baseline_evidence()
        # GitHub mutates this nested association to the PR's current head.
        # The recorded run.head_sha and job.head_sha remain the exact baseline.
        run["pull_requests"][0]["head"]["sha"] = "b" * 40
        self.assertEqual(FOLLOWUP.validate_baseline(run, job, log), hashlib.sha256(log.encode()).hexdigest())

    def test_empty_or_reassigned_association_requires_verified_closed_release(self):
        run, job, log = baseline_evidence()
        for associations in ([], [{"number": FOLLOWUP.PR_NUMBER + 1,
                                    "head": {"ref": FOLLOWUP.BRANCH, "sha": "b" * 40},
                                    "base": {"ref": "main"}}]):
            # The same old run is reassociated to the new PR when a branch is reused.
            run["pull_requests"] = associations
            with self.subTest(associations=associations):
                with self.assertRaises(ValueError):
                    FOLLOWUP.validate_baseline(run, job, log)
                self.assertEqual(FOLLOWUP.validate_baseline(run, job, log, closed_release_verified=True),
                                 hashlib.sha256(log.encode()).hexdigest())

    def test_closed_release_flag_never_relaxes_immutable_run_or_job_sha(self):
        for change in ("run", "job"):
            run, job, log = baseline_evidence()
            run["pull_requests"] = []
            if change == "run":
                run["head_sha"] = "0" * 40
            elif change == "job":
                job["head_sha"] = "0" * 40
            with self.subTest(change=change), self.assertRaises(ValueError):
                FOLLOWUP.validate_baseline(run, job, log, closed_release_verified=True)

    def test_job_identity_must_match(self):
        for key, value in {
            "id": FOLLOWUP.JOB_ID + 1, "run_id": FOLLOWUP.RUN_ID + 1,
            "head_sha": "c" * 40, "name": "Backend focused tests",
            "status": "in_progress", "conclusion": "timed_out",
        }.items():
            with self.subTest(key=key):
                run, job, log = baseline_evidence()
                job[key] = value
                with self.assertRaises(ValueError):
                    FOLLOWUP.validate_baseline(run, job, log)

    def test_every_retained_prerequisite_must_have_completed_successfully(self):
        for name in FOLLOWUP.RETAINED_SUCCESS_STEPS:
            for status, conclusion in (("completed", "skipped"), ("in_progress", "success")):
                with self.subTest(name=name, status=status, conclusion=conclusion):
                    run, job, log = baseline_evidence()
                    step = next(item for item in job["steps"] if item["name"] == name)
                    step.update(status=status, conclusion=conclusion)
                    with self.assertRaises(ValueError):
                        FOLLOWUP.validate_baseline(run, job, log)

    def test_baseline_pytest_must_be_a_completed_failure(self):
        for status, conclusion in (("completed", "success"), ("completed", "skipped"), ("in_progress", "failure")):
            with self.subTest(status=status, conclusion=conclusion):
                run, job, log = baseline_evidence()
                next(item for item in job["steps"] if item["name"] == "Run pytest").update(
                    status=status, conclusion=conclusion
                )
                with self.assertRaises(ValueError):
                    FOLLOWUP.validate_baseline(run, job, log)

    def test_additional_failed_step_or_missing_operational_gate_is_rejected(self):
        run, job, log = baseline_evidence()
        job["steps"].append({"name": "Additional gate", "status": "completed", "conclusion": "failure"})
        with self.assertRaises(ValueError):
            FOLLOWUP.validate_baseline(run, job, log)
        for name in ("Exercise live HTTP release flow", "Prove PostgreSQL backup and restore"):
            run, job, log = baseline_evidence()
            job["steps"] = [item for item in job["steps"] if item["name"] != name]
            with self.subTest(name=name), self.assertRaises(ValueError):
                FOLLOWUP.validate_baseline(run, job, log)

    def test_incomplete_duplicate_or_changed_pytest_totals_are_rejected(self):
        run, job, log = baseline_evidence()
        invalid = (
            "", log.split("1 failed,")[0], log + log,
            log.replace("1 failed,", "2 failed,"),
            log.replace("3673 passed", "3672 passed"),
            log.replace("4 skipped", "5 skipped"),
            log.replace("1 warning in", "1 warning, 1 error in"),
            log.replace("1 warning in", "1 warning, 1 xfailed in"),
        )
        for index, text in enumerate(invalid):
            with self.subTest(index=index), self.assertRaises(ValueError):
                FOLLOWUP.validate_baseline(run, job, text)

    def test_failed_node_inventory_is_exact_and_has_no_collection_error(self):
        run, job, log = baseline_evidence()
        for text in (
            log.replace("test_reconcile_nunca_chama_rag", "test_other"),
            "\n".join(line for line in log.splitlines() if not line.startswith("FAILED")),
            log + "FAILED tests/test_other.py::test_other - AssertionError\n",
            log + "ERROR tests/test_other.py::test_other - RuntimeError\n",
            log + "!!!!!!!! Interrupted: collection failure !!!!!!!!\n",
        ):
            with self.subTest(text=text[-90:]), self.assertRaises(ValueError):
                FOLLOWUP.validate_baseline(run, job, text)


class DiffScopeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.paths = sorted(FOLLOWUP.ALLOWED_PATHS)
        self.ci_delta = sorted(FOLLOWUP.CI_ONLY_PATHS)
        self.fixture = b"synthetic reviewed fixture\n"
        for name in self.paths:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(self.fixture if name == FOLLOWUP.FIXTURE_PATH else b"reviewed CI file\n")
        self.mode = "100644"
        self.baseline_blob = "e41def371f97ece2b6523cc135e55260c0484a1e"
        self.certified_blob = "0dae85a5600b2c343aff750a7a90ce19cfa9e36e"
        self.dirty = ""
        self.addCleanup(patch.stopall)
        patch.object(FOLLOWUP, "FIXTURE_SHA256", hashlib.sha256(self.fixture).hexdigest()).start()
        self.run = patch.object(FOLLOWUP.subprocess, "run").start()
        self.output = patch.object(FOLLOWUP.subprocess, "check_output", side_effect=self.git_output).start()

    def git_output(self, command, **kwargs):
        self.assertEqual(command[:3], ["git", "-C", str(self.root)])
        args = command[3:]
        if args == ["diff", "--no-renames", "--name-only", f"{FOLLOWUP.BASELINE_SHA}..HEAD"]:
            return "\n".join(self.paths) + "\n"
        if args == ["diff", "--no-renames", "--name-only", f"{FOLLOWUP.CERTIFIED_SHA}..HEAD"]:
            return "\n".join(self.ci_delta)
        if args[:3] == ["ls-tree", "HEAD", "--"]:
            return f"{self.mode} blob {'1' * 40}\t{args[3]}\n"
        if args == ["rev-parse", f"{FOLLOWUP.BASELINE_SHA}:{FOLLOWUP.FIXTURE_PATH}"]:
            return self.baseline_blob
        if args == ["rev-parse", f"{FOLLOWUP.CERTIFIED_SHA}:{FOLLOWUP.FIXTURE_PATH}"]:
            return self.certified_blob
        if args == ["status", "--porcelain", "--untracked-files=no"]:
            return self.dirty
        self.fail(f"Unexpected git command: {args!r}")

    def test_exact_reviewed_diff_requires_baseline_ancestry(self):
        self.assertEqual(FOLLOWUP.validate_diff(self.root), self.paths)
        self.assertEqual(self.run.call_count, 2)
        for sha in (FOLLOWUP.BASELINE_SHA, FOLLOWUP.CERTIFIED_SHA):
            self.run.assert_any_call(
                ["git", "-C", str(self.root), "merge-base", "--is-ancestor", sha, "HEAD"],
                check=True, capture_output=True,
            )

    def test_ci_delta_must_be_nonempty_and_exclude_even_the_passed_fixture(self):
        for delta in ([], [FOLLOWUP.FIXTURE_PATH], ["backend/app/main.py"], ["frontend/src/App.tsx"]):
            self.ci_delta = delta
            with self.subTest(delta=delta), self.assertRaises(ValueError):
                FOLLOWUP.validate_diff(self.root)

    def test_external_manifest_cannot_expand_scope(self):
        with self.assertRaises(ValueError):
            FOLLOWUP.validate_diff(self.root, {"allowed_paths": ["backend/app/main.py"]})
        self.run.assert_not_called()

    def test_non_descendant_is_rejected_without_fallback(self):
        self.run.side_effect = subprocess.CalledProcessError(1, "git")
        with self.assertRaises(subprocess.CalledProcessError):
            FOLLOWUP.validate_diff(self.root)
        self.output.assert_not_called()

    def test_product_dependency_corpus_or_other_test_change_is_rejected(self):
        for extra in ("backend/app/main.py", "backend/requirements.txt", "backend/tests/conftest.py",
                      "backend/tests/test_other.py", "content/clinical.md", "frontend/src/App.tsx"):
            with self.subTest(extra=extra):
                self.paths = sorted(FOLLOWUP.ALLOWED_PATHS | {extra})
                with self.assertRaises(ValueError):
                    FOLLOWUP.validate_diff(self.root)

    def test_missing_reviewed_path_is_rejected(self):
        self.paths.remove(FOLLOWUP.FIXTURE_PATH)
        with self.assertRaises(ValueError):
            FOLLOWUP.validate_diff(self.root)

    def test_fixture_content_is_sealed(self):
        (self.root / FOLLOWUP.FIXTURE_PATH).write_bytes(self.fixture + b"# another edit\n")
        with self.assertRaises(ValueError):
            FOLLOWUP.validate_diff(self.root)

    def test_baseline_fixture_blob_is_sealed(self):
        self.baseline_blob = "2" * 40
        with self.assertRaises(ValueError):
            FOLLOWUP.validate_diff(self.root)

    def test_successfully_tested_fixture_blob_is_sealed(self):
        self.certified_blob = "2" * 40
        with self.assertRaises(ValueError):
            FOLLOWUP.validate_diff(self.root)

    def test_deleted_non_regular_and_symlinked_files_are_rejected(self):
        for mode in ("120000", "160000", "100755"):
            self.mode = mode
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                FOLLOWUP.validate_diff(self.root)
        self.mode = "100644"
        path = self.root / FOLLOWUP.FIXTURE_PATH
        path.unlink()
        with self.assertRaises(ValueError):
            FOLLOWUP.validate_diff(self.root)
        target = self.root / "synthetic-target"
        target.write_bytes(self.fixture)
        path.symlink_to(target)
        with self.assertRaises(ValueError):
            FOLLOWUP.validate_diff(self.root)

    def test_uncommitted_tracked_changes_are_rejected(self):
        self.dirty = " M .github/workflows/ci.yml\n"
        with self.assertRaises(ValueError):
            FOLLOWUP.validate_diff(self.root)


class CompletedReleaseTests(unittest.TestCase):
    def test_exact_completed_release_is_valid_without_live_pr_associations(self):
        run, jobs = completed_release_evidence()
        FOLLOWUP.validate_completed_release(run, jobs)

    def test_completed_run_identity_and_success_are_required(self):
        for key, value in {"id": FOLLOWUP.CERTIFIED_RUN_ID + 1, "head_sha": "0" * 40,
                           "head_branch": "other", "path": ".github/workflows/other.yml",
                           "event": "push", "status": "in_progress", "conclusion": "failure",
                           "run_attempt": 2, "repository": {"full_name": "fork/MeuCardio"}}.items():
            run, jobs = completed_release_evidence()
            run[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                FOLLOWUP.validate_completed_release(run, jobs)

    def test_both_unique_successful_jobs_must_match_the_certified_run_and_sha(self):
        for index in (0, 1):
            for key, value in {"id": 0, "run_id": 0, "head_sha": "0" * 40, "name": "other",
                               "status": "in_progress", "conclusion": "skipped"}.items():
                run, jobs = completed_release_evidence()
                jobs[index][key] = value
                with self.subTest(index=index, key=key), self.assertRaises(ValueError):
                    FOLLOWUP.validate_completed_release(run, jobs)
            run, jobs = completed_release_evidence()
            jobs.append(deepcopy(jobs[index]))
            with self.subTest(index=index, duplicate=True), self.assertRaises(ValueError):
                FOLLOWUP.validate_completed_release(run, jobs)

    def test_pytest_http_backup_and_named_certificate_must_all_be_successful(self):
        run, jobs = completed_release_evidence()
        for index in range(len(jobs[0]["steps"])):
            for status, conclusion in (("in_progress", "success"), ("completed", "skipped")):
                altered = deepcopy(jobs)
                altered[0]["steps"][index].update(status=status, conclusion=conclusion)
                with self.subTest(index=index, status=status, conclusion=conclusion), self.assertRaises(ValueError):
                    FOLLOWUP.validate_completed_release(run, altered)


class DecisionContextTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.candidate = "d" * 40
        self.candidate_tree = "f" * 40
        self.active_number = FOLLOWUP.PR_NUMBER + 1
        self.ci_delta = sorted(FOLLOWUP.CI_ONLY_PATHS)
        self.pr = {
            "number": self.active_number,
            "head": {"sha": self.candidate, "ref": FOLLOWUP.BRANCH,
                     "repo": {"full_name": FOLLOWUP.REPOSITORY}},
            "base": {"ref": "main", "repo": {"full_name": FOLLOWUP.REPOSITORY}},
            "merge_commit_sha": self.candidate, "merged": True,
        }
        self.original_pr = deepcopy(self.pr)
        self.original_pr.update(number=FOLLOWUP.PR_NUMBER, merge_commit_sha=FOLLOWUP.CERTIFIED_SHA)
        self.original_pr["head"]["sha"] = FOLLOWUP.CERTIFIED_SHA
        self.run, self.job, self.log = baseline_evidence()
        self.run["pull_requests"] = []
        self.completed_run, self.completed_jobs = completed_release_evidence()
        self.archive = zip_report(("pytest-output.txt", self.log))
        self.artifact = artifact_evidence(self.archive)
        self.artifacts = {"artifacts": [self.artifact]}
        self.jobs = {"jobs": [self.job]}
        self.associated = [{"number": self.active_number, "head": deepcopy(self.pr["head"])}]
        self.main_sha = self.candidate
        self.addCleanup(patch.stopall)
        patch.dict(FOLLOWUP.os.environ, {"RUNNER_TEMP": str(self.root)}).start()
        patch.object(FOLLOWUP, "ARTIFACT_SHA256", hashlib.sha256(self.archive).hexdigest()).start()
        self.git = patch.object(FOLLOWUP, "_git", side_effect=self.git_value).start()
        self.api = patch.object(FOLLOWUP, "_github", side_effect=self.github).start()
        self.binary_api = patch.object(FOLLOWUP, "_github_binary", return_value=self.archive).start()
        self.ancestry = patch.object(FOLLOWUP.subprocess, "run", return_value=subprocess.CompletedProcess([], 0)).start()
        self.diff = patch.object(FOLLOWUP, "validate_diff", return_value=sorted(FOLLOWUP.ALLOWED_PATHS)).start()

    def git_value(self, root, *args):
        self.assertEqual(root, self.root)
        if args == ("rev-parse", "HEAD"):
            return self.candidate
        if args == ("rev-parse", "HEAD^{tree}"):
            return self.candidate_tree
        if args == ("diff", "--no-renames", "--name-only", f"{FOLLOWUP.CERTIFIED_SHA}..HEAD"):
            return "\n".join(self.ci_delta)
        self.fail(f"Unexpected git operation: {args!r}")

    def github(self, path, *, raw=False):
        base = f"repos/{FOLLOWUP.REPOSITORY}"
        payloads = {
            f"{base}/pulls/{FOLLOWUP.PR_NUMBER}": self.original_pr,
            f"{base}/pulls/{self.active_number}": self.pr,
            f"{base}/git/ref/heads/main": {"object": {"sha": self.main_sha}},
            f"{base}/commits/{self.candidate}/pulls": self.associated,
            f"{base}/actions/runs/{FOLLOWUP.CERTIFIED_RUN_ID}": self.completed_run,
            f"{base}/actions/runs/{FOLLOWUP.CERTIFIED_RUN_ID}/jobs?filter=all&per_page=100": {"jobs": self.completed_jobs},
            f"{base}/actions/runs/{FOLLOWUP.RUN_ID}": self.run,
            f"{base}/actions/runs/{FOLLOWUP.RUN_ID}/jobs?filter=all&per_page=100": self.jobs,
            f"{base}/actions/runs/{FOLLOWUP.RUN_ID}/artifacts": self.artifacts,
        }
        self.assertIn(path, payloads)
        self.assertFalse(raw)
        return deepcopy(payloads[path])

    def resolve(self, **overrides):
        context = {"event": "pull_request", "number": str(self.active_number),
                   "head_ref": FOLLOWUP.BRANCH, "repository": FOLLOWUP.REPOSITORY}
        context.update(overrides)
        return FOLLOWUP.resolve_decision(self.root, **context)

    def test_exact_pr_emits_ci_continuity_without_any_backend_test_to_run(self):
        decision = self.resolve()
        self.assertEqual(decision.backend_mode, "ci-only-continuation")
        self.assertEqual(decision.focused_tests, ())
        self.assertEqual(decision.suite_key, FOLLOWUP.SUITE_KEY)
        proof = json.loads((self.root / "backend-failed-test-followup.json").read_text())
        self.assertEqual(proof["candidate_sha"], self.candidate)
        self.assertEqual(proof["candidate_tree"], self.candidate_tree)
        self.assertEqual(proof["baseline_sha"], FOLLOWUP.BASELINE_SHA)
        self.assertEqual(proof["baseline_run_id"], FOLLOWUP.RUN_ID)
        self.assertEqual(proof["baseline_job_id"], FOLLOWUP.JOB_ID)
        self.assertEqual(proof["baseline_result"], {"failed": 1, "passed": 3673, "skipped": 4})
        self.assertEqual(proof["test_already_passed"], FOLLOWUP.TEST_NODE)
        self.assertEqual(proof["backend_tests_to_run"], [])
        self.assertEqual(proof["certified_application_sha"], FOLLOWUP.CERTIFIED_SHA)
        self.assertEqual(proof["certified_run_id"], FOLLOWUP.CERTIFIED_RUN_ID)
        self.assertEqual(proof["certified_backend_job_id"], FOLLOWUP.CERTIFIED_JOB_ID)
        self.assertEqual(proof["active_pull_request"], self.active_number)
        self.assertEqual(proof["baseline_report_sha256"], hashlib.sha256(self.log.encode()).hexdigest())
        self.assertEqual(proof["baseline_artifact_id"], FOLLOWUP.ARTIFACT_ID)
        self.assertEqual(proof["baseline_artifact_sha256"], hashlib.sha256(self.archive).hexdigest())
        self.binary_api.assert_called_once_with(
            f"repos/{FOLLOWUP.REPOSITORY}/actions/artifacts/{FOLLOWUP.ARTIFACT_ID}/zip"
        )
        self.assertEqual(proof["completed_operational_gates"], ["HTTP release flow", "PostgreSQL backup and restore"])
        self.assertIn("not-a-full-suite-or-exact-SHA-reuse-certificate", decision.reasons)

    def test_unrelated_pr_and_unsupported_event_do_not_apply(self):
        self.assertIsNone(self.resolve(number="933", head_ref="other"))
        self.assertIsNone(self.resolve(event="workflow_dispatch"))
        self.api.assert_not_called()
        self.diff.assert_not_called()

    def test_relevant_pr_with_wrong_context_fails_closed(self):
        for override in ({"number": "918"}, {"number": str(FOLLOWUP.PR_NUMBER), "head_ref": "other"},
                         {"repository": "fork/MeuCardio"}):
            with self.subTest(override=override), self.assertRaises(ValueError):
                self.resolve(**override)

    def test_stale_head_fork_wrong_base_or_branch_is_rejected(self):
        original = deepcopy(self.pr)
        for section, key, value in (
            ("head", "sha", "e" * 40), ("head", "ref", "other"),
            ("head", "repo", {"full_name": "fork/MeuCardio"}),
            ("base", "ref", "develop"), ("base", "repo", {"full_name": "fork/MeuCardio"}),
        ):
            self.pr = deepcopy(original)
            self.pr[section][key] = value
            with self.subTest(section=section, key=key), self.assertRaises(ValueError):
                self.resolve()

    def test_exact_main_push_needs_same_head_and_associated_pr(self):
        self.assertEqual(self.resolve(event="push").backend_mode, "ci-only-continuation")
        self.main_sha = "e" * 40
        with self.assertRaises(ValueError):
            self.resolve(event="push")
        self.main_sha = self.candidate
        self.associated = []
        with self.assertRaises(ValueError):
            self.resolve(event="push")

    def test_associated_but_different_integration_sha_is_rejected(self):
        self.pr["head"]["sha"] = "e" * 40
        with self.assertRaises(ValueError):
            self.resolve(event="push")
        self.pr["merge_commit_sha"] = self.candidate
        with self.assertRaises(ValueError):
            self.resolve(event="push")

    def test_unrelated_push_does_not_borrow_this_baseline(self):
        self.pr["head"]["sha"] = "e" * 40
        self.associated = [{"number": 918}]
        self.ci_delta = ["frontend/src/App.tsx"]
        self.assertIsNone(self.resolve(event="push"))
        self.diff.assert_not_called()

    def test_ci_only_descendant_is_rejected_when_pr_association_disappears(self):
        self.associated = []
        with self.assertRaises(ValueError):
            self.resolve(event="push")
        self.diff.assert_not_called()

    def test_original_merge_or_completed_release_cannot_be_borrowed(self):
        original = deepcopy(self.original_pr)
        for key, value in (("merged", False), ("merge_commit_sha", "0" * 40)):
            self.original_pr = deepcopy(original)
            self.original_pr[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.resolve()
        self.original_pr = original
        self.completed_run["head_sha"] = "0" * 40
        with self.assertRaises(ValueError):
            self.resolve()

    def test_missing_or_duplicated_baseline_job_is_rejected(self):
        for jobs in ([], [deepcopy(self.job), deepcopy(self.job)]):
            self.jobs = {"jobs": jobs}
            with self.subTest(count=len(jobs)), self.assertRaises(ValueError):
                self.resolve()

    def test_missing_or_duplicated_baseline_artifact_is_rejected(self):
        for artifacts in ([], [deepcopy(self.artifact), deepcopy(self.artifact)]):
            self.artifacts = {"artifacts": artifacts}
            with self.subTest(count=len(artifacts)), self.assertRaises(ValueError):
                self.resolve()
        self.binary_api.assert_not_called()

    def test_api_scope_or_baseline_failure_does_not_fall_back_to_full(self):
        self.api.side_effect = ValueError("synthetic API unavailable")
        with self.assertRaises(ValueError):
            self.resolve()
        self.api.side_effect = self.github
        self.diff.side_effect = ValueError("synthetic unexpected product change")
        with self.assertRaises(ValueError):
            self.resolve()
        self.diff.side_effect = None
        self.job["head_sha"] = "0" * 40
        with self.assertRaises(ValueError):
            self.resolve()
        self.assertFalse((self.root / "backend-failed-test-followup.json").exists())


class FollowupJUnitTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "result.xml"

    def write_junit(self, *, tests="1", failures="0", errors="0", skipped="0",
                    name="test_reconcile_nunca_chama_rag", classname="backend.tests.test_reconcile_rag_pipeline",
                    child=None, extra_case=False):
        root = ET.Element("testsuites")
        suite = ET.SubElement(root, "testsuite", tests=tests, failures=failures, errors=errors, skipped=skipped)
        case = ET.SubElement(suite, "testcase", name=name, classname=classname)
        if child:
            ET.SubElement(case, child)
        if extra_case:
            ET.SubElement(suite, "testcase", name="test_other", classname=classname)
        ET.ElementTree(root).write(self.path, encoding="utf-8", xml_declaration=True)

    def test_one_exact_pass_is_accepted(self):
        for classname in ("backend.tests.test_reconcile_rag_pipeline", "tests.test_reconcile_rag_pipeline"):
            self.write_junit(classname=classname)
            with self.subTest(classname=classname):
                FOLLOWUP.validate_followup_junit(self.path)

    def test_zero_or_multiple_tests_and_any_nonpass_total_are_rejected(self):
        for override in ({"tests": "0"}, {"tests": "2"}, {"failures": "1"},
                         {"errors": "1"}, {"skipped": "1"}, {"tests": "invalid"}):
            self.write_junit(**override)
            with self.subTest(override=override), self.assertRaises(ValueError):
                FOLLOWUP.validate_followup_junit(self.path)

    def test_wrong_node_and_hidden_nonpass_children_are_rejected(self):
        for override in ({"name": "test_other"}, {"classname": "other.test_reconcile_rag_pipeline"},
                         {"child": "skipped"}, {"child": "failure"}, {"child": "error"},
                         {"extra_case": True}):
            self.write_junit(**override)
            with self.subTest(override=override), self.assertRaises(ValueError):
                FOLLOWUP.validate_followup_junit(self.path)

    def test_empty_or_malformed_report_is_rejected(self):
        for text in ("", "<testsuites>", "<testsuites/>"):
            self.path.write_text(text)
            with self.subTest(text=text), self.assertRaises((ValueError, ET.ParseError)):
                FOLLOWUP.validate_followup_junit(self.path)


if __name__ == "__main__":
    unittest.main()
