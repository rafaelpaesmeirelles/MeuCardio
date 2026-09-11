from types import SimpleNamespace
import pytest

from app.models.guideline import Guideline, GuidelineLink
from app.models.specialty_guide import SpecialtyDisease
from app.services import guideline_clinical_update as clinical
from app.services import guideline_clinical_update_runtime as runtime
from app.services.clinical_text import _safe_http_url, structured_clinical_updates
from app.services import clinical_change_approvals as approvals
from app.models.clinical_change_proposal import ClinicalChangeProposal
from app.core.config import settings


def guideline(slug="esc-2026-heart-failure"):
    return SimpleNamespace(slug=slug, ano=2026, published_at=None)


def test_plain_override_is_marked_and_removable_without_touching_other_updates():
    first = guideline("primeira")
    second = guideline("segunda")
    impact = {"override_pt": "Nova orientação confirmada.", "source_url": "https://doi.org/10.1000/test"}
    block_a = runtime._plain_override(first, impact)
    block_b = runtime._plain_override(second, impact)
    text = f"{block_b}\n\n{block_a}\n\nConteúdo histórico preservado."

    stripped = runtime._strip_plain_override(text, "primeira")

    assert "corvia-intelligence:primeira:plain:start" not in stripped
    assert "corvia-intelligence:segunda:plain:start" in stripped
    assert "Conteúdo histórico preservado." in stripped


def test_already_applied_is_scoped_by_guideline_and_item_type():
    target = SimpleNamespace(
        body_md="<!-- corvia-intelligence:g1:start -->\ntexto\n<!-- corvia-intelligence:g1:end -->",
        summary="",
        treatment_summary="",
        notes={},
        resumo="",
    )
    assert runtime._already_applied(target, "document", "g1") is True
    assert runtime._already_applied(target, "document", "g2") is False


def test_drug_update_is_idempotent_per_guideline():
    target = SimpleNamespace(notes={"corvia_intelligence_updates": [
        {"guideline_slug": "g1", "change": "mudança"}
    ]})
    assert runtime._already_applied(target, "drug", "g1") is True
    assert runtime._already_applied(target, "drug", "g2") is False


def test_only_trusted_scientific_hosts_are_accepted():
    allowed = ["doi.org", "escardio.org", "portal.cardiol.br"]
    assert clinical._trusted_url("https://doi.org/10.1093/example", allowed) is True
    assert clinical._trusted_url("https://www.escardio.org/guidelines/test", allowed) is True
    assert clinical._trusted_url("https://evil.example/escardio.org/guideline", allowed) is False


def test_analysis_schema_requires_explicit_source_support_flag():
    change = clinical.ANALYSIS_SCHEMA["properties"]["key_changes"]["items"]
    assert "explicit_in_source" in change["required"]
    assert "source_url" in change["required"]


def test_runtime_install_replaces_core_helpers_with_idempotent_guards(monkeypatch):
    original_plain = clinical._plain_override
    original_strip = clinical._strip_plain_override
    original_apply = clinical._apply_override
    original_summary = clinical._ensure_summary_document

    runtime.install_runtime_guards()
    assert clinical._plain_override is runtime._plain_override
    assert clinical._strip_plain_override is runtime._strip_plain_override
    assert clinical._apply_override is runtime._guarded_apply_override

    monkeypatch.setattr(clinical, "_plain_override", original_plain)
    monkeypatch.setattr(clinical, "_strip_plain_override", original_strip)
    monkeypatch.setattr(clinical, "_apply_override", original_apply)
    monkeypatch.setattr(clinical, "_ensure_summary_document", original_summary)


