"""Contrato público mínimo para identificar a revisão implantada."""


def test_version_retorna_commit_injetado(client, monkeypatch):
    commit = "1bea10cf2f168abf069f721ec0d5017573c05528"
    monkeypatch.setenv("DEPLOY_COMMIT", commit)

    response = client.get("/api/version")

    assert response.status_code == 200
    assert response.json() == {"commit": commit}


def test_version_sem_injecao_nao_inventa_commit(client, monkeypatch):
    monkeypatch.delenv("DEPLOY_COMMIT", raising=False)

    response = client.get("/api/version")

    assert response.status_code == 200
    assert response.json() == {"commit": "unknown"}
