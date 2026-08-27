from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "content" / "Cardiopatias_congênitas" / "conduto-ventriculo-direito-arteria-pulmonar-seguimento-reintervencao-e-valva-transcateter.md"


def _text() -> str:
    return DOC.read_text(encoding="utf-8")


def test_documento_e_transversal_e_permanece_pendente():
    text = _text().casefold()
    assert "review_status: pendente_revisao" in text
    assert "nó longitudinal tudo com tudo" in text
    for required in ("tronco arterial comum", "atresia pulmonar", "rastelli", "ross"):
        assert required in text


def test_preserva_criterios_achd_2025_com_nivel_de_evidencia():
    text = _text()
    assert "COR 1, LOE B-NR" in text
    assert "COR 2a, LOE B-NR" in text
    assert "COR 2a, LOE C-LD" in text


def test_coronaria_e_gate_pre_intervencao():
    text = _text().casefold()
    assert "risco de compressão coronariana" in text
    assert "tc coronariana" in text
    assert "teste de compressão" in text
    assert "não substitui avaliação" in text or "não substitui" in text


def test_nao_automatiza_dispositivo_ou_indicacao_por_numero_isolado():
    text = _text().casefold()
    assert "gradiente isolado" in text
    assert "diâmetro do conduto → escolha automática" in text
    assert "um único número" in text


def test_endocardite_e_stent_sao_complicacoes_explicitas():
    text = _text().casefold()
    assert "endocardite" in text
    assert "fratura" in text
    assert "stent" in text


def test_sem_posologia_ou_energia():
    text = _text().casefold()
    for pattern in (
        r"\b\d+(?:[.,]\d+)?\s*mg/kg\b",
        r"\b\d+(?:[.,]\d+)?\s*mcg/kg/min\b",
        r"\b\d+(?:[.,]\d+)?\s*j/kg\b",
    ):
        assert re.search(pattern, text) is None