def test_owner_approved_disease_update_keeps_definition_and_reapplies_only_exact_snapshot(db, criar_usuario):
    owner, _ = criar_usuario(email=settings.admin_email, role="admin")
    item = SpecialtyDisease(
        slug="doenca-intelligence-sem-contaminacao-teste",
        name="Doença de teste do Intelligence",
        aliases=[], area="cardiologia", category="teste",
        summary="Definição clínica canônica.",
        treatment_summary="Tratamento canônico.",
        review_status="revisado", published=True, version=1,
    )
    source = Guideline(
        slug="diretriz-intelligence-sem-contaminacao-teste",
        org="ESC", titulo="Diretriz de teste", ano=2026,
        url="https://www.escardio.org/teste",
    )
    replacement = Guideline(
        slug="diretriz-intelligence-substituta-teste",
        org="ESC", titulo="Diretriz substituta de teste", ano=2027,
        url="https://www.escardio.org/teste-substituta",
    )
    db.add_all([item, source, replacement])
    db.commit()
    impact = {
        "item_type": "disease", "item_id": item.id,
        "target_section": "definicao",
        "change_summary_pt": "Mudança confirmada e auditável.",
        "override_pt": "Nova orientação que não pertence ao campo definição.",
        "source_url": "https://www.escardio.org/teste",
    }

    try:
        before = approvals.snapshot(item)
        with pytest.raises(PermissionError, match="proprietário"):
            clinical._apply_override(db, source, impact, record=True)
        proposals = approvals.build_proposals(db, source, {}, [impact], verified_impacts=[impact])
        db.commit()
        proposal = next(p for p in proposals if p.payload["changes"][0]["item_type"] == "disease")
        assert proposal.status == "pending" and approvals.snapshot(item) == before
        assert structured_clinical_updates(db, "disease", item.id) == []
        approvals.approve(db, proposal.id, proposal.version, owner)
        db.refresh(item)
        first_version = item.version

        assert item.summary == "Definição clínica canônica."
        assert item.treatment_summary == "Tratamento canônico."
        assert "corvia-intelligence" not in item.summary.casefold()
        link = db.query(GuidelineLink).filter(
            GuidelineLink.guideline_id == source.id,
            GuidelineLink.item_type == "disease",
            GuidelineLink.item_id == item.id,
            GuidelineLink.origem == "human_approval",
            GuidelineLink.confirmado.is_(True),
        ).one()
        assert "Mudança confirmada" in (link.trecho or "")
        updates = structured_clinical_updates(db, "disease", item.id)
        assert len(updates) == 1
        assert updates[0]["change_summary"] == "Mudança confirmada e auditável."
        assert updates[0]["recommendation"] == (
            "Nova orientação que não pertence ao campo definição."
        )
        assert updates[0]["source_url"] == "https://www.escardio.org/teste"
        assert _safe_http_url("javascript:alert(1)") is None
        assert _safe_http_url("https://usuario:senha@example.com") is None

        source.superseded_by_id = replacement.id
        db.commit()
        assert structured_clinical_updates(db, "disease", item.id) == []
        assert runtime._guarded_apply_override(db, source, impact, record=False) is False
        source.superseded_by_id = None
        db.commit()

        # Direct replay is still denied. Only the exact, already-approved
        # before snapshot may be restored after canonical reconciliation.
        with pytest.raises(PermissionError, match="proprietário"):
            runtime._guarded_apply_override(db, source, impact, record=False)
        for field in ("source_refs", "source_urls", "review_note", "version"):
            setattr(item, field, before[field])
        db.commit()
        assert structured_clinical_updates(db, "disease", item.id) == []
        replay = runtime.reapply_confirmed_updates(db)
        assert replay["reapplied"] == 1 and replay["legacy_unreviewed_overrides_applied"] == 0
        db.refresh(item)
        rehydrated_version = item.version
        assert rehydrated_version == first_version
        assert item.source_refs
        assert item.source_urls == ["https://www.escardio.org/teste"]
        assert item.review_note == "CorVIA Intelligence: Mudança confirmada e auditável."
        assert item.summary == "Definição clínica canônica."
        assert runtime.reapply_confirmed_updates(db)["reapplied"] == 0
        db.refresh(item)
        assert item.version == rehydrated_version
        assert len(structured_clinical_updates(db, "disease", item.id)) == 1
    finally:
        db.rollback()
        db.query(ClinicalChangeProposal).filter(ClinicalChangeProposal.guideline_id == source.id).delete()
        db.query(GuidelineLink).filter(GuidelineLink.guideline_id == source.id).delete()
        db.delete(item)
        db.delete(source)
        db.delete(replacement)
        db.commit()
