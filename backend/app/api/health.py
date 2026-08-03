from fastapi import APIRouter, HTTPException
from redis import Redis
from sqlalchemy import text

from app.core.config import settings
from app.core.db import engine

router = APIRouter(prefix="/api", tags=["infra"])


@router.get("/health")
def health() -> dict[str, str]:
    """Liveness: confirma que o processo HTTP está respondendo."""
    return {"status": "ok"}


@router.get("/ready")
def ready() -> dict[str, object]:
    """Readiness: exige banco e Redis disponíveis antes de receber tráfego."""
    components: dict[str, str] = {"database": "ok", "redis": "ok"}

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception:
        components["database"] = "unavailable"

    redis_client = None
    try:
        redis_client = Redis.from_url(
            settings.redis_url,
            socket_connect_timeout=1,
            socket_timeout=1,
        )
        redis_client.ping()
    except Exception:
        components["redis"] = "unavailable"
    finally:
        if redis_client is not None:
            redis_client.close()

    if any(status != "ok" for status in components.values()):
        raise HTTPException(
            status_code=503,
            detail={"status": "not_ready", "components": components},
        )

    return {"status": "ready", "components": components}
