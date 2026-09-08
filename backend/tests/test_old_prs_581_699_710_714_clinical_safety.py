import json
import re
from pathlib import Path

import pytest

from app.services.disease_manifest import load_disease_records
from app.services.triage_manifest import load_triage_records


ROOT = Path(__file__).resolve().parents[2]
DISEASES = ROOT / "doencas" / "metadados.json"
TRIAGE = ROOT / "triagem-sintomas" / "metadados.json"
DOSE_TOKEN = re.compile(
    r"(?i)(?<![\w])\d+(?:[.,]\d+)?\s*(?:mg|mcg|µg|μg|g|ui)(?:\s*/\s*(?:kg|min|h|dia|ml))?\b"
)


@pytest.fixture(scope="module")
def diseases():
    return {item["slug"]: item for item in load_disease_records(DISEASES)}


@pytest.fixture(scope="module")
def triages():
    return {item["slug"]: item for item in load_triage_records(TRIAGE)}


def _by_id(items, identifier):
    return next(item for item in items if item["id"] == identifier)


@pytest.mark.parametrize(
    "token",
    ["6 mg", "100 mcg", "50 µg", "50 μg", "1 g", "5 UI", "0,1 mcg/kg/min"],
)
def test_dose_guard_recognizes_all_relevant_units(token):
    assert DOSE_TOKEN.search(token), token


def test_pr581_separates_regular_svt_from_preexcited_af(diseases):
    svt = diseases["taquicardia-supraventricular"]
    rules = svt["assistant_rules"]
    preexcited = _by_id(rules, "tsv-fa-preexcitada-suspeita")
    assert preexcited["when"] == {
        "all": [{"field": "current_ecg_pattern", "op": "eq", "value": "qrs_largo_irregular"}]
    }
    text = json.dumps(preexcited, ensure_ascii=False).lower()
    assert "procainamida" in text and "ibutilida" in text
    assert "flecainida/propafenona sem avaliação" in text
    stable = _by_id(rules, "tsv-aguda-estavel-estreita-regular")
    assert "qrs_estreito_regular" in json.dumps(stable)
    instability = _by_id(rules, "tsv-instabilidade-hemodinamica")
    assert "taquicardia_atual_em_curso" in json.dumps(instability)


def test_pr581_vagal_mat_wpw_and_pregnancy_guards(diseases):
    svt = diseases["taquicardia-supraventricular"]
    rules = svt["assistant_rules"]
    vagal = _by_id(rules, "tsv-resposta-manobra-vagal")
    assert "terminou_abruptamente" in json.dumps(vagal)
    assert "qrs_estreito_regular" in json.dumps(vagal)
    assert "hemodynamic_instability" in json.dumps(vagal)
    slowed = _by_id(rules, "tsv-manobra-apenas-lentificou")
    assert "não confirma" in json.dumps(slowed, ensure_ascii=False)
    mat = _by_id(rules, "tsv-doenca-pulmonar-multifocal")
    assert "underlying_lung_disease" not in json.dumps(mat)
    assert "60% dos casos" in svt["epidemiology"]
    assert "SPERRI ≤250 ms" in json.dumps(svt, ensure_ascii=False)
    assert "qualquer trimestre" in json.dumps(
        _by_id(rules, "tsv-gestacao-regular-estavel"), ensure_ascii=False
    )


def test_pr699_has_autonomous_troponin_intoxication_qrs_and_qtc_flows(diseases):
    record = diseases["cardiotoxicidade-por-cocaina-e-estimulantes"]
    question_ids = {item["id"] for item in record["assistant_questions"]}
    rule_ids = {item["id"] for item in record["assistant_rules"]}
    assert "ecg_qtc_prolongado" in question_ids
    assert {
        "troponina_alterada_fluxo_sca",
        "intoxicacao_simpaticomimetica_ativa",
        "qtc_prolongado_toxicidade_eletrica",
    } <= rule_ids
    qrs = _by_id(record["assistant_rules"], "qrs_alargado_bloqueio_sodio")
    assert qrs["add"]["risk"] == "emergencia"


