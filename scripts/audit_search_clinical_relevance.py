#!/usr/bin/env python3
"""Audit the real search function against a clinical gold set, without writes.

Run with backend dependencies and PYTHONPATH=backend against the isolated QA
corpus. Backend imports are deliberately lazy so the evaluator and its tests
need neither SQLAlchemy nor a database. This does not exercise HTTP or auth.
"""
from __future__ import annotations

import argparse
from contextlib import redirect_stdout
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import Callable


DEFAULT_GOLD = Path(__file__).resolve().parent / "fixtures/tudo_com_tudo_search_mitral.json"
CLINICAL_FIELDS = ("clinical_role", "clinical_context", "relation_type", "context_only")


class AuditContractError(ValueError):
    """A response cannot be audited reliably because its contract is broken."""


def identity(item: dict) -> str:
    """Keep slugs from different catalogue fronts distinct."""
    frente, slug = item.get("frente"), item.get("slug")
    if not isinstance(frente, str) or not frente or not isinstance(slug, str) or not slug:
        raise AuditContractError("Every result and gold item needs frente and slug.")
    return f"{frente}:{slug}"


def collect_pages(fetch: Callable[[str, int, int], dict], query: str,
                  page_size: int = 25, max_pages: int = 1000) -> dict:
    """Collect every page, rejecting omissions, duplicates and unstable counts."""
    if not 1 <= page_size <= 100 or max_pages < 1:
        raise AuditContractError("page_size must be 1..100 and max_pages positive.")
    results, pages, seen = [], [], set()
    first = None
    offset = 0
    for _ in range(max_pages):
        page = fetch(query, page_size, offset)
        if not isinstance(page, dict) or not isinstance(page.get("results"), list):
            raise AuditContractError("Search must return an object containing results.")
        rows = page["results"]
        if type(page.get("total")) is not int or page["total"] < 0:
            raise AuditContractError("Search total must be a nonnegative integer.")
        if (page.get("query") != query or page.get("offset") != offset
                or page.get("limit") != page_size or page.get("count") != len(rows)
                or len(rows) > page_size):
            raise AuditContractError("Pagination query, offset, limit or count is inconsistent.")
        if first is None:
            first = page
            for field in ("por_frente", "por_secao"):
                counts = page.get(field)
                if (not isinstance(counts, dict)
                        or any(type(n) is not int or n < 0 for n in counts.values())
                        or sum(counts.values()) != page["total"]):
                    raise AuditContractError(f"{field} does not agree with total.")
        else:
            for field in ("total", "por_frente", "por_secao", "primary_disease", "primary_drug"):
                if page.get(field) != first.get(field):
                    raise AuditContractError(f"Pagination changed {field} between pages.")
        for row in rows:
            key = identity(row)
            if key in seen:
                raise AuditContractError(f"Duplicate paginated result: {key}.")
            seen.add(key)
        next_offset = page.get("next_offset")
        expected_offset = offset + len(rows)
        if expected_offset > page["total"]:
            raise AuditContractError("Collected more results than the reported total.")
        if expected_offset < page["total"]:
            if not rows or type(next_offset) is not int or next_offset != expected_offset:
                raise AuditContractError("Pagination omitted results or did not advance correctly.")
        elif next_offset is not None:
            raise AuditContractError("Pagination must end when the reported total is reached.")
        pages.append({"offset": offset, "count": len(rows), "next_offset": next_offset})
        results.extend(rows)
        if next_offset is None:
            return {
                "query": query, "count": len(results), "total": first["total"],
                "page_size": page_size, "pages": pages,
                "por_frente": first["por_frente"], "por_secao": first["por_secao"],
                "primary_disease": first.get("primary_disease"),
                "primary_drug": first.get("primary_drug"),
                "supplementary_groups": first.get("supplementary_groups", []),
                "results": results,
            }
        offset = next_offset
    raise AuditContractError("Pagination exceeded max_pages before completion.")


