"""Metadata-only corrections: source proof, identity, loaders and neutral runtime."""
from hashlib import sha256
import json
from types import SimpleNamespace

import pytest

from app.services import editorial_kind_overrides as editorial
from app.services import importer, carregar_estudos, guideline_clinical_update as intelligence
from app.services import clinical_change_approvals as approvals
from app.models.content import Document


@pytest.fixture(autouse=True)
def _banco_limpo():
    """All sessions are local doubles; these tests do not connect to a database."""
    yield


def ledger(tmp_path, entry=None):
    entries = [entry] if entry else []
    claims = {e["evidence_id"]: {
        **{key: e[key] for key in editorial.CLAIM_FIELDS},
        "decision_basis": "confirmed_publication_genre",
        "rationale": "Synthetic fixture with explicit genre evidence",
        "evidence": [{"source_url": "https://example.test/publication", "publication_type": "randomized trial"}],
    } for e in entries}
    evidence_path = tmp_path / "evidence.json"
    evidence_path.write_text(json.dumps({"schema_version": 1, "scope": editorial.SCOPE, "claims": claims}))
    registry_path = tmp_path / "registry.json"
    registry_path.write_text(json.dumps({"schema_version": 1, "scope": editorial.SCOPE,
        "evidence_file": evidence_path.name, "evidence_sha256": sha256(evidence_path.read_bytes()).hexdigest(), "entries": entries}))
    return editorial.load_editorial_registry(registry_path)


def markdown_entry(tmp_path):
    source = tmp_path / "content" / "trial.md"
    source.parent.mkdir(exist_ok=True)
    source.write_text('---\nslug: trial\ntitle: Trial\nkind: diretriz\nreview_status: revisado\npublished: false\n---\nOriginal clinical body.\n')
    return source, {"entity_type": "documento", "slug": "trial", "field": "kind",
        "origin": "canonical_markdown", "old_value": "diretriz", "new_value": "estudo",
        "source_path": "content/trial.md", "source_sha256": sha256(source.read_bytes()).hexdigest(), "evidence_id": "trial-genre"}


def test_exact_source_and_claim_correction_does_not_modify_source(tmp_path):
    source, entry = markdown_entry(tmp_path)
    original = source.read_bytes()
    registry = ledger(tmp_path, entry)
    assert editorial.validate_editorial_sources(tmp_path, registry)["canonical_claims_checked"] == 1
    assert editorial.canonical_editorial_value("documento", "trial", "kind", "diretriz", entry["source_sha256"], registry=registry) == "estudo"
    assert source.read_bytes() == original
    assert editorial.canonical_editorial_value("documento", "unknown", "kind", "diretriz", "0"*64, registry=registry) == "diretriz"


def test_any_source_change_invalidates_correction(tmp_path):
    source, entry = markdown_entry(tmp_path)
    registry = ledger(tmp_path, entry)
    source.write_text(source.read_text().replace('Original clinical body.', 'Changed clinical body.'))
    with pytest.raises(ValueError, match="Stale"):
        editorial.validate_editorial_sources(tmp_path, registry)


@pytest.mark.parametrize("mutation", ["identity", "field", "new_value", "source_sha256", "path"])
def test_unproven_or_unsafe_claim_rejected(tmp_path, mutation):
    _, entry = markdown_entry(tmp_path)
    registry = ledger(tmp_path, entry)
    path = tmp_path / "registry.json"
    data = json.loads(path.read_text())
    claim = data["entries"][0]
    if mutation == "identity": claim["slug"] = "other"
    elif mutation == "field": claim["field"] = "published"
    elif mutation == "new_value": claim["new_value"] = "consenso"
    elif mutation == "source_sha256": claim["source_sha256"] = "0" * 64
    else: claim["source_path"] = "../escape.md"
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError): editorial.load_editorial_registry(path)


def test_evidence_tampering_rejected(tmp_path):
    ledger(tmp_path)
    (tmp_path / "evidence.json").write_text('{}')
    with pytest.raises(ValueError, match="fingerprint"):
        editorial.load_editorial_registry(tmp_path / "registry.json")


def guideline():
    return SimpleNamespace(id=8, slug="verified-source", org="PUBMED", titulo="Original source title",
        ano=2026, doi="10.example/trial", url="https://example.test/trial", source_fingerprint="a"*64,
        tema="Teste", published_at=None, superseded_by_id=None)


def runtime_entry(g):
    identity = editorial.guideline_source_identity(g)
    return {"entity_type": "documento", "slug": f"corvia-intelligence-{g.slug}", "field": "kind",
        "origin": "intelligence_summary", "old_value": "diretriz", "new_value": "estudo",
        "source_identity": identity, "source_sha256": editorial.json_sha256(identity), "evidence_id": "source-genre"}


