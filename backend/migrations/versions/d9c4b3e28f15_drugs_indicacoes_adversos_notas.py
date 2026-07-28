"""drugs: indicações, efeitos adversos e notas

O modelo `drugs` não tinha campo para indicação nem para efeito adverso — dois
dados centrais num comparador de medicamento. A extração dos documentos de
content/Farmacologia mostrou que essa informação existe e estava escrita: 78
seções de indicação e 59 de efeitos adversos. `notes` guarda o restante do
conteúdo curado com o título de origem como chave.

Revision ID: d9c4b3e28f15
Revises: c5a2f81b6e07
Create Date: 2026-07-28 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'd9c4b3e28f15'
down_revision = 'c5a2f81b6e07'
branch_labels = None
depends_on = None

COLUNAS = [
    ('indications', postgresql.ARRAY(sa.String())),
    ('adverse_effects', postgresql.ARRAY(sa.String())),
    ('notes', postgresql.JSONB()),
    ('published', sa.Boolean()),
]


def upgrade() -> None:
    existentes = {c["name"] for c in sa.inspect(op.get_bind()).get_columns("drugs")}
    for nome, tipo in COLUNAS:
        if nome not in existentes:
            servidor = sa.text("false") if nome == "published" else None
            op.add_column('drugs', sa.Column(nome, tipo, nullable=True,
                                             server_default=servidor))
    indices = {i["name"] for i in sa.inspect(op.get_bind()).get_indexes("drugs")}
    if "ix_drugs_published" not in indices:
        op.create_index("ix_drugs_published", "drugs", ["published"])


def downgrade() -> None:
    existentes = {c["name"] for c in sa.inspect(op.get_bind()).get_columns("drugs")}
    for nome, _ in reversed(COLUNAS):
        if nome in existentes:
            op.drop_column('drugs', nome)
