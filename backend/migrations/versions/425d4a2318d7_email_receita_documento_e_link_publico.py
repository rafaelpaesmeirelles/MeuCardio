"""Tarefa 29: e-mail de destinatário (receita/documento) e link público de PDF

Decisão do Rafael em 30/07/2026: em vez de anexar o PDF clínico ao e-mail
(via CorvIA Mail/Zoho, o que reabriria o conflito com o termo LGPD da
caixa), o paciente recebe um link único e temporário. Três mudanças:

1. `prescription_recipients.email_cifrado` — e-mail do paciente na receita,
   cifrado no mesmo padrão de nome/endereço/documento.
2. `generated_documents.destinatario_email_cifrado` — idem, para
   atestado/laudo gerado a partir de modelo.
3. Tabela `document_share_links` — token de acesso público ao PDF.

Revision ID: 425d4a2318d7
Revises: b55dd7126ced
Create Date: 2026-07-30 04:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = '425d4a2318d7'
down_revision = 'b55dd7126ced'
branch_labels = None
depends_on = None


def _colunas(bind, tabela):
    return {c["name"] for c in sa.inspect(bind).get_columns(tabela)}


def _tabelas(bind):
    return set(sa.inspect(bind).get_table_names())


def upgrade() -> None:
    bind = op.get_bind()

    if "email_cifrado" not in _colunas(bind, "prescription_recipients"):
        op.add_column("prescription_recipients", sa.Column("email_cifrado", sa.LargeBinary(), nullable=True))

    if "destinatario_email_cifrado" not in _colunas(bind, "generated_documents"):
        op.add_column(
            "generated_documents",
            sa.Column("destinatario_email_cifrado", sa.LargeBinary(), nullable=True),
        )

    if "document_share_links" not in _tabelas(bind):
        op.create_table(
            "document_share_links",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("token", sa.String(64), nullable=False),
            sa.Column("tipo", sa.String(30), nullable=False),
            sa.Column("referencia_id", sa.Integer(), nullable=False),
            sa.Column("criado_por", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("primeiro_acesso_em", sa.DateTime(timezone=True), nullable=True),
            sa.Column("acessos", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                      server_default=sa.text("now()")),
        )
        op.create_index("ix_document_share_links_token", "document_share_links", ["token"], unique=True)
        op.create_index("ix_document_share_links_tipo", "document_share_links", ["tipo"])
        op.create_index("ix_document_share_links_referencia_id", "document_share_links", ["referencia_id"])
        op.create_index("ix_document_share_links_criado_por", "document_share_links", ["criado_por"])


def downgrade() -> None:
    bind = op.get_bind()

    if "document_share_links" in _tabelas(bind):
        op.drop_table("document_share_links")

    if "destinatario_email_cifrado" in _colunas(bind, "generated_documents"):
        op.drop_column("generated_documents", "destinatario_email_cifrado")

    if "email_cifrado" in _colunas(bind, "prescription_recipients"):
        op.drop_column("prescription_recipients", "email_cifrado")
