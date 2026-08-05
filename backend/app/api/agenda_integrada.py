"""API segura da Agenda Integrada, configuração e mobilidade."""

from __future__ import annotations

import re
from datetime import date, datetime, time, timedelta, timezone
from typing import Literal
from zoneinfo import ZoneInfo

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.core.security import current_user
from app.models.agenda import (
    AppointmentCommunication,
    AppointmentResource,
    AvailabilityException,
    AvailabilityRule,
    CalendarDelegation,
    CalendarIntegration,
    CalendarLocation,
    CalendarOutboxEvent,
    MobilityPreference,
    SchedulingResource,
    SchedulingService,
)
from app.models.audit import AuditLog
from app.models.clinical_docs import Appointment
from app.models.round import Patient
from app.models.user import User
from app.services.agenda_integrada.connectors import ConnectorError, connector_catalog, get_connector
from app.services.agenda_integrada.domain import (
    SYNC_STRATEGIES,
    available_slots,
    fim_agendamento,
    find_conflicts,
    integration_credentials,
    process_outbox_event,
    queue_external_operation,
    store_integration_credentials,
    sync_integration,
    timezone_valido,
)
from app.services.agenda_integrada.traffic import traffic_eta
from app.services.agenda_integrada.notifications import send_appointment_communication, send_pending_communications
from app.services.cofre import cifrar_campo

router = APIRouter(prefix="/api/agenda", tags=["agenda-integrada"])

EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
VALID_STATUSES = {
    "pending_external", "proposed", "pendente", "confirmado", "booked", "arrived",
    "realizado", "faltou", "cancelado",
}
VALID_MODES = {"presencial", "teleconsulta", "domiciliar"}
VALID_PAYMENTS = {"particular", "convenio", "cortesia", "nao_informado"}
MOBILITY_CONSENT_VERSION = "mobility-v1-2026-08-05"


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class LocationIn(StrictModel):
    name: str = Field(min_length=2, max_length=160)
    timezone: str = "America/Sao_Paulo"
    address: dict = Field(default_factory=dict)
    phone: str | None = Field(default=None, max_length=30)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    default_arrival_buffer_minutes: int = Field(default=15, ge=0, le=180)
    color: str = Field(default="#087E8B", pattern=r"^#[0-9A-Fa-f]{6}$")
    active: bool = True

    @field_validator("timezone")
    @classmethod
    def _timezone(cls, value: str) -> str:
        return timezone_valido(value)


class ServiceIn(StrictModel):
    location_id: int | None = None
    code: str = Field(min_length=2, max_length=80, pattern=r"^[a-z0-9][a-z0-9_-]+$")
    name: str = Field(min_length=2, max_length=180)
    category: str = Field(default="consulta", max_length=80)
    description: str | None = Field(default=None, max_length=2000)
    duration_minutes: int = Field(default=30, ge=5, le=1440)
    buffer_before_minutes: int = Field(default=0, ge=0, le=240)
    buffer_after_minutes: int = Field(default=0, ge=0, le=240)
    slot_interval_minutes: int = Field(default=15, ge=5, le=240)
    visit_mode: Literal["presencial", "teleconsulta", "domiciliar"] = "presencial"
    payment_mode: Literal["particular", "convenio", "cortesia", "nao_informado"] = "particular"
    private_price_cents: int | None = Field(default=None, ge=0, le=100_000_000)
    currency: str = Field(default="BRL", pattern=r"^[A-Z]{3}$")
    accepts_insurance: bool = False
    allow_extra_slot: bool = False
    max_extra_slots: int = Field(default=0, ge=0, le=20)
    color: str = Field(default="#087E8B", pattern=r"^#[0-9A-Fa-f]{6}$")
    external_mappings: dict = Field(default_factory=dict)
    active: bool = True


class ResourceIn(StrictModel):
    location_id: int | None = None
    name: str = Field(min_length=2, max_length=160)
    resource_type: Literal["sala", "equipamento", "equipe", "leito", "outro"] = "sala"
    capacity: int = Field(default=1, ge=1, le=100)
    metadata: dict = Field(default_factory=dict)
    active: bool = True


class AvailabilityRuleIn(StrictModel):
    location_id: int
    service_id: int | None = None
    weekday: int = Field(ge=0, le=6)
    start_time: time
    end_time: time
    label: str = Field(default="Rotina de trabalho", min_length=2, max_length=160)
    routine_type: Literal["atendimento", "plantao", "telemedicina", "administrativo", "outro"] = "atendimento"
    visit_mode: Literal["presencial", "teleconsulta", "domiciliar"] = "presencial"
    arrival_buffer_minutes: int = Field(default=15, ge=0, le=180)
    planning_notes: str | None = Field(default=None, max_length=500)
    slot_interval_minutes: int = Field(default=15, ge=5, le=240)
    valid_from: date | None = None
    valid_until: date | None = None
    active: bool = True


class WorkRoutineIn(StrictModel):
    location_id: int
    service_id: int | None = None
    weekdays: list[int] = Field(min_length=1, max_length=7)
    start_time: time
    end_time: time
    label: str = Field(default="Rotina de trabalho", min_length=2, max_length=160)
    routine_type: Literal["atendimento", "plantao", "telemedicina", "administrativo", "outro"] = "atendimento"
    visit_mode: Literal["presencial", "teleconsulta", "domiciliar"] = "presencial"
    arrival_buffer_minutes: int = Field(default=15, ge=0, le=180)
    slot_interval_minutes: int = Field(default=15, ge=5, le=240)
    planning_notes: str | None = Field(default=None, max_length=500)
    valid_from: date | None = None
    valid_until: date | None = None
    allow_overlap: bool = False

    @field_validator("weekdays")
    @classmethod
    def _weekdays(cls, value: list[int]) -> list[int]:
        if any(day < 0 or day > 6 for day in value):
            raise ValueError("Dia da semana inválido.")
        return sorted(set(value))


