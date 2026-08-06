"""Verificação de identidade pós-pagamento (Trabalho 11).

Revision ID: f63e20260806
Revises: f62d20260806
Create Date: 2026-08-06
"""

from alembic import op
import sqlalchemy as sa

revision = "f63e20260806"
down_revision = "f62d20260806"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "kyc_verifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("doc_profissional_frente", sa.String(120), nullable=False),
        sa.Column("doc_profissional_verso", sa.String(120), nullable=False),
        sa.Column("doc_pessoal_frente", sa.String(120), nullable=True),
        sa.Column("doc_pessoal_verso", sa.String(120), nullable=True),
        sa.Column("doc_pessoal_digital", sa.String(120), nullable=True),
        sa.Column("selfie", sa.String(120), nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="aguardando_revisao"),
        sa.Column("crm_check_status", sa.String(20), nullable=False, server_default="nao_verificado"),
        sa.Column("crm_check_detalhe", sa.String(500), nullable=True),
        sa.Column("crm_check_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column("liberado_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column("aprovado_em", sa.DateTime(timezone=True), nullable=True),
        sa.Column("aprovado_por", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("nota_revisao", sa.String(1000), nullable=True),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_kyc_verifications_owner_id", "kyc_verifications", ["owner_id"], unique=True)
    op.create_index("ix_kyc_verifications_status", "kyc_verifications", ["status"])


def downgrade() -> None:
    op.drop_index("ix_kyc_verifications_status", table_name="kyc_verifications")
    op.drop_index("ix_kyc_verifications_owner_id", table_name="kyc_verifications")
    op.drop_table("kyc_verifications")
