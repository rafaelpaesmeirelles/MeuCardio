"""Regras transacionais, disponibilidade e sincronização da Agenda Integrada."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.agenda import (
    AppointmentCommunication,
    AppointmentResource,
    AvailabilityException,
    AvailabilityRule,
    CalendarIntegration,
    CalendarOutboxEvent,
    CalendarLocation,
    SchedulingService,
)
from app.models.clinical_docs import Appointment
from app.services.agenda_integrada.connectors import ConnectorError, get_connector
from app.services.cofre import cifrar_campo, decifrar_campo

ACTIVE_APPOINTMENT_STATUSES = {
    "pending_external", "proposed", "pendente", "confirmado", "booked", "arrived", "realizado",
}
SYNC_STRATEGIES = {"external_authoritative", "bidirectional", "meucardio_authoritative"}


def timezone_valido(nome: str) -> str:
    try:
        ZoneInfo(nome)
    except (ZoneInfoNotFoundError, ValueError):
        raise ValueError("Fuso horário IANA inválido.") from None
    return nome


def garantir_aware(valor: datetime, nome_fuso: str) -> datetime:
    zona = ZoneInfo(timezone_valido(nome_fuso))
    if valor.tzinfo is None:
        valor = valor.replace(tzinfo=zona)
    return valor.astimezone(timezone.utc)


def fim_agendamento(inicio: datetime, duration_minutes: int) -> datetime:
    if not 5 <= duration_minutes <= 1440:
        raise ValueError("Duração precisa ficar entre 5 e 1.440 minutos.")
    return inicio + timedelta(minutes=duration_minutes)


def integration_credentials(integration: CalendarIntegration) -> dict:
    if not integration.credentials_cipher:
        return {}
    raw = decifrar_campo(integration.credentials_cipher, integration.id)
    parsed = json.loads(raw)
    if not isinstance(parsed, dict):
        raise ValueError("Credencial de integração inválida.")
    return parsed


def integration_cursor(integration: CalendarIntegration) -> str | None:
    if not integration.cursor_cipher:
        return None
    return decifrar_campo(integration.cursor_cipher, integration.id)


def store_integration_credentials(integration: CalendarIntegration, credentials: dict) -> None:
    oauth = {"access_token", "refresh_token", "expires_at", "token_type", "scope"}
    allowed = {"username", "app_specific_password"} if integration.provider == "apple_icloud" else oauth
    unknown = set(credentials) - allowed
    if unknown:
        raise ValueError(f"Campos de credencial não aceitos: {', '.join(sorted(unknown))}.")
    integration.credentials_cipher = cifrar_campo(
        json.dumps(credentials, ensure_ascii=False, separators=(",", ":")), integration.id
    )


def find_conflicts(
    db: Session,
    *,
    owner_id: int,
    starts_at: datetime,
    ends_at: datetime,
    appointment_id: int | None = None,
    resource_ids: list[int] | None = None,
) -> list[dict]:
    query = db.query(Appointment).filter(
        Appointment.owner_id == owner_id,
        Appointment.deleted_at.is_(None),
        Appointment.status.in_(ACTIVE_APPOINTMENT_STATUSES),
        Appointment.scheduled_at < ends_at,
    )
    if appointment_id is not None:
        query = query.filter(Appointment.id != appointment_id)

    resource_appointment_ids: set[int] | None = None
    if resource_ids:
        resource_appointment_ids = {
            row[0] for row in db.query(AppointmentResource.appointment_id).filter(
                AppointmentResource.resource_id.in_(resource_ids)
            ).all()
        }

    conflicts: list[dict] = []
    for item in query.order_by(Appointment.scheduled_at).all():
        item_end = item.ends_at or fim_agendamento(item.scheduled_at, item.duration_minutes)
        same_professional = starts_at < item_end and ends_at > item.scheduled_at
        same_resource = resource_appointment_ids is not None and item.id in resource_appointment_ids
        if same_professional or same_resource:
            conflicts.append({
                "appointment_id": item.id,
                "starts_at": item.scheduled_at.isoformat(),
                "ends_at": item_end.isoformat(),
                "reason": "professional" if same_professional else "resource",
            })
    return conflicts


def available_slots(
    db: Session,
    *,
    owner_id: int,
    location_id: int,
    service_id: int,
    start_date: date,
    end_date: date,
) -> list[dict]:
    if end_date < start_date or (end_date - start_date).days > 93:
        raise ValueError("O período de disponibilidade deve ter entre 1 e 93 dias.")

    location = db.query(CalendarLocation).filter(
        CalendarLocation.id == location_id, CalendarLocation.owner_id == owner_id,
        CalendarLocation.active.is_(True),
    ).first()
    service = db.query(SchedulingService).filter(
        SchedulingService.id == service_id, SchedulingService.owner_id == owner_id,
        SchedulingService.active.is_(True),
    ).first()
    if not location or not service:
        raise ValueError("Local ou serviço não encontrado.")
    zona = ZoneInfo(timezone_valido(location.timezone))

    rules = db.query(AvailabilityRule).filter(
        AvailabilityRule.owner_id == owner_id,
        AvailabilityRule.location_id == location_id,
        AvailabilityRule.active.is_(True),
        or_(AvailabilityRule.service_id.is_(None), AvailabilityRule.service_id == service_id),
    ).all()
    start_utc = datetime.combine(start_date, time.min, zona).astimezone(timezone.utc)
    end_utc = datetime.combine(end_date + timedelta(days=1), time.min, zona).astimezone(timezone.utc)
    exceptions = db.query(AvailabilityException).filter(
        AvailabilityException.owner_id == owner_id,
        or_(AvailabilityException.location_id.is_(None), AvailabilityException.location_id == location_id),
        AvailabilityException.starts_at < end_utc,
        AvailabilityException.ends_at > start_utc,
    ).all()

    result: list[dict] = []
    current = start_date
    while current <= end_date:
        for rule in rules:
            if rule.weekday != current.weekday():
                continue
            if rule.valid_from and current < rule.valid_from:
                continue
            if rule.valid_until and current > rule.valid_until:
                continue
            cursor = datetime.combine(current, rule.start_time, zona)
            limit = datetime.combine(current, rule.end_time, zona)
            interval = timedelta(minutes=rule.slot_interval_minutes or service.slot_interval_minutes)
            duration = timedelta(
                minutes=service.buffer_before_minutes + service.duration_minutes + service.buffer_after_minutes
            )
            while cursor + duration <= limit:
                clinical_start = cursor + timedelta(minutes=service.buffer_before_minutes)
                clinical_end = clinical_start + timedelta(minutes=service.duration_minutes)
                utc_start = clinical_start.astimezone(timezone.utc)
                utc_end = clinical_end.astimezone(timezone.utc)
                blocked = any(utc_start < ex.ends_at and utc_end > ex.starts_at for ex in exceptions)
                conflicts = [] if blocked else find_conflicts(
                    db, owner_id=owner_id, starts_at=utc_start, ends_at=utc_end
                )
                result.append({
                    "starts_at": utc_start,
                    "ends_at": utc_end,
                    "available": not blocked and not conflicts,
                    "block_reason": "exception" if blocked else ("appointment" if conflicts else None),
                    "extra_slot_allowed": bool(service.allow_extra_slot),
                })
                cursor += interval
        current += timedelta(days=1)
    return result


def appointment_payload(db: Session, appointment: Appointment) -> dict:
    service = db.get(SchedulingService, appointment.service_id) if appointment.service_id else None
    location = db.get(CalendarLocation, appointment.location_id) if appointment.location_id else None
    return {
        "appointment_id": appointment.id,
        "starts_at": appointment.scheduled_at.isoformat(),
        "ends_at": (appointment.ends_at or fim_agendamento(appointment.scheduled_at, appointment.duration_minutes)).isoformat(),
        "timezone": appointment.timezone,
        "patient_name": appointment.patient_name_temp,
        "service_name": service.name if service else appointment.appointment_type,
        "location_name": location.name if location else "",
        "notes": appointment.notes or "",
    }


def queue_external_operation(
    db: Session,
    *,
    appointment: Appointment,
    integration: CalendarIntegration | None,
    operation: str,
) -> CalendarOutboxEvent | None:
    if integration is None or integration.sync_strategy == "external_authoritative":
        return None
    if not integration.enabled or not integration.write_enabled or not settings.agenda_external_writes_enabled:
        appointment.sync_status = "write_disabled"
        return None
    connector = get_connector(integration.provider, {}, integration.configuration)
    capability_name = {
        "create": "create_appointment",
        "reschedule": "reschedule_appointment",
        "cancel": "cancel_appointment",
    }[operation]
    if not getattr(connector.capabilities, capability_name):
        appointment.sync_status = "unsupported_operation"
        return None

    key = f"agenda:{integration.id}:{appointment.id}:{appointment.version}:{operation}"
    existing = db.query(CalendarOutboxEvent).filter(CalendarOutboxEvent.idempotency_key == key).first()
    if existing:
        return existing
    event = CalendarOutboxEvent(
        owner_id=appointment.owner_id,
        integration_id=integration.id,
        appointment_id=appointment.id,
        operation=operation,
        idempotency_key=key,
        payload=appointment_payload(db, appointment),
    )
    db.add(event)
    appointment.sync_status = "pending_external"
    return event


def _parse_external_datetime(value: str | None) -> datetime | None:
    if not value or "T" not in value:
        return None
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def sync_integration(db: Session, integration: CalendarIntegration, *, full: bool = False, transport=None) -> dict:
    if not settings.agenda_integrations_enabled or not integration.enabled:
        raise ConnectorError("integration_disabled", "Integração desativada.", status_code=409)
    from app.services.agenda_integrada.external_accounts import ensure_fresh_credentials

    credentials = ensure_fresh_credentials(db, integration)
    connector = get_connector(integration.provider, credentials, integration.configuration, transport=transport)
    if not connector.capabilities.read_appointments:
        raise ConnectorError("read_not_supported", "Leitura de agenda não homologada.", status_code=409)

    now = datetime.now(timezone.utc)
    start = now - timedelta(days=settings.agenda_sync_lookback_days)
    end = now + timedelta(days=settings.agenda_sync_horizon_days)
    integration.last_sync_started_at = now
    integration.last_error_code = None
    integration.last_error_message = None
    db.flush()

    try:
        cursor = None if full else integration_cursor(integration)
        result = connector.pull(cursor=cursor, start=start, end=end)
        if result.full_resync_required:
            result = connector.pull(cursor=None, start=start, end=end)

        created = updated = cancelled = skipped = 0
        for external in result.appointments:
            starts_at = _parse_external_datetime(external.starts_at)
            ends_at = _parse_external_datetime(external.ends_at)
            existing = db.query(Appointment).filter(
                Appointment.integration_id == integration.id,
                Appointment.external_practitioner_id == external.practitioner_external_id,
                Appointment.external_appointment_id == external.external_id,
            ).first()
            is_cancelled = external.status.lower() in {"cancelled", "canceled", "deleted"}
            if is_cancelled:
                if existing and existing.status != "cancelado":
                    existing.status = "cancelado"
                    existing.cancelled_at = now
                    existing.sync_status = "synced"
                    existing.version += 1
                    cancelled += 1
                else:
                    skipped += 1
                continue
            if starts_at is None or ends_at is None or ends_at <= starts_at:
                skipped += 1
                continue
            duration = max(5, int((ends_at - starts_at).total_seconds() // 60))
            if existing is None:
                existing = Appointment(
                    owner_id=integration.owner_id,
                    patient_name_temp=(external.title or "Compromisso externo")[:200],
                    scheduled_at=starts_at,
                    ends_at=ends_at,
                    duration_minutes=duration,
                    appointment_type="consulta",
                    status="confirmado",
                    source=integration.provider,
                    sync_status="synced",
                    integration_id=integration.id,
                    external_practitioner_id=external.practitioner_external_id,
                    external_appointment_id=external.external_id,
                    external_version=external.version,
                    external_updated_at=_parse_external_datetime(external.external_updated_at),
                    timezone=integration.configuration.get("timezone") or settings.fuso_operacao,
                )
                db.add(existing)
                db.flush()
                created += 1
            else:
                existing.scheduled_at = starts_at
                existing.ends_at = ends_at
                existing.duration_minutes = duration
                existing.patient_name_temp = (external.title or existing.patient_name_temp or "Compromisso externo")[:200]
                existing.external_version = external.version
                existing.external_updated_at = _parse_external_datetime(external.external_updated_at)
                existing.sync_status = "synced"
                existing.sync_error = None
                existing.deleted_at = None
                existing.version += 1
                updated += 1
            conflicts = find_conflicts(
                db, owner_id=integration.owner_id, starts_at=starts_at, ends_at=ends_at,
                appointment_id=existing.id,
            )
            existing.conflict_reason = "Conflito importado da agenda externa." if conflicts else None

        if result.cursor:
            integration.cursor_cipher = cifrar_campo(result.cursor, integration.id)
        finished = datetime.now(timezone.utc)
        integration.last_sync_finished_at = finished
        integration.last_success_at = finished
        integration.status = "connected"
        integration.capabilities = asdict(connector.capabilities)
        db.commit()
        return {"created": created, "updated": updated, "cancelled": cancelled, "skipped": skipped}
    except Exception as exc:
        db.rollback()
        integration = db.get(CalendarIntegration, integration.id)
        integration.last_sync_finished_at = datetime.now(timezone.utc)
        integration.last_error_code = getattr(exc, "code", "sync_failed")
        integration.last_error_message = str(exc)[:500]
        integration.status = "error"
        db.commit()
        raise


def process_outbox_event(db: Session, event: CalendarOutboxEvent, *, transport=None) -> dict:
    if event.status == "processed":
        return {"id": event.id, "status": event.status, "appointment_id": event.appointment_id}
    if not settings.agenda_external_writes_enabled:
        raise ConnectorError("external_writes_disabled", "Escrita externa desativada globalmente.", status_code=409)
    integration = db.get(CalendarIntegration, event.integration_id)
    appointment = db.get(Appointment, event.appointment_id) if event.appointment_id else None
    if not integration or not appointment or integration.owner_id != event.owner_id:
        raise ConnectorError("outbox_target_missing", "Destino da operação não existe.", status_code=409)
    if not integration.enabled or not integration.write_enabled:
        raise ConnectorError("external_writes_disabled", "Escrita desativada nesta integração.", status_code=409)

    from app.services.agenda_integrada.external_accounts import ensure_fresh_credentials

    connector = get_connector(
        integration.provider, ensure_fresh_credentials(db, integration), integration.configuration, transport=transport
    )
    event.status = "processing"
    event.locked_at = datetime.now(timezone.utc)
    event.attempts += 1
    db.flush()
    try:
        if event.operation == "create":
            response = connector.create(event.payload, idempotency_key=event.idempotency_key)
            appointment.external_appointment_id = str(response.get("id") or "") or appointment.external_appointment_id
            appointment.status = "confirmado"
            appointment.confirmation_status = "confirmed"
            if appointment.patient_email_cipher and not db.query(AppointmentCommunication).filter(
                AppointmentCommunication.appointment_id == appointment.id,
                AppointmentCommunication.purpose == "confirmation",
            ).first():
                db.add(AppointmentCommunication(
                    owner_id=appointment.owner_id,
                    appointment_id=appointment.id,
                    channel="email",
                    purpose="confirmation",
                    status="pending",
                    recipient_cipher=appointment.patient_email_cipher,
                    consent_basis="explicit_schedule_email",
                ))
        elif event.operation == "reschedule":
            if not appointment.external_appointment_id:
                raise ConnectorError("external_identity_missing", "Agendamento externo ainda não foi criado.", status_code=409)
            response = connector.reschedule(
                appointment.external_appointment_id, event.payload, version=appointment.external_version
            )
        elif event.operation == "cancel":
            if not appointment.external_appointment_id:
                raise ConnectorError("external_identity_missing", "Agendamento externo ainda não foi criado.", status_code=409)
            response = connector.cancel(
                appointment.external_appointment_id, reason=appointment.notes, version=appointment.external_version
            )
        else:
            raise ConnectorError("invalid_operation", "Operação de outbox inválida.", status_code=422)
        appointment.external_version = response.get("etag") or response.get("changeKey") or appointment.external_version
        appointment.sync_status = "synced"
        appointment.sync_error = None
        event.status = "processed"
        event.processed_at = datetime.now(timezone.utc)
        event.last_error_code = None
        event.last_error_message = None
        db.commit()
        return {"id": event.id, "status": event.status, "appointment_id": appointment.id}
    except Exception as exc:
        retryable = bool(getattr(exc, "retryable", False))
        event.status = "retry" if retryable and event.attempts < settings.agenda_outbox_max_attempts else "failed"
        event.available_at = datetime.now(timezone.utc) + timedelta(minutes=min(60, 2 ** min(event.attempts, 6)))
        event.last_error_code = getattr(exc, "code", "write_failed")
        event.last_error_message = str(exc)[:500]
        appointment.sync_status = "sync_error"
        appointment.sync_error = str(exc)[:500]
        db.commit()
        raise
