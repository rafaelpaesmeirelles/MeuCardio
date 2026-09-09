"""Read-only search acceptance on an existing published scientific catalogue.

Run with the backend environment configured; no writes, backfill or publication.
This checks retrieval behaviour, not medical review of every returned item.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from sqlalchemy import text
from app.api.search import search
from app.core.db import SessionLocal


def audit() -> dict:
    queries = ["FA", "fibrilacao atrial", "HAS", "hipertensao arterial",
               "insuficiencia cardiaca", "holter 24h"]
    reports = []
    for query in queries:
        with SessionLocal() as db:
            db.execute(text("SET TRANSACTION READ ONLY"))
            db.execute(text("SET LOCAL statement_timeout = '30s'"))
            started = time.monotonic()
            response = search(q=query, frente=None, limit=100, offset=0, db=db, _=None)
            reports.append({
                "query": query, "seconds": round(time.monotonic() - started, 3),
                "total": response["total"], "next_offset": response["next_offset"],
                "por_frente": response["por_frente"],
                "first_page": [(x["frente"], x["slug"]) for x in response["results"]],
                "supplementary_count": sum(len(g["itens"]) for g in response.get("supplementary_groups", [])),
            })
    by_query = {r["query"]: r for r in reports}
    fa, has, holter = (by_query[q] for q in ("FA", "HAS", "holter 24h"))
    checks = {
        "fa_alias_same_results": fa["first_page"] == by_query["fibrilacao atrial"]["first_page"],
        "fa_alias_same_total": fa["total"] == by_query["fibrilacao atrial"]["total"],
        "has_alias_same_results": has["first_page"] == by_query["hipertensao arterial"]["first_page"],
        "fa_core_scores": {("calculadora", "cha2ds2-vasc"), ("calculadora", "has-bled")} <= set(fa["first_page"]),
        "fa_core_fronts_first_page": {"doenca", "documento", "medicamento", "exame", "estudo", "evidencia", "calculadora"} <= {f for f, _ in fa["first_page"]},
        "fa_no_acronym_substring_noise": not {("calculadora", s) for s in ("ventilacao-protetora-uco", "acidose-metabolica-winter-anion-gap-uco", "dapt-score")} & set(fa["first_page"]),
        "holter_canonical_exam": ("exame", "holter-24h") in holter["first_page"],
        "pagination_not_silently_truncated": all(r["next_offset"] is not None for r in reports if r["total"] > 100),
        "unique_typed_identities": all(len(r["first_page"]) == len(set(r["first_page"])) for r in reports),
        "counts_reconcile": all(sum(r["por_frente"].values()) == r["total"] for r in reports),
    }
    return {"scope": "technical retrieval acceptance; not exhaustive clinical relevance certification",
            "read_only": True, "checks": checks, "passed": all(checks.values()), "queries": reports}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = audit()
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(rendered + "\n")
    else:
        print(rendered)
    raise SystemExit(0 if report["passed"] else 1)