def evaluate_response(response: dict, gold: dict) -> dict:
    """Pure clinical contract evaluation; no backend imports or implicit judging."""
    rows = response["results"]
    keys = [identity(row) for row in rows]
    if len(set(keys)) != len(keys):
        raise AuditContractError("Duplicate results cannot be clinically evaluated.")
    positions = {key: i for i, key in enumerate(keys, 1)}
    by_key = dict(zip(keys, rows))
    failures: list[dict] = []

    def fail(code: str, key: str | None = None, **details) -> None:
        failures.append({"code": code, **({"key": key} if key else {}), **details})

    expected_disease = gold.get("disease_slug")
    actual_disease = (response.get("primary_disease") or {}).get("slug")
    if expected_disease and actual_disease != expected_disease:
        fail("primary_disease_mismatch", expected=expected_disease, actual=actual_disease)

    required = []
    for item in gold.get("required", []):
        key = identity(item)
        position = positions.get(key)
        actual_role = by_key.get(key, {}).get("clinical_role")
        required.append({**item, "position": position, "actual_role": actual_role})
        if position is None:
            fail("required_missing", key)
            continue
        if item.get("max_position") is not None and position > item["max_position"]:
            fail("required_position", key, expected_max=item["max_position"], actual=position)
        if item.get("expected_role") and actual_role != item["expected_role"]:
            fail("required_role", key, expected=item["expected_role"], actual=actual_role)

    forbidden_found = []
    for item in gold.get("forbidden", []):
        key = identity(item)
        if key in positions:
            forbidden_found.append({**item, "position": positions[key]})
            fail("forbidden_result", key)

    qualified = []
    for item in gold.get("qualified", []):
        key = identity(item)
        row = by_key.get(key, {})
        context = row.get("clinical_context") or ""
        missing_text = [phrase for phrase in item.get("context_contains", [])
                        if phrase.casefold() not in context.casefold()]
        qualified.append({**item, "position": positions.get(key),
                          "actual_role": row.get("clinical_role"),
                          "actual_context": context, "missing_context_phrases": missing_text})
        if not row:
            fail("qualified_missing", key)
            continue
        if row.get("clinical_role") != item["role"]:
            fail("qualified_role", key, expected=item["role"], actual=row.get("clinical_role"))
        if missing_text:
            fail("qualified_context", key, missing_phrases=missing_text, actual=context)

    controls = []
    for item in gold.get("cross_lesion_controls", []):
        key = identity(item)
        row = by_key.get(key)
        controls.append({**item, "present": row is not None, "position": positions.get(key),
                         "actual_role": row.get("clinical_role") if row else None,
                         "actual_context": row.get("clinical_context") if row else None})
        if row is not None:
            if not row.get("clinical_role") or row["clinical_role"] == item["must_not_be_role"]:
                fail("cross_lesion_role", key, actual=row.get("clinical_role"))
            if not isinstance(row.get("clinical_context"), str) or not row["clinical_context"].strip():
                fail("cross_lesion_context_missing", key)

    contextual_positions = [i for i, row in enumerate(rows, 1)
                            if row.get("clinical_role") in ("comparison", "mention")]
    first_contextual = min(contextual_positions, default=None)
    for item in gold.get("top_priorities", []):
        key = identity(item)
        if key not in positions:
            fail("top_priority_missing", key)
        elif first_contextual is not None and positions[key] >= first_contextual:
            fail("top_priority_after_context", key, position=positions[key],
                 first_comparison_or_mention=first_contextual)

    # These are independent gold judgments, not the runtime clinical profile.
    judgments = {identity(item): item for item in gold.get("baseline", {}).get("top_20_review", [])}
    judgments.update({identity(item): item for item in gold.get("top_20_clinical_review", [])})
    top_twenty = []
    for position, row in enumerate(rows[:20], 1):
        key = identity(row)
        judgment = judgments.get(key)
        top_twenty.append({
            "position": position, "frente": row["frente"], "slug": row["slug"],
            "title": row.get("title"), "actual_role": row.get("clinical_role"),
            "actual_context": row.get("clinical_context"),
            "judgment": "reviewed" if judgment else "unjudged",
            "expected_role": judgment.get("expected_role") if judgment else None,
            "reason": judgment.get("reason") if judgment else None,
        })
        if judgment and row.get("clinical_role") != judgment.get("expected_role"):
            fail("top_20_role", key, expected=judgment.get("expected_role"),
                 actual=row.get("clinical_role"))
    unjudged = [identity(item) for item in top_twenty if item["judgment"] == "unjudged"]
    return {
        "query": response.get("query"), "passed": not failures, "failures": failures,
        "required": required, "forbidden_tested_count": len(gold.get("forbidden", [])),
        "forbidden_found": forbidden_found, "forbidden_note": gold.get("forbidden_note"),
        "qualified": qualified, "cross_lesion_controls": controls,
        "first_comparison_or_mention_position": first_contextual,
        "top_20": {
            "returned_count": len(top_twenty), "judged_count": len(top_twenty) - len(unjudged),
            "unjudged_keys": unjudged, "clinical_review_complete": not unjudged,
            "items": top_twenty,
            "metric_note": "Julgamentos clínicos do gold; não calcula P@20. Itens não julgados permanecem indeterminados.",
        },
    }


