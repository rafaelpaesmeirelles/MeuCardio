"""API segura da Agenda Integrada, configuração e mobilidade."""

from __future__ import annotations

import logging
import re
from datetime import date, datetime, time, timedelta, timezone
from typing import Literal
from urllib.parse import urlencode
from zoneinfo import ZoneInfo

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.core.security import current_user
from app.models.agenda import (
    AppointmentCommunication,
    AppointmentResource,
    AvailabilityException,
    AvailabilityRule,
    CalendarCommitmentException,
    CalendarCommitmentSeries,
    CalendarDelegation,
    CalendarIntegration,
    CalendarLocation,
    CalendarOutboxEvent,
    ExternalContact,
    GoogleTestUserRequest,
    MobilityPreference,
    SchedulingResource,
    SchedulingService,
)
from app.models.audit import AuditLog
from app.models.clinical_docs import Appointment
from app.models.round import Patient
from app.models.user import User
from app.services.agenda_integrada.connectors import (
    ConnectorError,
    connector_catalog,
    get_connector,
)
from app.services.agenda_integrada.contacts import sync_contacts
from app.services.agenda_integrada.domain import (
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
from app.services.agenda_integrada.external_accounts import (
    begin_oauth,
    complete_oauth,
    disconnect_integration,
    ensure_fresh_credentials,
    oauth_configured,
)
from app.services.agenda_integrada.notifications import (
    send_appointment_communication,
    send_pending_communications,
)
from app.services.agenda_integrada.recurrence import (
    occurrence_dates,
    occurrence_interval,
)
from app.services.agenda_integrada.traffic import traffic_eta
from app.services.apple_mail import AppleMailError
from app.services import apple_mail
from app.services.cofre import cifrar_campo

log = logging.getLogger("meucardio.agenda")

router = APIRouter(prefix="/api/agenda", tags=["agenda-integrada"])
oauth_callback_router = APIRouter(prefix="/api/agenda/oauth", tags=["contas-externas"])

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


class CommitmentSeriesIn(StrictModel):
    title: str = Field(min_length=2, max_length=200)
    category: Literal["compromisso", "trabalho", "reuniao", "plantao", "estudo", "pessoal", "outro"] = "compromisso"
    description: str | None = Field(default=None, max_length=4000)
    location_id: int | None = None
    timezone: str = "America/Sao_Paulo"
    starts_on: date
    start_time: time
    duration_minutes: int = Field(default=30, ge=5, le=1440)
    recurrence: Literal["none", "daily", "weekly", "monthly"] = "none"
    recurrence_interval: int = Field(default=1, ge=1, le=52)
    weekdays: list[int] = Field(default_factory=list, max_length=7)
    month_day: int | None = Field(default=None, ge=1, le=31)
    ends_on: date | None = None
    blocks_scheduling: bool = True
    color: str = Field(default="#6B4EFF", pattern=r"^#[0-9A-Fa-f]{6}$")

    @field_validator("timezone")
    @classmethod
    def _timezone(cls, value: str) -> str:
        return timezone_valido(value)

    @field_validator("weekdays")
    @classmethod
    def _weekdays(cls, value: list[int]) -> list[int]:
        if any(day < 0 or day > 6 for day in value):
            raise ValueError("Dia da semana inválido.")
        return sorted(set(value))

    @model_validator(mode="after")
    def _recurrence(self):
        if self.ends_on and self.ends_on < self.starts_on:
            raise ValueError("A data final precisa ser igual ou posterior à inicial.")
        if self.recurrence == "weekly" and not self.weekdays:
            self.weekdays = [self.starts_on.weekday()]
        if self.recurrence == "monthly" and self.month_day is None:
            self.month_day = self.starts_on.day
        return self


class CommitmentExceptionIn(StrictModel):
    occurrence_date: date
    action: Literal["cancel", "override"]
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    title: str | None = Field(default=None, max_length=200)
    location_id: int | None = None
    notes: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def _override(self):
        if self.action == "override" and (self.starts_at is None or self.ends_at is None):
            raise ValueError("Informe o novo início e fim da ocorrência.")
        # A comparação definitiva ocorre no endpoint após ambos os valores
        # serem normalizados no fuso da ocorrência. Isso também aceita com
        # segurança um cliente que envie um valor com offset e outro sem.
        return self


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


class PreferenciasSincronizacaoIn(StrictModel):
    """Trabalho 16 (07/08/2026) — `sync_calendar`/`sync_mail`/`contacts`
    alteram só a PREFERÊNCIA de uso, nunca o que a conta pode tecnicamente
    fazer (isso vem de `capabilities`, concedido no momento da conexão/
    OAuth — reconectar ou trocar de escopo é o único jeito de mudar
    capacidade real). Todos opcionais: o médico manda só o que quer mudar."""
    sync_calendar: bool | None = None
    sync_mail: bool | None = None
    contacts: bool | None = None


class AppleIntegrationIn(StrictModel):
    apple_id: str = Field(min_length=5, max_length=320)
    app_specific_password: str = Field(min_length=16, max_length=32)
    contacts: bool = True
    consent_accepted: bool
    # E-mail é opt-in separado da Agenda/Contatos (Trabalho 10) — mesma
    # senha específica de app funciona pros dois fins, mas o consentimento
    # de ler/enviar e-mail é uma autorização distinta, texto próprio.
    mail: bool = False
    mail_consent_accepted: bool = False

    @field_validator("apple_id")
    @classmethod
    def _apple_id(cls, value: str) -> str:
        if not EMAIL_RE.fullmatch(value):
            raise ValueError("ID Apple inválido.")
        return value.lower()

    @field_validator("app_specific_password")
    @classmethod
    def _app_password(cls, value: str) -> str:
        compact = value.replace("-", "").replace(" ", "")
        if len(compact) != 16 or not compact.isalnum():
            raise ValueError("Use a senha específica de app da Apple, com 16 caracteres.")
        return "-".join(compact[index:index + 4] for index in range(0, 16, 4))


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


def _commitment_series(db: Session, series_id: int, owner_id: int) -> CalendarCommitmentSeries:
    item = db.query(CalendarCommitmentSeries).filter(
        CalendarCommitmentSeries.id == series_id,
        CalendarCommitmentSeries.owner_id == owner_id,
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Compromisso recorrente não encontrado.")
    return item


def _dump_commitment_series(db: Session, item: CalendarCommitmentSeries) -> dict:
    location = db.get(CalendarLocation, item.location_id) if item.location_id else None
    return {
        "id": item.id, "title": item.title, "category": item.category,
        "description": item.description, "location_id": item.location_id,
        "location": _dump_location(location) if location else None,
        "timezone": item.timezone, "starts_on": item.starts_on,
        "start_time": item.start_time, "duration_minutes": item.duration_minutes,
        "recurrence": item.recurrence, "recurrence_interval": item.recurrence_interval,
        "weekdays": item.weekdays or [], "month_day": item.month_day,
        "ends_on": item.ends_on, "blocks_scheduling": item.blocks_scheduling,
        "color": item.color, "active": item.active,
    }


def _commitment_occurrences(
    db: Session, owner_id: int, start_date: date, end_date: date,
    *, include_cancelled: bool = True,
) -> list[dict]:
    series_items = db.query(CalendarCommitmentSeries).filter(
        CalendarCommitmentSeries.owner_id == owner_id,
        CalendarCommitmentSeries.active.is_(True),
        CalendarCommitmentSeries.starts_on <= end_date,
        (CalendarCommitmentSeries.ends_on.is_(None) | (CalendarCommitmentSeries.ends_on >= start_date)),
    ).all()
    series_ids = [item.id for item in series_items]
    exceptions = db.query(CalendarCommitmentException).filter(
        CalendarCommitmentException.owner_id == owner_id,
        CalendarCommitmentException.series_id.in_(series_ids),
        CalendarCommitmentException.occurrence_date >= start_date,
        CalendarCommitmentException.occurrence_date <= end_date,
    ).all() if series_ids else []
    exception_map = {(item.series_id, item.occurrence_date): item for item in exceptions}
    result: list[dict] = []
    for series in series_items:
        base_location = db.get(CalendarLocation, series.location_id) if series.location_id else None
        for occurrence_date in occurrence_dates(series, start_date, end_date):
            exception = exception_map.get((series.id, occurrence_date))
            cancelled = bool(exception and exception.action == "cancel")
            if cancelled and not include_cancelled:
                continue
            starts_at, ends_at = occurrence_interval(series, occurrence_date)
            title = series.title
            location = base_location
            notes = series.description
            if exception and exception.action == "override":
                starts_at = exception.override_starts_at or starts_at
                ends_at = exception.override_ends_at or ends_at
                title = exception.override_title or title
                if exception.override_location_id:
                    location = db.get(CalendarLocation, exception.override_location_id)
                notes = exception.notes or notes
            result.append({
                "id": f"commitment:{series.id}:{occurrence_date.isoformat()}",
                "calendar_kind": "commitment", "series_id": series.id,
                "occurrence_date": occurrence_date, "title": title,
                "patient_name": None, "patient_phone": None,
                "starts_at": starts_at, "ends_at": ends_at,
                "duration_minutes": max(5, int((ends_at - starts_at).total_seconds() // 60)),
                "appointment_type": series.category,
                "status": "cancelado" if cancelled else "confirmado",
                "notes": notes, "location": _dump_location(location) if location else None,
                "service": None, "visit_mode": "presencial" if location else "nao_informado",
                "payment_mode": "nao_informado", "price_cents": None,
                "source": "corvia_manual", "sync_status": "local_only",
                "conflict_reason": None, "version": 1,
                "recurrence": series.recurrence,
                "blocks_scheduling": series.blocks_scheduling,
                "is_exception": exception is not None,
                "color": series.color,
            })
    return sorted(result, key=lambda item: item["starts_at"])


def _commitment_conflicts(
    db: Session, owner_id: int, starts_at: datetime, ends_at: datetime,
) -> list[dict]:
    conflicts = []
    for item in _commitment_occurrences(
        db, owner_id, starts_at.date() - timedelta(days=1), ends_at.date() + timedelta(days=1),
        include_cancelled=False,
    ):
        if item["blocks_scheduling"] and starts_at < item["ends_at"] and ends_at > item["starts_at"]:
            conflicts.append({
                "commitment_id": item["id"], "starts_at": item["starts_at"].isoformat(),
                "ends_at": item["ends_at"].isoformat(), "reason": "manual_commitment",
            })
    return conflicts


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
        "google_oauth_modo_teste": settings.google_oauth_modo_teste,
        "connectors": [
            {**item, "oauth_configured": oauth_configured(item["provider"])}
            if item["provider"] in {"google_calendar", "microsoft_365"} else item
            for item in connector_catalog()
        ],
    }


_EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


class GoogleTesteSolicitarIn(BaseModel):
    google_email: str = Field(min_length=5, max_length=320)

    @field_validator("google_email")
    @classmethod
    def _google_email(cls, value: str) -> str:
        if not _EMAIL_RE.fullmatch(value):
            raise ValueError("E-mail inválido.")
        return value.strip().lower()


@router.post("/google-teste/solicitar", status_code=201)
def solicitar_teste_google(data: GoogleTesteSolicitarIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    """Pré-cadastro de liberação enquanto o app está em modo Testing (ver
    GoogleTestUserRequest). Não chama o Google — só guarda o pedido e avisa
    o admin. Idempotente: pedido pendente existente do mesmo usuário é
    atualizado (e-mail pode ter mudado), não duplicado."""
    if not settings.google_oauth_modo_teste:
        raise HTTPException(status_code=409, detail="O Google já não está em modo de teste — conecte direto.")
    existente = db.query(GoogleTestUserRequest).filter(
        GoogleTestUserRequest.user_id == user.id, GoogleTestUserRequest.status == "pendente",
    ).first()
    if existente:
        existente.google_email = data.google_email
        item = existente
    else:
        item = GoogleTestUserRequest(user_id=user.id, google_email=data.google_email)
        db.add(item)
    _audit(db, user, "google_teste_solicitado", "google_test_user_request", None, {"google_email": data.google_email})
    db.commit(); db.refresh(item)
    return {"id": item.id, "status": item.status}


@router.get("/google-teste/status")
def status_teste_google(db: Session = Depends(get_db), user: User = Depends(current_user)):
    item = db.query(GoogleTestUserRequest).filter(
        GoogleTestUserRequest.user_id == user.id,
    ).order_by(GoogleTestUserRequest.id.desc()).first()
    if not item:
        return {"status": None}
    return {"status": item.status, "google_email": item.google_email, "created_at": item.created_at}


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


@router.get("/commitment-series")
def list_commitment_series(
    professional_id: int | None = None, db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    owner_id = _owner_for(db, user, professional_id, "view")
    return [_dump_commitment_series(db, item) for item in db.query(CalendarCommitmentSeries).filter(
        CalendarCommitmentSeries.owner_id == owner_id,
    ).order_by(CalendarCommitmentSeries.active.desc(), CalendarCommitmentSeries.starts_on, CalendarCommitmentSeries.start_time).all()]


@router.post("/commitment-series", status_code=201)
def create_commitment_series(
    data: CommitmentSeriesIn, professional_id: int | None = None,
    db: Session = Depends(get_db), user: User = Depends(current_user),
):
    owner_id = _owner_for(db, user, professional_id, "create")
    if data.location_id and not db.query(CalendarLocation).filter(
        CalendarLocation.id == data.location_id,
        CalendarLocation.owner_id == owner_id,
        CalendarLocation.active.is_(True),
    ).first():
        raise HTTPException(status_code=404, detail="Local não encontrado.")
    item = CalendarCommitmentSeries(owner_id=owner_id, active=True, **data.model_dump())
    db.add(item); db.flush()
    _audit(db, user, "calendar_commitment_series_create", "calendar_commitment_series", item.id, {
        "recurrence": item.recurrence, "blocks_scheduling": item.blocks_scheduling,
    })
    db.commit(); db.refresh(item)
    return _dump_commitment_series(db, item)


@router.patch("/commitment-series/{series_id}")
def update_commitment_series(
    series_id: int, data: CommitmentSeriesIn, professional_id: int | None = None,
    db: Session = Depends(get_db), user: User = Depends(current_user),
):
    owner_id = _owner_for(db, user, professional_id, "configure")
    item = _commitment_series(db, series_id, owner_id)
    if data.location_id and not db.query(CalendarLocation).filter(
        CalendarLocation.id == data.location_id, CalendarLocation.owner_id == owner_id,
        CalendarLocation.active.is_(True),
    ).first():
        raise HTTPException(status_code=404, detail="Local não encontrado.")
    for key, value in data.model_dump().items():
        setattr(item, key, value)
    _audit(db, user, "calendar_commitment_series_update", "calendar_commitment_series", item.id)
    db.commit(); db.refresh(item)
    return _dump_commitment_series(db, item)


@router.delete("/commitment-series/{series_id}", status_code=204)
def disable_commitment_series(
    series_id: int, professional_id: int | None = None, db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    owner_id = _owner_for(db, user, professional_id, "configure")
    item = _commitment_series(db, series_id, owner_id)
    item.active = False
    _audit(db, user, "calendar_commitment_series_disable", "calendar_commitment_series", item.id)
    db.commit()
    return None


@router.get("/commitments")
def list_commitments(
    start: date = Query(...), end: date = Query(...), include_cancelled: bool = True,
    professional_id: int | None = None, db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    if end < start or (end - start).days > 400:
        raise HTTPException(status_code=422, detail="Consulte um período entre 1 e 400 dias.")
    owner_id = _owner_for(db, user, professional_id, "view")
    return _commitment_occurrences(db, owner_id, start, end, include_cancelled=include_cancelled)


@router.put("/commitment-series/{series_id}/exceptions")
def put_commitment_exception(
    series_id: int, data: CommitmentExceptionIn, professional_id: int | None = None,
    db: Session = Depends(get_db), user: User = Depends(current_user),
):
    owner_id = _owner_for(db, user, professional_id, "configure")
    series = _commitment_series(db, series_id, owner_id)
    if data.occurrence_date not in occurrence_dates(series, data.occurrence_date, data.occurrence_date):
        raise HTTPException(status_code=422, detail="A data informada não pertence a esta recorrência.")
    location = None
    if data.location_id:
        location = db.query(CalendarLocation).filter(
            CalendarLocation.id == data.location_id, CalendarLocation.owner_id == owner_id,
            CalendarLocation.active.is_(True),
        ).first()
        if not location:
            raise HTTPException(status_code=404, detail="Local não encontrado.")
    starts_at = _aware(data.starts_at, location.timezone if location else series.timezone) if data.starts_at else None
    ends_at = _aware(data.ends_at, location.timezone if location else series.timezone) if data.ends_at else None
    if starts_at and ends_at and ends_at <= starts_at:
        raise HTTPException(status_code=422, detail="O novo fim precisa ser posterior ao início.")
    item = db.query(CalendarCommitmentException).filter(
        CalendarCommitmentException.series_id == series.id,
        CalendarCommitmentException.occurrence_date == data.occurrence_date,
    ).first()
    if item is None:
        item = CalendarCommitmentException(
            owner_id=owner_id, series_id=series.id, occurrence_date=data.occurrence_date,
        )
        db.add(item)
    item.action = data.action
    item.override_starts_at = starts_at if data.action == "override" else None
    item.override_ends_at = ends_at if data.action == "override" else None
    item.override_title = data.title if data.action == "override" else None
    item.override_location_id = data.location_id if data.action == "override" else None
    item.notes = data.notes
    db.flush()
    _audit(db, user, "calendar_commitment_exception_upsert", "calendar_commitment_exception", item.id, {
        "series_id": series.id, "occurrence_date": data.occurrence_date.isoformat(), "action": data.action,
    })
    db.commit(); db.refresh(item)
    return {
        "id": item.id, "series_id": item.series_id, "occurrence_date": item.occurrence_date,
        "action": item.action,
    }


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
    # Trabalho 16: agendamento importado de conta cuja preferência de
    # sincronização de agenda está desligada não aparece — sem apagar nada,
    # só parar de mostrar (a próxima sincronização real ainda escreve os
    # dados; é a LEITURA que respeita a preferência). Nunca afeta os
    # compromissos nativos (integration_id nulo).
    desligadas = db.query(CalendarIntegration.id).filter(
        CalendarIntegration.owner_id == owner_id, CalendarIntegration.sync_calendar.is_(False),
    )
    query = query.filter(
        or_(Appointment.integration_id.is_(None), Appointment.integration_id.notin_(desligadas))
    )
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
    conflicts.extend(_commitment_conflicts(db, owner_id, starts_at, ends_at))
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
    conflicts.extend(_commitment_conflicts(db, owner_id, starts_at, ends_at))
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


@router.get("/oauth/{provider_slug}/start")
def start_external_account(
    provider_slug: Literal["google", "microsoft"],
    contacts: bool = True,
    mail: bool = False,
    calendar_write: bool = False,
    consent_accepted: bool = False,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    provider = "google_calendar" if provider_slug == "google" else "microsoft_365"
    if not consent_accepted:
        raise HTTPException(status_code=422, detail="Aceite a sincronização de Calendário, Contatos e, quando solicitado, E-mail.")
    if calendar_write and not settings.agenda_external_writes_enabled:
        raise HTTPException(status_code=409, detail="A escrita em calendários externos está desativada pelo administrador.")
    try:
        url = begin_oauth(
            db, owner_id=user.id, provider=provider,
            calendar_write=calendar_write, contacts=contacts, mail=mail,
        )
    except ConnectorError as exc:
        raise HTTPException(status_code=exc.status_code, detail={"code": exc.code, "message": str(exc)}) from exc
    _audit(db, user, "external_account_oauth_start", "calendar_integration", None, {"provider": provider})
    db.commit()
    return {"authorization_url": url}


def _oauth_callback(provider: str, code: str | None, state: str | None, error: str | None, db: Session):
    target = f"{settings.public_url.rstrip('/')}/agenda"
    if error or not code or not state:
        return RedirectResponse(f"{target}?conta_erro=autorizacao_cancelada", status_code=303)
    try:
        integration = complete_oauth(db, provider=provider, code=code, state=state)
    except ConnectorError as exc:
        return RedirectResponse(f"{target}?{urlencode({'conta_erro': exc.code})}", status_code=303)

    # A autorização já deve produzir valor imediato: importa a agenda e os
    # contatos na primeira volta do provedor. Uma indisponibilidade temporária
    # não revoga a conta recém-conectada; ela permanece pronta para a ação
    # manual “Sincronizar”, com o erro técnico registrado na integração.
    sincronizacao = "ok"
    try:
        sync_integration(db, integration, full=True)
        if integration.contacts_enabled:
            integration = db.get(CalendarIntegration, integration.id) or integration
            sync_contacts(db, integration, full=True)
    except ConnectorError as exc:
        sincronizacao = "pendente"
        integration = db.get(CalendarIntegration, integration.id) or integration
        integration.last_error_code = exc.code
        integration.last_error_message = str(exc)[:500]
        db.commit()

    return RedirectResponse(f"{target}?{urlencode({'conta_conectada': integration.provider, 'sincronizacao': sincronizacao})}", status_code=303)


@oauth_callback_router.get("/google/callback")
def google_oauth_callback(
    code: str | None = None, state: str | None = None, error: str | None = None,
    db: Session = Depends(get_db),
):
    return _oauth_callback("google_calendar", code, state, error, db)


@oauth_callback_router.get("/microsoft/callback")
def microsoft_oauth_callback(
    code: str | None = None, state: str | None = None, error: str | None = None,
    db: Session = Depends(get_db),
):
    return _oauth_callback("microsoft_365", code, state, error, db)


@router.post("/integrations/apple", status_code=201)
def connect_apple(data: AppleIntegrationIn, db: Session = Depends(get_db), user: User = Depends(current_user)):
    if not data.consent_accepted:
        raise HTTPException(status_code=422, detail="Aceite a sincronização de Calendário e Contatos.")
    if data.mail and not data.mail_consent_accepted:
        raise HTTPException(status_code=422, detail="Aceite a leitura e o envio de e-mail pela caixa iCloud.")
    existing = db.query(CalendarIntegration).filter(
        CalendarIntegration.owner_id == user.id,
        CalendarIntegration.provider == "apple_icloud",
        CalendarIntegration.external_account_id == data.apple_id,
    ).first()
    item = existing or CalendarIntegration(
        owner_id=user.id, provider="apple_icloud", display_name=data.apple_id,
        external_account_id=data.apple_id, sync_strategy="external_authoritative",
    )
    if not existing:
        db.add(item); db.flush()
    item.status = "connected"
    item.enabled = True
    item.write_enabled = False
    item.contacts_enabled = data.contacts
    capacidades_calendario = next(x["capabilities"] for x in connector_catalog() if x["provider"] == "apple_icloud")
    item.capabilities = {**capacidades_calendario, "read_mail": data.mail, "send_mail": data.mail}
    item.consent_version = "external-accounts-v1-2026-08-05"
    item.consent_at = datetime.now(timezone.utc)
    item.revoked_at = None
    store_integration_credentials(item, {
        "username": data.apple_id,
        "app_specific_password": data.app_specific_password,
    })
    try:
        diagnosis = get_connector("apple_icloud", integration_credentials(item), {}).diagnose()
        if data.mail:
            # Confirma de verdade que a senha também autentica no IMAP, em
            # vez de supor que "a mesma senha serve pra tudo na Apple" —
            # mesmo cuidado de nunca simular sucesso sem testar.
            apple_mail.diagnose(integration_credentials(item))
    except ConnectorError as exc:
        db.rollback()
        # 07/08/2026: até aqui só o status HTTP final chegava ao log
        # (`http_request_completed` genérico) — o código/mensagem reais do
        # que a Apple respondeu nunca ficavam registrados no servidor, só no
        # corpo da resposta ao navegador. Foi exatamente essa lacuna que
        # atrasou o diagnóstico do bug de redirecionamento de partição
        # (corrigido no mesmo dia, ver apple_dav.py). Log explícito aqui para
        # qualquer falha futura já vir com o código/mensagem no log do
        # servidor, sem depender de reproduzir de novo.
        log.warning("Falha ao conectar Apple (owner_id=%s): %s — %s", user.id, exc.code, exc)
        raise HTTPException(status_code=exc.status_code, detail={"code": exc.code, "message": str(exc)}) from exc
    except AppleMailError as exc:
        db.rollback()
        log.warning("Falha ao conectar e-mail Apple (owner_id=%s): %s", user.id, exc)
        raise HTTPException(status_code=exc.status_code, detail={"code": "apple_mail_error", "message": str(exc)}) from exc
    _audit(db, user, "external_account_connected", "calendar_integration", item.id, {"provider": "apple_icloud", "mail": data.mail})
    db.commit(); db.refresh(item)
    return {"id": item.id, "provider": item.provider, "status": item.status, "diagnosis": diagnosis}


@router.get("/integrations")
def list_integrations(professional_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)):
    owner_id = _owner_for(db, user, professional_id, "configure")
    result = []
    for x in db.query(CalendarIntegration).filter(CalendarIntegration.owner_id == owner_id).order_by(CalendarIntegration.display_name).all():
        contact_count = db.query(ExternalContact).filter(
            ExternalContact.integration_id == x.id, ExternalContact.deleted.is_(False),
        ).count()
        result.append({"id": x.id, "provider": x.provider, "display_name": x.display_name, "status": x.status, "sync_strategy": x.sync_strategy, "enabled": x.enabled, "write_enabled": x.write_enabled, "contacts_enabled": x.contacts_enabled, "sync_calendar": x.sync_calendar, "sync_mail": x.sync_mail, "contact_count": contact_count, "configuration": x.configuration, "capabilities": x.capabilities, "has_credentials": bool(x.credentials_cipher), "consent_at": x.consent_at, "revoked_at": x.revoked_at, "last_success_at": x.last_success_at, "last_error_code": x.last_error_code, "last_error_message": x.last_error_message})
    return result


@router.post("/integrations", status_code=201)
def create_integration(data: IntegrationIn, professional_id: int | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)):
    owner_id = _owner_for(db, user, professional_id, "configure"); known = {x["provider"]: x for x in connector_catalog()}
    if data.provider not in known: raise HTTPException(status_code=422, detail="Provedor não suportado.")
    if data.provider in {"google_calendar", "microsoft_365", "apple_icloud"}:
        raise HTTPException(status_code=422, detail="Use o botão seguro de conexão da conta externa.")
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
    try:
        credentials = (
            ensure_fresh_credentials(db, item)
            if item.provider in {"google_calendar", "microsoft_365", "apple_icloud"}
            else integration_credentials(item)
        )
        result = get_connector(item.provider, credentials, item.configuration).diagnose()
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


@router.post("/integrations/{integration_id}/sync-all")
def run_external_sync(integration_id: int, full: bool = False, db: Session = Depends(get_db), user: User = Depends(current_user)):
    item = _integration(db, integration_id, user.id)
    try:
        calendar_result = sync_integration(db, item, full=full)
        item = _integration(db, integration_id, user.id)
        contacts_result = sync_contacts(db, item, full=full) if item.contacts_enabled else None
    except ConnectorError as exc:
        raise HTTPException(status_code=exc.status_code, detail={"code": exc.code, "message": str(exc)}) from exc
    _audit(db, user, "external_account_sync", "calendar_integration", item.id, {
        "provider": item.provider, "calendar": calendar_result, "contacts": contacts_result,
    })
    db.commit()
    return {"calendar": calendar_result, "contacts": contacts_result}


@router.post("/integrations/{integration_id}/sync-contacts")
def run_contacts_sync(integration_id: int, full: bool = False, db: Session = Depends(get_db), user: User = Depends(current_user)):
    item = _integration(db, integration_id, user.id)
    try:
        result = sync_contacts(db, item, full=full)
    except ConnectorError as exc:
        raise HTTPException(status_code=exc.status_code, detail={"code": exc.code, "message": str(exc)}) from exc
    _audit(db, user, "external_contacts_sync", "calendar_integration", item.id, {"provider": item.provider, **result})
    db.commit(); return result


@router.patch("/integrations/{integration_id}/preferencias")
def alterar_preferencias_sincronizacao(
    integration_id: int, dados: PreferenciasSincronizacaoIn,
    db: Session = Depends(get_db), user: User = Depends(current_user),
):
    """Liga/desliga o que a Corvia efetivamente USA de uma conta já
    conectada — agenda, contatos, e-mail —, sem desconectar. Só aceita
    ligar o que a conta REALMENTE tem (capabilities); ligar o que não tem
    seria fingir uma sincronização que não vai acontecer. Efetivo na
    próxima leitura (agenda/caixa unificada já filtram por estes campos),
    sem precisar de nova sincronização."""
    item = _integration(db, integration_id, user.id)
    capacidades = item.capabilities or {}

    if dados.sync_calendar is not None:
        if dados.sync_calendar and not capacidades.get("read_appointments"):
            raise HTTPException(status_code=422, detail="Esta conta não tem agenda para sincronizar.")
        item.sync_calendar = dados.sync_calendar
    if dados.sync_mail is not None:
        if dados.sync_mail and not capacidades.get("read_mail"):
            raise HTTPException(status_code=422, detail="Esta conta não tem e-mail conectado.")
        item.sync_mail = dados.sync_mail
    if dados.contacts is not None:
        if dados.contacts and not capacidades.get("read_contacts"):
            raise HTTPException(status_code=422, detail="Esta conta não sincroniza contatos.")
        item.contacts_enabled = dados.contacts

    _audit(db, user, "sync_preferences_changed", "calendar_integration", item.id, {
        "provider": item.provider, "sync_calendar": item.sync_calendar,
        "sync_mail": item.sync_mail, "contacts_enabled": item.contacts_enabled,
    })
    db.commit(); db.refresh(item)
    return {
        "id": item.id, "sync_calendar": item.sync_calendar,
        "sync_mail": item.sync_mail, "contacts_enabled": item.contacts_enabled,
    }


@router.delete("/integrations/{integration_id}", status_code=204)
def disconnect_external_account(integration_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    item = _integration(db, integration_id, user.id)
    disconnect_integration(db, item)
    db.query(ExternalContact).filter(ExternalContact.integration_id == item.id).update({ExternalContact.deleted: True})
    _audit(db, user, "external_account_disconnected", "calendar_integration", item.id, {"provider": item.provider})
    db.commit()


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
