"""ECG longitudinal e sugestão clínica multimodal revisável.

Revision ID: f84a20260822
Revises: f83a20260822
Create Date: 2026-08-22
"""
from alembic import context, op
import sqlalchemy as sa

revision = "f84a20260822"
down_revision = "f83a20260822"
branch_labels = None
depends_on = None

_ECG = "patient_ecg_records"
_SUGGESTION = "patient_clinical_ai_suggestions"


def _existing_tables() -> set[str]:
    if context.is_offline_mode():
        return set()
    return set(sa.inspect(op.get_bind()).get_table_names())


def upgrade() -> None:
    tables = _existing_tables()
    if _ECG not in tables:
        op.create_table(
            _ECG,
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("owner_id", sa.Integer(), nullable=False),
            sa.Column("patient_profile_id", sa.Integer(), nullable=False),
            sa.Column("author_id", sa.Integer(), nullable=False),
            sa.Column("source_encounter_id", sa.Integer(), nullable=True),
            sa.Column("performed_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("storage_key", sa.String(length=80), nullable=False),
            sa.Column("original_name_cifrado", sa.LargeBinary(), nullable=False),
            sa.Column("media_type", sa.String(length=40), nullable=False),
            sa.Column("size_bytes", sa.Integer(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.CheckConstraint("size_bytes > 0", name="ck_patient_ecg_records_size_positive"),
            sa.CheckConstraint(
                "media_type IN ('image/jpeg', 'image/png', 'image/webp', 'application/pdf')",
                name="ck_patient_ecg_records_media_type",
            ),
            sa.ForeignKeyConstraint(["author_id"], ["users.id"], ondelete="RESTRICT"),
            sa.ForeignKeyConstraint(
                ["owner_id"], ["users.id"], ondelete="CASCADE"
            ),
            sa.ForeignKeyConstraint(
                ["patient_profile_id"], ["patient_profiles.id"], ondelete="RESTRICT"
            ),
            sa.ForeignKeyConstraint(
                ["source_encounter_id"], ["clinical_encounters.id"], ondelete="SET NULL"
            ),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("storage_key"),
        )
        op.create_index("ix_patient_ecg_records_owner_id", _ECG, ["owner_id"])
        op.create_index("ix_patient_ecg_records_patient_profile_id", _ECG, ["patient_profile_id"])
        op.create_index("ix_patient_ecg_records_author_id", _ECG, ["author_id"])
        op.create_index("ix_patient_ecg_records_source_encounter_id", _ECG, ["source_encounter_id"])
        op.create_index("ix_patient_ecg_records_performed_at", _ECG, ["performed_at"])

    tables = _existing_tables()
    if _SUGGESTION not in tables:
        op.create_table(
            _SUGGESTION,
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("owner_id", sa.Integer(), nullable=False),
            sa.Column("patient_profile_id", sa.Integer(), nullable=False),
            sa.Column("ecg_record_id", sa.Integer(), nullable=False),
            sa.Column("requested_by", sa.Integer(), nullable=False),
            sa.Column("mode", sa.String(length=40), nullable=False),
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
            sa.CheckConstraint(
                "mode IN ('ecg_assistance', 'triage', 'emergency', 'clinical_assistant')",
                name="ck_patient_clinical_ai_suggestions_mode",
            ),
            sa.CheckConstraint(
                "status IN ('generated', 'accepted', 'rejected')",
                name="ck_patient_clinical_ai_suggestions_status",
            ),
            sa.CheckConstraint(
                "(status = 'generated' AND reviewed_at IS NULL AND reviewed_by IS NULL "
                "AND accepted_result_id IS NULL) OR "
                "(status = 'rejected' AND reviewed_at IS NOT NULL AND reviewed_by IS NOT NULL "
                "AND accepted_result_id IS NULL) OR "
                "(status = 'accepted' AND reviewed_at IS NOT NULL AND reviewed_by IS NOT NULL "
                "AND accepted_result_id IS NOT NULL)",
                name="ck_patient_clinical_ai_suggestions_review_state",
            ),
            sa.ForeignKeyConstraint(
                ["accepted_result_id"], ["patient_exam_results.id"], ondelete="RESTRICT"
            ),
            sa.ForeignKeyConstraint(
                ["ecg_record_id"], ["patient_ecg_records.id"], ondelete="RESTRICT"
            ),
            sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(
                ["patient_profile_id"], ["patient_profiles.id"], ondelete="RESTRICT"
            ),
            sa.ForeignKeyConstraint(["requested_by"], ["users.id"], ondelete="RESTRICT"),
            sa.ForeignKeyConstraint(["reviewed_by"], ["users.id"], ondelete="SET NULL"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("accepted_result_id"),
        )
        op.create_index("ix_patient_clinical_ai_suggestions_owner_id", _SUGGESTION, ["owner_id"])
        op.create_index(
            "ix_patient_clinical_ai_suggestions_patient_profile_id", _SUGGESTION,
            ["patient_profile_id"],
        )
        op.create_index("ix_patient_clinical_ai_suggestions_ecg_record_id", _SUGGESTION, ["ecg_record_id"])
        op.create_index("ix_patient_clinical_ai_suggestions_requested_by", _SUGGESTION, ["requested_by"])
        op.create_index("ix_patient_clinical_ai_suggestions_mode", _SUGGESTION, ["mode"])
        op.create_index("ix_patient_clinical_ai_suggestions_status", _SUGGESTION, ["status"])
        op.create_index("ix_patient_clinical_ai_suggestions_reviewed_by", _SUGGESTION, ["reviewed_by"])
        op.create_index(
            "uq_patient_clinical_ai_suggestions_accepted_ecg", _SUGGESTION,
            ["ecg_record_id"], unique=True, postgresql_where=sa.text("status = 'accepted'"),
        )


def downgrade() -> None:
    tables = _existing_tables()
    if context.is_offline_mode() or _SUGGESTION in tables:
        op.drop_table(_SUGGESTION)
    if context.is_offline_mode() or _ECG in tables:
        op.drop_table(_ECG)