class AvailabilityExceptionIn(StrictModel):
    location_id: int | None = None
    starts_at: datetime
    ends_at: datetime
    exception_type: Literal["bloqueio", "ferias", "evento", "disponibilidade_extra"] = "bloqueio"
    reason: str | None = Field(default=None, max_length=300)


class AppointmentIn(StrictModel):
    professional_id: int | None = None
    patient_id: int | None = None
    patient_name: str | None = Field(default=None, max_length=200)
    patient_phone: str | None = Field(default=None, max_length=30)
    patient_email: str | None = Field(default=None, max_length=255)
    email_consent: bool = False
    starts_at: datetime
    duration_minutes: int | None = Field(default=None, ge=5, le=1440)
    service_id: int | None = None
    location_id: int | None = None
    integration_id: int | None = None
    resource_ids: list[int] = Field(default_factory=list, max_length=20)
    appointment_type: str = Field(default="consulta", max_length=40)
    visit_mode: Literal["presencial", "teleconsulta", "domiciliar"] | None = None
    payment_mode: Literal["particular", "convenio", "cortesia", "nao_informado"] | None = None
    insurance_name: str | None = Field(default=None, max_length=160)
    price_cents: int | None = Field(default=None, ge=0, le=100_000_000)
    notes: str | None = Field(default=None, max_length=4000)
    allow_extra_slot: bool = False

    @field_validator("patient_email")
    @classmethod
    def _email(cls, value: str | None) -> str | None:
        if value and not EMAIL_RE.fullmatch(value):
            raise ValueError("E-mail do paciente inválido.")
        return value.lower() if value else None


class RescheduleIn(StrictModel):
    starts_at: datetime
    duration_minutes: int | None = Field(default=None, ge=5, le=1440)
    resource_ids: list[int] | None = Field(default=None, max_length=20)
    allow_extra_slot: bool = False
    expected_version: int | None = Field(default=None, ge=1)


class CancelIn(StrictModel):
    reason: str = Field(min_length=3, max_length=500)
    expected_version: int | None = Field(default=None, ge=1)


class IntegrationIn(StrictModel):
    provider: str = Field(min_length=2, max_length=40)
    display_name: str = Field(min_length=2, max_length=160)
    sync_strategy: Literal["external_authoritative", "bidirectional", "meucardio_authoritative"] = "external_authoritative"
    configuration: dict = Field(default_factory=dict)
    credentials: dict = Field(default_factory=dict)
    enabled: bool = False
    write_enabled: bool = False
    consent_accepted: bool = False
    consent_version: str | None = Field(default=None, max_length=40)


class MobilityIn(StrictModel):
    enabled: bool
    consent_accepted: bool = False
    automatic_foreground_refresh: bool = True
    refresh_interval_minutes: int = Field(default=5, ge=2, le=60)
    travel_mode: Literal["driving"] = "driving"


