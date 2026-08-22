"""Cadastro identificável de paciente e núcleo do Prontuário Eletrônico.

`PatientProfile` permanece separado do `Patient` anonimizado do Round. Os
atendimentos (`ClinicalEncounter`) usam o mesmo paciente identificável, mas
cifram em repouso o conteúdo clínico. Atendimento finalizado é imutável;
correção posterior nasce como adendo separado.

Problemas, alergias e medicações em uso compõem o resumo clínico longitudinal.
O conteúdo de cada item também é cifrado; quando deixa de ser vigente, o item
é inativado e preservado no histórico em vez de ser apagado.

Todo endpoint é escopado por `owner_id == user.id`: médico A nunca confirma a
existência do paciente/atendimento do médico B. Leituras e mutações geram
AuditLog sem copiar conteúdo clínico para o log.
"""
from __future__ import annotations

import json
from datetime import date, datetime, timezone
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user
from app.models.audit import AuditLog
from app.models.clinical_docs import Appointment
from app.models.patient_profile import PatientProfile
from app.models.prontuario import ClinicalEncounter, PatientClinicalItem
from app.services import cofre
from app.services.clinical_ownership import encounter_for_user, patient_profile_for_user
from app.services.patient_profile_service import snapshot_de
from app.services.professional_profile import normalize_search_text

router = APIRouter(prefix="/api/pacientes", tags=["pacientes"])


class EnderecoIn(BaseModel):
    logradouro: str | None = None
    numero: str | None = None
    complemento: str | None = None
    bairro: str | None = None
    cidade: str | None = None
    uf: str | None = None
    cep: str | None = None

    def esta_vazio(self) -> bool:
        return not any((
            self.logradouro, self.numero, self.complemento,
            self.bairro, self.cidade, self.uf, self.cep,
        ))


class PatientProfileIn(BaseModel):
    full_name: str
    cpf: str | None = None
    birth_date: date | None = None
    sex: str | None = None
    phone: str | None = None
    email: str | None = None
    endereco: EnderecoIn | None = None


class ClinicalItemIn(BaseModel):
    kind: Literal["problema", "alergia", "medicacao"]
    name: str
    details: str | None = None
    source_encounter_id: int | None = None


class EncounterIn(BaseModel):
    encounter_type: str = "consulta"
    appointment_id: int | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None
    chief_complaint: str | None = None
    anamnesis: str | None = None
    physical_exam: str | None = None
    assessment: str | None = None
    plan: str | None = None
    vital_signs: dict = {}
    amendment_of_id: int | None = None
    amendment_reason: str | None = None


class EncounterPatch(BaseModel):
    encounter_type: str | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None
    chief_complaint: str | None = None
    anamnesis: str | None = None
    physical_exam: str | None = None
    assessment: str | None = None
    plan: str | None = None
    vital_signs: dict | None = None
    status: str | None = None


def _dump(perfil: PatientProfile) -> dict:
    snap = snapshot_de(perfil)
    return {
        "id": perfil.id,
        "full_name": snap["full_name"],
        "cpf": snap["cpf"],
        "birth_date": snap["birth_date"],
        "sex": snap["sex"],
        "phone": snap["phone"],
        "email": snap["email"],
        "endereco": snap["endereco"],
        "created_at": perfil.created_at,
        "updated_at": perfil.updated_at,
    }


def _gravar_campos(perfil: PatientProfile, dados: PatientProfileIn) -> None:
    """`perfil.id` precisa existir antes de cifrar (é o AAD do cofre)."""
    perfil.full_name_cifrado = cofre.cifrar_campo(dados.full_name.strip(), perfil.id)
    perfil.cpf_cifrado = cofre.cifrar_campo(dados.cpf.strip(), perfil.id) if dados.cpf and dados.cpf.strip() else None
    perfil.birth_date = dados.birth_date
    perfil.sex = (dados.sex or "").strip()[:1] or None
    perfil.phone_cifrado = cofre.cifrar_campo(dados.phone.strip(), perfil.id) if dados.phone and dados.phone.strip() else None
    perfil.email_cifrado = cofre.cifrar_campo(dados.email.strip(), perfil.id) if dados.email and dados.email.strip() else None
    if dados.endereco and not dados.endereco.esta_vazio():
        perfil.endereco_cifrado = cofre.cifrar_campo(
            json.dumps(dados.endereco.model_dump(), ensure_ascii=False), perfil.id,
        )
    else:
        perfil.endereco_cifrado = None


