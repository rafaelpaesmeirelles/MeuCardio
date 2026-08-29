"""Exames multimodais longitudinais e sugestões revisáveis de IA.

Revision ID: f86c20260829
Revises: f86b20260829
Create Date: 2026-08-29
"""
from alembic import op
import sqlalchemy as sa

revision = "f86c20260829"
down_revision = "f86b20260829"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "patient_multimodal_exam_records",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("patient_profile_id", sa.Integer(), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.Column("source_encounter_id", sa.Integer(), nullable=True),
        sa.Column("performed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("exam_type", sa.String(length=60), nullable=False),
        sa.Column("storage_key", sa.String(length=100), nullable=False),
        sa.Column("original_name_cifrado", sa.LargeBinary(), nullable=False),
        sa.Column("media_type", sa.String(length=120), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("notes_cifrado", sa.LargeBinary(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("size_bytes > 0", name="ck_patient_multimodal_exam_size_positive"),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["patient_profile_id"], ["patient_profiles.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["source_encounter_id"], ["clinical_encounters.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("storage_key"),
    )
    for column in ("owner_id", "patient_profile_id", "author_id", "source_encounter_id", "performed_at", "exam_type"):
        op.create_index(f"ix_patient_multimodal_exam_records_{column}", "patient_multimodal_exam_records", [column])

    op.create_table(
        "patient_multimodal_ai_suggestions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("patient_profile_id", sa.Integer(), nullable=False),
        sa.Column("exam_record_id", sa.Integer(), nullable=False),
        sa.Column("requested_by", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("payload_cifrado", sa.LargeBinary(), nullable=False),
        sa.Column("provider", sa.String(length=30), nullable=False),
        sa.Column("model", sa.String(length=100), nullable=False),
        sa.Column("prompt_version", sa.String(length=80), nullable=False),
        sa.Column("tokens_input", sa.Integer(), nullable=False),
        sa.Column("tokens_output", sa.Integer(), nullable=False),
        sa.Column("reviewed_by", sa.Integer(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("review_note_cifrado", sa.LargeBinary(), nullable=True),
        sa.Column("accepted_result_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("status IN ('generated','accepted','rejected')", name="ck_patient_multimodal_ai_status"),
        sa.CheckConstraint(
            "(status = 'generated' AND reviewed_at IS NULL AND reviewed_by IS NULL AND accepted_result_id IS NULL) OR "
            "(status = 'rejected' AND reviewed_at IS NOT NULL AND reviewed_by IS NOT NULL AND accepted_result_id IS NULL) OR "
            "(status = 'accepted' AND reviewed_at IS NOT NULL AND reviewed_by IS NOT NULL AND accepted_result_id IS NOT NULL)",
            name="ck_patient_multimodal_ai_review_state",
        ),
        sa.ForeignKeyConstraint(["accepted_result_id"], ["patient_exam_results.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["exam_record_id"], ["patient_multimodal_exam_records.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["patient_profile_id"], ["patient_profiles.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["requested_by"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["reviewed_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("accepted_result_id"),
    )
    for column in ("owner_id", "patient_profile_id", "exam_record_id", "requested_by", "status", "reviewed_by"):
        op.create_index(f"ix_patient_multimodal_ai_suggestions_{column}", "patient_multimodal_ai_suggestions", [column])
    op.create_index(
        "uq_patient_multimodal_ai_accepted_exam",
        "patient_multimodal_ai_suggestions",
        ["exam_record_id"],
        unique=True,
        postgresql_where=sa.text("status = 'accepted'"),
    )


def downgrade() -> None:
    op.drop_table("patient_multimodal_ai_suggestions")
    op.drop_table("patient_multimodal_exam_records")
