from pathlib import Path

from app.services.disease_manifest import load_disease_records


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "doencas/metadados.json"


def _hub():
    return next(item for item in load_disease_records(BASE) if item["slug"] == "hipertensao-resistente-e-refrataria")


def _question(hub, question_id):
    return next(item for item in hub["assistant_questions"] if item["id"] == question_id)


def _rule(hub, rule_id):
    return next(item for item in hub["assistant_rules"] if item["id"] == rule_id)


def _strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from _strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _strings(item)


def test_har_revisada_e_autorizada():
    hub = _hub()
    note = hub["review_note"].casefold()
    assert hub["review_status"] == "revisado"
    assert "publicação autorizada" in note
    assert "responsável médico" in note


def test_emergencia_exige_pa_acentuada_e_lesao_aguda():
    hub = _hub()
    rule = _rule(hub, "har-emergencia-lesao-orgao-alvo")
    assert {item["field"] for item in rule["when"]["all"]} == {"hypertensive_crisis_now", "acute_target_organ_symptoms"}


def test_resistencia_confirmada_exige_exclusao_de_pseudorresistencia_e_seguranca_mra():
    hub = _hub()
    rule = _rule(hub, "har-resistencia-confirmada-sem-mra")
    fields = {item["field"] for item in rule["when"]["all"]}
    for required in ("out_of_office_confirmation", "adherence_confirmed", "bp_measurement_technique", "mra_safety_status"):
        assert required in fields
    assert "adesao_confirmada" in str(rule)
    assert "tecnica_confirmada_adequada" in str(rule)


def test_refratariedade_exige_pa_cronica_nao_controlada():
    hub = _hub()
    control = _question(hub, "chronic_bp_control")
    assert control["required"] is True
    rule = _rule(hub, "har-refrataria-cinco-classes")
    assert any(item["field"] == "chronic_bp_control" and item["value"] == "nao_controlada" for item in rule["when"]["all"])
    text = " ".join(rule["add"]["messages"]).casefold()
    assert "ativação de barorreflexo não é terapia rotineira" in text


def test_amilorida_nao_e_mra_e_hipercalemia_nao_recebe_substituto_poupador_de_k():
    hub = _hub()
    assert "amilorida" not in _question(hub, "includes_mra")["label"].casefold()
    assert _question(hub, "includes_amiloride")["required"] is True
    limited = _rule(hub, "har-mra-limitado-por-potassio-ou-rim")
    text = " ".join(limited["add"]["messages"]).casefold()
    assert "não substituir automaticamente" in text
    assert "eplerenona ou amilorida" in text

    safety_triggers = ("hipercalemia", "hiperpotassemia", "função renal", "taxa de filtração", "tfge", "disfunção renal")
    potassium_sparing = ("amilorida", "eplerenona")
    safe_qualifiers = (
        "não substituir",
        "não deve ser usada",
        "não usar",
        "apenas se",
        "se potássio e função renal permitirem",
        "k/tfge permitirem",
        "podem perpetuar risco de hiperpotassemia",
    )
    unsafe = []
    for raw in _strings(hub):
        value = raw.casefold()
        if any(drug in value for drug in potassium_sparing) and any(trigger in value for trigger in safety_triggers):
            if not any(qualifier in value for qualifier in safe_qualifiers):
                unsafe.append(raw)
    assert unsafe == [], f"Recomendações poupadoras de K sem trava explícita: {unsafe}"


def test_mra_so_e_sugerido_apos_k_e_funcao_renal_revistos():
    hub = _hub()
    safety = _question(hub, "mra_safety_status")
    assert safety["required"] is True
    unknown = _rule(hub, "har-mra-seguranca-nao-avaliada")
    assert "potássio" in " ".join(unknown["add"]["suggested_tests"]).casefold()
    assert "tfge" in " ".join(unknown["add"]["suggested_tests"]).casefold()


def test_barorreflexo_nao_e_apresentado_como_opcao_rotineira_e_fontes_atualizadas():
    hub = _hub()
    text = str(hub).casefold()
    assert "ativação do barorreflexo" in text
    assert "permanece estratégia investigacional/não rotineira" in text
    assert "não são recomendadas rotineiramente" in text
    refs = " ".join(hub["source_refs"])
    assert "39210715" in refs
    assert "BAXFENDY" in refs
