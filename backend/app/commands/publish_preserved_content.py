"""Publica registros revisados que pertencem ao corpus canônico atual.

O reconciliador mantém registros antigos no PostgreSQL para auditoria. Eles
devem permanecer despublicados mesmo que tenham sido revisados no passado.
Este comando, mantido para uso operacional, restringe a publicação aos slugs
presentes nas fontes versionadas do commit atual.

Depois da reconciliação, restaura também os overrides clínicos confirmados pelo
CorVIA Intelligence. Assim uma atualização científica aplicada entre deploys
não é perdida quando arquivos versionados são novamente importados para o DB.
"""

from __future__ import annotations

import argparse
import json
from typing import Any

from sqlalchemy.orm import Session

from app.commands.reconcile_content import FRONTS, _canonical_source_slugs, _ensure_source
from app.core.db import SessionLocal


def publish_preserved_reviewed(db: Session, *, dry_run: bool = False) -> dict[str, Any]:
    by_front: dict[str, int] = {}
    total = 0
    try:
        for front, config in FRONTS.items():
            model = config["model"]
            source = _ensure_source(front, str(config["path"]))
            canonical_slugs = _canonical_source_slugs(front, source)
            query = db.query(model).filter(
                model.slug.in_(canonical_slugs),
                model.published.is_(False),
                model.review_status == "revisado",
            )
            changed = query.count() if dry_run else query.update(
                {model.published: True}, synchronize_session=False
            )
            by_front[front] = int(changed)
            total += int(changed)
        if dry_run:
            db.rollback()
        else:
            db.commit()
    except Exception:
        db.rollback()
        raise
    return {"published_total": total, "published_by_front": by_front, "dry_run": dry_run}


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
