"""Ponte operacional entre Agenda, PatientProfile e Prontuário.

Não altera o vocabulário de sincronização externa da Agenda. Estados como
`called` e `in_service` existem apenas no fluxo clínico local.
"""
from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user
from app.models.appointment_clinical_flow import AppointmentClinicalFlow
from app.models.audit import AuditLog
from app.models.clinical_docs import Appointment
from app.models.patient_profile import PatientProfile
from app.models.prontuario import ClinicalEncounter
from app.services.clinical_ownership import patient_profile_for_user
from app.services.patient_profile_service import snapshot_de

router = APIRouter(prefix="/api/agenda-clinica", tags=["agenda-clinica"])
_TZ = ZoneInfo("America/Sao_Paulo")


class VinculoIn(BaseModel):
    patient_profile_id: int


class TransicaoIn(BaseModel):
    action: str
    patient_profile_id: int | None = None


def _agendamento(db: Session, user_id: int, appointment_id: int) -> Appointment:
    row = (
        db.query(Appointment)
        .filter(
            Appointment.id == appointment_id,
            Appointment.owner_id == user_id,
            Appointment.deleted_at.is_(None),
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado.")
    return row


def _flow(db: Session, user_id: int, appointment_id: int, criar: bool = False) -> AppointmentClinicalFlow | None:
    row = (
        db.query(AppointmentClinicalFlow)
        .filter(
            AppointmentClinicalFlow.owner_id == user_id,
            AppointmentClinicalFlow.appointment_id == appointment_id,
        )
        .first()
    )
    if row is None and criar:
        row = AppointmentClinicalFlow(owner_id=user_id, appointment_id=appointment_id)
        db.add(row)
        db.flush()
    return row


def _encounter(db: Session, user_id: int, appointment_id: int) -> ClinicalEncounter | None:
    return (
        db.query(ClinicalEncounter)
        .filter(
            ClinicalEncounter.owner_id == user_id,
            ClinicalEncounter.appointment_id == appointment_id,
        )
        .first()
    )


def _audit(db: Session, user_id: int, action: str, appointment_id: int, flow: AppointmentClinicalFlow) -> None:
    db.add(AuditLog(
        user_id=user_id,
        action=action,
        entity="appointment_clinical_flow",
        entity_id=str(appointment_id),
        detail={"state": flow.state, "patient_profile_id": flow.patient_profile_id},
    ))


def _dump(db: Session, appointment: Appointment, flow: AppointmentClinicalFlow | None) -> dict:
    encounter = _encounter(db, appointment.owner_id, appointment.id)
    patient_name = appointment.patient_name_temp or "Paciente não vinculado"
    if flow and flow.patient_profile_id:
        perfil = db.get(PatientProfile, flow.patient_profile_id)
        if perfil and perfil.owner_id == appointment.owner_id:
            patient_name = snapshot_de(perfil).get("full_name") or patient_name
    return {
        "appointment_id": appointment.id,
        "scheduled_at": appointment.scheduled_at,
        "duration_minutes": appointment.duration_minutes,
        "appointment_type": appointment.appointment_type,
        "appointment_status": appointment.status,
        "patient_name": patient_name,
        "patient_profile_id": flow.patient_profile_id if flow else None,
        "state": flow.state if flow else "scheduled",
        "arrived_at": flow.arrived_at if flow else None,
        "called_at": flow.called_at if flow else None,
        "service_started_at": flow.service_started_at if flow else None,
        "completed_at": flow.completed_at if flow else None,
        "encounter_id": encounter.id if encounter else None,
        "encounter_status": encounter.status if encounter else None,
    }


@router.get("/hoje")
def sala_de_espera(
    dia: date | None = Query(None),
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    alvo = dia or datetime.now(_TZ).date()
    inicio_local = datetime.combine(alvo, time.min, tzinfo=_TZ)
    fim_local = inicio_local + timedelta(days=1)
    inicio = inicio_local.astimezone(timezone.utc)
    fim = fim_local.astimezone(timezone.utc)
    rows = (
        db.query(Appointment)
        .filter(
            Appointment.owner_id == user.id,
            Appointment.deleted_at.is_(None),
            Appointment.scheduled_at >= inicio,
            Appointment.scheduled_at < fim,
            Appointment.status.notin_(("cancelado", "faltou", "realizado")),
        )
        .order_by(Appointment.scheduled_at.asc(), Appointment.id.asc())
        .all()
    )
    flows = {
        x.appointment_id: x
        for x in db.query(AppointmentClinicalFlow).filter(
            AppointmentClinicalFlow.owner_id == user.id,
            AppointmentClinicalFlow.appointment_id.in_([x.id for x in rows]),
        ).all()
    } if rows else {}
    return [_dump(db, row, flows.get(row.id)) for row in rows]


@router.post("/{appointment_id}/vincular")
def vincular_paciente(
    appointment_id: int,
    dados: VinculoIn,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    appointment = _agendamento(db, user.id, appointment_id)
    perfil = patient_profile_for_user(dados.patient_profile_id, db, user)
    flow = _flow(db, user.id, appointment_id, criar=True)
    assert flow is not None
    existente = _encounter(db, user.id, appointment_id)
    if existente and existente.patient_profile_id != perfil.id:
        raise HTTPException(status_code=409, detail="Agendamento já possui atendimento de outro paciente.")
    if flow.state in {"in_service", "completed"} and flow.patient_profile_id not in {None, perfil.id}:
        raise HTTPException(status_code=409, detail="Paciente não pode ser trocado após o início do atendimento.")
    flow.patient_profile_id = perfil.id
    _audit(db, user.id, "link_appointment_patient_profile", appointment.id, flow)
    db.commit()
    db.refresh(flow)
    return _dump(db, appointment, flow)


@router.post("/{appointment_id}/transicao")
def transicao(
    appointment_id: int,
    dados: TransicaoIn,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    appointment = _agendamento(db, user.id, appointment_id)
    flow = _flow(db, user.id, appointment_id, criar=True)
    assert flow is not None
    if dados.patient_profile_id is not None:
        perfil = patient_profile_for_user(dados.patient_profile_id, db, user)
        if flow.patient_profile_id not in {None, perfil.id}:
            raise HTTPException(status_code=409, detail="Agendamento já está vinculado a outro paciente.")
        flow.patient_profile_id = perfil.id

    agora = datetime.now(timezone.utc)
    acao = dados.action.strip().lower()
    if acao == "arrive":
        if flow.arrived_at is None:
            flow.arrived_at = agora
        if flow.state == "scheduled":
            flow.state = "arrived"
        if appointment.status not in {"realizado", "cancelado", "faltou"}:
            appointment.status = "arrived"
    elif acao == "call":
        if flow.arrived_at is None:
            raise HTTPException(status_code=409, detail="Registre a chegada antes de chamar o paciente.")
        if flow.called_at is None:
            flow.called_at = agora
        if flow.state in {"scheduled", "arrived"}:
            flow.state = "called"
    elif acao == "start":
        if flow.patient_profile_id is None:
            raise HTTPException(status_code=409, detail="Vincule o paciente ao prontuário antes de iniciar.")
        existente = _encounter(db, user.id, appointment_id)
        if existente is not None:
            if existente.patient_profile_id != flow.patient_profile_id:
                raise HTTPException(status_code=409, detail="Agendamento já possui atendimento de outro paciente.")
            if existente.status == "finalized":
                raise HTTPException(status_code=409, detail="Atendimento deste agendamento já foi finalizado.")
            encounter = existente
        else:
            encounter = ClinicalEncounter(
                owner_id=user.id,
                patient_profile_id=flow.patient_profile_id,
                appointment_id=appointment.id,
                author_id=user.id,
                encounter_type=appointment.appointment_type or "consulta",
                status="in_progress",
                started_at=agora,
            )
            db.add(encounter)
            db.flush()
            db.add(AuditLog(
                user_id=user.id,
                action="create_clinical_encounter_from_appointment",
                entity="clinical_encounter",
                entity_id=str(encounter.id),
                detail={"patient_profile_id": flow.patient_profile_id, "appointment_id": appointment.id},
            ))
        if flow.service_started_at is None:
            flow.service_started_at = agora
        flow.state = "in_service"
    elif acao == "complete":
        encounter = _encounter(db, user.id, appointment_id)
        if encounter is None or encounter.status != "finalized":
            raise HTTPException(status_code=409, detail="Finalize o atendimento clínico antes de concluir a agenda.")
        if flow.completed_at is None:
            flow.completed_at = agora
        flow.state = "completed"
        appointment.status = "realizado"
    else:
        raise HTTPException(status_code=422, detail="Transição inválida.")

    _audit(db, user.id, f"appointment_clinical_{acao}", appointment.id, flow)
    db.commit()
    db.refresh(flow)
    return _dump(db, appointment, flow)
