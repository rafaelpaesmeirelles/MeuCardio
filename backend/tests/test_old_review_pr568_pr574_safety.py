from pathlib import Path

from app.services.clinical_rule_engine import (
    validate_question_definitions,
    validate_rule_definitions,
)
from app.services.disease_manifest import load_disease_records


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "doencas/metadados.json"
SLUGS = {
    "miocardite",
    "dislipidemia",
    "diabetes-mellitus-tipo-2",
    "tromboembolismo-venoso",
}


def _records():
    return {
        item["slug"]: item
        for item in load_disease_records(BASE)
        if item["slug"] in SLUGS
    }


def _rules(record):
    return {item["id"]: item for item in record["assistant_rules"]}


def _questions(record):
    return {item["id"]: item for item in record["assistant_questions"]}


def test_quatro_hubs_permanecem_revisados_e_com_regras_validas():
    records = _records()
    assert records.keys() == SLUGS
    for slug, record in records.items():
        assert record["review_status"] == "revisado"
        question_errors, question_ids = validate_question_definitions(
            slug, record["assistant_questions"]
        )
        rule_errors = validate_rule_definitions(
            slug, record["assistant_rules"], question_ids
        )
        assert question_errors == []
        assert rule_errors == []


def test_miocardite_nao_indica_biopsia_automaticamente_nem_absolutiza_classe_iii():
    record = _records()["miocardite"]
    text = str(record).casefold()
    high_risk = _rules(record)["alto-risco-estratificacao"]
    assert "não torna a biópsia obrigatória" in str(high_risk).casefold()
    assert "não equivale a contraindicação absoluta" in text
    assert "idade, sexo, produto e dose" in text
    assert "números históricos" in text


def test_dislipidemia_exige_dois_de_tres_e_nao_recomenda_heparina_rotineira():
    record = _records()["dislipidemia"]
    questions = _questions(record)
    rules = _rules(record)
    text = str(record).casefold()
    assert "2 de 3 critérios" in questions["acute_pancreatitis_now"]["label"]
    assert "não usar heparina rotineiramente" in str(
        rules["disl-pancreatite-aguda-em-curso"]
    ).casefold()
    assert "inclisirana" in text and "não deve ser apresentada" in text
    assert "disl-risco-cardiovascular-a-calcular" in rules
    assert "disl-hepatopatia-ativa-separada-da-intolerancia-muscular" in rules


def test_diabetes_tem_rank_opcao_exclusiva_e_regras_renal_e_perioperatoria():
    record = _records()["diabetes-mellitus-tipo-2"]
    questions = _questions(record)
    rules = _rules(record)
    text = str(record).casefold()
    therapy = questions["current_cv_protective_therapy"]
    assert record["prevalence_rank"] == 1
    assert therapy["type"] == "select"
    assert {option["value"] for option in therapy["options"]} == {
        "isglt2",
        "glp1_ra",
        "ambas",
        "nenhuma",
    }
    assert rules["dmt2cv-sem-terapia-protetora"]["when"]["all"][0]["op"] == "eq"
    assert "pelo menos 3 dias" in text and "pelo menos 4 dias" in text
    assert "dmt2cv-finerenona-elegivel" in rules
    assert "não constitui, isoladamente, indicação" in text


def test_tev_limita_apicat_e_qualifica_obesidade_e_perfil_de_saf():
    record = _records()["tromboembolismo-venoso"]
    rules = _rules(record)
    text = str(record).casefold()
    assert "apixabana 2,5 mg duas vezes ao dia" in text
    assert "não deve ser generalizado automaticamente" in text
    assert "tev-obesidade-extrema" in rules
    assert "tev-cirurgia-bariatrica" in rules
    assert "tev-saf-alto-risco" in rules
    assert "tev-saf-venosa-baixo-risco" in rules
    assert any("40162636" in ref for ref in record["source_refs"])
    assert any("34259389" in ref for ref in record["source_refs"])
    assert any("30002145" in ref for ref in record["source_refs"])
