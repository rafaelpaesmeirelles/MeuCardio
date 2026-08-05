"""Compromissos manuais recorrentes e exceções pontuais.

Revision ID: f50a20260805
Revises: f49a20260805
Create Date: 2026-08-05
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "f50a20260805"
down_revision = "f49a20260805"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "calendar_commitment_series",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("location_id", sa.Integer(), sa.ForeignKey("calendar_locations.id", ondelete="SET NULL"), nullable=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("category", sa.String(40), nullable=False, server_default="compromisso"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("timezone", sa.String(80), nullable=False, server_default="America/Sao_Paulo"),
        sa.Column("starts_on", sa.Date(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("recurrence", sa.String(20), nullable=False, server_default="none"),
        sa.Column("recurrence_interval", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("weekdays", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("month_day", sa.Integer(), nullable=True),
        sa.Column("ends_on", sa.Date(), nullable=True),
        sa.Column("blocks_scheduling", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("color", sa.String(16), nullable=False, server_default="#6B4EFF"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("duration_minutes BETWEEN 5 AND 1440", name="ck_commitment_duration"),
        sa.CheckConstraint("recurrence_interval BETWEEN 1 AND 52", name="ck_commitment_interval"),
        sa.CheckConstraint("month_day IS NULL OR month_day BETWEEN 1 AND 31", name="ck_commitment_month_day"),
        sa.CheckConstraint("ends_on IS NULL OR ends_on >= starts_on", name="ck_commitment_date_range"),
    )
    for column in ("owner_id", "location_id", "starts_on", "ends_on", "recurrence", "active"):
        op.create_index(f"ix_calendar_commitment_series_{column}", "calendar_commitment_series", [column])

    op.create_table(
        "calendar_commitment_exceptions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("series_id", sa.Integer(), sa.ForeignKey("calendar_commitment_series.id", ondelete="CASCADE"), nullable=False),
        sa.Column("occurrence_date", sa.Date(), nullable=False),
        sa.Column("action", sa.String(20), nullable=False, server_default="override"),
        sa.Column("override_starts_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("override_ends_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("override_title", sa.String(200), nullable=True),
        sa.Column("override_location_id", sa.Integer(), sa.ForeignKey("calendar_locations.id", ondelete="SET NULL"), nullable=True),
        sa.Column("notes", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("series_id", "occurrence_date", name="uq_commitment_exception_occurrence"),
        sa.CheckConstraint("action IN ('cancel', 'override')", name="ck_commitment_exception_action"),
        sa.CheckConstraint(
            "action = 'cancel' OR (override_starts_at IS NOT NULL AND override_ends_at IS NOT NULL AND override_ends_at > override_starts_at)",
            name="ck_commitment_exception_override_range",
        ),
    )
    for column in ("owner_id", "series_id", "occurrence_date"):
        op.create_index(f"ix_calendar_commitment_exceptions_{column}", "calendar_commitment_exceptions", [column])


def downgrade() -> None:
    op.drop_table("calendar_commitment_exceptions")
    op.drop_table("calendar_commitment_series")