def compare_alias(canonical: dict, alias: dict) -> dict:
    canonical_keys = [identity(row) for row in canonical["results"]]
    alias_keys = [identity(row) for row in alias["results"]]
    canonical_rows = {identity(row): row for row in canonical["results"]}
    alias_rows = {identity(row): row for row in alias["results"]}
    metadata_differences = [
        {"key": key, "field": field, "canonical": canonical_rows[key].get(field),
         "alias": alias_rows[key].get(field)}
        for key in canonical_keys if key in alias_rows
        for field in CLINICAL_FIELDS
        if canonical_rows[key].get(field) != alias_rows[key].get(field)
    ]
    same_disease = canonical.get("primary_disease") == alias.get("primary_disease")
    return {
        "query": alias["query"], "passed": canonical_keys == alias_keys and same_disease and not metadata_differences,
        "same_primary_disease": same_disease, "same_order": canonical_keys == alias_keys,
        "missing_keys": [key for key in canonical_keys if key not in alias_rows],
        "additional_keys": [key for key in alias_keys if key not in canonical_rows],
        "clinical_metadata_differences": metadata_differences,
    }


def compare_baseline(current: dict, baseline: dict, gold: dict) -> dict:
    before_keys = [identity(row) for row in baseline["results"]]
    after_keys = [identity(row) for row in current["results"]]
    if len(set(before_keys)) != len(before_keys):
        raise AuditContractError("Baseline contains duplicate typed identities.")
    before = {key: i for i, key in enumerate(before_keys, 1)}
    after = {key: i for i, key in enumerate(after_keys, 1)}
    return {
        "provenance": gold.get("baseline", {}).get("provenance"),
        "baseline_query": baseline.get("query"),
        "baseline_reported_total": baseline.get("total"),
        "baseline_collected_count": len(before_keys), "current_count": len(after_keys),
        "baseline_complete": baseline.get("total") == len(before_keys),
        "added_keys": [key for key in after_keys if key not in before],
        "removed_keys": [key for key in before_keys if key not in after],
        "required_positions": [{**item, "before": before.get(identity(item)),
                                "after": after.get(identity(item))} for item in gold.get("required", [])],
        "note": "Comparação descritiva; o baseline anterior não recebe retroativamente novos requisitos de classificação.",
    }


