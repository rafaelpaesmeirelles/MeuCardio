"""Resultados longitudinais de exames do PatientProfile.

Revision ID: f83a20260822
Revises: f82a20260822
Create Date: 2026-08-22
"""
from alembic import op
import sqlalchemy as sa

revision = "f83a20260822"
down_revision = "f82a20260822"
branch_labels = None
depends_on = None

_TABLE = "patient_exam_results"


def upgrade() -> None:
    bind = op.get_bind()
    if _TABLE in sa.inspect(bind).get_table_names():
        return
    op.create_table(
        _TABLE,
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("patient_profile_id", sa.Integer(), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.Column("source_encounter_id", sa.Integer(), nullable=True),
        sa.Column("lab_test_id", sa.Integer(), nullable=True),
        sa.Column("correction_of_id", sa.Integer(), nullable=True),
        sa.Column("exam_kind", sa.String(length=30), nullable=False),
        sa.Column("performed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("payload_cifrado", sa.LargeBinary(), nullable=False),
        sa.Column("correction_reason_cifrado", sa.LargeBinary(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["patient_profile_id"], ["patient_profiles.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["source_encounter_id"], ["clinical_encounters.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["lab_test_id"], ["lab_tests.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["correction_of_id"], [_TABLE + ".id"], ondelete="RESTRICT"),
        sa.CheckConstraint(
            "exam_kind IN ('laboratorial', 'metodo_grafico', 'imagem', 'outro')",
            name="ck_patient_exam_results_kind",
        ),
        sa.CheckConstraint(
            "correction_of_id IS NULL OR correction_of_id <> id",
            name="ck_patient_exam_results_not_self_correction",
        ),
        sa.UniqueConstraint("correction_of_id", name="uq_patient_exam_results_correction_of"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_patient_exam_results_owner_id", _TABLE, ["owner_id"], unique=False)
    op.create_index("ix_patient_exam_results_patient_profile_id", _TABLE, ["patient_profile_id"], unique=False)
    op.create_index("ix_patient_exam_results_author_id", _TABLE, ["author_id"], unique=False)
    op.create_index("ix_patient_exam_results_source_encounter_id", _TABLE, ["source_encounter_id"], unique=False)
    op.create_index("ix_patient_exam_results_lab_test_id", _TABLE, ["lab_test_id"], unique=False)
    op.create_index("ix_patient_exam_results_correction_of_id", _TABLE, ["correction_of_id"], unique=False)
    op.create_index("ix_patient_exam_results_exam_kind", _TABLE, ["exam_kind"], unique=False)
    op.create_index("ix_patient_exam_results_performed_at", _TABLE, ["performed_at"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    if _TABLE in sa.inspect(bind).get_table_names():
        op.drop_table(_TABLE)
