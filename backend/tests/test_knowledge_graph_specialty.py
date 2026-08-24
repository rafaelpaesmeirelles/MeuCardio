"""Integração de doença e triagem por sintoma no grafo clínico.

A régua destes testes é deliberadamente conservadora: relações automáticas
só podem nascer de metadado estruturado inequívoco. Nenhum fuzzy matching,
score inventado ou promoção automática para `revisado`.
"""
from sqlalchemy import select, text

from app.models.content import Document
from app.models.knowledge import KnowledgeEntity, KnowledgeRelation
from app.models.specialty_guide import SpecialtyDisease, SymptomTriageGuide
from app.services import knowledge_graph as kg

TABELAS = (
    "knowledge_relations", "knowledge_entities",
    "symptom_triage_guides", "specialty_diseases",
    "document_revisions", "documents",
    "evidence_records", "scientific_studies", "drugs", "clinical_cases",
    "study_tracks", "gallery_images", "lab_tests", "emergency_protocols",
    "discharge_checklists", "patient_materials",
)


def _limpar(db):
    db.execute(text(f"TRUNCATE {', '.join(TABELAS)} RESTART IDENTITY CASCADE"))
    db.commit()


def _semear(db):
    db.add(Document(
        slug="bradicardia-documento",
        title="Avaliação da bradicardia sintomática",
        kind="modulo",
        theme="Arritmias",
        body_md="corpo",
        review_status="revisado",
        published=True,
    ))
    doenca = SpecialtyDisease(
        slug="doenca-no-sinusal-teste",
        name="Disfunção do nó sinusal",
        aliases=["Doença do nó sinusal"],
        area="cardiogeriatria",
        category="arritmia",
        prevalence_rank=1,
        completeness="basico",
        summary="Bradicardia e incompetência cronotrópica relacionadas à disfunção do nó sinusal.",
        related_document_slugs=["bradicardia-documento"],
        review_status="revisado",
        published=True,
    )
    triagem = SymptomTriageGuide(
        slug="pulso-lento-teste",
        name="Pulso lento / bradicardia",
        aliases=["bradicardia"],
        areas=["geral", "cardiogeriatria"],
        summary="Triagem sindrômica de pulso lento.",
        questions=[{"id": "instavel", "type": "boolean", "required": True}],
        rules=[{
            "id": "instabilidade",
            "when": {"all": [{"field": "instavel", "op": "truthy"}]},
            "add": {"risk": "emergencia"},
        }],
        default_tests=["ECG"],
        differentials=["Doença do nó sinusal", "Hipercalemia"],
        red_flags=["Hipotensão"],
        ambulatory_flow=["Correlacionar sintomas e ritmo"],
        emergency_flow=["Avaliar estabilidade"],
        tags=["bradicardia"],
        source_refs=["2021 ESC Guidelines on cardiac pacing"],
        source_urls=["https://www.escardio.org/Guidelines/Clinical-Practice-Guidelines/Cardiac-Pacing-and-Cardiac-Resynchronization-Therapy"],
        review_status="revisado",
        published=True,
    )
    db.add_all([doenca, triagem])
    db.commit()
    return doenca, triagem


