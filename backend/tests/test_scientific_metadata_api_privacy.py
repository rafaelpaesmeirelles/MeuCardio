"""Contratos de privacidade para metadados editoriais científicos."""

import inspect

import pytest

from app.api import calculators as calculators_api
from app.api import specialty_guides as specialty_guides_api
from app.api.evidence import _detail as evidence_detail
from app.api.exportacao import _dump as patient_material_detail
from app.api.studies import _detail as study_detail
from app.models.evidence import EvidenceRecord
from app.models.patient_material import PatientMaterial
from app.models.study import ScientificStudy


@pytest.fixture(autouse=True)
def _banco_limpo():
    """Os contratos exercitam serializadores puros, sem PostgreSQL."""
    yield


def test_detalhes_clinicos_nao_expoem_nota_ou_proveniencia_editorial():
    study = ScientificStudy(
        id=1,
        slug="estudo-metadados",
        title="Estudo com metadados",
        study_type="coorte",
        authors="Equipe",
        journal="Journal",
        year=2026,
        theme="Teste",
        summary="Resumo",
        key_findings="Achados",
        clinical_implications="Implicações",
        tags=["teste"],
        review_note="Revisão independente pendente.",
        fonte_producao="lote versionado",
    )
    evidence = EvidenceRecord(
        slug="evidencia-metadados",
        statement="Recomendação clínica.",
        recommendation_class="I",
        evidence_level="A",
        society="SBC",
        year=2026,
        guideline_title="Diretriz",
        reference="Referência",
        source_url="https://example.test/evidence",
        theme="Teste",
        review_status="revisado",
        review_note="Nota interna.",
    )
    material = PatientMaterial(
        slug="material-metadados",
        titulo="Material com metadados",
        tema="Teste",
        secoes=[],
        sinais_de_alerta=[],
        perguntas=[],
        fontes=["PMID:12345678"],
        review_note="Conferido editorialmente.",
        fonte_producao="lote versionado",
    )

    for detail in (
        study_detail(study),
        evidence_detail(evidence),
        patient_material_detail(material),
    ):
        assert "review_note" not in detail
        assert "fonte_producao" not in detail


def test_outros_serializadores_clinicos_omitem_metadados_editoriais():
    for function in (
        specialty_guides_api._disease_detail,
        specialty_guides_api._triage_detail,
    ):
        assert '"review_note"' not in inspect.getsource(function)
    for function in (
        calculators_api.list_calculators,
        calculators_api.get_calculator,
        calculators_api.run_calculator,
    ):
        assert '"fonte_producao"' not in inspect.getsource(function)
