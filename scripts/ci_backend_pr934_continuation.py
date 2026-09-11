"""Verified PR934 baseline plus real focused tests; never a new full certificate.

This profile is sealed to the reviewed PR934 delta and focused test list. It
cannot accept an incomplete or failed backend baseline. Historical owner
decisions and exact-SHA reuse are untouched; a seal is not baseline approval.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess

try:
    from ci_backend_policy import PolicyDecision, SAFE_TEST_PATH
except ModuleNotFoundError as exc:
    if exc.name != "ci_backend_policy":
        raise
    from scripts.ci_backend_policy import PolicyDecision, SAFE_TEST_PATH


REPOSITORY = "rafaelpaesmeirelles/MeuCardio"
PR_NUMBER = 934
BRANCH = "codex/atelier-mobility-audit-20260911"
BASELINE_SHA = "7201d7377e393b53afb0e27bf0ca1dca81173095"
BASELINE_RUN_ID = 34635195463
BASELINE_JOB_ID = 103381373201
BASELINE_ATTEMPT = 1
SUITE_PREFIX = "backend-risk-v1-focused-pr934-7201d737-"
EVIDENCE_NAME = "backend-pr934-continuation.json"

# Seal only after independent review of the final delta. Each entry must be
# {"before": <SHA256 or None for addition>, "after": <SHA256 or None for deletion>}.
# No caller-controlled manifest, directory wildcard or environment override.
REVIEWED_DELTA: dict[str, dict[str, str | None]] | None = {
    "backend/app/data/pricing/kairos-453-2026-08.json": {
        "before": None,
        "after": "ff070fdf46b257253d9e618de56bfb63f3e2b33333bab332e734537d05ec8363"
    },
    "backend/app/data/pricing/kairos-453-2026-08-curation-audit.json": {
        "before": None,
        "after": "593aa4d944c6e65f40c1ea0048363cc75ccf91b372a500ed5ef1c1d3b101860a"
    },
    "backend/app/services/pricing/kairos_provider.py": {
        "before": "555f89a8fa3d7d0cf2efa33e7fe11d3aadbd108b71fdd0f2b690d1ad9cfc6861",
        "after": "0ef44f20389577aaf11c8eb81a741a9a903e731a08ac48153af01eb15e930faf"
    },
    "backend/scripts/prepare_kairos_snapshot.py": {
        "before": "6e68b525cd21fd6a28f5e3d419dcda644130ec47822e83064fa432d08b523b00",
        "after": "574f99f84d4682c44a087ca73335e9bacec70b26b767651ed8ccf462ed764140"
    },
    "backend/tests/test_kairos_matching_no_db.py": {
        "before": "1e07b6849df244be56bd5d7d1189073cc2c1fdd00b297485b9d37f4ed1cc011d",
        "after": "78c349361ac92e50a8aefa431b5611d76d8892a09c3914307e6c10a476a6130c"
    },
    "backend/tests/test_kairos_preparation_no_db.py": {
        "before": "9b7701299f6af38e78669c77a53d6afd3d243060d7d5b31675f85317206eb445",
        "after": "84173001bfbe845f60b5973a8b7bbe750c7fcd3e5741ff9bb84f661066d8c105"
    },
    "backend/tests/test_kairos_corpus_boundary_no_db.py": {
        "before": None,
        "after": "44b5bc931cb2a34a941715d49c3f1d58dec9f07f32aa4e883de4dcdcaccba664"
    },
    "docs/pricing-architecture.md": {
        "before": "3ec022b87635c8e52f1669644dffbb75fc0104677f5745a3e5ac5add7066c557",
        "after": "dbb5d0895f79693a098a7f069102c82e162c8e42d026df0a6b1f7ae2e2605b8a"
    },
    "frontend/scripts/atelier-clinical-functional-qa.mjs": {
        "before": "f517e9aaef0db039c3bc681e1657fef1eb59e56ae854dd081d5c6af45680cbbf",
        "after": "581a53d5a040fddc0b30d6388d1fca25936f5c44f22d07a0163f34c4efa17a38"
    },
    "medicamentos/kairos-453-2026-08.json": {
        "before": "ff070fdf46b257253d9e618de56bfb63f3e2b33333bab332e734537d05ec8363",
        "after": "7a7ac549bead518f3566dce41e64702090448545c35d7b56e3316d79ef896e9e"
    },
    "medicamentos/kairos-453-2026-08-curation-audit.json": {
        "before": "593aa4d944c6e65f40c1ea0048363cc75ccf91b372a500ed5ef1c1d3b101860a",
        "after": None
    },
    "frontend/scripts/check-form-control-contrast.mjs": {
        "before": "85560533a139f034415150ce7206109aec3dba5faa9de0f4fd3c90bac06452b8",
        "after": "eaa1a2a6c639812134795addb57edeb6ab489d7ef4f5a8ae931944c2a9d154ec"
    },
    "docs/qa/2026-09-11-auditoria-funcoes-atelier.md": {
        "before": "b9e6206096a6bc36d2c593baebfd80181ed2e5d35e2f82daba1313eedd365220",
        "after": "874bd9c0082757e4e0607d730163047daca9ae4544da6b33afcd8cafd6e78565"
    },
    "frontend/src/components/DeferredAssistantMap.tsx": {
        "before": None,
        "after": "08621e94f23c064d2be038b29e16039432becce7461fb22e81a3b2bbfd6dcbcd"
    },
    "frontend/src/components/PersonalAssistantPanel.tsx": {
        "before": "8adfdd9afa4dcda9b2d3e12ca023ff73c39df0a630f754d70a147a81853f086b",
        "after": "6a9c4be44046a6059f2b365b01df1f5dcd659ba715f92bbf33464010a185fdbf"
    },
    "frontend/src/components/PatientPrescricao.tsx": {
        "before": "eed4c2a532c8f365017d6d3b75d34472d3a5dce5eafce35b30ed43938fb298a7",
        "after": "16ec26b08b2df669f28f80bde84a2bcb033d0b8e03861479c2152d713445f48e"
    },
    "frontend/scripts/check-assistant-map-loading.test.mjs": {
        "before": None,
        "after": "a3f65652770816197f317b867e88dc5d4de26d70f3e7fd46f3ad4d670b5ce848"
    }
}
FOCUSED_TESTS: tuple[str, ...] = (
    "tests/test_kairos_matching_no_db.py",
    "tests/test_kairos_preparation_no_db.py",
    "tests/test_kairos_corpus_boundary_no_db.py",
)
POLICY_DELTA: dict[str, dict[str, str | None]] | None = {
    ".github/workflows/ci.yml": {
        "before": "29b1371c4c737d046cc4c0e79dfa528cd5c5507df4ea988a7e18a75e7e382c84",
        "after": "60dfcc1141e9332a6d6bab683a049c3c3687df6ec1fd14585e172d4559985b13",
    },
    "scripts/ci_backend_followup.py": {
        "before": "c466fa3dfb5fffe797835588f078ce50d4cbe341115a020a903538b8a66038ae",
        "after": "28eb01516956749a2c93690b9f15028989724c703e75a37639e18b766c567f9f",
    },
    "scripts/tests/test_ci_pr934_continuation.py": {
        "before": None,
        "after": "0138d20441bc501edff1850393707db63c0ce7049be3cd4aaf654fa86c30bcdd",
    },
}
SELF_SOURCE_SHA256 = "36e552402997186c8cbfb059fffea87d14339678c6ef8d1c77f52b4d7c724e28"
SELF_PATH = "scripts/ci_backend_pr934_continuation.py"

# Three policy files are pinned byte-for-byte. This module is pinned after
# replacing ONLY its own SELF_SOURCE_SHA256 literal, avoiding self-reference
# without excluding any reviewed delta, focused test or executable logic.
POLICY_PATHS = frozenset({
    "scripts/ci_backend_pr934_continuation.py",
    "scripts/tests/test_ci_pr934_continuation.py",
    "scripts/ci_backend_followup.py",
    ".github/workflows/ci.yml",
})
REQUIRED_BASELINE_STEPS = (
    "Enforce Node 24 action runtimes", "Validate operational shell scripts",
    "Audit Python production dependencies", "Apply migrations through the operational command",
    "Verify migration command is idempotent", "Smoke test explicit administrator bootstrap",
    "Compile Python modules", "Run pytest", "Exercise live HTTP release flow",
    "Prove PostgreSQL backup and restore", "Backend suite certificate backend-risk-v1-full",
)


def _git(root: Path, *args: str, binary: bool = False):
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True, timeout=20)
    if result.returncode:
        raise ValueError("Cannot verify PR934 Git evidence")
    return result.stdout if binary else result.stdout.decode("utf-8").strip()


def _github(path: str):
    try:
        result = subprocess.run(["gh", "api", path], capture_output=True, timeout=30)
        if result.returncode or len(result.stdout) > 2 * 1024 * 1024:
            raise ValueError("Cannot verify bounded PR934 GitHub evidence")
        return json.loads(result.stdout)
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
        raise ValueError("Cannot verify PR934 GitHub evidence") from exc


def _sha256_blob(root: Path, ref: str, path: str) -> str | None:
    entry = _git(root, "ls-tree", ref, "--", path)
    if not entry:
        return None
    if not entry.startswith("100644 blob "):
        raise ValueError(f"PR934 delta is not a regular non-executable file: {path}")
    return hashlib.sha256(_git(root, "show", f"{ref}:{path}", binary=True)).hexdigest()


def normalized_self_hash(source: bytes) -> str:
    source, count = re.subn(
        rb'^SELF_SOURCE_SHA256 = (?:None|"[0-9a-f]{64}")$',
        b'SELF_SOURCE_SHA256 = "<self-digest>"', source, flags=re.MULTILINE)
    if count != 1:
        raise ValueError("PR934 self-digest declaration is missing or ambiguous")
    return hashlib.sha256(source).hexdigest()


def validate_delta(root: Path) -> dict:
    if not REVIEWED_DELTA or not FOCUSED_TESTS or not POLICY_DELTA or not SELF_SOURCE_SHA256:
        raise ValueError("PR934 continuation is not sealed; baseline/final delta review required")
    if set(REVIEWED_DELTA) & POLICY_PATHS:
        raise ValueError("PR934 product hashes cannot override policy paths")
    if set(POLICY_DELTA) != POLICY_PATHS - {SELF_PATH}:
        raise ValueError("PR934 policy hashes must cover the exact three companion files")
    reviewed = {**REVIEWED_DELTA, **POLICY_DELTA}
    for path, hashes in reviewed.items():
        if (PurePosixPath(path).is_absolute() or ".." in PurePosixPath(path).parts
                or not re.fullmatch(r"[A-Za-z0-9_.\-/]+", path)
                or set(hashes) != {"before", "after"}
                or any(value is not None and not re.fullmatch(r"[0-9a-f]{64}", value)
                       for value in hashes.values())):
            raise ValueError("Invalid reviewed PR934 path/hash pair")
    _git(root, "merge-base", "--is-ancestor", BASELINE_SHA, "HEAD")
    if _git(root, "status", "--porcelain", "--untracked-files=no"):
        raise ValueError("PR934 continuation checkout has uncommitted tracked changes")
    changed = set(_git(root, "diff", "--no-renames", "--name-only", f"{BASELINE_SHA}..HEAD").splitlines())
    if changed != set(REVIEWED_DELTA) | POLICY_PATHS:
        raise ValueError("PR934 continuation changed paths differ from the reviewed exact delta")
    evidence = {}
    for path in sorted(changed):
        hashes = {"before": _sha256_blob(root, BASELINE_SHA, path), "after": _sha256_blob(root, "HEAD", path)}
        if path in reviewed and hashes != reviewed[path]:
            raise ValueError(f"PR934 reviewed content hash differs: {path}")
        if path in POLICY_PATHS and hashes["after"] is None:
            raise ValueError("PR934 policy implementation cannot be deleted")
        evidence[path] = hashes
    if normalized_self_hash(_git(root, "show", f"HEAD:{SELF_PATH}", binary=True)) != SELF_SOURCE_SHA256:
        raise ValueError("PR934 reviewed policy source digest differs")
    if len(set(FOCUSED_TESTS)) != len(FOCUSED_TESTS):
        raise ValueError("Duplicate PR934 focused test")
    for test in FOCUSED_TESTS:
        if not SAFE_TEST_PATH.fullmatch(test) or _sha256_blob(root, "HEAD", f"backend/{test}") is None:
            raise ValueError("PR934 focused test is unsafe or missing")
    return evidence


def validate_baseline(run: dict, jobs: dict) -> dict:
    expected = {"id": BASELINE_RUN_ID, "head_sha": BASELINE_SHA, "head_branch": BRANCH,
                "path": ".github/workflows/ci.yml", "event": "pull_request",
                "status": "completed", "run_attempt": BASELINE_ATTEMPT}
    if (any(run.get(key) != value for key, value in expected.items())
            or run.get("repository", {}).get("full_name") != REPOSITORY
            or run.get("conclusion") not in {"success", "failure"}):
        raise ValueError("PR934 baseline run is incomplete or has a different identity")
    entries = jobs.get("jobs", [])
    if not isinstance(entries, list) or jobs.get("total_count") != len(entries):
        raise ValueError("PR934 baseline job inventory is incomplete")
    by_name = {}
    for name in ("Backend tests", "Backend risk gate"):
        found = [job for job in entries if job.get("name") == name]
        if len(found) != 1:
            raise ValueError("PR934 baseline job is missing or ambiguous")
        job = found[0]
        if (any(job.get(key) != value for key, value in {
                "run_id": BASELINE_RUN_ID, "head_sha": BASELINE_SHA,
                "run_attempt": BASELINE_ATTEMPT, "head_branch": BRANCH,
                "status": "completed", "conclusion": "success"}.items())
                or (name == "Backend tests" and job.get("id") != BASELINE_JOB_ID)):
            raise ValueError("PR934 baseline backend/gate is not completely approved")
        by_name[name] = job
    for name in REQUIRED_BASELINE_STEPS:
        matches = [step for step in by_name["Backend tests"].get("steps", []) if step.get("name") == name]
        if len(matches) != 1 or any(matches[0].get(k) != v for k, v in
                                  {"status": "completed", "conclusion": "success"}.items()):
            raise ValueError(f"PR934 baseline required step is not approved: {name}")
    # The original frontend can fail while the backend is independently green.
    # Reject additional failed/cancelled jobs rather than treating them as known.
    failures = [job for job in entries if job.get("conclusion") == "failure"]
    if (any(job.get("status") != "completed" or job.get("conclusion") not in {"success", "failure", "skipped"}
            for job in entries)
            or any(job.get("name") != "Frontend build" for job in failures)
            or (run["conclusion"] == "failure") != bool(failures)):
        raise ValueError("PR934 baseline has an unaccounted failure or incomplete job")
    return {"sha": BASELINE_SHA, "run_id": BASELINE_RUN_ID, "attempt": BASELINE_ATTEMPT,
            "job_id": BASELINE_JOB_ID, "risk_gate_job_id": by_name["Backend risk gate"]["id"],
            "run_conclusion": run["conclusion"], "backend_conclusion": "success",
            "certificate": "backend-risk-v1-full", "failed_other_jobs": [j["name"] for j in failures]}


def resolve_decision(root: Path, *, event: str, number: str, head_ref: str, repository: str):
    relevant = event == "pull_request" and (number == str(PR_NUMBER) or head_ref == BRANCH)
    if not relevant and event != "push":
        return None
    if repository != REPOSITORY:
        if relevant:
            raise ValueError("PR934 continuation repository mismatch")
        return None
    candidate = _git(root, "rev-parse", "HEAD")
    if relevant and (number != str(PR_NUMBER) or head_ref != BRANCH):
        raise ValueError("PR934 continuation event identity mismatch")
    # Historical pushes from before this profile cannot be its promotion. Do
    # not add API dependencies to unrelated historical owner/reuse decisions.
    if event == "push" and not _git(root, "ls-tree", "HEAD", "--", SELF_PATH):
        return None
    pr = _github(f"repos/{REPOSITORY}/pulls/{PR_NUMBER}")
    if event == "push":
        associated = _github(f"repos/{REPOSITORY}/commits/{candidate}/pulls")
        related = [item for item in associated if item.get("number") == PR_NUMBER]
        if not related:
            if candidate in {pr.get("head", {}).get("sha"), pr.get("merge_commit_sha")}:
                raise ValueError("PR934 promotion association is incomplete; no automatic full fallback")
            return None
        if len(related) != 1:
            raise ValueError("PR934 promotion association is ambiguous")
        if pr.get("merged") is not True or pr.get("merge_commit_sha") != candidate:
            raise ValueError("PR934 promotion merge metadata is incomplete or not the exact fast-forward SHA")
    if (pr.get("number") != PR_NUMBER or pr.get("base", {}).get("ref") != "main"
            or pr.get("base", {}).get("repo", {}).get("full_name") != REPOSITORY
            or pr.get("head", {}).get("repo", {}).get("full_name") != REPOSITORY
            or pr.get("head", {}).get("ref") != BRANCH or pr.get("head", {}).get("sha") != candidate):
        raise ValueError("PR934 exact head identity is not verified")
    if event == "push" and _github(f"repos/{REPOSITORY}/git/ref/heads/main").get("object", {}).get("sha") != candidate:
        raise ValueError("PR934 promotion is not the exact current main")
    delta = validate_delta(root)
    run = _github(f"repos/{REPOSITORY}/actions/runs/{BASELINE_RUN_ID}")
    jobs = _github(f"repos/{REPOSITORY}/actions/runs/{BASELINE_RUN_ID}/attempts/{BASELINE_ATTEMPT}/jobs?per_page=100")
    baseline = validate_baseline(run, jobs)
    scope = {"baseline": baseline, "delta": delta, "focused_tests": list(FOCUSED_TESTS)}
    digest = hashlib.sha256(json.dumps(scope, sort_keys=True).encode()).hexdigest()[:16]
    suite_key = SUITE_PREFIX + digest
    proof = {"scope": "Verified complete backend baseline plus real focused follow-up; not a new full-suite pass",
             "status": "baseline_verified_focused_tests_pending", "repository": REPOSITORY,
             "pull_request": PR_NUMBER, "candidate_sha": candidate,
             "candidate_tree": _git(root, "rev-parse", "HEAD^{tree}"), "event": event,
             "suite_key": suite_key, **scope}
    (Path(os.environ.get("RUNNER_TEMP", "/tmp")) / EVIDENCE_NAME).write_text(
        json.dumps(proof, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return PolicyDecision(backend_mode="focused", suite_key=suite_key,
                          focused_tests=FOCUSED_TESTS,
                          reasons=(f"verified-complete-backend-baseline:{BASELINE_SHA}",
                                   f"baseline-run:{BASELINE_RUN_ID}", "reviewed-exact-delta:PR934",
                                   "real-focused-tests-required:not-a-new-full-suite-certificate"))
