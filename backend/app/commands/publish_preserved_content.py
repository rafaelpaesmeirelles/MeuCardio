"""Publica registros canônicos com intenção e aprovação explícitas.

O reconciliador mantém registros antigos no PostgreSQL para auditoria. Eles
devem permanecer despublicados mesmo que tenham sido revisados no passado.
Este comando, mantido para uso operacional, não pode contornar o reconciliador:
``published:false`` permanece em quarentena e ausência legada preserva o estado
existente sem promover registros novos.

Depois da reconciliação, restaura também os overrides clínicos confirmados pelo
CorVIA Intelligence. Assim uma atualização científica aplicada entre deploys
não é perdida quando arquivos versionados são novamente importados para o DB.
"""

from __future__ import annotations

import argparse
import json
from typing import Any

from sqlalchemy.orm import Session

from app.commands.reconcile_content import (
    FRONTS,
    _canonical_publication_intents,
    _canonical_source_slugs,
    _ensure_source,
    _load_editorial_approvals,
    _synchronize_publication,
    _validate_editorial_approvals,
)
from app.core.db import SessionLocal


def publish_preserved_reviewed(db: Session, *, dry_run: bool = False) -> dict[str, Any]:
    canonical_slugs: dict[str, set[str]] = {}
    publication_intents: dict[str, dict[str, bool | None]] = {}
    try:
        for front, config in FRONTS.items():
            source = _ensure_source(front, str(config["path"]))
            canonical_slugs[front] = _canonical_source_slugs(front, source)
            intents = _canonical_publication_intents(front, source)
            if set(intents) != canonical_slugs[front]:
                raise RuntimeError(
                    f"Frente {front}: intenção de publicação não cobre o corpus canônico."
                )
            publication_intents[front] = intents

        approvals = _load_editorial_approvals()
        _validate_editorial_approvals(canonical_slugs, approvals=approvals)
        (
            published,
            unpublished_absent,
            unpublished_unreviewed,
            unpublished_ineligible,
        ) = _synchronize_publication(
            db,
            canonical_slugs,
            publish_reviewed=True,
            approved_slugs=approvals,
            publication_intents=publication_intents,
            dry_run=dry_run,
        )
    except Exception:
        db.rollback()
        raise
    return {
        "published_total": sum(published.values()),
        "published_by_front": published,
        "unpublished_absent": unpublished_absent,
        "unpublished_unreviewed": unpublished_unreviewed,
        "unpublished_ineligible": unpublished_ineligible,
        "dry_run": dry_run,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        result = publish_preserved_reviewed(db, dry_run=args.dry_run)
        if not args.dry_run:
            from app.services.guideline_clinical_update_runtime import reapply_confirmed_updates
            result["guideline_updates"] = reapply_confirmed_updates(db)
    except Exception as exc:  # noqa: BLE001
        db.rollback()
        print(json.dumps({"status": "error", "type": type(exc).__name__, "detail": str(exc)}, ensure_ascii=False, indent=2))
        return 1
    finally:
        db.close()

    print(json.dumps({"status": "ok", **result}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
