"""Offline PR934 provenance tests; never invoke backend pytest, DB or GitHub."""
from __future__ import annotations

from copy import deepcopy
from contextlib import ExitStack
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
    "ci_backend_pr934_continuation", ROOT / "scripts/ci_backend_pr934_continuation.py")
assert SPEC and SPEC.loader
PROFILE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = PROFILE
SPEC.loader.exec_module(PROFILE)


def evidence():
    run = {"id": PROFILE.BASELINE_RUN_ID, "head_sha": PROFILE.BASELINE_SHA,
           "head_branch": PROFILE.BRANCH, "path": ".github/workflows/ci.yml",
           "event": "pull_request", "status": "completed", "conclusion": "failure",
           "run_attempt": 1, "repository": {"full_name": PROFILE.REPOSITORY},
           # GitHub mutates this association after a new PR commit. It is not
           # evidence of the immutable baseline SHA, unlike run/job head_sha.
           "pull_requests": [{"number": 934, "head": {"sha": "f" * 40}}]}
    common = {"run_id": PROFILE.BASELINE_RUN_ID, "head_sha": PROFILE.BASELINE_SHA,
              "head_branch": PROFILE.BRANCH, "run_attempt": 1,
              "status": "completed", "conclusion": "success"}
    jobs = [dict(common, id=PROFILE.BASELINE_JOB_ID, name="Backend tests", conclusion="failure", steps=[
        {"name": name, "status": "completed", "conclusion": "success"}
        for name in PROFILE.RETAINED_SUCCESS_STEPS] + [
            {"name": "Run pytest", "status": "completed", "conclusion": "failure"},
            *[{"name": name, "status": "completed", "conclusion": "skipped"}
              for name in PROFILE.PENDING_OPERATIONAL_STEPS]]),
        dict(common, id=1002, name="Backend risk gate", conclusion="failure"),
        dict(common, id=1003, name="Backend risk policy"),
        dict(common, id=1004, name="Frontend build", conclusion="failure")]
    return run, {"total_count": len(jobs), "jobs": jobs}


def report():
    return "\n".join("FAILED " + node + " - synthetic fixture" for node in PROFILE.FAILED_TEST_NODES) + (
        "\n6 failed, 3810 passed, 4 skipped, 1 warning in 2240.10s (0:37:20)\n")


def validate(run, jobs, log=None):
    return PROFILE.validate_baseline(run, jobs, report() if log is None else log)


def zip_report(*members):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, content in members or (("pytest-output.txt", report()),):
            archive.writestr(name, content)
    return stream.getvalue()


def artifact(archive):
    return {"id": PROFILE.ARTIFACT_ID, "name": "backend-pytest-failure", "expired": False,
            "size_in_bytes": len(archive), "digest": "sha256:" + hashlib.sha256(archive).hexdigest(),
            "workflow_run": {"id": PROFILE.BASELINE_RUN_ID, "head_sha": PROFILE.BASELINE_SHA,
                             "head_branch": PROFILE.BRANCH, "repository_id": 1312508910,
                             "head_repository_id": 1312508910}}


