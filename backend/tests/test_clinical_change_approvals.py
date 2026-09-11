from datetime import datetime, timezone
import copy
import pytest
from fastapi import HTTPException
from sqlalchemy import text
from app.core.config import settings
from app.core.db import SessionLocal
from app.core.security import create_access_token
from app.models.user import User
from app.models.content import Document, DocumentRevision
from app.models.guideline import Guideline
from app.models.audit import AuditLog
from app.models.clinical_change_proposal import ClinicalChangeProposal
from app.services import clinical_change_approvals as service
from app.services import guideline_clinical_update as core
from app.services import guideline_clinical_update_runtime as runtime
from _database_guard import assert_isolated_test_database


@pytest.fixture(autouse=True)
def _banco_limpo():
    assert_isolated_test_database(SessionLocal.kw['bind'].url)
    with SessionLocal() as db:
        db.execute(text("TRUNCATE clinical_change_proposals, guidelines, documents, audit_logs, users RESTART IDENTITY CASCADE"))
        db.commit()
    yield


@pytest.fixture
def setup(db):
    owner = User(email=settings.admin_email, full_name="Owner reviewer", role="admin", password_hash="unused", is_active=True)
    other = User(email="other-admin@example.test", full_name="Other admin", role="admin", password_hash="unused", is_active=True)
    db.add_all([owner, other])
    guideline = Guideline(slug="approval-source", org="ESC", titulo="Source for exact changes", ano=2026,
                         doi="10.1000/approval", url="https://www.escardio.org/source", source_fingerprint="1"*64,
                         published_at=datetime(2026, 9, 1, tzinfo=timezone.utc), detection_status="oficial_aprovada")
    docs = [Document(slug=f"approval-doc-{i}", title=f"Protocol {i}", theme="Arritmias", kind="protocolo",
                     summary="Existing summary", body_md="Existing treatment", published=True, review_status="revisado",
                     source_tier="A", source_refs=[], tags=[], gaps=[], version=1) for i in range(2)]
    db.add_all([guideline, *docs]); db.commit()
    analysis = {"title_pt": "Reviewed source summary", "summary_pt": "Source factual synthesis", "theme": "Arritmias",
                "topics": [], "key_changes": [], "limitations": [], "requires_site_update": True}
    impacts = [{"item_type": "document", "item_id": d.id, "target_section": "tratamento", "override_pt": "Proposed treatment correction",
                "source_url": guideline.url, "change_summary_pt": "Change requiring human review", "confidence": "alta",
                "explicit_support": True, "supersedes_existing_guidance": True} for d in docs]
    return owner, other, guideline, docs, analysis, impacts


def make(db, setup):
    owner, other, source, docs, analysis, impacts = setup
    proposals = service.build_proposals(db, source, analysis, impacts, verified_impacts=impacts, candidates_count=2)
    proposal = proposals[0]
    db.commit()
    return proposal


def test_radar_produces_pending_proposal_without_changing_clinical_text_or_publishing_summary(db, setup, monkeypatch):
    owner, other, source, docs, analysis, impacts = setup
    before = [service.snapshot(d) for d in docs]
    monkeypatch.setattr(core, "get_analysis", lambda *_: {**analysis, "source_identity": core._analysis_source_identity(source)})
    monkeypatch.setattr(core, "_candidate_items", lambda *_: [{"item_type": "document"}])
    monkeypatch.setattr(core, "_propose_impacts", lambda *_: (impacts, []))
    monkeypatch.setattr(core, "_verify_impacts", lambda *_: impacts)
    result = core.process_guideline(db, source)
    assert result["applied"] == 0 and result["human_approval_required"] is True
    assert db.query(Document).count() == 2
    assert db.query(ClinicalChangeProposal).count() == 3
    assert all(p.status == "pending" for p in db.query(ClinicalChangeProposal).all())
    assert [service.snapshot(d) for d in docs] == before


