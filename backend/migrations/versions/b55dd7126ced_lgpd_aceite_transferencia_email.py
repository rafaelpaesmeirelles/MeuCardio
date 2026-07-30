"""CorvIA Mail: registro do aceite LGPD (transferência internacional)

Decisão do Rafael em 30/07/2026 (CLAUDE.md, item 14b): em vez de esperar
confirmação da Zoho sobre a cláusula-padrão da ANPD, a base legal escolhida
para o uso do Zoho Mail360 (que não tem data center no Brasil) é o
consentimento específico e destacado do art. 33, VIII da LGPD. Este termo
precisa ficar registrado no cadastro do cliente — daí as duas colunas.

Revision ID: b55dd7126ced
Revises: c0410068d7f3
Create Date: 2026-07-30 02:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'b55dd7126ced'
down_revision = 'c0410068d7f3'
branch_labels = None
depends_on = None


def _colunas(bind, tabela):
    return {c["name"] for c in sa.inspect(bind).get_columns(tabela)}


def upgrade() -> None:
    bind = op.get_bind()
    existentes = _colunas(bind, "email_accounts")

    if "lgpd_aceite_em" not in existentes:
        op.add_column("email_accounts", sa.Column("lgpd_aceite_em", sa.DateTime(timezone=True), nullable=True))

    if "lgpd_aceite_versao" not in existentes:
        op.add_column("email_accounts", sa.Column("lgpd_aceite_versao", sa.String(20), nullable=True))


def downgrade() -> None:
    bind = op.get_bind()
    existentes = _colunas(bind, "email_accounts")

    if "lgpd_aceite_versao" in existentes:
        op.drop_column("email_accounts", "lgpd_aceite_versao")

    if "lgpd_aceite_em" in existentes:
        op.drop_column("email_accounts", "lgpd_aceite_em")
