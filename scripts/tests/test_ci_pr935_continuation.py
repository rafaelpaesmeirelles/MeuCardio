"""Offline adversarial guards for PR935; no backend pytest, database or network."""
from __future__ import annotations

from contextlib import ExitStack
from copy import deepcopy
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET
import zipfile


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))
SPEC = importlib.util.spec_from_file_location(
    "ci_backend_pr935_continuation", ROOT / "scripts/ci_backend_pr935_continuation.py")
assert SPEC and SPEC.loader
PROFILE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = PROFILE
SPEC.loader.exec_module(PROFILE)


def evidence():
    run = {"id": PROFILE.BASELINE_RUN_ID, "head_sha": PROFILE.BASELINE_SHA,
           "head_branch": PROFILE.BRANCH, "path": ".github/workflows/ci.yml",
           "event": "pull_request", "status": "completed", "conclusion": "failure",
           "run_attempt": 1, "repository": {"full_name": PROFILE.REPOSITORY},
           # GitHub associations can change after a subsequent push. The run
           # and job identities, not this mutable SHA, prove the baseline.
           "pull_requests": [{"number": 935, "head": {"sha": "f" * 40}}]}
    common = {"run_id": PROFILE.BASELINE_RUN_ID, "head_sha": PROFILE.BASELINE_SHA,
              "head_branch": PROFILE.BRANCH, "run_attempt": 1,
              "status": "completed", "conclusion": "success"}
    steps = [{"name": name, "status": "completed", "conclusion": "success"}
             for name in PROFILE.RETAINED_SUCCESS_STEPS]
    steps += [{"name": "Run pytest", "status": "completed", "conclusion": "failure"}]
    steps += [{"name": name, "status": "completed", "conclusion": "skipped"}
              for name in PROFILE.PENDING_OPERATIONAL_STEPS]
    jobs = [dict(common, id=PROFILE.BASELINE_JOB_ID, name="Backend tests", conclusion="failure", steps=steps),
            dict(common, id=103459688312, name="Backend risk gate", conclusion="failure"),
            dict(common, id=103452601833, name="Classify backend risk and reuse exact suites"),
            dict(common, id=103452690311, name="Frontend build"),
            dict(common, id=103452691251, name="Backend focused tests", conclusion="skipped")]
    return run, {"total_count": len(jobs), "jobs": jobs}


def report():
    return ("=========================== short test summary info ============================\n"
            f"FAILED {PROFILE.TEST_NODE} - AssertionError: synthetic fixture\n"
            "1 failed, 3879 passed, 4 skipped, 1 warning in 2200.10s (0:36:40)\n")


def archive_report(*members):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, value in members or (("pytest-output.txt", report()),):
            archive.writestr(name, value)
    return stream.getvalue()


def artifact(archive):
    return {"id": PROFILE.ARTIFACT_ID, "name": "backend-pytest-failure", "expired": False,
            "size_in_bytes": len(archive), "digest": "sha256:" + hashlib.sha256(archive).hexdigest(),
            "workflow_run": {"id": PROFILE.BASELINE_RUN_ID, "head_sha": PROFILE.BASELINE_SHA,
                             "head_branch": PROFILE.BRANCH, "repository_id": 1312508910,
                             "head_repository_id": 1312508910}}