def test_owner_approval_applies_exact_snapshots_atomically_and_repeated_request_is_idempotent(db, setup):
    owner, _, _, docs, _, _ = setup
    proposal = make(db, setup)
    service.approve(db, proposal.id, 1, owner)
    assert proposal.status == "approved" and proposal.version == 2
    for change in proposal.payload["changes"]:
        row = db.query(Document).filter_by(slug=change["slug"]).one()
        assert service.snapshot(row) == change["after"]
        assert row.reviewed_by == owner.id
    assert db.query(DocumentRevision).count() == 1
    service.approve(db, proposal.id, 1, owner)
    assert db.query(DocumentRevision).count() == 1
    assert db.query(AuditLog).filter_by(action="clinical_change_approved").count() == 1


def test_target_drift_rejects_whole_bundle_without_partially_applying_first_target(db, setup):
    owner, _, _, docs, _, _ = setup
    proposal = make(db, setup)
    docs[0].body_md = "Newer human correction"; db.commit()
    with pytest.raises(HTTPException) as exc:
        service.approve(db, proposal.id, 1, owner)
    assert exc.value.status_code == 409
    db.refresh(docs[1]); db.refresh(proposal)
    assert docs[1].body_md == "Existing treatment"
    assert db.query(Document).count() == 2 and db.query(DocumentRevision).count() == 0
    assert proposal.status == "pending"


def test_source_drift_and_non_owner_admin_cannot_authorize(db, setup):
    owner, other, source, docs, _, _ = setup
    proposal = make(db, setup)
    with pytest.raises(HTTPException) as exc:
        service.approve(db, proposal.id, 1, other)
    assert exc.value.status_code == 403
    source.doi = "10.1000/replaced"; db.commit()
    with pytest.raises(HTTPException) as exc:
        service.approve(db, proposal.id, 1, owner)
    assert exc.value.status_code == 409
    assert db.query(DocumentRevision).count() == 0


def test_rejection_does_not_change_clinical_content_or_publish_summary(db, setup):
    owner, _, _, docs, _, _ = setup
    proposal = make(db, setup)
    before = [service.snapshot(d) for d in docs]
    service.reject(db, proposal.id, 1, "Insufficient evidence", owner)
    assert proposal.status == "rejected" and proposal.reviewer_id == owner.id
    assert [service.snapshot(d) for d in docs] == before
    assert db.query(Document).count() == 2
    with pytest.raises(HTTPException) as exc:
        service.approve(db, proposal.id, 2, owner)
    assert exc.value.status_code == 409


def test_legacy_original_runtime_and_record_false_cannot_bypass_approval(db, setup):
    _, _, source, docs, analysis, impacts = setup
    for function in (core._apply_override, runtime._ORIGINAL_APPLY_OVERRIDE, runtime._guarded_apply_override):
        with pytest.raises(PermissionError): function(db, source, impacts[0], record=False)
    with pytest.raises(PermissionError): runtime._ensure_summary_published(db, source, analysis, impacts)
    assert runtime.reapply_confirmed_updates(db)["legacy_unreviewed_overrides_applied"] == 0
    assert docs[0].body_md == "Existing treatment"


def test_api_owner_authorization_version_conflict_and_read_only_listing(db, client, setup):
    owner, other, _, _, _, _ = setup
    proposal = make(db, setup)
    def headers(user): return {"Authorization": "Bearer " + create_access_token(user.email, scope="app")}
    response = client.get("/api/clinical-change-approvals", headers=headers(other))
    assert response.status_code == 403
    response = client.get("/api/clinical-change-approvals?status=pending&limit=50&offset=0", headers=headers(owner))
    assert response.status_code == 200 and response.json()["total"] == 3
    item = response.json()["items"][0]
    assert item["version"] == 1 and "before_text" not in item["proposed_changes"][0]
    detail = client.get(f"/api/clinical-change-approvals/{proposal.id}", headers=headers(owner)).json()
    assert detail["proposed_changes"][0]["before_text"]
    response = client.post(f"/api/clinical-change-approvals/{proposal.id}/approve", json={"expected_version": 99}, headers=headers(owner))
    assert response.status_code == 409
    db.refresh(proposal); assert proposal.status == "pending"


