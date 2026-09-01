#!/usr/bin/env python3
"""Single source of truth for PR CI reuse and final release gates.

The policy is deliberately fail-closed. Only documentation-only changes skip
backend tests. Frontend changes run the reviewed backend contract set; isolated
test modules may run as a targeted selection. Every other change requires the
complete backend certification.
"""

from __future__ import annotations

import argparse
import ast
from dataclasses import asdict, dataclass
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Any, Iterable, Sequence
from urllib.parse import quote


ATTESTATION_SCHEMA = 3
CI_WORKFLOW = {
    "name": "CI",
    "path": ".github/workflows/ci.yml",
    "event": "pull_request",
}
DEPLOY_WORKFLOW = {
    "name": "Deploy production",
    "path": ".github/workflows/deploy-production.yml",
}
DEPLOY_JOB_NAME = "Deploy certified web and Android release"
FRONTEND_CONTRACT_TESTS = (
    "backend/tests/test_agenda_routine_calendar_regression.py",
    "backend/tests/test_all_internal_surfaces_board_lock.py",
    "backend/tests/test_assistant_stream_ui_regression.py",
    "backend/tests/test_canonical_branding_contract.py",
    "backend/tests/test_cardiologia_intensiva_uco_contract.py",
    "backend/tests/test_clinical_os_launch_contract.py",
    "backend/tests/test_clinical_os_privacy_contract.py",
    "backend/tests/test_condicoes_profundas_adulto.py",
    "backend/tests/test_deploy_contract.py",
    "backend/tests/test_emergencia_fluxograma_busca_contract.py",
    "backend/tests/test_fullscreen_social_login_contract.py",
    "backend/tests/test_guia_doencas_regressions.py",
    "backend/tests/test_home_canonical_mobility_contract.py",
    "backend/tests/test_home_mobile_mobility_contract.py",
    "backend/tests/test_home_visual_contract.py",
    "backend/tests/test_identidade_documentos_audit.py",
    "backend/tests/test_mobile_commute_regressions_contract.py",
    "backend/tests/test_mobile_login_recovery_contract.py",
    "backend/tests/test_painel_menu_acervo.py",
    "backend/tests/test_panel_acervo_comunicacao_contract.py",
    "backend/tests/test_prehome_approved_auth_flow.py",
    "backend/tests/test_prehome_canonical_ui.py",
    "backend/tests/test_product_stabilization_frontend_contract.py",
    "backend/tests/test_public_prescription_verification_portal.py",
    "backend/tests/test_receituario_workspace_price_contract.py",
    "backend/tests/test_release_candidate_hotfix_contract.py",
    "backend/tests/test_reparos_pendentes_pr46.py",
    "backend/tests/test_rx_signature_queue_ui_contract.py",
    "backend/tests/test_tudo_com_tudo_medication_ui_contract.py",
    "backend/tests/test_tudo_com_tudo_mobile_contract.py",
    "backend/tests/test_uco_hyperkalemia_safety_clean.py",
    "backend/tests/test_windows_pending_release_contract.py",
)
RELEASE_GATES = (
    {
        "name": "Release final gate dispatcher",
        "path": ".github/workflows/release-final-dispatch.yml",
        "event": "push",
    },
    {
        "name": "RC2 Acceptance — Canonical CorVIA",
        "path": ".github/workflows/rc2-acceptance.yml",
        "event": "workflow_dispatch",
    },
    {
        "name": "Visual QA — Clinical OS",
        "path": ".github/workflows/visual-qa.yml",
        "event": "workflow_dispatch",
    },
    {
        "name": "Corpus database reconciliation",
        "path": ".github/workflows/corpus-database.yml",
        "event": "workflow_dispatch",
    },
    {
        "name": "Deep functional inventory and public apps",
        "path": ".github/workflows/deep-functional-and-app-gates.yml",
        "event": "workflow_dispatch",
    },
)


class PolicyError(RuntimeError):
    """A fail-closed policy violation."""


class TransientPolicyError(PolicyError):
    """GitHub has not exposed an expected immutable object yet."""


@dataclass(frozen=True, order=True)
class Change:
    status: str
    path: str
    previous_path: str | None = None


@dataclass(frozen=True)
class Classification:
    mode: str
    targeted_tests: tuple[str, ...]
    changes_digest: str
    reason: str


