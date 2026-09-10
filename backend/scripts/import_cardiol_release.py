#!/usr/bin/env python3
"""Validate/import reviewed Cardiol originals; offline dry-run is the default.

--database-plan reads current asset state without writes.
--apply is the explicitly authorized postdeployment operation.
Neither mode triggers a worker, paid AI generation or clinical approval.
"""
import argparse
import json
from pathlib import Path
from app.services.scientific_publication_import import apply_import, load_release, plan_import


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release-dir", type=Path,
                        default=Path(__file__).resolve().parents[2] / "releases" / "cardiol-20260910")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--database-plan", action="store_true", help="Read current asset state without writes.")
    mode.add_argument("--apply", action="store_true", help="Apply the authorized import after deployment.")
    args = parser.parse_args(argv)
    originals = load_release(args.release_dir)
    if not args.apply and not args.database_plan:
        report = plan_import(originals)
    else:
        from sqlalchemy import text
        from app.core.db import SessionLocal
        with SessionLocal() as db:
            if args.apply:
                report = apply_import(db, originals)
            else:
                db.execute(text("SET TRANSACTION READ ONLY"))
                report = plan_import(originals, db)
                db.rollback()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