def test_each_clinical_item_and_editorial_summary_are_independently_approved(db, setup):
    owner, _, _, docs, _, _ = setup
    proposal = make(db, setup)
    service.approve(db, proposal.id, 1, owner)
    assert docs[0].body_md != "Existing treatment" and docs[1].body_md == "Existing treatment"
    assert db.query(Document).count() == 2
    synthesis = db.query(ClinicalChangeProposal).filter(ClinicalChangeProposal.id != proposal.id).all()[-1]
    assert synthesis.payload["changes"][0]["item_type"] == "document_summary"
    assert "Proposed treatment correction" not in synthesis.payload["changes"][0]["after"]["body_md"]
    service.approve(db, synthesis.id, 1, owner)
    row = db.query(Document).filter_by(slug=synthesis.payload["changes"][0]["slug"]).one()
    assert service.snapshot(row) == synthesis.payload["changes"][0]["after"]


def test_stale_identity_map_cannot_overwrite_concurrent_human_correction(db, setup):
    owner, _, _, docs, _, _ = setup
    proposal = make(db, setup)
    original = docs[0].body_md
    with SessionLocal() as other:
        row = other.get(Document, docs[0].id)
        row.body_md = "Concurrent correction"; other.commit()
    assert docs[0].body_md == original
    with pytest.raises(HTTPException) as exc:
        service.approve(db, proposal.id, 1, owner)
    assert exc.value.status_code == 409
    db.refresh(docs[0]); assert docs[0].body_md == "Concurrent correction"


def test_reapply_requires_owner_audit_proof_and_never_retargets_recreated_document(db, setup):
    owner, _, _, docs, _, _ = setup
    proposal = make(db, setup)
    proposal.status = "approved"; proposal.reviewer_id = owner.id; proposal.reviewed_at = datetime.now(timezone.utc)
    db.commit()
    assert proposal.id in service.reapply_approved(db)["conflicting_proposals"]
    assert docs[0].body_md == "Existing treatment"
    proposal.status = "pending"; db.commit()
    service.approve(db, proposal.id, 1, owner)
    change = proposal.payload["changes"][0]
    db.delete(docs[0]); db.flush()
    recreated = Document(**change["before"]); db.add(recreated); db.commit()
    assert recreated.id != change["item_id"]
    assert proposal.id in service.reapply_approved(db)["conflicting_proposals"]
    assert recreated.body_md == "Existing treatment"


def test_reapply_exact_previously_approved_change_is_audited_and_idempotent(db, setup):
    owner, _, _, docs, _, _ = setup
    proposal = make(db, setup)
    service.approve(db, proposal.id, 1, owner)
    for key, value in proposal.payload["changes"][0]["before"].items():
        setattr(docs[0], key, value)
    db.commit()
    assert service.reapply_approved(db)["reapplied"] == 1
    assert service.snapshot(docs[0]) == proposal.payload["changes"][0]["after"]
    assert db.query(AuditLog).filter_by(action="clinical_change_reapplied").count() == 1
    assert service.reapply_approved(db)["reapplied"] == 0


def test_inconclusive_model_verification_still_creates_each_owner_review_item(db, setup, monkeypatch):
    _, _, source, docs, analysis, impacts = setup
    monkeypatch.setattr(core, "get_analysis", lambda *_: {**analysis, "source_identity": core._analysis_source_identity(source)})
    monkeypatch.setattr(core, "_candidate_items", lambda *_: [{"item_type": "document"}])
    monkeypatch.setattr(core, "_propose_impacts", lambda *_: (impacts, []))
    monkeypatch.setattr(core, "_verify_impacts", lambda *_: (_ for _ in ()).throw(RuntimeError("verification unavailable")))
    result = core.process_guideline(db, source)
    assert result["uncertain"] == 2 and result["applied"] == 0
    assert len(result["approval_proposal_ids"]) == 3
    assert all(p.payload["changes"][0]["verification_status"] == "needs_verification" for p in db.query(ClinicalChangeProposal).all())
    assert docs[0].body_md == "Existing treatment"


