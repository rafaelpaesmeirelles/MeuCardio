"""Ponte Agenda -> PatientProfile -> Encounter.

Revision ID: f80a20260822
Revises: f79c20260822
Create Date: 2026-08-22
"""
from alembic import op
import sqlalchemy as sa

revision = "f80a20260822"
down_revision = "f79c20260822"
branch_labels = None
depends_on = None

_TABLE = "appointment_clinical_flows"


def upgrade() -> None:
    bind = op.get_bind()
    if _TABLE in sa.inspect(bind).get_table_names():
        return
    op.create_table(
        _TABLE,
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("appointment_id", sa.Integer(), nullable=False),
        sa.Column("patient_profile_id", sa.Integer(), nullable=True),
        sa.Column("state", sa.String(length=20), nullable=False, server_default="scheduled"),
        sa.Column("arrived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("called_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("service_started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["appointment_id"], ["appointments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["patient_profile_id"], ["patient_profiles.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("owner_id", "appointment_id", name="uq_appointment_clinical_flow_owner_appointment"),
    )
    op.create_index("ix_appointment_clinical_flows_owner_id", _TABLE, ["owner_id"], unique=False)
    op.create_index("ix_appointment_clinical_flows_appointment_id", _TABLE, ["appointment_id"], unique=False)
    op.create_index("ix_appointment_clinical_flows_patient_profile_id", _TABLE, ["patient_profile_id"], unique=False)
    op.create_index("ix_appointment_clinical_flows_state", _TABLE, ["state"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    if _TABLE in sa.inspect(bind).get_table_names():
        op.drop_table(_TABLE)
