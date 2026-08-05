"""Domínio da Agenda Integrada.

O modelo usa o usuário profissional como tenant atual do Corvia. A separação
entre profissional e usuário delegado permite acrescentar secretárias sem
relaxar o isolamento já existente. Os nomes Schedule/Slot/Appointment seguem
os conceitos do FHIR R4, mas estas tabelas não alegam conformidade FHIR.
"""

from datetime import date, datetime, time, timezone

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Float,
    Integer,
    LargeBinary,
    String,
    Text,
    Time,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


def _agora() -> datetime:
    return datetime.now(timezone.utc)


class CalendarLocation(Base):
    __tablename__ = "calendar_locations"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(160))
    timezone: Mapped[str] = mapped_column(String(80), default="America/Sao_Paulo")
    address: Mapped[dict] = mapped_column(JSONB, default=dict)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    default_arrival_buffer_minutes: Mapped[int] = mapped_column(Integer, default=15)
    color: Mapped[str] = mapped_column(String(16), default="#087E8B")
    active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_agora)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_agora, onupdate=_agora)

    __table_args__ = (UniqueConstraint("owner_id", "name", name="uq_calendar_location_owner_name"),)


class SchedulingService(Base):
    __tablename__ = "scheduling_services"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    location_id: Mapped[int | None] = mapped_column(
        ForeignKey("calendar_locations.id", ondelete="SET NULL"), nullable=True, index=True
    )
    code: Mapped[str] = mapped_column(String(80))
    name: Mapped[str] = mapped_column(String(180))
    category: Mapped[str] = mapped_column(String(80), default="consulta")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=30)
    buffer_before_minutes: Mapped[int] = mapped_column(Integer, default=0)
    buffer_after_minutes: Mapped[int] = mapped_column(Integer, default=0)
    slot_interval_minutes: Mapped[int] = mapped_column(Integer, default=15)
    visit_mode: Mapped[str] = mapped_column(String(30), default="presencial")
    payment_mode: Mapped[str] = mapped_column(String(30), default="particular")
    private_price_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="BRL")
    accepts_insurance: Mapped[bool] = mapped_column(Boolean, default=False)
    allow_extra_slot: Mapped[bool] = mapped_column(Boolean, default=False)
    max_extra_slots: Mapped[int] = mapped_column(Integer, default=0)
    color: Mapped[str] = mapped_column(String(16), default="#087E8B")
    external_mappings: Mapped[dict] = mapped_column(JSONB, default=dict)
    active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_agora)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_agora, onupdate=_agora)

    __table_args__ = (UniqueConstraint("owner_id", "code", name="uq_scheduling_service_owner_code"),)


class SchedulingResource(Base):
    __tablename__ = "scheduling_resources"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    location_id: Mapped[int | None] = mapped_column(
        ForeignKey("calendar_locations.id", ondelete="SET NULL"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(160))
    resource_type: Mapped[str] = mapped_column(String(40), default="sala")
    capacity: Mapped[int] = mapped_column(Integer, default=1)
    metadata_json: Mapped[dict] = mapped_column("metadata", JSONB, default=dict)
    active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_agora)

    __table_args__ = (UniqueConstraint("owner_id", "name", name="uq_scheduling_resource_owner_name"),)


class ServiceResourceRequirement(Base):
    __tablename__ = "service_resource_requirements"

    id: Mapped[int] = mapped_column(primary_key=True)
    service_id: Mapped[int] = mapped_column(
        ForeignKey("scheduling_services.id", ondelete="CASCADE"), index=True
    )
    resource_id: Mapped[int] = mapped_column(
        ForeignKey("scheduling_resources.id", ondelete="CASCADE"), index=True
    )
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    required: Mapped[bool] = mapped_column(Boolean, default=True)

    __table_args__ = (UniqueConstraint("service_id", "resource_id", name="uq_service_resource"),)


