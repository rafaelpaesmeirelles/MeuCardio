"""Cadastro identificável de paciente e núcleo do Prontuário Eletrônico.

`PatientProfile` permanece separado do `Patient` anonimizado do Round. Os
atendimentos (`ClinicalEncounter`) usam o mesmo paciente identificável, mas
cifram em repouso o conteúdo clínico. Atendimento finalizado é imutável;
correção posterior nasce como adendo separado.

Problemas, alergias e medicações em uso compõem o resumo clínico longitudinal.
O conteúdo de cada item também é cifrado; quando deixa de ser vigente, o item
é inativado e preservado no histórico em vez de ser apagado.

Resultados de exames pertencem ao mesmo paciente canônico, mas não ao catálogo
científico `LabTest`. O catálogo pode ser referenciado; o resultado efetivo é
imutável, cifrado e corrigido somente por novo registro encadeado ao anterior.

Todo endpoint é escopado por `owner_id == user.id`: médico A nunca confirma a
existência do paciente/atendimento do médico B. Leituras e mutações geram
AuditLog sem copiar conteúdo clínico para o log.
"""
from __future__ import annotations

import json
from datetime import date, datetime, time, timedelta, timezone
from typing import Literal
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Response, UploadFile
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.core.security import current_user
from app.core.uploads import UploadRejected, safe_filename, validate_file
from app.models.audit import AuditLog
from app.models.clinical_docs import Appointment
from app.models.lab_test import LabTest
from app.models.patient_profile import PatientProfile
from app.models.prontuario import (
    ClinicalEncounter, PatientClinicalAISuggestion, PatientClinicalItem,
    PatientECGRecord, PatientExamResult,
)
from app.models.user import User
from app.services import cofre
from app.services.clinical_ownership import encounter_for_user, patient_profile_for_user
from app.services.ia import ecg_assist
from app.services.patient_profile_service import snapshot_de
from app.services.professional_profile import normalize_search_text

router = APIRouter(prefix="/api/pacientes", tags=["pacientes"])
ECG_SUGGESTION_PREVIEW_LIMIT = 20


def _operational_day_utc_bounds(now_utc: datetime | None = None) -> tuple[datetime, datetime]:
    """Retorna o dia civil operacional convertido em limites UTC."""
    current = now_utc or datetime.now(timezone.utc)
    zone = ZoneInfo(settings.fuso_operacao)
    local_day = current.astimezone(zone).date()
    start_local = datetime.combine(local_day, time.min, tzinfo=zone)
    end_local = datetime.combine(local_day + timedelta(days=1), time.min, tzinfo=zone)
    return start_local.astimezone(timezone.utc), end_local.astimezone(timezone.utc)


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


class ExamResultIn(BaseModel):
    exam_kind: Literal["laboratorial", "metodo_grafico", "imagem", "outro"] = "laboratorial"
    exam_name: str
    performed_at: datetime | None = None
    structured_result: str | None = None
    report_text: str | None = None
    # Compatibilidade transitória com o contrato inicial desta branch.
    result: str | None = None
    unit: str | None = None
    reference_range: str | None = None
    notes: str | None = None
    source: str | None = None
    lab_test_id: int | None = None
    source_encounter_id: int | None = None


class ExamCorrectionIn(ExamResultIn):
    correction_reason: str


class AISuggestionReviewIn(BaseModel):
    decision: Literal["accept", "reject"]
    final_interpretation: str | None = None
    review_note: str | None = None


class AIAnalysisRequestIn(BaseModel):
    # Literal True torna a transferência ao provedor uma ação explícita, não
    # um default silencioso de upload.
    confirm_external_processing: Literal[True]


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


def _exam_result_for_user(pid: int, result_id: int, db: Session, user) -> PatientExamResult:
    patient_profile_for_user(pid, db, user)
    row = db.get(PatientExamResult, result_id)
    if not row or row.owner_id != user.id or row.patient_profile_id != pid:
        raise HTTPException(status_code=404, detail="Resultado de exame não encontrado.")
    return row


