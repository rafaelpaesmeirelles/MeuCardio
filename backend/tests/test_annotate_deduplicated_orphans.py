"""Regressão do comando da Parte B (correção coordenada de 02/09/2026):
anota o motivo dos 22 órfãos sem tocar em published/review_status, e é
idempotente."""

import pytest
from sqlalchemy import text

from app.commands.annotate_deduplicated_orphans_20260902 import (
    BLOCKER_CHAGAS_SLUG,
    ORFAOS_ESTUDOS,
    ORFAOS_EVIDENCIAS,
    anotar,
)
from app.models.evidence import EvidenceRecord
from app.models.study import ScientificStudy


@pytest.fixture(autouse=True)
def _colecoes_limpas(db):
    db.execute(text("TRUNCATE scientific_studies, evidence_records RESTART IDENTITY CASCADE"))
    db.commit()
    yield
    db.execute(text("TRUNCATE scientific_studies, evidence_records RESTART IDENTITY CASCADE"))
    db.commit()


def _semear(db):
    for slug in ORFAOS_ESTUDOS:
        db.add(ScientificStudy(
            slug=slug, title=slug, study_type="ensaio_clinico", journal="Periódico de teste",
            year=2024, summary="Resumo de teste.", key_findings="Achados de teste.",
            clinical_implications="Implicações de teste.", theme="Geral",
            review_status="revisado", published=False,
        ))
    for slug in list(ORFAOS_EVIDENCIAS) + [BLOCKER_CHAGAS_SLUG]:
        db.add(EvidenceRecord(
            slug=slug, statement="Statement de teste.", recommendation_class="I",
            evidence_level="A", society="Sociedade de teste", year=2024,
            guideline_title="Diretriz de teste", reference="Referência de teste",
            theme="Geral", review_status="revisado", published=False,
        ))
    db.commit()


def test_anota_todos_sem_publicar_nada(db):
    _semear(db)

    resultado = anotar()

    assert len(resultado["estudos"]) == len(ORFAOS_ESTUDOS) == 19
    assert len(resultado["evidencias"]) == len(ORFAOS_EVIDENCIAS) + 1 == 3

    for slug in ORFAOS_ESTUDOS:
        item = db.query(ScientificStudy).filter(ScientificStudy.slug == slug).one()
        assert item.published is False
        assert item.review_status == "revisado"
        assert "Órfão de deduplicação" in item.review_note
        assert ORFAOS_ESTUDOS[slug].split(" / ")[0] in item.review_note

    chagas = db.query(EvidenceRecord).filter(EvidenceRecord.slug == BLOCKER_CHAGAS_SLUG).one()
    assert chagas.published is False
    assert "Blocker clínico não resolvido" in chagas.review_note
    assert "benznidazol" in chagas.review_note


def test_idempotente_rodar_duas_vezes_nao_duplica_texto(db):
    _semear(db)
    anotar()
    anotar()

    item = db.query(ScientificStudy).filter(
        ScientificStudy.slug == "scd-heft-cdi-vs-amiodarona-na-icfer"
    ).one()
    assert item.review_note.count("Órfão de deduplicação") == 1


def test_recusa_anotar_item_que_foi_publicado_por_engano(db):
    _semear(db)
    publicado_por_engano = db.query(ScientificStudy).filter(
        ScientificStudy.slug == "scd-heft-cdi-vs-amiodarona-na-icfer"
    ).one()
    publicado_por_engano.published = True
    db.commit()

    with pytest.raises(AssertionError):
        anotar()
