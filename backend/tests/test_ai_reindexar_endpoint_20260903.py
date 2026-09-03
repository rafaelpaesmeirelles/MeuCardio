"""Correção coordenada de 03/09/2026: POST /api/ai/reindexar chamava
`rag.indexar_tudo()` direto — só `documents`, sem o advisory lock do comando
de backfill, sem teto de itens (risco de timeout HTTP num backlog grande).
Passou a delegar para `app.commands.reindex_rag_completo_20260902.rodar()`."""

from sqlalchemy import text

from app.core.config import settings
from app.models.evidence import EvidenceRecord
from app.models.subscription import Subscription


class _ProvedorFake:
    def embeddings(self, textos):
        vetores = []
        for texto in textos:
            semente = sum(ord(c) for c in texto) % 997
            vetores.append([((semente + i) % 997) / 997 for i in range(1536)])
        return vetores


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_reindexar_cobre_documento_e_multi_frente(client, criar_usuario, db, monkeypatch):
    db.execute(text("TRUNCATE evidence_records, knowledge_chunks, rag_reindex_runs RESTART IDENTITY CASCADE"))
    db.commit()

    monkeypatch.setattr(settings, "ai_enabled", True)
    monkeypatch.setattr("app.services.rag.obter_provedor_embeddings", lambda: _ProvedorFake())
    monkeypatch.setattr("app.services.rag_multi.obter_provedor_embeddings", lambda: _ProvedorFake())

    admin, token = criar_usuario(email="ai.reindexar.multi@teste.local", role="admin")
    db.add(EvidenceRecord(
        slug="ai-reindexar-endpoint-teste", statement="Statement.", summary="Resumo.",
        recommendation_class="I", evidence_level="A", society="Sociedade", year=2024,
        guideline_title="Diretriz", reference="Ref.", theme="Farmacologia",
        review_status="revisado", published=True,
    ))
    db.commit()

    resposta = client.post("/api/ai/reindexar", headers=_headers(token))
    assert resposta.status_code == 200, resposta.text
    corpo = resposta.json()
    # Antes só existia "documentos"/"trechos" (só a frente `documents`) — agora
    # cobre as 12 frentes também.
    assert "por_frente" in corpo
    assert corpo["por_frente"]["evidencia"]["entidades"] == 1


def test_reindexar_devolve_409_se_ja_em_execucao(client, criar_usuario, db, monkeypatch):
    from app.commands.reindex_rag_completo_20260902 import _LOCK_KEY

    monkeypatch.setattr(settings, "ai_enabled", True)
    admin, token = criar_usuario(email="ai.reindexar.lock@teste.local", role="admin")

    obtido = db.execute(text("SELECT pg_try_advisory_lock(:k)"), {"k": _LOCK_KEY}).scalar()
    assert obtido is True
    try:
        resposta = client.post("/api/ai/reindexar", headers=_headers(token))
        assert resposta.status_code == 409
    finally:
        db.execute(text("SELECT pg_advisory_unlock(:k)"), {"k": _LOCK_KEY})
        db.commit()


def test_reindexar_exige_admin(client, criar_usuario, db):
    user, token = criar_usuario(email="ai.reindexar.naoadmin@teste.local")
    # assinante_ativo (router-level, app/main.py) roda antes de require_admin
    # — sem assinatura, um não-admin já leva 402 e o teste não checaria o que
    # de fato quer verificar (que require_admin recusa não-admin).
    db.add(Subscription(user_id=user.id, kind="meucardio", plano="basico", status="ativo"))
    db.commit()

    resposta = client.post("/api/ai/reindexar", headers=_headers(token))
    assert resposta.status_code == 403