def _dump_exam_result(
    row: PatientExamResult,
    db: Session,
    corrected_by_id: int | None = None,
) -> dict:
    payload = json.loads(cofre.decifrar_campo(row.payload_cifrado, row.id))
    catalog = db.get(LabTest, row.lab_test_id) if row.lab_test_id else None
    ai_origin = db.query(PatientClinicalAISuggestion).filter(
        PatientClinicalAISuggestion.owner_id == row.owner_id,
        PatientClinicalAISuggestion.patient_profile_id == row.patient_profile_id,
        PatientClinicalAISuggestion.accepted_result_id == row.id,
    ).first()
    structured_result = payload.get("structured_result")
    report_text = payload.get("report_text")
    # Registros produzidos pelos primeiros commits do lote continuam legíveis.
    legacy_result = payload.get("result")
    if structured_result is None and report_text is None and legacy_result is not None:
        structured_result = legacy_result
    return {
        "id": row.id,
        "patient_profile_id": row.patient_profile_id,
        "author_id": row.author_id,
        "source_encounter_id": row.source_encounter_id,
        "lab_test_id": row.lab_test_id,
        "lab_test_slug": catalog.slug if catalog else None,
        "lab_test_name": catalog.name if catalog else None,
        "correction_of_id": row.correction_of_id,
        "corrected_by_id": corrected_by_id,
        "is_superseded": corrected_by_id is not None,
        "correction_reason": (
            cofre.decifrar_campo(row.correction_reason_cifrado, row.id)
            if row.correction_reason_cifrado else None
        ),
        "exam_kind": row.exam_kind,
        "performed_at": row.performed_at,
        "exam_name": payload.get("exam_name") or "",
        "structured_result": structured_result,
        "report_text": report_text,
        "result": structured_result or report_text or "",
        "unit": payload.get("unit"),
        "reference_range": payload.get("reference_range"),
        "notes": payload.get("notes"),
        "source": payload.get("source"),
        "ecg_record_id": ai_origin.ecg_record_id if ai_origin else None,
        "ai_suggestion_id": ai_origin.id if ai_origin else None,
        "ai_review_status": ai_origin.status if ai_origin else None,
        "created_at": row.created_at,
    }


def _auditar_resultado(db: Session, user_id: int, action: str, row: PatientExamResult) -> None:
    db.add(AuditLog(
        user_id=user_id,
        action=action,
        entity="patient_exam_result",
        entity_id=str(row.id),
        detail={
            "patient_profile_id": row.patient_profile_id,
            "source_encounter_id": row.source_encounter_id,
            "lab_test_id": row.lab_test_id,
            "correction_of_id": row.correction_of_id,
            "exam_kind": row.exam_kind,
        },
    ))


def _normalizar_resultado(dados: ExamResultIn) -> dict:
    exam_name = dados.exam_name.strip()
    structured_result = (dados.structured_result or dados.result or "").strip() or None
    report_text = (dados.report_text or "").strip() or None
    unit = (dados.unit or "").strip() or None
    reference_range = (dados.reference_range or "").strip() or None
    notes = (dados.notes or "").strip() or None
    source = (dados.source or "").strip() or None

    if not exam_name:
        raise HTTPException(status_code=422, detail="Informe o exame.")
    if not structured_result and not report_text:
        raise HTTPException(status_code=422, detail="Informe um valor estruturado ou um laudo textual.")
    limites = (
        (exam_name, 240, "Nome do exame"),
        (structured_result, 500, "Resultado estruturado"),
        (report_text, 12000, "Laudo textual"),
        (unit, 80, "Unidade"),
        (reference_range, 500, "Referência"),
        (notes, 4000, "Observações"),
        (source, 240, "Origem"),
    )
    for valor, limite, rotulo in limites:
        if valor and len(valor) > limite:
            raise HTTPException(status_code=422, detail=f"{rotulo} excede {limite} caracteres.")
    return {
        "exam_name": exam_name,
        "structured_result": structured_result,
        "report_text": report_text,
        "unit": unit,
        "reference_range": reference_range,
        "notes": notes,
        "source": source,
    }