def _load_json(path: str | Path) -> Any:
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def _write_json(path: str | Path, payload: Any) -> None:
    Path(path).write_text(
        json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _validate_sha(value: str, label: str) -> str:
    if len(value) != 40 or any(character not in "0123456789abcdef" for character in value):
        raise PolicyError(f"{label} is not a full lowercase commit SHA: {value!r}")
    return value


def _validate_sha256(value: str, label: str) -> str:
    if len(value) != 64 or any(
        character not in "0123456789abcdef" for character in value
    ):
        raise PolicyError(f"{label} is not a lowercase SHA-256 digest: {value!r}")
    return value


def _file_sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                hasher.update(chunk)
    except OSError as error:
        raise PolicyError(f"release artifact is unavailable: {path}") from error
    return hasher.hexdigest()


def _verify_sidecar(path: Path, expected_digest: str, label: str) -> None:
    try:
        fields = path.read_text(encoding="utf-8").strip().split()
    except OSError as error:
        raise PolicyError(f"{label} sidecar is unavailable: {path}") from error
    if not fields or fields[0].lower() != expected_digest:
        raise PolicyError(f"{label} sidecar digest mismatch")


def _read_magic(path: Path, size: int, label: str) -> bytes:
    try:
        with path.open("rb") as handle:
            return handle.read(size)
    except OSError as error:
        raise PolicyError(f"{label} is unavailable: {path}") from error


def verify_release_receipt(
    *,
    receipt_path: str | Path,
    apk_path: str | Path,
    apk_sidecar_path: str | Path,
    expected_sha: str,
    expected_cert: str,
    windows_path: str | Path | None = None,
    windows_sidecar_path: str | Path | None = None,
) -> str:
    """Verify mutable files against the SHA-specific completion receipt.

    The receipt is the server-side record committed only after a successful
    release. Replacing an APK and its sidecar together cannot change the digest
    pinned in that receipt.
    """

    expected_sha = _validate_sha(expected_sha, "release receipt SHA")
    expected_cert = _validate_sha256(expected_cert, "release certificate")
    try:
        receipt = _load_json(receipt_path)
    except (OSError, json.JSONDecodeError) as error:
        raise PolicyError(
            f"release receipt is unavailable or invalid: {receipt_path}"
        ) from error
    if not isinstance(receipt, dict):
        raise PolicyError("release receipt is not a JSON object")

    apk = Path(apk_path)
    required = {
        "schema": 1,
        "sha": expected_sha,
        "android_cert_sha256": expected_cert,
        "android_name": apk.name,
    }
    for key, expected in required.items():
        if receipt.get(key) != expected:
            raise PolicyError(f"release receipt mismatch: {key}")

    if _read_magic(apk, 4, "published APK") != b"PK\x03\x04":
        raise PolicyError("published APK signature is invalid")
    android_sha = _file_sha256(apk)
    receipt_android_sha = receipt.get("android_sha256")
    if not isinstance(receipt_android_sha, str):
        raise PolicyError("release receipt APK digest is missing")
    _validate_sha256(receipt_android_sha, "release receipt APK digest")
    if receipt_android_sha != android_sha:
        raise PolicyError("release receipt APK digest mismatch")
    _verify_sidecar(Path(apk_sidecar_path), android_sha, "published APK")

    receipt_windows_sha = receipt.get("windows_sha256")
    if receipt_windows_sha is not None:
        if not isinstance(receipt_windows_sha, str):
            raise PolicyError("release receipt Windows digest is invalid")
        _validate_sha256(receipt_windows_sha, "release receipt Windows digest")
        if windows_path is None or windows_sidecar_path is None:
            raise PolicyError("release receipt requires Windows artifact verification")
        windows = Path(windows_path)
        if _read_magic(windows, 2, "published Windows artifact") != b"MZ":
            raise PolicyError("published Windows signature is invalid")
        if _file_sha256(windows) != receipt_windows_sha:
            raise PolicyError("release receipt Windows digest mismatch")
        _verify_sidecar(
            Path(windows_sidecar_path), receipt_windows_sha, "published Windows"
        )

    return android_sha


def _canonical_changes(changes: Iterable[Change]) -> list[Change]:
    return sorted(set(changes))


def changes_digest(changes: Iterable[Change]) -> str:
    payload = [asdict(change) for change in _canonical_changes(changes)]
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def parse_git_changes(raw: bytes) -> list[Change]:
    tokens = raw.split(b"\0")
    if tokens and not tokens[-1]:
        tokens.pop()
    changes: list[Change] = []
    index = 0
    status_names = {
        "A": "added",
        "M": "modified",
        "D": "removed",
        "T": "modified",
        "U": "modified",
        "X": "modified",
        "B": "modified",
    }
    while index < len(tokens):
        status_token = tokens[index].decode("ascii")
        index += 1
        code = status_token[0]
        if code in {"R", "C"}:
            if index + 1 >= len(tokens):
                raise PolicyError(f"Malformed git rename/copy record: {status_token}")
            previous = tokens[index].decode("utf-8", "surrogateescape")
            path = tokens[index + 1].decode("utf-8", "surrogateescape")
            index += 2
            changes.append(Change("renamed" if code == "R" else "copied", path, previous))
            continue
        if index >= len(tokens):
            raise PolicyError(f"Malformed git change record: {status_token}")
        path = tokens[index].decode("utf-8", "surrogateescape")
        index += 1
        changes.append(Change(status_names.get(code, "modified"), path))
    return _canonical_changes(changes)


def parse_github_changes(records: Sequence[dict[str, Any]]) -> list[Change]:
    status_names = {
        "added": "added",
        "modified": "modified",
        "changed": "modified",
        "removed": "removed",
        "renamed": "renamed",
        "copied": "copied",
    }
    changes = []
    for record in records:
        status = status_names.get(str(record.get("status")))
        path = record.get("filename")
        if status is None or not isinstance(path, str) or not path:
            raise PolicyError(f"Unsupported GitHub changed-file record: {record!r}")
        previous = record.get("previous_filename") if status in {"renamed", "copied"} else None
        if previous is not None and not isinstance(previous, str):
            raise PolicyError(f"Invalid previous filename for {path!r}")
        changes.append(Change(status, path, previous))
    return _canonical_changes(changes)


def _is_benign_path(path: str) -> bool:
    if path.startswith(("frontend/", "docs/")):
        return True
    return path in {
        "README.md",
        "CONTRIBUTING.md",
        "SECURITY.md",
        "CHANGELOG.md",
        "LICENSE",
        "LICENSE.md",
    }


def _is_isolated_test_module(path: str) -> bool:
    candidate = Path(path)
    return (
        path.startswith("backend/tests/")
        and candidate.name.startswith("test_")
        and candidate.suffix == ".py"
        and candidate.name != "conftest.py"
    )


def discover_frontend_contract_tests(repository_root: Path) -> tuple[str, ...]:
    """Find every backend test module with a lexical frontend dependency.

    Every test module is parsed before the selection is accepted. An unreadable
    or syntactically invalid corpus, or a corpus with no frontend contracts,
    makes coverage unprovable and therefore forces the full backend suite.
    """

    tests_root = (repository_root / "backend" / "tests").resolve()
    if not tests_root.is_dir():
        raise PolicyError(f"backend test root is unavailable: {tests_root}")
    contracts = []
    candidates = sorted(tests_root.rglob("test_*.py"))
    if not candidates:
        raise PolicyError("backend test corpus has no discoverable test modules")
    for path in candidates:
        resolved = path.resolve()
        if not resolved.is_file() or not resolved.is_relative_to(tests_root):
            raise PolicyError(f"unsafe backend test module: {path}")
        try:
            source = resolved.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(resolved))
        except (OSError, UnicodeError, SyntaxError) as error:
            raise PolicyError(f"cannot prove frontend contract coverage: {path}: {error}") from error
        frontend_literals = {
            node.value.replace("\\", "/")
            for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
        }
        if any(value == "frontend" or value.startswith("frontend/") for value in frontend_literals):
            contracts.append(resolved.relative_to(repository_root.resolve()).as_posix())
    if not contracts:
        raise PolicyError("no backend frontend-contract tests were discovered")
    discovered = tuple(sorted(contracts))
    if discovered != FRONTEND_CONTRACT_TESTS:
        missing = sorted(set(FRONTEND_CONTRACT_TESTS) - set(discovered))
        unreviewed = sorted(set(discovered) - set(FRONTEND_CONTRACT_TESTS))
        raise PolicyError(
            "frontend contract manifest drifted; "
            f"missing={missing!r} unreviewed={unreviewed!r}"
        )
    return discovered


