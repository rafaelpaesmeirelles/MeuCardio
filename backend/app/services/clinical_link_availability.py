"""Exact unavailable destinations: disclose absence without inventing an alias.

The registry changes presentation only. It never grants publication or creates
an entity. The offline audit verifies its evidence against the scoped release.
"""
from hashlib import sha256
import json
from pathlib import Path
import re
from urllib.parse import unquote

_REGISTRY_PATH = Path(__file__).with_suffix(".json")
_payload = json.loads(_REGISTRY_PATH.read_text(encoding="utf-8"))
if (_payload.get("schema_version") != 1 or
        _payload.get("scope") != "presentation_only_no_publication_authorization"):
    raise RuntimeError("Invalid unavailable-reference registry")
UNAVAILABLE_REFERENCES = _payload["references"]
UNAVAILABLE_SUFFIX = " (conteúdo indisponível nesta versão)"
_SCHEME = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")


def _reference_key(destination: str) -> str | None:
    path = unquote(destination).split("#", 1)[0].split("?", 1)[0].strip()
    if _SCHEME.match(path) or path.startswith("//"):
        return None
    if path.casefold().endswith(".md"):
        path = "/biblioteca/" + path.rsplit("/", 1)[-1][:-3]
    return path.rstrip("/")


def unavailable_clinical_link_reason(destination: str) -> str | None:
    record = UNAVAILABLE_REFERENCES.get(_reference_key(destination))
    return record["reason"] if record else None


def unavailable_clinical_link_label(label: str, destination: str) -> str | None:
    if unavailable_clinical_link_reason(destination) is None:
        return None
    return label + UNAVAILABLE_SUFFIX


def validate_unavailable_clinical_reference(
    destination: str, *, repository_root: Path, canonical_document_slugs: set[str],
    quarantined_document_slugs: set[str], source_path: str,
) -> dict | None:
    """Require exact proof and availability state before relaxing an audit link.

    Call only after the full snapshot/provenance validation. Unknown destinations
    are not exemptions; stale registries, changed evidence and renewed content
    fail closed until the presentation disposition is reconciled explicitly.
    """
    key = _reference_key(destination)
    record = UNAVAILABLE_REFERENCES.get(key)
    if record is None:
        return None
    slug = key.removeprefix("/biblioteca/")
    if not key.startswith("/biblioteca/") or source_path not in record["source_paths"]:
        raise RuntimeError("Unavailable reference not covered by its recorded source")
    root = repository_root.resolve()
    relative = Path(record["evidence_path"])
    evidence_path = (root / relative).resolve()
    if relative.is_absolute() or ".." in relative.parts or not evidence_path.is_relative_to(root):
        raise RuntimeError("Unsafe unavailable-reference evidence path")
    raw = evidence_path.read_bytes()
    if sha256(raw).hexdigest() != record["evidence_sha256"]:
        raise RuntimeError("Unavailable-reference evidence changed")
    evidence = json.loads(raw)
    reason = record["reason"]
    if reason == "target_quarantined":
        if (slug not in canonical_document_slugs or slug not in quarantined_document_slugs
                or slug not in evidence.get("quarantined", {}).get("documentos", [])):
            raise RuntimeError("Unavailable target no longer matches the approved quarantine")
    elif reason == "no_integral_approved_equivalent":
        matches = [item for item in evidence.get("items", []) if item.get("old_url") == key]
        if (slug in canonical_document_slugs or len(matches) != 1
                or matches[0].get("status") == "approved_same_entity"
                or source_path not in matches[0].get("source_paths", [])):
            raise RuntimeError("Unavailable target no longer matches the recorded bibliographic gap")
    else:
        raise RuntimeError("Unknown unavailable-reference reason")
    label = unavailable_clinical_link_label("Referenced content", destination)
    if label != "Referenced content" + UNAVAILABLE_SUFFIX:
        raise RuntimeError("Unavailable-reference presentation is not effective")
    return {"target": slug, "destination": key, "reason": reason,
            "evidence_path": record["evidence_path"], "evidence_sha256": record["evidence_sha256"],
            "presentation": "label_without_href", "suffix": UNAVAILABLE_SUFFIX}