def _preparar_resultado(
    pid: int,
    dados: ExamResultIn,
    db: Session,
    user,
    *,
    correction_of: PatientExamResult | None = None,
    correction_reason: str | None = None,
) -> PatientExamResult:
    """Valida e inclui um resultado na transação atual, sem fazer commit.

    A separação permite que a aceitação de sugestão IA e a criação do fato
    médico aconteçam atomicamente; nunca pode sobrar resultado aceito sem a
    respectiva decisão de revisão registrada.
    """
    patient_profile_for_user(pid, db, user)
    payload = _normalizar_resultado(dados)

    if dados.source_encounter_id is not None:
        source_encounter = encounter_for_user(dados.source_encounter_id, db, user)
        if source_encounter.patient_profile_id != pid:
            raise HTTPException(status_code=404, detail="Atendimento de origem não encontrado.")

    if dados.lab_test_id is not None:
        catalog = db.get(LabTest, dados.lab_test_id)
        if not catalog or not catalog.published:
            raise HTTPException(status_code=404, detail="Exame do catálogo CorVIA não encontrado.")

    if correction_of is not None:
        if not correction_reason:
            raise HTTPException(status_code=422, detail="Informe o motivo da correção do resultado.")
        if len(correction_reason) > 2000:
            raise HTTPException(status_code=422, detail="Motivo da correção excede 2000 caracteres.")
        already_corrected = db.query(PatientExamResult.id).filter(
            PatientExamResult.owner_id == user.id,
            PatientExamResult.patient_profile_id == pid,
            PatientExamResult.correction_of_id == correction_of.id,
        ).first()
        if already_corrected:
            raise HTTPException(
                status_code=409,
                detail="Este registro já foi substituído. Corrija o registro mais recente da cadeia.",
            )

    performed_at = dados.performed_at or datetime.now(timezone.utc)
    if performed_at.tzinfo is None:
        raise HTTPException(status_code=422, detail="A data clínica deve informar o fuso horário.")
    row = PatientExamResult(
        owner_id=user.id,
        patient_profile_id=pid,
        author_id=user.id,
        source_encounter_id=dados.source_encounter_id,
        lab_test_id=dados.lab_test_id,
        correction_of_id=correction_of.id if correction_of else None,
        exam_kind=dados.exam_kind,
        performed_at=performed_at,
        payload_cifrado=b"",
        correction_reason_cifrado=None,
    )
    db.add(row)
    db.flush()
    row.payload_cifrado = cofre.cifrar_campo(json.dumps(payload, ensure_ascii=False), row.id)
    if correction_reason:
        row.correction_reason_cifrado = cofre.cifrar_campo(correction_reason, row.id)
    _auditar_resultado(
        db,
        user.id,
        "correct_patient_exam_result" if correction_of else "create_patient_exam_result",
        row,
    )
    return row


def _criar_resultado(
    pid: int,
    dados: ExamResultIn,
    db: Session,
    user,
    *,
    correction_of: PatientExamResult | None = None,
    correction_reason: str | None = None,
) -> PatientExamResult:
    try:
        row = _preparar_resultado(
            pid,
            dados,
            db,
            user,
            correction_of=correction_of,
            correction_reason=correction_reason,
        )
        db.commit()
    except IntegrityError:
        db.rollback()
        if correction_of is not None and db.query(PatientExamResult.id).filter(
            PatientExamResult.owner_id == user.id,
            PatientExamResult.patient_profile_id == pid,
            PatientExamResult.correction_of_id == correction_of.id,
        ).first():
            raise HTTPException(
                status_code=409,
                detail="Este registro já foi substituído. Corrija o registro mais recente da cadeia.",
            )
        raise
    db.refresh(row)
    return row


def _ecg_for_user(pid: int, ecg_id: int, db: Session, user) -> PatientECGRecord:
    patient_profile_for_user(pid, db, user)
    row = db.get(PatientECGRecord, ecg_id)
    if not row or row.owner_id != user.id or row.patient_profile_id != pid:
        raise HTTPException(status_code=404, detail="ECG não encontrado.")
    return row


