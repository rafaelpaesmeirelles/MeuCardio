"""Curated offline publisher-original import. No fetch, AI, wallet or clinical changes.

Default validation is file-only. Database planning is read-only; application must
be explicitly requested by the deployment operator. All writes share the library
worker advisory lock and one database transaction. Previously acquired assets and AI processing history are preserved. A blocked
source acquisition with empty progress may receive a verified original while
retaining its attempt counter; no financial state is reconciled here.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

LOCK_ID = 719202611
RELEASE = "cardiol-20260910"
MAX_BYTES = 8 * 1024 * 1024
LICENSE_URLS = {
    "http://creativecommons.org/licenses/by/4.0/",
    "https://creativecommons.org/licenses/by/4.0/",
}
SAFE_EMPTY_STATUSES = {"pending", "blocked_fulltext", "blocked_license", "blocked_identity", "failed"}
SOURCE_HOSTS = {"www.ebi.ac.uk", "abccardiol.org", "www.abccardiol.org"}
XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"


@dataclass(frozen=True)
class Original:
    metadata: dict
    content: bytes
    parsed: dict
    summary: str | None
    manifest_sha256: str


def _sha(content):
    return hashlib.sha256(content).hexdigest()


def _local(root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or Path(relative).is_absolute():
        raise ValueError("Expected a release-relative file.")
    path = root / relative
    if ".." in Path(relative).parts or not path.resolve().is_relative_to(root.resolve()) or path.is_symlink():
        raise ValueError("Release file escapes its directory.")
    return path


def _license_equal(first, second):
    return first in LICENSE_URLS and second in LICENSE_URLS


def _verify_license(entry, source_recovery):
    proof = entry.get("license_evidence", {})
    if proof.get("doi") != entry["doi"] or not _license_equal(proof.get("license_url"), entry.get("license_url")):
        raise ValueError("License evidence does not match the article.")
    method = proof.get("method")
    if method == "original_article_permissions":
        # The parser independently verifies article-level machine-readable license.
        return False
    if method == "versioned_source_recovery":
        recovered = next((x for x in source_recovery["documents"] if x["doi"] == entry["doi"]), None)
        if not recovered or recovered.get("sha256") != entry["sha256"] or recovered.get("source_http_status") != 200:
            raise ValueError("Recovered source identity is unverified.")
        if not _license_equal(recovered.get("license_url"), entry["license_url"]):
            raise ValueError("Recovered source license is unverified.")
        return True
    if method != "publisher_metadata_confirmation":
        raise ValueError("Unknown license evidence method.")
    evidence = proof.get("evidence", {})
    if evidence.get("doi") != entry["doi"]:
        raise ValueError("Publisher confirmation DOI mismatch.")
    crossref = evidence.get("http_status") == 200 and evidence.get("queried_url") == "https://api.crossref.org/works/" + entry["doi"]
    if crossref:
        licenses = [x for x in evidence.get("licenses", []) if x.get("content-version") == "vor"]
        if any(_license_equal(x.get("URL"), entry["license_url"]) and
               x.get("start", {}).get("date-time", "9999") <= "2026-09-10T23:59:59Z" for x in licenses):
            return True
    publisher = evidence.get("publisher_verification", {})
    if publisher.get("http_status") == 200 and publisher.get("xml_http_status") == 200:
        url = urlsplit(publisher.get("xml_url", ""))
        if url.scheme != "https" or url.hostname not in SOURCE_HOSTS:
            raise ValueError("Publisher license confirmation URL is not official.")
        if not re.fullmatch(r"[0-9a-f]{64}", str(publisher.get("original_xml_sha256", ""))):
            raise ValueError("Publisher confirmation lacks original hash.")
        if any(_license_equal(x.get("attributes", {}).get("{http://www.w3.org/1999/xlink}href"),
                              entry["license_url"]) for x in publisher.get("license_evidence", [])
               if x.get("path") == "article/front/article-meta/permissions/license"):
            return True
    raise ValueError("Explicit publisher license confirmation missing.")


def validate_document(root: Path, entry: dict, checksums: dict, source_recovery: dict,
                      manifest_sha256: str) -> Original:
    from app.services.scientific_original_reading import parse_original_fulltext
    doi = entry.get("doi", "")
    if not re.fullmatch(r"10\.36660/abc\.20[0-9]{6}", doi):
        raise ValueError("Not a canonical SBC DOI in this curated release.")
    if entry.get("language") != "pt" or entry.get("year") not in (2025, 2026):
        raise ValueError("Unexpected language/year in curated release.")
    url = urlsplit(entry.get("source_url", ""))
    if url.scheme != "https" or url.hostname not in SOURCE_HOSTS or url.username or url.password:
        raise ValueError("Original URL is not an allowed official source.")
    expected = checksums.get(entry.get("file"))
    if not expected or (expected["sha256"], expected["bytes"]) != (entry.get("sha256"), entry.get("bytes")):
        raise ValueError("Manifest and versioned checksum record differ.")
    path = _local(root, entry["file"])
    if not path.is_file() or path.stat().st_size > MAX_BYTES:
        raise ValueError("Original missing or exceeds bounded import size.")
    content = path.read_bytes()
    if len(content) != entry["bytes"] or _sha(content) != entry["sha256"]:
        raise ValueError("Original SHA256/size mismatch.")
    fallback = _verify_license(entry, source_recovery)
    if entry.get("format") == "jats_xml":
        parsed = parse_original_fulltext(content, doi,
            verified_license_url=entry["license_url"] if fallback else None,
            verified_source_sha256=entry["sha256"] if fallback else None)
        if parsed.get("language") != "pt":
            raise ValueError("Root article is not originally Portuguese.")
        if not _license_equal(parsed.get("license_url"), entry["license_url"]):
            raise ValueError("Parsed original license differs from curated evidence.")
        # Parser has already rejected entities, unsafe XML and invalid article identity.
        meta = ET.fromstring(content).find("./front/article-meta")
        abstracts = [a for a in meta.findall("./abstract") if a.get(XML_LANG, "pt").split("-")[0] == "pt"]
        summary = "\n\n".join(" ".join("".join(a.itertext()).split()) for a in abstracts).strip() or None
        if summary and len(summary) > 50_000:
            raise ValueError("Publisher abstract exceeds the bounded metadata size.")
    elif entry.get("format") == "pdf":
        if (not content.startswith(b"%PDF-") or not fallback
                or doi != "10.36660/abc.20260565"
                or entry.get("corrects_doi") != "10.36660/abc.20250619"):
            raise ValueError("PDF is not the independently verified erratum.")
        readable = _local(root, entry.get("original_text_file", ""))
        if not readable.is_file() or not 500 <= readable.stat().st_size <= 100_000:
            raise ValueError("Verified readable PDF text is missing or exceeds its bound.")
        text_bytes = readable.read_bytes()
        if (_sha(text_bytes) != entry.get("original_text_sha256")
                or len(text_bytes) != entry.get("original_text_bytes")):
            raise ValueError("Readable PDF text SHA256/size mismatch.")
        original_text = text_bytes.decode("utf-8", errors="strict")
        if ("\x00" in original_text or doi not in original_text
                or entry["corrects_doi"] not in original_text
                or original_text.count("\f") != 1
                or entry.get("original_text_extraction", {}).get("pages") != 1):
            raise ValueError("Readable PDF text does not match the reviewed single-page erratum.")
        parsed = {"text": original_text, "title": entry["title"], "authors": [], "language": "pt",
                  "license_url": entry["license_url"],
                  "attribution": f'{entry["title"]}. Fonte: https://doi.org/{doi}. Licença: {entry["license_url"]}.',
                  "coverage": {"source_format": "pdf", "original_text_complete": True,
                               "text_extraction": "pdftotext-layout", "figures": "in_original",
                               "supplements": "not_included"}}
        summary = None
    else:
        raise ValueError("Unsupported original format.")
    return Original(entry, content, parsed, summary, manifest_sha256)


def load_release(root: Path) -> list[Original]:
    root = Path(root)
    manifest_bytes = _local(root, "import-manifest.json").read_bytes()
    manifest = json.loads(manifest_bytes)
    if manifest.get("schema_version") != 1 or manifest.get("release") != RELEASE:
        raise ValueError("Unrecognized curated release.")
    sources = manifest.get("source_manifests", [])
    if {x.get("file") for x in sources} != {"checksums.json", "acquisition.json", "source-recovery.json", "discovery.json"}:
        raise ValueError("Required provenance manifests missing.")
    for source in sources:
        if _sha(_local(root, source["file"]).read_bytes()) != source["sha256"]:
            raise ValueError("Versioned provenance manifest hash mismatch.")
    checks = json.loads(_local(root, "checksums.json").read_bytes())
    checksums = {x["file"]: x for x in checks}
    entries = manifest.get("documents", [])
    if len(entries) != 13 or len({x.get("doi") for x in entries}) != 13:
        raise ValueError("Expected exactly 13 distinct curated originals.")
    if {x.get("file") for x in entries} != set(checksums):
        raise ValueError("Curated manifest does not cover exactly the acquired originals.")
    recovery = json.loads(_local(root, "source-recovery.json").read_bytes())
    return [validate_document(root, entry, checksums, recovery, _sha(manifest_bytes)) for entry in entries]


def protected_reason(asset) -> str | None:
    if asset is None:
        return None
    if asset.original_storage_key or asset.translated_storage_key:
        return "existing_stored_artifact"
    if asset.summary_pt or asset.progress:
        return "existing_processing_history"
    # A source-only failure before any artifact/progress exists is recoverable
    # from the curated offline original. Preserve attempts as acquisition history.
    if asset.attempts and asset.status not in {"blocked_fulltext", "blocked_license"}:
        return "existing_processing_history"
    if asset.status not in SAFE_EMPTY_STATUSES:
        return "protected_state"
    return None


def _identity(original):
    from app.services.scientific_reading import source_identity
    return source_identity(original.metadata["doi"])


def _find_asset(db, key, *, lock=False):
    from app.models.scientific_publication_asset import ScientificPublicationAsset
    query = db.query(ScientificPublicationAsset).filter(ScientificPublicationAsset.source_key == key)
    if lock:
        query = query.with_for_update()
    return query.one_or_none()


def _find_guideline(db, doi):
    from sqlalchemy import func
    from app.models.guideline import Guideline
    rows = db.query(Guideline).filter(func.lower(Guideline.doi) == doi).all()
    return next((row for row in rows if _trusted_metadata(row)), rows[0] if rows else None)


def _trusted_metadata(guideline):
    from app.services.guideline_source_trust import is_trusted_official_guideline
    return is_trusted_official_guideline(guideline)


def _new_asset(db, source):
    from app.models.scientific_publication_asset import ScientificPublicationAsset
    asset = ScientificPublicationAsset(source_key=source["key"], doi=source["doi"], source_url=source["url"],
                                     status="pending", progress={}, coverage={}, attempts=0)
    db.add(asset)
    db.flush()
    return asset


def _new_guideline(db, original):
    from app.models.guideline import Guideline
    from app.services.guideline_source_trust import is_trusted_official_source
    entry = original.metadata
    url = "https://doi.org/" + entry["doi"]
    if not is_trusted_official_source(org="SBC", url=url, doi=entry["doi"]):
        raise ValueError("Curated source failed existing official-source trust.")
    db.add(Guideline(slug="sbc-original-" + entry["doi"].replace("/", "-").replace(".", "-"),
        org="SBC", titulo=original.parsed["title"], ano=entry["year"], doi=entry["doi"], url=url,
        detection_status="detected", source_fingerprint=_sha(("doi|" + entry["doi"]).encode())))


def plan_import(originals, db=None):
    rows = []
    for original in originals:
        if db is None:
            rows.append({"doi": original.metadata["doi"], "action": "create_or_attach_if_no_history",
                         "database_state": "not_inspected", "native_pt": True,
                         "publisher_abstract": bool(original.summary)})
            continue
        source = _identity(original)
        asset = _find_asset(db, source["key"])
        reason = protected_reason(asset)
        guideline = _find_guideline(db, source["doi"])
        if not reason and guideline is not None and not _trusted_metadata(guideline):
            reason = "existing_source_metadata_requires_review"
        rows.append({"doi": source["doi"], "action": "preserve" if reason else ("create" if asset is None else "attach"),
                     "reason": reason, "asset_id": asset.id if asset else None,
                     "create_source_metadata": not reason and guideline is None,
                     "native_pt": True, "publisher_abstract": bool(original.summary)})
    return {"release": RELEASE, "mode": "database_read_only" if db is not None else "offline_validation",
            "count": len(rows), "items": rows, "paid_calls": 0, "clinical_changes": 0}


def _acquire_lock(db):
    from sqlalchemy import text
    if not db.execute(text("SELECT pg_try_advisory_xact_lock(:key)"), {"key": LOCK_ID}).scalar():
        raise RuntimeError("Scientific library worker is busy; no import applied.")


def _store(content, owner_id):
    from app.services import cofre
    root = Path(os.getenv("SCIENTIFIC_PUBLICATION_LIBRARY_DIR", "/scientific-publication-library"))
    return cofre.guardar(content, owner_id, raiz=root)


def apply_import(db, originals):
    """Explicit operator action; validates files before invocation; commits once.

    Caller owns session lifetime. An unsuccessful database commit can leave only
    an unreferenced encrypted object, never publish an incomplete asset. Such an
    orphan is retained for later reconciliation rather than deleting an object
    after an uncertain commit.
    """
    _acquire_lock(db)
    rows = []
    try:
        for original in originals:
            source = _identity(original)
            asset = _find_asset(db, source["key"], lock=True)
            reason = protected_reason(asset)
            if reason:
                rows.append({"doi": source["doi"], "action": "preserved", "reason": reason, "asset_id": asset.id})
                continue
            guideline = _find_guideline(db, source["doi"])
            if guideline is not None and not _trusted_metadata(guideline):
                raise ValueError("Existing source metadata requires review; original cannot be exposed safely.")
            action = "created" if asset is None else "attached"
            if asset is None:
                asset = _new_asset(db, source)
            if guideline is None:
                _new_guideline(db, original)
            entry, parsed = original.metadata, original.parsed
            # Original bytes, immutable, encrypted and authenticated with asset id.
            asset.original_storage_key = _store(original.content, asset.id)
            asset.source_sha256 = entry["sha256"]
            asset.doi, asset.source_url = source["doi"], source["url"]
            asset.license_url, asset.pmcid = parsed["license_url"], entry.get("pmcid")
            asset.status, asset.retry_at = "original_ready", None
            asset.reason = "Original editorial em português; nenhuma tradução por IA solicitada."
            asset.summary_pt = original.summary
            asset.coverage = {**parsed["coverage"], "native_pt": True, "language": "pt",
                              "complete_text": False}
            asset.progress = {
                "title": parsed["title"], "authors": parsed["authors"], "attribution": parsed["attribution"],
                "language": "pt", "summary_origin": "publisher_abstract" if original.summary else None,
                "import_provenance": {"release": RELEASE, "manifest_sha256": original.manifest_sha256,
                    "source_sha256": asset.source_sha256, "license_url": asset.license_url,
                    "source_url": entry["source_url"], "license_evidence": entry["license_evidence"],
                    "imported_at": datetime.now(timezone.utc).isoformat()},
            }
            if entry["format"] == "pdf":
                text_bytes = parsed["text"].encode("utf-8")
                asset.progress = {**asset.progress, "original_text": {
                    "storage_key": _store(text_bytes, asset.id),
                    "sha256": _sha(text_bytes), "source_sha256": asset.source_sha256,
                    "source_format": "pdf", "extraction_method": "pdftotext-layout"}}
            if entry.get("corrects_doi"):
                asset.progress = {**asset.progress, "corrects_doi": entry["corrects_doi"],
                                  "correction_scope": entry.get("correction_scope")}
            rows.append({"doi": source["doi"], "action": action, "asset_id": asset.id,
                         "status": asset.status, "publisher_abstract": bool(original.summary)})
        db.commit()
    except Exception:
        db.rollback()
        raise
    return {"release": RELEASE, "mode": "applied", "count": len(rows), "items": rows,
            "paid_calls": 0, "clinical_changes": 0}
