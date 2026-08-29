"""Biblioteca científica privada por assinante.

Revision ID: f86b20260829
Revises: f86a20260829
Create Date: 2026-08-29
"""
from alembic import op
import sqlalchemy as sa

revision = "f86b20260829"
down_revision = "f86a20260829"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "scientific_user_documents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("storage_key", sa.String(length=100), nullable=False),
        sa.Column("original_name_cifrado", sa.LargeBinary(), nullable=False),
        sa.Column("display_title_cifrado", sa.LargeBinary(), nullable=True),
        sa.Column("media_type", sa.String(length=120), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("sha256", sa.String(length=64), nullable=False),
        sa.Column("document_type", sa.String(length=40), nullable=False),
        sa.Column("language", sa.String(length=20), nullable=True),
        sa.Column("doi", sa.String(length=160), nullable=True),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("extracted_text_cifrado", sa.LargeBinary(), nullable=True),
        sa.Column("translated_text_cifrado", sa.LargeBinary(), nullable=True),
        sa.Column("analysis_cifrado", sa.LargeBinary(), nullable=True),
        sa.Column("analysis_status", sa.String(length=24), nullable=False),
        sa.Column("analysis_error", sa.String(length=160), nullable=True),
        sa.Column("incorporation_recommended", sa.Boolean(), nullable=False),
        sa.Column("incorporation_status", sa.String(length=24), nullable=False),
        sa.Column("consented_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("incorporated_document_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("size_bytes > 0", name="ck_scientific_user_documents_size_positive"),
        sa.CheckConstraint(
            "analysis_status IN ('pendente','processando','concluido','erro')",
            name="ck_scientific_user_documents_analysis_status",
        ),
        sa.CheckConstraint(
            "incorporation_status IN ('nao_avaliado','nao_recomendado','aguardando_consentimento','consentido','incorporado','duplicado')",
            name="ck_scientific_user_documents_incorporation_status",
        ),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["incorporated_document_id"], ["documents.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("owner_id", "sha256", name="uq_scientific_user_document_owner_sha"),
        sa.UniqueConstraint("storage_key"),
    )
    op.create_index("ix_scientific_user_documents_owner_id", "scientific_user_documents", ["owner_id"])
    op.create_index("ix_scientific_user_documents_sha256", "scientific_user_documents", ["sha256"])
    op.create_index("ix_scientific_user_documents_document_type", "scientific_user_documents", ["document_type"])
    op.create_index("ix_scientific_user_documents_doi", "scientific_user_documents", ["doi"])
    op.create_index("ix_scientific_user_documents_analysis_status", "scientific_user_documents", ["analysis_status"])
    op.create_index("ix_scientific_user_documents_incorporation_status", "scientific_user_documents", ["incorporation_status"])
    op.create_index("ix_scientific_user_documents_incorporated_document_id", "scientific_user_documents", ["incorporated_document_id"])


def downgrade() -> None:
    op.drop_table("scientific_user_documents")
