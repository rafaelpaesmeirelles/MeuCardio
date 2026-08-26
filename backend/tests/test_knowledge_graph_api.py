"""`GET /api/grafo/relacionados` e `POST /api/admin/grafo/backfill` — casca
HTTP do Grafo de Conhecimento Clínico Universal (issue #52, nova fase).

A lógica em si já está coberta por `test_knowledge_graph.py` (chamada
direta ao serviço); este arquivo garante que a autorização por rota está
correta: leitura exige assinatura ativa (mesma régua de qualquer outra
frente de conteúdo), backfill é ação administrativa.
"""
from sqlalchemy import text

from app.models.content import Document
from app.models.evidence import EvidenceRecord
from app.models.knowledge import KnowledgeEntity, KnowledgeRelation
from app.models.subscription import Subscription
from app.services.knowledge_graph import BackfillEmAndamento

TEMA = "Insuficiência cardíaca"

TABELAS = (
    "knowledge_relations", "knowledge_entities",
    "document_revisions", "documents", "evidence_records", "scientific_studies",
    "drugs", "clinical_cases", "study_tracks", "gallery_images", "lab_tests",
    "emergency_protocols", "discharge_checklists", "patient_materials",
)


def _limpar(db):
    db.execute(text(f"TRUNCATE {', '.join(TABELAS)} RESTART IDENTITY CASCADE"))
    db.commit()


def _headers_admin(criar_usuario):
    _, token = criar_usuario(role="admin")
    return {"Authorization": f"Bearer {token}"}


def _headers_medico_sem_assinatura(criar_usuario):
    _, token = criar_usuario(email="medico-sem-assinatura@teste.local", role="medico")
    return {"Authorization": f"Bearer {token}"}


def _headers_medico_assinante(db, criar_usuario):
    user, token = criar_usuario(email="medico-assinante@teste.local", role="medico")
    db.add(Subscription(user_id=user.id, kind="meucardio", plano="basico", status="ativo"))
    db.commit()
    return {"Authorization": f"Bearer {token}"}


def _semear(db):
    db.add(Document(
        slug="ic-doc-api", title="Manejo da IC crônica", kind="modulo", theme=TEMA,
        body_md="corpo", review_status="revisado", published=True,
    ))
    db.add(EvidenceRecord(
        slug="ic-ev-api", theme=TEMA, statement="Beta-bloqueador reduz mortalidade na ICFEr",
        recommendation_class="I", evidence_level="A", society="ESC", year=2021,
        guideline_title="ESC 2021 Heart Failure", reference="ESC 2021, ref completa",
        review_status="revisado", published=True,
    ))
    db.commit()


def test_relacionados_exige_autenticacao(client, db):
    _limpar(db)
    resposta = client.get("/api/grafo/relacionados", params={"entity_type": "documento", "slug": "x"})
    assert resposta.status_code == 401


def test_relacionados_exige_assinatura_ativa(client, db, criar_usuario):
    _limpar(db)
    headers = _headers_medico_sem_assinatura(criar_usuario)
    resposta = client.get(
        "/api/grafo/relacionados", params={"entity_type": "documento", "slug": "x"}, headers=headers,
    )
    assert resposta.status_code == 402


def test_relacionados_funciona_para_assinante_ativo(client, db, criar_usuario):
    _limpar(db)
    _semear(db)
    client.post("/api/admin/grafo/backfill", headers=_headers_admin(criar_usuario))

    headers = _headers_medico_assinante(db, criar_usuario)
    resposta = client.get(
        "/api/grafo/relacionados", params={"entity_type": "documento", "slug": "ic-doc-api"}, headers=headers,
    )
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["slug"] == "ic-doc-api"
    tipos = {g["tipo"] for g in corpo["grupos"]}
    assert "evidencia" in tipos


def test_relacionados_rejeita_entity_type_desconhecido(client, db, criar_usuario):
    _limpar(db)
    headers = _headers_medico_assinante(db, criar_usuario)
    resposta = client.get(
        "/api/grafo/relacionados", params={"entity_type": "paciente", "slug": "x"}, headers=headers,
    )
    assert resposta.status_code == 422


def test_relacionados_item_fora_do_grafo_devolve_lista_vazia_sem_erro(client, db, criar_usuario):
    _limpar(db)
    headers = _headers_medico_assinante(db, criar_usuario)
    resposta = client.get(
        "/api/grafo/relacionados", params={"entity_type": "documento", "slug": "nao-existe"}, headers=headers,
    )
    assert resposta.status_code == 200
    assert resposta.json()["grupos"] == []


def test_backfill_exige_admin(client, db, criar_usuario):
    _limpar(db)
    headers = _headers_medico_assinante(db, criar_usuario)
    resposta = client.post("/api/admin/grafo/backfill", headers=headers)
    assert resposta.status_code == 403


def test_backfill_via_rota_real_cria_entidades_e_grava_audit_log(client, db, criar_usuario):
    _limpar(db)
    _semear(db)
    resposta = client.post("/api/admin/grafo/backfill", headers=_headers_admin(criar_usuario))
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["entidades_criadas_ou_atualizadas"] >= 2

    entidades = db.execute(text("SELECT COUNT(*) FROM knowledge_entities")).scalar_one()
    assert entidades >= 2
    relacoes = db.execute(text("SELECT COUNT(*) FROM knowledge_relations")).scalar_one()
    assert relacoes >= 1

    ultimo_log = db.execute(
        text("SELECT action, entity FROM audit_logs WHERE action = 'grafo_backfill' ORDER BY id DESC LIMIT 1")
    ).first()
    assert ultimo_log is not None
    assert ultimo_log.entity == "knowledge_graph"


def test_backfill_e_idempotente_pela_rota_real(client, db, criar_usuario):
    _limpar(db)
    _semear(db)
    headers = _headers_admin(criar_usuario)

    client.post("/api/admin/grafo/backfill", headers=headers)
    entidades_1 = db.execute(text("SELECT COUNT(*) FROM knowledge_entities")).scalar_one()
    relacoes_1 = db.execute(text("SELECT COUNT(*) FROM knowledge_relations")).scalar_one()

    resposta_2 = client.post("/api/admin/grafo/backfill", headers=headers)
    assert resposta_2.status_code == 200
    entidades_2 = db.execute(text("SELECT COUNT(*) FROM knowledge_entities")).scalar_one()
    relacoes_2 = db.execute(text("SELECT COUNT(*) FROM knowledge_relations")).scalar_one()

    assert entidades_1 == entidades_2
    assert relacoes_1 == relacoes_2


def test_backfill_concorrente_responde_409(client, db, criar_usuario, monkeypatch):
    from app.api import admin as admin_api

    def _ocupado(_db, *, commit=True):
        raise BackfillEmAndamento("Outra reconciliação está em andamento.")

    monkeypatch.setattr(admin_api, "backfill_mesmo_tema", _ocupado)
    resposta = client.post("/api/admin/grafo/backfill", headers=_headers_admin(criar_usuario))

    assert resposta.status_code == 409
    assert "em andamento" in resposta.json()["detail"]
