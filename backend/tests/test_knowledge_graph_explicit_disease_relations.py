"""Relações curadas doença -> coleção no grafo Tudo com Tudo."""
import json

from sqlalchemy import select, text

from app.models.checklist import DischargeChecklist
from app.models.content import Document
from app.models.emergency import EmergencyProtocol
from app.models.knowledge import KnowledgeEntity, KnowledgeRelation
from app.models.specialty_guide import SpecialtyDisease
from app.models.study_track import StudyTrack
from app.services import knowledge_graph as kg


TABELAS = (
    "knowledge_relations", "knowledge_entities", "specialty_diseases",
    "document_revisions", "documents", "study_tracks", "emergency_protocols",
    "discharge_checklists", "evidence_records", "scientific_studies", "drugs",
    "clinical_cases", "gallery_images", "lab_tests", "patient_materials",
    "symptom_triage_guides",
)


def _limpar(db):
    db.execute(text(f"TRUNCATE {', '.join(TABELAS)} RESTART IDENTITY CASCADE"))
    db.commit()


def _manifesto(tmp_path, monkeypatch):
    caminho = tmp_path / "relacoes-explicitas.json"
    caminho.write_text(json.dumps([
        {
            "source_disease_slug": "sca-teste",
            "target_type": tipo,
            "target_slug": slug,
            "relation_type": "associated_with",
            "review_status": "revisado",
            "provenance_type": "editorial",
            "confidence": "explicit",
            "relevance_score": 1.0,
            "review_note": "Relação direta de teste.",
        }
        for tipo, slug in (
            ("protocolo_emergencia", "protocolo-sca-teste"),
            ("checklist", "checklist-sca-teste"),
            ("trilha", "trilha-sca-teste"),
        )
    ]), encoding="utf-8")
    monkeypatch.setattr(kg, "_ARQUIVO_RELACOES_EXPLICITAS", caminho)


def _semear(db):
    db.add_all([
        Document(
            slug="documento-sca-teste", title="Documento SCA", kind="modulo",
            theme="Síndrome coronariana aguda", body_md="corpo",
            review_status="revisado", published=True,
        ),
        SpecialtyDisease(
            slug="sca-teste", name="Síndrome coronariana aguda teste",
            area="geral", category="coronariopatia", summary="Resumo.",
            review_status="revisado", published=True,
        ),
        EmergencyProtocol(
            slug="protocolo-sca-teste", titulo="Protocolo SCA", ordem=1,
            documento_slug="documento-sca-teste",
            review_status="revisado", published=True,
        ),
        DischargeChecklist(
            slug="checklist-sca-teste", condicao="Alta após SCA",
            review_status="revisado", published=True,
        ),
        StudyTrack(
            slug="trilha-sca-teste", titulo="Trilha SCA",
            review_status="revisado", published=True,
        ),
    ])
    db.commit()


def _slugs_relacionados(db, tipo, slug):
    resultado = kg.relacionados_de(db, entity_type=tipo, slug=slug)
    assert resultado is not None
    return {
        item["slug"]
        for grupo in resultado["grupos"]
        for item in grupo["itens"]
    }


def test_manifesto_cria_tres_arestas_e_navegacao_bidirecional(
    db, tmp_path, monkeypatch,
):
    _limpar(db)
    _manifesto(tmp_path, monkeypatch)
    _semear(db)

    resultado = kg.backfill_mesmo_tema(db)

    assert resultado["relacoes_doenca_explicitas_criadas"] == 3
    assert resultado["relacoes_doenca_explicitas_nao_resolvidas"] == 0
    no_doenca = db.execute(select(KnowledgeEntity).where(
        KnowledgeEntity.entity_type == "doenca",
        KnowledgeEntity.slug == "sca-teste",
    )).scalar_one()
    arestas = db.execute(select(KnowledgeRelation).where(
        KnowledgeRelation.source_entity_id == no_doenca.id,
        KnowledgeRelation.relation_type == "associated_with",
        KnowledgeRelation.review_status == "revisado",
    )).scalars().all()
    assert len(arestas) == 3
    assert all(aresta.provenance_type == "editorial" for aresta in arestas)
    assert all(aresta.confidence == "explicit" for aresta in arestas)

    assert {
        "protocolo-sca-teste", "checklist-sca-teste", "trilha-sca-teste",
    } <= _slugs_relacionados(db, "doenca", "sca-teste")
    for tipo, slug in (
        ("protocolo_emergencia", "protocolo-sca-teste"),
        ("checklist", "checklist-sca-teste"),
        ("trilha", "trilha-sca-teste"),
    ):
        assert "sca-teste" in _slugs_relacionados(db, tipo, slug)


def test_doenca_devolvida_a_pendente_desativa_relacoes_sem_apagar_auditoria(
    db, tmp_path, monkeypatch,
):
    _limpar(db)
    _manifesto(tmp_path, monkeypatch)
    _semear(db)
    kg.backfill_mesmo_tema(db)

    doenca = db.execute(select(SpecialtyDisease).where(
        SpecialtyDisease.slug == "sca-teste"
    )).scalar_one()
    doenca.review_status = "pendente_revisao"
    doenca.published = False
    db.commit()

    resultado = kg.backfill_mesmo_tema(db)

    assert resultado["relacoes_doenca_explicitas_criadas"] == 0
    assert resultado["relacoes_doenca_explicitas_nao_resolvidas"] == 3
    assert {
        item["motivo"] for item in resultado["amostra_relacoes_doenca_nao_resolvidas"]
    } == {"doenca_nao_publicada"}
    no_doenca = db.execute(select(KnowledgeEntity).where(
        KnowledgeEntity.entity_type == "doenca",
        KnowledgeEntity.slug == "sca-teste",
    )).scalar_one()
    assert no_doenca.status == "arquivado"
    arestas = db.execute(select(KnowledgeRelation).where(
        KnowledgeRelation.source_entity_id == no_doenca.id,
        KnowledgeRelation.relation_type == "associated_with",
    )).scalars().all()
    assert len(arestas) == 3
    assert {aresta.review_status for aresta in arestas} == {"rejeitado"}
    assert kg.relacionados_de(db, entity_type="doenca", slug="sca-teste") is None
    assert "sca-teste" not in _slugs_relacionados(
        db, "protocolo_emergencia", "protocolo-sca-teste",
    )


def test_manifesto_rejeita_relacao_duplicada(tmp_path, monkeypatch):
    _manifesto(tmp_path, monkeypatch)
    payload = json.loads(kg._ARQUIVO_RELACOES_EXPLICITAS.read_text(encoding="utf-8"))
    kg._ARQUIVO_RELACOES_EXPLICITAS.write_text(
        json.dumps([payload[0], payload[0]]), encoding="utf-8",
    )

    try:
        kg._carregar_manifesto_relacoes_explicitas()
        assert False, "deveria rejeitar aresta duplicada"
    except RuntimeError as exc:
        assert "duplicada" in str(exc)
