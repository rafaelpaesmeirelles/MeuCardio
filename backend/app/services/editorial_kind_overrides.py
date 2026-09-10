"""Hash-bound editorial metadata corrections; never publication authorization.

Canonical source bytes remain the scientific authority. This independent ledger
can change only Document.kind or ScientificStudy.study_type, after exact matching.
It does not supply review status, publication flags, body text, or entity aliases.
"""
from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from hashlib import sha256
import json
from pathlib import Path
import re

REGISTRY_PATH = Path(__file__).with_name("editorial_kind_registry.json")
SCOPE = "editorial_metadata_only_no_publication_authorization"
IDENTITY_FIELDS = ("slug", "org", "titulo", "ano", "doi", "url", "source_fingerprint")
CLAIM_FIELDS = ("entity_type", "slug", "field", "old_value", "new_value", "source_sha256")
_FIELDS = {"documento": "kind", "estudo": "study_type"}
_ORIGINS = {"canonical_markdown", "canonical_json", "intelligence_summary"}
_VALUES = {"preprint", "errata", "documento", "estudo", "revisao", "revisão", "diretriz", "guideline", "consenso", "consensus", "posicionamento", "protocolo", "conduta", "ensaio_clinico", "estudo_observacional", "revisao_sistematica", "revisao_narrativa", "meta_analise", "metanalise", "modulo", "farmacologia"}
_BASES = {"confirmed_publication_genre", "neutral_remove_unsupported_formal_claim"}
_active_registry = ContextVar("editorial_kind_registry", default=None)


def json_sha256(value) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()


def guideline_source_identity(guideline) -> dict:
    if isinstance(guideline, dict):
        return {key: guideline.get(key) for key in IDENTITY_FIELDS}
    return {key: getattr(guideline, key, None) for key in IDENTITY_FIELDS}


def _safe_path(root: Path, relative: str) -> Path:
    path = Path(relative)
    target = (root / path).resolve()
    if path.is_absolute() or ".." in path.parts or not target.is_relative_to(root.resolve()):
        raise ValueError("Editorial evidence/source path escapes its root")
    return target


def load_editorial_registry(path: Path | str | None = None) -> dict:
    """Read and validate the complete claim/evidence ledger, failing closed."""
    if path is None and _active_registry.get() is not None:
        return _active_registry.get()
    path = Path(path or REGISTRY_PATH)
    raw = path.read_bytes()
    data = json.loads(raw)
    if data.get("schema_version") != 1 or data.get("scope") != SCOPE:
        raise ValueError("Invalid editorial registry schema/scope")
    evidence_path = _safe_path(path.parent, data["evidence_file"])
    evidence_raw = evidence_path.read_bytes()
    if sha256(evidence_raw).hexdigest() != data.get("evidence_sha256"):
        raise ValueError("Editorial evidence fingerprint mismatch")
    evidence = json.loads(evidence_raw)
    if evidence.get("schema_version") != 1 or evidence.get("scope") != SCOPE:
        raise ValueError("Invalid editorial evidence schema/scope")
    index, seen_evidence = {}, set()
    entries = data.get("entries")
    claims = evidence.get("claims")
    if not isinstance(entries, list) or not isinstance(claims, dict):
        raise ValueError("Invalid editorial entries/claims")
    for entry in entries:
        key = (entry.get("entity_type"), entry.get("slug"))
        if not isinstance(key[1], str) or not key[1] or key in index:
            raise ValueError("Duplicate/invalid editorial identity")
        if _FIELDS.get(key[0]) != entry.get("field") or entry.get("origin") not in _ORIGINS:
            raise ValueError("Unsupported editorial field/origin")
        if entry["origin"] == "intelligence_summary" and key[0] != "documento":
            raise ValueError("Runtime genre applies only to Document")
        if entry["origin"] == "canonical_markdown" and key[0] != "documento":
            raise ValueError("Markdown genre applies only to Document")
        if entry["origin"] == "canonical_json" and key[0] != "estudo":
            raise ValueError("JSON genre applies only to ScientificStudy")
        if entry.get("new_value") not in _VALUES or not isinstance(entry.get("old_value"), str):
            raise ValueError("Unsupported editorial kind")
        # Structural graph type changes require their own migration and review.
        if entry["old_value"] in {"fluxograma", "flowchart", "algoritmo"}:
            raise ValueError("Editorial correction cannot change graph entity type")
        if not re.fullmatch(r"[a-f0-9]{64}", entry.get("source_sha256", "")):
            raise ValueError("Missing editorial source fingerprint")
        evidence_id = entry.get("evidence_id")
        claim = claims.get(evidence_id, {})
        if any(claim.get(field) != entry.get(field) for field in CLAIM_FIELDS):
            raise ValueError("Editorial evidence does not prove this exact claim")
        if claim.get("decision_basis") not in _BASES or not claim.get("rationale") or not claim.get("evidence"):
            raise ValueError("Editorial genre requires explicit evidence and rationale")
        if claim["decision_basis"] == "neutral_remove_unsupported_formal_claim" and entry["new_value"] != "documento":
            raise ValueError("Unverified genres must remain neutral")
        if entry["origin"] == "intelligence_summary":
            identity = entry.get("source_identity", {})
            if set(identity) != set(IDENTITY_FIELDS) or json_sha256(identity) != entry["source_sha256"]:
                raise ValueError("Runtime source identity fingerprint mismatch")
            if key[1] != f"corvia-intelligence-{identity['slug']}"[:255]:
                raise ValueError("Runtime source/document identity mismatch")
        else:
            _safe_path(Path("/editorial-root"), entry.get("source_path", ""))
            if not entry.get("source_path"):
                raise ValueError("Canonical source path missing")
        index[key] = entry
        seen_evidence.add(evidence_id)
    if set(claims) != seen_evidence:
        raise ValueError("Editorial evidence contains unbound claims")
    return {**data, "index": index, "registry_sha256": sha256(raw).hexdigest(), "registry_path": str(path), "evidence_path": str(evidence_path)}


