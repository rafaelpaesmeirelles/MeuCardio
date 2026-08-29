from __future__ import annotations

"""Reconstrói em lote sínteses científicas a partir dos documentos originais.

Uso no ambiente da aplicação:

    python -m app.commands.rebuild_scientific_sources

O comando é intencionalmente conservador: para em rate limit, quando a fila
termina ou quando uma rodada não progride. Itens cujo original não pôde ser
consultado ficam retidos pelo quality gate, sem publicação.
"""

import argparse
import json

from app.core.db import SessionLocal
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


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    limit = max(1, min(int(args.limit), COMPLETE_PUBLICATION_LIMIT))
    max_rounds = max(1, int(args.max_rounds))

    totals = {
        "processed": 0,
        "reopened_low_quality": 0,
        "quarantined_fallback_documents": 0,
        "blocked_source_original": 0,
        "failures": 0,
    }
    rounds: list[dict] = []
    exit_code = 0

    db = SessionLocal()
    try:
        for round_number in range(1, max_rounds + 1):
            result = process_pending_guidelines(db, limit=limit)
            snapshot = {
                "round": round_number,
                "processed": int(result.get("processed") or 0),
                "reopened_low_quality": int(result.get("reopened_low_quality") or 0),
                "quarantined_fallback_documents": int(result.get("quarantined_fallback_documents") or 0),
                "blocked_source_original": int(result.get("blocked_source_original") or 0),
                "remaining": int(result.get("remaining") or 0),
                "rate_limited": bool(result.get("rate_limited")),
                "failures": list(result.get("failures") or []),
            }
            rounds.append(snapshot)
            totals["processed"] += snapshot["processed"]
            totals["reopened_low_quality"] += snapshot["reopened_low_quality"]
            totals["quarantined_fallback_documents"] += snapshot["quarantined_fallback_documents"]
            totals["blocked_source_original"] += snapshot["blocked_source_original"]
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
            "rounds": rounds,
        }, ensure_ascii=False, sort_keys=True))
        return 1
    finally:
        db.close()

    print(json.dumps({
        "status": "ok" if exit_code == 0 else "incomplete",
        "totals": totals,
        "rounds": rounds,
        "remaining": rounds[-1]["remaining"] if rounds else None,
        "rate_limited": rounds[-1]["rate_limited"] if rounds else False,
    }, ensure_ascii=False, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
