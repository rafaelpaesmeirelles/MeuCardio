"""Correção coordenada de 03/09/2026, seção 9 (observabilidade): GET
/api/ai/status precisa distinguir "chave configurada" de "embeddings
realmente operacionais", e nunca vazar API key/saldo."""

from sqlalchemy import text

from app.models.rag import RagReindexRun
from app.models.subscription import Subscription


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _subscribe(db, user_id: int) -> None:
    db.add(Subscription(user_id=user_id, kind="meucardio", plano="basico", status="ativo"))
    db.commit()


def test_status_rag_sem_nenhum_backfill_executado_e_desconhecido_nao_falso(client, criar_usuario, db):
    db.execute(text("TRUNCATE rag_reindex_runs RESTART IDENTITY CASCADE"))
    db.commit()

    user, token = criar_usuario(email="ai.status.rag.vazio@teste.local")
    _subscribe(db, user.id)

    resposta = client.get("/api/ai/status", headers=_headers(token))
    assert resposta.status_code == 200
    rag_status = resposta.json()["rag"]

    # "nunca rodou" não pode ser confundido com "funcionando" nem com "quebrado"
    assert rag_status["embeddings_operacionais"] is None
    assert rag_status["motivo_indisponibilidade"] == "backfill_nunca_executado"
    assert rag_status["ultimo_backfill"] is None
    assert rag_status["fallback_lexico_disponivel"] is True


def test_status_rag_distingue_quota_insuficiente_de_sucesso(client, criar_usuario, db):
    from datetime import datetime, timezone

    db.execute(text("TRUNCATE rag_reindex_runs RESTART IDENTITY CASCADE"))
    db.add(RagReindexRun(
        started_at=datetime.now(timezone.utc), finished_at=datetime.now(timezone.utc),
        dry_run=False, entidades_processadas=0, trechos_gerados=0, falhas=3,
        backlog_restante=50, exit_code=2,
        detalhe={"erro": "insufficient_quota: sem crédito no provedor de embeddings"},
    ))
    db.commit()

    user, token = criar_usuario(email="ai.status.rag.quota@teste.local")
    _subscribe(db, user.id)

    resposta = client.get("/api/ai/status", headers=_headers(token))
    rag_status = resposta.json()["rag"]

    assert rag_status["embeddings_operacionais"] is False
    assert rag_status["motivo_indisponibilidade"] == "quota_insuficiente"
    assert rag_status["ultimo_backfill"]["backlog_restante"] == 50


def test_status_rag_nao_expoe_api_key_nem_campos_financeiros(client, criar_usuario, db):
    user, token = criar_usuario(email="ai.status.rag.seguranca@teste.local")
    _subscribe(db, user.id)

    corpo = client.get("/api/ai/status", headers=_headers(token)).json()
    bruto = str(corpo).lower()

    for termo_proibido in ("sk-", "api_key", "apikey", "saldo", "credit_balance", "billing"):
        assert termo_proibido not in bruto, f"campo sensível vazando em /api/ai/status: {termo_proibido!r}"
