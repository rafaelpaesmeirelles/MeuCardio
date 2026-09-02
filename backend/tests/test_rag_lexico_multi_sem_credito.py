"""Parte 2/3/7 da correção coordenada de 02/09/2026: a busca da IA
(`rag.recuperar()`) precisa achar as 12 frentes de `rag_sources.FONTES_RAG` +
calculadoras por via LÉXICA, reaproveitando a mesma consulta de
`catalog_search` usada por `/api/search` — não só documentos, e não só
quando o provedor de embeddings está disponível.

Prova exigida pelo Rafael: uma pergunta da IA acha pelo menos uma entidade
de CADA tipo elegível mesmo quando a recuperação semântica está
indisponível (provedor sem crédito). Depois, prova que léxico + semântico
funcionam juntos sem conflito de namespace."""

import pytest
from sqlalchemy import text

from app.models.checklist import DischargeChecklist
from app.models.clinical_case import ClinicalCase
from app.models.drug import Drug
from app.models.emergency import EmergencyProtocol
from app.models.evidence import EvidenceRecord
from app.models.gallery import GalleryImage
from app.models.lab_test import LabTest
from app.models.patient_material import PatientMaterial
from app.models.specialty_guide import SpecialtyDisease, SymptomTriageGuide
from app.models.study import ScientificStudy
from app.models.study_track import StudyTrack
from app.services.rag import recuperar

TABELAS = (
    "gallery_images", "lab_tests", "evidence_records", "scientific_studies",
    "drugs", "clinical_cases", "study_tracks", "discharge_checklists",
    "patient_materials", "emergency_protocols", "specialty_diseases",
    "symptom_triage_guides", "knowledge_chunks",
)

FRENTES_ESPERADAS = {
    "galeria", "exame", "evidencia", "estudo", "medicamento", "caso_clinico",
    "trilha", "checklist", "material_paciente", "protocolo_emergencia",
    "doenca", "triagem_sintoma",
}


class _ProvedorSemCredito:
    """Simula o provedor de embeddings sem crédito — igual ao erro real
    (`insufficient_quota`/`credit_balance_exhausted`) confirmado ao vivo
    nesta correção: qualquer chamada a `.embeddings()` levanta."""

    def embeddings(self, textos):
        raise RuntimeError("insufficient_quota: sem crédito no provedor de embeddings")


class _ProvedorFake:
    def embeddings(self, textos):
        vetores = []
        for texto in textos:
            semente = sum(ord(c) for c in texto) % 997
            vetores.append([((semente + i) % 997) / 997 for i in range(1536)])
        return vetores


@pytest.fixture(autouse=True)
def _acervo_limpo(db):
    db.execute(text(f"TRUNCATE {', '.join(TABELAS)} RESTART IDENTITY CASCADE"))
    db.commit()
    yield
    db.execute(text(f"TRUNCATE {', '.join(TABELAS)} RESTART IDENTITY CASCADE"))
    db.commit()


def _semear_doze_frentes(db, sentinela: str) -> None:
    db.add_all([
        GalleryImage(
            slug=f"{sentinela}-galeria", title=f"{sentinela} galeria",
            modality="ecocardiograma", theme="Tema sentinela", findings="Achado sentinela",
            file_path="teste.png", source_name="Fonte de teste", source_url="https://example.test",
            license="CC0", attribution="Teste", review_status="revisado", published=True,
        ),
        LabTest(
            slug=f"{sentinela}-exame", name=f"{sentinela} exame", category="laboratorial",
            what_it_measures="Medida sentinela", indications="Indicação sentinela",
            interpretation="Interpretação sentinela", theme="Tema sentinela",
            review_status="revisado", published=True,
        ),
        EvidenceRecord(
            slug=f"{sentinela}-evidencia", statement=f"{sentinela} evidência",
            recommendation_class="I", evidence_level="A", society="Sociedade de teste",
            year=2026, guideline_title="Diretriz sentinela", reference="Referência sentinela",
            theme="Tema sentinela", review_status="revisado", published=True,
        ),
        ScientificStudy(
            slug=f"{sentinela}-estudo", title=f"{sentinela} estudo", study_type="ensaio_clinico",
            journal="Periódico de teste", year=2026, summary="Resumo sentinela",
            key_findings="Achado sentinela", clinical_implications="Implicação sentinela",
            theme="Tema sentinela", review_status="revisado", published=True,
        ),
        Drug(
            slug=f"{sentinela}-medicamento", generic_name=f"{sentinela} medicamento",
            drug_class="Classe sentinela", review_status="revisado", published=True,
        ),
        ClinicalCase(
            slug=f"{sentinela}-caso", titulo=f"{sentinela} caso", tema="Tema sentinela",
            nivel="intermediario", enunciado="Enunciado sentinela", pergunta="Pergunta sentinela?",
            opcoes=["A", "B"], resposta_correta=0, explicacao="Explicação sentinela",
            review_status="revisado", published=True,
        ),
        StudyTrack(
            slug=f"{sentinela}-trilha", titulo=f"{sentinela} trilha", tema="Tema sentinela",
            objetivo="Objetivo sentinela", etapas=[], review_status="revisado", published=True,
        ),
        DischargeChecklist(
            slug=f"{sentinela}-checklist", condicao=f"{sentinela} checklist",
            resumo="Resumo sentinela", theme="Tema sentinela", itens=[],
            review_status="revisado", published=True,
        ),
        PatientMaterial(
            slug=f"{sentinela}-material", titulo=f"{sentinela} material",
            tema="Tema sentinela", resumo="Resumo sentinela", secoes=[],
            review_status="revisado", published=True,
        ),
        EmergencyProtocol(
            slug=f"{sentinela}-emergencia", titulo=f"{sentinela} emergência",
            gatilho="Gatilho sentinela", documento_slug=f"{sentinela}-documento-inexistente",
            review_status="revisado", published=True,
        ),
        SpecialtyDisease(
            slug=f"{sentinela}-doenca", name=f"{sentinela} doença", area="cardiologia",
            category="categoria sentinela", summary="Resumo sentinela", completeness="completo",
            review_status="revisado", published=True,
        ),
        SymptomTriageGuide(
            slug=f"{sentinela}-triagem", name=f"{sentinela} triagem",
            areas=["cardiologia"], summary="Resumo sentinela", questions=[],
            review_status="revisado", published=True,
        ),
    ])
    db.commit()