class AvailabilityRule(Base):
    __tablename__ = "availability_rules"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    location_id: Mapped[int] = mapped_column(
        ForeignKey("calendar_locations.id", ondelete="CASCADE"), index=True
    )
    service_id: Mapped[int | None] = mapped_column(
        ForeignKey("scheduling_services.id", ondelete="CASCADE"), nullable=True, index=True
    )
    weekday: Mapped[int] = mapped_column(Integer)
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)
    label: Mapped[str] = mapped_column(String(160), default="Rotina de trabalho")
    routine_type: Mapped[str] = mapped_column(String(30), default="atendimento")
    visit_mode: Mapped[str] = mapped_column(String(30), default="presencial")
    arrival_buffer_minutes: Mapped[int] = mapped_column(Integer, default=15)
    planning_notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    slot_interval_minutes: Mapped[int] = mapped_column(Integer, default=15)
    valid_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    valid_until: Mapped[date | None] = mapped_column(Date, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_agora)


class AvailabilityException(Base):
    __tablename__ = "availability_exceptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    location_id: Mapped[int | None] = mapped_column(
        ForeignKey("calendar_locations.id", ondelete="CASCADE"), nullable=True, index=True
    )
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    exception_type: Mapped[str] = mapped_column(String(30), default="bloqueio")
    reason: Mapped[str | None] = mapped_column(String(300), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_agora)


class CalendarCommitmentSeries(Base):
    """Compromisso manual único ou recorrente, sem dados de paciente."""

    __tablename__ = "calendar_commitment_series"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    location_id: Mapped[int | None] = mapped_column(
        ForeignKey("calendar_locations.id", ondelete="SET NULL"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(200))
    category: Mapped[str] = mapped_column(String(40), default="compromisso")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    timezone: Mapped[str] = mapped_column(String(80), default="America/Sao_Paulo")
    starts_on: Mapped[date] = mapped_column(Date, index=True)
    start_time: Mapped[time] = mapped_column(Time)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=30)
    recurrence: Mapped[str] = mapped_column(String(20), default="none", index=True)
    recurrence_interval: Mapped[int] = mapped_column(Integer, default=1)
    weekdays: Mapped[list] = mapped_column(JSONB, default=list)
    month_day: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ends_on: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    blocks_scheduling: Mapped[bool] = mapped_column(Boolean, default=True)
    color: Mapped[str] = mapped_column(String(16), default="#6B4EFF")
    active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_agora)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_agora, onupdate=_agora)


class CalendarCommitmentException(Base):
    """Cancelamento ou alteração de uma ocorrência sem mudar a série-base."""

    __tablename__ = "calendar_commitment_exceptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    series_id: Mapped[int] = mapped_column(
        ForeignKey("calendar_commitment_series.id", ondelete="CASCADE"), index=True
    )
    occurrence_date: Mapped[date] = mapped_column(Date, index=True)
    action: Mapped[str] = mapped_column(String(20), default="override")
    override_starts_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    override_ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    override_title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    override_location_id: Mapped[int | None] = mapped_column(
        ForeignKey("calendar_locations.id", ondelete="SET NULL"), nullable=True
    )
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_agora)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_agora, onupdate=_agora)

    __table_args__ = (
        UniqueConstraint("series_id", "occurrence_date", name="uq_commitment_exception_occurrence"),
    )


class CalendarDelegation(Base):
    __tablename__ = "calendar_delegations"

    id: Mapped[int] = mapped_column(primary_key=True)
    professional_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    delegate_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    can_view: Mapped[bool] = mapped_column(Boolean, default=True)
    can_create: Mapped[bool] = mapped_column(Boolean, default=False)
    can_reschedule: Mapped[bool] = mapped_column(Boolean, default=False)
    can_cancel: Mapped[bool] = mapped_column(Boolean, default=False)
    can_configure: Mapped[bool] = mapped_column(Boolean, default=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_agora)

    __table_args__ = (
        UniqueConstraint("professional_id", "delegate_user_id", name="uq_calendar_delegation"),
    )


