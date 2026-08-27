from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "content" / "Cardiologia_pediátrica" / "tronco-arterial-comum-abordagem-operacional-do-neonato-ao-adulto.md"
BASE = ROOT / "content" / "Cardiologia_pediátrica" / "tronco-arterial-comum-classificacao-associacao-com-22q11-e-desfechos-cirurgicos-contemporaneos.md"


def _text() -> str:
    return DOC.read_text(encoding="utf-8")


def test_documento_operacional_complementa_fonte_base_e_permanece_pendente():
    text = _text()
    assert DOC.exists()
    assert BASE.exists()
    assert "review_status: pendente_revisao" in text
    assert "fonte_producao: chatgpt" in text
    assert "classificação, 22q11.2 e desfechos" in text.casefold()


def test_gates_anatomicos_essenciais_estao_explicitos():
    text = _text().casefold()
    for required in (
        "interrupção do arco",
        "coronárias",
        "valva truncal",
        "trajeto vd–artéria pulmonar",
        "22q11.2",
        "cardiopatia congênita do adulto",
    ):
        assert required in text
    assert "prostaglandina não é consequência automática" in text
    assert "spo₂ relativamente alta não significa fisiologia favorável" in text


def test_tudo_com_tudo_declara_conexoes_e_limites():
    text = _text().casefold()
    assert "tudo com tudo" in text
    assert "cardiologia intensiva/uco" in text
    assert "não" in text
    assert "prescrição automática" in text or "prescrição" in text


def test_documento_nao_codifica_posologia_ou_energia():
    text = _text().casefold()
    padroes = [
        r"\b\d+(?:[.,]\d+)?\s*mg/kg\b",
        r"\b\d+(?:[.,]\d+)?\s*mcg/kg/min\b",
        r"\b\d+(?:[.,]\d+)?\s*j/kg\b",
        r"\b\d+(?:[.,]\d+)?\s*mg\s+(?:iv|ev|vo)\b",
    ]
    assert all(re.search(pattern, text) is None for pattern in padroes)


def test_transicao_para_achd_carrega_mapa_anatomico_cirurgico():
    text = _text().casefold()
    for required in (
        "mapa anatômico e cirúrgico",
        "operações prévias",
        "conduto",
        "neoaorta",
        "seguimento",
    ):
        assert required in text