def classify_changes(
    changes: Sequence[Change], *, repository_root: Path | None = None
) -> Classification:
    canonical = _canonical_changes(changes)
    digest = changes_digest(canonical)
    if not canonical:
        return Classification("full", (), digest, "empty or unavailable diff")

    targeted: set[str] = set()
    frontend_changed = False
    for change in canonical:
        involved_paths = tuple(
            path for path in (change.previous_path, change.path) if path is not None
        )
        if change.status in {"renamed", "copied"}:
            if all(_is_benign_path(path) for path in involved_paths):
                frontend_changed = frontend_changed or any(
                    path.startswith("frontend/") for path in involved_paths
                )
                continue
            return Classification(
                "full",
                (),
                digest,
                f"{change.status} path may have broad impact: {involved_paths!r}",
            )
        if change.status == "removed":
            if _is_benign_path(change.path):
                frontend_changed = frontend_changed or change.path.startswith("frontend/")
                continue
            return Classification(
                "full", (), digest, f"deleted non-benign path: {change.path}"
            )
        if _is_benign_path(change.path):
            frontend_changed = frontend_changed or change.path.startswith("frontend/")
            continue
        if _is_isolated_test_module(change.path):
            targeted.add(change.path)
            continue
        return Classification(
            "full", (), digest, f"non-allowlisted or broad-impact path: {change.path}"
        )

    if frontend_changed:
        try:
            targeted.update(
                discover_frontend_contract_tests(repository_root or Path.cwd().resolve())
            )
        except PolicyError as error:
            return Classification(
                "full",
                (),
                digest,
                f"frontend contract coverage is not provable: {error}",
            )
    if targeted:
        return Classification(
            "targeted",
            tuple(sorted(targeted)),
            digest,
            "isolated backend tests and all discovered frontend contracts cover the change",
        )
    return Classification(
        "skip",
        (),
        digest,
        "only frontend or documentation allowlist paths changed",
    )


