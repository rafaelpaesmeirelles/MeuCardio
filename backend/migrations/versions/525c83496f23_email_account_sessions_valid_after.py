"""Marco de revogação de sessão da caixa CorvIA Mail (issue #52, gate final).

Achado do gate final da estabilização de 09-10/08/2026: a sessão principal
(`users.sessions_valid_after`) já invalidava token emitido antes de uma
troca de senha; a sessão separada da caixa de e-mail (token `scope="email"`)
não tinha equivalente — trocar/redefinir a senha da caixa não revogava
tokens já emitidos, inclusive "permanecer conectado" (até 30 dias).

Coluna nova, nullable, additiva — sem dado a migrar (nasce `NULL` para toda
linha existente, e `current_email_account()` trata `NULL` como "nunca
revogado", preservando o comportamento de quem nunca trocou a senha da
caixa). Reversível.

Revision ID: 525c83496f23
Revises: 26751b9d12f0
Create Date: 2026-08-10
"""

from alembic import op
import sqlalchemy as sa

revision = "525c83496f23"
down_revision = "26751b9d12f0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Idempotente — mesma cautela já documentada no projeto (CLAUDE.md) para
    # sessão paralela aplicando DDL fora do alembic_version.
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    colunas = {c["name"] for c in inspector.get_columns("email_accounts")}
    if "sessions_valid_after" not in colunas:
        op.add_column(
            "email_accounts",
            sa.Column("sessions_valid_after", sa.DateTime(timezone=True), nullable=True),
        )


def downgrade() -> None:
    op.drop_column("email_accounts", "sessions_valid_after")
