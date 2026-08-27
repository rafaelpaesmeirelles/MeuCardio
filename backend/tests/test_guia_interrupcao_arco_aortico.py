from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "content" / "Cardiologia_pediátrica" / "interrupcao-do-arco-aortico-do-colapso-neonatal-ao-seguimento-achd.md"


def _text() -> str:
    return DOC.read_text(encoding="utf-8")


def test_documento_cobre_anatomia_ducto_e_achd():
    text = _text().casefold()
    assert "review_status: pendente_revisao" in text
    for required in (
        "tipo a",
        "tipo b",
        "tipo c",
        "ducto",
        "22q11.2",
        "lvoto",
        "cardiopatia congênita do adulto",
    ):
        assert required in text


def test_nao_confunde_saturacao_com_perfusao_sistemica():
    text = _text().casefold()
    assert "spo₂ isolada não exclui iaa" in text
    assert "lactato" in text
    assert "diurese" in text
    assert "perfusão" in text


def test_iaa_b_abre_gate_22q11_sem_diagnostico_automatico():
    text = _text().casefold()
    assert "iaa tipo b motive investigação" in text
    assert "tipo b não confirma 22q11.2 sem teste" in text
    assert "cálcio" in text
    assert "imun" in text


def test_documento_preserva_lvoto_como_risco_longitudinal():
    text = _text().casefold()
    assert "lvoto pode emergir ou progredir depois do reparo" in text
    assert "gradiente isolado não indica reintervenção" in text


def test_sem_posologia_ou_energia_automatizada():
    text = _text().casefold()
    for pattern in (
        r"\b\d+(?:[.,]\d+)?\s*mg/kg\b",
        r"\b\d+(?:[.,]\d+)?\s*mcg/kg/min\b",
        r"\b\d+(?:[.,]\d+)?\s*j/kg\b",
    ):
        assert re.search(pattern, text) is None
    assert "não codifica dose de prostaglandina" in text