def _suggestion_for_user(
    pid: int, ecg_id: int, suggestion_id: int, db: Session, user,
) -> PatientClinicalAISuggestion:
    _ecg_for_user(pid, ecg_id, db, user)
    row = db.get(PatientClinicalAISuggestion, suggestion_id)
    if (
        not row
        or row.owner_id != user.id
        or row.patient_profile_id != pid
        or row.ecg_record_id != ecg_id
    ):
        raise HTTPException(status_code=404, detail="Sugestão clínica não encontrada.")
    return row


def _dump_ai_suggestion(row: PatientClinicalAISuggestion) -> dict:
    payload = json.loads(cofre.decifrar_campo(row.payload_cifrado, row.id))
    return {
        "id": row.id,
        "mode": row.mode,
        "status": row.status,
        "payload": payload,
        "provider": row.provider,
        "model": row.model,
        "prompt_version": row.prompt_version,
        "created_at": row.created_at,
        "reviewed_by": row.reviewed_by,
        "reviewed_at": row.reviewed_at,
        "review_note": (
            cofre.decifrar_campo(row.review_note_cifrado, row.id)
            if row.review_note_cifrado else None
        ),
        "accepted_result_id": row.accepted_result_id,
    }


def _dump_ecg(row: PatientECGRecord, db: Session) -> dict:
    suggestions = (
        db.query(PatientClinicalAISuggestion)
        .filter(
            PatientClinicalAISuggestion.owner_id == row.owner_id,
            PatientClinicalAISuggestion.patient_profile_id == row.patient_profile_id,
            PatientClinicalAISuggestion.ecg_record_id == row.id,
        )
        .order_by(PatientClinicalAISuggestion.created_at.desc(), PatientClinicalAISuggestion.id.desc())
        .limit(ECG_SUGGESTION_PREVIEW_LIMIT)
        .all()
    )
    return {
        "id": row.id,
        "patient_profile_id": row.patient_profile_id,
        "author_id": row.author_id,
        "source_encounter_id": row.source_encounter_id,
        "performed_at": row.performed_at,
        "original_name": cofre.decifrar_campo(row.original_name_cifrado, row.id),
        "media_type": row.media_type,
        "size_bytes": row.size_bytes,
        "created_at": row.created_at,
        "suggestions": [_dump_ai_suggestion(item) for item in suggestions],
    }