class BaselineTests(unittest.TestCase):
    def validate(self, run=None, jobs=None, log=None):
        original_run, original_jobs = evidence()
        return PROFILE.validate_baseline(original_run if run is None else run,
                                         original_jobs if jobs is None else jobs,
                                         report() if log is None else log)

    def test_profile_pins_the_current_pr935_failure_not_pr934_or_another_run(self):
        self.assertEqual(PROFILE.PR_NUMBER, 935)
        self.assertEqual(PROFILE.REPOSITORY, "rafaelpaesmeirelles/MeuCardio")
        self.assertEqual(PROFILE.BRANCH, "codex/integration-followup-20260911")
        self.assertEqual(PROFILE.BASELINE_SHA, "5cc9ddb2c0be7c407274aa52ccb6bc737eec9d20")
        self.assertEqual(PROFILE.BASELINE_RUN_ID, 34657383923)
        self.assertEqual(PROFILE.BASELINE_JOB_ID, 103452690228)
        self.assertEqual(PROFILE.ARTIFACT_ID, 10287131424)
        self.assertEqual(PROFILE.ARTIFACT_BYTES, 985)
        self.assertEqual(PROFILE.ARTIFACT_SHA256, "68156a5abed3dcd8bfe1128149c73042fb63cf9aac3fa34666b33048f95da613")
        self.assertEqual(PROFILE.TEST_NODE, "tests/test_panel_acervo_comunicacao_contract.py::test_home_nao_duplica_contagem_especializada_que_ja_e_canonica_na_biblioteca")

    def test_failed_baseline_is_not_relabelled_as_a_full_pass(self):
        proof = self.validate()
        self.assertIsNone(proof["full_certificate"])
        self.assertEqual(proof["run_conclusion"], "failure")
        self.assertEqual(proof["result"], {"failed": 1, "passed": 3879, "skipped": 4, "warnings": 1})
        self.assertEqual(proof["pending_operational_steps"], list(PROFILE.PENDING_OPERATIONAL_STEPS))

    def test_wrong_run_identity_or_unfinished_execution_fails_closed(self):
        for key, value in {"id": 1, "head_sha": "0" * 40, "head_branch": "other",
                           "path": ".github/workflows/other.yml", "event": "push",
                           "status": "in_progress", "conclusion": "success", "run_attempt": 2,
                           "repository": {"full_name": "fork/MeuCardio"}}.items():
            run, jobs = evidence()
            run[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.validate(run, jobs)

    def test_job_identity_must_match_the_immutable_baseline(self):
        for index in range(5):
            for key, value in {"run_id": 1, "head_sha": "0" * 40, "run_attempt": 2,
                               "head_branch": "other", "status": "in_progress"}.items():
                run, jobs = evidence()
                jobs["jobs"][index][key] = value
                with self.subTest(index=index, key=key), self.assertRaises(ValueError):
                    self.validate(run, jobs)
        run, jobs = evidence()
        jobs["jobs"][0]["id"] += 1
        with self.assertRaises(ValueError):
            self.validate(run, jobs)

    def test_retained_steps_cannot_be_missing_duplicated_failed_or_skipped(self):
        for name in PROFILE.RETAINED_SUCCESS_STEPS:
            for alteration in ("missing", "duplicate", "failure", "skipped", "pending"):
                run, jobs = evidence()
                steps = jobs["jobs"][0]["steps"]
                step = next(item for item in steps if item["name"] == name)
                if alteration == "missing":
                    steps.remove(step)
                elif alteration == "duplicate":
                    steps.append(deepcopy(step))
                elif alteration == "pending":
                    step.update(status="in_progress", conclusion=None)
                else:
                    step["conclusion"] = alteration
                with self.subTest(name=name, alteration=alteration), self.assertRaises(ValueError):
                    self.validate(run, jobs)

    def test_pytest_failure_and_pending_http_backup_are_required_as_observed(self):
        for name in ("Run pytest", *PROFILE.PENDING_OPERATIONAL_STEPS):
            for alteration in ("success", "pending", "missing"):
                run, jobs = evidence()
                steps = jobs["jobs"][0]["steps"]
                step = next(item for item in steps if item["name"] == name)
                if alteration == "missing":
                    steps.remove(step)
                else:
                    step["conclusion"] = None if alteration == "pending" else alteration
                with self.subTest(name=name, alteration=alteration), self.assertRaises(ValueError):
                    self.validate(run, jobs)

    def test_other_failures_or_incomplete_ambiguous_inventory_are_not_reused(self):
        for alteration in ("truncated", "missing-backend", "duplicate-backend", "extra-job-failure",
                           "frontend-failure", "policy-failure", "focused-success", "extra-step-failure"):
            run, jobs = evidence()
            if alteration == "truncated":
                jobs["total_count"] += 1
            elif alteration == "missing-backend":
                jobs["jobs"].pop(0)
                jobs["total_count"] -= 1
            elif alteration == "duplicate-backend":
                jobs["jobs"].append(deepcopy(jobs["jobs"][0]))
                jobs["total_count"] += 1
            elif alteration == "extra-job-failure":
                job = dict(jobs["jobs"][2], id=1010, name="Unrelated failing job", conclusion="failure")
                jobs["jobs"].append(job)
                jobs["total_count"] += 1
            elif alteration == "extra-step-failure":
                jobs["jobs"][0]["steps"].append({"name": "Other step", "status": "completed", "conclusion": "failure"})
            else:
                index = {"frontend-failure": 3, "policy-failure": 2, "focused-success": 4}[alteration]
                jobs["jobs"][index]["conclusion"] = "success" if index == 4 else "failure"
            with self.subTest(alteration=alteration), self.assertRaises(ValueError):
                self.validate(run, jobs)

    def test_log_requires_only_the_exact_failed_node_and_exact_totals(self):
        original = report()
        variants = [original.replace("3879 passed", "3878 passed"), original.replace("4 skipped", "5 skipped"),
                    original.replace("1 warning", "2 warnings"), original + original,
                    original.replace(PROFILE.TEST_NODE, "tests/test_other.py::test_other"),
                    "\n".join(line for line in original.splitlines() if not line.startswith("FAILED ")),
                    original + "FAILED tests/test_other.py::test_other - second failure\n",
                    original + "ERROR tests/test_setup.py - setup failed\n",
                    original + "!!! Interrupted: collection error !!!\n",
                    original.replace(" in 2200.10s", ", 1 error in 2200.10s")]
        for log in variants:
            with self.subTest(log=log[-70:]), self.assertRaises(ValueError):
                self.validate(log=log)
        ansi = "\n".join("2026-09-11T22:00:00.123Z \x1b[31m" + line + "\x1b[0m" for line in original.splitlines())
        self.assertEqual(self.validate(log=ansi)["result"]["passed"], 3879)


class ArtifactTests(unittest.TestCase):
    def verify(self, archive, metadata=None):
        with patch.object(PROFILE, "ARTIFACT_SHA256", hashlib.sha256(archive).hexdigest()), patch.object(PROFILE, "ARTIFACT_BYTES", len(archive)):
            return PROFILE.validate_artifact(artifact(archive) if metadata is None else metadata, archive)

    def test_one_bounded_pinned_member_is_read_without_extraction(self):
        archive = archive_report()
        with patch.object(zipfile.ZipFile, "extract") as extract, patch.object(zipfile.ZipFile, "extractall") as extractall:
            self.assertEqual(self.verify(archive), report())
        extract.assert_not_called()
        extractall.assert_not_called()

    def test_wrong_artifact_metadata_or_repository_is_rejected(self):
        archive = archive_report()
        for key, value in {"id": 0, "name": "other", "expired": True, "size_in_bytes": 0,
                           "digest": "sha256:" + "0" * 64}.items():
            metadata = artifact(archive)
            metadata[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.verify(archive, metadata)
        for key, value in {"id": 0, "head_sha": "0" * 40, "head_branch": "other",
                           "repository_id": 0, "head_repository_id": 0}.items():
            metadata = artifact(archive)
            metadata["workflow_run"][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.verify(archive, metadata)

    def test_byte_tampering_cannot_reuse_original_artifact_digest(self):
        archive = archive_report()
        with patch.object(PROFILE, "ARTIFACT_SHA256", hashlib.sha256(archive).hexdigest()), patch.object(PROFILE, "ARTIFACT_BYTES", len(archive)), self.assertRaises(ValueError):
            PROFILE.validate_artifact(artifact(archive), archive[:-1] + bytes([archive[-1] ^ 1]))

    def test_extra_unsafe_oversized_or_invalid_members_fail_closed(self):
        for archive in (archive_report(("../pytest-output.txt", "bad")),
                        archive_report(("pytest-output.txt", report()), ("extra.txt", "bad")),
                        archive_report(("pytest-output.txt", b"x" * (PROFILE.MAX_REPORT_BYTES + 1))),
                        archive_report(("pytest-output.txt", b"\xff\xfe")), b"not a zip"):
            with self.subTest(size=len(archive)), self.assertRaises((ValueError, zipfile.BadZipFile)):
                self.verify(archive)


class JUnitTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix="corvia-pr935-junit-")
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.junit = self.root / "followup.xml"

    def xml(self):
        root = ET.Element("testsuites")
        suite = ET.SubElement(root, "testsuite", tests="1", failures="0", errors="0", skipped="0")
        file, name = PROFILE.TEST_NODE.split("::")
        ET.SubElement(suite, "testcase", classname=file.removesuffix(".py").replace("/", "."), name=name)
        return root, suite

    def save(self, root):
        self.junit.write_bytes(ET.tostring(root))

    def test_exact_single_passing_case_is_accepted(self):
        root, _ = self.xml()
        self.save(root)
        self.assertIsNone(PROFILE.validate_followup_junit(self.junit))

    def test_missing_extra_duplicate_or_wrong_test_identity_is_rejected(self):
        for alteration in ("missing", "extra", "duplicate", "wrong-name", "wrong-module"):
            root, suite = self.xml()
            if alteration == "missing":
                suite.remove(suite[0])
            elif alteration == "extra":
                ET.SubElement(suite, "testcase", classname="tests.other", name="test_other")
            elif alteration == "duplicate":
                suite.append(deepcopy(suite[0]))
            else:
                suite[0].set("name" if alteration == "wrong-name" else "classname", "other")
            self.save(root)
            with self.subTest(alteration=alteration), self.assertRaises(ValueError):
                PROFILE.validate_followup_junit(self.junit)

    def test_skip_xfail_failure_error_and_false_totals_are_not_passes(self):
        for tag in ("skipped", "failure", "error"):
            root, suite = self.xml()
            ET.SubElement(suite[0], tag)
            self.save(root)
            with self.subTest(tag=tag), self.assertRaises(ValueError):
                PROFILE.validate_followup_junit(self.junit)
        for key, value in (("tests", "2"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
            root, suite = self.xml()
            suite.set(key, value)
            self.save(root)
            with self.subTest(key=key), self.assertRaises(ValueError):
                PROFILE.validate_followup_junit(self.junit)

    def test_missing_file_multiple_suites_or_hostile_xml_fail_closed(self):
        with self.assertRaises((ValueError, FileNotFoundError)):
            PROFILE.validate_followup_junit(self.junit)
        root, _ = self.xml()
        ET.SubElement(root, "testsuite")
        self.save(root)
        with self.assertRaises(ValueError):
            PROFILE.validate_followup_junit(self.junit)
        for raw in (b"x" * (PROFILE.MAX_REPORT_BYTES + 1), b"<!DOCTYPE x><testsuites/>",
                    b'<!ENTITY x "x"><testsuites/>', b"<broken"):
            self.junit.write_bytes(raw)
            with self.subTest(raw=raw[:30]), self.assertRaises((ValueError, ET.ParseError)):
                PROFILE.validate_followup_junit(self.junit)


class DeltaTests(unittest.TestCase):
    """Exercise the real verifier with an in-memory Git object database."""

    def setUp(self):
        self.root = Path("/offline-fixture/pr935")
        self.source = (b'SELF_SOURCE_SHA256 = None\nREVIEWED_DELTA = {"locked": True}\n'
                       b'TEST_NODE = "literal-node"\n# reviewed executable logic\n')
        self.before = {path: (None if path == "scripts/tests/test_ci_pr935_continuation.py"
                             else ("baseline " + path + "\n").encode())
                       for path in PROFILE.COMPANION_PATHS}
        self.before[PROFILE.SELF_PATH] = None
        self.after = {path: ("reviewed " + path + "\n").encode() for path in PROFILE.COMPANION_PATHS}
        self.after[PROFILE.SELF_PATH] = self.source
        self.changed = set(PROFILE.COMPANION_PATHS) | {PROFILE.SELF_PATH}
        self.modes = {}
        self.dirty = False
        self.ancestor = True
        self.reviewed = {path: {"before": self.digest(self.before[path]), "after": self.digest(self.after[path])}
                         for path in PROFILE.COMPANION_PATHS}
        for name, value in (("REVIEWED_DELTA", self.reviewed),
                            ("SELF_SOURCE_SHA256", PROFILE.normalized_self_hash(self.source))):
            patcher = patch.object(PROFILE, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        patcher = patch.object(PROFILE, "_git", side_effect=self.git)
        patcher.start()
        self.addCleanup(patcher.stop)

    @staticmethod
    def digest(value):
        return None if value is None else hashlib.sha256(value).hexdigest()

    def git(self, root, *args, binary=False):
        self.assertEqual(root, self.root)
        if args == ("merge-base", "--is-ancestor", PROFILE.BASELINE_SHA, "HEAD"):
            if not self.ancestor:
                raise ValueError("Baseline is not an ancestor")
            return ""
        if args == ("status", "--porcelain", "--untracked-files=no"):
            return " M backend/app/auth.py" if self.dirty else ""
        if args == ("diff", "--no-renames", "--name-only", f"{PROFILE.BASELINE_SHA}..HEAD"):
            return "\n".join(sorted(self.changed))
        if len(args) == 4 and args[0] == "ls-tree" and args[2] == "--":
            ref, path = args[1], args[3]
            objects = self.after if ref == "HEAD" else self.before
            if objects.get(path) is None:
                return ""
            return self.modes.get((ref, path), "100644") + " blob " + "c" * 40 + "\t" + path
        if len(args) == 2 and args[0] == "show":
            ref, path = args[1].split(":", 1)
            self.assertTrue(binary)
            value = (self.after if ref == "HEAD" else self.before)[path]
            if value is None:
                raise ValueError("Missing fixture blob")
            return value
        raise AssertionError(f"Unexpected Git command: {args!r}")

    def test_exact_five_companions_and_new_self_are_verified_byte_for_byte(self):
        self.assertEqual(PROFILE.COMPANION_PATHS, frozenset({
            "backend/tests/test_panel_acervo_comunicacao_contract.py",
            "docs/qa/2026-09-11-auditoria-funcoes-atelier.md", ".github/workflows/ci.yml",
            "scripts/ci_backend_followup.py", "scripts/tests/test_ci_pr935_continuation.py"}))
        proof = PROFILE.validate_delta(self.root)
        self.assertEqual(set(proof), self.changed)
        for path, expected in self.reviewed.items():
            self.assertEqual(proof[path], expected)
        self.assertIsNone(proof[PROFILE.SELF_PATH]["before"])

    def test_unsealed_or_incomplete_companion_map_cannot_issue_a_decision(self):
        for name, value in (("REVIEWED_DELTA", None), ("REVIEWED_DELTA", {}), ("SELF_SOURCE_SHA256", None)):
            with self.subTest(name=name, value=value), patch.object(PROFILE, name, value), self.assertRaises(ValueError):
                PROFILE.validate_delta(self.root)
        for alteration in ("missing", "extra", "self-override"):
            reviewed = deepcopy(self.reviewed)
            if alteration == "missing":
                reviewed.pop(sorted(reviewed)[0])
            else:
                reviewed[PROFILE.SELF_PATH if alteration == "self-override" else "backend/app/auth.py"] = {
                    "before": None, "after": "0" * 64}
            with self.subTest(alteration=alteration), patch.object(PROFILE, "REVIEWED_DELTA", reviewed), self.assertRaises(ValueError):
                PROFILE.validate_delta(self.root)

    def test_before_and_after_hashes_are_compared_not_merely_reported(self):
        for path in sorted(self.reviewed):
            for side in ("before", "after"):
                reviewed = deepcopy(self.reviewed)
                reviewed[path][side] = "0" * 64
                with self.subTest(path=path, side=side), patch.object(PROFILE, "REVIEWED_DELTA", reviewed), self.assertRaises(ValueError):
                    PROFILE.validate_delta(self.root)

    def test_any_extra_product_change_or_missing_approved_path_is_rejected(self):
        for path in ("backend/app/api/auth.py", "backend/app/services/pricing/kairos_provider.py",
                     "frontend/src/pages/Home.tsx", "backend/conftest.py"):
            self.changed.add(path)
            with self.subTest(path=path), self.assertRaises(ValueError):
                PROFILE.validate_delta(self.root)
            self.changed.remove(path)
        self.changed.remove(sorted(PROFILE.COMPANION_PATHS)[0])
        with self.assertRaises(ValueError):
            PROFILE.validate_delta(self.root)

    def test_dirty_checkout_or_nonancestor_baseline_fails_closed(self):
        self.dirty = True
        with self.assertRaises(ValueError):
            PROFILE.validate_delta(self.root)
        self.dirty = False
        self.ancestor = False
        with self.assertRaises(ValueError):
            PROFILE.validate_delta(self.root)

    def test_executable_symlink_removed_or_preexisting_self_is_ineligible(self):
        path = "scripts/ci_backend_followup.py"
        for mode in ("100755", "120000"):
            self.modes[("HEAD", path)] = mode
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                PROFILE.validate_delta(self.root)
        self.modes.clear()
        original = self.after[path]
        self.after[path] = None
        with self.assertRaises(ValueError):
            PROFILE.validate_delta(self.root)
        self.after[path] = original
        self.before[PROFILE.SELF_PATH] = b"preexisting implementation"
        with self.assertRaises(ValueError):
            PROFILE.validate_delta(self.root)

    def test_self_hash_normalizes_only_its_own_literal_not_rules_or_executable_source(self):
        rewritten = self.source.replace(b"SELF_SOURCE_SHA256 = None", b'SELF_SOURCE_SHA256 = "' + b"0" * 64 + b'"')
        self.assertEqual(PROFILE.normalized_self_hash(self.source), PROFILE.normalized_self_hash(rewritten))
        for old, new in ((b'"locked": True', b'"locked": False'),
                         (b'"literal-node"', b'"other-node"'), (b"reviewed executable logic", b"changed executable logic")):
            changed = self.source.replace(old, new)
            self.assertNotEqual(PROFILE.normalized_self_hash(self.source), PROFILE.normalized_self_hash(changed))
            self.after[PROFILE.SELF_PATH] = changed
            with self.subTest(old=old), self.assertRaises(ValueError):
                PROFILE.validate_delta(self.root)
        for source in (b"# missing digest\n", self.source + b"SELF_SOURCE_SHA256 = None\n"):
            with self.subTest(source=source[:30]), self.assertRaises(ValueError):
                PROFILE.normalized_self_hash(source)


class DecisionTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix="corvia-pr935-decision-")
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.candidate = "a" * 40
        self.tree = "b" * 40
        self.delta = {"backend/tests/test_panel_acervo_comunicacao_contract.py":
                      {"before": "1" * 64, "after": "2" * 64}}

    def git(self, root, *args, binary=False):
        self.assertEqual(root, self.root)
        if args == ("rev-parse", "HEAD"):
            return self.candidate
        if args == ("rev-parse", "HEAD^{tree}"):
            return self.tree
        if args == ("ls-tree", "HEAD", "--", PROFILE.SELF_PATH):
            return "100644 blob " + "c" * 40 + "\t" + PROFILE.SELF_PATH
        raise AssertionError(f"Unexpected local Git command: {args!r}")

    def context(self, *, pr_change=None, baseline_change=None, associated=None, main=None, artifacts_change=None):
        run, jobs = evidence()
        if baseline_change:
            baseline_change(run, jobs)
        pr = {"number": PROFILE.PR_NUMBER, "merged": True, "merge_commit_sha": self.candidate,
              "base": {"ref": "main", "repo": {"full_name": PROFILE.REPOSITORY}},
              "head": {"ref": PROFILE.BRANCH, "sha": self.candidate,
                       "repo": {"full_name": PROFILE.REPOSITORY}}}
        if pr_change:
            pr_change(pr)
        archive = archive_report()
        artifacts = {"artifacts": [artifact(archive)]}
        if artifacts_change:
            artifacts_change(artifacts)
        responses = {
            f"repos/{PROFILE.REPOSITORY}/pulls/{PROFILE.PR_NUMBER}": pr,
            f"repos/{PROFILE.REPOSITORY}/commits/{self.candidate}/pulls":
                [{"number": PROFILE.PR_NUMBER}] if associated is None else associated,
            f"repos/{PROFILE.REPOSITORY}/git/ref/heads/main": {"object": {"sha": self.candidate if main is None else main}},
            f"repos/{PROFILE.REPOSITORY}/actions/runs/{PROFILE.BASELINE_RUN_ID}": run,
            f"repos/{PROFILE.REPOSITORY}/actions/runs/{PROFILE.BASELINE_RUN_ID}/attempts/1/jobs?per_page=100": jobs,
            f"repos/{PROFILE.REPOSITORY}/actions/runs/{PROFILE.BASELINE_RUN_ID}/artifacts?per_page=100": artifacts,
        }
        stack = ExitStack()
        stack.enter_context(patch.dict(os.environ, {"RUNNER_TEMP": str(self.root)}))
        self.api = stack.enter_context(patch.object(PROFILE, "_github", side_effect=lambda path: deepcopy(responses[path])))
        self.binary = stack.enter_context(patch.object(PROFILE, "_github_binary", return_value=archive))
        stack.enter_context(patch.object(PROFILE, "_git", side_effect=self.git))
        self.check_delta = stack.enter_context(patch.object(PROFILE, "validate_delta", return_value=self.delta))
        stack.enter_context(patch.object(PROFILE, "ARTIFACT_SHA256", hashlib.sha256(archive).hexdigest()))
        stack.enter_context(patch.object(PROFILE, "ARTIFACT_BYTES", len(archive)))
        return stack

    def resolve(self, *, event="pull_request", number="935", branch=None, repository=None):
        return PROFILE.resolve_decision(self.root, event=event, number=number,
                                        head_ref=PROFILE.BRANCH if branch is None else branch,
                                        repository=PROFILE.REPOSITORY if repository is None else repository)

    def test_exact_pr_and_fast_forward_promotion_have_one_literal_target_and_same_key(self):
        with self.context():
            pr = self.resolve()
            push = self.resolve(event="push", number="", branch="")
        self.assertEqual(pr.backend_mode, PROFILE.MODE)
        self.assertEqual(pr.focused_tests, (PROFILE.TEST_NODE,))
        self.assertEqual(pr.suite_key, push.suite_key)
        self.assertTrue(pr.suite_key.startswith(PROFILE.SUITE_PREFIX))
        proof = json.loads((self.root / PROFILE.EVIDENCE_NAME).read_text())
        self.assertEqual(proof["candidate_sha"], self.candidate)
        self.assertEqual(proof["baseline"]["result"]["failed"], 1)
        self.assertIsNone(proof["baseline"]["full_certificate"])
        self.binary.assert_called_with(f"repos/{PROFILE.REPOSITORY}/actions/artifacts/{PROFILE.ARTIFACT_ID}/zip")

    def test_future_pr_same_branch_or_wrong_repository_cannot_borrow_the_profile(self):
        for kwargs in ({"number": "936"}, {"branch": "other"}, {"repository": "fork/MeuCardio"}):
            with self.context(), self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                self.resolve(**kwargs)
            self.check_delta.assert_not_called()

    def test_unrelated_pr_does_not_trigger_the_exception_or_network(self):
        with patch.object(PROFILE, "_github") as api:
            self.assertIsNone(self.resolve(number="999", branch="other"))
        api.assert_not_called()

    def test_pr_head_base_number_and_repository_must_match_exactly(self):
        mutations = [lambda pr: pr.update(number=936), lambda pr: pr["head"].update(sha="0" * 40),
                     lambda pr: pr["head"].update(ref="other"), lambda pr: pr["base"].update(ref="other"),
                     lambda pr: pr["head"]["repo"].update(full_name="fork/MeuCardio"),
                     lambda pr: pr["base"]["repo"].update(full_name="fork/MeuCardio")]
        for mutation in mutations:
            with self.context(pr_change=mutation), self.subTest(mutation=mutation), self.assertRaises(ValueError):
                self.resolve()
            self.check_delta.assert_not_called()

    def test_push_requires_exact_merged_head_main_and_unambiguous_association(self):
        variants = [{"pr_change": lambda pr: pr.update(merged=False)},
                    {"pr_change": lambda pr: pr.update(merge_commit_sha="0" * 40)},
                    {"main": "0" * 40}, {"associated": []},
                    {"associated": [{"number": 935}, {"number": 935}]}]
        for variant in variants:
            with self.context(**variant), self.subTest(variant=variant), self.assertRaises(ValueError):
                self.resolve(event="push", number="", branch="")
            self.check_delta.assert_not_called()

    def test_unrelated_future_push_does_not_take_pr935_continuation(self):
        with self.context(associated=[{"number": 999}], pr_change=lambda pr: (
                pr["head"].update(sha="0" * 40), pr.update(merge_commit_sha="1" * 40))):
            self.assertIsNone(self.resolve(event="push", number="", branch=""))
        self.check_delta.assert_not_called()

    def test_failed_provenance_never_writes_a_certificate_or_silently_falls_back(self):
        for field, value in (("status", "in_progress"), ("conclusion", "success")):
            with self.context(baseline_change=lambda run, jobs: run.update({field: value})), self.subTest(field=field), self.assertRaises(ValueError):
                self.resolve()
            self.assertFalse((self.root / PROFILE.EVIDENCE_NAME).exists())
        for change in (lambda data: data.update(artifacts=[]),
                       lambda data: data["artifacts"].append(deepcopy(data["artifacts"][0]))):
            with self.context(artifacts_change=change), self.assertRaises(ValueError):
                self.resolve()
            self.assertFalse((self.root / PROFILE.EVIDENCE_NAME).exists())
        with self.context(), patch.object(PROFILE, "validate_delta", side_effect=ValueError("Unreviewed runtime delta")), self.assertRaises(ValueError):
            self.resolve()
        self.assertFalse((self.root / PROFILE.EVIDENCE_NAME).exists())

    def test_missing_github_evidence_is_fatal_before_any_decision(self):
        with self.context(), patch.object(PROFILE, "_github", side_effect=ValueError("Unavailable evidence")), self.assertRaises(ValueError):
            self.resolve()
        self.assertFalse((self.root / PROFILE.EVIDENCE_NAME).exists())


class RunnerTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix="corvia-pr935-runner-")
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.junit = self.root / "followup.xml"
        self.source = b'SELF_SOURCE_SHA256 = None\n# isolated executable source\n'
        script = self.root / PROFILE.SELF_PATH
        script.parent.mkdir(parents=True, exist_ok=True)
        script.write_bytes(self.source)
        test_file, test_name = PROFILE.TEST_NODE.split("::")
        target = self.root / "backend" / test_file
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(f"def {test_name}():\n    pass\n", encoding="utf-8")

    def context(self, *, env_change=None, returncode=0, emit=True):
        env = {"FOCUSED_TESTS": PROFILE.TEST_NODE, "CANDIDATE_SHA": "a" * 40,
               "SUITE_KEY": PROFILE.SUITE_PREFIX + "b" * 16,
               "PYTEST_ADDOPTS": "tests --ignore=tests/test_panel_acervo_comunicacao_contract.py",
               "PYTEST_PLUGINS": "unreviewed_plugin"}
        env.update(env_change or {})
        def child(command, **kwargs):
            if emit and returncode == 0:
                root, _ = JUnitTests.xml(self)
                self.junit.write_bytes(ET.tostring(root))
            return subprocess.CompletedProcess(command, returncode)
        stack = ExitStack()
        stack.enter_context(patch.dict(os.environ, env))
        stack.enter_context(patch.object(PROFILE, "_git", return_value="a" * 40))
        stack.enter_context(patch.object(PROFILE, "SELF_SOURCE_SHA256", PROFILE.normalized_self_hash(self.source)))
        stack.enter_context(patch.object(PROFILE, "validate_delta", return_value={"verified": True}))
        self.child = stack.enter_context(patch.object(PROFILE.subprocess, "run", side_effect=child))
        return stack

    def test_runner_executes_only_literal_node_and_clears_environment_config_injection(self):
        with self.context():
            self.assertEqual(PROFILE.run_followup(self.root, self.junit), 0)
        self.child.assert_called_once()
        args, kwargs = self.child.call_args
        self.assertEqual(args[0], [sys.executable, "-m", "pytest", "-q", "--tb=short", "--rootdir=.",
                                  "-o", "addopts=", PROFILE.TEST_NODE, "--junitxml=" + str(self.junit.resolve())])
        self.assertEqual(kwargs["cwd"], self.root / "backend")
        self.assertNotIn("PYTEST_ADDOPTS", kwargs["env"])
        self.assertNotIn("PYTEST_PLUGINS", kwargs["env"])
        self.assertFalse(kwargs.get("shell", False))

    def test_wrong_selection_sha_scope_or_unsealed_source_stops_before_child(self):
        for env in ({"FOCUSED_TESTS": ""}, {"FOCUSED_TESTS": "tests"},
                    {"FOCUSED_TESTS": PROFILE.TEST_NODE + " tests/test_extra.py"},
                    {"CANDIDATE_SHA": "c" * 40}, {"SUITE_KEY": "backend-risk-v1-full"}):
            with self.context(env_change=env), self.subTest(env=env), self.assertRaises(ValueError):
                PROFILE.run_followup(self.root, self.junit)
            self.child.assert_not_called()
        with self.context(), patch.object(PROFILE, "SELF_SOURCE_SHA256", "0" * 64), self.assertRaises(ValueError):
            PROFILE.run_followup(self.root, self.junit)
        self.child.assert_not_called()

    def test_child_failure_is_returned_without_success_certificate(self):
        with self.context(returncode=1):
            self.assertEqual(PROFILE.run_followup(self.root, self.junit), 1)
        self.assertFalse(self.junit.exists())

    def test_exit_zero_without_new_junit_cannot_reuse_old_passing_report(self):
        with self.context(emit=False), self.assertRaises((ValueError, FileNotFoundError)):
            PROFILE.run_followup(self.root, self.junit)
        self.child.assert_called_once()
        root, _ = JUnitTests.xml(self)
        self.junit.write_bytes(ET.tostring(root))
        with self.context(emit=False), self.assertRaises((ValueError, FileNotFoundError)):
            PROFILE.run_followup(self.root, self.junit)
        self.child.assert_not_called()


if __name__ == "__main__":
    unittest.main()
