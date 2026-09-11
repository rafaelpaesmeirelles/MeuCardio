"""PR932's single failed-test continuation; never a full-suite certificate.

The unchanged runtime retains the observed baseline result. Only the reviewed
fixture repair is exercised again, followed by the previously skipped HTTP and
backup gates. Any scope/provenance mismatch stops CI rather than running full.
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
ARTIFACT_ID = 10261753294
ARTIFACT_SHA256 = "09c7664412d15bcccfcb1bbeaa4de7750142cc68a4246072b9b934adba3f6225"
TEST_NODE = "backend/tests/test_reconcile_rag_pipeline.py::test_reconcile_nunca_chama_rag"
FIXTURE_PATH = TEST_NODE.split("::")[0]
FIXTURE_SHA256 = "d6bfe40112c759cfe60e4795a1ab42af4404d8b5c27143b7c00aad9a52f212d1"
SUITE_KEY = "backend-risk-v1-failed-test-followup-pr932-efb10e02"
ALLOWED_PATHS = frozenset({
    FIXTURE_PATH,
    ".github/workflows/ci.yml",
    "scripts/ci_backend_followup.py",
    "scripts/ci_backend_failed_test_followup.py",
    "scripts/tests/test_ci_failed_test_followup.py",
})
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


def validate_baseline(run: dict, job: dict, log: str) -> str:
    expected_run = {"id": RUN_ID, "head_sha": BASELINE_SHA, "head_branch": BRANCH,
                    "path": ".github/workflows/ci.yml", "event": "pull_request",
                    "status": "completed", "conclusion": "failure", "run_attempt": 1}
    if any(run.get(key) != value for key, value in expected_run.items()):
        raise ValueError("Unexpected baseline run identity")
    if run.get("repository", {}).get("full_name") != REPOSITORY:
        raise ValueError("Unexpected baseline repository")
    # pull_requests[].head.sha is live PR metadata, not the run's snapshot.
    # Immutable run.head_sha and job.head_sha above/below bind the actual code.
    if not any(pr.get("number") == PR_NUMBER and pr.get("head", {}).get("ref") == BRANCH
               and pr.get("base", {}).get("ref") == "main"
               for pr in run.get("pull_requests", [])):
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
    if _git(root, "status", "--porcelain", "--untracked-files=no"):
        raise ValueError("Follow-up checkout contains uncommitted changes")
    return paths


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
    pr = _github(f"repos/{REPOSITORY}/pulls/{PR_NUMBER}")
    if event == "push" and candidate not in {pr.get("head", {}).get("sha"), pr.get("merge_commit_sha")}:
        associated = _github(f"repos/{REPOSITORY}/commits/{candidate}/pulls")
        pr_head = pr.get("head", {}).get("sha", "")
        if not re.fullmatch(r"[0-9a-f]{40}", pr_head):
            raise ValueError("Cannot identify the follow-up head")
        head_commit = _github(f"repos/{REPOSITORY}/git/commits/{pr_head}")
        same_tree = _git(root, "rev-parse", "HEAD^{tree}") == head_commit.get("tree", {}).get("sha")
        if same_tree or any(item.get("number") == PR_NUMBER for item in associated):
            raise ValueError("Follow-up integration is not the exact tested PR head; no full fallback")
        return None
    if (pr.get("number") != PR_NUMBER or pr.get("base", {}).get("ref") != "main"
            or pr.get("base", {}).get("repo", {}).get("full_name") != REPOSITORY
            or pr.get("head", {}).get("repo", {}).get("full_name") != REPOSITORY
            or pr.get("head", {}).get("ref") != BRANCH or pr.get("head", {}).get("sha") != candidate):
        raise ValueError("Follow-up PR/head identity mismatch; no full fallback")
    if relevant_pr and (number != str(PR_NUMBER) or head_ref != BRANCH):
        raise ValueError("Follow-up event identity mismatch")
    if event == "push":
        current_main = _github(f"repos/{REPOSITORY}/git/ref/heads/main")
        associated = _github(f"repos/{REPOSITORY}/commits/{candidate}/pulls")
        if current_main.get("object", {}).get("sha") != candidate or not any(item.get("number") == PR_NUMBER for item in associated):
            raise ValueError("Follow-up main promotion evidence incomplete; no full fallback")
    paths = validate_diff(root)
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
    log_hash = validate_baseline(run, matching[0], log)
    summary = {
        "scope": "single failed-test continuation, not a full-suite pass or waiver",
        "instruction": "Se houver falha, corrija e refaca somente o teste que falhou",
        "candidate_sha": candidate, "candidate_tree": _git(root, "rev-parse", "HEAD^{tree}"), "baseline_sha": BASELINE_SHA,
        "baseline_run_id": RUN_ID, "baseline_job_id": JOB_ID, "baseline_report_sha256": log_hash,
        "baseline_artifact_id": ARTIFACT_ID, "baseline_artifact_sha256": ARTIFACT_SHA256,
        "baseline_result": {"failed": 1, "passed": 3673, "skipped": 4},
        "test_to_run": TEST_NODE, "changed_paths": paths,
        "pending_operational_gates": ["HTTP release flow", "PostgreSQL backup and restore"],
        "retained_success_steps": list(RETAINED_SUCCESS_STEPS),
    }
    Path(os.environ.get("RUNNER_TEMP", "/tmp"), "backend-failed-test-followup.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    return PolicyDecision(backend_mode="failed-test-followup", suite_key=SUITE_KEY,
        focused_tests=(TEST_NODE,), reasons=(f"baseline:{BASELINE_SHA}", "3673-passed-4-skipped-retained",
            "single-reviewed-test-fixture-repair", "runtime-corpus-dependencies-unchanged",
            "pending-http-and-backup-gates-required", "not-a-full-suite-certificate"))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Validate the single failed-test result")
    parser.add_argument("--junit", type=Path, required=True)
    validate_followup_junit(parser.parse_args().junit)
    print("Verified exactly one passed test: " + TEST_NODE)
