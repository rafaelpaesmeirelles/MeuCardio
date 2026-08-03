"""Executa o ciclo de migração do banco fora do startup da API.

As extensões precisam existir antes da migration-base porque o schema inicial já
contém colunas ``vector``. Depois desse preflight, toda evolução de schema,
triggers, índices e backfills é aplicada pelo Alembic.
"""

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text

from app.core.config import settings

REQUIRED_EXTENSIONS = ("vector", "pg_trgm", "unaccent")


def ensure_required_extensions() -> None:
    engine = create_engine(settings.database_url, pool_pre_ping=True, future=True)
    try:
        with engine.begin() as connection:
            for extension in REQUIRED_EXTENSIONS:
                connection.execute(
                    text(f'CREATE EXTENSION IF NOT EXISTS "{extension}"')
                )
    finally:
        engine.dispose()


def upgrade_to_head() -> None:
    backend_dir = Path(__file__).resolve().parents[2]
    alembic_config = Config(str(backend_dir / "alembic.ini"))
    alembic_config.set_main_option("script_location", str(backend_dir / "migrations"))
    ensure_required_extensions()
    command.upgrade(alembic_config, "head")


def main() -> None:
    upgrade_to_head()


if __name__ == "__main__":
    main()