def _cifrar_texto(valor: str | None, encounter_id: int) -> bytes | None:
    if valor is None:
        return None
    return cofre.cifrar_campo(valor, encounter_id)


def _decifrar_texto(valor: bytes | None, encounter_id: int) -> str | None:
    return cofre.decifrar_campo(valor, encounter_id) if valor is not None else None


def _gravar_conteudo(encounter: ClinicalEncounter, dados: EncounterIn | EncounterPatch) -> None:
    campos = {
        "chief_complaint": "chief_complaint_cifrado",
        "anamnesis": "anamnesis_cifrado",
        "physical_exam": "physical_exam_cifrado",
        "assessment": "assessment_cifrado",
        "plan": "plan_cifrado",
    }
    presentes = dados.model_fields_set
    for origem, destino in campos.items():
        if origem in presentes:
            setattr(encounter, destino, _cifrar_texto(getattr(dados, origem), encounter.id))
    if "vital_signs" in presentes:
        sinais = getattr(dados, "vital_signs")
        encounter.vital_signs_cifrado = (
            cofre.cifrar_campo(json.dumps(sinais or {}, ensure_ascii=False), encounter.id)
            if sinais is not None else None
        )


def _dump_encounter(encounter: ClinicalEncounter) -> dict:
    sinais: dict = {}
    if encounter.vital_signs_cifrado is not None:
        sinais = json.loads(cofre.decifrar_campo(encounter.vital_signs_cifrado, encounter.id))
    return {
        "id": encounter.id,
        "patient_profile_id": encounter.patient_profile_id,
        "appointment_id": encounter.appointment_id,
        "author_id": encounter.author_id,
        "encounter_type": encounter.encounter_type,
        "status": encounter.status,
        "started_at": encounter.started_at,
        "ended_at": encounter.ended_at,
        "finalized_at": encounter.finalized_at,
        "amendment_of_id": encounter.amendment_of_id,
        "amendment_reason": _decifrar_texto(encounter.amendment_reason_cifrado, encounter.id),
        "chief_complaint": _decifrar_texto(encounter.chief_complaint_cifrado, encounter.id),
        "anamnesis": _decifrar_texto(encounter.anamnesis_cifrado, encounter.id),
        "physical_exam": _decifrar_texto(encounter.physical_exam_cifrado, encounter.id),
        "assessment": _decifrar_texto(encounter.assessment_cifrado, encounter.id),
        "plan": _decifrar_texto(encounter.plan_cifrado, encounter.id),
        "vital_signs": sinais,
        "created_at": encounter.created_at,
        "updated_at": encounter.updated_at,
    }


def _auditar(db: Session, user_id: int, action: str, encounter: ClinicalEncounter) -> None:
    db.add(AuditLog(
        user_id=user_id,
        action=action,
        entity="clinical_encounter",
        entity_id=str(encounter.id),
        detail={
            "patient_profile_id": encounter.patient_profile_id,
            "appointment_id": encounter.appointment_id,
            "status": encounter.status,
            "amendment_of_id": encounter.amendment_of_id,
        },
    ))


def _item_for_user(pid: int, item_id: int, db: Session, user) -> PatientClinicalItem:
    patient_profile_for_user(pid, db, user)
    item = db.get(PatientClinicalItem, item_id)
    if not item or item.owner_id != user.id or item.patient_profile_id != pid:
        raise HTTPException(status_code=404, detail="Item clínico não encontrado.")
    return item


