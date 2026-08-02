"""Tarefa A: preço regulado de medicamento via CMED

Pedido do Rafael (02/08/2026), puxado da fila para agora: marca, laboratório,
apresentação e PMC (preço máximo ao consumidor) via lista oficial da CMED —
fonte obrigatória e única. Duas tabelas novas, sem mudança nas existentes:

1. `cmed_versoes` — uma linha por lista importada (a CMED publica todo mês),
   com data de publicação, hash e nº de linhas. Sem isto não dá para provar
   de qual lista veio um preço, e a Tarefa B depende de gravar snapshot por
   versão.
2. `cmed_apresentacoes` — uma linha por apresentação comercial (marca +
   dosagem + embalagem), casada por nome de substância normalizado com
   `drugs.id` quando possível (`drug_id` nulo é esperado e não é erro — ver
   `app/services/cmed_precos.py`).

`Prescription.items` (Tarefa B) não precisa de migração: já é JSONB
schemaless, os campos novos (`brand_name`, `manufacturer`, `ggrem`,
`pmc_snapshot`, `uf`, `cmed_version`) entram só pelo schema Pydantic.

Revision ID: b3f7a1c9d2e4
Revises: a1b2c3d4e5f6
Create Date: 2026-08-02 23:50:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'b3f7a1c9d2e4'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def _tabelas(bind):
    return set(sa.inspect(bind).get_table_names())


def upgrade() -> None:
    bind = op.get_bind()
    tabelas = _tabelas(bind)

    if "cmed_versoes" not in tabelas:
        op.create_table(
            "cmed_versoes",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("publicado_em", sa.String(8), nullable=False),
            sa.Column("arquivo_url", sa.Text(), nullable=False),
            sa.Column("sha256", sa.String(64), nullable=False),
            sa.Column("linhas", sa.Integer(), nullable=False),
            sa.Column("baixado_em", sa.DateTime(timezone=True), nullable=False,
                      server_default=sa.text("now()")),
        )
        op.create_index("ix_cmed_versoes_publicado_em", "cmed_versoes", ["publicado_em"])

    if "cmed_apresentacoes" not in tabelas:
        op.create_table(
            "cmed_apresentacoes",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("cmed_versao_id", sa.Integer(), sa.ForeignKey("cmed_versoes.id"), nullable=False),
            sa.Column("drug_id", sa.Integer(), sa.ForeignKey("drugs.id"), nullable=True),
            sa.Column("substancia_cmed", sa.Text(), nullable=False),
            sa.Column("laboratorio", sa.Text(), nullable=False),
            sa.Column("produto", sa.Text(), nullable=False),
            sa.Column("apresentacao", sa.Text(), nullable=False),
            sa.Column("ggrem", sa.String(30), nullable=False),
            sa.Column("registro", sa.String(30), nullable=True),
            sa.Column("ean1", sa.String(20), nullable=True),
            sa.Column("tarja", sa.String(20), nullable=True),
            sa.Column("tipo_produto", sa.Text(), nullable=True),
            sa.Column("classe_terapeutica", sa.Text(), nullable=True),
            sa.Column("restricao_hospitalar", sa.Boolean(), nullable=False, server_default=sa.false()),
            sa.Column("pmc_por_aliquota", postgresql.JSONB(astext_type=sa.Text()), nullable=False,
                      server_default="{}"),
        )
        op.create_index("ix_cmed_apresentacoes_cmed_versao_id", "cmed_apresentacoes", ["cmed_versao_id"])
        op.create_index("ix_cmed_apresentacoes_drug_id", "cmed_apresentacoes", ["drug_id"])
        op.create_index("ix_cmed_apresentacoes_substancia_cmed", "cmed_apresentacoes", ["substancia_cmed"])
        op.create_index("ix_cmed_apresentacoes_ggrem", "cmed_apresentacoes", ["ggrem"])


def downgrade() -> None:
    bind = op.get_bind()
    tabelas = _tabelas(bind)
    if "cmed_apresentacoes" in tabelas:
        op.drop_table("cmed_apresentacoes")
    if "cmed_versoes" in tabelas:
        op.drop_table("cmed_versoes")