class BaselineTests(unittest.TestCase):
    def test_exact_failed_baseline_keeps_passes_and_pending_operational_gates_honest(self):
        run, jobs = evidence()
        proof = validate(run, jobs)
        self.assertIsNone(proof["full_certificate"])
        self.assertEqual(proof["run_conclusion"], "failure")
        self.assertEqual(proof["result"], {"failed": 6, "passed": 3810, "skipped": 4, "warnings": 1})
        self.assertEqual(proof["pending_operational_steps"], list(PROFILE.PENDING_OPERATIONAL_STEPS))

    def test_run_identity_and_completion_are_mandatory(self):
        for key, value in {"id": 1, "head_sha": "0" * 40, "head_branch": "other",
                           "path": ".github/workflows/other.yml", "event": "push",
                           "status": "in_progress", "conclusion": "cancelled", "run_attempt": 2,
                           "repository": {"full_name": "fork/MeuCardio"}}.items():
            run, jobs = evidence()
            run[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate(run, jobs)

    def test_backend_and_gate_require_exact_original_job_metadata(self):
        for job_index in (0, 1):
            for key, value in {"run_id": 1, "head_sha": "0" * 40, "run_attempt": 2,
                               "head_branch": "other", "status": "in_progress",
                               "conclusion": "success"}.items():
                run, jobs = evidence()
                jobs["jobs"][job_index][key] = value
                with self.subTest(job=job_index, key=key), self.assertRaises(ValueError):
                    validate(run, jobs)
        run, jobs = evidence()
        jobs["jobs"][0]["id"] += 1
        with self.assertRaises(ValueError):
            validate(run, jobs)
        for key in ("run_attempt", "head_branch"):
            run, jobs = evidence()
            del jobs["jobs"][0][key]
            with self.subTest(missing=key), self.assertRaises(ValueError):
                validate(run, jobs)

    def test_every_full_gate_must_succeed_not_only_pytest(self):
        for name in PROFILE.RETAINED_SUCCESS_STEPS:
            for alteration in ("missing", "duplicate", "failure", "skipped", "pending"):
                run, jobs = evidence()
                steps = jobs["jobs"][0]["steps"]
                step = next(s for s in steps if s["name"] == name)
                if alteration == "missing":
                    steps.remove(step)
                elif alteration == "duplicate":
                    steps.append(deepcopy(step))
                elif alteration == "pending":
                    step.update(status="pending", conclusion=None)
                else:
                    step["conclusion"] = alteration
                with self.subTest(name=name, alteration=alteration), self.assertRaises(ValueError):
                    validate(run, jobs)

    def test_pytest_failed_and_operational_gates_skipped_are_not_passed_evidence(self):
        for name in ("Run pytest", *PROFILE.PENDING_OPERATIONAL_STEPS):
            for conclusion in ("success", None):
                run, jobs = evidence()
                next(s for s in jobs["jobs"][0]["steps"] if s["name"] == name)["conclusion"] = conclusion
                with self.subTest(name=name, conclusion=conclusion), self.assertRaises(ValueError):
                    validate(run, jobs)
        run, jobs = evidence()
        jobs["jobs"][0]["steps"].append({"name": "Upload artifact", "status": "completed", "conclusion": "failure"})
        with self.assertRaises(ValueError):
            validate(run, jobs)

    def test_exact_failed_nodes_totals_no_error_or_interruption_are_required(self):
        run, jobs = evidence()
        original = report()
        variants = [original.replace("3810 passed", "3809 passed"), original.replace("4 skipped", "5 skipped"),
                    original.replace("1 warning", "2 warnings"), original + original,
                    original.replace(PROFILE.FAILED_TEST_NODES[0], "tests/test_other.py::test_other"),
                    "\n".join(original.splitlines()[1:]), original + "ERROR tests/test_setup.py - setup\n",
                    original + "!!! Interrupted: collection error !!!\n", original.replace(" in 2240.10s", ", 1 error in 2240.10s")]
        for log in variants:
            with self.subTest(log=log[-80:]), self.assertRaises(ValueError):
                validate(run, jobs, log)
        ansi = "\n".join("2026-09-11T19:26:00.123Z \x1b[31m" + line + "\x1b[0m" for line in original.splitlines())
        self.assertEqual(validate(run, jobs, ansi)["result"]["failed"], 6)

    def test_unknown_failure_incomplete_or_ambiguous_inventory_is_rejected(self):
        for alteration in ("truncated", "missing-backend", "duplicate-backend", "unknown-failure",
                           "cancelled", "in-progress", "wrong-run-conclusion"):
            run, jobs = evidence()
            if alteration == "truncated":
                jobs["total_count"] += 1
            elif alteration == "missing-backend":
                jobs["jobs"].pop(0)
                jobs["total_count"] -= 1
            elif alteration == "duplicate-backend":
                jobs["jobs"].append(deepcopy(jobs["jobs"][0]))
                jobs["total_count"] += 1
            elif alteration == "unknown-failure":
                jobs["jobs"][2]["conclusion"] = "failure"
            elif alteration == "cancelled":
                jobs["jobs"][2]["conclusion"] = "cancelled"
            elif alteration == "in-progress":
                jobs["jobs"][2]["status"] = "in_progress"
            else:
                run["conclusion"] = "success"
            with self.subTest(alteration=alteration), self.assertRaises(ValueError):
                validate(run, jobs)


class ArtifactTests(unittest.TestCase):
    def verify(self, archive, metadata=None):
        with patch.object(PROFILE, "ARTIFACT_SHA256", hashlib.sha256(archive).hexdigest()), patch.object(PROFILE, "ARTIFACT_BYTES", len(archive)):
            return PROFILE.validate_artifact(metadata or artifact(archive), archive)

    def test_single_bounded_member_is_read_without_extracting(self):
        archive = zip_report()
        with patch.object(zipfile.ZipFile, "extract") as extract, patch.object(zipfile.ZipFile, "extractall") as extractall:
            self.assertEqual(self.verify(archive), report())
        extract.assert_not_called()
        extractall.assert_not_called()

    def test_original_identity_digest_expiry_size_and_provenance_are_required(self):
        archive = zip_report()
        for key, value in {"id": 0, "name": "other", "expired": True, "size_in_bytes": 0, "digest": "sha256:" + "0" * 64}.items():
            metadata = artifact(archive)
            metadata[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.verify(archive, metadata)
        for key, value in {"id": 0, "head_sha": "0" * 40, "head_branch": "other", "repository_id": 0, "head_repository_id": 0}.items():
            metadata = artifact(archive)
            metadata["workflow_run"][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.verify(archive, metadata)

    def test_wrong_archive_bytes_member_or_encoding_fail_closed(self):
        original = zip_report()
        with patch.object(PROFILE, "ARTIFACT_SHA256", hashlib.sha256(original).hexdigest()), patch.object(PROFILE, "ARTIFACT_BYTES", len(original)), self.assertRaises(ValueError):
            PROFILE.validate_artifact(artifact(original), original[:-1] + b"x")
        for archive in (zip_report(("../pytest-output.txt", "bad")), zip_report(("pytest-output.txt", "ok"), ("extra", "bad")),
                        zip_report(("pytest-output.txt", b"x" * (PROFILE.MAX_REPORT_BYTES + 1))),
                        zip_report(("pytest-output.txt", b"\xff\xfe")), b"not a zip"):
            with self.subTest(size=len(archive)), self.assertRaises((ValueError, zipfile.BadZipFile)):
                self.verify(archive)


class GitProfileTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="corvia-ci-pr934-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git("init", "-q")
        self.write("backend/app/data/pricing/snapshot.json", "baseline bytes\n")
        self.write("medicamentos/old-audit.json", "source audit\n")
        self.write("backend/tests/test_pricing.py", "# selected offline fixture\n")
        for node in PROFILE.FAILED_TEST_NODES:
            test, name = node.split("::")
            self.write("backend/" + test, "def " + name + "():\n    pass\n")
        self.write("scripts/ci_backend_followup.py", "# old wrapper\n")
        self.write(".github/workflows/ci.yml", "# old workflow\n")
        self.commit()
        self.baseline = self.git("rev-parse", "HEAD")
        self.write("backend/app/data/pricing/snapshot.json", "reviewed same prices, new location\n")
        self.write("backend/app/data/pricing/new-audit.json", "source audit\n")
        (self.root / "medicamentos/old-audit.json").unlink()
        for path in PROFILE.POLICY_PATHS - {PROFILE.SELF_PATH}:
            self.write(path, "# reviewed policy fixture " + path + "\n")
        self.write(PROFILE.SELF_PATH, 'SELF_SOURCE_SHA256 = None\nREVIEWED_DELTA = {"locked": True}\n'
                   'FOCUSED_TESTS = ("literal",)\n# reviewed executable logic\n')
        self.commit()
        self.candidate = self.git("rev-parse", "HEAD")
        product_paths = {"backend/app/data/pricing/snapshot.json", "backend/app/data/pricing/new-audit.json",
                         "medicamentos/old-audit.json"}
        self.reviewed = self.hashes(product_paths)
        self.policy = self.hashes(PROFILE.POLICY_PATHS - {PROFILE.SELF_PATH})
        self.self_hash = PROFILE.normalized_self_hash((self.root / PROFILE.SELF_PATH).read_bytes())
        for key, value in {"BASELINE_SHA": self.baseline, "REVIEWED_DELTA": self.reviewed,
                           "POLICY_DELTA": self.policy, "SELF_SOURCE_SHA256": self.self_hash,
                           "FOCUSED_TESTS": ("tests/test_pricing.py",)}.items():
            patcher = patch.object(PROFILE, key, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        env_patch = patch.dict(os.environ, {"RUNNER_TEMP": str(self.root)})
        env_patch.start()
        self.addCleanup(env_patch.stop)

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.root), *args], text=True,
                                       stderr=subprocess.DEVNULL).strip()

    def write(self, path, text):
        file = self.root / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(text, encoding="utf-8")

    def commit(self):
        self.git("add", ".")
        self.git("-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false",
                 "-c", "user.name=Offline Fixture", "-c", "user.email=fixture@example.invalid",
                 "commit", "-qm", "isolated evidence")

    def hashes(self, paths):
        return {path: {"before": PROFILE._sha256_blob(self.root, self.baseline, path),
                       "after": PROFILE._sha256_blob(self.root, "HEAD", path)} for path in paths}

    def api(self, *, pr_change=None, baseline_change=None, associated=None, main=None):
        run, jobs = evidence()
        if baseline_change:
            baseline_change(run, jobs)
        pr = {"number": 934, "merged": True, "merge_commit_sha": self.candidate,
              "base": {"ref": "main", "repo": {"full_name": PROFILE.REPOSITORY}},
              "head": {"ref": PROFILE.BRANCH, "sha": self.candidate,
                       "repo": {"full_name": PROFILE.REPOSITORY}}}
        if pr_change:
            pr_change(pr)
        archive = zip_report()
        responses = {
            f"repos/{PROFILE.REPOSITORY}/pulls/934": pr,
            f"repos/{PROFILE.REPOSITORY}/commits/{self.candidate}/pulls":
                [{"number": 934}] if associated is None else associated,
            f"repos/{PROFILE.REPOSITORY}/git/ref/heads/main": {"object": {"sha": main or self.candidate}},
            f"repos/{PROFILE.REPOSITORY}/actions/runs/{PROFILE.BASELINE_RUN_ID}": run,
            f"repos/{PROFILE.REPOSITORY}/actions/runs/{PROFILE.BASELINE_RUN_ID}/attempts/1/jobs?per_page=100": jobs,
            f"repos/{PROFILE.REPOSITORY}/actions/runs/{PROFILE.BASELINE_RUN_ID}/artifacts?per_page=100": {"artifacts": [artifact(archive)]},
        }
        stack = ExitStack()
        stack.enter_context(patch.object(PROFILE, "_github", side_effect=lambda path: deepcopy(responses[path])))
        stack.enter_context(patch.object(PROFILE, "_github_binary", return_value=archive))
        stack.enter_context(patch.object(PROFILE, "ARTIFACT_SHA256", hashlib.sha256(archive).hexdigest()))
        stack.enter_context(patch.object(PROFILE, "ARTIFACT_BYTES", len(archive)))
        return stack

    def resolve(self, event="pull_request", number="934", branch=None, repo=None):
        return PROFILE.resolve_decision(self.root, event=event, number=number,
                                        head_ref=PROFILE.BRANCH if branch is None else branch,
                                        repository=repo or PROFILE.REPOSITORY)

    def test_exact_closed_delta_includes_addition_removal_and_policy_pins(self):
        proof = PROFILE.validate_delta(self.root)
        self.assertEqual(set(proof), set(self.reviewed) | PROFILE.POLICY_PATHS)
        self.assertIsNone(proof["medicamentos/old-audit.json"]["after"])
        self.assertIsNone(proof["backend/app/data/pricing/new-audit.json"]["before"])

    def test_unsealed_profile_cannot_issue_any_decision(self):
        for key, value in (("REVIEWED_DELTA", None), ("FOCUSED_TESTS", ()),
                           ("POLICY_DELTA", None), ("SELF_SOURCE_SHA256", None)):
            with self.subTest(key=key), patch.object(PROFILE, key, value), self.api(), self.assertRaisesRegex(ValueError, "not sealed"):
                self.resolve()

    def test_before_after_and_policy_hashes_are_compared_not_just_recorded(self):
        for mapping in (self.reviewed, self.policy):
            path = sorted(mapping)[0]
            for side in ("before", "after"):
                original = mapping[path][side]
                mapping[path][side] = "0" * 64
                with self.subTest(path=path, side=side), self.assertRaisesRegex(ValueError, "hash differs"):
                    PROFILE.validate_delta(self.root)
                mapping[path][side] = original

    def test_any_extra_runtime_or_policy_change_invalidates_the_profile(self):
        for path in ("backend/app/auth.py", "scripts/ci_backend_followup.py",
                     ".github/workflows/ci.yml", "scripts/tests/test_ci_pr934_continuation.py",
                     PROFILE.SELF_PATH):
            self.git("checkout", "-q", self.candidate)
            self.write(path, (self.root / path).read_text() + "# extra delta\n" if (self.root / path).exists() else "# forbidden runtime\n")
            self.commit()
            with self.subTest(path=path), self.assertRaises(ValueError):
                PROFILE.validate_delta(self.root)

    def test_self_digest_excludes_only_its_own_literal(self):
        source = (self.root / PROFILE.SELF_PATH).read_bytes()
        changed_literal = source.replace(b"SELF_SOURCE_SHA256 = None", b'SELF_SOURCE_SHA256 = "' + b"0" * 64 + b'"')
        self.assertEqual(PROFILE.normalized_self_hash(source), PROFILE.normalized_self_hash(changed_literal))
        for old, new in ((b'"locked": True', b'"locked": False'), (b'"literal"', b'"other-test"'),
                         (b"reviewed executable logic", b"changed executable logic")):
            self.assertNotEqual(PROFILE.normalized_self_hash(source), PROFILE.normalized_self_hash(source.replace(old, new)))
        for bad in (b"# no declaration", source + b"SELF_SOURCE_SHA256 = None\n"):
            with self.assertRaises(ValueError):
                PROFILE.normalized_self_hash(bad)

    def test_tracked_dirty_worktree_and_nonancestor_fail_closed(self):
        self.write("backend/app/data/pricing/snapshot.json", "uncommitted\n")
        with self.assertRaisesRegex(ValueError, "uncommitted"):
            PROFILE.validate_delta(self.root)
        self.git("checkout", "--", "backend/app/data/pricing/snapshot.json")
        with patch.object(PROFILE, "BASELINE_SHA", "0" * 40), self.assertRaises(ValueError):
            PROFILE.validate_delta(self.root)

    def test_symlink_executable_or_removed_policy_is_not_eligible(self):
        path = "scripts/ci_backend_followup.py"
        for alteration in ("symlink", "executable", "deleted"):
            self.git("checkout", "-q", self.candidate)
            file = self.root / path
            if alteration == "executable":
                self.git("update-index", "--chmod=+x", path)
                file.chmod(0o755)
            else:
                file.unlink()
                if alteration == "symlink":
                    file.symlink_to("/tmp/not-followed")
            self.commit()
            with self.subTest(alteration=alteration), self.assertRaises(ValueError):
                PROFILE.validate_delta(self.root)

    def test_test_list_is_literal_existing_and_nonduplicated(self):
        for tests in (("tests/test_missing.py",), ("tests/test_pricing.py::test_one",),
                      ("tests/test_pricing.py;echo",), ("../test_outside.py",),
                      ("tests/test_pricing.py", "tests/test_pricing.py")):
            with self.subTest(tests=tests), patch.object(PROFILE, "FOCUSED_TESTS", tests), self.assertRaises(ValueError):
                PROFILE.validate_delta(self.root)

    def test_pr_and_exact_ff_push_have_same_focused_key_and_explicit_proof(self):
        with self.api():
            pr = self.resolve()
            push = self.resolve(event="push", number="", branch="")
        self.assertEqual(pr.suite_key, push.suite_key)
        self.assertEqual(pr.backend_mode, PROFILE.MODE)
        self.assertTrue(pr.suite_key.startswith(PROFILE.SUITE_PREFIX))
        self.assertEqual(pr.focused_tests, PROFILE.FAILED_TEST_NODES + ("tests/test_pricing.py",))
        proof = json.loads((self.root / PROFILE.EVIDENCE_NAME).read_text())
        self.assertEqual(proof["candidate_sha"], self.candidate)
        self.assertEqual(proof["status"], "failed_baseline_verified_followup_and_operational_gates_pending")
        self.assertEqual(proof["baseline"]["run_conclusion"], "failure")
        self.assertIn("not a full-suite pass", proof["scope"])

    def test_different_or_incomplete_baseline_never_falls_back_to_full(self):
        for key, value in (("conclusion", "success"), ("status", "in_progress")):
            with self.api(baseline_change=lambda run, jobs: jobs["jobs"][0].update({key: value})), self.assertRaises(ValueError):
                self.resolve()
        self.assertFalse((self.root / PROFILE.EVIDENCE_NAME).exists())

    def test_exact_pr_number_branch_repo_and_head_are_required(self):
        for kwargs in ({"number": "935"}, {"branch": "other"}, {"repo": "fork/MeuCardio"}):
            with self.api(), self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                self.resolve(**kwargs)
        for change in (lambda pr: pr["head"].update(sha="0" * 40),
                       lambda pr: pr["head"]["repo"].update(full_name="fork/MeuCardio"),
                       lambda pr: pr["base"].update(ref="other")):
            with self.api(pr_change=change), self.assertRaises(ValueError):
                self.resolve()

    def test_promotion_requires_merged_exact_main_and_complete_association(self):
        variants = ({"pr_change": lambda pr: pr.update(merged=False)},
                    {"pr_change": lambda pr: pr.update(merge_commit_sha="0" * 40)},
                    {"main": "0" * 40}, {"associated": []},
                    {"associated": [{"number": 934}, {"number": 934}]})
        for variant in variants:
            with self.api(**variant), self.subTest(variant=variant), self.assertRaises(ValueError):
                self.resolve(event="push", number="", branch="")

    def test_unrelated_pr_or_future_push_does_not_use_this_exception(self):
        with patch.object(PROFILE, "_github") as api:
            self.assertIsNone(self.resolve(number="999", branch="other"))
            api.assert_not_called()
        with self.api(associated=[{"number": 999}], pr_change=lambda pr: (
                pr["head"].update(sha="0" * 40), pr.update(merge_commit_sha="1" * 40))):
            self.assertIsNone(self.resolve(event="push", number="", branch=""))

    def test_historical_push_without_profile_needs_no_new_api_evidence(self):
        self.git("checkout", "-q", self.baseline)
        with patch.object(PROFILE, "_github") as api:
            self.assertIsNone(self.resolve(event="push", number="", branch=""))
            api.assert_not_called()

    def test_missing_api_evidence_stops_classification_without_artifact(self):
        with patch.object(PROFILE, "_github", side_effect=ValueError("temporary evidence unavailable")), self.assertRaises(ValueError):
            self.resolve()
        self.assertFalse((self.root / PROFILE.EVIDENCE_NAME).exists())


class JUnitAndRunnerTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="corvia-pr934-junit-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        for node in PROFILE.FAILED_TEST_NODES:
            test, name = node.split("::")
            self.write("backend/" + test, "def " + name + "():\n    pass\n")
        reviewed = {}
        for test, count in zip(PROFILE.FOCUSED_TESTS, (9, 20, 3)):
            path = "backend/" + test
            self.write(path, "class FixtureTest:\n" + "".join("    def test_price_" + str(i) + "(self): pass\n" for i in range(count)))
            reviewed[path] = {"before": None, "after": hashlib.sha256((self.root / path).read_bytes()).hexdigest()}
        patcher = patch.object(PROFILE, "REVIEWED_DELTA", reviewed)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.expected = PROFILE.expected_followup_cases(self.root)
        self.junit = self.root / "result.xml"
        self.source = b'SELF_SOURCE_SHA256 = None\n# isolated runner source\n'
        self.write(PROFILE.SELF_PATH, self.source.decode())

    def write(self, path, source):
        file = self.root / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(source, encoding="utf-8")

    def xml(self):
        suites = ET.Element("testsuites")
        suite = ET.SubElement(suites, "testsuite", tests="38", failures="0", errors="0", skipped="0")
        for classname, name in sorted(self.expected):
            ET.SubElement(suite, "testcase", classname=classname, name=name)
        return suites, suite

    def save(self, xml):
        self.junit.write_bytes(ET.tostring(xml))

    def test_static_sources_prove_six_exact_nodes_and_32_pricing_cases_without_imports(self):
        self.assertEqual(len(self.expected), 38)
        for node in PROFILE.FAILED_TEST_NODES:
            file, name = node.split("::")
            self.assertIn((file.removesuffix(".py").replace("/", "."), name), self.expected)
        xml, _ = self.xml()
        self.save(xml)
        PROFILE.validate_followup_junit(self.junit, self.expected)

    def test_missing_extra_duplicate_or_wrong_identity_cannot_replace_a_required_case(self):
        for alteration in ("missing", "extra", "duplicate", "wrong-name", "wrong-module"):
            xml, suite = self.xml()
            if alteration == "missing":
                suite.remove(suite[0])
            elif alteration == "extra":
                ET.SubElement(suite, "testcase", classname="unreviewed", name="test_extra")
            elif alteration == "duplicate":
                suite[0].attrib = dict(suite[1].attrib)
            elif alteration == "wrong-name":
                suite[0].set("name", "test_other")
            else:
                suite[0].set("classname", "tests.other")
            self.save(xml)
            with self.subTest(alteration=alteration), self.assertRaises(ValueError):
                PROFILE.validate_followup_junit(self.junit, self.expected)

    def test_no_skip_xfail_failure_error_or_false_suite_totals_are_accepted(self):
        for tag in ("skipped", "failure", "error"):
            xml, suite = self.xml()
            ET.SubElement(suite[0], tag)
            self.save(xml)
            with self.subTest(tag=tag), self.assertRaises(ValueError):
                PROFILE.validate_followup_junit(self.junit, self.expected)
        for key, value in (("tests", "39"), ("failures", "1"), ("errors", "1"), ("skipped", "1")):
            xml, suite = self.xml()
            suite.set(key, value)
            self.save(xml)
            with self.subTest(key=key), self.assertRaises(ValueError):
                PROFILE.validate_followup_junit(self.junit, self.expected)

    def test_junit_is_single_suite_bounded_and_without_entity_declarations(self):
        xml, _ = self.xml()
        ET.SubElement(xml, "testsuite")
        self.save(xml)
        with self.assertRaises(ValueError):
            PROFILE.validate_followup_junit(self.junit, self.expected)
        for raw in (b"x" * (PROFILE.MAX_REPORT_BYTES + 1), b'<!DOCTYPE x><testsuites/>', b'<!ENTITY x "x"><testsuites/>'):
            self.junit.write_bytes(raw)
            with self.assertRaises(ValueError):
                PROFILE.validate_followup_junit(self.junit, self.expected)

    def test_changed_source_missing_function_or_unreviewed_count_stops_before_pytest(self):
        path = self.root / "backend" / PROFILE.FOCUSED_TESTS[0]
        source = path.read_bytes()
        path.write_bytes(source + b"# unreviewed\n")
        with self.assertRaises(ValueError):
            PROFILE.expected_followup_cases(self.root)
        path.write_bytes(source)
        with patch.object(PROFILE, "EXPECTED_KAIROS_TESTS", 31), self.assertRaises(ValueError):
            PROFILE.expected_followup_cases(self.root)
        path = self.root / "backend" / PROFILE.FAILED_TEST_NODES[0].split("::")[0]
        path.write_text("# no expected function\n")
        with self.assertRaises(ValueError):
            PROFILE.expected_followup_cases(self.root)

    def context(self, env_change=None, returncode=0):
        env = {"FOCUSED_TESTS": " ".join(PROFILE.FAILED_TEST_NODES + PROFILE.FOCUSED_TESTS),
               "CANDIDATE_SHA": "a" * 40, "SUITE_KEY": PROFILE.SUITE_PREFIX + "b" * 16}
        env.update(env_change or {})
        stack = ExitStack()
        stack.enter_context(patch.dict(os.environ, env))
        stack.enter_context(patch.object(PROFILE, "_git", return_value="a" * 40))
        stack.enter_context(patch.object(PROFILE, "SELF_SOURCE_SHA256", PROFILE.normalized_self_hash(self.source)))
        self.child = stack.enter_context(patch.object(PROFILE.subprocess, "run", return_value=subprocess.CompletedProcess([], returncode)))
        return stack

    def test_runner_passes_only_the_literal_selection_and_validates_38_passes(self):
        xml, _ = self.xml()
        self.save(xml)
        with self.context():
            self.assertEqual(PROFILE.run_followup(self.root, self.junit), 0)
        args, kwargs = self.child.call_args
        command = args[0]
        self.assertEqual(command[:6], [sys.executable, "-m", "pytest", "-q", "--tb=short", "--rootdir=."])
        self.assertEqual(command[6:-1], list(PROFILE.FAILED_TEST_NODES + PROFILE.FOCUSED_TESTS))
        self.assertEqual(kwargs, {"cwd": self.root / "backend"})

    def test_runner_rejects_missing_extra_selection_sha_or_wrong_scope_before_child(self):
        for env in ({"FOCUSED_TESTS": ""}, {"FOCUSED_TESTS": "tests"}, {"CANDIDATE_SHA": "c" * 40},
                    {"SUITE_KEY": "backend-risk-v1-full"}):
            with self.context(env), self.subTest(env=env), self.assertRaises(ValueError):
                PROFILE.run_followup(self.root, self.junit)
            self.child.assert_not_called()

    def test_runner_does_not_hide_pytest_failure_or_accept_missing_junit(self):
        with self.context(returncode=1):
            self.assertEqual(PROFILE.run_followup(self.root, self.junit), 1)
        with self.context(returncode=0), self.assertRaises(FileNotFoundError):
            PROFILE.run_followup(self.root, self.junit)


class IntegrationTests(unittest.TestCase):
    def test_historical_profiles_precede_new_profile_and_exception_is_before_default(self):
        source = (ROOT / "scripts/ci_backend_followup.py").read_text()
        self.assertLess(source.index("decision = failed_test_followup("), source.index("decision = pr934_continuation("))
        self.assertLess(source.index("decision = pr934_continuation("), source.index("decision = classify_paths("))
        self.assertNotIn("try:\n        decision = pr934_continuation", source)

    def test_existing_backend_job_retains_pending_gates_and_exact_sha_certificate(self):
        source = (ROOT / ".github/workflows/ci.yml").read_text()
        self.assertIn("scripts.tests.test_ci_pr934_continuation", source)
        self.assertIn("backend-pr934-continuation.json", source)
        self.assertIn('python scripts/ci_backend_pr934_continuation.py --run-followup', source)
        self.assertIn("Backend suite certificate ${{ needs.backend-risk-policy.outputs.suite_key }}", source)
        self.assertIn("Reuse only an identical successful suite for this exact SHA", source)
        self.assertIn("pr934-failed-tests-followup)", source)
        self.assertIn("backend-pr934-followup.xml", source)
        backend = source.split("  backend:\n", 1)[1].split("  backend-focused:\n", 1)[0]
        self.assertIn("outputs.backend_mode == 'pr934-failed-tests-followup'", backend)
        self.assertLess(backend.index("--run-followup"), backend.index("- name: Exercise live HTTP release flow"))
        self.assertLess(backend.index("- name: Exercise live HTTP release flow"), backend.index("- name: Prove PostgreSQL backup and restore"))
        self.assertLess(backend.index("- name: Prove PostgreSQL backup and restore"), backend.index("- name: Backend suite certificate"))
        for step in ("Exercise live HTTP release flow", "Prove PostgreSQL backup and restore"):
            stanza = backend.split("- name: " + step, 1)[1].split("\n      - name:", 1)[0]
            self.assertNotIn("\n        if:", stanza)
        runner = (ROOT / "scripts/ci_backend_pr934_continuation.py").read_text()
        self.assertIn('*targets, "--junitxml="', runner)
        self.assertIn('validate_followup_junit(junit, expected)', runner)


if __name__ == "__main__":
    unittest.main()