def _dump_item(item: PatientClinicalItem) -> dict:
    payload = json.loads(cofre.decifrar_campo(item.payload_cifrado, item.id))
    return {
        "id": item.id,
        "patient_profile_id": item.patient_profile_id,
        "kind": item.kind,
        "is_active": item.is_active,
        "name": payload.get("name") or "",
        "details": payload.get("details"),
        "source_encounter_id": item.source_encounter_id,
        "created_at": item.created_at,
        "ended_at": item.ended_at,
    }


def _auditar_item(db: Session, user_id: int, action: str, item: PatientClinicalItem) -> None:
    db.add(AuditLog(
        user_id=user_id,
        action=action,
        entity="patient_clinical_item",
        entity_id=str(item.id),
        detail={
            "patient_profile_id": item.patient_profile_id,
            "kind": item.kind,
            "is_active": item.is_active,
            "source_encounter_id": item.source_encounter_id,
        },
    ))


@router.get("")
def listar_pacientes(
    busca: str | None = Query(None, max_length=120),
    db: Session = Depends(get_db), user=Depends(current_user),
):
    rows = (
        db.query(PatientProfile)
        .filter(PatientProfile.owner_id == user.id)
        .order_by(PatientProfile.created_at.desc())
        .all()
    )
    alvo = normalize_search_text(busca)
    resultado = []
    for perfil in rows:
        dump = _dump(perfil)
        if alvo and alvo not in normalize_search_text(dump["full_name"]):
            continue
        resultado.append(dump)
    return resultado


@router.post("", status_code=201)
def criar_paciente(dados: PatientProfileIn, db: Session = Depends(get_db), user=Depends(current_user)):
    if not dados.full_name.strip():
        raise HTTPException(status_code=422, detail="Informe o nome do paciente.")
    perfil = PatientProfile(owner_id=user.id, full_name_cifrado=b"")
    db.add(perfil)
    db.flush()
    _gravar_campos(perfil, dados)
    db.commit()
    db.refresh(perfil)
    return _dump(perfil)


@router.get("/{pid}")
def obter_paciente(pid: int, db: Session = Depends(get_db), user=Depends(current_user)):
    perfil = patient_profile_for_user(pid, db, user)
    return _dump(perfil)


@router.put("/{pid}")
def editar_paciente(pid: int, dados: PatientProfileIn, db: Session = Depends(get_db), user=Depends(current_user)):
    if not dados.full_name.strip():
        raise HTTPException(status_code=422, detail="Informe o nome do paciente.")
    perfil = patient_profile_for_user(pid, db, user)
    _gravar_campos(perfil, dados)
    db.commit()
    db.refresh(perfil)
    return _dump(perfil)


@router.delete("/{pid}", status_code=204)
def apagar_paciente(pid: int, db: Session = Depends(get_db), user=Depends(current_user)):
    perfil = patient_profile_for_user(pid, db, user)
    existe_prontuario = (
        db.query(ClinicalEncounter.id)
        .filter(ClinicalEncounter.owner_id == user.id, ClinicalEncounter.patient_profile_id == perfil.id)
        .first()
        or db.query(PatientClinicalItem.id)
        .filter(PatientClinicalItem.owner_id == user.id, PatientClinicalItem.patient_profile_id == perfil.id)
        .first()
    )
    if existe_prontuario:
        raise HTTPException(
            status_code=409,
            detail="Paciente possui prontuário clínico e não pode ser apagado fisicamente.",
        )
    db.delete(perfil)
    db.commit()