class CommuteIn(StrictModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


def _owner_for(db: Session, user: User, requested: int | None, permission: str) -> int:
    owner_id = requested or user.id
    if owner_id == user.id or user.role == "admin":
        return owner_id
    delegation = db.query(CalendarDelegation).filter(
        CalendarDelegation.professional_id == owner_id,
        CalendarDelegation.delegate_user_id == user.id,
        CalendarDelegation.active.is_(True),
    ).first()
    if not delegation or not getattr(delegation, f"can_{permission}", False):
        raise HTTPException(status_code=403, detail="Sem permissão para esta agenda.")
    return owner_id


def _audit(db: Session, user: User, action: str, entity: str, entity_id: int | None, detail: dict | None = None) -> None:
    db.add(AuditLog(
        user_id=user.id, action=action, entity=entity,
        entity_id=str(entity_id) if entity_id is not None else None,
        detail=detail or {},
    ))


def _integration(db: Session, integration_id: int, owner_id: int) -> CalendarIntegration:
    result = db.query(CalendarIntegration).filter(
        CalendarIntegration.id == integration_id, CalendarIntegration.owner_id == owner_id
    ).first()
    if not result:
        raise HTTPException(status_code=404, detail="Integração não encontrada.")
    return result


def _appointment(db: Session, appointment_id: int, owner_id: int) -> Appointment:
    result = db.query(Appointment).filter(
        Appointment.id == appointment_id, Appointment.owner_id == owner_id,
        Appointment.deleted_at.is_(None),
    ).first()
    if not result:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado.")
    return result


def _aware(value: datetime, timezone_name: str) -> datetime:
    """Interpreta datas sem offset no fuso explícito do local e normaliza em UTC."""
    if value.tzinfo is None:
        value = value.replace(tzinfo=ZoneInfo(timezone_name))
    return value.astimezone(timezone.utc)


def _dump_location(item: CalendarLocation) -> dict:
    return {
        "id": item.id, "name": item.name, "timezone": item.timezone, "address": item.address,
        "phone": item.phone, "latitude": item.latitude, "longitude": item.longitude,
        "default_arrival_buffer_minutes": item.default_arrival_buffer_minutes,
        "color": item.color, "active": item.active,
    }


def _dump_service(item: SchedulingService) -> dict:
    return {
        "id": item.id, "location_id": item.location_id, "code": item.code, "name": item.name,
        "category": item.category, "description": item.description,
        "duration_minutes": item.duration_minutes, "buffer_before_minutes": item.buffer_before_minutes,
        "buffer_after_minutes": item.buffer_after_minutes, "slot_interval_minutes": item.slot_interval_minutes,
        "visit_mode": item.visit_mode, "payment_mode": item.payment_mode,
        "private_price_cents": item.private_price_cents, "currency": item.currency,
        "accepts_insurance": item.accepts_insurance, "allow_extra_slot": item.allow_extra_slot,
        "max_extra_slots": item.max_extra_slots, "color": item.color,
        "external_mappings": item.external_mappings, "active": item.active,
    }


def _dump_routine(db: Session, item: AvailabilityRule) -> dict:
    location = db.get(CalendarLocation, item.location_id)
    service = db.get(SchedulingService, item.service_id) if item.service_id else None
    return {
        "id": item.id, "location_id": item.location_id, "service_id": item.service_id,
        "weekday": item.weekday, "start_time": item.start_time, "end_time": item.end_time,
        "label": item.label, "routine_type": item.routine_type, "visit_mode": item.visit_mode,
        "arrival_buffer_minutes": item.arrival_buffer_minutes,
        "slot_interval_minutes": item.slot_interval_minutes, "planning_notes": item.planning_notes,
        "valid_from": item.valid_from, "valid_until": item.valid_until, "active": item.active,
        "location": _dump_location(location) if location else None,
        "service": _dump_service(service) if service else None,
    }


def _upcoming_routines(db: Session, owner_id: int, *, days: int = 14) -> list[dict]:
    """Materializa a rotina recorrente sem persistir posições ou trajetos."""
    now_utc = datetime.now(timezone.utc)
    rules = db.query(AvailabilityRule).filter(
        AvailabilityRule.owner_id == owner_id,
        AvailabilityRule.active.is_(True),
    ).all()
    result: list[dict] = []
    for rule in rules:
        location = db.get(CalendarLocation, rule.location_id)
        if not location or not location.active:
            continue
        zone = ZoneInfo(location.timezone)
        local_today = now_utc.astimezone(zone).date()
        for offset in range(days + 1):
            work_date = local_today + timedelta(days=offset)
            if work_date.weekday() != rule.weekday:
                continue
            if rule.valid_from and work_date < rule.valid_from:
                continue
            if rule.valid_until and work_date > rule.valid_until:
                continue
            starts_at = datetime.combine(work_date, rule.start_time, tzinfo=zone)
            ends_at = datetime.combine(work_date, rule.end_time, tzinfo=zone)
            if ends_at <= now_utc:
                continue
            service = db.get(SchedulingService, rule.service_id) if rule.service_id else None
            result.append({
                "routine_id": rule.id, "appointment_id": None,
                "starts_at": starts_at.astimezone(timezone.utc),
                "ends_at": ends_at.astimezone(timezone.utc),
                "service_name": service.name if service else rule.label,
                "routine_type": rule.routine_type, "visit_mode": rule.visit_mode,
                "arrival_buffer_minutes": rule.arrival_buffer_minutes,
                "planning_notes": rule.planning_notes,
                "source": "work_routine", "location": _dump_location(location),
            })
    return sorted(result, key=lambda item: item["starts_at"])


def _dump_appointment(db: Session, item: Appointment) -> dict:
    location = db.get(CalendarLocation, item.location_id) if item.location_id else None
    service = db.get(SchedulingService, item.service_id) if item.service_id else None
    return {
        "id": item.id, "patient_id": item.patient_id, "patient_name": item.patient_name_temp,
        "patient_phone": item.patient_phone_temp, "has_patient_email": bool(item.patient_email_cipher),
        "starts_at": item.scheduled_at, "ends_at": item.ends_at,
        "duration_minutes": item.duration_minutes, "appointment_type": item.appointment_type,
        "status": item.status, "notes": item.notes, "location": _dump_location(location) if location else None,
        "service": _dump_service(service) if service else None, "visit_mode": item.visit_mode,
        "payment_mode": item.payment_mode, "insurance_name": item.insurance_name,
        "price_cents": item.price_cents, "currency": item.currency, "source": item.source,
        "integration_id": item.integration_id, "sync_status": item.sync_status,
        "sync_error": item.sync_error, "confirmation_status": item.confirmation_status,
        "conflict_reason": item.conflict_reason, "version": item.version,
    }


@router.get("/capabilities")
def capabilities(_=Depends(current_user)):
    return {
        "integrations_enabled": settings.agenda_integrations_enabled,
        "external_writes_enabled": settings.agenda_external_writes_enabled,
        "background_sync_enabled": settings.agenda_background_sync_enabled,
        "traffic_configured": settings.traffic_configured,
        "traffic_provider": settings.traffic_provider,
        "connectors": connector_catalog(),
    }


@router.get("/locations")
def list_locations(professional_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)):
    owner_id = _owner_for(db, user, professional_id, "view")
    return [_dump_location(x) for x in db.query(CalendarLocation).filter(CalendarLocation.owner_id == owner_id).order_by(CalendarLocation.name).all()]


@router.post("/locations", status_code=201)
def create_location(data: LocationIn, professional_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)):
    owner_id = _owner_for(db, user, professional_id, "configure")
    item = CalendarLocation(owner_id=owner_id, **data.model_dump())
    db.add(item); db.flush()
    _audit(db, user, "agenda_location_create", "calendar_location", item.id, {"owner_id": owner_id})
    db.commit(); db.refresh(item)
    return _dump_location(item)


@router.patch("/locations/{location_id}")
def update_location(location_id: int, data: LocationIn, professional_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)):
    owner_id = _owner_for(db, user, professional_id, "configure")
    item = db.query(CalendarLocation).filter(CalendarLocation.id == location_id, CalendarLocation.owner_id == owner_id).first()
    if not item: raise HTTPException(status_code=404, detail="Local não encontrado.")
    for key, value in data.model_dump().items(): setattr(item, key, value)
    _audit(db, user, "agenda_location_update", "calendar_location", item.id)
    db.commit(); db.refresh(item)
    return _dump_location(item)


@router.get("/services")
def list_services(professional_id: int | None = None, active: bool | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)):
    owner_id = _owner_for(db, user, professional_id, "view")
    query = db.query(SchedulingService).filter(SchedulingService.owner_id == owner_id)
    if active is not None: query = query.filter(SchedulingService.active.is_(active))
    return [_dump_service(x) for x in query.order_by(SchedulingService.name).all()]