class MobilityPreference(Base):
    """Consentimento persistente, sem armazenar a posição atual do usuário."""

    __tablename__ = "mobility_preferences"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), unique=True, index=True
    )
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    consent_version: Mapped[str | None] = mapped_column(String(40), nullable=True)
    consent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    automatic_foreground_refresh: Mapped[bool] = mapped_column(Boolean, default=True)
    refresh_interval_minutes: Mapped[int] = mapped_column(Integer, default=5)
    travel_mode: Mapped[str] = mapped_column(String(30), default="driving")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_agora, onupdate=_agora)


class CalendarIntegration(Base):
    __tablename__ = "calendar_integrations"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    provider: Mapped[str] = mapped_column(String(40), index=True)
    display_name: Mapped[str] = mapped_column(String(160))
    status: Mapped[str] = mapped_column(String(30), default="draft", index=True)
    sync_strategy: Mapped[str] = mapped_column(String(40), default="external_authoritative")
    enabled: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    write_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    credentials_cipher: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    cursor_cipher: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    configuration: Mapped[dict] = mapped_column(JSONB, default=dict)
    capabilities: Mapped[dict] = mapped_column(JSONB, default=dict)
    consent_version: Mapped[str | None] = mapped_column(String(40), nullable=True)
    consent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_sync_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_sync_finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_success_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    last_error_message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_agora)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_agora, onupdate=_agora)

    __table_args__ = (
        UniqueConstraint("owner_id", "provider", "display_name", name="uq_calendar_integration_owner"),
    )


class ExternalPatientLink(Base):
    __tablename__ = "external_patient_links"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    integration_id: Mapped[int] = mapped_column(
        ForeignKey("calendar_integrations.id", ondelete="CASCADE"), index=True
    )
    patient_id: Mapped[int | None] = mapped_column(
        ForeignKey("patients.id", ondelete="SET NULL"), nullable=True, index=True
    )
    external_patient_id: Mapped[str] = mapped_column(String(255))
    link_status: Mapped[str] = mapped_column(String(30), default="pending")
    matched_by: Mapped[str | None] = mapped_column(String(40), nullable=True)
    consent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_agora)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_agora, onupdate=_agora)

    __table_args__ = (
        UniqueConstraint("integration_id", "external_patient_id", name="uq_external_patient_provider_id"),
    )


class AppointmentResource(Base):
    __tablename__ = "appointment_resources"

    id: Mapped[int] = mapped_column(primary_key=True)
    appointment_id: Mapped[int] = mapped_column(ForeignKey("appointments.id", ondelete="CASCADE"), index=True)
    resource_id: Mapped[int] = mapped_column(
        ForeignKey("scheduling_resources.id", ondelete="RESTRICT"), index=True
    )

    __table_args__ = (UniqueConstraint("appointment_id", "resource_id", name="uq_appointment_resource"),)


class CalendarOutboxEvent(Base):
    __tablename__ = "calendar_outbox_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    integration_id: Mapped[int] = mapped_column(
        ForeignKey("calendar_integrations.id", ondelete="CASCADE"), index=True
    )
    appointment_id: Mapped[int | None] = mapped_column(
        ForeignKey("appointments.id", ondelete="SET NULL"), nullable=True, index=True
    )
    operation: Mapped[str] = mapped_column(String(30))
    idempotency_key: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    payload: Mapped[dict] = mapped_column(JSONB, default=dict)
    status: Mapped[str] = mapped_column(String(30), default="pending", index=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    available_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_agora, index=True)
    locked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    last_error_message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_agora)


class AppointmentCommunication(Base):
    __tablename__ = "appointment_communications"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    appointment_id: Mapped[int] = mapped_column(ForeignKey("appointments.id", ondelete="CASCADE"), index=True)
    channel: Mapped[str] = mapped_column(String(30), default="email")
    purpose: Mapped[str] = mapped_column(String(40), default="confirmation")
    status: Mapped[str] = mapped_column(String(30), default="pending", index=True)
    recipient_cipher: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    consent_basis: Mapped[str | None] = mapped_column(String(80), nullable=True)
    provider_message_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    error_message: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_agora)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
