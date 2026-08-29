"""Elenco do Programa Farmácia Popular do Brasil (PFPB)

Gap encontrado por sessão externa (Claude chat), 29/08/2026 — ver CLAUDE.md.
O produto já resolve preço-teto (CMED) e preço-de-mercado (K@iros); faltava
a camada de acesso/subsídio via Farmácia Popular. Duas tabelas novas, sem
mudança nas existentes — mesmo espírito de `cmed_versoes`/`cmed_apresentacoes`
(ver `b3f7a1c9d2e4_cmed_versoes_e_apresentacoes.py`), não reinvenção:

1. `farmacia_popular_versoes` — uma linha por conferência/carga do elenco
   (o PFPB não publica um arquivo único versionado e datável como a CMED,
   então o campo é "quando conferimos", não "data de publicação de arquivo").
2. `farmacia_popular_itens` — uma linha por substância+dose do elenco,
   casada por nome normalizado com `drugs.id` quando possível (`drug_id`
   nulo é esperado para itens fora do escopo cardiológico do catálogo).

Nota sobre o grafo de migrações: encadeada em `f84a20260822`, que era um dos
cinco heads simultâneos encontrados nesta sessão (`alembic heads` — condição
pré-existente, não criada nem corrigida por este commit; mesclar os heads é
tarefa separada, fora do escopo desta feature).

Revision ID: d5c9b2e1a8f6
Revises: f84a20260822
Create Date: 2026-08-29 04:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'd5c9b2e1a8f6'
down_revision = 'f84a20260822'
branch_labels = None
depends_on = None


def _tabelas(bind):
    return set(sa.inspect(bind).get_table_names())


def upgrade() -> None:
    bind = op.get_bind()
    tabelas = _tabelas(bind)

    if "farmacia_popular_versoes" not in tabelas:
        op.create_table(
            "farmacia_popular_versoes",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("conferido_em", sa.String(8), nullable=False),
            sa.Column("fontes", sa.Text(), nullable=False),
            sa.Column("observacao", sa.Text(), nullable=True),
            sa.Column("itens", sa.Integer(), nullable=False),
            sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False,
                      server_default=sa.text("now()")),
        )
        op.create_index(
            "ix_farmacia_popular_versoes_conferido_em",
            "farmacia_popular_versoes", ["conferido_em"],
        )

    if "farmacia_popular_itens" not in tabelas:
        op.create_table(
            "farmacia_popular_itens",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("farmacia_popular_versao_id", sa.Integer(),
                      sa.ForeignKey("farmacia_popular_versoes.id"), nullable=False),
            sa.Column("drug_id", sa.Integer(), sa.ForeignKey("drugs.id"), nullable=True),
            sa.Column("substancia_pfpb", sa.Text(), nullable=False),
            sa.Column("dose_referencia", sa.Text(), nullable=False),
            sa.Column("categoria", sa.String(60), nullable=False),
            sa.Column("indicacao", sa.Text(), nullable=False),
            sa.Column("criterio_acesso", sa.Text(), nullable=False),
            sa.Column("ean", sa.String(20), nullable=True),
            sa.Column("fonte_refs", sa.Text(), nullable=False),
            sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.true()),
        )
        op.create_index(
            "ix_farmacia_popular_itens_farmacia_popular_versao_id",
            "farmacia_popular_itens", ["farmacia_popular_versao_id"],
        )
        op.create_index("ix_farmacia_popular_itens_drug_id", "farmacia_popular_itens", ["drug_id"])
        op.create_index(
            "ix_farmacia_popular_itens_substancia_pfpb",
            "farmacia_popular_itens", ["substancia_pfpb"],
        )
        op.create_index("ix_farmacia_popular_itens_categoria", "farmacia_popular_itens", ["categoria"])
        op.create_index("ix_farmacia_popular_itens_ean", "farmacia_popular_itens", ["ean"])


def downgrade() -> None:
    bind = op.get_bind()
    tabelas = _tabelas(bind)
    if "farmacia_popular_itens" in tabelas:
        op.drop_table("farmacia_popular_itens")
    if "farmacia_popular_versoes" in tabelas:
        op.drop_table("farmacia_popular_versoes")
