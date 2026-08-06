"""Certificado A1 do médico (Trabalho 7 — assinatura digital, provedor
A1_ARQUIVO).

Revision ID: f62d20260806
Revises: f61c20260806
Create Date: 2026-08-06
"""

from alembic import op
import sqlalchemy as sa

revision = "f62d20260806"
down_revision = "f61c20260806"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "digital_certificates",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("arquivo_nome", sa.String(120), nullable=False),
        sa.Column("senha_cifrada", sa.LargeBinary(), nullable=False),
        sa.Column("titular_cn", sa.String(255), nullable=False),
        sa.Column("numero_serie", sa.String(80), nullable=False),
        sa.Column("valido_ate", sa.DateTime(timezone=True), nullable=False),
        sa.Column("certificadora", sa.String(120), nullable=True),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_digital_certificates_owner_id", "digital_certificates", ["owner_id"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_digital_certificates_owner_id", table_name="digital_certificates")
    op.drop_table("digital_certificates")