def run_audit(fetch: Callable[[str, int, int], dict], gold: dict, page_size: int = 25,
              baseline: dict | None = None) -> dict:
    if gold.get("schema_version") != 1 or not isinstance(gold.get("query"), str):
        raise AuditContractError("Gold must use schema_version 1 and contain query.")
    queries = list(dict.fromkeys([gold["query"], *gold.get("aliases", [])]))
    responses = [collect_pages(fetch, query, page_size) for query in queries]
    evaluations = [evaluate_response(response, gold) for response in responses]
    aliases = [compare_alias(responses[0], response) for response in responses[1:]]
    failures = [dict(failure, query=report["query"])
                for report in evaluations for failure in report["failures"]]
    failures.extend({"code": "alias_mismatch", "query": item["query"]}
                    for item in aliases if not item["passed"])
    return {
        "schema_version": 1, "passed": not failures, "failures": failures,
        "query": gold["query"], "scope": gold.get("scope"),
        "evaluations": evaluations, "alias_comparisons": aliases, "responses": responses,
        "baseline_comparison": compare_baseline(responses[0], baseline, gold) if baseline else None,
        "generic_recovery_without_profile": {
            "executed": False,
            "note": "Exige testes independentes sem perfil clínico; este auditor não altera o perfil do serviço.",
            "items": gold.get("generic_recovery_without_profile", []),
        },
    }


def audit_database(gold: dict, page_size: int, baseline: dict | None = None) -> dict:
    """Use the actual endpoint function in one consistent, read-only snapshot."""
    from sqlalchemy import text

    from app.api.search import search
    from app.core.db import SessionLocal

    db = SessionLocal()
    try:
        db.execute(text("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ, READ ONLY"))
        db.execute(text("SET LOCAL statement_timeout = '60s'"))
        if db.execute(text("SHOW transaction_read_only")).scalar_one() != "on":
            raise AuditContractError("Database did not confirm a READ ONLY transaction.")

        def fetch(query: str, limit: int, offset: int) -> dict:
            return search(q=query, frente=None, secao=None, limit=limit, offset=offset,
                          db=db, _=None)

        report = run_audit(fetch, gold, page_size, baseline)
        report["execution"] = {
            "entrypoint": "app.api.search.search", "transport": "python_function",
            "authentication_exercised": False, "transaction_read_only": True,
            "transaction_isolation": "repeatable read",
            "statement_timeout_seconds": 60,
            "note": "Chamada direta da função do endpoint; não é teste HTTP nem teste de autenticação.",
        }
        return report
    finally:
        db.rollback()
        db.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gold", type=Path, default=DEFAULT_GOLD)
    parser.add_argument("--baseline", type=Path, help="Optional earlier scientific search response JSON.")
    parser.add_argument("--output", type=Path, help="Write JSON here instead of stdout.")
    parser.add_argument("--page-size", type=int, default=25, choices=range(1, 101), metavar="1..100")
    args = parser.parse_args(argv)
    try:
        gold = json.loads(args.gold.read_text(encoding="utf-8"))
        baseline = json.loads(args.baseline.read_text(encoding="utf-8")) if args.baseline else None
        # Preserve stdout as machine-readable JSON even if a backend import prints.
        with redirect_stdout(sys.stderr):
            report = audit_database(gold, args.page_size, baseline)
        status = 0 if report["passed"] else 1
    except (AuditContractError, json.JSONDecodeError) as exc:
        report = {"schema_version": 1, "passed": False,
                  "failures": [{"code": "audit_contract_error", "message": str(exc)}]}
        status = 2
    except Exception as exc:
        # SQL exception strings can include connection details; do not export them.
        report = {"schema_version": 1, "passed": False, "failures": [{
            "code": "audit_execution_error", "error_type": type(exc).__name__,
            "message": "Audit did not complete; verify backend dependencies and the isolated QA database configuration.",
        }]}
        status = 2
    report["generated_at"] = datetime.now(timezone.utc).isoformat()
    payload = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    else:
        sys.stdout.write(payload)
    return status


if __name__ == "__main__":
    raise SystemExit(main())
