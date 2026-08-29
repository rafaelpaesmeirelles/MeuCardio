from __future__ import annotations

import json

from app.core.db import SessionLocal
from app.services.guideline_clinical_update_runtime import reapply_confirmed_updates


def main() -> int:
    db = SessionLocal()
    try:
        result = reapply_confirmed_updates(db)
    except Exception as exc:  # noqa: BLE001
        db.rollback()
        print(json.dumps({"status": "error", "type": type(exc).__name__, "detail": str(exc)}, ensure_ascii=False))
        return 1
    finally:
        db.close()
    print(json.dumps({"status": "ok", **result}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
