from pathlib import Path

from app.services.clinical_rule_engine import evaluate_rules, validate_question_definitions, validate_rule_definitions
from app.services.disease_manifest import load_disease_records


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "doencas/metadados.json"
SLUG = "dispositivos-cardiacos-implantaveis"


def _disease():
    return next(item for item in load_disease_records(BASE) if item["slug"] == SLUG)


def _answers(disease, **overrides):
    answers = {}
    for question in disease["assistant_questions"]:
        qid = question["id"]
        qtype = question["type"]
        if qtype == "boolean":
            value = False
        elif qtype == "number":
            value = question.get("min", 0)
        elif qtype == "select":
            value = question["options"][0]["value"]
        elif qtype == "multiselect":
            value = [question["options"][0]["value"]] if question.get("required") else []
        else:
            value = "não informado"
        answers[qid] = value
    answers.update(overrides)
    return answers


def _evaluate(**overrides):
    disease = _disease()
    return evaluate_rules(
        questions=disease["assistant_questions"],
        rules=disease["assistant_rules"],
        answers=_answers(disease, **overrides),
        base_tests=disease.get("tests"),
        base_differentials=disease.get("differentials"),
        base_ambulatory_flow=disease.get("ambulatory_flow"),
        base_emergency_flow=disease.get("emergency_flow"),
    )


def test_cied_overlay_fica_revisado_e_regras_validas():
    disease = _disease()
    assert disease["review_status"] == "revisado"
    assert "Publicação autorizada" in disease["review_note"]
    q_errors, qids = validate_question_definitions(SLUG, disease["assistant_questions"])
    r_errors = validate_rule_definitions(SLUG, disease["assistant_rules"], qids)
    assert q_errors == []
    assert r_errors == []


def test_rassi_e_prognostico_e_nao_criterio_isolado_de_cdi():
    disease = _disease()
    text = str(disease).casefold()
    assert "mortalidade global" in text
    assert "não constitui critério isolado" in text
    assert any("27571011" in ref for ref in disease["source_refs"])
    assert any("16928995" in ref for ref in disease["source_refs"])


def test_febre_sem_bacteremia_nao_vira_infeccao_sistemica_de_cied():
    result = _evaluate(
        systemic_infection_signs=True,
        cied_bacteremia_without_other_source=False,
        cied_hardware_exposed_or_purulent=False,
        pocket_local_signs=False,
    )
    assert "cied-sinais-sistemicos-sem-bacteremia-documentada" in result["matched_rules"]
    assert "cied-infeccao-sistemica-suspeita" not in result["matched_rules"]
    assert result["risk"] != "emergencia"


def test_hardware_exposto_ou_pus_dispara_fluxo_especifico():
    result = _evaluate(cied_hardware_exposed_or_purulent=True)
    assert "cied-erosao-bolsa-infeccao-local" in result["matched_rules"]
    assert result["risk"] in {"urgente", "emergencia"}
    assert any("hardware" in flag.casefold() or "exposição" in flag.casefold() for flag in result["red_flags"])


def test_multiplos_choques_apropriados_sao_emergencia_e_choque_unico_nao_e_ignorado():
    multiple = _evaluate(icd_shock_history="multiplos_apropriados")
    assert "cdi-multiplos-choques-apropriados" in multiple["matched_rules"]
    assert multiple["risk"] == "emergencia"

    single = _evaluate(icd_shock_history="unico_apropriado")
    assert "cdi-choque-unico-apropriado" in single["matched_rules"]
    assert single["risk"] in {"urgente", "emergencia"}


def test_falha_suspeita_de_lead_de_choque_recebe_prioridade_propria():
    result = _evaluate(
        device_type="cdi",
        lead_dysfunction_signs=True,
        pacing_dependent=False,
        shock_lead_involved_or_suspected=True,
    )
    assert "cied-disfuncao-lead-choque" in result["matched_rules"]
    assert "cied-disfuncao-eletrodo-nao-dependente" not in result["matched_rules"]
    assert result["risk"] in {"urgente", "emergencia"}


def test_rm_com_lead_de_maior_risco_nao_recebe_reassuracao_generica():
    result = _evaluate(
        mri_needed=True,
        device_mri_conditional="nao_condicional",
        mri_high_risk_lead_context=True,
    )
    assert "cied-rm-contexto-lead-alto-risco" in result["matched_rules"]
    assert "cied-rm-nao-condicional" not in result["matched_rules"]
    assert any("avaliação individual" in msg.casefold() for msg in result["messages"])
