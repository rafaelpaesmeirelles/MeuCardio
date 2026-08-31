"""Purge expired encrypted Heart Team cache rows.

Dry-run by default. The normal daily maintenance job must invoke with --apply.
"""

from __future__ import annotations

import argparse

from app.core.db import SessionLocal
from app.models.audit import AuditLog
from app.models.heart_team import HeartTeamCache
from app.services.heart_team import purge_expired_cache, utcnow


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    with SessionLocal() as db:
        count = db.query(HeartTeamCache).filter(HeartTeamCache.expires_at <= utcnow()).count()
        if args.apply:
            deleted = purge_expired_cache(db)
            db.add(AuditLog(action="heart_team.cache_purge_maintenance", entity="heart_team_cache", detail={"deleted": deleted}, user_id=None)); db.commit()
            print(f"deleted={deleted}")
        else:
            print(f"would_delete={count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
