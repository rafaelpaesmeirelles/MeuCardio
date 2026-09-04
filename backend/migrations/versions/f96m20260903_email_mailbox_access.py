"""Acesso delegado a caixas nativas CorVIA Mail.

Revision ID: f96m20260903
Revises: f95c20260902
Create Date: 2026-09-03

Permite que um assinante gerencie mais de uma caixa @corvia.med.br sem
transferir a titularidade original de nenhuma delas. O caso inicial aprovado
é rafael@corvia.med.br -> contato@corvia.med.br.
"""
from alembic import op
import sqlalchemy as sa

revision = "f96m20260903"
down_revision = "f95c20260902"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "email_mailbox_access",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("owner_user_id", sa.Integer(), nullable=False),
        sa.Column("email_account_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["email_account_id"], ["email_accounts.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("owner_user_id", "email_account_id", name="uq_email_mailbox_access_owner_account"),
    )
    op.create_index("ix_email_mailbox_access_owner", "email_mailbox_access", ["owner_user_id"])
    op.create_index("ix_email_mailbox_access_account", "email_mailbox_access", ["email_account_id"])

    # Delegação inicial solicitada explicitamente pelo administrador. A carga é
    # idempotente e só acontece se as duas caixas já existirem no banco.
    op.execute(
        """
        INSERT INTO email_mailbox_access (owner_user_id, email_account_id, created_at)
        SELECT pessoal.user_id, empresa.id, CURRENT_TIMESTAMP
        FROM email_accounts AS pessoal
        JOIN email_accounts AS empresa ON empresa.email_address = 'contato@corvia.med.br'
        WHERE pessoal.email_address = 'rafael@corvia.med.br'
        ON CONFLICT (owner_user_id, email_account_id) DO NOTHING
        """
    )


def downgrade() -> None:
    op.drop_index("ix_email_mailbox_access_account", table_name="email_mailbox_access")
    op.drop_index("ix_email_mailbox_access_owner", table_name="email_mailbox_access")
    op.drop_table("email_mailbox_access")
