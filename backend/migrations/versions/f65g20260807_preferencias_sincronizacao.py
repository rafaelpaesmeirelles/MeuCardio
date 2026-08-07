"""Preferência de sincronização por conta conectada (Trabalho 16, 07/08/2026).

`sync_calendar`/`sync_mail` — o que já é TECNICAMENTE possível (capabilities,
concedido no momento da conexão/OAuth) e o que o médico QUER que a Corvia
efetivamente use são coisas diferentes: uma conta Google conectada com
escopo de e-mail concedido pode, mesmo assim, ser uma conta que o médico só
quer usar para agenda. `contacts_enabled` já existe (Trabalho de Agenda
Integrada) e só ganha rota de alternar depois de conectado — sem coluna
nova para ela.

Nasce `true` nas duas (opt-out, não opt-in): é o comportamento que já
existia antes desta preferência existir — conectar já mostrava tudo que a
conta permitisse.

Revision ID: f65g20260807
Revises: f64f20260807
Create Date: 2026-08-07
"""

from alembic import op
import sqlalchemy as sa

revision = "f65g20260807"
down_revision = "f64f20260807"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "calendar_integrations",
        sa.Column("sync_calendar", sa.Boolean(), nullable=False, server_default="true"),
    )
    op.add_column(
        "calendar_integrations",
        sa.Column("sync_mail", sa.Boolean(), nullable=False, server_default="true"),
    )


def downgrade() -> None:
    op.drop_column("calendar_integrations", "sync_mail")
    op.drop_column("calendar_integrations", "sync_calendar")