@router.post("/services", status_code=201)
def create_service(data: ServiceIn, professional_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)):
    owner_id = _owner_for(db, user, professional_id, "configure")
    if data.location_id and not db.query(CalendarLocation).filter(CalendarLocation.id == data.location_id, CalendarLocation.owner_id == owner_id).first():
        raise HTTPException(status_code=404, detail="Local não encontrado.")
    item = SchedulingService(owner_id=owner_id, **data.model_dump())
    db.add(item); db.flush()
    _audit(db, user, "agenda_service_create", "scheduling_service", item.id, {"owner_id": owner_id})
    db.commit(); db.refresh(item)
    return _dump_service(item)


@router.patch("/services/{service_id}")
def update_service(service_id: int, data: ServiceIn, professional_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)):
    owner_id = _owner_for(db, user, professional_id, "configure")
    item = db.query(SchedulingService).filter(SchedulingService.id == service_id, SchedulingService.owner_id == owner_id).first()
    if not item: raise HTTPException(status_code=404, detail="Serviço não encontrado.")
    if data.location_id and not db.query(CalendarLocation).filter(
        CalendarLocation.id == data.location_id, CalendarLocation.owner_id == owner_id
    ).first():
        raise HTTPException(status_code=404, detail="Local não encontrado.")
    for key, value in data.model_dump().items(): setattr(item, key, value)
    _audit(db, user, "agenda_service_update", "scheduling_service", item.id)
    db.commit(); db.refresh(item)
    return _dump_service(item)


@router.get("/resources")
def list_resources(professional_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)):
    owner_id = _owner_for(db, user, professional_id, "view")
    return [{"id": x.id, "location_id": x.location_id, "name": x.name, "resource_type": x.resource_type, "capacity": x.capacity, "metadata": x.metadata_json, "active": x.active} for x in db.query(SchedulingResource).filter(SchedulingResource.owner_id == owner_id).order_by(SchedulingResource.name).all()]


@router.post("/resources", status_code=201)
def create_resource(data: ResourceIn, professional_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)):
    owner_id = _owner_for(db, user, professional_id, "configure")
    if data.location_id and not db.query(CalendarLocation).filter(
        CalendarLocation.id == data.location_id, CalendarLocation.owner_id == owner_id
    ).first():
        raise HTTPException(status_code=404, detail="Local não encontrado.")
    payload = data.model_dump(); metadata = payload.pop("metadata")
    item = SchedulingResource(owner_id=owner_id, metadata_json=metadata, **payload)
    db.add(item); db.flush(); _audit(db, user, "agenda_resource_create", "scheduling_resource", item.id)
    db.commit(); db.refresh(item)
    return {"id": item.id, "name": item.name, "resource_type": item.resource_type, "capacity": item.capacity}


@router.get("/availability/rules")
def list_rules(professional_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)):
    owner_id = _owner_for(db, user, professional_id, "view")
    return [_dump_routine(db, item) for item in db.query(AvailabilityRule).filter(
        AvailabilityRule.owner_id == owner_id
    ).order_by(AvailabilityRule.weekday, AvailabilityRule.start_time).all()]


@router.post("/availability/rules", status_code=201)
def create_rule(data: AvailabilityRuleIn, professional_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)):
    owner_id = _owner_for(db, user, professional_id, "configure")
    if data.end_time <= data.start_time: raise HTTPException(status_code=422, detail="O fim precisa ser posterior ao início.")
    if data.valid_from and data.valid_until and data.valid_until < data.valid_from: raise HTTPException(status_code=422, detail="Período de vigência inválido.")
    if not db.query(CalendarLocation).filter(CalendarLocation.id == data.location_id, CalendarLocation.owner_id == owner_id).first(): raise HTTPException(status_code=404, detail="Local não encontrado.")
    if data.service_id and not db.query(SchedulingService).filter(SchedulingService.id == data.service_id, SchedulingService.owner_id == owner_id).first(): raise HTTPException(status_code=404, detail="Serviço não encontrado.")
    item = AvailabilityRule(owner_id=owner_id, **data.model_dump()); db.add(item); db.flush()
    _audit(db, user, "agenda_availability_rule_create", "availability_rule", item.id)
    db.commit(); db.refresh(item); return _dump_routine(db, item)


@router.get("/work-routines")
def list_work_routines(professional_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)):
    return list_rules(professional_id=professional_id, db=db, user=user)


@router.post("/work-routines", status_code=201)
def create_work_routine(data: WorkRoutineIn, professional_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)):
    owner_id = _owner_for(db, user, professional_id, "configure")
    if data.end_time <= data.start_time:
        raise HTTPException(status_code=422, detail="O horário de saída precisa ser posterior ao de entrada.")
    if data.valid_from and data.valid_until and data.valid_until < data.valid_from:
        raise HTTPException(status_code=422, detail="Período de vigência inválido.")
    location = db.query(CalendarLocation).filter(
        CalendarLocation.id == data.location_id, CalendarLocation.owner_id == owner_id,
        CalendarLocation.active.is_(True),
    ).first()
    if not location:
        raise HTTPException(status_code=404, detail="Local não encontrado.")
    if data.service_id and not db.query(SchedulingService).filter(
        SchedulingService.id == data.service_id, SchedulingService.owner_id == owner_id,
        SchedulingService.active.is_(True),
    ).first():
        raise HTTPException(status_code=404, detail="Serviço não encontrado.")
    if not data.allow_overlap:
        conflict = db.query(AvailabilityRule).filter(
            AvailabilityRule.owner_id == owner_id,
            AvailabilityRule.weekday.in_(data.weekdays),
            AvailabilityRule.active.is_(True),
            AvailabilityRule.start_time < data.end_time,
            AvailabilityRule.end_time > data.start_time,
        ).first()
        if conflict:
            raise HTTPException(status_code=409, detail={
                "code": "routine_conflict", "message": "A rotina se sobrepõe a outro período de trabalho.",
                "routine_id": conflict.id,
            })
    payload = data.model_dump(exclude={"weekdays", "allow_overlap"})
    created: list[AvailabilityRule] = []
    for weekday in data.weekdays:
        item = AvailabilityRule(owner_id=owner_id, weekday=weekday, active=True, **payload)
        db.add(item); created.append(item)
    db.flush()
    _audit(db, user, "work_routine_create", "availability_rule", created[0].id, {
        "owner_id": owner_id, "weekdays": data.weekdays, "location_id": data.location_id,
        "period_count": len(created),
    })
    db.commit()
    return [_dump_routine(db, item) for item in created]


