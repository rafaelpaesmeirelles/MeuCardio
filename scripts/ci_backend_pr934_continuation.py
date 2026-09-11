"""PR934's six failed tests plus retained baseline evidence, not a full pass.

The original run failed: 6 failed, 3810 passed, 4 skipped. Its pending HTTP and
backup gates must execute after the six repairs and the reviewed Káiros tests.
No failed/incomplete follow-up or different delta can become a full certificate.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

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
MODE = "pr934-failed-tests-followup"
SUITE_PREFIX = "backend-risk-v1-failed-tests-pr934-7201d737-"
EVIDENCE_NAME = "backend-pr934-continuation.json"
ARTIFACT_ID = 10279800250
ARTIFACT_SHA256 = "a83329b9d70bbff8a030c7791945c439b73faa1bcfc484c4031b6e787f0df3ab"
ARTIFACT_BYTES = 2217
MAX_REPORT_BYTES = 2 * 1024 * 1024
FAILED_TEST_NODES = (
    "tests/test_feature_inventory.py::test_published_feature_inventory_is_intact",
    "tests/test_home_canonical_mobility_contract.py::test_mapa_do_destino_existe_no_mobile_e_no_rail_desktop_antes_da_rota",
    "tests/test_mobile_commute_regressions_contract.py::test_mapa_preserva_instancia_entre_atualizacoes",
    "tests/test_prehome_canonical_ui.py::test_scoped_light_theme_remains_after_global_contrast_guard",
    "tests/test_receituario_workspace_price_contract.py::test_receituario_workspace_uses_audited_kairos_price_without_changing_shell",
    "tests/test_reconcile_content_full_run.py::test_reconcile_publish_reviewed_termina_sem_excecao_contra_conteudo_real",
)

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
        "after": "1b447d01c0e74bb0c81f3deeff593e7e6fe9701e0d5464b71269ae8f270ff58d"
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
    },
    "scripts/feature_inventory.py": {
        "before": "bcc9176dbfbf6f6c7484d9178d8790d8d35ebf80e7cb20d4b0a3687a8aa6ba3b",
        "after": "905ed2ebf33508cebd3421e57091dcae44f3fe62ccf1c2e7b381c11fddcf6c7d"
    },
    "backend/tests/test_home_canonical_mobility_contract.py": {
        "before": "58c5ab5df8a373b8e3155a8ea0c394ec16ca083c41f648641a4977eb21119abe",
        "after": "390fc10b7de2db0f733e013939d893217862d57178e02893f654d51855c98418"
    },
    "backend/tests/test_mobile_commute_regressions_contract.py": {
        "before": "733b6d0149191a1927c6c25dc9d15dcafaebdf0e4bc9924a603e4f807f83d2b2",
        "after": "d115007f01f97c014ab7fa611e399d1a4130472db3485108a648c2a9bd0fc426"
    },
    "backend/tests/test_prehome_canonical_ui.py": {
        "before": "cf7905570113bc5831c6505b162fda71e6d9eaea984f126fe6e8e05a4337edfd",
        "after": "69ed82ca64a625e953edccfae1b8364bf84facca144285651393341cffbbaa9b"
    },
    "backend/tests/test_receituario_workspace_price_contract.py": {
        "before": "c8b166038a486f25c09f72470ede1491ff5db88dea3480f61b7e50be45d29bbe",
        "after": "4d2a5f5186f886ad65133d9b37d825099865bbd86fd8d8b9917df2183ce52ffb"
    }
}
FOCUSED_TESTS: tuple[str, ...] = (
    "tests/test_kairos_matching_no_db.py",
    "tests/test_kairos_preparation_no_db.py",
    "tests/test_kairos_corpus_boundary_no_db.py",
)
EXPECTED_KAIROS_TESTS = 32
POLICY_DELTA: dict[str, dict[str, str | None]] | None = {
    ".github/workflows/ci.yml": {
        "before": "29b1371c4c737d046cc4c0e79dfa528cd5c5507df4ea988a7e18a75e7e382c84",
        "after": "29eece1ccaaaa49761d8a0664539b143672dffe39d900503a29d8820b5430fc3",
    },
    "scripts/ci_backend_followup.py": {
        "before": "c466fa3dfb5fffe797835588f078ce50d4cbe341115a020a903538b8a66038ae",
        "after": "28eb01516956749a2c93690b9f15028989724c703e75a37639e18b766c567f9f",
    },
    "scripts/tests/test_ci_pr934_continuation.py": {
        "before": None,
        "after": "89a19f08fd03f827dcf7b6189b3d995e6a33f5bcc9986df3c3c4cfc57e122c1c",
    },
}
SELF_SOURCE_SHA256 = "24b2bb0344e443d999017ffd4c6b3a5d4c9bcdb4bda987210ccd227c7198a6e6"
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


def _github_binary(path: str) -> bytes:
    # Size bounded after gh exits; this is not a subprocess memory sandbox.
    # The pinned ZIP is 2217 bytes. Decompression is separately bounded below.
    try:
        result = subprocess.run(["gh", "api", "-H", "Cache-Control: no-cache", path],
                                capture_output=True, timeout=45)
        if result.returncode or len(result.stdout) > MAX_REPORT_BYTES:
            raise ValueError("Cannot read the bounded PR934 baseline artifact")
        return result.stdout
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ValueError("Cannot read the PR934 baseline artifact") from exc


def validate_artifact(artifact: dict, archive: bytes) -> str:
    expected = {"id": ARTIFACT_ID, "name": "backend-pytest-failure", "expired": False,
                "digest": "sha256:" + ARTIFACT_SHA256, "size_in_bytes": ARTIFACT_BYTES}
    if any(artifact.get(key) != value for key, value in expected.items()):
        raise ValueError("PR934 baseline artifact identity/digest/size differs")
    provenance = {"id": BASELINE_RUN_ID, "head_sha": BASELINE_SHA, "head_branch": BRANCH,
                  "repository_id": 1312508910, "head_repository_id": 1312508910}
    if any(artifact.get("workflow_run", {}).get(key) != value for key, value in provenance.items()):
        raise ValueError("PR934 baseline artifact provenance differs")
    if len(archive) != ARTIFACT_BYTES or hashlib.sha256(archive).hexdigest() != ARTIFACT_SHA256:
        raise ValueError("PR934 baseline artifact bytes differ from the pinned digest")
    with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
        entries = bundle.infolist()
        if len(entries) != 1 or entries[0].filename != "pytest-output.txt" or entries[0].file_size > MAX_REPORT_BYTES:
            raise ValueError("PR934 baseline artifact has unexpected members")
        with bundle.open(entries[0]) as stream:
            content = stream.read(MAX_REPORT_BYTES + 1)
        if len(content) > MAX_REPORT_BYTES:
            raise ValueError("PR934 baseline report exceeds bounded size")
        return content.decode("utf-8")


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
    for node in FAILED_TEST_NODES:
        parts = node.split("::")
        if (len(parts) != 2 or not SAFE_TEST_PATH.fullmatch(parts[0])
                or not re.fullmatch(r"test_[A-Za-z0-9_]+", parts[1])
                or _sha256_blob(root, "HEAD", f"backend/{parts[0]}") is None):
            raise ValueError("PR934 failed test node is unsafe or missing")
    return evidence


def validate_baseline(run: dict, jobs: dict, log: str) -> dict:
    expected = {"id": BASELINE_RUN_ID, "head_sha": BASELINE_SHA, "head_branch": BRANCH,
                "path": ".github/workflows/ci.yml", "event": "pull_request",
                "status": "completed", "run_attempt": BASELINE_ATTEMPT}
    if (any(run.get(key) != value for key, value in expected.items())
            or run.get("repository", {}).get("full_name") != REPOSITORY
            or run.get("conclusion") != "failure"):
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
                "status": "completed", "conclusion": "failure"}.items())
                or (name == "Backend tests" and job.get("id") != BASELINE_JOB_ID)):
            raise ValueError("PR934 baseline backend/gate differs from the reviewed failed run")
        by_name[name] = job
    expected_steps = {**{name: "success" for name in RETAINED_SUCCESS_STEPS},
                      "Run pytest": "failure", **{name: "skipped" for name in PENDING_OPERATIONAL_STEPS}}
    for name, conclusion in expected_steps.items():
        matches = [step for step in by_name["Backend tests"].get("steps", []) if step.get("name") == name]
        if len(matches) != 1 or any(matches[0].get(k) != v for k, v in
                                  {"status": "completed", "conclusion": conclusion}.items()):
            raise ValueError(f"PR934 baseline required step differs: {name}")
    if {step.get("name") for step in by_name["Backend tests"].get("steps", [])
            if step.get("conclusion") == "failure"} != {"Run pytest"}:
        raise ValueError("PR934 baseline contains an additional failed backend step")
    failures = [job for job in entries if job.get("conclusion") == "failure"]
    if (any(job.get("status") != "completed" or job.get("conclusion") not in {"success", "failure", "skipped"}
            for job in entries)
            or sorted(job.get("name", "") for job in failures) != ["Backend risk gate", "Backend tests", "Frontend build"]):
        raise ValueError("PR934 baseline has an unaccounted failure or incomplete job")
    clean = re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", log)
    clean = re.sub(r"(?m)^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?Z\s?", "", clean)
    summaries = re.findall(r"(?m)^(?:=+\s*)?(\d+) failed, (\d+) passed, (\d+) skipped, (\d+) warnings? in [^\n]+", clean)
    if summaries != [("6", "3810", "4", "1")]:
        raise ValueError("PR934 baseline final pytest totals differ or are incomplete")
    if re.findall(r"(?m)^FAILED\s+(\S+)(?:\s|$)", clean) != list(FAILED_TEST_NODES):
        raise ValueError("PR934 baseline failed-node inventory differs from the exact six repairs")
    if re.search(r"(?m)^(?:ERROR\s|!+.*(?:Interrupted|ERRORS?))", clean):
        raise ValueError("PR934 baseline contains collection/setup errors or interruption")
    return {"sha": BASELINE_SHA, "run_id": BASELINE_RUN_ID, "attempt": BASELINE_ATTEMPT,
            "job_id": BASELINE_JOB_ID, "risk_gate_job_id": by_name["Backend risk gate"]["id"],
            "run_conclusion": "failure", "backend_conclusion": "failure", "full_certificate": None,
            "result": {"failed": 6, "passed": 3810, "skipped": 4, "warnings": 1},
            "failed_nodes": list(FAILED_TEST_NODES), "retained_success_steps": list(RETAINED_SUCCESS_STEPS),
            "pending_operational_steps": list(PENDING_OPERATIONAL_STEPS),
            "artifact_id": ARTIFACT_ID, "artifact_sha256": ARTIFACT_SHA256,
            "report_sha256": hashlib.sha256(log.encode()).hexdigest()}


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
    artifacts = _github(f"repos/{REPOSITORY}/actions/runs/{BASELINE_RUN_ID}/artifacts?per_page=100")
    matching = [item for item in artifacts.get("artifacts", []) if item.get("id") == ARTIFACT_ID]
    if len(matching) != 1:
        raise ValueError("PR934 original pytest report artifact is missing or ambiguous")
    archive = _github_binary(f"repos/{REPOSITORY}/actions/artifacts/{ARTIFACT_ID}/zip")
    log = validate_artifact(matching[0], archive)
    baseline = validate_baseline(run, jobs, log)
    targets = FAILED_TEST_NODES + FOCUSED_TESTS
    scope = {"baseline": baseline, "delta": delta, "followup_targets": list(targets)}
    digest = hashlib.sha256(json.dumps(scope, sort_keys=True).encode()).hexdigest()[:16]
    suite_key = SUITE_PREFIX + digest
    proof = {"scope": "Six failed tests plus reviewed Kairos deltas and pending HTTP/backup gates; not a full-suite pass",
             "status": "failed_baseline_verified_followup_and_operational_gates_pending", "repository": REPOSITORY,
             "pull_request": PR_NUMBER, "candidate_sha": candidate,
             "candidate_tree": _git(root, "rev-parse", "HEAD^{tree}"), "event": event,
             "suite_key": suite_key, **scope}
    (Path(os.environ.get("RUNNER_TEMP", "/tmp")) / EVIDENCE_NAME).write_text(
        json.dumps(proof, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return PolicyDecision(backend_mode=MODE, suite_key=suite_key,
                          focused_tests=targets,
                          reasons=(f"verified-failed-backend-baseline:{BASELINE_SHA}",
                                   f"baseline-run:{BASELINE_RUN_ID}", "reviewed-exact-delta:PR934",
                                   "six-failed-nodes-plus-Kairos-tests-and-pending-HTTP-backup-required",
                                   "not-a-full-suite-certificate"))


def expected_followup_cases(root: Path) -> set[tuple[str, str]]:
    """Read pinned test sources as AST only: no test imports or DB side effects."""
    expected = set()
    for node in FAILED_TEST_NODES:
        test, name = node.split("::")
        tree = ast.parse((root / "backend" / test).read_text(encoding="utf-8"))
        if not any(isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == name
                   for item in tree.body):
            raise ValueError("A required PR934 failed-node function is absent")
        expected.add((test.removesuffix(".py").replace("/", "."), name))
    kairos = set()
    for test in FOCUSED_TESTS:
        path = root / "backend" / test
        source = path.read_bytes()
        if hashlib.sha256(source).hexdigest() != (REVIEWED_DELTA or {}).get("backend/" + test, {}).get("after"):
            raise ValueError("A selected PR934 pricing test differs from its reviewed hash")
        module = test.removesuffix(".py").replace("/", ".")
        tree = ast.parse(source)
        for item in tree.body:
            if isinstance(item, ast.ClassDef):
                for method in item.body:
                    if isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef)) and method.name.startswith("test_"):
                        kairos.add((module + "." + item.name, method.name))
            elif isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name.startswith("test_"):
                kairos.add((module, item.name))
    if len(expected) != 6 or len(kairos) != EXPECTED_KAIROS_TESTS or expected & kairos:
        raise ValueError("PR934 follow-up static inventory is not six repairs plus the reviewed pricing cases")
    return expected | kairos


def validate_followup_junit(path: Path, expected: set[tuple[str, str]]) -> None:
    with path.open("rb") as stream:
        content = stream.read(MAX_REPORT_BYTES + 1)
    if len(content) > MAX_REPORT_BYTES or b"<!DOCTYPE" in content or b"<!ENTITY" in content:
        raise ValueError("PR934 follow-up JUnit is not a bounded plain report")
    root = ET.fromstring(content)
    suites, cases = list(root.iter("testsuite")), list(root.iter("testcase"))
    if len(suites) != 1 or len(cases) != len(expected):
        raise ValueError("PR934 follow-up JUnit has missing or extra cases")
    if any(suites[0].get(key) != value for key, value in
           {"tests": str(len(expected)), "failures": "0", "errors": "0", "skipped": "0"}.items()):
        raise ValueError("PR934 follow-up must pass every selected case without skips or errors")
    if ({(case.get("classname"), case.get("name")) for case in cases} != expected
            or any(list(root.iter(tag)) for tag in ("failure", "error", "skipped"))):
        raise ValueError("PR934 follow-up JUnit identities or outcomes differ")


def run_followup(root: Path, junit: Path) -> int:
    """Execute only the source-literal selection inside the CI test environment."""
    targets = FAILED_TEST_NODES + FOCUSED_TESTS
    if (os.environ.get("FOCUSED_TESTS") != " ".join(targets)
            or os.environ.get("CANDIDATE_SHA") != _git(root, "rev-parse", "HEAD")
            or not re.fullmatch(re.escape(SUITE_PREFIX) + r"[0-9a-f]{16}", os.environ.get("SUITE_KEY", ""))
            or normalized_self_hash((root / SELF_PATH).read_bytes()) != SELF_SOURCE_SHA256):
        raise ValueError("PR934 runner identity, literal selection or source seal differs")
    expected = expected_followup_cases(root)
    # No shell, caller-supplied nodes, collection fallback, xfail or implicit full
    # suite. --rootdir fixes JUnit classnames relative to backend/tests.
    result = subprocess.run([sys.executable, "-m", "pytest", "-q", "--tb=short", "--rootdir=.",
                             *targets, "--junitxml=" + str(junit.resolve())], cwd=root / "backend")
    if result.returncode:
        return result.returncode
    validate_followup_junit(junit, expected)
    print(f"Verified PR934 follow-up: {len(expected)} exact passes; HTTP/backup gates still required.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run only the reviewed PR934 repairs and pricing tests")
    parser.add_argument("--run-followup", action="store_true", required=True)
    parser.add_argument("--junit", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(run_followup(Path(__file__).resolve().parents[1], args.junit))
