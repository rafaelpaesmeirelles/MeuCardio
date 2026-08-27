from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "content" / "Cardiopatias_congênitas" / "valva-truncal-neoaortica-disfuncao-reintervencao-e-seguimento-no-tronco-arterial.md"


def _text() -> str:
    return DOC.read_text(encoding="utf-8")


def test_documento_permanece_pendente_e_longitudinal():
    text = _text().casefold()
    assert "review_status: pendente_revisao" in text
    assert "nó longitudinal tudo com tudo" in text
    assert "valva neoaórtica" in text or "neoaórtica" in text
    assert "15 anos" in text


def test_nao_transforma_marcadores_em_gatilho_cirurgico():
    text = _text().casefold()
    assert "marcadores de risco, não gatilhos isolados de cirurgia" in text
    assert "z-score não é indicação cirúrgica automática" in text
    assert "moderada" in text
    assert "quadricúspide" in text


def test_separa_reparo_de_substituicao_em_lactente():
    text = _text().casefold()
    assert "substituição neonatal/infantil" in text
    assert "não deve aparecer no sistema como alternativa equivalente" in text
    assert "metanálise de 2023" in text


def test_tudo_com_tudo_conecta_conduto_coronaria_endocardite_e_achd():
    text = _text().casefold()
    for required in (
        "conduto vd–ap",
        "coron",
        "endocardite",
        "achd",
        "função do ve",
    ):
        assert required in text


def test_nao_extrapola_valvopatia_aortica_adquirida():
    text = _text().casefold()
    assert "extrapolar critérios de valvopatia aórtica adquirida" in text
    assert "limiares de aneurisma degenerativo" in text


def test_sem_posologia_ou_energia():
    text = _text().casefold()
    for pattern in (
        r"\b\d+(?:[.,]\d+)?\s*mg/kg\b",
        r"\b\d+(?:[.,]\d+)?\s*mcg/kg/min\b",
        r"\b\d+(?:[.,]\d+)?\s*j/kg\b",
    ):
        assert re.search(pattern, text) is None
