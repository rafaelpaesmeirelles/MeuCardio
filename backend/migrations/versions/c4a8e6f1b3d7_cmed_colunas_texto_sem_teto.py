"""Tarefa A: cmed_apresentacoes.{ggrem,registro,ean1,tarja} viram Text

A primeira importação real (02/08/2026) estourou `tarja VARCHAR(20)` — a CMED
anexa nota/rodapé ao valor em algumas linhas (ex. "- (*)" não é o problema,
mas há variantes mais longas na planilha real de 25.702 linhas). Nenhum
destes quatro campos tem formato fixo garantido por norma que justifique um
teto arbitrário; a tabela está vazia (import anterior rolou tudo de volta
numa transação só), então não há dado pra migrar.

Revision ID: c4a8e6f1b3d7
Revises: b3f7a1c9d2e4
Create Date: 2026-08-03 00:20:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'c4a8e6f1b3d7'
down_revision = 'b3f7a1c9d2e4'
branch_labels = None
depends_on = None

COLUNAS = ("ggrem", "registro", "ean1", "tarja")


def upgrade() -> None:
    for coluna in COLUNAS:
        op.alter_column("cmed_apresentacoes", coluna, type_=sa.Text(), existing_nullable=True)


def downgrade() -> None:
    op.alter_column("cmed_apresentacoes", "ggrem", type_=sa.String(30), existing_nullable=True)
    op.alter_column("cmed_apresentacoes", "registro", type_=sa.String(30), existing_nullable=True)
    op.alter_column("cmed_apresentacoes", "ean1", type_=sa.String(20), existing_nullable=True)
    op.alter_column("cmed_apresentacoes", "tarja", type_=sa.String(20), existing_nullable=True)