def test_recuperar_acha_as_doze_frentes_so_por_lexico_sem_credito(db, monkeypatch):
    monkeypatch.setattr("app.services.rag.obter_provedor_embeddings", lambda: _ProvedorSemCredito())
    monkeypatch.setattr("app.services.rag.settings.ai_top_k", 40)

    sentinela = "corviasentinela"
    _semear_doze_frentes(db, sentinela)

    trechos = recuperar(db, sentinela)

    tipos_encontrados = {t["entity_type"] for t in trechos}
    faltando = FRENTES_ESPERADAS - tipos_encontrados
    assert not faltando, f"Frentes não encontradas por léxico sem crédito: {faltando}"
    for trecho in trechos:
        assert trecho["conteudo"]
        assert trecho["rota"]


def test_recuperar_acha_calculadora_so_por_lexico_sem_credito(db, monkeypatch):
    monkeypatch.setattr("app.services.rag.obter_provedor_embeddings", lambda: _ProvedorSemCredito())
    monkeypatch.setattr("app.services.rag.settings.ai_top_k", 40)

    trechos = recuperar(db, "cha2ds2-vasc")

    tipos = {t["entity_type"] for t in trechos}
    assert "calculadora" in tipos
    calc = next(t for t in trechos if t["entity_type"] == "calculadora")
    assert calc["conteudo"]
    assert calc["rota"].startswith("/calculadoras/")


def test_recuperar_nao_propaga_excecao_do_provedor_de_embeddings(db, monkeypatch):
    """O ponto central da Parte 3: falha no provedor não pode derrubar a
    pergunta inteira — só o braço semântico fica vazio, léxico responde."""
    monkeypatch.setattr("app.services.rag.obter_provedor_embeddings", lambda: _ProvedorSemCredito())

    sentinela = "corviasemcredito"
    _semear_doze_frentes(db, sentinela)

    trechos = recuperar(db, sentinela)  # não deve levantar
    assert isinstance(trechos, list)


def test_recuperar_combina_lexico_e_semantico_multi_sem_colidir(db, monkeypatch):
    """Léxico (chave `(entity_type, slug)`) e semântico (chave `chunk_id`
    inteiro) da mesma gaveta 'multi' não podem se confundir no RRF nem na
    resolução final — cada resultado continua íntegro."""
    monkeypatch.setattr("app.services.rag.obter_provedor_embeddings", lambda: _ProvedorFake())
    monkeypatch.setattr("app.services.rag_multi.obter_provedor_embeddings", lambda: _ProvedorFake())
    monkeypatch.setattr("app.services.rag.settings.ai_top_k", 40)

    from app.services.rag_multi import indexar_tipo

    sentinela = "corviahibrida"
    _semear_doze_frentes(db, sentinela)
    indexar_tipo(db, "evidencia", apenas_pendentes=False)
    indexar_tipo(db, "exame", apenas_pendentes=False)

    trechos = recuperar(db, sentinela)

    tipos_encontrados = {t["entity_type"] for t in trechos}
    faltando = FRENTES_ESPERADAS - tipos_encontrados
    assert not faltando, f"Frentes não encontradas com léxico+semântico combinados: {faltando}"
    slugs = {t["slug"] for t in trechos}
    assert f"{sentinela}-evidencia" in slugs
    assert f"{sentinela}-exame" in slugs
