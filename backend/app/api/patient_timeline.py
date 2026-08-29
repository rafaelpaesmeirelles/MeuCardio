"""Linha do tempo longitudinal do PatientProfile sem duplicar dados clínicos.

Os eventos são derivados em leitura das fontes canônicas do prontuário:
Encounter, resumo clínico, resultados de exames, Agenda/Sala de Espera,
ECG/exames multimodais e artefatos explicitamente vinculados. Nada é copiado
para uma tabela de timeline.
"""
from __future__ import annotations

import json

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user
from app.models.appointment_clinical_flow import AppointmentClinicalFlow
from app.models.audit import AuditLog
from app.models.clinical_docs import Appointment, GeneratedDocument, Prescription
from app.models.encounter_artifact import EncounterArtifact
from app.models.patient_multimodal import PatientMultimodalAISuggestion, PatientMultimodalExamRecord
from app.models.prontuario import (
    ClinicalEncounter, PatientClinicalAISuggestion, PatientClinicalItem,
    PatientECGRecord, PatientExamResult,
)
from app.services import cofre
from app.services.clinical_ownership import patient_profile_for_user
from app.services.ia.cardiovascular_exam_assist import EXAM_TYPES

router = APIRouter(prefix="/api/pacientes", tags=["prontuario"])

_KIND_LABEL = {
    "problema": ("Problema registrado", "Problema inativado"),
    "alergia": ("Alergia registrada", "Alergia inativada"),
    "medicacao": ("Medicação em uso", "Medicação inativada"),
}
_FLOW_LABEL = {
    "scheduled": "Agendado",
    "arrived": "Aguardando",
    "called": "Chamado",
    "in_service": "Em atendimento",
    "completed": "Concluído",
}


def _texto(valor: bytes | None, row_id: int) -> str | None:
    return cofre.decifrar_campo(valor, row_id) if valor is not None else None


def _resumo_encounter(row: ClinicalEncounter) -> str:
    for value in (row.chief_complaint_cifrado, row.assessment_cifrado, row.plan_cifrado):
        text = _texto(value, row.id)
        if text and text.strip():
            return text.strip()[:240]
    return "Sem resumo registrado."


def _payload_item(row: PatientClinicalItem) -> dict:
    return json.loads(cofre.decifrar_campo(row.payload_cifrado, row.id))


def _payload_resultado(row: PatientExamResult) -> dict:
    return json.loads(cofre.decifrar_campo(row.payload_cifrado, row.id))


