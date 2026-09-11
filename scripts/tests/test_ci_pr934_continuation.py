"""Offline PR934 provenance tests; never invoke backend pytest, DB or GitHub."""
from __future__ import annotations

from copy import deepcopy
import hashlib
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
    jobs = [dict(common, id=PROFILE.BASELINE_JOB_ID, name="Backend tests", steps=[
        {"name": name, "status": "completed", "conclusion": "success"}
        for name in PROFILE.REQUIRED_BASELINE_STEPS]),
        dict(common, id=1002, name="Backend risk gate"),
        dict(common, id=1003, name="Backend risk policy"),
        dict(common, id=1004, name="Frontend build", conclusion="failure")]
    return run, {"total_count": len(jobs), "jobs": jobs}


class BaselineTests(unittest.TestCase):
    def test_complete_backend_with_only_known_frontend_failure_is_honest(self):
        run, jobs = evidence()
        proof = PROFILE.validate_baseline(run, jobs)
        self.assertEqual(proof["certificate"], "backend-risk-v1-full")
        self.assertEqual(proof["run_conclusion"], "failure")
        self.assertEqual(proof["failed_other_jobs"], ["Frontend build"])
        run["conclusion"] = jobs["jobs"][-1]["conclusion"] = "success"
        self.assertEqual(PROFILE.validate_baseline(run, jobs)["failed_other_jobs"], [])

    def test_run_identity_and_completion_are_mandatory(self):
        for key, value in {"id": 1, "head_sha": "0" * 40, "head_branch": "other",
                           "path": ".github/workflows/other.yml", "event": "push",
                           "status": "in_progress", "conclusion": "cancelled", "run_attempt": 2,
                           "repository": {"full_name": "fork/MeuCardio"}}.items():
            run, jobs = evidence()
            run[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                PROFILE.validate_baseline(run, jobs)

    def test_backend_and_gate_require_exact_original_job_metadata(self):
        for job_index in (0, 1):
            for key, value in {"run_id": 1, "head_sha": "0" * 40, "run_attempt": 2,
                               "head_branch": "other", "status": "in_progress",
                               "conclusion": "failure"}.items():
                run, jobs = evidence()
                jobs["jobs"][job_index][key] = value
                with self.subTest(job=job_index, key=key), self.assertRaises(ValueError):
                    PROFILE.validate_baseline(run, jobs)
        run, jobs = evidence()
        jobs["jobs"][0]["id"] += 1
        with self.assertRaises(ValueError):
            PROFILE.validate_baseline(run, jobs)
        for key in ("run_attempt", "head_branch"):
            run, jobs = evidence()
            del jobs["jobs"][0][key]
            with self.subTest(missing=key), self.assertRaises(ValueError):
                PROFILE.validate_baseline(run, jobs)

    def test_every_full_gate_must_succeed_not_only_pytest(self):
        for name in PROFILE.REQUIRED_BASELINE_STEPS:
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
                    PROFILE.validate_baseline(run, jobs)

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
                PROFILE.validate_baseline(run, jobs)


class GitProfileTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="corvia-ci-pr934-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git("init", "-q")
        self.write("backend/app/data/pricing/snapshot.json", "baseline bytes\n")
        self.write("medicamentos/old-audit.json", "source audit\n")
        self.write("backend/tests/test_pricing.py", "# selected offline fixture\n")
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
        responses = {
            f"repos/{PROFILE.REPOSITORY}/pulls/934": pr,
            f"repos/{PROFILE.REPOSITORY}/commits/{self.candidate}/pulls":
                [{"number": 934}] if associated is None else associated,
            f"repos/{PROFILE.REPOSITORY}/git/ref/heads/main": {"object": {"sha": main or self.candidate}},
            f"repos/{PROFILE.REPOSITORY}/actions/runs/{PROFILE.BASELINE_RUN_ID}": run,
            f"repos/{PROFILE.REPOSITORY}/actions/runs/{PROFILE.BASELINE_RUN_ID}/attempts/1/jobs?per_page=100": jobs,
        }
        return patch.object(PROFILE, "_github", side_effect=lambda path: deepcopy(responses[path]))

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
        self.assertEqual(pr.backend_mode, "focused")
        self.assertTrue(pr.suite_key.startswith(PROFILE.SUITE_PREFIX))
        self.assertEqual(pr.focused_tests, ("tests/test_pricing.py",))
        proof = json.loads((self.root / PROFILE.EVIDENCE_NAME).read_text())
        self.assertEqual(proof["candidate_sha"], self.candidate)
        self.assertEqual(proof["status"], "baseline_verified_focused_tests_pending")
        self.assertEqual(proof["baseline"]["run_conclusion"], "failure")
        self.assertIn("not a new full-suite pass", proof["scope"])

    def test_failed_or_incomplete_baseline_never_falls_back_to_full(self):
        for key, value in (("conclusion", "failure"), ("status", "in_progress")):
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


class IntegrationTests(unittest.TestCase):
    def test_historical_profiles_precede_new_profile_and_exception_is_before_default(self):
        source = (ROOT / "scripts/ci_backend_followup.py").read_text()
        self.assertLess(source.index("decision = failed_test_followup("), source.index("decision = pr934_continuation("))
        self.assertLess(source.index("decision = pr934_continuation("), source.index("decision = classify_paths("))
        self.assertNotIn("try:\n        decision = pr934_continuation", source)

    def test_existing_real_focused_job_and_exact_sha_certificate_remain_required(self):
        source = (ROOT / ".github/workflows/ci.yml").read_text()
        self.assertIn("scripts.tests.test_ci_pr934_continuation", source)
        self.assertIn("backend-pr934-continuation.json", source)
        self.assertIn('python -m pytest -q --tb=short "${tests[@]}"', source)
        self.assertIn("Backend suite certificate ${{ needs.backend-risk-policy.outputs.suite_key }}", source)
        self.assertIn("Reuse only an identical successful suite for this exact SHA", source)
        self.assertNotIn("backend_mode == 'pr934", source)


if __name__ == "__main__":
    unittest.main()
