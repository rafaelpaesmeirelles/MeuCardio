import logging
import os

from fastapi import APIRouter, HTTPException
from redis import Redis
from sqlalchemy import text

from app.core.config import settings
from app.core.db import engine
from app.core.observability import current_request_id

router = APIRouter(prefix="/api", tags=["infra"])
logger = logging.getLogger("corvia.health")


@router.get("/health")
def health() -> dict[str, str]:
    """Liveness: confirma que o processo HTTP está respondendo."""
    return {"status": "ok"}


@router.get("/version")
def version() -> dict[str, str]:
    """Identifica o commit injetado pelo deploy, sem expor configuração sensível."""
    return {"commit": os.getenv("DEPLOY_COMMIT", "unknown")}


def _pool_stats() -> dict[str, int] | None:
    """Estatísticas do pool de conexões do SQLAlchemy — só inteiros, sem
    nenhum dado de conexão (host/usuário/senha continuam só no `.env`).
    Achado de auditoria (issue #52, subfase 6): não havia nenhuma forma de
    observar o pool antes desta rota ganhar este campo — `/api/ready` só
    testava UMA conexão avulsa (`SELECT 1`), que não revela esgotamento do
    pool sob carga real. Informativo, nunca decide o status 503 sozinho:
    pool cheio não é necessariamente indisponibilidade (pode ser só pico de
    tráfego legítimo), e um `.pool` sem os atributos esperados (implementação
    de pool não padrão) não pode derrubar o readiness por isso."""
    try:
        pool = engine.pool
        return {
            "size": pool.size(),
            "checked_out": pool.checkedout(),
            "checked_in": pool.checkedin(),
            "overflow": pool.overflow(),
        }
    except Exception:
        return None


@router.get("/ready")
def ready() -> dict[str, object]:
    """Readiness: exige banco e Redis disponíveis antes de receber tráfego."""
    components: dict[str, str] = {"database": "ok", "redis": "ok"}
    failures: dict[str, str] = {}

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception as exc:
        components["database"] = "unavailable"
        failures["database"] = type(exc).__name__

    redis_client = None
    try:
        redis_client = Redis.from_url(
            settings.redis_url,
            socket_connect_timeout=1,
            socket_timeout=1,
        )
        redis_client.ping()
    except Exception as exc:
        components["redis"] = "unavailable"
        failures["redis"] = type(exc).__name__
    finally:
        if redis_client is not None:
            redis_client.close()

    if any(status != "ok" for status in components.values()):
        logger.warning(
            "readiness_failed",
            extra={
                "event": "readiness_failed",
                "request_id": current_request_id(),
                "components": components,
                "result": failures,
            },
        )
        raise HTTPException(
            status_code=503,
            detail={"status": "not_ready", "components": components},
        )

    resultado: dict[str, object] = {"status": "ready", "components": components}
    pool = _pool_stats()
    if pool is not None:
        resultado["database_pool"] = pool
    return resultado
