#!/usr/bin/env python3
"""Apply the user's bounded PR918 follow-up authorization, never a full certificate."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess

from ci_backend_policy import classify_paths, classify_authorized_no_backend_ci, PolicyDecision, _write_github_outputs


def github(path: str, *, raw: bool = False):
    result = subprocess.run(["gh", "api", path], check=True, capture_output=True, text=True)
    return result.stdout if raw else json.loads(result.stdout)


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


def authorized_context(manifest: dict, *, event: str, number: str, candidate: str, pr: dict,
                       candidate_tree: str, pr_tree: str, associated: list[dict]) -> bool:
    """Only this PR's exact current head or its associated main integration tree."""
    if pr.get("number") != manifest["pull_request"] or pr.get("base", {}).get("ref") != "main":
        return False
    if event == "pull_request":
        return number == str(manifest["pull_request"]) and candidate == pr.get("head", {}).get("sha")
    if event == "push":
        return (bool(pr.get("merged")) and pr.get("merge_commit_sha") == candidate
                and candidate_tree == pr_tree
                and any(item.get("number") == manifest["pull_request"] for item in associated))
    return False



def changed_followup_paths(baseline: str, pr_head: str, candidate: str) -> list[str]:
    # The approved PR head must descend from the tested baseline. A squash
    # integration may have a different ancestry, already bound to that exact
    # PR tree and merge SHA by authorized_context.
    subprocess.run(["git", "merge-base", "--is-ancestor", baseline, pr_head], check=True, capture_output=True)
    return git("diff", "--no-renames", "--name-only", "--diff-filter=ACDMRTUXB", f"{baseline}..{candidate}").splitlines()

SECTION_BRANCH = "codex/fix-tct-section-visibility-20260910"
SECTION_BASE = "02ad2d6a38301667a82eb60444b531d1e1fcd4e1"
SECTION_DECISION = "tct-section-visibility-20260910"
SECTION_MANIFEST = "docs/ci/tct-section-visibility-no-backend-ci.json"
SECTION_REPOSITORY = "rafaelpaesmeirelles/MeuCardio"


EDITORIAL_BRANCH = "codex/fix-editorial-classifications-20260910"
EDITORIAL_BASE = "4c58de6fb7cd64bd8767f062d9ef0ee814870cda"
EDITORIAL_DECISION = "editorial-classifications-20260910"
EDITORIAL_MANIFEST = "docs/ci/editorial-classifications-no-backend-ci.json"
EDITORIAL_REPOSITORY = "rafaelpaesmeirelles/MeuCardio"

FEATURE_BRANCH = "codex/fix-feature-discovery-20260910"
FEATURE_BASE = "db0a3ff71a184e2d6711168427e7565d6e0c9e48"
FEATURE_DECISION = "feature-discovery-20260910"
FEATURE_MANIFEST = "docs/ci/feature-discovery-no-backend-ci.json"
FEATURE_REPOSITORY = "rafaelpaesmeirelles/MeuCardio"

FEATURE_SCOPE = {
    "manifest": FEATURE_MANIFEST, "head_branch": FEATURE_BRANCH,
    "repository": FEATURE_REPOSITORY, "decision_id": FEATURE_DECISION,
    "base_sha": FEATURE_BASE, "minimum_pull_request": 921,
    "local_evidence": "docs/feature-discovery-audit-20260910.md",
    "decision_document": "docs/ci/feature-discovery-owner-decision.md",
    "suite_key": "backend-risk-v1-authorized-no-backend-ci-feature-discovery-20260910",
}


SECTION_SCOPE = {
    "manifest": SECTION_MANIFEST, "head_branch": SECTION_BRANCH,
    "repository": SECTION_REPOSITORY, "decision_id": SECTION_DECISION,
    "base_sha": SECTION_BASE, "minimum_pull_request": 919,
    "local_evidence": "docs/tct-section-visibility-20260910.md",
    "decision_document": "docs/ci/tct-section-visibility-owner-decision.md",
    "suite_key": "backend-risk-v1-authorized-no-backend-ci-tct-section-visibility-20260910",
}
EDITORIAL_SCOPE = {
    "manifest": EDITORIAL_MANIFEST, "head_branch": EDITORIAL_BRANCH,
    "repository": EDITORIAL_REPOSITORY, "decision_id": EDITORIAL_DECISION,
    "base_sha": EDITORIAL_BASE, "minimum_pull_request": 920,
    "local_evidence": "docs/editorial-classification-audit-20260910.md",
    "decision_document": "docs/ci/editorial-classifications-owner-decision.md",
    "suite_key": "backend-risk-v1-authorized-no-backend-ci-editorial-classifications-20260910",
}


def section_visibility_owner_decision(root: Path, **context):
    return scoped_owner_decision(root, scope=SECTION_SCOPE, **context)


def editorial_classification_owner_decision(root: Path, **context):
    return scoped_owner_decision(root, scope=EDITORIAL_SCOPE, **context)


