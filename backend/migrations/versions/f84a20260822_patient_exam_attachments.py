"""Arquivos originais cifrados vinculados a resultados de exames.

Revision ID: f84a20260822
Revises: f83a20260822
Create Date: 2026-08-22
"""
from alembic import op
import sqlalchemy as sa

revision = "f84a20260822"
down_revision = "f83a20260822"
branch_labels = None
depends_on = None

_TABLE = "patient_exam_attachments"


def upgrade() -> None:
    bind = op.get_bind()
    if _TABLE in sa.inspect(bind).get_table_names():
        return
    op.create_table(
        _TABLE,
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("patient_exam_result_id", sa.Integer(), nullable=False),
        sa.Column("uploaded_by", sa.Integer(), nullable=False),
        sa.Column("storage_name", sa.String(length=80), nullable=False),
        sa.Column("original_name_cifrado", sa.LargeBinary(), nullable=False),
        sa.Column("mime_type", sa.String(length=80), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["patient_exam_result_id"], ["patient_exam_results.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("storage_name", name="uq_patient_exam_attachments_storage_name"),
    )
    op.create_index("ix_patient_exam_attachments_owner_id", _TABLE, ["owner_id"], unique=False)
    op.create_index("ix_patient_exam_attachments_patient_exam_result_id", _TABLE, ["patient_exam_result_id"], unique=False)
    op.create_index("ix_patient_exam_attachments_uploaded_by", _TABLE, ["uploaded_by"], unique=False)
    op.create_index("ix_patient_exam_attachments_storage_name", _TABLE, ["storage_name"], unique=True)


def downgrade() -> None:
    bind = op.get_bind()
    if _TABLE in sa.inspect(bind).get_table_names():
        op.drop_table(_TABLE)
