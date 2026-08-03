"""move search extensions, triggers and indexes to Alembic

Revision ID: d5b9f2c7a104
Revises: c4a8e6f1b3d7
Create Date: 2026-08-03
"""

from alembic import op

revision = "d5b9f2c7a104"
down_revision = "c4a8e6f1b3d7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # O comando `python -m app.commands.migrate` cria as extensões antes da
    # baseline, pois o schema inicial já contém o tipo VECTOR. Mantê-las aqui
    # também torna esta revisão autossuficiente em bancos já inicializados.
    op.execute('CREATE EXTENSION IF NOT EXISTS "vector"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pg_trgm"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "unaccent"')

    op.execute(
        """
        CREATE OR REPLACE FUNCTION documents_search_vector_update() RETURNS trigger AS $$
        BEGIN
          NEW.search_vector :=
            setweight(to_tsvector('portuguese', coalesce(NEW.title, '')), 'A') ||
            setweight(to_tsvector('portuguese', coalesce(NEW.summary, '')), 'B') ||
            setweight(to_tsvector('portuguese', array_to_string(coalesce(NEW.tags, '{}'), ' ')), 'B') ||
            setweight(to_tsvector('portuguese', coalesce(NEW.body_md, '')), 'C');
          RETURN NEW;
        END
        $$ LANGUAGE plpgsql;
        """
    )
    op.execute("DROP TRIGGER IF EXISTS documents_search_vector_trg ON documents")
    op.execute(
        """
        CREATE TRIGGER documents_search_vector_trg
        BEFORE INSERT OR UPDATE ON documents
        FOR EACH ROW EXECUTE FUNCTION documents_search_vector_update()
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS documents_search_idx ON documents USING GIN (search_vector)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS documents_trgm_idx ON documents USING GIN (title gin_trgm_ops)"
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS document_chunks_embedding_idx
        ON document_chunks USING hnsw (embedding vector_cosine_ops)
        """
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION gallery_search_vector_update() RETURNS trigger AS $$
        BEGIN
          NEW.search_vector :=
            setweight(to_tsvector('portuguese', coalesce(NEW.title, '')), 'A') ||
            setweight(to_tsvector('portuguese', coalesce(NEW.theme, '') || ' ' ||
                                  coalesce(NEW.modality, '')), 'B') ||
            setweight(to_tsvector('portuguese', array_to_string(coalesce(NEW.tags, '{}'), ' ')), 'B') ||
            setweight(to_tsvector('portuguese', coalesce(NEW.findings, '') || ' ' ||
                                  coalesce(NEW.teaching_points, '')), 'C');
          RETURN NEW;
        END $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE OR REPLACE FUNCTION lab_tests_search_vector_update() RETURNS trigger AS $$
        BEGIN
          NEW.search_vector :=
            setweight(to_tsvector('portuguese', coalesce(NEW.name, '')), 'A') ||
            setweight(to_tsvector('portuguese', coalesce(NEW.theme, '') || ' ' ||
                                  coalesce(NEW.category, '')), 'B') ||
            setweight(to_tsvector('portuguese', array_to_string(coalesce(NEW.tags, '{}'), ' ')), 'B') ||
            setweight(to_tsvector('portuguese', coalesce(NEW.what_it_measures, '') || ' ' ||
                                  coalesce(NEW.indications, '') || ' ' ||
                                  coalesce(NEW.interpretation, '') || ' ' ||
                                  coalesce(NEW.reference_range, '') || ' ' ||
                                  coalesce(NEW.limitations, '')), 'C');
          RETURN NEW;
        END $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE OR REPLACE FUNCTION evidence_search_vector_update() RETURNS trigger AS $$
        BEGIN
          NEW.search_vector :=
            setweight(to_tsvector('portuguese', coalesce(NEW.statement, '')), 'A') ||
            setweight(to_tsvector('portuguese', coalesce(NEW.theme, '') || ' ' ||
                                  coalesce(NEW.society, '') || ' ' ||
                                  coalesce(NEW.recommendation_class, '')), 'B') ||
            setweight(to_tsvector('portuguese', array_to_string(coalesce(NEW.tags, '{}'), ' ')), 'B') ||
            setweight(to_tsvector('portuguese', coalesce(NEW.guideline_title, '') || ' ' ||
                                  coalesce(NEW.reference, '')), 'C');
          RETURN NEW;
        END $$ LANGUAGE plpgsql;
        """
    )
    op.execute(
        """
        CREATE OR REPLACE FUNCTION studies_search_vector_update() RETURNS trigger AS $$
        BEGIN
          NEW.search_vector :=
            setweight(to_tsvector('portuguese', coalesce(NEW.title, '')), 'A') ||
            setweight(to_tsvector('portuguese', coalesce(NEW.theme, '') || ' ' ||
                                  coalesce(NEW.journal, '') || ' ' ||
                                  coalesce(NEW.authors, '')), 'B') ||
            setweight(to_tsvector('portuguese', array_to_string(coalesce(NEW.tags, '{}'), ' ')), 'B') ||
            setweight(to_tsvector('portuguese', coalesce(NEW.summary, '') || ' ' ||
                                  coalesce(NEW.key_findings, '') || ' ' ||
                                  coalesce(NEW.clinical_implications, '') || ' ' ||
                                  coalesce(NEW.limitations, '')), 'C');
          RETURN NEW;
        END $$ LANGUAGE plpgsql;
        """
    )

    for table, trigger, function in (
        ("gallery_images", "gallery_search_vector_trg", "gallery_search_vector_update"),
        ("lab_tests", "lab_tests_search_vector_trg", "lab_tests_search_vector_update"),
        ("evidence_records", "evidence_search_vector_trg", "evidence_search_vector_update"),
        ("scientific_studies", "studies_search_vector_trg", "studies_search_vector_update"),
    ):
        op.execute(f"DROP TRIGGER IF EXISTS {trigger} ON {table}")
        op.execute(
            f"CREATE TRIGGER {trigger} BEFORE INSERT OR UPDATE ON {table} "
            f"FOR EACH ROW EXECUTE FUNCTION {function}()"
        )

    op.execute(
        "CREATE INDEX IF NOT EXISTS gallery_search_idx ON gallery_images USING GIN (search_vector)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS lab_tests_search_idx ON lab_tests USING GIN (search_vector)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS evidence_search_idx ON evidence_records USING GIN (search_vector)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS studies_search_idx ON scientific_studies USING GIN (search_vector)"
    )

    # Triggers só atuam em INSERT/UPDATE; o backfill torna registros existentes
    # pesquisáveis e fica barato nas execuções subsequentes.
    op.execute("UPDATE gallery_images SET id = id WHERE search_vector IS NULL")
    op.execute("UPDATE lab_tests SET id = id WHERE search_vector IS NULL")
    op.execute("UPDATE evidence_records SET id = id WHERE search_vector IS NULL")
    op.execute("UPDATE scientific_studies SET id = id WHERE search_vector IS NULL")


def downgrade() -> None:
    for table, trigger in (
        ("scientific_studies", "studies_search_vector_trg"),
        ("evidence_records", "evidence_search_vector_trg"),
        ("lab_tests", "lab_tests_search_vector_trg"),
        ("gallery_images", "gallery_search_vector_trg"),
        ("documents", "documents_search_vector_trg"),
    ):
        op.execute(f"DROP TRIGGER IF EXISTS {trigger} ON {table}")

    for index in (
        "studies_search_idx",
        "evidence_search_idx",
        "lab_tests_search_idx",
        "gallery_search_idx",
        "document_chunks_embedding_idx",
        "documents_trgm_idx",
        "documents_search_idx",
    ):
        op.execute(f"DROP INDEX IF EXISTS {index}")

    for function in (
        "studies_search_vector_update",
        "evidence_search_vector_update",
        "lab_tests_search_vector_update",
        "gallery_search_vector_update",
        "documents_search_vector_update",
    ):
        op.execute(f"DROP FUNCTION IF EXISTS {function}()")

    # Extensões podem ser compartilhadas por outras tabelas ou aplicações; não
    # são removidas automaticamente no downgrade.
