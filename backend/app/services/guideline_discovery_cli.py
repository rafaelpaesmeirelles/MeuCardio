import json
import os

from app.core.db import SessionLocal
from app.services.guideline_radar_runtime import run_radar


def _force_requested() -> bool:
    return os.getenv("CORVIA_INTELLIGENCE_FORCE", "").strip().casefold() in {"1", "true", "yes", "on"}


def main() -> None:
    db = SessionLocal()
    try:
        result = run_radar(db, force=_force_requested(), origin="cli")
        print(json.dumps(result, ensure_ascii=False, default=str, sort_keys=True))
    finally:
        db.close()


if __name__ == "__main__":
    main()