@router.delete("/work-routines/{routine_id}", status_code=204)
def disable_work_routine(routine_id: int, professional_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)):
    owner_id = _owner_for(db, user, professional_id, "configure")
    item = db.query(AvailabilityRule).filter(
        AvailabilityRule.id == routine_id, AvailabilityRule.owner_id == owner_id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Rotina não encontrada.")
    item.active = False
    _audit(db, user, "work_routine_disable", "availability_rule", item.id)
    db.commit()
    return None


@router.post("/availability/exceptions", status_code=201)
def create_exception(data: AvailabilityExceptionIn, professional_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)):
    owner_id = _owner_for(db, user, professional_id, "configure")
    location = None
    if data.location_id:
        location = db.query(CalendarLocation).filter(
            CalendarLocation.id == data.location_id, CalendarLocation.owner_id == owner_id
        ).first()
        if not location: raise HTTPException(status_code=404, detail="Local não encontrado.")
    timezone_name = location.timezone if location else settings.fuso_operacao
    starts_at = _aware(data.starts_at, timezone_name); ends_at = _aware(data.ends_at, timezone_name)
    if ends_at <= starts_at: raise HTTPException(status_code=422, detail="O fim precisa ser posterior ao início.")
    payload = data.model_dump(exclude={"starts_at", "ends_at"})
    item = AvailabilityException(owner_id=owner_id, starts_at=starts_at, ends_at=ends_at, **payload); db.add(item); db.flush()
    _audit(db, user, "agenda_availability_exception_create", "availability_exception", item.id, {"type": item.exception_type})
    db.commit(); db.refresh(item); return item


@router.get("/availability/slots")
def slots(location_id: int, service_id: int, start_date: date, end_date: date, professional_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)):
    owner_id = _owner_for(db, user, professional_id, "view")
    try: return available_slots(db, owner_id=owner_id, location_id=location_id, service_id=service_id, start_date=start_date, end_date=end_date)
    except ValueError as exc: raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/appointments")
def list_appointments(
    start: datetime | None = None, end: datetime | None = None, status: str | None = None,
    source: str | None = None, location_id: int | None = None, service_id: int | None = None,
    search: str | None = Query(default=None, max_length=100), professional_id: int | None = None,
    db: Session = Depends(get_db), user: User = Depends(current_user),
):
    owner_id = _owner_for(db, user, professional_id, "view")
    query = db.query(Appointment).filter(Appointment.owner_id == owner_id, Appointment.deleted_at.is_(None))
    if start: query = query.filter(Appointment.scheduled_at >= start)
    if end: query = query.filter(Appointment.scheduled_at <= end)
    if status: query = query.filter(Appointment.status == status)
    if source: query = query.filter(Appointment.source == source)
    if location_id: query = query.filter(Appointment.location_id == location_id)
    if service_id: query = query.filter(Appointment.service_id == service_id)
    if search: query = query.filter(Appointment.patient_name_temp.ilike(f"%{search}%"))
    return [_dump_appointment(db, item) for item in query.order_by(Appointment.scheduled_at).limit(2000).all()]


@router.post("/appointments", status_code=201)
def create_appointment(data: AppointmentIn, background_tasks: BackgroundTasks, db: Session = Depends(get_db), user: User = Depends(current_user)):
    owner_id = _owner_for(db, user, data.professional_id, "create")
    if not data.patient_id and not data.patient_name: raise HTTPException(status_code=422, detail="Informe o paciente.")
    if data.patient_email and not data.email_consent: raise HTTPException(status_code=422, detail="Confirme o consentimento para comunicação por e-mail.")
    if data.patient_id and not db.query(Patient).filter(Patient.id == data.patient_id, Patient.created_by == owner_id).first(): raise HTTPException(status_code=404, detail="Paciente não encontrado.")
    service = db.query(SchedulingService).filter(SchedulingService.id == data.service_id, SchedulingService.owner_id == owner_id, SchedulingService.active.is_(True)).first() if data.service_id else None
    if data.service_id and not service:
        raise HTTPException(status_code=404, detail="Serviço não encontrado.")
    location_id = data.location_id or (service.location_id if service else None)
    location = db.query(CalendarLocation).filter(
        CalendarLocation.id == location_id, CalendarLocation.owner_id == owner_id
    ).first() if location_id else None
    if location_id and not location: raise HTTPException(status_code=404, detail="Local não encontrado.")
    integration = _integration(db, data.integration_id, owner_id) if data.integration_id else None
    if integration and integration.sync_strategy == "external_authoritative": raise HTTPException(status_code=409, detail="Esta agenda é controlada pelo sistema externo; crie o agendamento na origem.")
    duration = data.duration_minutes or (service.duration_minutes if service else 30)
    starts_at = _aware(data.starts_at, location.timezone if location else settings.fuso_operacao)
    ends_at = fim_agendamento(starts_at, duration)
    resources = db.query(SchedulingResource).filter(SchedulingResource.owner_id == owner_id, SchedulingResource.id.in_(data.resource_ids)).all() if data.resource_ids else []
    if len(resources) != len(set(data.resource_ids)): raise HTTPException(status_code=404, detail="Recurso não encontrado.")
    conflicts = find_conflicts(db, owner_id=owner_id, starts_at=starts_at, ends_at=ends_at, resource_ids=data.resource_ids)
    extra_allowed = bool(service and service.allow_extra_slot and data.allow_extra_slot)
    if conflicts and not extra_allowed: raise HTTPException(status_code=409, detail={"code": "schedule_conflict", "conflicts": conflicts})
    item = Appointment(
        owner_id=owner_id, patient_id=data.patient_id, patient_name_temp=data.patient_name,
        patient_phone_temp=data.patient_phone, scheduled_at=starts_at, ends_at=ends_at,
        duration_minutes=duration, appointment_type=data.appointment_type, status="confirmado",
        notes=data.notes, location_id=location_id, service_id=data.service_id, integration_id=data.integration_id,
        source="corvia", sync_status="local_only", timezone=(location.timezone if location else settings.fuso_operacao),
        visit_mode=data.visit_mode or (service.visit_mode if service else "presencial"),
        payment_mode=data.payment_mode or (service.payment_mode if service else "nao_informado"),
        insurance_name=data.insurance_name, price_cents=data.price_cents if data.price_cents is not None else (service.private_price_cents if service else None),
        conflict_reason="Encaixe autorizado pelo profissional." if conflicts else None,
        confirmation_status="confirmed",
    )
    db.add(item); db.flush()
    if data.patient_email: item.patient_email_cipher = cifrar_campo(data.patient_email, item.id)
    for resource in resources: db.add(AppointmentResource(appointment_id=item.id, resource_id=resource.id))
    external_event = queue_external_operation(db, appointment=item, integration=integration, operation="create")
    if external_event is not None:
        item.status = "pending_external"
        item.confirmation_status = "pending_external"
    communication = None
    if data.patient_email and external_event is None:
        communication = AppointmentCommunication(owner_id=owner_id, appointment_id=item.id, channel="email", purpose="confirmation", status="pending", recipient_cipher=cifrar_campo(data.patient_email, item.id), consent_basis="explicit_schedule_email")
        db.add(communication); db.flush()
    _audit(db, user, "agenda_appointment_create", "appointment", item.id, {"owner_id": owner_id, "source": "corvia", "extra_slot": bool(conflicts)})
    db.commit(); db.refresh(item)
    if communication is not None: background_tasks.add_task(send_appointment_communication, communication.id)
    return _dump_appointment(db, item)


