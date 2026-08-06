"""Consentimento do médico para o assistente de IA usar ferramentas
(agenda e CorvIA Mail do próprio usuário).

Revision ID: f52a20260806
Revises: f51a20260805
Create Date: 2026-08-06
"""

from alembic import op
import sqlalchemy as sa

revision = "f52a20260806"
down_revision = "f51a20260805"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("ia_ferramentas_consent_em", sa.DateTime(timezone=True), nullable=True))
    op.add_column("users", sa.Column("ia_ferramentas_consent_versao", sa.String(40), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "ia_ferramentas_consent_versao")
    op.drop_column("users", "ia_ferramentas_consent_em")
