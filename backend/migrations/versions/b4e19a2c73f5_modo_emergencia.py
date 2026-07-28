"""Tabela `emergency_protocols` — curadoria do Modo Emergência (Tarefa 15).

Idempotente: este banco já teve `alembic_version` fora de sincronia com o
schema real, e migração que assume o estado do catálogo em vez de conferir
reproduz aquele incidente.

Revision ID: b4e19a2c73f5
Revises: a2f47d81c6b9
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "b4e19a2c73f5"
down_revision = "a2f47d81c6b9"
branch_labels = None
depends_on = None

TABELA = "emergency_protocols"


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
        sa.Column("gatilho", sa.String(length=400), nullable=True),
        sa.Column("ordem", sa.Integer(), nullable=False, server_default="99"),
        sa.Column("documento_slug", sa.String(length=255), nullable=False),
        sa.Column("fluxograma_slug", sa.String(length=255), nullable=True),
        sa.Column("relacionados", postgresql.ARRAY(sa.String()), nullable=False,
                  server_default=sa.text("'{}'::varchar[]")),
        sa.Column("review_status", sa.String(length=40), nullable=False,
                  server_default="pendente_revisao"),
        # Nasce despublicado. Qual protocolo aparece na tela de emergência é
        # decisão clínica, não efeito colateral de uma migração.
        sa.Column("published", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.text("now()")),
        sa.UniqueConstraint("slug", name="uq_emergency_protocols_slug"),
    )
    op.create_index("ix_emergency_protocols_slug", TABELA, ["slug"])
    op.create_index("ix_emergency_protocols_ordem", TABELA, ["ordem"])
    op.create_index("ix_emergency_protocols_published", TABELA, ["published"])
    op.create_index("ix_emergency_protocols_documento_slug", TABELA, ["documento_slug"])


def downgrade() -> None:
    if _existe(TABELA):
        op.drop_table(TABELA)
