"""Coluna `search_vector` em galeria, exames, evidências e estudos.

Prioridade definida pelo Rafael em 29/07/2026: 103 itens publicados e invisíveis
para quem pesquisa é mais urgente que ampliar conteúdo novo.

Só a coluna entra por migração. A função de trigger e o índice GIN ficam no
`bootstrap.py`, junto com os de `documents`, porque rodam no startup e precisam
ser reaplicáveis sem migração nova — foi a decisão já tomada para `documents` e
não há motivo para divergir agora.

Idempotente: confere o catálogo antes de alterar.

Revision ID: f1c93d47b8e2
Revises: d8e42c91f3a7
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "f1c93d47b8e2"
down_revision = "d8e42c91f3a7"
branch_labels = None
depends_on = None

TABELAS = ("gallery_images", "lab_tests", "evidence_records", "scientific_studies")


def _tem_coluna(tabela: str, coluna: str) -> bool:
    insp = sa.inspect(op.get_bind())
    if not insp.has_table(tabela):
        return True          # tabela ausente: nada a fazer, e não é erro aqui
    return any(c["name"] == coluna for c in insp.get_columns(tabela))


def upgrade() -> None:
    for tabela in TABELAS:
        if not _tem_coluna(tabela, "search_vector"):
            op.add_column(tabela, sa.Column("search_vector", postgresql.TSVECTOR(),
                                            nullable=True))


def downgrade() -> None:
    for tabela in TABELAS:
        if _tem_coluna(tabela, "search_vector"):
            op.drop_column(tabela, "search_vector")