@router.post("/appointments/{appointment_id}/reschedule")
def reschedule_appointment(appointment_id: int, data: RescheduleIn, professional_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)):
    owner_id = _owner_for(db, user, professional_id, "reschedule"); item = _appointment(db, appointment_id, owner_id)
    if data.expected_version and item.version != data.expected_version: raise HTTPException(status_code=409, detail="O agendamento foi alterado por outra sessão.")
    integration = _integration(db, item.integration_id, owner_id) if item.integration_id else None
    if integration and integration.sync_strategy == "external_authoritative": raise HTTPException(status_code=409, detail="Reagende no sistema externo de origem.")
    duration = data.duration_minutes or item.duration_minutes
    starts_at = _aware(data.starts_at, item.timezone or settings.fuso_operacao)
    ends_at = fim_agendamento(starts_at, duration)
    resource_ids = data.resource_ids if data.resource_ids is not None else [r[0] for r in db.query(AppointmentResource.resource_id).filter(AppointmentResource.appointment_id == item.id).all()]
    resources = db.query(SchedulingResource).filter(
        SchedulingResource.owner_id == owner_id,
        SchedulingResource.id.in_(resource_ids),
    ).all() if resource_ids else []
    if len(resources) != len(set(resource_ids)):
        raise HTTPException(status_code=404, detail="Recurso não encontrado.")
    conflicts = find_conflicts(db, owner_id=owner_id, starts_at=starts_at, ends_at=ends_at, appointment_id=item.id, resource_ids=resource_ids)
    service = db.get(SchedulingService, item.service_id) if item.service_id else None
    if conflicts and not (data.allow_extra_slot and service and service.allow_extra_slot): raise HTTPException(status_code=409, detail={"code": "schedule_conflict", "conflicts": conflicts})
    item.scheduled_at = starts_at; item.ends_at = ends_at; item.duration_minutes = duration; item.version += 1
    item.conflict_reason = "Encaixe autorizado pelo profissional." if conflicts else None
    if data.resource_ids is not None:
        db.query(AppointmentResource).filter(AppointmentResource.appointment_id == item.id).delete()
        for resource in resources:
            db.add(AppointmentResource(appointment_id=item.id, resource_id=resource.id))
    queue_external_operation(db, appointment=item, integration=integration, operation="reschedule")
    _audit(db, user, "agenda_appointment_reschedule", "appointment", item.id, {"version": item.version})
    db.commit(); db.refresh(item); return _dump_appointment(db, item)


@router.post("/appointments/{appointment_id}/cancel")
def cancel_appointment(appointment_id: int, data: CancelIn, professional_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)):
    owner_id = _owner_for(db, user, professional_id, "cancel"); item = _appointment(db, appointment_id, owner_id)
    if data.expected_version and item.version != data.expected_version: raise HTTPException(status_code=409, detail="O agendamento foi alterado por outra sessão.")
    integration = _integration(db, item.integration_id, owner_id) if item.integration_id else None
    if integration and integration.sync_strategy == "external_authoritative": raise HTTPException(status_code=409, detail="Cancele no sistema externo de origem.")
    item.status = "cancelado"; item.cancelled_at = datetime.now(timezone.utc); item.notes = data.reason; item.version += 1
    queue_external_operation(db, appointment=item, integration=integration, operation="cancel")
    _audit(db, user, "agenda_appointment_cancel", "appointment", item.id, {"version": item.version})
    db.commit(); return _dump_appointment(db, item)


