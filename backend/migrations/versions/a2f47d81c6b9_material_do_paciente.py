"""Tabela `patient_materials` — material educativo do paciente (Tarefa 12).

Idempotente por decisão de projeto: este banco já teve `alembic_version` fora de
sincronia com o schema real, e uma migração que assume o estado do catálogo em
vez de conferir volta a produzir o mesmo incidente. Aqui a criação só acontece
se a tabela não existir.

Revision ID: a2f47d81c6b9
Revises: e5c72a90f14b
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "a2f47d81c6b9"
down_revision = "e5c72a90f14b"
branch_labels = None
depends_on = None

TABELA = "patient_materials"


def _existe(nome: str) -> bool:
    return sa.inspect(op.get_bind()).has_table(nome)


def upgrade() -> None:
    if _existe(TABELA):
        return

    op.create_table(
        TABELA,
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(length=160), nullable=False),
        sa.Column("titulo", sa.String(length=300), nullable=False),
        sa.Column("subtitulo", sa.String(length=400), nullable=True),
        sa.Column("tema", sa.String(length=80), nullable=False),
        sa.Column("documento_slug", sa.String(length=255), nullable=True),
        sa.Column("secoes", postgresql.JSONB(), nullable=False,
                  server_default=sa.text("'[]'::jsonb")),
        sa.Column("sinais_de_alerta", postgresql.ARRAY(sa.String()), nullable=False,
                  server_default=sa.text("'{}'::varchar[]")),
        sa.Column("perguntas", postgresql.ARRAY(sa.String()), nullable=False,
                  server_default=sa.text("'{}'::varchar[]")),
        sa.Column("fontes", postgresql.ARRAY(sa.String()), nullable=False,
                  server_default=sa.text("'{}'::varchar[]")),
        sa.Column("resumo", sa.Text(), nullable=True),
        sa.Column("review_status", sa.String(length=40), nullable=False,
                  server_default="pendente_revisao"),
        # Nasce despublicado, sempre. Material que vai para a mão de um leigo
        # não entra no ar por efeito colateral de uma migração.
        sa.Column("published", sa.Boolean(), nullable=False,
                  server_default=sa.text("false")),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.UniqueConstraint("slug", name="uq_patient_materials_slug"),
    )
    op.create_index("ix_patient_materials_slug", TABELA, ["slug"])
    op.create_index("ix_patient_materials_tema", TABELA, ["tema"])
    op.create_index("ix_patient_materials_published", TABELA, ["published"])
    op.create_index("ix_patient_materials_documento_slug", TABELA, ["documento_slug"])


def downgrade() -> None:
    if _existe(TABELA):
        op.drop_table(TABELA)
