from app.api import health as health_api


def test_liveness_does_not_depend_on_external_services(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness_checks_database_and_redis(client):
    response = client.get("/api/ready")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "components": {"database": "ok", "redis": "ok"},
    }


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
