import json

from app.core.db import SessionLocal
from app.services.guideline_discovery import discover_and_publish
from app.services.guideline_discovery_worldwide import enable_worldwide_sources


def main() -> None:
    enable_worldwide_sources()
    db = SessionLocal()
    try:
        result = discover_and_publish(db)
        print(json.dumps(result, ensure_ascii=False, default=str, sort_keys=True))
    finally:
        db.close()


if __name__ == "__main__":
    main()
