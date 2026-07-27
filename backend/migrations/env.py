"""Ambiente do Alembic — usa a mesma configuração e os mesmos modelos do app,
pra nunca ficar dessincronizado do que o backend realmente espera."""

import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import settings  # noqa: E402
from app.core.db import Base  # noqa: E402
import app.models  # noqa: E402, F401 — registra todas as tabelas em Base.metadata

config = context.config
config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Índices criados por SQL cru em app/services/bootstrap.py (GIN full-text, GIN
# trigram e hnsw do pgvector). Não existem nos modelos, então o autogenerate os
# enxerga como "sobra" e gera um drop_index a cada migração nova — foi assim que
# a f95465113955 quase levou junto a busca semântica e a busca textual.
INDICES_FORA_DO_METADATA = {
    "documents_search_idx",
    "documents_trgm_idx",
    "document_chunks_embedding_idx",
}


def include_object(object_, name, type_, reflected, compare_to):
    if type_ == "index" and name in INDICES_FORA_DO_METADATA:
        return False
    return True


def run_migrations_offline() -> None:
    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
