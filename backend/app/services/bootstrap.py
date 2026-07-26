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
