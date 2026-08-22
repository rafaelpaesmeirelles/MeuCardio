"""Artefatos produzidos no contexto de um atendimento do Prontuário.

O vínculo é explícito e não altera o documento/prescrição original. Assim,
as regras legais, snapshots e assinatura continuam nos módulos canônicos.
"""
import re
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user
from app.models.audit import AuditLog
from app.models.clinical_docs import GeneratedDocument, Prescription
from app.models.encounter_artifact import EncounterArtifact
from app.models.receituario import PrescriptionDocument, PrescriptionRecipient
from app.services import cofre
from app.services.clinical_ownership import encounter_for_user, patient_profile_for_user
from app.services.patient_profile_service import snapshot_de
from app.services.professional_profile import normalize_search_text

router = APIRouter(prefix="/api/pacientes", tags=["prontuario"])


class ArtefatoIn(BaseModel):
    tipo: Literal["prescricao", "documento"]
    artifact_id: int = Field(gt=0)


def _encounter(pid: int, eid: int, db: Session, user, *, mutacao: bool = False):
    patient_profile_for_user(pid, db, user)
    encounter = encounter_for_user(eid, db, user)
    if encounter.patient_profile_id != pid:
        raise HTTPException(status_code=404, detail="Atendimento não encontrado.")
    if mutacao and encounter.status == "finalized":
        raise HTTPException(
            status_code=409,
            detail="Atendimento finalizado é histórico; novos artefatos devem pertencer a um novo atendimento ou adendo.",
        )
    return encounter


def _validar_destinatario_prescricao(prescricao_id: int, pid: int, db: Session, user) -> None:
    """Prova que o destinatário cifrado corresponde ao PatientProfile do Encounter.

    É comparação determinística de identidade, nunca busca/fuzzy matching: nome
    normalizado precisa coincidir e, se o cadastro tiver CPF, o documento da
    receita também precisa coincidir dígito a dígito.
    """
    perfil = patient_profile_for_user(pid, db, user)
    snap = snapshot_de(perfil)
    destinatario = (
        db.query(PrescriptionRecipient)
        .filter(PrescriptionRecipient.prescription_id == prescricao_id)
        .first()
    )
    if not destinatario:
        raise HTTPException(status_code=409, detail="Receita sem destinatário identificável não pode ser vinculada ao prontuário.")

    nome = cofre.decifrar_campo(destinatario.nome_cifrado, prescricao_id)
    if normalize_search_text(nome) != normalize_search_text(snap.get("full_name")):
        raise HTTPException(status_code=409, detail="Destinatário da receita não corresponde ao paciente deste atendimento.")

    cpf = re.sub(r"\D", "", snap.get("cpf") or "")
    if cpf:
        documento = (
            cofre.decifrar_campo(destinatario.documento_cifrado, prescricao_id)
            if destinatario.documento_cifrado else ""
        )
        if re.sub(r"\D", "", documento) != cpf:
            raise HTTPException(status_code=409, detail="Documento do destinatário não corresponde ao paciente deste atendimento.")


def _validar_artefato(dados: ArtefatoIn, pid: int, db: Session, user):
    if dados.tipo == "prescricao":
        row = db.get(Prescription, dados.artifact_id)
        if not row or row.created_by != user.id:
            raise HTTPException(status_code=404, detail="Prescrição não encontrada.")
        _validar_destinatario_prescricao(row.id, pid, db, user)
        return row

    row = db.get(GeneratedDocument, dados.artifact_id)
    if not row or row.created_by != user.id:
        raise HTTPException(status_code=404, detail="Documento não encontrado.")
    if row.patient_profile_id != pid:
        raise HTTPException(status_code=409, detail="Documento não corresponde ao paciente deste atendimento.")
    return row


def _dump(link: EncounterArtifact, db: Session) -> dict:
    if link.artifact_type == "prescricao":
        presc = db.get(Prescription, link.artifact_id)
        docs = (
            db.query(PrescriptionDocument)
            .filter(PrescriptionDocument.prescription_id == link.artifact_id)
            .order_by(PrescriptionDocument.id.asc())
            .all()
        )
        return {
            "id": link.id,
            "tipo": "prescricao",
            "artifact_id": link.artifact_id,
            "created_at": presc.created_at if presc else link.created_at,
            "titulo": "Prescrição",
            "detalhes": [
                {"id": d.id, "tipo": d.tipo_codigo, "status": d.status}
                for d in docs
            ],
        }

    doc = db.get(GeneratedDocument, link.artifact_id)
    return {
        "id": link.id,
        "tipo": "documento",
        "artifact_id": link.artifact_id,
        "created_at": doc.created_at if doc else link.created_at,
        "titulo": doc.title if doc else "Documento indisponível",
        "doc_type": doc.doc_type if doc else None,
    }


@router.get("/{pid}/atendimentos/{eid}/artefatos")
def listar_artefatos(
    pid: int, eid: int, db: Session = Depends(get_db), user=Depends(current_user),
):
    _encounter(pid, eid, db, user)
    rows = (
        db.query(EncounterArtifact)
        .filter(
            EncounterArtifact.owner_id == user.id,
            EncounterArtifact.encounter_id == eid,
        )
        .order_by(EncounterArtifact.created_at.asc(), EncounterArtifact.id.asc())
        .all()
    )
    return [_dump(row, db) for row in rows]


@router.post("/{pid}/atendimentos/{eid}/artefatos", status_code=201)
def vincular_artefato(
    pid: int, eid: int, dados: ArtefatoIn,
    db: Session = Depends(get_db), user=Depends(current_user),
):
    _encounter(pid, eid, db, user, mutacao=True)
    _validar_artefato(dados, pid, db, user)

    existente = (
        db.query(EncounterArtifact)
        .filter(
            EncounterArtifact.owner_id == user.id,
            EncounterArtifact.artifact_type == dados.tipo,
            EncounterArtifact.artifact_id == dados.artifact_id,
        )
        .first()
    )
    if existente:
        if existente.encounter_id != eid:
            raise HTTPException(status_code=409, detail="Artefato já pertence a outro atendimento.")
        return _dump(existente, db)

    link = EncounterArtifact(
        owner_id=user.id,
        encounter_id=eid,
        artifact_type=dados.tipo,
        artifact_id=dados.artifact_id,
    )
    db.add(link)
    db.flush()
    db.add(AuditLog(
        user_id=user.id,
        action="link_encounter_artifact",
        entity="clinical_encounter",
        entity_id=str(eid),
        detail={"artifact_type": dados.tipo, "artifact_id": dados.artifact_id},
    ))
    db.commit()
    db.refresh(link)
    return _dump(link, db)
