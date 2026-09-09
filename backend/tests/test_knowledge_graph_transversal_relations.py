"""PostgreSQL integration for reviewed transversal graph reconciliation."""
import pytest
from sqlalchemy import select, text

from app.models.drug import Drug
from app.models.knowledge import KnowledgeEntity, KnowledgeRelation
from app.models.lab_test import LabTest
from app.services import knowledge_graph as kg


TABLES = (
    "knowledge_relations", "knowledge_entities", "specialty_diseases",
    "document_revisions", "documents", "study_tracks", "emergency_protocols",
    "discharge_checklists", "evidence_records", "scientific_studies", "drugs",
    "clinical_cases", "gallery_images", "lab_tests", "patient_materials",
    "symptom_triage_guides",
)
DRUG = "med-transversal-teste"
EXAM = "exame-transversal-teste"


@pytest.fixture
def transversal_pair(db, monkeypatch):
    db.execute(text(f"TRUNCATE {', '.join(TABLES)} RESTART IDENTITY CASCADE"))
    db.commit()
    records = [{
        "source_type": "medicamento", "source_slug": DRUG,
        "target_type": "exame", "target_slug": EXAM,
        "relation_type": "monitor_with", "relevance_score": 1.0,
        "provenance_type": "editorial", "confidence": "explicit",
        "review_status": "revisado",
        "evidence_source": f"exames/metadados.json#{EXAM}.indications",
        "review_note": "Monitorização explicitamente descrita na fonte de teste.",
    }]
    monkeypatch.setattr(kg, "load_transversal_relations", lambda path: records)
    monkeypatch.setattr(kg, "_carregar_manifesto_relacoes_explicitas", lambda: [])
    drug = Drug(
        slug=DRUG, generic_name="Medicamento transversal teste",
        drug_class="Classe de teste", review_status="revisado", published=True,
    )
    exam = LabTest(
        slug=EXAM, name="Exame transversal teste", category="laboratorial",
        theme="Monitorização exclusiva teste", what_it_measures="Medida de teste",
        indications="Monitorização do medicamento de teste.",
        interpretation="Interpretação de teste.",
        review_status="revisado", published=True,
    )
    db.add_all([drug, exam])
    db.commit()
    yield records, drug, exam
    db.rollback()
    db.execute(text(f"TRUNCATE {', '.join(TABLES)} RESTART IDENTITY CASCADE"))
    db.commit()


def _edge(db):
    return db.execute(select(KnowledgeRelation).where(
        KnowledgeRelation.relation_type == "monitor_with",
    )).scalar_one()


def _related_slugs(db, kind, slug):
    result = kg.relacionados_de(db, entity_type=kind, slug=slug)
    assert result is not None
    return {item["slug"] for group in result["grupos"] for item in group["itens"]}


def test_transversal_backfill_is_idempotent_and_navigable_both_directions(db, transversal_pair):
    first = kg.backfill_mesmo_tema(db)
    edge = _edge(db)
    identity = edge.id
    fingerprint = edge.extra["_fingerprint"]
    assert first["relacoes_transversais_criadas"] == 1
    assert first["relacoes_transversais_nao_resolvidas"] == 0
    assert edge.provenance_type == "editorial"
    assert edge.confidence == "explicit"
    assert edge.review_status == "revisado"
    assert EXAM in _related_slugs(db, "medicamento", DRUG)
    assert DRUG in _related_slugs(db, "exame", EXAM)

    second = kg.backfill_mesmo_tema(db)
    edge = _edge(db)
    assert second["relacoes_transversais_criadas"] == 0
    assert second["relacoes_transversais_nao_resolvidas"] == 0
    assert edge.id == identity
    assert edge.extra["_fingerprint"] == fingerprint
    assert edge.review_status == "revisado"