def test_pr710_limits_isolated_surgery_and_updates_evidence(diseases):
    record = diseases["insuficiencia-tricuspide"]
    surgery = _by_id(record["assistant_rules"], "cirurgia_isolada_considerar")
    assert {"field": "gravidade_it", "op": "eq", "value": "grave"} in surgery["when"]["all"]
    assert "hospitalizações recorrentes" in record["treatment_summary"]
    all_text = json.dumps(record, ensure_ascii=False).lower()
    assert "comparação indireta" in all_text
    assert "10.1016/j.amjcard.2025.02.033" in all_text


def test_pr711_cied_collects_missing_findings_and_does_not_call_mass_vegetation(triages):
    record = triages["suspeita-infeccao-dispositivo-cardiaco-implantavel"]
    questions = {item["id"]: item for item in record["questions"]}
    assert questions["days_since_procedure"]["max"] == 3650
    assert {
        "dehiscence_communicates_with_pocket",
        "pocket_pain_tenderness",
        "early_inflammation_severe_or_progressive",
    } <= questions.keys()
    dehiscence = _by_id(record["rules"], "deiscencia-sutura")
    assert "dehiscence_communicates_with_pocket" in json.dumps(dehiscence)
    mass = _by_id(record["rules"], "vegetacao-eletrodo-previa")
    assert "não é sinônimo automático" in json.dumps(mass, ensure_ascii=False)
    _by_id(record["rules"], "febre-isolada-em-portador-cied")


def test_pr712_vascular_triage_has_nonoverlapping_late_radial_branch(triages):
    record = triages["complicacao-local-pos-cateterismo-procedimento-vascular"]
    site = _by_id(record["questions"], "access_site")
    assert {item["value"] for item in site["options"]} >= {"radial", "ulnar", "femoral"}
    neuro = _by_id(record["rules"], "isquemia-aguda-deficit-neurologico")
    assert "distal_pulse_absent_or_reduced" not in json.dumps(neuro)
    late = _by_id(record["rules"], "deteccao-tardia-possivel-rao-radial")
    assert "capillary_refill_delayed" in json.dumps(late)
    benign = _by_id(record["rules"], "equimose-leve-estavel-sem-outros-sinais")
    assert {"field": "capillary_refill_delayed", "op": "falsy"} in benign["when"]["all"]


def test_pr713_has_sequential_dissection_and_syndrome_specific_branches(diseases):
    record = diseases["emergencia-hipertensiva"]
    text = json.dumps(record, ensure_ascii=False).lower()
    assert "antes do vasodilatador" in text
    assert "trombectomia" in text
    assert "pa_gestacional_grave_persistente" in text
    assert "tipo_excesso_catecolaminergico" in text
    assert "emergencia-outros-orgaos-alvo" in text
    assert "apenas_pa_elevada_sem_lesao" not in text


def test_pr714_separates_ctepd_and_current_emergencies(diseases):
    record = diseases["cteph"]
    text = json.dumps(record, ensure_ascii=False).lower()
    assert "pulmonary_hypertension_confirmed" in text
    assert "ctepd sem hipertensão pulmonar" in text
    assert "investigacional/off-label" in text
    assert "hemoptise_ameacadora" in text
    residual = _by_id(record["assistant_rules"], "residual-pos-eap-reavaliar")
    assert "papm_pos_eap_ge_38" in json.dumps(residual)
    assert "rvp_pos_eap_ge_5" in json.dumps(residual)
    assert any(
        slug.startswith("falencia-aguda-do-ventriculo-direito")
        for slug in record["related_document_slugs"]
    )


def test_old_pr_rules_do_not_embed_unreviewed_numeric_drug_doses(diseases, triages):
    selected = [
        diseases[slug]
        for slug in (
            "cardiotoxicidade-por-cocaina-e-estimulantes",
            "insuficiencia-tricuspide",
            "emergencia-hipertensiva",
            "cteph",
            "wolff-parkinson-white",
            "taquicardia-supraventricular",
        )
    ] + [
        triages["suspeita-infeccao-dispositivo-cardiaco-implantavel"],
        triages["complicacao-local-pos-cateterismo-procedimento-vascular"],
    ]
    for record in selected:
        rules = record.get("assistant_rules", record.get("rules", []))
        assert not DOSE_TOKEN.search(json.dumps(rules, ensure_ascii=False)), record["slug"]
