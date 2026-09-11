"""PR932 evidence and its CI-only repair; never a new full-suite certificate.

The repaired test, HTTP flow and backup already passed on certified 5279d677.
The later policy-only correction retains that proof only when all application
bytes and the passed fixture remain unchanged. Missing evidence stops CI rather
than repeating the backend suite or silently broadening an exception.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET
import zipfile

from ci_backend_policy import PolicyDecision

REPOSITORY = "rafaelpaesmeirelles/MeuCardio"
BRANCH = "codex/atelier-premium-20260911"
PR_NUMBER = 932
BASELINE_SHA = "efb10e02e0237daacfe2054e5afca200dee62804"
RUN_ID = 34593060917
JOB_ID = 103242658960
CERTIFIED_SHA = "5279d677190b042a16a7806181fff1cad1fdf01b"
CERTIFIED_RUN_ID = 34598249285
CERTIFIED_JOB_ID = 103259140812
CERTIFIED_GATE_JOB_ID = 103259547272
ARTIFACT_ID = 10261753294
ARTIFACT_SHA256 = "09c7664412d15bcccfcb1bbeaa4de7750142cc68a4246072b9b934adba3f6225"
TEST_NODE = "backend/tests/test_reconcile_rag_pipeline.py::test_reconcile_nunca_chama_rag"
FIXTURE_PATH = TEST_NODE.split("::")[0]
FIXTURE_SHA256 = "d6bfe40112c759cfe60e4795a1ab42af4404d8b5c27143b7c00aad9a52f212d1"
REPAIRED_SUITE_KEY = "backend-risk-v1-failed-test-followup-pr932-efb10e02"
SUITE_KEY = "backend-risk-v1-ci-only-continuation-pr932-5279d677"
ALLOWED_PATHS = frozenset({
    FIXTURE_PATH,
    ".github/workflows/ci.yml",
    "scripts/ci_backend_followup.py",
    "scripts/ci_backend_failed_test_followup.py",
    "scripts/tests/test_ci_failed_test_followup.py",
})
CI_ONLY_PATHS = ALLOWED_PATHS - {FIXTURE_PATH}
RETAINED_SUCCESS_STEPS = (
    "Enforce Node 24 action runtimes", "Validate operational shell scripts",
    "Audit Python production dependencies", "Apply migrations through the operational command",
    "Verify migration command is idempotent", "Smoke test explicit administrator bootstrap",
    "Compile Python modules",
)


def _git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def _github(path: str, *, raw: bool = False):
    # Logs remain in memory; never print CI output, which may contain secrets.
    result = subprocess.run(["gh", "api", path], capture_output=True, text=True, timeout=45)
    if result.returncode or len(result.stdout) > 16 * 1024 * 1024:
        raise ValueError("Cannot verify bounded baseline evidence; refusing follow-up")
    return result.stdout if raw else json.loads(result.stdout)


def _github_binary(path: str) -> bytes:
    # The pinned artifact is 1110 bytes. This is a post-download size check,
    # not a subprocess memory sandbox; the ZIP member has a bounded read below.
    result = subprocess.run(["gh", "api", "-H", "Cache-Control: no-cache", path], capture_output=True, timeout=45)
    if result.returncode or len(result.stdout) > 2 * 1024 * 1024:
        # Only a numeric HTTP status can escape; never expose a signed URL/body.
        match = re.search(rb"HTTP (\d{3})", result.stderr)
        status = match.group(1).decode() if match else "unavailable"
        raise ValueError(f"Cannot read the bounded baseline artifact (HTTP {status})")
    return result.stdout


def validate_artifact(artifact: dict, archive: bytes) -> str:
    expected = {"id": ARTIFACT_ID, "name": "backend-pytest-failure", "expired": False,
                "digest": "sha256:" + ARTIFACT_SHA256}
    if any(artifact.get(key) != value for key, value in expected.items()):
        raise ValueError("Unexpected baseline artifact identity or digest")
    provenance = artifact.get("workflow_run", {})
    if any(provenance.get(key) != value for key, value in
           {"id": RUN_ID, "head_sha": BASELINE_SHA, "head_branch": BRANCH,
            "repository_id": 1312508910, "head_repository_id": 1312508910}.items()):
        raise ValueError("Unexpected baseline artifact provenance")
    if len(archive) > 2 * 1024 * 1024 or hashlib.sha256(archive).hexdigest() != ARTIFACT_SHA256:
        raise ValueError("Baseline artifact archive checksum mismatch")
    with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
        entries = bundle.infolist()
        if len(entries) != 1 or entries[0].filename != "pytest-output.txt" or entries[0].file_size > 2 * 1024 * 1024:
            raise ValueError("Unexpected baseline artifact members")
        # Read the single member into memory; never extract paths to disk.
        with bundle.open(entries[0]) as report:
            content = report.read(2 * 1024 * 1024 + 1)
        if len(content) > 2 * 1024 * 1024:
            raise ValueError("Baseline report exceeds its bounded size")
        return content.decode("utf-8")


def validate_baseline(run: dict, job: dict, log: str, *, closed_release_verified: bool = False) -> str:
    expected_run = {"id": RUN_ID, "head_sha": BASELINE_SHA, "head_branch": BRANCH,
                    "path": ".github/workflows/ci.yml", "event": "pull_request",
                    "status": "completed", "conclusion": "failure", "run_attempt": 1}
    if any(run.get(key) != value for key, value in expected_run.items()):
        raise ValueError("Unexpected baseline run identity")
    if run.get("repository", {}).get("full_name") != REPOSITORY:
        raise ValueError("Unexpected baseline repository")
    # GitHub mutates the entire pull_requests list: it may disappear on merge
    # or be reassigned to a later PR on this branch. After the original merge,
    # ancestry and completed CI have been verified, it is not historical proof.
    # Immutable run.head_sha and job.head_sha above/below bind the actual code.
    associations = run.get("pull_requests", [])
    if not closed_release_verified and not any(pr.get("number") == PR_NUMBER and pr.get("head", {}).get("ref") == BRANCH
               and pr.get("base", {}).get("ref") == "main"
               for pr in associations):
        raise ValueError("Baseline run is not associated with the exact PR932 head")
    expected_job = {"id": JOB_ID, "run_id": RUN_ID, "head_sha": BASELINE_SHA,
                    "name": "Backend tests", "status": "completed", "conclusion": "failure"}
    if any(job.get(key) != value for key, value in expected_job.items()):
        raise ValueError("Unexpected baseline job identity")
    steps = {step.get("name"): step for step in job.get("steps", [])}
    for name in RETAINED_SUCCESS_STEPS:
        if steps.get(name, {}).get("conclusion") != "success" or steps[name].get("status") != "completed":
            raise ValueError("Baseline prerequisite was not completed successfully")
    if steps.get("Run pytest", {}).get("conclusion") != "failure" or steps["Run pytest"].get("status") != "completed":
        raise ValueError("Baseline pytest did not complete with a test failure")
    for name in ("Exercise live HTTP release flow", "Prove PostgreSQL backup and restore"):
        if steps.get(name, {}).get("conclusion") != "skipped":
            raise ValueError("Unexpected operational-gate baseline; review required")
    if {name for name, step in steps.items() if step.get("conclusion") == "failure"} != {"Run pytest"}:
        raise ValueError("Baseline contains an additional failed step")
    clean = re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", log)
    clean = re.sub(r"(?m)^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?Z\s?", "", clean)
    summaries = re.findall(r"(?m)^(?:=+\s*)?(\d+) failed, (\d+) passed, (\d+) skipped, (\d+) warnings? in [^\n]+", clean)
    if summaries != [("1", "3673", "4", "1")]:
        raise ValueError("Baseline final pytest totals differ or are incomplete")
    failed = re.findall(r"(?m)^FAILED\s+(\S+)(?:\s|$)", clean)
    if failed != [TEST_NODE.removeprefix("backend/")]:
        raise ValueError("Baseline failed-node inventory is not the one approved repair")
    if re.search(r"(?m)^(?:ERROR\s|!+.*(?:Interrupted|ERRORS?))", clean):
        raise ValueError("Baseline contains collection/setup errors or interruption")
    return hashlib.sha256(log.encode()).hexdigest()


def validate_diff(root: Path, manifest: dict | None = None) -> list[str]:
    # No caller-provided manifest may expand this correction's sealed scope.
    if manifest not in (None, {}):
        raise ValueError("External scope overrides are not supported")
    subprocess.run(["git", "-C", str(root), "merge-base", "--is-ancestor", BASELINE_SHA, "HEAD"],
                   check=True, capture_output=True)
    subprocess.run(["git", "-C", str(root), "merge-base", "--is-ancestor", CERTIFIED_SHA, "HEAD"],
                   check=True, capture_output=True)
    ci_delta = set(_git(root, "diff", "--no-renames", "--name-only", f"{CERTIFIED_SHA}..HEAD").splitlines())
    if not ci_delta or not ci_delta.issubset(CI_ONLY_PATHS):
        raise ValueError("Certified application changed; CI-only continuation is forbidden")
    paths = _git(root, "diff", "--no-renames", "--name-only", f"{BASELINE_SHA}..HEAD").splitlines()
    if set(paths) != ALLOWED_PATHS:
        raise ValueError("Follow-up changed paths differ from the reviewed test/CI-only correction")
    for path in paths:
        entry = _git(root, "ls-tree", "HEAD", "--", path)
        if not entry.startswith("100644 blob ") or not (root / path).is_file() or (root / path).is_symlink():
            raise ValueError("Follow-up contains a deleted, symlinked or non-regular file")
    fixture = (root / FIXTURE_PATH).read_bytes()
    if _git(root, "rev-parse", f"{BASELINE_SHA}:{FIXTURE_PATH}") != "e41def371f97ece2b6523cc135e55260c0484a1e":
        raise ValueError("Unexpected baseline fixture blob")
    if hashlib.sha256(fixture).hexdigest() != FIXTURE_SHA256:
        raise ValueError("Fixture differs from the reviewed single-test repair")
    if _git(root, "rev-parse", f"{CERTIFIED_SHA}:{FIXTURE_PATH}") != "0dae85a5600b2c343aff750a7a90ce19cfa9e36e":
        raise ValueError("Certified fixture blob is not the passed repair")
    if _git(root, "status", "--porcelain", "--untracked-files=no"):
        raise ValueError("Follow-up checkout contains uncommitted changes")
    return paths


def validate_completed_release(run: dict, jobs: list[dict]) -> None:
    expected = {"id": CERTIFIED_RUN_ID, "head_sha": CERTIFIED_SHA, "head_branch": BRANCH,
                "path": ".github/workflows/ci.yml", "event": "pull_request",
                "status": "completed", "conclusion": "success", "run_attempt": 1}
    if any(run.get(key) != value for key, value in expected.items()) or run.get("repository", {}).get("full_name") != REPOSITORY:
        raise ValueError("Completed release CI evidence is invalid")
    for job_id, job_name in ((CERTIFIED_JOB_ID, "Backend tests"), (CERTIFIED_GATE_JOB_ID, "Backend risk gate")):
        found = [job for job in jobs if job.get("id") == job_id]
        if len(found) != 1 or any(found[0].get(key) != value for key, value in
            {"run_id": CERTIFIED_RUN_ID, "head_sha": CERTIFIED_SHA, "name": job_name,
             "status": "completed", "conclusion": "success"}.items()):
            raise ValueError("Completed release job evidence is invalid")
        if job_id == CERTIFIED_JOB_ID:
            steps = {step.get("name"): step for step in found[0].get("steps", [])}
            for name in ("Run pytest", "Exercise live HTTP release flow", "Prove PostgreSQL backup and restore",
                         "Backend suite certificate " + REPAIRED_SUITE_KEY):
                if steps.get(name, {}).get("status") != "completed" or steps[name].get("conclusion") != "success":
                    raise ValueError("Completed release is missing a required successful gate")


def validate_followup_junit(path: Path) -> None:
    root = ET.parse(path).getroot()
    suites = list(root.iter("testsuite"))
    cases = list(root.iter("testcase"))
    if len(suites) != 1 or len(cases) != 1:
        raise ValueError("Follow-up must execute exactly one test case")
    suite, case = suites[0], cases[0]
    if any(suite.get(key) != expected for key, expected in
           {"tests": "1", "failures": "0", "errors": "0", "skipped": "0"}.items()):
        raise ValueError("Follow-up did not complete with exactly one pass")
    if (case.get("name") != "test_reconcile_nunca_chama_rag"
            or case.get("classname") not in {"tests.test_reconcile_rag_pipeline", "backend.tests.test_reconcile_rag_pipeline"}
            or list(case.iter("skipped")) or list(case.iter("failure")) or list(case.iter("error"))):
        raise ValueError("Follow-up result does not prove the required test passed")


def resolve_decision(root: Path, *, event: str, number: str, head_ref: str, repository: str):
    relevant_pr = event == "pull_request" and (number == str(PR_NUMBER) or head_ref == BRANCH)
    if not relevant_pr and event != "push":
        return None
    if repository != REPOSITORY:
        if relevant_pr:
            raise ValueError("Follow-up repository mismatch")
        return None
    candidate = _git(root, "rev-parse", "HEAD")
    if event == "pull_request":
        if not number.isdigit() or int(number) < PR_NUMBER or head_ref != BRANCH:
            raise ValueError("Follow-up event identity mismatch")
        active_number = int(number)
    else:
        associated = _github(f"repos/{REPOSITORY}/commits/{candidate}/pulls")
        related = [item for item in associated if item.get("head", {}).get("ref") == BRANCH]
        exact = [item for item in related if item.get("head", {}).get("sha") == candidate]
        if not exact:
            ancestry = subprocess.run(["git", "-C", str(root), "merge-base", "--is-ancestor", CERTIFIED_SHA, "HEAD"], capture_output=True)
            delta = set(_git(root, "diff", "--no-renames", "--name-only", f"{CERTIFIED_SHA}..HEAD").splitlines()) if ancestry.returncode == 0 else None
            if related or (delta is not None and delta.issubset(CI_ONLY_PATHS)):
                raise ValueError("CI continuation PR association incomplete; no full fallback")
            return None
        if len(exact) != 1 or not isinstance(exact[0].get("number"), int) or exact[0]["number"] < PR_NUMBER:
            raise ValueError("CI continuation PR association is ambiguous")
        active_number = exact[0]["number"]
    pr = _github(f"repos/{REPOSITORY}/pulls/{active_number}")
    if (pr.get("number") != active_number or pr.get("base", {}).get("ref") != "main"
            or pr.get("base", {}).get("repo", {}).get("full_name") != REPOSITORY
            or pr.get("head", {}).get("repo", {}).get("full_name") != REPOSITORY
            or pr.get("head", {}).get("ref") != BRANCH or pr.get("head", {}).get("sha") != candidate):
        raise ValueError("Follow-up PR/head identity mismatch; no full fallback")
    if event == "push":
        current_main = _github(f"repos/{REPOSITORY}/git/ref/heads/main")
        if current_main.get("object", {}).get("sha") != candidate or not pr.get("merged") or pr.get("merge_commit_sha") != candidate:
            raise ValueError("Follow-up main promotion evidence incomplete; no full fallback")
    original = _github(f"repos/{REPOSITORY}/pulls/{PR_NUMBER}")
    if (original.get("number") != PR_NUMBER or original.get("merged") is not True
            or original.get("merge_commit_sha") != CERTIFIED_SHA
            or original.get("base", {}).get("repo", {}).get("full_name") != REPOSITORY
            or original.get("head", {}).get("repo", {}).get("full_name") != REPOSITORY
            or original.get("head", {}).get("ref") != BRANCH or original.get("base", {}).get("ref") != "main"):
        raise ValueError("Original merged release identity is not verified")
    paths = validate_diff(root)
    certified_run = _github(f"repos/{REPOSITORY}/actions/runs/{CERTIFIED_RUN_ID}")
    certified_jobs = _github(f"repos/{REPOSITORY}/actions/runs/{CERTIFIED_RUN_ID}/jobs?filter=all&per_page=100")
    validate_completed_release(certified_run, certified_jobs.get("jobs", []))
    run = _github(f"repos/{REPOSITORY}/actions/runs/{RUN_ID}")
    jobs = _github(f"repos/{REPOSITORY}/actions/runs/{RUN_ID}/jobs?filter=all&per_page=100")
    matching = [job for job in jobs.get("jobs", []) if job.get("id") == JOB_ID]
    if len(matching) != 1:
        raise ValueError("Unique baseline job evidence is missing")
    artifacts = _github(f"repos/{REPOSITORY}/actions/runs/{RUN_ID}/artifacts")
    matching_artifacts = [item for item in artifacts.get("artifacts", []) if item.get("id") == ARTIFACT_ID]
    if len(matching_artifacts) != 1:
        raise ValueError("Unique original pytest report artifact is missing")
    archive = _github_binary(f"repos/{REPOSITORY}/actions/artifacts/{ARTIFACT_ID}/zip")
    log = validate_artifact(matching_artifacts[0], archive)
    log_hash = validate_baseline(run, matching[0], log, closed_release_verified=True)
    summary = {
        "scope": "CI-only repair; unchanged application retains completed release evidence; not a full-suite pass or exact-SHA reuse",
        "instruction": "Se houver falha, corrija e refaca somente o teste que falhou",
        "candidate_sha": candidate, "candidate_tree": _git(root, "rev-parse", "HEAD^{tree}"), "baseline_sha": BASELINE_SHA,
        "baseline_run_id": RUN_ID, "baseline_job_id": JOB_ID, "baseline_report_sha256": log_hash,
        "baseline_artifact_id": ARTIFACT_ID, "baseline_artifact_sha256": ARTIFACT_SHA256,
        "baseline_result": {"failed": 1, "passed": 3673, "skipped": 4},
        "certified_application_sha": CERTIFIED_SHA, "certified_run_id": CERTIFIED_RUN_ID,
        "certified_backend_job_id": CERTIFIED_JOB_ID, "active_pull_request": active_number,
        "test_already_passed": TEST_NODE, "backend_tests_to_run": [], "changed_paths": paths,
        "completed_operational_gates": ["HTTP release flow", "PostgreSQL backup and restore"],
        "retained_success_steps": list(RETAINED_SUCCESS_STEPS),
    }
    Path(os.environ.get("RUNNER_TEMP", "/tmp"), "backend-failed-test-followup.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    return PolicyDecision(backend_mode="ci-only-continuation", suite_key=SUITE_KEY,
        focused_tests=(), reasons=(f"baseline:{BASELINE_SHA}", f"completed-ci:{CERTIFIED_RUN_ID}",
            "CI-only-repair-after-PR932-merge", "application-and-passed-test-fixture-unchanged",
            "HTTP-and-backup-gates-already-passed", "not-a-full-suite-or-exact-SHA-reuse-certificate"))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Validate the single failed-test result")
    parser.add_argument("--junit", type=Path, required=True)
    validate_followup_junit(parser.parse_args().junit)
    print("Verified exactly one passed test: " + TEST_NODE)
