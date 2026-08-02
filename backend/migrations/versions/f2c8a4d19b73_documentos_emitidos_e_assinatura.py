"""Tarefa 4: catálogo de assinatura digital e persistência do PDF emitido

Pedido do Rafael (02/08/2026): conectar os principais serviços de
assinatura digital, com o usuário escolhendo qual usar, e manter a opção de
não assinar digitalmente (carimbo e assinatura manual). Duas mudanças:

1. Tabela `documentos_emitidos` — até aqui NENHUM PDF clínico era
   persistido: os 4 pontos de emissão geravam bytes na hora e descartavam,
   e o render nem era determinístico (`pdf_documento.py` carimbava
   `datetime.now()` a cada chamada). Assinatura PAdES se liga a um
   artefato de bytes estável; sem persistir, não há o que assinar. Os
   bytes em si não vão nesta tabela — ficam cifrados no cofre existente
   (`services/cofre.py`), em `settings.documentos_dir`; aqui só a
   referência (`arquivo_nome`, `sha256`) e os metadados de auditoria.

2. `users.assinatura_metodo_preferido` — método de assinatura sugerido por
   padrão na tela de emissão. Nenhum provedor tem credencial hoje (a do
   VIDAAS foi pedida em 28/07/2026, sem retorno); só "MANUAL" funciona de
   fato — ver `app/services/assinatura/`.

Revision ID: f2c8a4d19b73
Revises: a3f6d081c9e4
Create Date: 2026-08-02 21:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'f2c8a4d19b73'
down_revision = 'a3f6d081c9e4'
branch_labels = None
depends_on = None


def _colunas(bind, tabela):
    return {c["name"] for c in sa.inspect(bind).get_columns(tabela)}


def _tabelas(bind):
    return set(sa.inspect(bind).get_table_names())


def upgrade() -> None:
    bind = op.get_bind()

    if "assinatura_metodo_preferido" not in _colunas(bind, "users"):
        op.add_column("users", sa.Column("assinatura_metodo_preferido", sa.String(20), nullable=True))

    if "documentos_emitidos" not in _tabelas(bind):
        op.create_table(
            "documentos_emitidos",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("tipo", sa.String(30), nullable=False),
            sa.Column("referencia_id", sa.Integer(), nullable=False),
            sa.Column("metodo", sa.String(20), nullable=False),
            sa.Column("nivel", sa.String(20), nullable=False),
            sa.Column("arquivo_nome", sa.String(120), nullable=False),
            sa.Column("sha256", sa.String(64), nullable=False),
            sa.Column("bytes_tam", sa.Integer(), nullable=False),
            sa.Column("assinado_em", sa.DateTime(timezone=True), nullable=True),
            sa.Column("criado_por", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
            sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False,
                      server_default=sa.text("now()")),
        )
        op.create_index("ix_documentos_emitidos_tipo", "documentos_emitidos", ["tipo"])
        op.create_index("ix_documentos_emitidos_referencia_id", "documentos_emitidos", ["referencia_id"])
        op.create_index("ix_documentos_emitidos_criado_por", "documentos_emitidos", ["criado_por"])


def downgrade() -> None:
    bind = op.get_bind()

    if "documentos_emitidos" in _tabelas(bind):
        op.drop_table("documentos_emitidos")

    if "assinatura_metodo_preferido" in _colunas(bind, "users"):
        op.drop_column("users", "assinatura_metodo_preferido")
