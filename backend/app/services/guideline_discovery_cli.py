import json

from app.core.db import SessionLocal
from app.services.guideline_discovery_worldwide import discover_and_publish_worldwide


def main() -> None:
    db = SessionLocal()
    try:
        result = discover_and_publish_worldwide(db)
        print(json.dumps(result, ensure_ascii=False, default=str, sort_keys=True))
    finally:
        db.close()


if __name__ == "__main__":
    main()