def test_transversal_unpublished_target_is_unresolved_and_archived(db, transversal_pair):
    _, _, exam = transversal_pair
    kg.backfill_mesmo_tema(db)
    identity = _edge(db).id
    exam.published = False
    exam.review_status = "pendente_revisao"
    db.commit()

    result = kg.backfill_mesmo_tema(db)
    assert result["relacoes_transversais_criadas"] == 0
    assert result["relacoes_transversais_nao_resolvidas"] == 1
    assert result["amostra_relacoes_transversais_nao_resolvidas"][0]["motivo"] == "destino_nao_publicado"
    edge = _edge(db)
    assert edge.id == identity
    assert edge.review_status == "rejeitado"
    assert edge.extra["_inactive_reason"] == "source_removed"
    node = db.execute(select(KnowledgeEntity).where(
        KnowledgeEntity.entity_type == "exame", KnowledgeEntity.slug == EXAM,
    )).scalar_one()
    assert node.status == "arquivado"
    assert kg.relacionados_de(db, entity_type="exame", slug=EXAM) is None
    assert EXAM not in _related_slugs(db, "medicamento", DRUG)


def test_transversal_removed_manifest_edge_can_return_without_duplication(db, transversal_pair):
    records, _, _ = transversal_pair
    kg.backfill_mesmo_tema(db)
    identity = _edge(db).id
    record = records.pop()
    kg.backfill_mesmo_tema(db)
    assert _edge(db).review_status == "rejeitado"
    assert _edge(db).extra["_inactive_reason"] == "source_removed"

    records.append(record)
    result = kg.backfill_mesmo_tema(db)
    assert result["relacoes_transversais_criadas"] == 0
    assert _edge(db).id == identity
    assert _edge(db).review_status == "revisado"
    assert "_inactive_reason" not in _edge(db).extra


def test_transversal_human_rejection_survives_removal_and_source_change(db, transversal_pair):
    records, _, _ = transversal_pair
    kg.backfill_mesmo_tema(db)
    edge = _edge(db)
    identity = edge.id
    edge.review_status = "rejeitado"
    edge.extra = {**edge.extra, "human_review_note": "Decisão editorial de rejeitar."}
    db.commit()

    record = records.pop()
    kg.backfill_mesmo_tema(db)
    assert _edge(db).review_status == "rejeitado"
    assert _edge(db).extra.get("_inactive_reason") != "source_removed"
    records.append({**record, "review_note": "Fonte atualizada após rejeição humana."})
    kg.backfill_mesmo_tema(db)
    edge = _edge(db)
    assert edge.id == identity
    assert edge.review_status == "rejeitado"
    assert edge.extra["human_review_note"] == "Decisão editorial de rejeitar."
    assert edge.extra.get("_inactive_reason") != "source_removed"


def test_trilha_material_paciente_aparece_nos_dois_sentidos(db, transversal_pair):
    from app.models.patient_material import PatientMaterial
    from app.models.study_track import StudyTrack

    material = PatientMaterial(slug="material-paciente-etapa-teste", titulo="Entenda a pericardite",
                               tema="Pericárdio", review_status="revisado", published=True)
    track = StudyTrack(slug="trilha-material-etapa-teste", titulo="Pericardite",
                       tema="Pericárdio", objetivo="Comunicação", nivel="intermediário",
                       review_status="revisado", published=True,
                       etapas=[{"ordem": 1, "item_type": "material_paciente",
                                "item_slug": material.slug, "por_que": "Preparar a orientação."}])
    db.add_all([material, track])
    db.commit()
    kg.backfill_mesmo_tema(db)
    assert material.slug in _related_slugs(db, "trilha", track.slug)
    assert track.slug in _related_slugs(db, "material_paciente", material.slug)
    edge = db.execute(select(KnowledgeRelation).where(
        KnowledgeRelation.relation_type == "contains",
    )).scalar_one()
    # A ligação estrutural é navegável, mas só o manifesto editorial explícito
    # promove sua revisão. Esta fixture isola a estrutura, sem esse manifesto.
    assert edge.review_status == "pendente_revisao"
    assert edge.provenance_type == "structured_metadata"
    assert edge.extra["campo"] == "StudyTrack.etapas"