def test_approval_invalidates_old_chunks_but_new_body_remains_in_lexical_context(db, setup):
    from app.models.rag import DocumentChunk
    from app.services.rag_multi import buscar_lexico_multi
    owner, _, _, docs, _, _ = setup
    proposal = make(db, setup)
    db.add(DocumentChunk(document_id=docs[0].id, ordem=0, titulo_secao="Old treatment", conteudo="Existing treatment",
                         embedding=[0.01] * settings.embedding_dim, tokens_aprox=10, content_hash="0"*64, embedding_model=settings.openai_embedding_model))
    db.commit()
    service.approve(db, proposal.id, 1, owner)
    assert db.query(DocumentChunk).filter_by(document_id=docs[0].id).count() == 0
    rows = buscar_lexico_multi(db, "Proposed treatment correction", 10)
    found = next(row for row in rows if row["slug"] == docs[0].slug)
    assert "Proposed treatment correction" in found["conteudo"]


def test_failure_after_target_write_rolls_back_body_revision_link_and_decision(db, setup, monkeypatch):
    owner, _, _, docs, _, _ = setup
    proposal = make(db, setup)
    apply = service._apply_snapshot
    def fail_after_write(*args, **kwargs):
        apply(*args, **kwargs)
        raise RuntimeError("failed after mutation")
    monkeypatch.setattr(service, "_apply_snapshot", fail_after_write)
    with pytest.raises(RuntimeError): service.approve(db, proposal.id, 1, owner)
    db.refresh(docs[0]); db.refresh(proposal)
    assert docs[0].body_md == "Existing treatment" and proposal.status == "pending"
    assert db.query(DocumentRevision).count() == 0


def test_legacy_analysis_remains_readable_but_is_reanalyzed_before_new_proposals(db, setup, monkeypatch):
    import json
    from app.models.guideline import GuidelineLink
    _, _, source, docs, analysis, impacts = setup
    db.add(GuidelineLink(guideline_id=source.id, item_type="analysis", item_id=0, origem="intelligence", confirmado=True,
                         trecho=json.dumps({**analysis, "summary_pt": "Legacy source summary"})))
    db.commit()
    assert core.get_analysis(db, source)["summary_pt"] == "Legacy source summary"
    calls = []
    monkeypatch.setattr(core, "_analyze_source", lambda *_: calls.append(1) or analysis)
    monkeypatch.setattr(core, "_candidate_items", lambda *_: [])
    monkeypatch.setattr(core, "_propose_impacts", lambda *_: ([], []))
    monkeypatch.setattr(core, "_verify_impacts", lambda *_: [])
    core.process_guideline(db, source)
    assert calls == [1]
    saved = core.get_analysis(db, source)
    assert saved["source_identity"] == core._analysis_source_identity(source)
    assert saved["source_identity_sha256"] and saved["source_bound_at"]


def test_source_change_during_analysis_discards_result_without_new_proposal(db, setup, monkeypatch):
    _, _, source, _, analysis, _ = setup
    source_id = source.id
    def analyze(_):
        with SessionLocal() as other:
            row = other.get(Guideline, source_id); row.doi = "10.1000/changed-during-analysis"; other.commit()
        return analysis
    monkeypatch.setattr(core, "_analyze_source", analyze)
    with pytest.raises(ValueError, match="fonte mudou"):
        core.process_guideline(db, source)
    assert db.query(ClinicalChangeProposal).count() == 0
    assert core.get_analysis(db, source) is None


def test_source_change_during_verification_discards_proposal_and_does_not_rebind_cached_analysis(db, setup, monkeypatch):
    _, _, source, _, analysis, impacts = setup
    source_id = source.id
    original_identity = core._analysis_source_identity(source)
    monkeypatch.setattr(core, "_analyze_source", lambda *_: analysis)
    monkeypatch.setattr(core, "_candidate_items", lambda *_: [{"item_type": "document"}])
    monkeypatch.setattr(core, "_propose_impacts", lambda *_: (impacts, []))
    def verify(*_):
        with SessionLocal() as other:
            row = other.get(Guideline, source_id); row.url = "https://www.escardio.org/replaced-during-verification"; other.commit()
        return impacts
    monkeypatch.setattr(core, "_verify_impacts", verify)
    with pytest.raises(ValueError, match="fonte mudou"):
        core.process_guideline(db, source)
    assert db.query(ClinicalChangeProposal).count() == 0
    assert core.get_analysis(db, source)["source_identity"] == original_identity
    assert core._analysis_source_identity(source) != original_identity
