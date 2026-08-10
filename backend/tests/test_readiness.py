from app.api import health as health_api


def test_liveness_does_not_depend_on_external_services(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness_checks_database_and_redis(client):
    response = client.get("/api/ready")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ready"
    assert body["components"] == {"database": "ok", "redis": "ok"}


def test_readiness_reports_database_pool_stats(client):
    """Achado de auditoria (issue #52, subfase 6): antes desta rota ganhar
    o campo `database_pool`, não havia nenhuma forma de observar
    esgotamento do pool de conexões — só uma conexão avulsa era testada."""
    response = client.get("/api/ready")
    assert response.status_code == 200
    pool = response.json()["database_pool"]
    assert pool["size"] >= 0
    assert pool["checked_out"] >= 0
    assert pool["checked_in"] >= 0
    assert pool["overflow"] >= -pool["size"]  # overflow negativo é válido (conexões ociosas recolhidas)


def test_readiness_pool_stats_never_block_readiness_when_pool_introspection_fails(client, monkeypatch):
    """Uma falha ao introspeccionar o pool (ex.: implementação de pool não
    padrão) é diagnóstico perdido, nunca motivo de 503 — o banco pode estar
    perfeitamente saudável mesmo sem conseguirmos descrever o pool."""
    from app.api import health as health_api

    monkeypatch.setattr(health_api, "_pool_stats", lambda: None)
    response = client.get("/api/ready")
    assert response.status_code == 200
    assert "database_pool" not in response.json()


def test_readiness_returns_503_when_redis_is_unavailable(client, monkeypatch):
    class UnavailableRedis:
        @classmethod
        def from_url(cls, *args, **kwargs):
            raise ConnectionError("redis indisponível")

    monkeypatch.setattr(health_api, "Redis", UnavailableRedis)

    response = client.get("/api/ready")
    assert response.status_code == 503
    assert response.json()["detail"] == {
        "status": "not_ready",
        "components": {"database": "ok", "redis": "unavailable"},
    }
