"""Assinatura de e-mail opcional (logo Corvia + logo/dados profissionais)
anexada ao final dos e-mails enviados pelo CorvIA Mail.

Revision ID: f53a20260806
Revises: f52a20260806
Create Date: 2026-08-06
"""

from alembic import op
import sqlalchemy as sa

revision = "f53a20260806"
down_revision = "f52a20260806"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("email_assinatura_ativa", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("users", sa.Column("email_assinatura_incluir_telefone", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("users", sa.Column("email_assinatura_incluir_endereco", sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade() -> None:
    op.drop_column("users", "email_assinatura_incluir_endereco")
    op.drop_column("users", "email_assinatura_incluir_telefone")
    op.drop_column("users", "email_assinatura_ativa")