def feature_discovery_owner_decision(root: Path, **context):
    return scoped_owner_decision(root, scope=FEATURE_SCOPE, **context)


def scoped_owner_decision(root: Path, *, event: str, number: str,
                          head_ref: str, repository: str, scope: dict):
    """Verify one explicitly registered correction; no other PR grants authority."""
    path = root / scope["manifest"]
    if not path.is_file():
        if event == "pull_request" and head_ref == scope["head_branch"]:
            raise ValueError("Scoped owner decision missing; refusing backend CI")
        return None
    manifest = json.loads(path.read_text())
    approved_number = manifest.get("pull_request")
    relevant_pr = event == "pull_request" and (
        head_ref == scope["head_branch"] or (approved_number is not None and number == str(approved_number)))
    if not relevant_pr and event != "push":
        return None
    if (repository != scope["repository"] or manifest.get("repository") != scope["repository"]
            or manifest.get("decision_id") != scope["decision_id"]
            or manifest.get("head_branch") != scope["head_branch"]
            or manifest.get("base_sha") != scope["base_sha"]
            or manifest.get("authorization", {}).get("instruction") != "Sem novo ci backend"
            or manifest.get("authorization", {}).get("mode") != "authorized-no-backend-ci"):
        raise ValueError("Scoped owner decision identity is invalid; refusing backend CI")
    # The initial draft supplies the number. Before sealing it, no suite and no
    # successful waiver are allowed, even if someone prematurely merges it.
    if approved_number is None:
        raise ValueError("Scoped owner-decision bootstrap awaits a sealed PR number; refusing backend CI")
    if not isinstance(approved_number, int) or isinstance(approved_number, bool) or approved_number < scope["minimum_pull_request"]:
        raise ValueError("Scoped owner-decision PR number is invalid; refusing backend CI")
    candidate = git("rev-parse", "HEAD")
    pr = github(f"repos/{repository}/pulls/{approved_number}")
    pr_head = pr.get("head", {}).get("sha", "")
    if len(pr_head) != 40 or any(c not in "0123456789abcdef" for c in pr_head):
        raise ValueError("Scoped owner-decision PR head is invalid; refusing backend CI")
    subprocess.run(["git", "fetch", "--no-tags", "origin", pr_head], check=True, capture_output=True)
    candidate_tree = git("rev-parse", "HEAD^{tree}")
    pr_tree = git("rev-parse", f"{pr_head}^{{tree}}")
    associated = github(f"repos/{repository}/commits/{candidate}/pulls") if event == "push" else []
    if not isinstance(associated, list):
        raise ValueError("Scoped owner-decision integration association is invalid")
    possible_integration = (any(item.get("number") == approved_number for item in associated)
        or (bool(pr.get("merged")) and
            (candidate == pr.get("merge_commit_sha") or candidate_tree == pr_tree)))
    if event == "push" and not possible_integration:
        return None
    identity = (pr.get("number") == approved_number
        and pr.get("base", {}).get("ref") == "main"
        and pr.get("base", {}).get("repo", {}).get("full_name") == repository
        and pr.get("head", {}).get("ref") == scope["head_branch"]
        and pr.get("head", {}).get("repo", {}).get("full_name") == repository)
    applicable = identity and authorized_context({"pull_request": approved_number}, event=event,
        number=number, candidate=candidate, pr=pr, candidate_tree=candidate_tree,
        pr_tree=pr_tree, associated=associated)
    if not applicable or (event == "pull_request" and head_ref != scope["head_branch"]):
        raise ValueError("Scoped owner-decision PR/integration evidence incomplete; refusing backend CI")
    paths = changed_followup_paths(scope["base_sha"], pr_head, candidate)
    evidence = manifest.get("local_evidence", [])
    if evidence != [scope["local_evidence"]]:
        raise ValueError("Scoped owner-decision evidence references are invalid")
    for evidence_path in [*evidence, scope["decision_document"]]:
        if not (root / evidence_path).is_file():
            raise ValueError("Scoped owner-decision local evidence is missing")
    summary = {"decision_id": scope["decision_id"], "authorization": manifest["authorization"],
        "pull_request": approved_number, "base_sha": scope["base_sha"],
        "candidate_sha": candidate, "candidate_tree": candidate_tree,
        "local_evidence": evidence, "changed_paths": paths,
        "backend_ci_executed": False, "test_certificate": None,
        "scope": "backend CI não executado por decisão do responsável"}
    Path(os.environ.get("RUNNER_TEMP", "/tmp"), "backend-no-ci-owner-decision.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    return PolicyDecision(backend_mode="authorized-no-backend-ci",
        suite_key=scope["suite_key"],
        focused_tests=(), reasons=("backend CI não executado por decisão do responsável",
            "user-instruction:Sem novo ci backend", "not-a-full-or-focused-test-certificate",
            f"independent-owner-decision:{scope['decision_id']}", f"pull-request:{approved_number}"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paths-file", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--github-output", type=Path)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    os.chdir(root)
    original_paths = args.paths_file.read_text().splitlines()
    decision = None
    event, number = os.environ.get("EVENT_NAME", ""), os.environ.get("PR_NUMBER", "")
    context = dict(event=event, number=number, head_ref=os.environ.get("PR_HEAD_REF", ""),
                   repository=os.environ.get("REPOSITORY", ""))
    decision = feature_discovery_owner_decision(root, **context)
    if decision is None:
        decision = editorial_classification_owner_decision(root, **context)
    if decision is None:
        decision = section_visibility_owner_decision(root, **context)
    if decision is not None:
        if args.github_output:
            _write_github_outputs(args.github_output, decision)
        print(json.dumps(decision.github_outputs(), ensure_ascii=False, indent=2))
        return 0
    if event == "pull_request" and number == "918" and not args.manifest.is_file():
        raise ValueError("PR918 follow-up authorization is missing; refusing a repeated full suite")
    if args.manifest.is_file() and (event == "push" or (event == "pull_request" and number == "918")):
        manifest = json.loads(args.manifest.read_text())
        if (manifest.get("pull_request") != 918 or manifest.get("baseline_run_id") != 34418893616
                or manifest.get("baseline_job_id") != 102689862687
                or manifest.get("baseline_sha") != "eddcb80d3fc99e7c25b330c943637f49691826fa"):
            raise ValueError("Follow-up authorization does not match the approved release")
        repository = os.environ["REPOSITORY"]
        if repository != "rafaelpaesmeirelles/MeuCardio":
            raise ValueError("Follow-up authorization is for a different repository")
        candidate = git("rev-parse", "HEAD")
        pr = github(f"repos/{repository}/pulls/918")
        pr_head = pr.get("head", {}).get("sha", "")
        if len(pr_head) != 40 or any(c not in "0123456789abcdef" for c in pr_head):
            raise ValueError("Invalid PR head")
        subprocess.run(["git", "fetch", "--no-tags", "origin", pr_head], check=True, capture_output=True)
        associated = github(f"repos/{repository}/commits/{candidate}/pulls") if event == "push" else []
        candidate_tree = git("rev-parse", "HEAD^{tree}")
        pr_tree = git("rev-parse", f"{pr_head}^{{tree}}")
        applicable = authorized_context(manifest, event=event, number=number, candidate=candidate,
            pr=pr, candidate_tree=candidate_tree, pr_tree=pr_tree, associated=associated)
        if event == "pull_request" and number == "918" and not applicable:
            raise ValueError("PR918 candidate is stale or outside the exact authorized head; no repeated full suite")
        # GitHub's commit-to-PR association may lag behind the merge metadata.
        # Recognizing a possible integration only blocks fallback; it never grants
        # the exception without every authorized_context identity check above.
        possible_integration = (any(item.get("number") == 918 for item in associated)
            or (bool(pr.get("merged")) and
                (candidate == pr.get("merge_commit_sha") or candidate_tree == pr_tree)))
        if event == "push" and possible_integration and not applicable:
            raise ValueError("PR918 integration evidence is incomplete or its tree differs; refusing a repeated full suite")
        if applicable:
            baseline = manifest.get("functional_baseline_sha")
            if baseline != "266cde7454ec808f37dd4ab0ef6d83415b607c63":
                raise ValueError("The functional origin of this release is not the authorized 266cde74")
            paths = changed_followup_paths(baseline, pr_head, candidate)
            # Metadata only. The owner explicitly revoked further backend CI;
            # no job-log download, pytest invocation or suite certificate here.
            job = github(f"repos/{repository}/actions/jobs/{manifest['baseline_job_id']}")
            decision = classify_authorized_no_backend_ci(paths, repo_root=root, manifest=manifest, baseline_job=job)
            summary = {"authorization": manifest["authorization"], "functional_baseline_sha": baseline,
                       "baseline_run_id": manifest["baseline_run_id"], "baseline_job_id": manifest["baseline_job_id"],
                       "baseline_conclusion": job["conclusion"], "initial_full_result": manifest["initial_full_result"],
                       "failed_followup_classification": manifest["failed_followup_classification"],
                       "candidate_sha": candidate, "candidate_tree": git("rev-parse", "HEAD^{tree}"),
                       "local_evidence": manifest["local_evidence"], "changed_paths": paths,
                       "backend_ci_executed": False, "test_certificate": None,
                       "scope": "backend CI não executado por decisão do responsável"}
            Path(os.environ.get("RUNNER_TEMP", "/tmp"), "backend-no-ci-owner-decision.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2)+"\n")
    if decision is None:
        decision = classify_paths(original_paths, repo_root=root)
    if args.github_output:
        _write_github_outputs(args.github_output, decision)
    print(json.dumps(decision.github_outputs(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
