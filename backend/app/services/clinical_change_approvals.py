"""Clinical changes are immutable proposals until the owner approves exact CAS snapshots."""
import copy
import hashlib
import json
from datetime import datetime, timezone
from types import SimpleNamespace
from fastapi import HTTPException
from sqlalchemy import inspect, or_
from app.core.security import is_owner_admin
from app.models.audit import AuditLog
from app.models.clinical_change_proposal import ClinicalChangeProposal as Proposal
from app.models.content import Document, DocumentRevision
from app.models.guideline import Guideline, GuidelineLink
from app.models.emergency import EmergencyProtocol
from app.models.user import User
from app.models.rag import DocumentChunk, KnowledgeChunk
from app.services import guideline_clinical_update as core
from app.services.clinical_change_authorization import preview_only

IGNORED = {"id", "search_vector", "updated_at", "reviewed_at", "reviewed_by"}
SOURCE_FIELDS = ("id", "slug", "org", "titulo", "ano", "doi", "url", "published_at", "source_fingerprint", "superseded_by_id")


def normalized(value):
    return json.loads(json.dumps(value, ensure_ascii=False, default=str, sort_keys=True))


def digest(value):
    return hashlib.sha256(json.dumps(normalized(value), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def snapshot(row):
    return normalized({c.key: copy.deepcopy(getattr(row, c.key)) for c in inspect(type(row)).column_attrs if c.key not in IGNORED})


def source_identity(row):
    return normalized({key: getattr(row, key) for key in SOURCE_FIELDS})


class PreviewSession:
    clinical_preview_only = True
    def __init__(self, model, target):
        self.model, self.target = model, target
    def get(self, model, item_id):
        if model is not self.model or self.target.id != item_id:
            raise ValueError("Alvo diferente do snapshot de prévia")
        return self.target
    def add(self, row):
        if not isinstance(row, DocumentRevision):
            raise ValueError("Prévia não pode persistir objetos")


def scope_for(db, row):
    result = {"fluxograma": isinstance(row, Document) and row.kind == "fluxograma", "emergency_protocols": []}
    if isinstance(row, Document):
        protocols = db.query(EmergencyProtocol).filter(EmergencyProtocol.published.is_(True), or_(
            EmergencyProtocol.documento_slug == row.slug, EmergencyProtocol.fluxograma_slug == row.slug,
            EmergencyProtocol.relacionados.any(row.slug))).all()
        result["emergency_protocols"] = [{"slug": p.slug, "title": p.titulo,
            "relation": "fluxograma" if p.fluxograma_slug == row.slug else "documento"} for p in protocols]
    return result


def build_proposals(db, guideline, analysis, impacts, *, verified_impacts=(), candidates_count=0):
    if guideline.superseded_by_id is not None:
        raise ValueError("Fonte substituída não pode propor conduta vigente")
    changes = []
    verified_keys = {(i.get("item_type"), int(i.get("item_id") or 0), i.get("override_pt")) for i in verified_impacts}
    from app.services.guideline_clinical_update_runtime import _ORIGINAL_APPLY_OVERRIDE
    for impact in impacts:
        key = (str(impact["item_type"]), int(impact["item_id"]))
        row = core._get_target(db, *key)
        if row is None or not getattr(row, "published", False):
            changes.append({"item_type": "unresolved", "item_id": key[1], "slug": f"unresolved-{key[0]}-{key[1]}",
                "label": impact.get("change_summary_pt") or "Sugestão sem alvo confirmado", "before": None,
                "after": {"suggestion": impact.get("override_pt"), "requested_item_type": key[0]},
                "source_url": impact.get("source_url"), "change_summary_pt": impact.get("change_summary_pt"),
                "impact_scope": {}, "impact": normalized(impact), "can_approve": False,
                "verification_status": "needs_verification"})
            continue
        before = snapshot(row)
        target = SimpleNamespace(id=row.id, **copy.deepcopy(before))
        with preview_only():
            changed = _ORIGINAL_APPLY_OVERRIDE(PreviewSession(type(row), target), guideline, impact, record=False)
        after = {key: normalized(getattr(target, key)) for key in before}
        if not changed or before == after:
            continue
        changes.append({"item_type": key[0], "item_id": row.id, "slug": row.slug,
            "label": core._target_label(key[0], row), "before": before, "after": after,
            "source_url": impact["source_url"], "change_summary_pt": impact["change_summary_pt"],
            "impact_scope": scope_for(db, row), "impact": normalized(impact),
            "can_approve": not impact.get("_validation_issues"),
            "verification_status": "verified" if (key[0], key[1], impact.get("override_pt")) in verified_keys and not impact.get("_validation_issues") else "needs_verification"})
    # A síntese editorial também precisa de revisão; original/licença é outra fila.
    slug = f"corvia-intelligence-{guideline.slug}"[:255]
    existing = db.query(Document).filter(Document.slug == slug).first()
    before = snapshot(existing) if existing else None
    after = copy.deepcopy(before) if before else {
        "slug": slug, "evidence_level": None, "gaps": [], "version": 1,
    }
    body = core._summary_body(guideline, analysis, [])
    after.update({"title": str(analysis.get("title_pt") or guideline.titulo)[:500],
        "kind": core.runtime_document_kind(guideline),
        "theme": str(analysis.get("theme") or guideline.tema or core.TEMA_PADRAO)[:80],
        "summary": str(analysis.get("summary_pt") or "")[:12000], "body_md": body,
        "tags": list(dict.fromkeys(["corvia-intelligence", "atualizacao-clinica", *(analysis.get("topics") or [])]))[:30],
        "source_refs": [x for x in [guideline.url, f"https://doi.org/{guideline.doi}" if guideline.doi else None] if x],
        "source_tier": "A", "review_status": "revisado", "published": True})
    if before and before != after:
        after["version"] = before["version"] + 1
    if before != after:
        changes.append({"item_type": "document_summary", "item_id": existing.id if existing else None,
            "slug": slug, "label": after["title"], "before": before, "after": after,
            "source_url": guideline.url, "change_summary_pt": "Revisar e disponibilizar a síntese editorial desta publicação.",
            "impact_scope": {"fluxograma": False, "emergency_protocols": []}, "can_approve": True, "verification_status": "needs_verification"})
    proposals = []
    for change in changes:
        payload = {"source": source_identity(guideline), "changes": [change], "analysis": normalized(analysis),
                   "candidates_count": candidates_count, "verified_count": len(verified_impacts),
                   "uncertain_count": max(0, len(impacts) - len(verified_impacts))}
        fingerprint = digest(payload)
        proposal = db.query(Proposal).filter_by(guideline_id=guideline.id, fingerprint=fingerprint).first()
        if proposal is None:
            proposal = Proposal(guideline_id=guideline.id, payload=payload, fingerprint=fingerprint, status="pending", version=1)
            db.add(proposal); db.flush()
            db.add(AuditLog(action="clinical_change_proposed", entity="clinical_change_proposal", entity_id=str(proposal.id),
                            detail={"fingerprint": fingerprint, "guideline_id": guideline.id, "changes": 1,
                                    "owner_notification": "pending_clinical_approval_badge"}))
        proposals.append(proposal)
    return proposals


def _owner(user):
    if not is_owner_admin(user):
        raise HTTPException(403, "A aprovação clínica é restrita ao proprietário do CorVIA.")


def _proposal(db, proposal_id):
    proposal = db.query(Proposal).filter_by(id=proposal_id).populate_existing().with_for_update().first()
    if not proposal:
        raise HTTPException(404, "Proposta clínica não encontrada.")
    if digest(proposal.payload) != proposal.fingerprint:
        raise HTTPException(409, "O conteúdo da proposta não corresponde à versão apresentada.")
    return proposal


def _target(db, change, lock=True):
    if change["item_type"] in {"document", "document_summary"}:
        query = db.query(Document).filter(Document.slug == change["slug"])
    else:
        row = core._get_target(db, change["item_type"], change["item_id"])
        if row is None:
            return None
        query = db.query(type(row)).filter(type(row).id == change["item_id"])
    return (query.populate_existing().with_for_update() if lock else query).first()


def _apply_snapshot(db, proposal, change, row, *, reviewer_id):
    if change["item_type"] == "unresolved":
        raise HTTPException(409, "Confirme o alvo clínico antes de produzir uma proposta aplicável.")
    if row is None:
        row = Document(**change["after"])
        db.add(row)
    else:
        if isinstance(row, Document) and row.body_md != change["after"].get("body_md"):
            db.add(DocumentRevision(document_id=row.id, version=row.version, body_md=row.body_md, author_id=reviewer_id))
        allowed = {c.key for c in inspect(type(row)).column_attrs} - IGNORED
        if set(change["after"]) - allowed:
            raise HTTPException(409, "Campo da proposta não é aplicável à versão atual.")
        for key, value in change["after"].items():
            if normalized(getattr(row, key)) != value:
                setattr(row, key, copy.deepcopy(value))
    if isinstance(row, Document):
        row.reviewed_by = reviewer_id
        row.reviewed_at = datetime.now(timezone.utc)
    db.flush()
    if snapshot(row) != change["after"]:
        raise HTTPException(409, "A alteração resultante divergiu da proposta aprovada.")
    # Remove trechos antigos na mesma transação; nenhuma IA cita conduta anterior.
    if isinstance(row, Document):
        db.query(DocumentChunk).filter_by(document_id=row.id).delete(synchronize_session=False)
    else:
        graph_type = {"evidence": "evidencia", "disease": "doenca", "drug": "medicamento", "checklist": "checklist", "triage": "triagem_sintoma"}.get(change["item_type"])
        if graph_type:
            db.query(KnowledgeChunk).filter_by(entity_type=graph_type, entity_id=row.id).delete(synchronize_session=False)
    item_type = "intelligence_document" if change["item_type"] == "document_summary" else change["item_type"]
    link = db.query(GuidelineLink).filter_by(guideline_id=proposal.guideline_id, item_type=item_type, item_id=row.id).first()
    if link is None:
        link = GuidelineLink(guideline_id=proposal.guideline_id, item_type=item_type, item_id=row.id)
        db.add(link)
    link.origem, link.confirmado = "human_approval", True
    link.trecho = json.dumps({**change.get("impact", {}), "proposal_id": proposal.id, "fingerprint": proposal.fingerprint,
                             "reviewer_id": reviewer_id, "mode": "owner_approved_exact_snapshot",
                             "target_label": change["label"], "target_section": change.get("impact", {}).get("target_section", "síntese editorial"),
                             "change_summary_pt": change["change_summary_pt"], "source_url": change["source_url"],
                             "applied_at": datetime.now(timezone.utc).isoformat(), "before": change["before"],
                             "effect_kind": effect_kind(change)}, ensure_ascii=False)
    return row


def effect_kind(change):
    if change["item_type"] == "document_summary":
        return "editorial_summary"
    clinical_fields = {"body_md", "summary", "treatment_summary", "dosing", "ambulatory_flow", "emergency_flow", "notes", "rules", "itens", "indications", "contraindications", "monitoring"}
    if any((change["before"] or {}).get(key) != change["after"].get(key) for key in clinical_fields):
        return "clinical_content"
    return "references_metadata"


def approval_proof(db, proposal):
    if not proposal.reviewer_id or not proposal.reviewed_at:
        return False
    events = db.query(AuditLog).filter_by(action="clinical_change_approved", entity="clinical_change_proposal",
        entity_id=str(proposal.id), user_id=proposal.reviewer_id).all()
    return any((event.detail or {}).get("owner_verified") is True and
               event.detail.get("fingerprint") == proposal.fingerprint and
               event.detail.get("version") == proposal.version for event in events)


def approve(db, proposal_id, expected_version, user):
    _owner(user)
    try:
        proposal = _proposal(db, proposal_id)
        if proposal.status == "approved":
            if not approval_proof(db, proposal):
                raise HTTPException(409, "A proposta não possui comprovante de aprovação do proprietário.")
            return proposal
        if proposal.status != "pending" or proposal.version != expected_version:
            raise HTTPException(409, "A proposta já foi decidida ou sua versão mudou. Recarregue a revisão.")
        guideline = db.query(Guideline).filter_by(id=proposal.guideline_id).populate_existing().with_for_update().one()
        if source_identity(guideline) != proposal.payload["source"]:
            raise HTTPException(409, "A identidade ou vigência da fonte mudou. É necessária nova revisão.")
        targets = []
        for change in sorted(proposal.payload["changes"], key=lambda c: (c["item_type"], c["slug"])):
            if not change.get("can_approve", True):
                raise HTTPException(409, "A sugestão exige confirmar alvo/fonte antes de gerar proposta aplicável.")
            row = _target(db, change)
            if (snapshot(row) if row else None) != change["before"] or (row and change["item_id"] is not None and row.id != change["item_id"]):
                raise HTTPException(409, f"O conteúdo de {change['label']} mudou após a proposta. É necessária nova revisão.")
            targets.append((change, row))
        for change, row in targets:
            _apply_snapshot(db, proposal, change, row, reviewer_id=user.id)
        proposal.status, proposal.reviewer_id = "approved", user.id
        proposal.reviewed_at = datetime.now(timezone.utc); proposal.version += 1
        guideline.detection_status = "revisada"
        db.add(AuditLog(user_id=user.id, action="clinical_change_approved", entity="clinical_change_proposal", entity_id=str(proposal.id),
                        detail={"fingerprint": proposal.fingerprint, "version": proposal.version, "changes": len(targets), "owner_verified": True, "rag_reindex_required": True}))
        db.commit()
        return proposal
    except Exception:
        db.rollback()
        raise


def reject(db, proposal_id, expected_version, reason, user):
    _owner(user)
    try:
        proposal = _proposal(db, proposal_id)
        if proposal.status == "rejected":
            return proposal
        if proposal.status != "pending" or proposal.version != expected_version:
            raise HTTPException(409, "A proposta já foi decidida ou sua versão mudou.")
        reason = reason.strip()
        if not reason:
            raise HTTPException(422, "Informe o motivo da rejeição.")
        proposal.status, proposal.reviewer_id, proposal.rejection_reason = "rejected", user.id, reason[:2000]
        proposal.reviewed_at = datetime.now(timezone.utc); proposal.version += 1
        db.add(AuditLog(user_id=user.id, action="clinical_change_rejected", entity="clinical_change_proposal", entity_id=str(proposal.id),
                        detail={"fingerprint": proposal.fingerprint, "reason": proposal.rejection_reason, "version": proposal.version}))
        db.commit()
        return proposal
    except Exception:
        db.rollback()
        raise


def dump(db, proposal, *, details=True):
    source = proposal.payload["source"]
    reviewer = db.get(User, proposal.reviewer_id) if details and proposal.reviewer_id else None
    events = db.query(AuditLog).filter(AuditLog.entity == "clinical_change_proposal", AuditLog.entity_id == str(proposal.id)).order_by(AuditLog.id).all() if details else []
    return {"id": proposal.id, "version": proposal.version, "status": proposal.status, "created_at": proposal.created_at,
        "verification_status": proposal.payload["changes"][0].get("verification_status", "needs_verification"),
        "can_approve": all(c.get("can_approve", True) for c in proposal.payload["changes"]),
        "blocking_reason": None if all(c.get("can_approve", True) for c in proposal.payload["changes"]) else "A sugestão não possui alvo ou fonte confirmados. Corrija a referência e gere uma nova proposta aplicável; a rejeição continua disponível.",
        "candidates_count": proposal.payload.get("candidates_count", 0), "verified_count": proposal.payload.get("verified_count", 0),
        "uncertain_count": proposal.payload.get("uncertain_count", 0),
        "guideline": {"id": source["id"], "slug": source["slug"], "title": source["titulo"], "doi": source["doi"], "url": source["url"]},
        "proposed_changes": [{**{k: v for k, v in c.items() if k != "impact"},
            "changed_fields": [key for key in c["after"] if (c["before"] or {}).get(key) != c["after"][key]],
            "effect_kind": effect_kind(c),
            "before_text": json.dumps(c["before"], ensure_ascii=False, indent=2) if c["before"] else "Novo documento; ainda não publicado.",
            "after_text": json.dumps(c["after"], ensure_ascii=False, indent=2)} for c in proposal.payload["changes"]] if details else [
                {"item_type": c["item_type"], "label": c["label"], "slug": c["slug"],
                 "change_summary_pt": c["change_summary_pt"], "effect_kind": effect_kind(c),
                 "verification_status": c.get("verification_status", "needs_verification")}
                for c in proposal.payload["changes"]],
        "reviewed_at": proposal.reviewed_at, "reviewer_id": proposal.reviewer_id,
        "reviewer_name": reviewer.full_name if reviewer else None, "rejection_reason": proposal.rejection_reason,
        "audit_events": [{"action": event.action, "at": event.created_at, "reviewer_id": event.user_id,
                          "reason": (event.detail or {}).get("reason")} for event in events]}


def reapply_approved(db):
    """Only exact owner-approved snapshots may survive corpus reconciliation."""
    reapplied, conflicts = 0, []
    try:
        proposals = db.query(Proposal).filter_by(status="approved").order_by(Proposal.id).populate_existing().with_for_update().all()
        valid = []
        for proposal in proposals:
            guideline = db.query(Guideline).filter_by(id=proposal.guideline_id).populate_existing().with_for_update().first()
            if not guideline or source_identity(guideline) != proposal.payload["source"] or digest(proposal.payload) != proposal.fingerprint or not approval_proof(db, proposal):
                conflicts.append(proposal.id); continue
            valid.append(proposal)
        for proposal in valid:
            targets, conflict = [], False
            for change in sorted(proposal.payload["changes"], key=lambda c: (c["item_type"], c["slug"])):
                row = _target(db, change)
                current = snapshot(row) if row else None
                if row and change["item_id"] is not None and row.id != change["item_id"]:
                    conflict = True; break
                if current == change["after"]:
                    continue
                later_states = [c["after"] for p in valid if p.id > proposal.id for c in p.payload["changes"]
                                if c["item_type"] == change["item_type"] and c["slug"] == change["slug"]]
                if current in later_states:
                    continue
                if current != change["before"]:
                    conflict = True; break
                targets.append((change, row))
            if conflict:
                conflicts.append(proposal.id); continue
            for change, row in targets:
                _apply_snapshot(db, proposal, change, row, reviewer_id=proposal.reviewer_id)
                reapplied += 1
            if targets:
                db.add(AuditLog(action="clinical_change_reapplied", entity="clinical_change_proposal", entity_id=str(proposal.id),
                                detail={"fingerprint": proposal.fingerprint, "approved_by": proposal.reviewer_id, "changes": len(targets), "rag_reindex_required": True}))
        db.commit()
        return {"reapplied": reapplied, "missing": 0, "conflicting_proposals": conflicts, "legacy_unreviewed_overrides_applied": 0}
    except Exception:
        db.rollback()
        raise