@router.get("/workday/next-locations")
def next_locations(limit: int = Query(default=3, ge=1, le=10), professional_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)):
    owner_id = _owner_for(db, user, professional_id, "view"); now = datetime.now(timezone.utc)
    routines = _upcoming_routines(db, owner_id, days=14)
    result = list(routines)
    items = db.query(Appointment).filter(Appointment.owner_id == owner_id, Appointment.location_id.is_not(None), Appointment.deleted_at.is_(None), Appointment.status.notin_(("cancelado", "faltou")), Appointment.scheduled_at >= now).order_by(Appointment.scheduled_at).limit(60).all()
    for item in items:
        covered_by_routine = any(
            routine["location"]["id"] == item.location_id
            and routine["starts_at"] <= item.scheduled_at < routine["ends_at"]
            for routine in routines
        )
        if covered_by_routine:
            continue
        location = db.get(CalendarLocation, item.location_id)
        service = db.get(SchedulingService, item.service_id) if item.service_id else None
        if location:
            result.append({
                "routine_id": None, "appointment_id": item.id,
                "starts_at": item.scheduled_at, "ends_at": item.ends_at,
                "service_name": service.name if service else item.appointment_type,
                "routine_type": None, "visit_mode": item.visit_mode,
                "arrival_buffer_minutes": location.default_arrival_buffer_minutes,
                "planning_notes": None, "source": "appointment",
                "location": _dump_location(location),
            })
    result.sort(key=lambda entry: entry["starts_at"])
    return result[:limit]


@router.get("/workday/plan")
def workday_plan(days: int = Query(default=7, ge=1, le=31), professional_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)):
    owner_id = _owner_for(db, user, professional_id, "view")
    now = datetime.now(timezone.utc); until = now + timedelta(days=days)
    routines = [item for item in _upcoming_routines(db, owner_id, days=days) if item["starts_at"] <= until]
    appointments = db.query(Appointment).filter(
        Appointment.owner_id == owner_id, Appointment.deleted_at.is_(None),
        Appointment.status.notin_(("cancelado", "faltou")),
        Appointment.scheduled_at >= now, Appointment.scheduled_at <= until,
    ).order_by(Appointment.scheduled_at).all()
    warnings: list[dict] = []
    for index, current in enumerate(routines):
        if current["visit_mode"] == "presencial" and (
            current["location"]["latitude"] is None or current["location"]["longitude"] is None
        ):
            warnings.append({"code": "location_not_geocoded", "routine_id": current["routine_id"], "location_id": current["location"]["id"]})
        if index:
            previous = routines[index - 1]
            if previous["ends_at"] > current["starts_at"] and previous["location"]["id"] != current["location"]["id"]:
                warnings.append({"code": "routine_overlap_different_locations", "routine_id": current["routine_id"], "previous_routine_id": previous["routine_id"]})
    return {
        "generated_at": now, "horizon_days": days,
        "routines": routines,
        "appointments": [_dump_appointment(db, item) for item in appointments],
        "summary": {
            "work_periods": len(routines), "appointments": len(appointments),
            "distinct_locations": len({item["location"]["id"] for item in routines}),
            "warnings": len(warnings),
        },
        "warnings": warnings,
    }


@router.get("/mobility/preferences")
def get_mobility(db: Session = Depends(get_db), user: User = Depends(current_user)):
    pref = db.query(MobilityPreference).filter(MobilityPreference.owner_id == user.id).first()
    return {"enabled": bool(pref and pref.enabled), "consent_version": pref.consent_version if pref else None, "consent_at": pref.consent_at if pref else None, "automatic_foreground_refresh": pref.automatic_foreground_refresh if pref else True, "refresh_interval_minutes": pref.refresh_interval_minutes if pref else 5, "travel_mode": pref.travel_mode if pref else "driving", "traffic_configured": settings.traffic_configured}


@router.get("/mobility/map-config")
def get_map_config(user: User = Depends(current_user)):
    """Configuração pública do mapa, entregue somente a uma sessão autenticada.

    Chaves de Maps JavaScript são visíveis no navegador por definição e devem
    ser protegidas no Google Cloud por HTTP referrer e restrição de API. A
    credencial privada de Routes nunca é devolvida por esta rota.
    """
    is_google = settings.traffic_provider == "google_routes"
    return {
        "provider": "google_maps" if is_google else settings.traffic_provider,
        "configured": bool(is_google and settings.google_maps_browser_api_key),
        "api_key": settings.google_maps_browser_api_key if is_google else None,
    }