def test_backfill_registra_doenca_e_triagem_e_arestas_estruturadas(db):
    _limpar(db)
    doenca, triagem = _semear(db)

    resultado = kg.backfill_mesmo_tema(db)

    assert resultado["entidades_especializadas_criadas"] == 2
    assert resultado["relacoes_estruturadas_especializadas_criadas"] >= 2

    no_doenca = db.execute(
        select(KnowledgeEntity).where(
            KnowledgeEntity.entity_type == "doenca",
            KnowledgeEntity.slug == doenca.slug,
        )
    ).scalar_one()
    no_triagem = db.execute(
        select(KnowledgeEntity).where(
            KnowledgeEntity.entity_type == "triagem_sintoma",
            KnowledgeEntity.slug == triagem.slug,
        )
    ).scalar_one()
    no_doc = db.execute(
        select(KnowledgeEntity).where(
            KnowledgeEntity.entity_type == "documento",
            KnowledgeEntity.slug == "bradicardia-documento",
        )
    ).scalar_one()

    rel_doc = db.execute(
        select(KnowledgeRelation).where(
            KnowledgeRelation.source_entity_id == no_doenca.id,
            KnowledgeRelation.target_entity_id == no_doc.id,
            KnowledgeRelation.relation_type == "mentioned_in",
        )
    ).scalar_one()
    assert rel_doc.provenance_type == "structured_metadata"
    assert rel_doc.confidence == "derived"
    assert rel_doc.review_status == "pendente_revisao"
    assert rel_doc.extra["campo"] == "related_document_slugs"

    rel_diferencial = db.execute(
        select(KnowledgeRelation).where(
            KnowledgeRelation.source_entity_id == no_doenca.id,
            KnowledgeRelation.target_entity_id == no_triagem.id,
            KnowledgeRelation.relation_type == "differential_for",
        )
    ).scalar_one()
    assert rel_diferencial.provenance_type == "structured_metadata"
    assert rel_diferencial.confidence == "derived"
    assert rel_diferencial.review_status == "pendente_revisao"
    assert rel_diferencial.extra["valor"] == "Doença do nó sinusal"

    relacionados = kg.relacionados_de(
        db, entity_type="triagem_sintoma", slug=triagem.slug,
    )
    assert relacionados is not None
    grupo_doenca = next(g for g in relacionados["grupos"] if g["tipo"] == "doenca")
    assert grupo_doenca["itens"][0]["slug"] == doenca.slug
    assert grupo_doenca["itens"][0]["rota"] == f"/doencas/{doenca.slug}"


def test_diferencial_ambiguo_nao_vira_aresta_automatica(db):
    _limpar(db)
    db.add_all([
        SpecialtyDisease(
            slug="ambigua-a", name="Síndrome X", aliases=["SX"],
            area="cardiogeriatria", category="teste", summary="A",
            review_status="revisado", published=True,
        ),
        SpecialtyDisease(
            slug="ambigua-b", name="Outra síndrome", aliases=["SX"],
            area="cardiogeriatria", category="teste", summary="B",
            review_status="revisado", published=True,
        ),
        SymptomTriageGuide(
            slug="triagem-ambigua", name="Sintoma teste", aliases=[], areas=["geral"],
            summary="Teste de ambiguidade.",
            questions=[{"id": "x", "type": "boolean"}],
            rules=[{"id": "x", "when": {"all": [{"field": "x", "op": "truthy"}]}, "add": {}}],
            default_tests=[], differentials=["SX"], red_flags=[],
            ambulatory_flow=["Avaliar"], emergency_flow=["Avaliar"],
            tags=[], source_refs=["Fonte teste"], source_urls=[],
            review_status="revisado", published=True,
        ),
    ])
    db.commit()

    kg.backfill_mesmo_tema(db)

    arestas = db.execute(
        select(KnowledgeRelation).where(KnowledgeRelation.relation_type == "differential_for")
    ).scalars().all()
    assert arestas == []


def test_despublicar_doenca_arquiva_no_sem_apagar_aresta(db):
    _limpar(db)
    doenca, triagem = _semear(db)
    kg.backfill_mesmo_tema(db)

    no_doenca = db.execute(
        select(KnowledgeEntity).where(
            KnowledgeEntity.entity_type == "doenca",
            KnowledgeEntity.slug == doenca.slug,
        )
    ).scalar_one()
    arestas_antes = db.execute(
        select(KnowledgeRelation).where(
            (KnowledgeRelation.source_entity_id == no_doenca.id)
            | (KnowledgeRelation.target_entity_id == no_doenca.id)
        )
    ).scalars().all()
    assert arestas_antes

    doenca.published = False
    db.commit()
    resultado = kg.backfill_mesmo_tema(db)

    db.refresh(no_doenca)
    assert resultado["entidades_arquivadas"] >= 1
    assert no_doenca.status == "arquivado"
    assert kg.relacionados_de(db, entity_type="doenca", slug=doenca.slug) is None

    arestas_depois = db.execute(
        select(KnowledgeRelation).where(
            (KnowledgeRelation.source_entity_id == no_doenca.id)
            | (KnowledgeRelation.target_entity_id == no_doenca.id)
        )
    ).scalars().all()
    assert len(arestas_depois) == len(arestas_antes)

    # A triagem permanece ativa: retirar uma doença do ar não despublica
    # automaticamente outro conteúdo global.
    no_triagem = db.execute(
        select(KnowledgeEntity).where(
            KnowledgeEntity.entity_type == "triagem_sintoma",
            KnowledgeEntity.slug == triagem.slug,
        )
    ).scalar_one()
    assert no_triagem.status == "ativo"