@router.get("/{pid}/resumo-clinico")
def listar_resumo_clinico(
    pid: int,
    incluir_inativos: bool = False,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    patient_profile_for_user(pid, db, user)
    query = db.query(PatientClinicalItem).filter(
        PatientClinicalItem.owner_id == user.id,
        PatientClinicalItem.patient_profile_id == pid,
    )
    if not incluir_inativos:
        query = query.filter(PatientClinicalItem.is_active.is_(True))
    rows = query.order_by(PatientClinicalItem.created_at.desc(), PatientClinicalItem.id.desc()).all()
    db.add(AuditLog(
        user_id=user.id,
        action="list_patient_clinical_summary",
        entity="patient_profile",
        entity_id=str(pid),
        detail={"count": len(rows), "include_inactive": incluir_inativos},
    ))
    db.commit()
    return [_dump_item(row) for row in rows]


@router.post("/{pid}/resumo-clinico", status_code=201)
def criar_item_resumo(
    pid: int,
    dados: ClinicalItemIn,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    patient_profile_for_user(pid, db, user)
    name = dados.name.strip()
    details = (dados.details or "").strip() or None
    if not name:
        raise HTTPException(status_code=422, detail="Informe o item clínico.")
    if len(name) > 240:
        raise HTTPException(status_code=422, detail="Item clínico excede 240 caracteres.")
    if details and len(details) > 3000:
        raise HTTPException(status_code=422, detail="Detalhes excedem 3000 caracteres.")

    if dados.source_encounter_id is not None:
        source = encounter_for_user(dados.source_encounter_id, db, user)
        if source.patient_profile_id != pid:
            raise HTTPException(status_code=404, detail="Atendimento de origem não encontrado.")

    item = PatientClinicalItem(
        owner_id=user.id,
        patient_profile_id=pid,
        source_encounter_id=dados.source_encounter_id,
        kind=dados.kind,
        is_active=True,
        payload_cifrado=b"",
    )
    db.add(item)
    db.flush()
    item.payload_cifrado = cofre.cifrar_campo(
        json.dumps({"name": name, "details": details}, ensure_ascii=False), item.id,
    )
    _auditar_item(db, user.id, "create_patient_clinical_item", item)
    db.commit()
    db.refresh(item)
    return _dump_item(item)


@router.post("/{pid}/resumo-clinico/{item_id}/inativar")
def inativar_item_resumo(
    pid: int,
    item_id: int,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    item = _item_for_user(pid, item_id, db, user)
    if item.is_active:
        item.is_active = False
        item.ended_at = datetime.now(timezone.utc)
        _auditar_item(db, user.id, "inactivate_patient_clinical_item", item)
        db.commit()
        db.refresh(item)
    return _dump_item(item)


@router.get("/{pid}/atendimentos")
def listar_atendimentos(pid: int, db: Session = Depends(get_db), user=Depends(current_user)):
    patient_profile_for_user(pid, db, user)
    rows = (
        db.query(ClinicalEncounter)
        .filter(ClinicalEncounter.owner_id == user.id, ClinicalEncounter.patient_profile_id == pid)
        .order_by(ClinicalEncounter.created_at.desc(), ClinicalEncounter.id.desc())
        .all()
    )
    db.add(AuditLog(
        user_id=user.id,
        action="list_clinical_encounters",
        entity="patient_profile",
        entity_id=str(pid),
        detail={"count": len(rows)},
    ))
    db.commit()
    return [_dump_encounter(row) for row in rows]


@router.post("/{pid}/atendimentos", status_code=201)
def criar_atendimento(
    pid: int,
    dados: EncounterIn,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    patient_profile_for_user(pid, db, user)

    tipo = (dados.encounter_type or "consulta").strip()[:40] or "consulta"
    amendment_of_id = dados.amendment_of_id
    if amendment_of_id is not None:
        original = encounter_for_user(amendment_of_id, db, user)
        if original.patient_profile_id != pid:
            raise HTTPException(status_code=404, detail="Atendimento não encontrado.")
        if original.status not in {"finalized", "amended"}:
            raise HTTPException(status_code=409, detail="Adendo só pode referenciar atendimento finalizado.")
        if not (dados.amendment_reason or "").strip():
            raise HTTPException(status_code=422, detail="Informe o motivo do adendo.")
        tipo = "adendo"

    if dados.appointment_id is not None:
        if amendment_of_id is not None:
            raise HTTPException(status_code=422, detail="Adendo não reutiliza o agendamento original.")
        appointment = db.get(Appointment, dados.appointment_id)
        if not appointment or appointment.owner_id != user.id:
            raise HTTPException(status_code=404, detail="Agendamento não encontrado.")
        duplicado = (
            db.query(ClinicalEncounter.id)
            .filter(
                ClinicalEncounter.owner_id == user.id,
                ClinicalEncounter.appointment_id == dados.appointment_id,
            )
            .first()
        )
        if duplicado:
            raise HTTPException(status_code=409, detail="Este agendamento já possui atendimento iniciado.")

    agora = datetime.now(timezone.utc)
    encounter = ClinicalEncounter(
        owner_id=user.id,
        patient_profile_id=pid,
        appointment_id=dados.appointment_id,
        author_id=user.id,
        encounter_type=tipo,
        status="draft",
        started_at=dados.started_at or agora,
        ended_at=dados.ended_at,
        amendment_of_id=amendment_of_id,
    )
    db.add(encounter)
    db.flush()
    _gravar_conteudo(encounter, dados)
    if amendment_of_id is not None:
        encounter.amendment_reason_cifrado = _cifrar_texto(dados.amendment_reason, encounter.id)
    _auditar(db, user.id, "create_clinical_encounter", encounter)
    db.commit()
    db.refresh(encounter)
    return _dump_encounter(encounter)


@router.get("/{pid}/atendimentos/{encounter_id}")
def obter_atendimento(
    pid: int,
    encounter_id: int,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    patient_profile_for_user(pid, db, user)
    encounter = encounter_for_user(encounter_id, db, user)
    if encounter.patient_profile_id != pid:
        raise HTTPException(status_code=404, detail="Atendimento não encontrado.")
    _auditar(db, user.id, "read_clinical_encounter", encounter)
    db.commit()
    return _dump_encounter(encounter)


@router.patch("/{pid}/atendimentos/{encounter_id}")
def editar_atendimento(
    pid: int,
    encounter_id: int,
    dados: EncounterPatch,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    patient_profile_for_user(pid, db, user)
    encounter = encounter_for_user(encounter_id, db, user)
    if encounter.patient_profile_id != pid:
        raise HTTPException(status_code=404, detail="Atendimento não encontrado.")
    if encounter.status in {"finalized", "amended", "cancelled"}:
        raise HTTPException(
            status_code=409,
            detail="Atendimento finalizado é imutável. Registre um adendo para corrigir o histórico.",
        )

    presentes = dados.model_fields_set
    if "status" in presentes:
        if dados.status not in {"draft", "in_progress"}:
            raise HTTPException(status_code=422, detail="Use a ação de finalizar para concluir o atendimento.")
        encounter.status = dados.status
    if "encounter_type" in presentes and dados.encounter_type is not None:
        encounter.encounter_type = dados.encounter_type.strip()[:40] or encounter.encounter_type
    if "started_at" in presentes:
        encounter.started_at = dados.started_at
    if "ended_at" in presentes:
        encounter.ended_at = dados.ended_at

    _gravar_conteudo(encounter, dados)
    _auditar(db, user.id, "update_clinical_encounter", encounter)
    db.commit()
    db.refresh(encounter)
    return _dump_encounter(encounter)


@router.post("/{pid}/atendimentos/{encounter_id}/finalizar")
def finalizar_atendimento(
    pid: int,
    encounter_id: int,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    patient_profile_for_user(pid, db, user)
    encounter = encounter_for_user(encounter_id, db, user)
    if encounter.patient_profile_id != pid:
        raise HTTPException(status_code=404, detail="Atendimento não encontrado.")
    if encounter.status in {"finalized", "amended"}:
        return _dump_encounter(encounter)
    if encounter.status == "cancelled":
        raise HTTPException(status_code=409, detail="Atendimento cancelado não pode ser finalizado.")

    agora = datetime.now(timezone.utc)
    encounter.status = "finalized"
    encounter.finalized_at = agora
    encounter.ended_at = encounter.ended_at or agora
    _auditar(db, user.id, "finalize_clinical_encounter", encounter)
    db.commit()
    db.refresh(encounter)
    return _dump_encounter(encounter)
