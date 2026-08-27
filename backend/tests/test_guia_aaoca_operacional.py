from pathlib import Path

import frontmatter


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "content/Cardiopatias_congênitas/aaoca-origem-aortica-anomala-de-coronaria-risco-isquemia-e-decisao-operacional.md"


def _document():
    return frontmatter.loads(DOC.read_text(encoding="utf-8"))


def test_aaoca_esta_revisado_e_fontes_sao_strings():
    doc = _document()
    assert doc.metadata["review_status"] == "revisado"
    assert "publicação autorizada" in doc.metadata["review_note"]
    assert "responsável médico" in doc.metadata["review_note"]
    assert doc.metadata["fonte_producao"] == "chatgpt"
    assert doc.metadata["slug"] == "aaoca-origem-aortica-anomala-de-coronaria-risco-isquemia-e-decisao-operacional"
    assert len(doc.metadata["source_refs"]) >= 3
    assert all(isinstance(ref, str) for ref in doc.metadata["source_refs"])


def test_aaoca_separa_anatomia_isquemia_e_decisao_compartilhada():
    text = DOC.read_text(encoding="utf-8").casefold()
    for required in (
        "angio",
        "curso intramural",
        "óstio em fenda",
        "ângulo agudo",
        "isquemia",
        "exercício ou dobutamina",
        "decisão compartilhada",
        "seguimento longitudinal",
    ):
        assert required in text


def test_aaoca_preserva_indicacao_cirurgica_sem_menu_automatico():
    text = DOC.read_text(encoding="utf-8").casefold()
    assert "sintomas atribuíveis à anomalia" in text
    assert "evidência diagnóstica de isquemia miocárdica atribuível" in text
    assert "coronária esquerda anômala" in text
    assert "anatomia de alto risco" in text
    assert "interarterial = operar" in text
    assert "não deve" in text
    assert "escolher técnica cirúrgica" in text


def test_aaoca_nao_trata_teste_negativo_como_risco_zero():
    text = DOC.read_text(encoding="utf-8").casefold()
    assert "teste negativo" in text
    assert "risco zero" in text
    assert "ecg de esforço isolado" in text


def test_aaoca_tudo_com_tudo_aponta_para_nos_existentes():
    text = DOC.read_text(encoding="utf-8")
    assert "../Cardiologia_pediátrica/origem-aortica-anomala-de-coronaria-com-sincope-ou-isquemia-de-esforco.md" in text
    assert "cardiopatia-congenita-do-adulto-achd-manejo-abrangente-esc-2020.md" in text
    assert "teste-cardiopulmonar-de-exercicio-na-cardiopatia-congenita-aha-2025.md" in text


def test_aaoca_nao_embute_posologia_ou_parametro_de_dispositivo():
    text = DOC.read_text(encoding="utf-8").casefold()
    for forbidden in ("mg/kg", "mcg/kg", "meq/h", "mmol/h", "j/kg", "p-level", "rpm"):
        assert forbidden not in text
