from pathlib import Path

from app.services.disease_manifest import load_disease_records


BASE = Path(__file__).resolve().parents[2] / "doencas" / "metadados.json"


def _records():
    return {item["slug"]: item for item in load_disease_records(BASE)}


def _by_id(items):
    return {item["id"]: item for item in items}


def _has(conditions, field, op=None, value=None):
    return any(
        item.get("field") == field
        and (op is None or item.get("op") == op)
        and (value is None or item.get("value") == value)
        for item in conditions
    )


def test_pr685_im_separa_nao_grave_e_restringe_gatilhos_de_intervencao():
    hub = _records()["insuficiencia-mitral"]
    rules = _by_id(hub["assistant_rules"])

    nonsevere = rules["rule_nonsevere_mr_no_intervention_trigger"]
    assert _has(nonsevere["when"]["any"], "mr_severity", "eq", "leve")
    assert _has(nonsevere["when"]["any"], "mr_severity", "eq", "moderada")

    lv = rules["rule_primary_mr_incipient_dysfunction"]["when"]["all"]
    assert _has(lv, "lvef_percent", "lte", 60)
    assert not _has(lv, "incipient_lv_dysfunction")

    hf = rules["rule_secondary_mr_optimize_therapy"]["when"]["all"]
    assert _has(hf, "secondary_mr_mechanism", "eq", "ventricular")

    teer = rules["rule_high_surgical_risk_alternative"]["when"]["all"]
    assert _has(teer, "mr_severity", "eq", "grave")
    assert _has(teer, "teer_candidate_criteria", "truthy")

    af = rules["rule_primary_severe_mr_new_af_intervention"]["when"]["all"]
    assert _has(af, "mr_etiology", "eq", "primaria")
    assert _has(af, "mr_severity", "eq", "grave")

    acute = " ".join(rules["rule_acute_severe_mr_emergency"]["add"]["emergency_flow"])
    assert "cirurgia cardíaca" in acute
    assert "urgente" in acute


def test_pr688_em_anatomia_edema_wilkins_e_doac_contextualizados():
    hub = _records()["estenose-mitral"]
    questions = _by_id(hub["assistant_questions"])
    rules = _by_id(hub["assistant_rules"])

    assert questions["wilkins_score"]["min"] == 4
    assert questions["wilkins_score"]["max"] == 16

    favorable = rules["anatomia_favoravel_valvuloplastia"]["when"]["all"]
    assert _has(favorable, "etiology", "eq", "reumatica")
    assert _has(favorable, "severity_ms", "eq", "grave")
    assert _has(favorable, "symptomatic", "truthy")

    edema = rules["edema_agudo_pulmao_taquiarritmia"]
    assert len(edema["when"]["all"]) == 1
    assert _has(edema["when"]["all"], "acute_pulmonary_edema", "truthy")
    assert "tempo diastólico" in " ".join(edema["add"]["emergency_flow"])

    doac = rules["doac_inadequado_fa_reumatica"]["when"]
    assert _has(doac["any"], "mitral_valve_area_cm2", "lte", 2.0)
    assert _has(doac["any"], "severity_ms", "eq", "moderada")
    assert "degenerativa/calcífica" in hub["summary"]
    assert "estenose degenerativa/calcífica" in hub["treatment_summary"]


def test_pr689_cmd_valida_fe_periparto_remoto_e_elegibilidade_de_dispositivos():
    hub = _records()["cardiomiopatia-dilatada"]
    questions = _by_id(hub["assistant_questions"])
    rules = _by_id(hub["assistant_rules"])

    assert questions["fracao_ejecao_percentual"]["min"] == 0
    assert questions["fracao_ejecao_percentual"]["max"] == 100

    acute_peripartum = rules["periparto_suporte"]["when"]["all"]
    assert len(acute_peripartum) == 1
    assert _has(acute_peripartum, "periodo_periparto_atual", "truthy")
    assert "urgência obstétrica" in " ".join(
        rules["periparto_remoto_sem_urgencia_obstetrica"]["add"]["messages"]
    )

    icd = rules["cdi_prevencao_primaria_avaliar"]["when"]
    for field in (
        "fracao_ejecao_percentual",
        "em_terapia_otimizada_guiada_diretriz",
        "tempo_terapia_otimizada_dias",
        "causas_reversiveis_excluidas",
        "sobrevida_funcional_maior_um_ano",
    ):
        assert _has(icd["all"], field)
    assert _has(icd["any"], "classe_funcional_nyha", "eq", "ii")
    assert _has(icd["any"], "classe_funcional_nyha", "eq", "iii")

    crt = rules["trc_avaliar"]["when"]
    assert _has(crt["all"], "ritmo_sinusal", "truthy")
    assert _has(crt["any"], "classe_funcional_nyha", "eq", "ii")
    assert _has(crt["any"], "classe_funcional_nyha", "eq", "iv")


def test_pr690_hsat_iah_stop_bang_e_fa_corrigidos_sem_pmid_irrelevante():
    hub = _records()["apneia-do-sono-e-coracao"]
    questions = _by_id(hub["assistant_questions"])
    rules = _by_id(hub["assistant_rules"])

    diagnostic = hub["diagnostic_approach"]
    assert "leve: IAH de 5 a <15/h" in diagnostic
    assert "moderada: 15 a <30/h" in diagnostic
    assert "grave: ≥30/h" in diagnostic
    assert "sem doença cardiorrespiratória significativa" in diagnostic

    score = questions["stop_bang_score"]
    assert (score["min"], score["max"], score["step"]) == (0, 8, 1)
    intermediate = rules["stop_bang_intermediario_ambulatorial"]["when"]["all"]
    assert _has(intermediate, "stop_bang_score", "gte", 3)
    assert _has(intermediate, "stop_bang_score", "lte", 4)

    af = rules["fibrilacao_atrial_apneia_nao_tratada"]["when"]["all"]
    assert _has(af, "sleep_apnea_type", "eq", "obstrutiva")
    assert "21300732" not in " ".join(hub["source_refs"] + hub["source_urls"])


def test_vicadrostat_nao_mantem_placeholder_nem_cifra_nao_sustentada():
    path = BASE.parents[1] / "content" / "Hipertensão" / (
        "vicadrostat-terceiro-inibidor-da-aldosterona-sintase-da-drc-a-hipertensao.md"
    )
    text = path.read_text(encoding="utf-8")
    assert "VERIFICAÇÃO HUMANA" not in text
    assert "nenhum valor em mmHg deve ser atribuído" in text
    assert "registro oficial vigente" in text
