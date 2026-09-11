"""Schema 2 reconciles an exact approved snapshot without transient publication."""
import json
from pathlib import Path

import pytest
from sqlalchemy import text

from app.commands import reconcile_content as rc
from app.models.content import Document
from app.services import knowledge_graph as kg
from app.services.scientific_loader_safety import publication_quarantine, enforce_safe_publication
from _editorial_fixtures import write_empty_editorial_registry


def document(slug, published=True):
    return Document(slug=slug, title=slug, kind="modulo", theme="Teste",
                    body_md="Texto aprovado", review_status="revisado", published=published)


@pytest.fixture
def documents_only(db, monkeypatch):
    db.execute(text("TRUNCATE documents RESTART IDENTITY CASCADE"))
    db.commit()
    monkeypatch.setattr(rc, "FRONTS", {"documentos": {
        "model": Document, "minimum": 1, "path": "/content", "loader": None}})
    return db


def test_quarantine_wins_all_legacy_flags_and_archives_aliases(documents_only):
    db = documents_only
    rows = [document(s) for s in ("approved", "excluded", "removed", "corvia-intelligence-runtime")]
    db.add_all(rows)
    db.commit()
    excluded = rows[1]
    node = kg.registrar_entidade(db, entity_type="documento", canonical_id=excluded.id,
                                slug="old-alias", title="Alias")
    db.commit()
    canonical = {"documentos": {"approved", "excluded"}}
    rc._synchronize_publication(db, canonical, publish_reviewed=True,
        approved_slugs=canonical, publication_intents={"documentos": {"approved": False, "excluded": True}},
        full_corpus_authorized_slugs=canonical, quarantined_slugs={"documentos": {"excluded"}}, commit=False)
    kg.arquivar_entidades_de_conteudo_despublicado(db, commit=False)
    db.commit()
    assert {r.slug: r.published for r in db.query(Document)} == {
        "approved": True, "excluded": False, "removed": False, "corvia-intelligence-runtime": True}
    db.refresh(node)
    assert node.status == "arquivado"
    inventory = rc._database_inventory(db, canonical, include_published_slugs=True)
    assert inventory["fronts"]["documentos"]["published_slugs"] == ["approved"]
    assert inventory["runtime_managed_total"] == 1


def test_loader_scope_blocks_legacy_true_and_resets_after_failure():
    row = document("excluded")
    with pytest.raises(RuntimeError):
        with publication_quarantine({"documentos": {"excluded"}}, {"documentos": Document}):
            enforce_safe_publication(row, {"slug": "excluded", "published": True}, is_new=False)
            assert row.published is False
            raise RuntimeError("loader failure")
    row.published = True
    enforce_safe_publication(row, {"slug": "excluded", "published": True}, is_new=False)
    assert row.published is True


def test_snapshot_freezes_sources_and_materializes_evidence_assets(tmp_path, monkeypatch):
    monkeypatch.setattr(rc, "REPOSITORY_ROOT", tmp_path)
    monkeypatch.setattr(rc, "FRONTS", {"documentos": {"path": "/content"}})
    content = tmp_path / "content"
    content.mkdir()
    doc = content / "approved.md"
    doc.write_text("---\nslug: approved\ntitle: Approved\nkind: modulo\nreview_status: revisado\n---\nApproved bytes")
    asset = tmp_path / "galeria" / "image.png"
    asset.parent.mkdir()
    asset.write_bytes(b"approved-image")
    evidence = tmp_path / "docs" / "evidence.json"
    evidence.parent.mkdir()
    evidence.write_text(json.dumps({"references": [{"path": "galeria/image.png"}]}))
    auth = tmp_path / "authorization.json"
    auth.write_text(json.dumps({"schema_version": 2, "provenance": {
        "documentos": {"approved": {"evidence_path": "docs/evidence.json"}}}}))
    prepared = {"documentos": (content, {"approved"}, {"approved": None})}
    with rc._immutable_release_sources(prepared, auth) as (snapshot, copied_auth, root):
        doc.write_text("Modified live bytes")
        asset.write_bytes(b"modified-image")
        assert (snapshot["documentos"][0] / "approved.md").read_text().endswith("Approved bytes")
        assert (root / "galeria/image.png").read_bytes() == b"approved-image"
        assert not (root / "galeria/image.png").is_symlink()
        assert copied_auth.is_file()
    assert not root.exists()


@pytest.mark.parametrize("missing", [False, True])
def test_schema2_missing_or_without_publish_stops_before_database(tmp_path, monkeypatch, missing):
    path = tmp_path / "authorization.json"
    if not missing:
        path.write_text('{"schema_version": 2}')
    monkeypatch.setattr(rc, "FRONTS", {})
    monkeypatch.setattr(rc, "SessionLocal", lambda: pytest.fail("Database opened before gate"))
    with pytest.raises(RuntimeError, match="não encontrada|exige --publish-reviewed"):
        rc.reconcile(authorization_path=path)