def git_classification(base_sha: str, head_sha: str) -> tuple[Classification, str]:
    base_sha = _validate_sha(base_sha, "base SHA")
    head_sha = _validate_sha(head_sha, "head SHA")
    checked_out = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    if checked_out != head_sha:
        raise PolicyError(f"checked-out HEAD {checked_out} differs from PR head {head_sha}")
    for sha in (base_sha, head_sha):
        subprocess.run(["git", "cat-file", "-e", f"{sha}^{{commit}}"], check=True)
    raw = subprocess.check_output(
        ["git", "diff", "--find-renames", "--name-status", "-z", base_sha, head_sha]
    )
    tested_tree = subprocess.check_output(
        ["git", "rev-parse", f"{head_sha}^{{tree}}"], text=True
    ).strip()
    return classify_changes(parse_git_changes(raw)), _validate_sha(tested_tree, "tested tree")


def write_github_outputs(path: str | Path, values: dict[str, str]) -> None:
    with Path(path).open("a", encoding="utf-8") as handle:
        for key, value in values.items():
            if "\n" in value or "\r" in value:
                raise PolicyError(f"multiline GitHub output is not permitted: {key}")
            handle.write(f"{key}={value}\n")


def build_attestation(args: argparse.Namespace) -> dict[str, Any]:
    mode = args.backend_mode
    tests = json.loads(args.targeted_tests)
    if mode not in {"full", "targeted", "skip"}:
        raise PolicyError(f"invalid backend mode: {mode}")
    if not isinstance(tests, list) or any(not isinstance(item, str) for item in tests):
        raise PolicyError("targeted tests must be a JSON string list")
    expected_result = "skipped" if mode == "skip" else "success"
    if args.backend_result != expected_result:
        raise PolicyError(
            f"backend result {args.backend_result!r} is invalid for mode {mode!r}"
        )
    if args.frontend_result != "success":
        raise PolicyError(f"frontend result is not successful: {args.frontend_result}")
    if mode != "targeted" and tests:
        raise PolicyError(f"mode {mode} cannot attest targeted tests")
    return {
        "schema": ATTESTATION_SCHEMA,
        "repository": args.repository,
        "pr_number": int(args.pr_number),
        "base_sha": _validate_sha(args.base_sha, "base SHA"),
        "head_sha": _validate_sha(args.head_sha, "head SHA"),
        "tested_tree": _validate_sha(args.tested_tree, "tested tree"),
        "backend_mode": mode,
        "targeted_tests": sorted(tests),
        "changes_digest": args.changes_digest,
        "backend_result": args.backend_result,
        "frontend_result": args.frontend_result,
        "run_id": int(args.run_id),
        "run_attempt": int(args.run_attempt),
    }


def _parse_time(value: str | None, label: str) -> datetime:
    if not value:
        raise PolicyError(f"missing GitHub timestamp: {label}")
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _select_pull(pulls: Sequence[dict[str, Any]], merge_sha: str) -> dict[str, Any]:
    matches = [
        pull
        for pull in pulls
        if pull.get("merged_at")
        and pull.get("merge_commit_sha") == merge_sha
        and pull.get("base", {}).get("ref") == "main"
    ]
    if len(matches) != 1:
        raise PolicyError(f"expected one merged PR for {merge_sha}, found {len(matches)}")
    return matches[0]


