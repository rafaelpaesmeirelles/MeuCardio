from __future__ import annotations

"""Reconstrói em lote sínteses científicas a partir dos documentos originais.

Uso no ambiente da aplicação:

    python -m app.commands.rebuild_scientific_sources

O comando é intencionalmente conservador: para em rate limit, quando a fila
termina ou quando uma rodada não progride. Itens cujo original não pôde ser
consultado ficam retidos pelo quality gate, sem publicação.

A saída JSON é também o relatório de auditoria: além dos totais, registra por
item DOI, URL primária, nível de acesso, partes observadas do original e estado
final de publicação. Assim é possível provar quais sínteses foram realmente
reconstruídas e quais permaneceram em quarentena.
"""

import argparse
import json

from app.core.db import SessionLocal
from app.models.guideline import Guideline
from app.services import guideline_clinical_update as core
from app.services.guideline_clinical_update_runtime import (
    COMPLETE_PUBLICATION_LIMIT,
    process_pending_guidelines,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Reconstrói sínteses CorVIA Intelligence usando a fonte original."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=COMPLETE_PUBLICATION_LIMIT,
        help=f"Máximo por rodada (1-{COMPLETE_PUBLICATION_LIMIT}).",
    )
    parser.add_argument(
        "--max-rounds",
        type=int,
        default=20,
        help="Limite de rodadas para evitar loop não intencional.",
    )
    return parser


def _audit_item(db, item: dict) -> dict:
    guideline_id = int(item.get("guideline_id") or 0)
    guideline = db.get(Guideline, guideline_id) if guideline_id else None
    analysis = core.get_analysis(db, guideline) if guideline is not None else None
    analysis = analysis if isinstance(analysis, dict) else {}
    doc = None
    if guideline is not None:
        slug = f"corvia-intelligence-{guideline.slug}"[:255]
        doc = db.query(core.Document).filter(core.Document.slug == slug).first()

    return {
        "guideline_id": guideline_id or None,
        "slug": item.get("slug") or (guideline.slug if guideline is not None else None),
        "title": guideline.titulo if guideline is not None else None,
        "org": guideline.org if guideline is not None else None,
        "doi": guideline.doi if guideline is not None else None,
        "guideline_url": guideline.url if guideline is not None else None,
        "pipeline_status": item.get("status"),
        "quality_gate": item.get("quality_gate"),
        "source_access_level": analysis.get("source_access_level"),
        "primary_source_url": analysis.get("primary_source_url"),
        "source_access_reason_pt": analysis.get("source_access_reason_pt"),
        "original_sections_seen": list(analysis.get("original_sections_seen") or [])[:8],
        "source_urls_seen": list(analysis.get("source_urls_seen") or [])[:8],
        "summary_published": bool(doc.published) if doc is not None else False,
        "review_status": doc.review_status if doc is not None else None,
        "gaps": list(doc.gaps or []) if doc is not None else [],
        "candidates": int(item.get("candidates") or 0),
        "proposed": int(item.get("proposed") or 0),
        "verified": int(item.get("verified") or 0),
        "applied": int(item.get("applied") or 0),
    }


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    limit = max(1, min(int(args.limit), COMPLETE_PUBLICATION_LIMIT))
    max_rounds = max(1, int(args.max_rounds))

    totals = {
        "processed": 0,
        "reopened_low_quality": 0,
        "quarantined_fallback_documents": 0,
        "blocked_source_original": 0,
        "published_from_original": 0,
        "failures": 0,
    }
    rounds: list[dict] = []
    audit_items: list[dict] = []
    exit_code = 0

    db = SessionLocal()
    try:
        for round_number in range(1, max_rounds + 1):
            result = process_pending_guidelines(db, limit=limit)
            round_items = [
                _audit_item(db, item)
                for item in (result.get("items") or [])
                if isinstance(item, dict)
            ]
            published_from_original = sum(
                item.get("quality_gate") == "published_from_original"
                and item.get("summary_published") is True
                for item in round_items
            )
            snapshot = {
                "round": round_number,
                "processed": int(result.get("processed") or 0),
                "reopened_low_quality": int(result.get("reopened_low_quality") or 0),
                "quarantined_fallback_documents": int(result.get("quarantined_fallback_documents") or 0),
                "blocked_source_original": int(result.get("blocked_source_original") or 0),
                "published_from_original": int(published_from_original),
                "remaining": int(result.get("remaining") or 0),
                "rate_limited": bool(result.get("rate_limited")),
                "failures": list(result.get("failures") or []),
                "items": round_items,
            }
            rounds.append(snapshot)
            audit_items.extend(round_items)
            totals["processed"] += snapshot["processed"]
            totals["reopened_low_quality"] += snapshot["reopened_low_quality"]
            totals["quarantined_fallback_documents"] += snapshot["quarantined_fallback_documents"]
            totals["blocked_source_original"] += snapshot["blocked_source_original"]
            totals["published_from_original"] += snapshot["published_from_original"]
            totals["failures"] += len(snapshot["failures"])

            if snapshot["rate_limited"]:
                break
            if snapshot["remaining"] == 0:
                break
            if snapshot["processed"] == 0:
                exit_code = 2
                break
    except Exception as exc:  # noqa: BLE001
        db.rollback()
        print(json.dumps({
            "status": "error",
            "type": type(exc).__name__,
            "detail": str(exc),
            "totals": totals,
            "items": audit_items,
            "rounds": rounds,
        }, ensure_ascii=False, sort_keys=True))
        return 1
    finally:
        db.close()

    print(json.dumps({
        "status": "ok" if exit_code == 0 else "incomplete",
        "totals": totals,
        "items": audit_items,
        "rounds": rounds,
        "remaining": rounds[-1]["remaining"] if rounds else None,
        "rate_limited": rounds[-1]["rate_limited"] if rounds else False,
    }, ensure_ascii=False, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