@router.put("/mobility/preferences")
def set_mobility(data: MobilityIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    if data.enabled and not data.consent_accepted: raise HTTPException(status_code=422, detail="É necessário aceitar o uso da localização para cálculo de deslocamento.")
    pref = db.query(MobilityPreference).filter(MobilityPreference.owner_id == user.id).first()
    if not pref: pref = MobilityPreference(owner_id=user.id); db.add(pref)
    pref.enabled = data.enabled; pref.automatic_foreground_refresh = data.automatic_foreground_refresh; pref.refresh_interval_minutes = data.refresh_interval_minutes; pref.travel_mode = data.travel_mode
    if data.enabled: pref.consent_version = MOBILITY_CONSENT_VERSION; pref.consent_at = pref.consent_at or datetime.now(timezone.utc); pref.revoked_at = None
    else: pref.revoked_at = datetime.now(timezone.utc)
    _audit(db, user, "mobility_consent_granted" if data.enabled else "mobility_consent_revoked", "mobility_preference", None, {"consent_version": MOBILITY_CONSENT_VERSION})
    db.commit(); return get_mobility(db, user)


@router.post("/mobility/commute")
def commute(data: CommuteIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    pref = db.query(MobilityPreference).filter(MobilityPreference.owner_id == user.id, MobilityPreference.enabled.is_(True)).first()
    if not pref: raise HTTPException(status_code=403, detail="Ative o consentimento de localização na conta.")
    destinations = next_locations(limit=1, professional_id=user.id, db=db, user=user)
    if not destinations: return {"status": "no_upcoming_location", "destination": None, "routes": [], "tips": []}
    destination = destinations[0]; location = destination["location"]
    if location["latitude"] is None or location["longitude"] is None: return {"status": "destination_not_geocoded", "destination": destination, "routes": [], "tips": []}
    try:
        result = traffic_eta(origin_latitude=data.latitude, origin_longitude=data.longitude, destination_latitude=location["latitude"], destination_longitude=location["longitude"], arrival_buffer_minutes=location["default_arrival_buffer_minutes"])
    except ConnectorError as exc: raise HTTPException(status_code=exc.status_code, detail={"code": exc.code, "message": str(exc)}) from exc
    # Registra somente que a consulta ocorreu. Coordenadas e rota não entram na auditoria.
    _audit(db, user, "mobility_eta_lookup", "calendar_location", location["id"], {"provider": result.get("provider"), "status": result.get("status")})
    db.commit(); return {**result, "destination": destination}


@router.get("/integrations")
def list_integrations(professional_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)):
    owner_id = _owner_for(db, user, professional_id, "configure")
    return [{"id": x.id, "provider": x.provider, "display_name": x.display_name, "status": x.status, "sync_strategy": x.sync_strategy, "enabled": x.enabled, "write_enabled": x.write_enabled, "configuration": x.configuration, "capabilities": x.capabilities, "has_credentials": bool(x.credentials_cipher), "consent_at": x.consent_at, "last_success_at": x.last_success_at, "last_error_code": x.last_error_code, "last_error_message": x.last_error_message} for x in db.query(CalendarIntegration).filter(CalendarIntegration.owner_id == owner_id).order_by(CalendarIntegration.display_name).all()]


@router.post("/integrations", status_code=201)
def create_integration(data: IntegrationIn, professional_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)):
    owner_id = _owner_for(db, user, professional_id, "configure"); known = {x["provider"]: x for x in connector_catalog()}
    if data.provider not in known: raise HTTPException(status_code=422, detail="Provedor não suportado.")
    if data.enabled and not data.consent_accepted: raise HTTPException(status_code=422, detail="Aceite o consentimento de integração e transferência de dados.")
    if data.write_enabled and not known[data.provider]["capabilities"].get("create_appointment"): raise HTTPException(status_code=409, detail="Escrita não homologada para este provedor.")
    allowed_config = {"calendar_id", "timezone", "expose_patient_name"}
    if set(data.configuration) - allowed_config: raise HTTPException(status_code=422, detail="Configuração contém campos não aceitos.")
    if data.configuration.get("timezone"):
        try:
            timezone_valido(str(data.configuration["timezone"]))
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
    item = CalendarIntegration(owner_id=owner_id, provider=data.provider, display_name=data.display_name, status="draft", sync_strategy=data.sync_strategy, enabled=data.enabled, write_enabled=data.write_enabled, configuration=data.configuration, capabilities=known[data.provider]["capabilities"], consent_version=data.consent_version or "calendar-integration-v1", consent_at=datetime.now(timezone.utc) if data.consent_accepted else None)
    db.add(item); db.flush()
    try: store_integration_credentials(item, data.credentials)
    except ValueError as exc: raise HTTPException(status_code=422, detail=str(exc)) from exc
    _audit(db, user, "agenda_integration_create", "calendar_integration", item.id, {"provider": item.provider, "strategy": item.sync_strategy})
    db.commit(); db.refresh(item); return {"id": item.id, "provider": item.provider, "status": item.status, "enabled": item.enabled, "write_enabled": item.write_enabled, "has_credentials": bool(item.credentials_cipher)}


@router.post("/integrations/{integration_id}/diagnose")
def diagnose_integration(integration_id: int, professional_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)):
    owner_id = _owner_for(db, user, professional_id, "configure"); item = _integration(db, integration_id, owner_id)
    try: result = get_connector(item.provider, integration_credentials(item), item.configuration).diagnose()
    except ConnectorError as exc:
        item.status = "error"; item.last_error_code = exc.code; item.last_error_message = str(exc)[:500]
        _audit(db, user, "agenda_integration_diagnose_failed", "calendar_integration", item.id, {"provider": item.provider, "code": exc.code}); db.commit()
        raise HTTPException(status_code=exc.status_code, detail={"code": exc.code, "message": str(exc)}) from exc
    item.status = "connected" if result.get("ok") else "homologation_required"; item.last_error_code = result.get("code"); item.last_error_message = result.get("message")
    _audit(db, user, "agenda_integration_diagnose", "calendar_integration", item.id, {"provider": item.provider, "ok": bool(result.get("ok"))}); db.commit(); return result


@router.post("/integrations/{integration_id}/sync")
def run_sync(integration_id: int, full: bool = False, professional_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)):
    owner_id = _owner_for(db, user, professional_id, "configure"); item = _integration(db, integration_id, owner_id)
    try: result = sync_integration(db, item, full=full)
    except ConnectorError as exc: raise HTTPException(status_code=exc.status_code, detail={"code": exc.code, "message": str(exc)}) from exc
    _audit(db, user, "agenda_integration_sync", "calendar_integration", item.id, {"provider": item.provider, **result}); db.commit(); return result


@router.post("/outbox/{event_id}/process")
def process_outbox(event_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db), user: User = Depends(current_user)):
    event = db.query(CalendarOutboxEvent).filter(CalendarOutboxEvent.id == event_id, CalendarOutboxEvent.owner_id == user.id).first()
    if not event: raise HTTPException(status_code=404, detail="Operação não encontrada.")
    try:
        result = process_outbox_event(db, event)
        background_tasks.add_task(send_pending_communications, user.id)
        return result
    except ConnectorError as exc: raise HTTPException(status_code=exc.status_code, detail={"code": exc.code, "message": str(exc)}) from exc


@router.post("/communications/process-pending", status_code=202)
def process_pending_communication(background_tasks: BackgroundTasks, user: User = Depends(current_user)):
    background_tasks.add_task(send_pending_communications, user.id)
    return {"accepted": True}
