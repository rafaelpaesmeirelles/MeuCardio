"""Preenche vetores de busca científicos legados ainda nulos.

Revision ID: f92s20260901
Revises: f91s20260901
Create Date: 2026-09-01

As consultas transversais usam diretamente os vetores persistidos para manter
os índices GIN. As triggers já garantem o preenchimento em novos INSERT/UPDATE;
este backfill idempotente cobre registros anteriores à instalação delas.
"""

from alembic import op
import sqlalchemy as sa


revision = "f92s20260901"
down_revision = "f91s20260901"
branch_labels = None
depends_on = None

SEARCH_TABLES = (
    "documents",
    "gallery_images",
    "lab_tests",
    "evidence_records",
    "scientific_studies",
)


def upgrade() -> None:
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    for table in SEARCH_TABLES:
        if not inspector.has_table(table):
            raise RuntimeError(f"expected search table is missing: {table}")
        columns = {column["name"] for column in inspector.get_columns(table)}
        if not {"id", "search_vector"}.issubset(columns):
            raise RuntimeError(f"expected search columns are missing: {table}")

        # A atribuição neutra dispara a função canônica de cada tabela, sem
        # duplicar nesta migration as regras editoriais de peso A/B/C.
        connection.execute(sa.text(
            f"UPDATE {table} SET id = id WHERE search_vector IS NULL"
        ))
        remaining = connection.execute(sa.text(
            f"SELECT count(*) FROM {table} WHERE search_vector IS NULL"
        )).scalar_one()
        if remaining:
            raise RuntimeError(
                f"search vector backfill incomplete: {table} has {remaining} null rows"
            )


def downgrade() -> None:
    # Backfill de dado derivado: reintroduzir NULLs degradaria a busca e não
    # representa restauração válida de estado.
    pass
