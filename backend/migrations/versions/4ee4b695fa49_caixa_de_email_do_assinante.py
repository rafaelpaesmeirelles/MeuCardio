"""caixa de e-mail do assinante (Tarefa 28) — tabela email_accounts

Mapeia cada médico assinante à conta nativa criada no Zoho Mail360
(user_id, endereço nome@corvia.med.br e a account_key que o Mail360 devolve
na criação). Não guarda mensagem nenhuma — a caixa em si vive inteiramente no
Mail360; esta tabela só existe para saber, a partir do usuário logado na
Corvia, qual conta chamar na API.

Idempotente: confere a tabela no catálogo antes de criar, no mesmo padrão já
usado nas migrações anteriores deste banco.

Revision ID: 4ee4b695fa49
Revises: f1c93d47b8e2
Create Date: 2026-07-30 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = '4ee4b695fa49'
down_revision = 'f1c93d47b8e2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    tabelas = set(sa.inspect(bind).get_table_names())

    if "email_accounts" not in tabelas:
        op.create_table(
            "email_accounts",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("email_address", sa.String(255), nullable=False),
            sa.Column("mail360_account_key", sa.String(120), nullable=False),
            sa.Column("status", sa.String(20), nullable=False, server_default="ativa"),
            sa.Column(
                "created_at", sa.DateTime(timezone=True),
                nullable=False, server_default=sa.text("now()"),
            ),
        )
        op.create_index("ix_email_accounts_user_id", "email_accounts", ["user_id"], unique=True)
        op.create_index("ix_email_accounts_email_address", "email_accounts", ["email_address"], unique=True)
        op.create_index(
            "ix_email_accounts_mail360_account_key", "email_accounts", ["mail360_account_key"], unique=True
        )


def downgrade() -> None:
    bind = op.get_bind()
    tabelas = set(sa.inspect(bind).get_table_names())
    if "email_accounts" in tabelas:
        op.drop_table("email_accounts")