@contextmanager
def editorial_registry_scope(registry: dict):
    token = _active_registry.set(registry)
    try:
        yield
    finally:
        _active_registry.reset(token)


def canonical_editorial_value(entity_type: str, slug: str, field: str, old_value: str,
                              source_sha256: str, *, registry: dict | None = None) -> str:
    registry = registry if registry is not None else load_editorial_registry()
    entry = registry["index"].get((entity_type, slug))
    if entry is None:
        return old_value
    if entry["origin"] == "intelligence_summary" or entry["field"] != field:
        raise ValueError(f"Editorial source origin mismatch: {entity_type}:{slug}")
    if entry["old_value"] != old_value or entry["source_sha256"] != source_sha256:
        raise ValueError(f"Stale editorial source: {entity_type}:{slug}")
    return entry["new_value"]


def runtime_document_kind(guideline, *, registry: dict | None = None) -> str:
    registry = registry if registry is not None else load_editorial_registry()
    identity = guideline_source_identity(guideline)
    slug = f"corvia-intelligence-{identity['slug']}"[:255]
    entry = registry["index"].get(("documento", slug))
    if entry is None:
        return "documento"
    if entry["origin"] != "intelligence_summary" or entry["source_sha256"] != json_sha256(identity):
        raise ValueError(f"Stale verified runtime publication identity: {slug}")
    return entry["new_value"]


def validate_editorial_sources(root: Path | str, registry: dict | None = None) -> dict:
    """Validate ALL canonical corrections before any import/database mutation."""
    import frontmatter
    registry = registry if registry is not None else load_editorial_registry()
    root = Path(root)
    checked = 0
    json_records = {}
    for entry in registry["entries"]:
        if entry["origin"] == "intelligence_summary":
            continue
        source = _safe_path(root, entry["source_path"])
        if entry["origin"] == "canonical_markdown":
            raw = source.read_bytes()
            metadata = frontmatter.loads(raw.decode("utf-8")).metadata
            # Same slug resolver as the importer, including legacy fallback.
            from app.services.importer import _resolve_markdown_slug
            actual_slug = _resolve_markdown_slug(metadata, metadata.get("title") or source.stem, source=str(source))
            digest = sha256(raw).hexdigest()
            old_value = metadata.get("kind", "modulo")
        else:
            if source not in json_records:
                records = json.loads(source.read_text(encoding="utf-8"))
                if not isinstance(records, list):
                    raise ValueError("Canonical studies must be a list")
                slugs = [record.get("slug") for record in records]
                if len(set(slugs)) != len(slugs):
                    raise ValueError("Duplicate canonical study identity")
                json_records[source] = {record["slug"]: record for record in records}
            record = json_records[source].get(entry["slug"])
            if record is None:
                raise ValueError("Editorial study source missing")
            actual_slug = record["slug"]
            digest = json_sha256(record)
            old_value = record.get("study_type")
        if actual_slug != entry["slug"]:
            raise ValueError("Editorial canonical identity mismatch")
        canonical_editorial_value(entry["entity_type"], entry["slug"], entry["field"], old_value, digest, registry=registry)
        checked += 1
    return {"canonical_claims_checked": checked, "registry_sha256": registry["registry_sha256"], "evidence_sha256": registry["evidence_sha256"]}


def validate_materialized_editorial_values(db, registry: dict) -> int:
    """Check materialization before publication; does not change any DB state."""
    from app.models.content import Document
    from app.models.study import ScientificStudy
    checked = 0
    for entry in registry["entries"]:
        if entry["origin"] == "intelligence_summary":
            continue
        model = Document if entry["entity_type"] == "documento" else ScientificStudy
        row = db.query(model).filter(model.slug == entry["slug"]).first()
        if row is None or getattr(row, entry["field"]) != entry["new_value"]:
            raise ValueError(f"Editorial correction was not materialized: {entry['entity_type']}:{entry['slug']}")
        checked += 1
    return checked
