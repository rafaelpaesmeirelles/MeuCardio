"""Contrato do nó cardiovascular 22q11.2 do Guia de Doenças."""

from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "content" / "Cardiologia_pediátrica" / "22q11-2-cardiovascular-cardiopatias-conotruncais-seguranca-perioperatoria-e-transicao.md"


def _text() -> str:
    return DOC.read_text(encoding="utf-8")


def test_documento_preserva_revisao_humana_e_fontes_atuais():
    text = _text()
    assert "review_status: pendente_revisao" in text
    assert "fonte_producao: chatgpt" in text
    assert "Pediatrics. 2025" in text
    assert "GeneReviews" in text and "2025" in text
    assert "Genet Med. 2023" in text


def test_fenotipos_cardiacos_acionam_investigacao_sem_diagnostico_automatico():
    text = _text()
    for required in (
        "interrupção do arco aórtico tipo B",
        "tronco arterial comum",
        "tetralogia de Fallot",
        "CIV com anomalia do arco aórtico",
        "anomalia isolada do arco aórtico",
        "chromosome microarray",
        "Não inferir 22q11.2 apenas pelo nome da cardiopatia",
    ):
        assert required in text


def test_gate_perioperatorio_integra_imunidade_hemoderivados_e_calcio():
    text = _text()
    assert "CMV-negativos e irradiados" in text
    assert "profilaxia antimicrobiana" in text
    assert "monitorar cálcio pré e pós-operatório" in text
    assert "PTH" in text
    assert "não autoriza selecionar antibiótico" in text
    assert "não define dose de reposição" in text


def test_no_transversal_linka_apenas_documentos_existentes_da_base():
    text = _text()
    slugs = re.findall(r"\]\(/biblioteca/([^)]+)\)", text)
    assert set(slugs) == {
        "tronco-arterial-comum-classificacao-associacao-com-22q11-e-desfechos-cirurgicos-contemporaneos",
        "tetralogia-de-fallot-rastreio-pre-natal-crise-de-hipoxia-e-estrategia-cirurgica",
        "dupla-via-de-saida-de-ventriculo-direito-classificacao-anatomica-estrategia-cirurgica-e-desfechos",
    }
    document_slugs = {path.stem for path in (ROOT / "content").rglob("*.md")}
    assert set(slugs) <= document_slugs


def test_transicao_ach_intensiva_e_tudo_com_tudo_ficam_explicitos():
    text = _text()
    assert "Transição pediatria → cardiologia do adulto congênito" in text
    assert "Interface com Cardiologia Intensiva/UCO" in text
    assert "Relações clínicas diretas a preservar no grafo" in text
    assert "Relações que **não** devem ser automatizadas" in text
    for required in (
        "função de ambos os ventrículos",
        "história de arritmia",
        "situação conhecida da imunidade",
        "história de hipocalcemia/hipoparatireoidismo",
    ):
        assert required in text


def test_documento_nao_embute_posologia_energia_ou_prescricao_automatica():
    text = _text().casefold()
    forbidden_patterns = (
        r"\b\d+(?:[.,]\d+)?\s*mg/kg\b",
        r"\b\d+(?:[.,]\d+)?\s*mcg/kg/min\b",
        r"\b\d+(?:[.,]\d+)?\s*joules?\b",
        r"\b\d+(?:[.,]\d+)?\s*j/kg\b",
    )
    for pattern in forbidden_patterns:
        assert re.search(pattern, text) is None
    assert "não deve escolher vasoativo" in text
    assert "diagnóstico automático de 22q11.2" in text
    assert "indicação automática de cirurgia ou reintervenção" in text
