import json
import os

from app.core.db import SessionLocal
from app.services.guideline_discovery_worldwide import discover_and_publish_worldwide
from app.services.guideline_radar_schedule import decide_radar_run


def _force_requested() -> bool:
    return os.getenv("CORVIA_INTELLIGENCE_FORCE", "").strip().casefold() in {"1", "true", "yes", "on"}


def main() -> None:
    db = SessionLocal()
    try:
        schedule = decide_radar_run(db, force=_force_requested())
        if not schedule["run"]:
            print(json.dumps({
                "skipped": "adaptive_schedule",
                "radar_schedule": schedule,
            }, ensure_ascii=False, default=str, sort_keys=True))
            return

        result = discover_and_publish_worldwide(db)
        result["radar_schedule"] = schedule
        print(json.dumps(result, ensure_ascii=False, default=str, sort_keys=True))
    finally:
        db.close()


if __name__ == "__main__":
    main()
