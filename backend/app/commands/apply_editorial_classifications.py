"""Apply only reviewed runtime editorial metadata, atomically and with an audit.

Default mode is read-only. Canonical corrections belong to reconcile_content;
this command handles existing Intelligence summaries without regenerating them.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json

from sqlalchemy import text

from app.core.db import SessionLocal
from app.models.audit import AuditLog
from app.services.editorial_kind_overrides import (
    guideline_source_identity, json_sha256, load_editorial_registry,
)

CAS_FIELDS = (
    "id", "slug", "title", "kind", "theme", "tags", "source_refs",
    "evidence_level", "source_tier", "review_status", "published", "version",
    "body_sha256", "summary_sha256", "title_sha256", "source_metadata_sha256",
)
DOCUMENT_SQL = """SELECT id, slug, title, kind, theme, tags, source_refs,
 evidence_level, source_tier, review_status, published, version,
 encode(sha256(convert_to(coalesce(body_md, ''), 'UTF8')), 'hex') AS body_sha256,
 encode(sha256(convert_to(coalesce(summary, ''), 'UTF8')), 'hex') AS summary_sha256,
 encode(sha256(convert_to(coalesce(title, ''), 'UTF8')), 'hex') AS title_sha256
 FROM documents WHERE slug = :slug"""
SOURCE_SQL = """SELECT g.id AS guideline_id, l.id AS link_id,
 g.slug, g.org, g.titulo, g.ano, g.doi, g.url, g.source_fingerprint,
 l.confirmado FROM guidelines g JOIN guideline_links l ON l.guideline_id = g.id
 WHERE l.item_type = 'intelligence_document' AND l.item_id = :document_id"""


def validate_runtime_identity(entry: dict, row: dict, source: dict) -> None:
    """Document identity and exact source provenance are mandatory on every run."""
    expected = entry.get("expected") or {}
    if not set(CAS_FIELDS) <= set(expected) or not expected.get("cas_metadata_sha256"):
        raise ValueError(f"Incomplete reviewed runtime snapshot: {entry['slug']}")
    if row["id"] != expected["id"] or row["slug"] != entry["slug"]:
        raise ValueError(f"Runtime document identity changed: {entry['slug']}")
    if row["kind"] not in {entry["old_value"], entry["new_value"]}:
        raise ValueError(f"Runtime kind changed since review: {entry['slug']}")
    identity = guideline_source_identity(source)
    if (not source["confirmado"]
            or source["guideline_id"] != entry["expected_guideline_id"]
            or source["link_id"] != entry["expected_link_id"]
            or identity != entry["source_identity"]
            or json_sha256(identity) != entry["source_sha256"]):
        raise ValueError(f"Runtime publication identity changed: {entry['slug']}")


def validate_runtime_snapshot(entry: dict, row: dict, source: dict) -> None:
    """An unaudited application still requires the exact reviewed scientific bytes."""
    validate_runtime_identity(entry, row, source)
    expected = entry["expected"]
    current = {key: row[key] for key in CAS_FIELDS}
    current["kind"] = entry["old_value"]
    reviewed = {key: expected[key] for key in CAS_FIELDS}
    if (expected["kind"] != entry["old_value"]
            or json_sha256(reviewed) != expected["cas_metadata_sha256"]
            or current != reviewed):
        raise ValueError(f"Runtime content/metadata changed since review: {entry['slug']}")


def _completion_identity(registry: dict, entry: dict) -> dict:
    return {
        "decision_id": registry["decision_id"],
        "registry_sha256": registry["registry_sha256"],
        "evidence_sha256": registry["evidence_sha256"],
        "evidence_id": entry["evidence_id"],
        "source_sha256": entry["source_sha256"],
        "document_id": entry["expected"]["id"],
        "document_slug": entry["slug"],
        "old_kind": entry["old_value"],
        "new_kind": entry["new_value"],
        "scope": registry["scope"],
        "publication_changed": False,
    }


def _has_completion_audit(db, registry: dict, entry: dict) -> bool:
    expected = _completion_identity(registry, entry)
    rows = db.execute(text("SELECT detail FROM audit_logs "
        "WHERE entity = 'documento' AND entity_id = :slug "
        "AND action IN ('editorial_kind_reclassified', 'editorial_kind_verified')"),
        {"slug": entry["slug"]}).scalars()
    # Compare canonical JSON, preserving JSON types (e.g. integer id vs boolean).
    return any(isinstance(detail, dict) and set(expected) <= set(detail)
               and json_sha256({key: detail[key] for key in expected}) == json_sha256(expected)
               for detail in rows)


def plan_runtime_classifications(db, registry: dict, *, lock: bool = False,
                                 require_snapshot_ids: frozenset[int] = frozenset()) -> list[dict]:
    if tuple(registry.get("runtime_cas_fields", ())) != CAS_FIELDS:
        raise ValueError("Runtime compare-and-set contract differs from this command")
    planned = []
    for entry in sorted((e for e in registry["entries"] if e["origin"] == "intelligence_summary"),
                        key=lambda e: e["expected"]["id"]):
        row = db.execute(text(DOCUMENT_SQL + (" FOR UPDATE" if lock else "")),
                         {"slug": entry["slug"]}).mappings().one_or_none()
        if row is None:
            raise ValueError(f"Reviewed runtime document is missing: {entry['slug']}")
        row = dict(row)
        row["source_metadata_sha256"] = json_sha256({key: row[key]
            for key in ("source_refs", "source_tier", "evidence_level")})
        sources = db.execute(text(SOURCE_SQL + (" FOR UPDATE OF g, l" if lock else "")),
                             {"document_id": row["id"]}).mappings().all()
        if len(sources) != 1:
            raise ValueError(f"Runtime source linkage is not unique: {entry['slug']}")
        source = dict(sources[0])
        validate_runtime_identity(entry, row, source)
        completed = row["kind"] == entry["new_value"] and _has_completion_audit(db, registry, entry)
        if not completed or row["id"] in require_snapshot_ids:
            validate_runtime_snapshot(entry, row, source)
        planned.append({"entry": entry, "current": row["kind"], "completed": completed,
                        "change": row["kind"] != entry["new_value"]})
    return planned


def apply_runtime_classifications(db, registry: dict, planned: list[dict]) -> int:
    changed = 0
    for plan in planned:
        if plan["completed"]:
            continue
        entry = plan["entry"]
        if plan["change"]:
            updated = db.execute(text("UPDATE documents SET kind = :new_kind "
                "WHERE id = :id AND slug = :slug AND kind = :old_kind"), {
                    "new_kind": entry["new_value"], "id": entry["expected"]["id"],
                    "slug": entry["slug"], "old_kind": plan["current"],
                })
            if updated.rowcount != 1:
                raise ValueError(f"Runtime compare-and-set failed: {entry['slug']}")
            changed += 1
        # Retained classifications also need an exact, durable completion marker.
        db.add(AuditLog(user_id=None,
            action="editorial_kind_reclassified" if plan["change"] else "editorial_kind_verified",
            entity="documento", entity_id=entry["slug"], detail={
                **_completion_identity(registry, entry),
                "body_sha256": entry["expected"]["body_sha256"],
            }))
    return changed


def run(*, apply: bool = False, registry_path: str | None = None) -> dict:
    registry = load_editorial_registry(registry_path)
    with SessionLocal() as db:
        try:
            if not apply:
                db.execute(text("SET TRANSACTION READ ONLY"))
            db.execute(text("SET LOCAL statement_timeout = '30s'"))
            db.execute(text("SET LOCAL lock_timeout = '3s'"))
            if apply:
                db.execute(text("SELECT pg_advisory_xact_lock(71920, 20260910)"))
            planned = plan_runtime_classifications(db, registry, lock=apply)
            changed = apply_runtime_classifications(db, registry, planned) if apply else 0
            if apply:
                # SessionLocal disables autoflush; expose our completion markers before re-planning.
                db.flush()
                verified = plan_runtime_classifications(db, registry, require_snapshot_ids=frozenset(
                    p["entry"]["expected"]["id"] for p in planned if not p["completed"]))
                if any(p["change"] or not p["completed"] for p in verified):
                    raise ValueError("Runtime editorial materialization is incomplete")
                db.commit()
            else:
                db.rollback()
            return {
                "mode": "applied" if apply else "dry_run_read_only",
                "registry_sha256": registry["registry_sha256"],
                "runtime_reviewed": len(planned),
                "planned_changes": sum(p["change"] for p in planned),
                "changed": changed,
                "already_completed": sum(p["completed"] for p in planned),
                "completion_markers_recorded": sum(not p["completed"] for p in planned) if apply else 0,
                "retained_or_already_applied": sum(not p["change"] for p in planned),
                "target_kinds": dict(sorted(Counter(p["entry"]["new_value"] for p in planned).items())),
                "publication_changed": False,
                "clinical_content_changed": False,
            }
        except Exception:
            db.rollback()
            raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Apply the exact reviewed changes with row locks and audit")
    parser.add_argument("--registry", default=None, help="Path to the reviewed registry; default is the versioned package ledger")
    args = parser.parse_args()
    print(json.dumps(run(apply=args.apply, registry_path=args.registry), ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
