"""Criação de schema, índice de busca e usuário administrador inicial."""

import logging

from sqlalchemy import text

from app.core.config import settings
from app.core.db import Base, SessionLocal, engine
from app.core.security import hash_password

log = logging.getLogger(__name__)

TRIGGER_SQL = """
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

DROP TRIGGER IF EXISTS documents_search_vector_trg ON documents;
CREATE TRIGGER documents_search_vector_trg
BEFORE INSERT OR UPDATE ON documents
FOR EACH ROW EXECUTE FUNCTION documents_search_vector_update();

CREATE INDEX IF NOT EXISTS documents_search_idx ON documents USING GIN (search_vector);
CREATE INDEX IF NOT EXISTS documents_trgm_idx ON documents USING GIN (title gin_trgm_ops);

-- Índice aproximado para busca vetorial. HNSW dá recall melhor que IVFFlat
-- neste volume e não exige treino prévio sobre os dados.
CREATE INDEX IF NOT EXISTS document_chunks_embedding_idx
  ON document_chunks USING hnsw (embedding vector_cosine_ops);
"""

# ---------------------------------------------------------- quatro frentes --
# Galeria, exames, evidências e estudos passam a ter busca de texto completo.
# Eram 103 itens publicados e invisíveis para quem pesquisa — prioridade
# definida pelo Rafael em 29/07/2026.
#
# São quatro funções e não uma genérica porque cada frente tem esquema próprio:
# exames usa `name` onde as outras usam `title`, e **evidências não tem título
# nenhum** — o que aparece na tela é o `statement`, que é texto longo. Uma função
# única obrigaria a inventar um título para evidências, e o título inventado
# apareceria no resultado de busca com cara de dado.
#
# Pesos na mesma escala de `documents`: A identifica o item, B é contexto curto
# (tema, tags, sociedade), C é o corpo.
TRIGGER_FRENTES_SQL = """
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

CREATE OR REPLACE FUNCTION evidence_search_vector_update() RETURNS trigger AS $$
BEGIN
  -- `statement` e o proprio conteudo E o que identifica o registro: peso A.
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

DROP TRIGGER IF EXISTS gallery_search_vector_trg ON gallery_images;
CREATE TRIGGER gallery_search_vector_trg BEFORE INSERT OR UPDATE ON gallery_images
FOR EACH ROW EXECUTE FUNCTION gallery_search_vector_update();

DROP TRIGGER IF EXISTS lab_tests_search_vector_trg ON lab_tests;
CREATE TRIGGER lab_tests_search_vector_trg BEFORE INSERT OR UPDATE ON lab_tests
FOR EACH ROW EXECUTE FUNCTION lab_tests_search_vector_update();

DROP TRIGGER IF EXISTS evidence_search_vector_trg ON evidence_records;
CREATE TRIGGER evidence_search_vector_trg BEFORE INSERT OR UPDATE ON evidence_records
FOR EACH ROW EXECUTE FUNCTION evidence_search_vector_update();

DROP TRIGGER IF EXISTS studies_search_vector_trg ON scientific_studies;
CREATE TRIGGER studies_search_vector_trg BEFORE INSERT OR UPDATE ON scientific_studies
FOR EACH ROW EXECUTE FUNCTION studies_search_vector_update();

CREATE INDEX IF NOT EXISTS gallery_search_idx ON gallery_images USING GIN (search_vector);
CREATE INDEX IF NOT EXISTS lab_tests_search_idx ON lab_tests USING GIN (search_vector);
CREATE INDEX IF NOT EXISTS evidence_search_idx ON evidence_records USING GIN (search_vector);
CREATE INDEX IF NOT EXISTS studies_search_idx ON scientific_studies USING GIN (search_vector);

-- A trigger so preenche o vetor em INSERT/UPDATE. As linhas que ja estavam no
-- banco ficariam com search_vector nulo e invisiveis para sempre, que e
-- exatamente o defeito que esta tarefa veio corrigir. O UPDATE abaixo dispara a
-- trigger nas existentes, e o WHERE o torna barato depois da primeira vez.
UPDATE gallery_images     SET id = id WHERE search_vector IS NULL;
UPDATE lab_tests          SET id = id WHERE search_vector IS NULL;
UPDATE evidence_records   SET id = id WHERE search_vector IS NULL;
UPDATE scientific_studies SET id = id WHERE search_vector IS NULL;
"""


def init_db() -> None:
    """Roda a cada início do backend. Desde a adoção do Alembic (ver
    ../../migrations/), mudança de esquema deve virar migração — não editar
    este arquivo para adicionar coluna nova. `create_all` fica como rede de
    segurança para instalação nova (banco vazio), mas nunca altera tabela
    que já existe, então não conflita com o Alembic."""
    import app.models  # noqa: F401  (registra as tabelas)

    Base.metadata.create_all(engine)
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS unaccent"))
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.execute(text(TRIGGER_SQL))
        conn.execute(text(TRIGGER_FRENTES_SQL))

    from app.models.user import User

    db = SessionLocal()
    try:
        if not db.query(User).filter(User.email == settings.admin_email).first():
            db.add(User(
                email=settings.admin_email.lower(),
                full_name="Administrador",
                role="admin",
                password_hash=hash_password(settings.admin_password),
            ))
            db.commit()
            log.info("Usuário administrador criado: %s", settings.admin_email)
    finally:
        db.close()
