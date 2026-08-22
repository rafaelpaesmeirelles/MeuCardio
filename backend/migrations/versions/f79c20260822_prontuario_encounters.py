"""Núcleo de atendimentos do Prontuário Eletrônico CorVIA.

Revision ID: f79c20260822
Revises: f78b20260821
Create Date: 2026-08-22
"""

from alembic import op
import sqlalchemy as sa


revision = "f79c20260822"
down_revision = "f78b20260821"
branch_labels = None
depends_on = None


_TABLE = "clinical_encounters"


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if _TABLE in inspector.get_table_names():
        return

    op.create_table(
        _TABLE,
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("patient_profile_id", sa.Integer(), nullable=False),
        sa.Column("appointment_id", sa.Integer(), nullable=True),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.Column("encounter_type", sa.String(length=40), nullable=False, server_default="consulta"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="draft"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finalized_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("amendment_of_id", sa.Integer(), nullable=True),
        sa.Column("amendment_reason_cifrado", sa.LargeBinary(), nullable=True),
        sa.Column("chief_complaint_cifrado", sa.LargeBinary(), nullable=True),
        sa.Column("anamnesis_cifrado", sa.LargeBinary(), nullable=True),
        sa.Column("physical_exam_cifrado", sa.LargeBinary(), nullable=True),
        sa.Column("assessment_cifrado", sa.LargeBinary(), nullable=True),
        sa.Column("plan_cifrado", sa.LargeBinary(), nullable=True),
        sa.Column("vital_signs_cifrado", sa.LargeBinary(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["patient_profile_id"], ["patient_profiles.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["appointment_id"], ["appointments.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["amendment_of_id"], ["clinical_encounters.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("owner_id", "appointment_id", name="uq_encounter_owner_appointment"),
    )
    op.create_index("ix_clinical_encounters_owner_id", _TABLE, ["owner_id"], unique=False)
    op.create_index("ix_clinical_encounters_patient_profile_id", _TABLE, ["patient_profile_id"], unique=False)
    op.create_index("ix_clinical_encounters_appointment_id", _TABLE, ["appointment_id"], unique=False)
    op.create_index("ix_clinical_encounters_author_id", _TABLE, ["author_id"], unique=False)
    op.create_index("ix_clinical_encounters_status", _TABLE, ["status"], unique=False)
    op.create_index("ix_clinical_encounters_finalized_at", _TABLE, ["finalized_at"], unique=False)
    op.create_index("ix_clinical_encounters_amendment_of_id", _TABLE, ["amendment_of_id"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    if _TABLE in sa.inspect(bind).get_table_names():
        op.drop_table(_TABLE)