@router.get("/{pid}/linha-do-tempo")
def linha_do_tempo_paciente(
    pid: int,
    limite: int = Query(100, ge=1, le=200),
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    patient_profile_for_user(pid, db, user)
    eventos: list[dict] = []

    encounters = (
        db.query(ClinicalEncounter)
        .filter(ClinicalEncounter.owner_id == user.id, ClinicalEncounter.patient_profile_id == pid)
        .all()
    )
    encounter_ids = [row.id for row in encounters]
    for row in encounters:
        eventos.append({
            "id": f"atendimento:{row.id}",
            "tipo": "atendimento",
            "data": row.started_at or row.created_at,
            "titulo": "Adendo" if row.encounter_type == "adendo" else "Atendimento clínico",
            "resumo": _resumo_encounter(row),
            "status": row.status,
            "encounter_id": row.id,
        })

    itens = (
        db.query(PatientClinicalItem)
        .filter(PatientClinicalItem.owner_id == user.id, PatientClinicalItem.patient_profile_id == pid)
        .all()
    )
    for row in itens:
        payload = _payload_item(row)
        name = (payload.get("name") or "").strip()
        details = (payload.get("details") or "").strip()
        resumo = " · ".join(x for x in (name, details) if x)[:240]
        ativo, inativo = _KIND_LABEL.get(row.kind, ("Item clínico registrado", "Item clínico inativado"))
        eventos.append({
            "id": f"resumo:{row.id}:inicio",
            "tipo": row.kind,
            "data": row.created_at,
            "titulo": ativo,
            "resumo": resumo,
            "status": "ativo" if row.is_active else "inativo",
            "encounter_id": row.source_encounter_id,
        })
        if row.ended_at:
            eventos.append({
                "id": f"resumo:{row.id}:fim",
                "tipo": row.kind,
                "data": row.ended_at,
                "titulo": inativo,
                "resumo": name[:240],
                "status": "inativo",
                "encounter_id": row.source_encounter_id,
            })

    resultados = (
        db.query(PatientExamResult)
        .filter(PatientExamResult.owner_id == user.id, PatientExamResult.patient_profile_id == pid)
        .all()
    )
    corrected_by = {
        row.correction_of_id: row.id
        for row in resultados
        if row.correction_of_id is not None
    }
    ecgs = (
        db.query(PatientECGRecord)
        .filter(PatientECGRecord.owner_id == user.id, PatientECGRecord.patient_profile_id == pid)
        .all()
    )
    ai_suggestions = (
        db.query(PatientClinicalAISuggestion)
        .filter(
            PatientClinicalAISuggestion.owner_id == user.id,
            PatientClinicalAISuggestion.patient_profile_id == pid,
        )
        .order_by(PatientClinicalAISuggestion.created_at.desc())
        .all()
    )
    multimodal_exams = (
        db.query(PatientMultimodalExamRecord)
        .filter(
            PatientMultimodalExamRecord.owner_id == user.id,
            PatientMultimodalExamRecord.patient_profile_id == pid,
        )
        .all()
    )
    multimodal_suggestions = (
        db.query(PatientMultimodalAISuggestion)
        .filter(
            PatientMultimodalAISuggestion.owner_id == user.id,
            PatientMultimodalAISuggestion.patient_profile_id == pid,
        )
        .order_by(PatientMultimodalAISuggestion.created_at.desc())
        .all()
    )

    accepted_ecg_by_result = {
        row.accepted_result_id: row
        for row in ai_suggestions
        if row.status == "accepted" and row.accepted_result_id is not None
    }
    accepted_multimodal_by_result = {
        row.accepted_result_id: row
        for row in multimodal_suggestions
        if row.status == "accepted" and row.accepted_result_id is not None
    }
    latest_by_ecg: dict[int, PatientClinicalAISuggestion] = {}
    for suggestion in ai_suggestions:
        latest_by_ecg.setdefault(suggestion.ecg_record_id, suggestion)
    latest_by_multimodal: dict[int, PatientMultimodalAISuggestion] = {}
    for suggestion in multimodal_suggestions:
        latest_by_multimodal.setdefault(suggestion.exam_record_id, suggestion)

    for row in resultados:
        payload = _payload_resultado(row)
        nome = (payload.get("exam_name") or "").strip()
        valor = (payload.get("structured_result") or payload.get("result") or "").strip()
        laudo = (payload.get("report_text") or "").strip()
        unidade = (payload.get("unit") or "").strip()
        resultado = " ".join(x for x in (valor, unidade) if x).strip()
        origem = (payload.get("source") or "").strip()
        resumo = " · ".join(x for x in (nome, resultado or laudo, origem) if x)[:240]
        ecg_origin = accepted_ecg_by_result.get(row.id)
        multimodal_origin = accepted_multimodal_by_result.get(row.id)
        eventos.append({
            "id": f"resultado_exame:{row.id}",
            "tipo": "resultado_exame",
            "data": row.performed_at,
            "titulo": "Correção de resultado" if row.correction_of_id else "Resultado de exame",
            "resumo": resumo or "Resultado registrado.",
            "status": "substituido" if row.id in corrected_by else "correcao" if row.correction_of_id else "registrado",
            "encounter_id": row.source_encounter_id,
            "exam_result_id": row.id,
            "lab_test_id": row.lab_test_id,
            "correction_of_id": row.correction_of_id,
            "corrected_by_id": corrected_by.get(row.id),
            "is_superseded": row.id in corrected_by,
            "source": origem or None,
            "ecg_record_id": ecg_origin.ecg_record_id if ecg_origin else None,
            "multimodal_exam_record_id": multimodal_origin.exam_record_id if multimodal_origin else payload.get("multimodal_exam_record_id"),
            "ai_suggestion_id": ecg_origin.id if ecg_origin else multimodal_origin.id if multimodal_origin else payload.get("ai_suggestion_id"),
            "ai_review_status": ecg_origin.status if ecg_origin else multimodal_origin.status if multimodal_origin else None,
        })

    # Um ECG aceito aparece pela fonte canônica PatientExamResult; enquanto
    # não aceito, o próprio arquivo imutável é o evento.
    accepted_ecg_ids = {
        row.ecg_record_id for row in ai_suggestions if row.status == "accepted"
    }
    for row in ecgs:
        if row.id in accepted_ecg_ids:
            continue
        suggestion = latest_by_ecg.get(row.id)
        if suggestion and suggestion.status == "generated":
            resumo, status = "Sugestão da IA disponível; revisão médica pendente.", "awaiting_review"
        elif suggestion and suggestion.status == "rejected":
            resumo, status = "Sugestão da IA rejeitada; arquivo original preservado.", "ai_rejected"
        else:
            resumo, status = "Arquivo original anexado ao prontuário.", "uploaded"
        eventos.append({
            "id": f"ecg_anexado:{row.id}",
            "tipo": "ecg_anexado",
            "data": row.performed_at,
            "titulo": "ECG anexado",
            "resumo": resumo,
            "status": status,
            "encounter_id": row.source_encounter_id,
            "ecg_record_id": row.id,
            "ai_suggestion_id": suggestion.id if suggestion else None,
            "ai_review_status": suggestion.status if suggestion else None,
        })

    # Mesma regra para qualquer outro exame multimodal: o arquivo é fato
    # documental; a sugestão é apoio revisável. Após aceitação, só o
    # PatientExamResult escrito pelo médico aparece como fato clínico.
    accepted_multimodal_ids = {
        row.exam_record_id for row in multimodal_suggestions if row.status == "accepted"
    }
    for row in multimodal_exams:
        if row.id in accepted_multimodal_ids:
            continue
        suggestion = latest_by_multimodal.get(row.id)
        if suggestion and suggestion.status == "generated":
            resumo, status = "Sugestão multimodal da IA disponível; revisão médica pendente.", "awaiting_review"
        elif suggestion and suggestion.status == "rejected":
            resumo, status = "Sugestão da IA rejeitada; exame original preservado.", "ai_rejected"
        else:
            resumo, status = "Arquivo original do exame anexado ao prontuário.", "uploaded"
        eventos.append({
            "id": f"exame_multimodal:{row.id}",
            "tipo": "exame_multimodal",
            "data": row.performed_at,
            "titulo": f"{EXAM_TYPES.get(row.exam_type, row.exam_type)} anexado",
            "resumo": resumo,
            "status": status,
            "encounter_id": row.source_encounter_id,
            "multimodal_exam_record_id": row.id,
            "ai_suggestion_id": suggestion.id if suggestion else None,
            "ai_review_status": suggestion.status if suggestion else None,
        })

    flows = (
        db.query(AppointmentClinicalFlow)
        .filter(
            AppointmentClinicalFlow.owner_id == user.id,
            AppointmentClinicalFlow.patient_profile_id == pid,
        )
        .all()
    )
    for flow in flows:
        appointment = db.get(Appointment, flow.appointment_id)
        if not appointment or appointment.owner_id != user.id:
            continue
        eventos.append({
            "id": f"agenda:{appointment.id}",
            "tipo": "agenda",
            "data": appointment.scheduled_at,
            "titulo": f"Agenda · {appointment.appointment_type}",
            "resumo": _FLOW_LABEL.get(flow.state, flow.state),
            "status": flow.state,
            "appointment_id": appointment.id,
            "encounter_id": next((e.id for e in encounters if e.appointment_id == appointment.id), None),
        })

    if encounter_ids:
        links = (
            db.query(EncounterArtifact)
            .filter(
                EncounterArtifact.owner_id == user.id,
                EncounterArtifact.encounter_id.in_(encounter_ids),
            )
            .all()
        )
        for link in links:
            if link.artifact_type == "prescricao":
                artifact = db.get(Prescription, link.artifact_id)
                if not artifact or artifact.created_by != user.id:
                    continue
                data, titulo = artifact.created_at, "Prescrição emitida"
            else:
                artifact = db.get(GeneratedDocument, link.artifact_id)
                if not artifact or artifact.created_by != user.id:
                    continue
                data, titulo = artifact.created_at, artifact.title or "Documento gerado"
            eventos.append({
                "id": f"{link.artifact_type}:{link.artifact_id}",
                "tipo": link.artifact_type,
                "data": data,
                "titulo": titulo,
                "resumo": "Vinculado ao atendimento.",
                "status": None,
                "encounter_id": link.encounter_id,
                "artifact_id": link.artifact_id,
            })

    eventos.sort(key=lambda item: item["data"], reverse=True)
    resultado = eventos[:limite]
    db.add(AuditLog(
        user_id=user.id,
        action="list_patient_timeline",
        entity="patient_profile",
        entity_id=str(pid),
        detail={"count": len(resultado)},
    ))
    db.commit()
    return resultado