def _audit_ecg(db: Session, user_id: int, action: str, row: PatientECGRecord, **extra) -> None:
    db.add(AuditLog(
        user_id=user_id,
        action=action,
        entity="patient_ecg_record",
        entity_id=str(row.id),
        detail={
            "patient_profile_id": row.patient_profile_id,
            "source_encounter_id": row.source_encounter_id,
            **extra,
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
        or db.query(PatientExamResult.id)
        .filter(PatientExamResult.owner_id == user.id, PatientExamResult.patient_profile_id == perfil.id)
        .first()
        or db.query(PatientECGRecord.id)
        .filter(PatientECGRecord.owner_id == user.id, PatientECGRecord.patient_profile_id == perfil.id)
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


@router.get("/{pid}/resultados")
def listar_resultados(
    pid: int,
    limite: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    patient_profile_for_user(pid, db, user)
    rows = (
        db.query(PatientExamResult)
        .filter(PatientExamResult.owner_id == user.id, PatientExamResult.patient_profile_id == pid)
        .order_by(PatientExamResult.performed_at.desc(), PatientExamResult.id.desc())
        .limit(limite)
        .all()
    )
    corrected_by = dict(
        db.query(PatientExamResult.correction_of_id, PatientExamResult.id)
        .filter(
            PatientExamResult.owner_id == user.id,
            PatientExamResult.patient_profile_id == pid,
            PatientExamResult.correction_of_id.is_not(None),
        )
        .all()
    )
    db.add(AuditLog(
        user_id=user.id,
        action="list_patient_exam_results",
        entity="patient_profile",
        entity_id=str(pid),
        detail={"count": len(rows)},
    ))
    db.commit()
    return [_dump_exam_result(row, db, corrected_by.get(row.id)) for row in rows]


@router.post("/{pid}/resultados", status_code=201)
def criar_resultado(
    pid: int,
    dados: ExamResultIn,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    row = _criar_resultado(pid, dados, db, user)
    return _dump_exam_result(row, db)


@router.get("/{pid}/resultados/{result_id}")
def obter_resultado(
    pid: int,
    result_id: int,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    row = _exam_result_for_user(pid, result_id, db, user)
    all_rows = db.query(PatientExamResult).filter(
        PatientExamResult.owner_id == user.id,
        PatientExamResult.patient_profile_id == pid,
    ).all()
    by_id = {item.id: item for item in all_rows}
    corrected_by = {
        item.correction_of_id: item.id
        for item in all_rows
        if item.correction_of_id is not None
    }

    root = row
    visited: set[int] = set()
    while root.correction_of_id is not None and root.id not in visited:
        visited.add(root.id)
        parent = by_id.get(root.correction_of_id)
        if parent is None:
            break
        root = parent
    chain: list[PatientExamResult] = []
    current: PatientExamResult | None = root
    visited.clear()
    while current is not None and current.id not in visited:
        visited.add(current.id)
        chain.append(current)
        current = by_id.get(corrected_by.get(current.id, -1))

    _auditar_resultado(db, user.id, "read_patient_exam_result", row)
    db.commit()
    return {
        "result": _dump_exam_result(row, db, corrected_by.get(row.id)),
        "history": [_dump_exam_result(item, db, corrected_by.get(item.id)) for item in chain],
    }


@router.post("/{pid}/resultados/{result_id}/correcoes", status_code=201)
def corrigir_resultado(
    pid: int,
    result_id: int,
    dados: ExamCorrectionIn,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    original = _exam_result_for_user(pid, result_id, db, user)
    reason = dados.correction_reason.strip()
    row = _criar_resultado(
        pid,
        dados,
        db,
        user,
        correction_of=original,
        correction_reason=reason,
    )
    return _dump_exam_result(row, db)


@router.get("/{pid}/ecgs")
def listar_ecgs(
    pid: int,
    limite: int = Query(30, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    patient_profile_for_user(pid, db, user)
    rows = (
        db.query(PatientECGRecord)
        .filter(PatientECGRecord.owner_id == user.id, PatientECGRecord.patient_profile_id == pid)
        .order_by(PatientECGRecord.performed_at.desc(), PatientECGRecord.id.desc())
        .offset(offset)
        .limit(limite)
        .all()
    )
    db.add(AuditLog(
        user_id=user.id,
        action="list_patient_ecgs",
        entity="patient_profile",
        entity_id=str(pid),
        detail={"count": len(rows), "limit": limite, "offset": offset},
    ))
    result = [_dump_ecg(row, db) for row in rows]
    db.commit()
    return result


@router.get("/{pid}/ecgs/ia-status")
def status_ia_ecg(
    pid: int,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    patient_profile_for_user(pid, db, user)
    return {
        "enabled": bool(
            settings.ai_enabled
            and settings.ai_clinical_multimodal_enabled
            and ecg_assist.provider_configured()
        ),
        "supported_media_types": list(ecg_assist.supported_media_types()),
    }


@router.get("/{pid}/ecgs/{ecg_id}/sugestoes")
def listar_sugestoes_ecg(
    pid: int,
    ecg_id: int,
    limite: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    row = _ecg_for_user(pid, ecg_id, db, user)
    suggestions = (
        db.query(PatientClinicalAISuggestion)
        .filter(
            PatientClinicalAISuggestion.owner_id == user.id,
            PatientClinicalAISuggestion.patient_profile_id == pid,
            PatientClinicalAISuggestion.ecg_record_id == row.id,
        )
        .order_by(PatientClinicalAISuggestion.created_at.desc(), PatientClinicalAISuggestion.id.desc())
        .offset(offset)
        .limit(limite)
        .all()
    )
    db.add(AuditLog(
        user_id=user.id,
        action="list_patient_ecg_ai_suggestions",
        entity="patient_ecg_record",
        entity_id=str(row.id),
        detail={"count": len(suggestions), "limit": limite, "offset": offset},
    ))
    result = [_dump_ai_suggestion(suggestion) for suggestion in suggestions]
    db.commit()
    return result


@router.post("/{pid}/ecgs", status_code=201)
async def upload_ecg(
    pid: int,
    arquivo: UploadFile = File(...),
    performed_at: datetime = Form(...),
    source_encounter_id: int | None = Form(None),
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    patient_profile_for_user(pid, db, user)
    if performed_at.tzinfo is None:
        raise HTTPException(status_code=422, detail="A data clínica deve informar o fuso horário.")
    if source_encounter_id is not None:
        encounter = encounter_for_user(source_encounter_id, db, user)
        if encounter.patient_profile_id != pid:
            raise HTTPException(status_code=404, detail="Atendimento de origem não encontrado.")

    content = await arquivo.read(20 * 1024 * 1024 + 1)
    if len(content) > 20 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="O ECG precisa ter no máximo 20 MB.")
    try:
        original_name = safe_filename(arquivo.filename, "ecg")
        media_type = validate_file(content, original_name, "exam")
    except UploadRejected as error:
        raise HTTPException(status_code=error.status_code, detail=error.detail) from error

    row = PatientECGRecord(
        owner_id=user.id,
        patient_profile_id=pid,
        author_id=user.id,
        source_encounter_id=source_encounter_id,
        performed_at=performed_at,
        storage_key="",
        original_name_cifrado=b"",
        media_type=media_type,
        size_bytes=len(content),
    )
    storage_key: str | None = None
    try:
        db.add(row)
        db.flush()
        storage_key = cofre.guardar(content, row.id)
        row.storage_key = storage_key
        row.original_name_cifrado = cofre.cifrar_campo(original_name, row.id)
        _audit_ecg(
            db, user.id, "upload_patient_ecg", row,
            media_type=media_type, size_bytes=len(content),
        )
        db.commit()
    except cofre.CofreIndisponivel as error:
        db.rollback()
        if storage_key:
            cofre.apagar(storage_key)
        raise HTTPException(
            status_code=503,
            detail="Armazenamento seguro de ECG indisponível.",
        ) from error
    except Exception:
        db.rollback()
        if storage_key:
            cofre.apagar(storage_key)
        raise
    db.refresh(row)
    return _dump_ecg(row, db)


@router.get("/{pid}/ecgs/{ecg_id}/arquivo")
def abrir_ecg(
    pid: int,
    ecg_id: int,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    row = _ecg_for_user(pid, ecg_id, db, user)
    try:
        content = cofre.ler(row.storage_key, row.id)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail="Arquivo do ECG não encontrado.") from error
    except cofre.CofreIndisponivel as error:
        raise HTTPException(status_code=503, detail="Arquivo do ECG indisponível.") from error
    _audit_ecg(db, user.id, "read_patient_ecg", row)
    db.commit()
    extension = {
        "image/jpeg": "jpg", "image/png": "png", "image/webp": "webp", "application/pdf": "pdf",
    }.get(row.media_type, "bin")
    return Response(
        content=content,
        media_type=row.media_type,
        headers={
            "Content-Disposition": f'inline; filename="ecg-{row.id}.{extension}"',
            "Cache-Control": "no-store, private",
            "X-Content-Type-Options": "nosniff",
        },
    )


@router.post("/{pid}/ecgs/{ecg_id}/sugestoes", status_code=201)
def gerar_sugestao_ecg(
    pid: int,
    ecg_id: int,
    data: AIAnalysisRequestIn,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    if (
        not settings.ai_enabled
        or not settings.ai_clinical_multimodal_enabled
        or not ecg_assist.provider_configured()
    ):
        raise HTTPException(
            status_code=503,
            detail="A assistência multimodal clínica está desligada nesta instalação.",
        )
    row = _ecg_for_user(pid, ecg_id, db, user)
    if row.media_type not in ecg_assist.supported_media_types():
        raise HTTPException(
            status_code=422,
            detail="O provedor configurado não analisa este formato de ECG. Anexe JPEG, PNG ou WEBP.",
        )
    try:
        content = cofre.ler(row.storage_key, row.id)
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail="Arquivo do ECG não encontrado.") from error
    except cofre.CofreIndisponivel as error:
        raise HTTPException(status_code=503, detail="Arquivo do ECG indisponível.") from error
    user_id = user.id
    row_id = row.id
    media_type = row.media_type

    # Serializa a reserva da cota por médico/tenant. A tentativa é persistida
    # ANTES de qualquer transferência de PHI e a transação é encerrada antes
    # da chamada externa, evitando tanto corrida de cota quanto conexão ociosa.
    db.query(User.id).filter(User.id == user_id).with_for_update().one()
    start, end = _operational_day_utc_bounds()
    used = db.query(AuditLog.id).filter(
        AuditLog.user_id == user_id,
        AuditLog.action.in_(("ai_ecg_transfer_attempt", "ai_clinical_exam_transfer_attempt")),
        AuditLog.created_at >= start,
        AuditLog.created_at < end,
    ).count()
    if used >= settings.ai_daily_limit:
        db.rollback()
        raise HTTPException(
            status_code=429,
            detail=f"Limite diário de {settings.ai_daily_limit} análises atingido. Recomeça amanhã.",
        )
    attempt = AuditLog(
        user_id=user_id,
        action="ai_ecg_transfer_attempt",
        entity="patient_ecg_record",
        entity_id=str(row_id),
        detail={
            "patient_profile_id": pid,
            "ecg_record_id": row_id,
            "provider": settings.ai_provider,
            "external_processing_confirmed": data.confirm_external_processing,
            "status": "reserved",
        },
    )
    db.add(attempt)
    db.commit()
    attempt_id = attempt.id

    def registrar_resultado_transferencia(status: str, **detail: object) -> None:
        db.add(AuditLog(
            user_id=user_id,
            action="ai_ecg_transfer_outcome",
            entity="patient_ecg_record",
            entity_id=str(row_id),
            detail={
                "patient_profile_id": pid,
                "ecg_record_id": row_id,
                "transfer_attempt_id": attempt_id,
                "provider": settings.ai_provider,
                "status": status,
                **detail,
            },
        ))
        db.commit()

    try:
        analysis = ecg_assist.analyze_ecg(content, media_type)
    except ValueError as error:
        db.rollback()
        registrar_resultado_transferencia("invalid_response")
        if "exige ECG" in str(error) or "Formato" in str(error):
            raise HTTPException(status_code=422, detail=str(error)) from error
        raise HTTPException(
            status_code=502,
            detail="O provedor devolveu uma sugestão clínica inválida. Nenhum fato foi registrado.",
        ) from error
    except Exception as error:
        db.rollback()
        registrar_resultado_transferencia("provider_error", error_type=type(error).__name__)
        raise HTTPException(
            status_code=502,
            detail=f"O provedor multimodal não respondeu ({type(error).__name__}). Nenhum fato foi registrado.",
        ) from error

    row = _ecg_for_user(pid, ecg_id, db, user)
    suggestion = PatientClinicalAISuggestion(
        owner_id=user.id,
        patient_profile_id=pid,
        ecg_record_id=row.id,
        requested_by=user.id,
        mode="ecg_assistance",
        status="generated",
        payload_cifrado=b"",
        provider=analysis["provider"],
        model=analysis["model"],
        prompt_version=analysis["prompt_version"],
        tokens_input=analysis["tokens_input"],
        tokens_output=analysis["tokens_output"],
    )
    db.add(suggestion)
    db.flush()
    suggestion.payload_cifrado = cofre.cifrar_campo(
        json.dumps(analysis["payload"], ensure_ascii=False), suggestion.id,
    )
    db.add(AuditLog(
        user_id=user_id,
        action="ai_ecg_suggest",
        entity="patient_clinical_ai_suggestion",
        entity_id=str(suggestion.id),
        detail={
            "patient_profile_id": pid,
            "ecg_record_id": row.id,
            "provider": suggestion.provider,
            "model": suggestion.model,
            "prompt_version": suggestion.prompt_version,
            "external_processing_confirmed": data.confirm_external_processing,
            "transfer_attempt_id": attempt_id,
        },
    ))
    db.add(AuditLog(
        user_id=user_id,
        action="ai_ecg_transfer_outcome",
        entity="patient_ecg_record",
        entity_id=str(row_id),
        detail={
            "patient_profile_id": pid,
            "ecg_record_id": row_id,
            "transfer_attempt_id": attempt_id,
            "provider": suggestion.provider,
            "model": suggestion.model,
            "status": "success",
        },
    ))
    db.commit()
    db.refresh(suggestion)
    return _dump_ai_suggestion(suggestion)


@router.post("/{pid}/ecgs/{ecg_id}/sugestoes/{suggestion_id}/revisao")
def revisar_sugestao_ecg(
    pid: int,
    ecg_id: int,
    suggestion_id: int,
    data: AISuggestionReviewIn,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    _suggestion_for_user(pid, ecg_id, suggestion_id, db, user)
    suggestion = (
        db.query(PatientClinicalAISuggestion)
        .filter(
            PatientClinicalAISuggestion.id == suggestion_id,
            PatientClinicalAISuggestion.owner_id == user.id,
            PatientClinicalAISuggestion.patient_profile_id == pid,
            PatientClinicalAISuggestion.ecg_record_id == ecg_id,
        )
        .with_for_update()
        .one_or_none()
    )
    if suggestion is None:
        raise HTTPException(status_code=404, detail="Sugestão clínica não encontrada.")
    if suggestion.status != "generated":
        raise HTTPException(status_code=409, detail="Esta sugestão já foi revisada e é imutável.")

    review_note = (data.review_note or "").strip() or None
    if review_note and len(review_note) > 2000:
        raise HTTPException(status_code=422, detail="Nota de revisão excede 2000 caracteres.")
    now = datetime.now(timezone.utc)
    accepted_result: PatientExamResult | None = None

    try:
        if data.decision == "accept":
            final_interpretation = (data.final_interpretation or "").strip()
            if not final_interpretation:
                raise HTTPException(
                    status_code=422,
                    detail="Revise e confirme a interpretação médica antes de aceitar.",
                )
            if len(final_interpretation) > 12000:
                raise HTTPException(status_code=422, detail="Interpretação excede 12000 caracteres.")
            already_accepted = db.query(PatientClinicalAISuggestion.id).filter(
                PatientClinicalAISuggestion.owner_id == user.id,
                PatientClinicalAISuggestion.patient_profile_id == pid,
                PatientClinicalAISuggestion.ecg_record_id == ecg_id,
                PatientClinicalAISuggestion.status == "accepted",
            ).first()
            if already_accepted:
                raise HTTPException(status_code=409, detail="Este ECG já possui interpretação aceita.")
            ecg = _ecg_for_user(pid, ecg_id, db, user)
            accepted_result = _preparar_resultado(
                pid,
                ExamResultIn(
                    exam_kind="metodo_grafico",
                    exam_name="ECG",
                    performed_at=ecg.performed_at,
                    report_text=final_interpretation,
                    source="ECG anexado ao CorVIA · interpretação revisada pelo médico",
                    source_encounter_id=ecg.source_encounter_id,
                ),
                db,
                user,
            )
            suggestion.status = "accepted"
            suggestion.accepted_result_id = accepted_result.id
        else:
            suggestion.status = "rejected"

        suggestion.reviewed_by = user.id
        suggestion.reviewed_at = now
        suggestion.review_note_cifrado = (
            cofre.cifrar_campo(review_note, suggestion.id) if review_note else None
        )
        db.add(AuditLog(
            user_id=user.id,
            action="review_ai_ecg_suggestion",
            entity="patient_clinical_ai_suggestion",
            entity_id=str(suggestion.id),
            detail={
                "patient_profile_id": pid,
                "ecg_record_id": ecg_id,
                "decision": data.decision,
                "accepted_result_id": accepted_result.id if accepted_result else None,
            },
        ))
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Este ECG já foi revisado ou possui interpretação aceita.",
        ) from error
    db.refresh(suggestion)
    return {
        "suggestion": _dump_ai_suggestion(suggestion),
        "result": _dump_exam_result(accepted_result, db) if accepted_result else None,
    }


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