def test_graph_snapshot_never_falls_back_and_scope_resets(tmp_path, monkeypatch):
    live = tmp_path / "live.json"
    live.write_text("[]")
    root = tmp_path / "snapshot"
    root.mkdir()
    observed = []
    def fake_backfill(db, *, commit):
        observed.append(kg._graph_source(Path("/doencas/relacoes-explicitas.json"), live))
        return {}
    monkeypatch.setattr(kg, "_backfill_mesmo_tema", fake_backfill)
    with pytest.raises(RuntimeError, match="ausente no snapshot"):
        kg.backfill_mesmo_tema(None, source_root=root)
    frozen = root / "doencas/relacoes-explicitas.json"
    frozen.parent.mkdir()
    frozen.write_text("[]")
    kg.backfill_mesmo_tema(None, source_root=root)
    assert observed == [frozen]
    assert kg._SOURCE_ROOT.get() is None


def test_native_commits_cannot_reopen_frozen_records_on_later_failure(documents_only, tmp_path, monkeypatch):
    db = documents_only
    db.add_all([document("approved"), document("excluded")])
    db.commit()
    # This snapshot contains no metadata corrections. Validate a real empty,
    # hash-bound ledger instead of loading unrelated production evidence.
    write_empty_editorial_registry(tmp_path)
    source = tmp_path / "content"
    source.mkdir()
    for slug in ("approved", "excluded"):
        (source / f"{slug}.md").write_text(
            f"---\nslug: {slug}\ntitle: {slug}\nkind: modulo\ntheme: Teste\nreview_status: revisado\npublished: true\n---\nFrozen {slug}")
    canonical = {"documentos": {"approved", "excluded"}}
    metadata = {"schema_version": 2, "approved": {"documentos": ["approved"]},
                "quarantined": {"documentos": ["excluded"]}}
    monkeypatch.setattr(rc, "_load_full_corpus_authorization", lambda *a, **k: ({"documentos": {"approved"}}, metadata))
    monkeypatch.setattr(rc, "_load_editorial_approvals", lambda: canonical)
    monkeypatch.setattr(rc, "_validate_editorial_approvals", lambda *a, **k: {})
    original_load = rc._load_front
    def failing_load(*a, **k):
        result = original_load(*a, **k)
        db.expire_all()
        assert all(not r.published for r in db.query(Document))
        raise RuntimeError("failure after native loader commit")
    monkeypatch.setattr(rc, "_load_front", failing_load)
    with pytest.raises(RuntimeError, match="after native loader commit"):
        rc._reconcile_prepared({"documentos": (source, canonical["documentos"], {
            "approved": True, "excluded": True})}, publish_reviewed=True,
            allow_partial=True, authorization_path=tmp_path / "unused", evidence_root=tmp_path)
    db.expire_all()
    assert all(not r.published for r in db.query(Document))
    assert db.query(Document).filter_by(slug="approved").one().body_md == "Frozen approved"


def test_preserved_command_rejects_snapshot_before_publication(documents_only, monkeypatch):
    from app.commands import publish_preserved_content as preserved
    monkeypatch.setattr(preserved, "FRONTS", {})
    monkeypatch.setattr(preserved, "_load_full_corpus_authorization", lambda *a: ({}, {"schema_version": 2}))
    monkeypatch.setattr(preserved, "_synchronize_publication", lambda *a, **k: pytest.fail("publication bypass"))
    with pytest.raises(RuntimeError, match="carregar os bytes autorizados"):
        preserved.publish_preserved_reviewed(documents_only)


def test_gallery_uses_frozen_assets_and_keeps_canonical_file_path(db, tmp_path, monkeypatch):
    from app.services import carregar_galeria as gallery
    from app.models.gallery import GalleryImage
    live = tmp_path / "live-gallery"
    live.mkdir()
    frozen = tmp_path / "snapshot-gallery"
    frozen.mkdir()
    (frozen / "approved.png").write_bytes(b"image")
    metadata = frozen / "metadados.json"
    metadata.write_text(json.dumps([{
        "slug": "schema2-frozen-gallery", "title": "Fixture", "modality": "ECG",
        "theme": "Teste", "findings": "Fixture only", "file_path": "approved.png",
        "source_name": "Test", "source_url": "https://example.test/image",
        "license": "CC0", "attribution": "Test", "review_status": "revisado"}]))
    monkeypatch.setattr(gallery, "GALERIA_DIR", live)
    config = {"loader": "carregar_galeria"}
    result, _, _ = rc._load_front("galeria", config, prepared=(
        metadata, {"schema2-frozen-gallery"}, {"schema2-frozen-gallery": None}))
    assert result["sem_arquivo"] == []
    assert result["asset_root"] == str(frozen)
    row = db.query(GalleryImage).filter_by(slug="schema2-frozen-gallery").one()
    assert row.file_path == "approved.png"
    assert not row.published
    db.delete(row)
    db.commit()
