"""Agenda Integrada bidirecional, configuração e sincronização segura.

Revision ID: f49a20260805
Revises: f48a20260805
Create Date: 2026-08-05
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "f49a20260805"
down_revision = "f48a20260805"
branch_labels = None
depends_on = None


def _timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    ]


def upgrade() -> None:
    op.create_table(
        "calendar_locations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("timezone", sa.String(80), nullable=False, server_default="America/Sao_Paulo"),
        sa.Column("address", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("phone", sa.String(30), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("default_arrival_buffer_minutes", sa.Integer(), nullable=False, server_default="15"),
        sa.Column("color", sa.String(16), nullable=False, server_default="#087E8B"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        *_timestamps(),
        sa.UniqueConstraint("owner_id", "name", name="uq_calendar_location_owner_name"),
        sa.CheckConstraint("latitude IS NULL OR latitude BETWEEN -90 AND 90", name="ck_location_latitude"),
        sa.CheckConstraint("longitude IS NULL OR longitude BETWEEN -180 AND 180", name="ck_location_longitude"),
        sa.CheckConstraint("default_arrival_buffer_minutes BETWEEN 0 AND 180", name="ck_location_arrival_buffer"),
    )
    op.create_index("ix_calendar_locations_owner_id", "calendar_locations", ["owner_id"])
    op.create_index("ix_calendar_locations_active", "calendar_locations", ["active"])

    op.create_table(
        "scheduling_services",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("location_id", sa.Integer(), sa.ForeignKey("calendar_locations.id", ondelete="SET NULL"), nullable=True),
        sa.Column("code", sa.String(80), nullable=False),
        sa.Column("name", sa.String(180), nullable=False),
        sa.Column("category", sa.String(80), nullable=False, server_default="consulta"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("duration_minutes", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("buffer_before_minutes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("buffer_after_minutes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("slot_interval_minutes", sa.Integer(), nullable=False, server_default="15"),
        sa.Column("visit_mode", sa.String(30), nullable=False, server_default="presencial"),
        sa.Column("payment_mode", sa.String(30), nullable=False, server_default="particular"),
        sa.Column("private_price_cents", sa.Integer(), nullable=True),
        sa.Column("currency", sa.String(3), nullable=False, server_default="BRL"),
        sa.Column("accepts_insurance", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("allow_extra_slot", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("max_extra_slots", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("color", sa.String(16), nullable=False, server_default="#087E8B"),
        sa.Column("external_mappings", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        *_timestamps(),
        sa.UniqueConstraint("owner_id", "code", name="uq_scheduling_service_owner_code"),
        sa.CheckConstraint("duration_minutes BETWEEN 5 AND 1440", name="ck_service_duration"),
        sa.CheckConstraint("slot_interval_minutes BETWEEN 5 AND 240", name="ck_service_slot_interval"),
        sa.CheckConstraint("private_price_cents IS NULL OR private_price_cents >= 0", name="ck_service_price"),
    )
    op.create_index("ix_scheduling_services_owner_id", "scheduling_services", ["owner_id"])
    op.create_index("ix_scheduling_services_location_id", "scheduling_services", ["location_id"])
    op.create_index("ix_scheduling_services_active", "scheduling_services", ["active"])

    op.create_table(
        "scheduling_resources",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("location_id", sa.Integer(), sa.ForeignKey("calendar_locations.id", ondelete="SET NULL"), nullable=True),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("resource_type", sa.String(40), nullable=False, server_default="sala"),
        sa.Column("capacity", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("metadata", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("owner_id", "name", name="uq_scheduling_resource_owner_name"),
        sa.CheckConstraint("capacity > 0", name="ck_scheduling_resource_capacity"),
    )
    for column in ("owner_id", "location_id", "active"):
        op.create_index(f"ix_scheduling_resources_{column}", "scheduling_resources", [column])

    op.create_table(
        "service_resource_requirements",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("service_id", sa.Integer(), sa.ForeignKey("scheduling_services.id", ondelete="CASCADE"), nullable=False),
        sa.Column("resource_id", sa.Integer(), sa.ForeignKey("scheduling_resources.id", ondelete="CASCADE"), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("required", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.UniqueConstraint("service_id", "resource_id", name="uq_service_resource"),
        sa.CheckConstraint("quantity > 0", name="ck_service_resource_quantity"),
    )
    op.create_index("ix_service_resource_requirements_service_id", "service_resource_requirements", ["service_id"])
    op.create_index("ix_service_resource_requirements_resource_id", "service_resource_requirements", ["resource_id"])

    op.create_table(
        "availability_rules",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("location_id", sa.Integer(), sa.ForeignKey("calendar_locations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("service_id", sa.Integer(), sa.ForeignKey("scheduling_services.id", ondelete="CASCADE"), nullable=True),
        sa.Column("weekday", sa.Integer(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("label", sa.String(160), nullable=False, server_default="Rotina de trabalho"),
        sa.Column("routine_type", sa.String(30), nullable=False, server_default="atendimento"),
        sa.Column("visit_mode", sa.String(30), nullable=False, server_default="presencial"),
        sa.Column("arrival_buffer_minutes", sa.Integer(), nullable=False, server_default="15"),
        sa.Column("planning_notes", sa.String(500), nullable=True),
        sa.Column("slot_interval_minutes", sa.Integer(), nullable=False, server_default="15"),
        sa.Column("valid_from", sa.Date(), nullable=True),
        sa.Column("valid_until", sa.Date(), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("weekday BETWEEN 0 AND 6", name="ck_availability_weekday"),
        sa.CheckConstraint("end_time > start_time", name="ck_availability_time_range"),
        sa.CheckConstraint("slot_interval_minutes BETWEEN 5 AND 240", name="ck_availability_interval"),
        sa.CheckConstraint("arrival_buffer_minutes BETWEEN 0 AND 180", name="ck_availability_arrival_buffer"),
    )
    for column in ("owner_id", "location_id", "service_id", "active"):
        op.create_index(f"ix_availability_rules_{column}", "availability_rules", [column])

    op.create_table(
        "availability_exceptions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("location_id", sa.Integer(), sa.ForeignKey("calendar_locations.id", ondelete="CASCADE"), nullable=True),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("exception_type", sa.String(30), nullable=False, server_default="bloqueio"),
        sa.Column("reason", sa.String(300), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("ends_at > starts_at", name="ck_availability_exception_range"),
    )
    for column in ("owner_id", "location_id", "starts_at", "ends_at"):
        op.create_index(f"ix_availability_exceptions_{column}", "availability_exceptions", [column])

    op.create_table(
        "calendar_delegations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("professional_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("delegate_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("can_view", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("can_create", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("can_reschedule", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("can_cancel", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("can_configure", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("professional_id", "delegate_user_id", name="uq_calendar_delegation"),
        sa.CheckConstraint("professional_id <> delegate_user_id", name="ck_calendar_delegation_distinct"),
    )
    op.create_index("ix_calendar_delegations_professional_id", "calendar_delegations", ["professional_id"])
    op.create_index("ix_calendar_delegations_delegate_user_id", "calendar_delegations", ["delegate_user_id"])

    op.create_table(
        "mobility_preferences",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("consent_version", sa.String(40), nullable=True),
        sa.Column("consent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("automatic_foreground_refresh", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("refresh_interval_minutes", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("travel_mode", sa.String(30), nullable=False, server_default="driving"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("owner_id", name="uq_mobility_preferences_owner_id"),
        sa.CheckConstraint("refresh_interval_minutes BETWEEN 2 AND 60", name="ck_mobility_refresh_interval"),
    )
    op.create_index("ix_mobility_preferences_owner_id", "mobility_preferences", ["owner_id"])

    op.create_table(
        "calendar_integrations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("provider", sa.String(40), nullable=False),
        sa.Column("display_name", sa.String(160), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="draft"),
        sa.Column("sync_strategy", sa.String(40), nullable=False, server_default="external_authoritative"),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("write_enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("credentials_cipher", sa.LargeBinary(), nullable=True),
        sa.Column("cursor_cipher", sa.LargeBinary(), nullable=True),
        sa.Column("configuration", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("capabilities", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("consent_version", sa.String(40), nullable=True),
        sa.Column("consent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_sync_started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_sync_finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_success_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error_code", sa.String(80), nullable=True),
        sa.Column("last_error_message", sa.String(500), nullable=True),
        *_timestamps(),
        sa.UniqueConstraint("owner_id", "provider", "display_name", name="uq_calendar_integration_owner"),
    )
    for column in ("owner_id", "provider", "status", "enabled"):
        op.create_index(f"ix_calendar_integrations_{column}", "calendar_integrations", [column])

    op.create_table(
        "external_patient_links",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("integration_id", sa.Integer(), sa.ForeignKey("calendar_integrations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("patient_id", sa.Integer(), sa.ForeignKey("patients.id", ondelete="SET NULL"), nullable=True),
        sa.Column("external_patient_id", sa.String(255), nullable=False),
        sa.Column("link_status", sa.String(30), nullable=False, server_default="pending"),
        sa.Column("matched_by", sa.String(40), nullable=True),
        sa.Column("consent_at", sa.DateTime(timezone=True), nullable=True),
        *_timestamps(),
        sa.UniqueConstraint("integration_id", "external_patient_id", name="uq_external_patient_provider_id"),
    )
    for column in ("owner_id", "integration_id", "patient_id"):
        op.create_index(f"ix_external_patient_links_{column}", "external_patient_links", [column])

    appointment_columns = (
        sa.Column("patient_email_cipher", sa.LargeBinary(), nullable=True),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("location_id", sa.Integer(), sa.ForeignKey("calendar_locations.id", ondelete="SET NULL"), nullable=True),
        sa.Column("service_id", sa.Integer(), sa.ForeignKey("scheduling_services.id", ondelete="SET NULL"), nullable=True),
        sa.Column("integration_id", sa.Integer(), sa.ForeignKey("calendar_integrations.id", ondelete="SET NULL"), nullable=True),
        sa.Column("external_practitioner_id", sa.String(255), nullable=True),
        sa.Column("external_appointment_id", sa.String(255), nullable=True),
        sa.Column("external_version", sa.String(255), nullable=True),
        sa.Column("external_updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("source", sa.String(30), nullable=False, server_default="corvia"),
        sa.Column("sync_status", sa.String(30), nullable=False, server_default="local_only"),
        sa.Column("sync_error", sa.String(500), nullable=True),
        sa.Column("timezone", sa.String(80), nullable=False, server_default="America/Sao_Paulo"),
        sa.Column("visit_mode", sa.String(30), nullable=False, server_default="presencial"),
        sa.Column("payment_mode", sa.String(30), nullable=False, server_default="nao_informado"),
        sa.Column("insurance_name", sa.String(160), nullable=True),
        sa.Column("price_cents", sa.Integer(), nullable=True),
        sa.Column("currency", sa.String(3), nullable=False, server_default="BRL"),
        sa.Column("confirmation_status", sa.String(30), nullable=False, server_default="not_requested"),
        sa.Column("conflict_reason", sa.String(500), nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    for column in appointment_columns:
        op.add_column("appointments", column)
    op.execute("UPDATE appointments SET ends_at = scheduled_at + duration_minutes * INTERVAL '1 minute' WHERE ends_at IS NULL")
    for column in ("ends_at", "location_id", "service_id", "integration_id", "source", "sync_status", "deleted_at"):
        op.create_index(f"ix_appointments_{column}", "appointments", [column])
    op.create_unique_constraint(
        "uq_appointment_external_identity", "appointments",
        ["integration_id", "external_practitioner_id", "external_appointment_id"],
    )
    op.create_check_constraint("ck_appointment_duration", "appointments", "duration_minutes BETWEEN 5 AND 1440")
    op.create_check_constraint("ck_appointment_price", "appointments", "price_cents IS NULL OR price_cents >= 0")

    op.create_table(
        "appointment_resources",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("appointment_id", sa.Integer(), sa.ForeignKey("appointments.id", ondelete="CASCADE"), nullable=False),
        sa.Column("resource_id", sa.Integer(), sa.ForeignKey("scheduling_resources.id", ondelete="RESTRICT"), nullable=False),
        sa.UniqueConstraint("appointment_id", "resource_id", name="uq_appointment_resource"),
    )
    op.create_index("ix_appointment_resources_appointment_id", "appointment_resources", ["appointment_id"])
    op.create_index("ix_appointment_resources_resource_id", "appointment_resources", ["resource_id"])

    op.create_table(
        "calendar_outbox_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("integration_id", sa.Integer(), sa.ForeignKey("calendar_integrations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("appointment_id", sa.Integer(), sa.ForeignKey("appointments.id", ondelete="SET NULL"), nullable=True),
        sa.Column("operation", sa.String(30), nullable=False),
        sa.Column("idempotency_key", sa.String(120), nullable=False),
        sa.Column("payload", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("status", sa.String(30), nullable=False, server_default="pending"),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("available_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("locked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error_code", sa.String(80), nullable=True),
        sa.Column("last_error_message", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("idempotency_key", name="uq_calendar_outbox_idempotency_key"),
    )
    for column in ("owner_id", "integration_id", "appointment_id", "idempotency_key", "status", "available_at"):
        op.create_index(f"ix_calendar_outbox_events_{column}", "calendar_outbox_events", [column])

    op.create_table(
        "appointment_communications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("appointment_id", sa.Integer(), sa.ForeignKey("appointments.id", ondelete="CASCADE"), nullable=False),
        sa.Column("channel", sa.String(30), nullable=False, server_default="email"),
        sa.Column("purpose", sa.String(40), nullable=False, server_default="confirmation"),
        sa.Column("status", sa.String(30), nullable=False, server_default="pending"),
        sa.Column("recipient_cipher", sa.LargeBinary(), nullable=True),
        sa.Column("consent_basis", sa.String(80), nullable=True),
        sa.Column("provider_message_id", sa.String(255), nullable=True),
        sa.Column("error_message", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
    )
    for column in ("owner_id", "appointment_id", "status"):
        op.create_index(f"ix_appointment_communications_{column}", "appointment_communications", [column])


def downgrade() -> None:
    op.drop_table("appointment_communications")
    op.drop_table("calendar_outbox_events")
    op.drop_table("appointment_resources")

    op.drop_constraint("ck_appointment_price", "appointments", type_="check")
    op.drop_constraint("ck_appointment_duration", "appointments", type_="check")
    op.drop_constraint("uq_appointment_external_identity", "appointments", type_="unique")
    for column in ("deleted_at", "sync_status", "source", "integration_id", "service_id", "location_id", "ends_at"):
        op.drop_index(f"ix_appointments_{column}", table_name="appointments")
    for column in (
        "updated_at", "deleted_at", "cancelled_at", "version", "conflict_reason",
        "confirmation_status", "currency", "price_cents", "insurance_name", "payment_mode",
        "visit_mode", "timezone", "sync_error", "sync_status", "source", "external_updated_at",
        "external_version", "external_appointment_id", "external_practitioner_id",
        "integration_id", "service_id", "location_id", "ends_at", "patient_email_cipher",
    ):
        op.drop_column("appointments", column)

    op.drop_table("external_patient_links")
    op.drop_table("calendar_integrations")
    op.drop_table("mobility_preferences")
    op.drop_table("calendar_delegations")
    op.drop_table("availability_exceptions")
    op.drop_table("availability_rules")
    op.drop_table("service_resource_requirements")
    op.drop_table("scheduling_resources")
    op.drop_table("scheduling_services")
    op.drop_table("calendar_locations")