def test_runtime_requires_exact_source_identity_not_ai_title(tmp_path):
    g = guideline()
    registry = ledger(tmp_path, runtime_entry(g))
    assert editorial.runtime_document_kind(g, registry=registry) == "estudo"
    g.doi = "10.example/other"
    with pytest.raises(ValueError, match="Stale"):
        editorial.runtime_document_kind(g, registry=registry)
    g.slug = "unknown-guideline-sounding-title"
    assert editorial.runtime_document_kind(g, registry=registry) == "documento"


class Query:
    def __init__(self, row): self.row = row
    def filter(self, *args): return self
    def filter_by(self, **kwargs): return self
    def first(self): return self.row


class Session:
    def __init__(self, row=None): self.row, self.added = row, []
    def query(self, model):
        if model.__name__ == "ClinicalChangeProposal": return Query(None)
        return Query(self.row if model.__name__ != "GuidelineLink" else SimpleNamespace(id=1))
    def add(self, row): self.added.append(row)
    def flush(self):
        for row in self.added:
            if getattr(row, "id", None) is None: row.id = 7
    def commit(self): pass
    def rollback(self): pass
    def close(self): pass


def test_importer_refreshes_kind_identical_body_preserving_publication(tmp_path, monkeypatch):
    source, entry = markdown_entry(tmp_path)
    registry = ledger(tmp_path, entry)
    row = SimpleNamespace(id=1, slug="trial", body_md="Original clinical body.", version=8, published=False)
    session = Session(row)
    monkeypatch.setattr(importer, "SessionLocal", lambda: session)
    with editorial.editorial_registry_scope(registry):
        result = importer.import_directory(str(source.parent))
    assert not result.get("falhas")
    assert (row.kind, row.version, row.body_md, row.published) == ("estudo", 8, "Original clinical body.", False)
    assert session.added == []


def test_structured_study_full_record_hash_and_publication_preserved(tmp_path, monkeypatch):
    payload = {"slug": "resuscitation", "title": "Guideline", "study_type": "consenso", "review_status": "revisado", "published": False}
    source = tmp_path / "studies.json"
    source.write_text(json.dumps([payload]))
    entry = {"entity_type": "estudo", "slug": payload["slug"], "field": "study_type", "origin": "canonical_json",
        "old_value": "consenso", "new_value": "diretriz", "source_path": source.name,
        "source_sha256": editorial.json_sha256(payload), "evidence_id": "study-genre"}
    registry = ledger(tmp_path, entry)
    assert editorial.validate_editorial_sources(tmp_path, registry)["canonical_claims_checked"] == 1
    row = SimpleNamespace(id=1, slug=payload["slug"], study_type="consenso", published=False)
    monkeypatch.setattr(carregar_estudos, "SessionLocal", lambda: Session(row))
    with editorial.editorial_registry_scope(registry): carregar_estudos.carregar(str(source))
    assert row.study_type == "diretriz" and row.published is False
    assert json.loads(source.read_text()) == [payload]


@pytest.mark.parametrize("existing", [False, True])
def test_runtime_neutral_kind_is_only_proposed_until_owner_approval(tmp_path, monkeypatch, existing):
    registry = ledger(tmp_path)
    g = guideline()
    row = Document(id=1, slug=f"corvia-intelligence-{g.slug}", kind="diretriz", body_md="same body", version=4, published=False) if existing else None
    session = Session(row)
    monkeypatch.setattr(intelligence, "_summary_body", lambda *args: "same body")
    with editorial.editorial_registry_scope(registry):
        with pytest.raises(PermissionError, match="proprietário"):
            intelligence._ensure_summary_document(session, g, {}, [])
        assert session.added == []
        proposals = approvals.build_proposals(session, g, {}, [])
    assert len(proposals) == 1 and proposals[0].status == "pending"
    change = proposals[0].payload["changes"][0]
    assert change["item_type"] == "document_summary"
    assert change["after"]["kind"] == "documento"
    assert change["after"]["body_md"] == "same body"
    assert not any(isinstance(item, Document) for item in session.added)
    if existing:
        assert row.kind == "diretriz" and row.version == 4 and row.published is False
        assert change["before"] == approvals.snapshot(row)
    else:
        assert change["before"] is None


def test_materialization_check_fails_before_publication(tmp_path):
    _, entry = markdown_entry(tmp_path)
    registry = ledger(tmp_path, entry)
    row = SimpleNamespace(slug="trial", kind="diretriz", published=False)
    with pytest.raises(ValueError, match="not materialized"):
        editorial.validate_materialized_editorial_values(Session(row), registry)
    assert row.published is False
    row.kind = "estudo"
    assert editorial.validate_materialized_editorial_values(Session(row), registry) == 1