def select_reusable_ci_run(
    *,
    merge: dict[str, Any],
    pulls: Sequence[dict[str, Any]],
    head: dict[str, Any],
    runs: Sequence[dict[str, Any]],
    workflow: dict[str, Any],
    repository: str,
    merge_sha: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    pull = _select_pull(pulls, merge_sha)
    base = pull.get("base", {})
    pull_head = pull.get("head", {})
    base_sha = _validate_sha(str(base.get("sha", "")), "PR base SHA")
    head_sha = _validate_sha(str(pull_head.get("sha", "")), "PR head SHA")
    if base.get("repo", {}).get("full_name") != repository:
        raise PolicyError(f"PR #{pull['number']} does not target {repository}")
    parents = [parent.get("sha") for parent in merge.get("parents", [])]
    if parents != [base_sha, head_sha]:
        raise PolicyError(
            f"PR #{pull['number']} requires exact two-parent merge {[base_sha, head_sha]}; "
            f"found {parents}"
        )
    merge_tree = merge.get("commit", {}).get("tree", {}).get("sha")
    head_tree = head.get("commit", {}).get("tree", {}).get("sha")
    if merge_tree != head_tree:
        raise PolicyError(
            f"PR #{pull['number']} merge tree {merge_tree} differs from head tree {head_tree}"
        )
    expected_path = CI_WORKFLOW["path"]
    if (
        workflow.get("name") != CI_WORKFLOW["name"]
        or workflow.get("path") != expected_path
        or workflow.get("state") != "active"
        or not isinstance(workflow.get("id"), int)
    ):
        raise PolicyError(f"CI workflow identity mismatch: {workflow!r}")

    candidates = [
        run
        for run in runs
        if run.get("name") == CI_WORKFLOW["name"]
        and run.get("path") == expected_path
        and run.get("workflow_id") == workflow["id"]
        and run.get("event") == CI_WORKFLOW["event"]
        and run.get("head_sha") == head_sha
        and run.get("head_branch") == pull_head.get("ref")
        and run.get("head_repository", {}).get("id") == pull_head.get("repo", {}).get("id")
    ]
    if not candidates:
        raise TransientPolicyError(f"PR #{pull['number']} exact-head CI run is not indexed yet")
    latest = max(candidates, key=lambda run: (run.get("created_at", ""), run.get("id", 0)))
    if latest.get("status") != "completed" or latest.get("conclusion") != "success":
        raise PolicyError(
            f"PR #{pull['number']} was merged without a completed successful CI: "
            f"status={latest.get('status')} conclusion={latest.get('conclusion')}"
        )
    if _parse_time(latest.get("completed_at"), "CI completed_at") > _parse_time(
        pull.get("merged_at"), "PR merged_at"
    ):
        raise PolicyError(
            f"PR #{pull['number']} CI completed after merge; branch protection did not hold"
        )
    return pull, latest


def verify_attestation(
    *,
    attestation: dict[str, Any],
    pull: dict[str, Any],
    head: dict[str, Any],
    run: dict[str, Any],
    jobs: Sequence[dict[str, Any]],
    changes: Sequence[Change],
    repository: str,
) -> Classification:
    classification = classify_changes(changes)
    expected_backend_result = "skipped" if classification.mode == "skip" else "success"
    expected = {
        "schema": ATTESTATION_SCHEMA,
        "repository": repository,
        "pr_number": pull["number"],
        "base_sha": pull["base"]["sha"],
        "head_sha": pull["head"]["sha"],
        "tested_tree": head["commit"]["tree"]["sha"],
        "backend_mode": classification.mode,
        "targeted_tests": list(classification.targeted_tests),
        "changes_digest": classification.changes_digest,
        "backend_result": expected_backend_result,
        "frontend_result": "success",
        "run_id": int(run["id"]),
        "run_attempt": int(run.get("run_attempt", 1)),
    }
    mismatches = {
        key: (attestation.get(key), value)
        for key, value in expected.items()
        if attestation.get(key) != value
    }
    job_results = {job.get("name"): job.get("conclusion") for job in jobs}
    expected_jobs = {
        "Detect backend risk": "success",
        "Backend tests": expected_backend_result,
        "Frontend build": "success",
        "CI policy": "success",
    }
    invalid_jobs = {
        name: (job_results.get(name), result)
        for name, result in expected_jobs.items()
        if job_results.get(name) != result
    }
    if invalid_jobs:
        mismatches["jobs"] = invalid_jobs
    if mismatches:
        raise PolicyError(f"PR CI attestation mismatch: {mismatches}")
    return classification


def _gh(arguments: Sequence[str], *, json_output: bool = True) -> Any:
    command = ["gh", *arguments]
    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    if completed.returncode:
        raise TransientPolicyError(
            f"GitHub CLI failed ({' '.join(command)}): {completed.stderr.strip()}"
        )
    if not json_output:
        return completed.stdout
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise PolicyError(f"GitHub CLI returned invalid JSON for {' '.join(command)}") from error


def _gh_api(repository: str, endpoint: str) -> Any:
    return _gh(
        [
            "api",
            "-H",
            "Accept: application/vnd.github+json",
            "-H",
            "X-GitHub-Api-Version: 2022-11-28",
            f"repos/{repository}/{endpoint}",
        ]
    )


def _workflow_metadata(repository: str, path: str) -> dict[str, Any]:
    filename = quote(Path(path).name, safe="")
    metadata = _gh_api(repository, f"actions/workflows/{filename}")
    if metadata.get("path") != path:
        raise PolicyError(
            f"workflow filename {filename} resolved to {metadata.get('path')!r}, expected {path!r}"
        )
    return metadata


def _paginated(repository: str, endpoint: str, key: str | None = None) -> list[dict[str, Any]]:
    collected: list[dict[str, Any]] = []
    separator = "&" if "?" in endpoint else "?"
    for page in range(1, 31):
        payload = _gh_api(repository, f"{endpoint}{separator}per_page=100&page={page}")
        records = payload[key] if key is not None else payload
        if not isinstance(records, list):
            raise PolicyError(f"paginated GitHub response is not a list: {endpoint}")
        collected.extend(records)
        if len(records) < 100:
            return collected
    raise PolicyError(f"GitHub pagination exceeded the safe 3000-item limit: {endpoint}")


def verify_merged_pr_ci(repository: str, merge_sha: str, attempts: int, delay: float) -> None:
    merge_sha = _validate_sha(merge_sha, "merge SHA")
    merge = _gh_api(repository, f"commits/{merge_sha}")
    pulls = _gh_api(repository, f"commits/{merge_sha}/pulls")
    pull = _select_pull(pulls, merge_sha)
    head_sha = _validate_sha(str(pull.get("head", {}).get("sha", "")), "PR head SHA")
    head = _gh_api(repository, f"commits/{head_sha}")
    workflow = _workflow_metadata(repository, CI_WORKFLOW["path"])

    selected_run: dict[str, Any] | None = None
    last_transient: Exception | None = None
    for attempt in range(1, attempts + 1):
        runs = _paginated(
            repository,
            f"actions/runs?event=pull_request&head_sha={head_sha}",
            "workflow_runs",
        )
        try:
            pull, selected_run = select_reusable_ci_run(
                merge=merge,
                pulls=pulls,
                head=head,
                runs=runs,
                workflow=workflow,
                repository=repository,
                merge_sha=merge_sha,
            )
            break
        except TransientPolicyError as error:
            last_transient = error
            if attempt == attempts:
                raise
            time.sleep(delay)
    if selected_run is None:
        raise PolicyError(f"CI lookup exhausted without a run: {last_transient}")

    run_id = int(selected_run["id"])
    jobs_payload = _gh_api(repository, f"actions/runs/{run_id}/jobs?filter=latest&per_page=100")
    jobs = jobs_payload.get("jobs", [])
    changed_records = _paginated(repository, f"pulls/{pull['number']}/files")
    changes = parse_github_changes(changed_records)

    with tempfile.TemporaryDirectory(prefix="corvia-ci-attestation-") as directory:
        artifact = Path(directory) / "ci-pr-attestation.json"
        for attempt in range(1, attempts + 1):
            shutil.rmtree(directory, ignore_errors=True)
            Path(directory).mkdir(parents=True)
            try:
                _gh(
                    [
                        "run",
                        "download",
                        str(run_id),
                        "--repo",
                        repository,
                        "--name",
                        "ci-pr-attestation",
                        "--dir",
                        directory,
                    ],
                    json_output=False,
                )
            except TransientPolicyError:
                if attempt == attempts:
                    raise
                time.sleep(delay)
                continue
            if artifact.is_file():
                break
            if attempt == attempts:
                raise TransientPolicyError(f"CI run {run_id} attestation artifact is unavailable")
            time.sleep(delay)
        classification = verify_attestation(
            attestation=_load_json(artifact),
            pull=pull,
            head=head,
            run=selected_run,
            jobs=jobs,
            changes=changes,
            repository=repository,
        )
    print(
        f"PR #{pull['number']} CI run {run_id} completed before merge; "
        f"tree and {classification.mode} backend policy attest {merge_sha}."
    )


def _select_gate_run(
    runs: Sequence[dict[str, Any]],
    spec: dict[str, str],
    workflow: dict[str, Any],
    sha: str,
) -> dict[str, Any]:
    if (
        workflow.get("name") != spec["name"]
        or workflow.get("path") != spec["path"]
        or workflow.get("state") != "active"
        or not isinstance(workflow.get("id"), int)
    ):
        raise PolicyError(f"release workflow identity mismatch for {spec['path']}: {workflow!r}")
    candidates = [
        run
        for run in runs
        if run.get("name") == spec["name"]
        and run.get("path") == spec["path"]
        and run.get("workflow_id") == workflow["id"]
        and run.get("event") == spec["event"]
        and run.get("head_sha") == sha
        and run.get("head_branch") == "main"
    ]
    if not candidates:
        raise PolicyError(f"{spec['name']}: exact workflow path/ID run is missing for {sha}")
    latest = max(candidates, key=lambda run: (run.get("created_at", ""), run.get("id", 0)))
    if latest.get("status") != "completed" or latest.get("conclusion") != "success":
        raise PolicyError(
            f"{spec['name']}: status={latest.get('status')} conclusion={latest.get('conclusion')}"
        )
    return latest


def verify_release_gates(repository: str, sha: str) -> None:
    sha = _validate_sha(sha, "release SHA")
    current_main = _gh_api(repository, "git/ref/heads/main").get("object", {}).get("sha")
    if current_main != sha:
        raise PolicyError(f"release {sha} is obsolete; current main is {current_main}")
    runs = _paginated(
        repository,
        f"actions/runs?branch=main&head_sha={sha}",
        "workflow_runs",
    )
    certified = []
    for spec in RELEASE_GATES:
        workflow = _workflow_metadata(repository, spec["path"])
        run = _select_gate_run(runs, spec, workflow, sha)
        certified.append(f"{spec['path']}#{run['id']}")
    print(f"Exact release gates certified for {sha}: {', '.join(certified)}")


def find_successful_deploy_claim(
    *,
    runs: Sequence[dict[str, Any]],
    jobs_by_run: dict[int, Sequence[dict[str, Any]]],
    workflow: dict[str, Any],
    sha: str,
    current_run_id: int,
    current_run_attempt: int,
) -> tuple[int, int] | None:
    if (
        workflow.get("name") != DEPLOY_WORKFLOW["name"]
        or workflow.get("path") != DEPLOY_WORKFLOW["path"]
        or workflow.get("state") != "active"
        or not isinstance(workflow.get("id"), int)
    ):
        raise PolicyError(f"deploy workflow identity mismatch: {workflow!r}")
    candidates = [
        run
        for run in runs
        if run.get("name") == DEPLOY_WORKFLOW["name"]
        and run.get("path") == DEPLOY_WORKFLOW["path"]
        and run.get("workflow_id") == workflow["id"]
        and run.get("event") in {"workflow_run", "workflow_dispatch"}
        and run.get("head_sha") == sha
        and run.get("head_branch") == "main"
    ]
    for run in sorted(candidates, key=lambda item: int(item.get("id", 0)), reverse=True):
        run_id = int(run["id"])
        for job in jobs_by_run.get(run_id, ()):
            if job.get("name") != DEPLOY_JOB_NAME or job.get("conclusion") != "success":
                continue
            attempt = int(job.get("run_attempt", 1))
            if run_id == current_run_id and attempt >= current_run_attempt:
                continue
            return run_id, attempt
    return None


def check_deploy_claim(
    repository: str,
    sha: str,
    current_run_id: int,
    current_run_attempt: int,
    github_output: str,
) -> None:
    sha = _validate_sha(sha, "deploy claim SHA")
    current_main = _gh_api(repository, "git/ref/heads/main").get("object", {}).get("sha")
    if current_main != sha:
        raise PolicyError(f"deploy claim candidate {sha} is obsolete; current main is {current_main}")
    workflow = _workflow_metadata(repository, DEPLOY_WORKFLOW["path"])
    runs = _paginated(
        repository,
        f"actions/runs?branch=main&head_sha={sha}",
        "workflow_runs",
    )
    jobs_by_run: dict[int, Sequence[dict[str, Any]]] = {}
    for run in runs:
        if (
            run.get("path") == DEPLOY_WORKFLOW["path"]
            and run.get("workflow_id") == workflow.get("id")
            and run.get("head_sha") == sha
        ):
            run_id = int(run["id"])
            jobs_by_run[run_id] = _paginated(
                repository,
                f"actions/runs/{run_id}/jobs?filter=all",
                "jobs",
            )
    claim = find_successful_deploy_claim(
        runs=runs,
        jobs_by_run=jobs_by_run,
        workflow=workflow,
        sha=sha,
        current_run_id=current_run_id,
        current_run_attempt=current_run_attempt,
    )
    values = {"claimed": "true" if claim else "false"}
    if claim:
        values.update({"claim_run_id": str(claim[0]), "claim_run_attempt": str(claim[1])})
        print(
            f"Deploy claim already satisfied for {sha} by run {claim[0]} attempt {claim[1]}."
        )
    else:
        print(f"No successful deploy claim exists for {sha}; this serialized run may proceed.")
    write_github_outputs(github_output, values)


def run_targeted_tests(tests_json: str, report: str) -> None:
    repository_root = Path.cwd().parent.resolve()
    tests_root = (repository_root / "backend" / "tests").resolve()
    tests = json.loads(tests_json)
    if not isinstance(tests, list) or not tests:
        raise PolicyError("targeted mode requires at least one isolated test module")
    resolved = []
    for relative in tests:
        if not isinstance(relative, str) or not _is_isolated_test_module(relative):
            raise PolicyError(f"invalid targeted backend test: {relative!r}")
        path = (repository_root / relative).resolve()
        if not path.is_relative_to(tests_root) or not path.is_file():
            raise PolicyError(f"targeted backend test is unavailable: {relative}")
        resolved.append(str(path.relative_to(Path.cwd())))
    completed = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "--tb=short", *resolved],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    Path(report).write_text(completed.stdout, encoding="utf-8")
    print(completed.stdout, end="")
    raise SystemExit(completed.returncode)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    classify = subparsers.add_parser("classify-git")
    classify.add_argument("--base", required=True)
    classify.add_argument("--head", required=True)
    classify.add_argument("--github-output", required=True)
    classify.add_argument("--github-summary", required=True)

    attest = subparsers.add_parser("write-attestation")
    for argument in (
        "repository",
        "pr-number",
        "base-sha",
        "head-sha",
        "tested-tree",
        "backend-mode",
        "targeted-tests",
        "changes-digest",
        "backend-result",
        "frontend-result",
        "run-id",
        "run-attempt",
        "output",
    ):
        attest.add_argument(f"--{argument}", required=True)

    targeted = subparsers.add_parser("run-targeted-tests")
    targeted.add_argument("--tests-json", required=True)
    targeted.add_argument("--report", required=True)

    reuse = subparsers.add_parser("verify-merged-pr-ci")
    reuse.add_argument("--repository", required=True)
    reuse.add_argument("--merge-sha", required=True)
    reuse.add_argument("--attempts", type=int, default=5)
    reuse.add_argument("--delay", type=float, default=4.0)

    gates = subparsers.add_parser("verify-release-gates")
    gates.add_argument("--repository", required=True)
    gates.add_argument("--sha", required=True)

    claim = subparsers.add_parser("check-deploy-claim")
    claim.add_argument("--repository", required=True)
    claim.add_argument("--sha", required=True)
    claim.add_argument("--current-run-id", type=int, required=True)
    claim.add_argument("--current-run-attempt", type=int, required=True)
    claim.add_argument("--github-output", required=True)

    receipt = subparsers.add_parser("verify-release-receipt")
    receipt.add_argument("--receipt", required=True)
    receipt.add_argument("--apk", required=True)
    receipt.add_argument("--apk-sidecar", required=True)
    receipt.add_argument("--expected-sha", required=True)
    receipt.add_argument("--expected-cert", required=True)
    receipt.add_argument("--windows")
    receipt.add_argument("--windows-sidecar")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "classify-git":
            classification, tested_tree = git_classification(args.base, args.head)
            write_github_outputs(
                args.github_output,
                {
                    "backend_mode": classification.mode,
                    "targeted_tests": json.dumps(list(classification.targeted_tests)),
                    "changes_digest": classification.changes_digest,
                    "tested_tree": tested_tree,
                },
            )
            Path(args.github_summary).write_text(
                f"Backend mode: {classification.mode}. {classification.reason}.\n",
                encoding="utf-8",
            )
        elif args.command == "write-attestation":
            _write_json(args.output, build_attestation(args))
        elif args.command == "run-targeted-tests":
            run_targeted_tests(args.tests_json, args.report)
        elif args.command == "verify-merged-pr-ci":
            if not 1 <= args.attempts <= 10 or not 0 <= args.delay <= 30:
                raise PolicyError("retry bounds are invalid")
            verify_merged_pr_ci(args.repository, args.merge_sha, args.attempts, args.delay)
        elif args.command == "verify-release-gates":
            verify_release_gates(args.repository, args.sha)
        elif args.command == "check-deploy-claim":
            check_deploy_claim(
                args.repository,
                args.sha,
                args.current_run_id,
                args.current_run_attempt,
                args.github_output,
            )
        elif args.command == "verify-release-receipt":
            print(
                verify_release_receipt(
                    receipt_path=args.receipt,
                    apk_path=args.apk,
                    apk_sidecar_path=args.apk_sidecar,
                    expected_sha=args.expected_sha,
                    expected_cert=args.expected_cert,
                    windows_path=args.windows,
                    windows_sidecar_path=args.windows_sidecar,
                )
            )
        else:
            raise PolicyError(f"unsupported command: {args.command}")
    except (PolicyError, subprocess.CalledProcessError, json.JSONDecodeError) as error:
        print(f"CI/release policy blocked: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
