"""Retain PR935's 3879 passes; repair its one failed test and finish pending gates.

This is an exact-delta continuation, never a full-suite pass or a general waiver.
The failed baseline, immutable artifact and every changed byte remain auditable.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

try:
    from ci_backend_policy import PolicyDecision
except ModuleNotFoundError as exc:
    if exc.name != "ci_backend_policy":
        raise
    from scripts.ci_backend_policy import PolicyDecision


REPOSITORY = "rafaelpaesmeirelles/MeuCardio"
PR_NUMBER = 935
BRANCH = "codex/integration-followup-20260911"
BASELINE_SHA = "5cc9ddb2c0be7c407274aa52ccb6bc737eec9d20"
BASELINE_RUN_ID = 34657383923
BASELINE_JOB_ID = 103452690228
BASELINE_ATTEMPT = 1
MODE = "pr935-failed-test-followup"
SUITE_PREFIX = "backend-risk-v1-failed-test-pr935-5cc9ddb2-"
EVIDENCE_NAME = "backend-pr935-continuation.json"
ARTIFACT_ID = 10287131424
ARTIFACT_BYTES = 985
ARTIFACT_SHA256 = "68156a5abed3dcd8bfe1128149c73042fb63cf9aac3fa34666b33048f95da613"
MAX_REPORT_BYTES = 2 * 1024 * 1024
TEST_NODE = "tests/test_panel_acervo_comunicacao_contract.py::test_home_nao_duplica_contagem_especializada_que_ja_e_canonica_na_biblioteca"
SELF_PATH = "scripts/ci_backend_pr935_continuation.py"
COMPANION_PATHS = frozenset({
    "backend/tests/test_panel_acervo_comunicacao_contract.py",
    "docs/qa/2026-09-11-auditoria-funcoes-atelier.md",
    ".github/workflows/ci.yml",
    "scripts/ci_backend_followup.py",
    "scripts/tests/test_ci_pr935_continuation.py",
})
# Sealed after independent review. No environment or caller-provided override.
REVIEWED_DELTA: dict[str, dict[str, str | None]] | None = {
    ".github/workflows/ci.yml": {
        "before": "29eece1ccaaaa49761d8a0664539b143672dffe39d900503a29d8820b5430fc3",
        "after": "73548e0a92d04c521edac37cb50eb3c53b7455f6a197cb66c1a74ffec923b608",
    },
    "backend/tests/test_panel_acervo_comunicacao_contract.py": {
        "before": "122322cade4507e5fb4d732a4449fdecf9d5b0629b945b081687447b8b0dc9f0",
        "after": "d0650bd0b69b63737050050748c5f363333141cf45d1b715c7bbad9360752853",
    },
    "docs/qa/2026-09-11-auditoria-funcoes-atelier.md": {
        "before": "a358e5c8d12ca58ec4f807d9f934013834f593324caf36f9ca3d646ecbdaee4a",
        "after": "4cc71832b979f6f320e97466a7c14ec7a3f3fdca7d76474438259a7db8e3bf45",
    },
    "scripts/ci_backend_followup.py": {
        "before": "28eb01516956749a2c93690b9f15028989724c703e75a37639e18b766c567f9f",
        "after": "fa3ec480746043a9fbf3df4f825622cd40b2328aaf017246796bea76a91e6d84",
    },
    "scripts/tests/test_ci_pr935_continuation.py": {
        "before": None,
        "after": "84854b4caf31483fec6e811001259d4bd4c36a8746925d354bfeab323ef3e176",
    },
}
SELF_SOURCE_SHA256 = "ecb4d5d90f9462ebaa45d6727d758ad2aa1d270a77b9cd00069d7ab5d4251d3a"

RETAINED_SUCCESS_STEPS = (
    "Enforce Node 24 action runtimes", "Validate operational shell scripts",
    "Audit Python production dependencies", "Apply migrations through the operational command",
    "Verify migration command is idempotent", "Smoke test explicit administrator bootstrap",
    "Compile Python modules",
)
PENDING_OPERATIONAL_STEPS = (
    "Exercise live HTTP release flow", "Prove PostgreSQL backup and restore",
    "Backend suite certificate backend-risk-v1-full",
)
BASELINE_JOBS = {
    "Classify backend risk and reuse exact suites": (103452601833, "success"),
    "Backend tests": (BASELINE_JOB_ID, "failure"),
    "Frontend build": (103452690311, "success"),
    "Backend focused tests": (103452691251, "skipped"),
    "Backend risk gate": (103459688312, "failure"),
}


def _git(root: Path, *args: str, binary: bool = False):
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True, timeout=20)
    if result.returncode:
        raise ValueError("Cannot verify PR935 Git evidence")
    return result.stdout if binary else result.stdout.decode("utf-8").strip()


def _github(path: str):
    try:
        result = subprocess.run(["gh", "api", path], capture_output=True, timeout=30)
        if result.returncode or len(result.stdout) > MAX_REPORT_BYTES:
            raise ValueError("Cannot verify bounded PR935 GitHub evidence")
        return json.loads(result.stdout)
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
        raise ValueError("Cannot verify PR935 GitHub evidence") from exc


def _github_binary(path: str) -> bytes:
    try:
        result = subprocess.run(["gh", "api", "-H", "Cache-Control: no-cache", path],
                                capture_output=True, timeout=45)
        if result.returncode or len(result.stdout) > MAX_REPORT_BYTES:
            raise ValueError("Cannot read bounded PR935 baseline artifact")
        return result.stdout
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ValueError("Cannot read PR935 baseline artifact") from exc


def validate_artifact(artifact: dict, archive: bytes) -> str:
    expected = {"id": ARTIFACT_ID, "name": "backend-pytest-failure", "expired": False,
                "digest": "sha256:" + ARTIFACT_SHA256, "size_in_bytes": ARTIFACT_BYTES}
    if any(artifact.get(key) != value for key, value in expected.items()):
        raise ValueError("PR935 artifact identity/digest/size differs")
    provenance = {"id": BASELINE_RUN_ID, "head_sha": BASELINE_SHA, "head_branch": BRANCH,
                  "repository_id": 1312508910, "head_repository_id": 1312508910}
    if any(artifact.get("workflow_run", {}).get(key) != value for key, value in provenance.items()):
        raise ValueError("PR935 artifact provenance differs")
    if len(archive) != ARTIFACT_BYTES or hashlib.sha256(archive).hexdigest() != ARTIFACT_SHA256:
        raise ValueError("PR935 artifact bytes differ from pinned digest")
    with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
        entries = bundle.infolist()
        if (len(entries) != 1 or entries[0].filename != "pytest-output.txt"
                or entries[0].file_size > MAX_REPORT_BYTES or entries[0].is_dir()):
            raise ValueError("PR935 artifact has unexpected members")
        with bundle.open(entries[0]) as stream:
            content = stream.read(MAX_REPORT_BYTES + 1)
        if len(content) > MAX_REPORT_BYTES:
            raise ValueError("PR935 baseline report exceeds bounded size")
        return content.decode("utf-8")


def _sha256_blob(root: Path, ref: str, path: str) -> str | None:
    entry = _git(root, "ls-tree", ref, "--", path)
    if not entry:
        return None
    if not entry.startswith("100644 blob "):
        raise ValueError(f"PR935 delta is not a regular non-executable file: {path}")
    return hashlib.sha256(_git(root, "show", f"{ref}:{path}", binary=True)).hexdigest()


def normalized_self_hash(source: bytes) -> str:
    source, count = re.subn(
        rb'^SELF_SOURCE_SHA256 = (?:None|"[0-9a-f]{64}")$',
        b'SELF_SOURCE_SHA256 = "<self-digest>"', source, flags=re.MULTILINE)
    if count != 1:
        raise ValueError("PR935 self-digest declaration is missing or ambiguous")
    return hashlib.sha256(source).hexdigest()


def validate_delta(root: Path) -> dict:
    if not REVIEWED_DELTA or not SELF_SOURCE_SHA256:
        raise ValueError("PR935 continuation is not sealed; final delta review required")
    if set(REVIEWED_DELTA) != COMPANION_PATHS:
        raise ValueError("PR935 hashes must cover exactly the five companion files")
    for hashes in REVIEWED_DELTA.values():
        if (set(hashes) != {"before", "after"}
                or not isinstance(hashes["after"], str)
                or any(value is not None and not re.fullmatch(r"[0-9a-f]{64}", value)
                       for value in hashes.values())):
            raise ValueError("Invalid reviewed PR935 content hash pair")
    _git(root, "merge-base", "--is-ancestor", BASELINE_SHA, "HEAD")
    if _git(root, "status", "--porcelain", "--untracked-files=no"):
        raise ValueError("PR935 checkout has uncommitted tracked changes")
    changed = set(_git(root, "diff", "--no-renames", "--name-only", f"{BASELINE_SHA}..HEAD").splitlines())
    if changed != COMPANION_PATHS | {SELF_PATH}:
        raise ValueError("PR935 changed paths differ from the reviewed test/docs/CI-only delta")
    evidence = {}
    for path in sorted(changed):
        hashes = {"before": _sha256_blob(root, BASELINE_SHA, path), "after": _sha256_blob(root, "HEAD", path)}
        if path in REVIEWED_DELTA and hashes != REVIEWED_DELTA[path]:
            raise ValueError(f"PR935 reviewed content hash differs: {path}")
        if hashes["after"] is None or (path == SELF_PATH and hashes["before"] is not None):
            raise ValueError("PR935 continuation implementation must be present and newly introduced")
        evidence[path] = hashes
    if normalized_self_hash(_git(root, "show", f"HEAD:{SELF_PATH}", binary=True)) != SELF_SOURCE_SHA256:
        raise ValueError("PR935 reviewed policy source digest differs")
    return evidence


def validate_baseline(run: dict, jobs: dict, log: str) -> dict:
    expected = {"id": BASELINE_RUN_ID, "head_sha": BASELINE_SHA, "head_branch": BRANCH,
                "path": ".github/workflows/ci.yml", "event": "pull_request",
                "status": "completed", "conclusion": "failure", "run_attempt": BASELINE_ATTEMPT}
    if (any(run.get(key) != value for key, value in expected.items())
            or run.get("repository", {}).get("full_name") != REPOSITORY):
        raise ValueError("PR935 baseline run is incomplete or has a different identity")
    entries = jobs.get("jobs", [])
    if (not isinstance(entries, list) or jobs.get("total_count") != len(entries)
            or len(entries) != len(BASELINE_JOBS)):
        raise ValueError("PR935 baseline job inventory is incomplete or changed")
    by_name = {}
    for name, (job_id, conclusion) in BASELINE_JOBS.items():
        matches = [job for job in entries if job.get("name") == name]
        if len(matches) != 1:
            raise ValueError("PR935 baseline job is missing or ambiguous")
        job = matches[0]
        expected_job = {"id": job_id, "run_id": BASELINE_RUN_ID, "head_sha": BASELINE_SHA,
                        "run_attempt": BASELINE_ATTEMPT, "head_branch": BRANCH,
                        "status": "completed", "conclusion": conclusion}
        if any(job.get(key) != value for key, value in expected_job.items()):
            raise ValueError(f"PR935 baseline job identity/outcome differs: {name}")
        by_name[name] = job
    steps = by_name["Backend tests"].get("steps", [])
    expected_steps = {**{name: "success" for name in RETAINED_SUCCESS_STEPS},
                      "Run pytest": "failure", **{name: "skipped" for name in PENDING_OPERATIONAL_STEPS}}
    for name, conclusion in expected_steps.items():
        matches = [step for step in steps if step.get("name") == name]
        if len(matches) != 1 or any(matches[0].get(k) != v for k, v in
                                  {"status": "completed", "conclusion": conclusion}.items()):
            raise ValueError(f"PR935 baseline required step differs: {name}")
    if (any(step.get("status") != "completed" or step.get("conclusion") not in {"success", "failure", "skipped"}
            for step in steps)
            or [step.get("name") for step in steps if step.get("conclusion") == "failure"] != ["Run pytest"]):
        raise ValueError("PR935 baseline has an additional failed or incomplete backend step")
    clean = re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", log)
    clean = re.sub(r"(?m)^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?Z\s?", "", clean)
    summaries = re.findall(r"(?m)^(?:=+\s*)?(\d+) failed, (\d+) passed, (\d+) skipped, (\d+) warnings? in [^\n]+", clean)
    if summaries != [("1", "3879", "4", "1")]:
        raise ValueError("PR935 baseline final pytest totals differ or are incomplete")
    if re.findall(r"(?m)^FAILED\s+(\S+)(?:\s|$)", clean) != [TEST_NODE]:
        raise ValueError("PR935 baseline failed-node inventory differs from the one repair")
    if re.search(r"(?m)^(?:ERROR\s|!+.*(?:Interrupted|ERRORS?))", clean):
        raise ValueError("PR935 baseline contains collection/setup errors or interruption")
    return {"sha": BASELINE_SHA, "run_id": BASELINE_RUN_ID, "attempt": BASELINE_ATTEMPT,
            "job_id": BASELINE_JOB_ID, "risk_gate_job_id": by_name["Backend risk gate"]["id"],
            "run_conclusion": "failure", "backend_conclusion": "failure", "full_certificate": None,
            "result": {"failed": 1, "passed": 3879, "skipped": 4, "warnings": 1},
            "failed_nodes": [TEST_NODE], "retained_success_steps": list(RETAINED_SUCCESS_STEPS),
            "pending_operational_steps": list(PENDING_OPERATIONAL_STEPS),
            "artifact_id": ARTIFACT_ID, "artifact_sha256": ARTIFACT_SHA256,
            "report_sha256": hashlib.sha256(log.encode()).hexdigest()}


def resolve_decision(root: Path, *, event: str, number: str, head_ref: str, repository: str):
    relevant = event == "pull_request" and (number == str(PR_NUMBER) or head_ref == BRANCH)
    if not relevant and event != "push":
        return None
    if repository != REPOSITORY:
        if relevant:
            raise ValueError("PR935 continuation repository mismatch")
        return None
    candidate = _git(root, "rev-parse", "HEAD")
    if relevant and (number != str(PR_NUMBER) or head_ref != BRANCH):
        raise ValueError("PR935 continuation event identity mismatch")
    if event == "push" and not _git(root, "ls-tree", "HEAD", "--", SELF_PATH):
        return None
    pr = _github(f"repos/{REPOSITORY}/pulls/{PR_NUMBER}")
    if event == "push":
        associated = _github(f"repos/{REPOSITORY}/commits/{candidate}/pulls")
        related = [item for item in associated if item.get("number") == PR_NUMBER]
        if not related:
            if candidate in {pr.get("head", {}).get("sha"), pr.get("merge_commit_sha")}:
                raise ValueError("PR935 promotion association is incomplete; no full-suite fallback")
            return None
        if len(related) != 1 or pr.get("merged") is not True or pr.get("merge_commit_sha") != candidate:
            raise ValueError("PR935 promotion is not a verified exact-SHA fast-forward")
    if (pr.get("number") != PR_NUMBER or pr.get("base", {}).get("ref") != "main"
            or pr.get("base", {}).get("repo", {}).get("full_name") != REPOSITORY
            or pr.get("head", {}).get("repo", {}).get("full_name") != REPOSITORY
            or pr.get("head", {}).get("ref") != BRANCH or pr.get("head", {}).get("sha") != candidate):
        raise ValueError("PR935 exact head identity is not verified")
    if event == "push" and _github(f"repos/{REPOSITORY}/git/ref/heads/main").get("object", {}).get("sha") != candidate:
        raise ValueError("PR935 promotion is not the exact current main")
    delta = validate_delta(root)
    run = _github(f"repos/{REPOSITORY}/actions/runs/{BASELINE_RUN_ID}")
    jobs = _github(f"repos/{REPOSITORY}/actions/runs/{BASELINE_RUN_ID}/attempts/{BASELINE_ATTEMPT}/jobs?per_page=100")
    artifacts = _github(f"repos/{REPOSITORY}/actions/runs/{BASELINE_RUN_ID}/artifacts?per_page=100")
    matching = [item for item in artifacts.get("artifacts", []) if item.get("id") == ARTIFACT_ID]
    if len(matching) != 1:
        raise ValueError("PR935 original pytest report artifact is missing or ambiguous")
    archive = _github_binary(f"repos/{REPOSITORY}/actions/artifacts/{ARTIFACT_ID}/zip")
    baseline = validate_baseline(run, jobs, validate_artifact(matching[0], archive))
    scope = {"baseline": baseline, "delta": delta, "followup_targets": [TEST_NODE]}
    digest = hashlib.sha256(json.dumps(scope, sort_keys=True).encode()).hexdigest()[:16]
    suite_key = SUITE_PREFIX + digest
    proof = {"scope": "One repaired contract test and pending HTTP/backup gates; not a full-suite pass",
             "status": "failed_baseline_verified_followup_and_operational_gates_pending", "repository": REPOSITORY,
             "pull_request": PR_NUMBER, "candidate_sha": candidate,
             "candidate_tree": _git(root, "rev-parse", "HEAD^{tree}"), "event": event,
             "suite_key": suite_key, **scope}
    (Path(os.environ.get("RUNNER_TEMP", "/tmp")) / EVIDENCE_NAME).write_text(
        json.dumps(proof, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return PolicyDecision(backend_mode=MODE, suite_key=suite_key, focused_tests=(TEST_NODE,),
                          reasons=(f"verified-failed-backend-baseline:{BASELINE_SHA}",
                                   f"baseline-run:{BASELINE_RUN_ID}", "reviewed-exact-test-docs-CI-only-delta:PR935",
                                   "one-repaired-test-and-pending-HTTP-backup-required", "not-a-full-suite-certificate"))


def validate_followup_junit(path: Path) -> None:
    with path.open("rb") as stream:
        content = stream.read(MAX_REPORT_BYTES + 1)
    if len(content) > MAX_REPORT_BYTES or b"<!DOCTYPE" in content or b"<!ENTITY" in content:
        raise ValueError("PR935 follow-up JUnit is not a bounded plain report")
    root = ET.fromstring(content)
    suites, cases = list(root.iter("testsuite")), list(root.iter("testcase"))
    if len(suites) != 1 or len(cases) != 1:
        raise ValueError("PR935 follow-up JUnit must contain exactly one case")
    if any(suites[0].get(key) != value for key, value in
           {"tests": "1", "failures": "0", "errors": "0", "skipped": "0"}.items()):
        raise ValueError("PR935 repaired test must pass without skips or errors")
    test, name = TEST_NODE.split("::")
    if ((cases[0].get("classname"), cases[0].get("name")) != (test.removesuffix(".py").replace("/", "."), name)
            or any(list(root.iter(tag)) for tag in ("failure", "error", "skipped"))):
        raise ValueError("PR935 follow-up JUnit identity or outcome differs")


def run_followup(root: Path, junit: Path) -> int:
    if (os.environ.get("FOCUSED_TESTS") != TEST_NODE
            or os.environ.get("CANDIDATE_SHA") != _git(root, "rev-parse", "HEAD")
            or not re.fullmatch(re.escape(SUITE_PREFIX) + r"[0-9a-f]{16}", os.environ.get("SUITE_KEY", ""))
            or normalized_self_hash((root / SELF_PATH).read_bytes()) != SELF_SOURCE_SHA256):
        raise ValueError("PR935 runner identity, literal selection or source seal differs")
    validate_delta(root)
    if junit.exists() or junit.is_symlink():
        raise ValueError("PR935 follow-up requires a fresh JUnit path, not a prior result")
    # Neither environment addopts nor configuration may extend this selection.
    # The unchanged CI dependencies/conftest still run against isolated PG/Redis.
    env = os.environ.copy()
    env.pop("PYTEST_ADDOPTS", None)
    env.pop("PYTEST_PLUGINS", None)
    result = subprocess.run([sys.executable, "-m", "pytest", "-q", "--tb=short", "--rootdir=.",
                             "-o", "addopts=", TEST_NODE, "--junitxml=" + str(junit.resolve())],
                            cwd=root / "backend", env=env)
    if result.returncode:
        return result.returncode
    validate_followup_junit(junit)
    print("Verified PR935 follow-up: one exact pass; HTTP/backup gates still required.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run only the reviewed PR935 failed contract test")
    parser.add_argument("--run-followup", action="store_true", required=True)
    parser.add_argument("--junit", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(run_followup(Path(__file__).resolve().parents[1], args.junit))
