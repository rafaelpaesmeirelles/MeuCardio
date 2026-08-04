"""Publica registros preservados que já passaram por revisão editorial.

O reconciliador mantém registros antigos no PostgreSQL para auditoria. Este
comando torna públicos todos os registros preservados com
``review_status == "revisado"`` e mantém rascunhos/pendências indisponíveis.
É idempotente e seguro para execução em todo deploy.
"""

from __future__ import annotations

import argparse
import json
from typing import Any

from sqlalchemy.orm import Session

from app.commands.reconcile_content import FRONTS
from app.core.db import SessionLocal


def publish_preserved_reviewed(db: Session, *, dry_run: bool = False) -> dict[str, Any]:
    by_front: dict[str, int] = {}
    total = 0
    try:
        for front, config in FRONTS.items():
            model = config["model"]
            query = db.query(model).filter(
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
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"status": "error", "type": type(exc).__name__, "detail": str(exc)},
                         ensure_ascii=False, indent=2))
        return 1
    finally:
        db.close()

    print(json.dumps({"status": "ok", **result}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
