"""Explicit, auditable disease matches for the published search catalogue.

Tags identify the subject of a reviewed item; they never establish a treatment
indication. Clinical conditions and comparisons come from the versioned profile.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from sqlalchemy import text

from app.services.catalog_search import normalizar


CLINICAL_ROLES = frozenset({"direct", "conditional", "comparison", "mention"})
PROFILE_PATH = Path(__file__).resolve().parents[1] / "data" / "search_clinical_context.json"

# Only these catalogue fronts expose structured tags. Text bodies, themes and
# substring matches are intentionally absent; publication is checked again by
# the final catalogue query, including for curated and graph destinations.
TAGGED_FRONTS = (
    ("documento", "documents"), ("galeria", "gallery_images"),
    ("exame", "lab_tests"), ("evidencia", "evidence_records"),
    ("estudo", "scientific_studies"), ("doenca", "specialty_diseases"),
    ("triagem_sintoma", "symptom_triage_guides"),
)
REVIEWED_TAG_MATCHES_SQL = text("\nUNION ALL\n".join(
    f"""SELECT DISTINCT '{front}'::text AS frente, slug, tag
    FROM {table} CROSS JOIN LATERAL unnest(tags) AS tag
    WHERE published = true AND review_status = 'revisado'
      AND trim(regexp_replace(unaccent(lower(translate(tag,
          '₀₁₂₃₄₅₆₇₈₉', '0123456789'))), '[^a-z0-9]+', ' ', 'g'))
          = ANY(CAST(:disease_phrases AS text[]))"""
    for front, table in TAGGED_FRONTS
))


def disease_identity_phrases(disease) -> tuple[str, ...]:
    """Whole registered identities, including explicitly registered plurals."""
    values = [disease.name, disease.slug, *(disease.aliases or [])]
    phrases = {normalizar(str(value or "")) for value in values}
    return tuple(sorted((p for p in phrases if len(p.replace(" ", "")) >= 2),
                        key=lambda value: (-len(value.split()), -len(value), value)))


@lru_cache(maxsize=1)
def clinical_profiles() -> dict:
    if not PROFILE_PATH.exists():
        return {}
    payload = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1 or not isinstance(payload.get("diseases"), dict):
        raise ValueError("Invalid search clinical context schema")
    for profile in payload["diseases"].values():
        seen = set()
        for item in profile["items"]:
            key = (item["frente"], item["slug"])
            if (key in seen or item["role"] not in CLINICAL_ROLES
                    or type(item["priority"]) is not int
                    or not isinstance(item["context"], str) or not item["context"].strip()
                    or not item.get("evidence_sources")):
                raise ValueError("Invalid search clinical context item")
            seen.add(key)
    return payload["diseases"]


def disease_search_metadata(db, disease, connections: dict[str, dict]) -> dict[str, dict]:
    """Return selection identities and reasons, never synthetic result rows."""
    metadata = {}
    if not disease.published:
        return metadata
    for key, item in connections.items():
        if item.get("context_only"):
            continue
        metadata[key] = {
            "clinical_role": "direct", "clinical_context": None,
            "relation_type": item.get("relation_type"), "context_only": False,
            "match_reasons": [{"source": item.get("relation_method") or "structured_connection", "description":
                item.get("relation_reason") or "Vínculo estruturado com a doença."}],
        }
    for item in db.execute(REVIEWED_TAG_MATCHES_SQL, {
        "disease_phrases": list(disease_identity_phrases(disease)),
    }).mappings():
        key = f"{item['frente']}:{item['slug']}"
        connection = connections.get(key, {})
        value = metadata.setdefault(key, {
            "clinical_role": "direct", "clinical_context": None, "match_reasons": [],
            "relation_type": connection.get("relation_type"),
            "context_only": connection.get("context_only", False),
        })
        reason = {"source": "reviewed_tag", "description": f"Tag revisada: {item['tag']}."}
        if reason not in value["match_reasons"]:
            value["match_reasons"].append(reason)
    for item in clinical_profiles().get(disease.slug, {}).get("items", []):
        key = f"{item['frente']}:{item['slug']}"
        reasons = metadata.get(key, {}).get("match_reasons", [])
        metadata[key] = {
            "clinical_role": item["role"], "clinical_context": item["context"],
            "priority": item["priority"], "relation_type": item.get("relation_type"),
            "context_only": item["role"] in {"comparison", "mention"},
            "match_reasons": [*reasons, {"source": "clinical_profile", "description":
                item["context"], "evidence_sources": item["evidence_sources"]}],
        }
    return metadata
