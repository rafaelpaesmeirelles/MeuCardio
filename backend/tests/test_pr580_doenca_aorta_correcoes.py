from pathlib import Path

from app.services.disease_manifest import load_disease_records
from app.services.clinical_rule_engine import evaluate_rules


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "doencas/metadados.json"


def _disease():
    return next(item for item in load_disease_records(MANIFEST) if item["slug"] == "doenca-da-aorta")


def test_aorta_esta_revisada_e_vigilancia_aaa_e_sexo_especifica():
    disease = _disease()
    text = " ".join(disease["diagnostic_approach"]["rastreamento_e_vigilancia_do_aneurisma_de_aorta_abdominal"])
    assert disease["review_status"] == "revisado"
    assert "40-<45 mm em mulheres" in text
    assert "40-<50 mm em homens" in text
    assert "45-50 mm em mulheres" in text
    assert "50-55 mm em homens" in text


def test_aorta_tte_nao_e_rotulado_como_contraindicado():
    disease = _disease()
    blob = str(disease).casefold()
    assert "formalmente contraindicado (classe iii)" not in blob
    assert "tte é contraindicado" not in blob
    assert "não recomendado (classe iii)" in blob


def test_aorta_d_dimero_nao_e_gate_isolado_de_exclusao():
    disease = _disease()
    text = " ".join(disease["diagnostic_approach"]["diagnostico_da_sindrome_aortica_aguda"])
    assert "não deve funcionar como gate isolado de exclusão" in text
    assert "avaliação multiparamétrica" in text


def test_dor_isolada_nao_dispara_angio_tc_automatica():
    disease = _disease()
    answers = {
        "sudden_tearing_pain": True,
        "instability_shock": False,
        "pulsatile_abdominal_mass": False,
        "known_aneurysm_surveillance": False,
        "family_history_ctd": False,
        "age_range": "menor_70",
        "comorbidity_relevant": ["nenhuma_relevante"],
    }
    result = evaluate_rules(
        questions=disease["assistant_questions"],
        rules=disease["assistant_rules"],
        answers=answers,
        context="emergencia",
    )
    assert result["risk"] == "urgente"
    joined = " ".join(result.get("emergency_flow") or [])
    assert "não inferir indicação de angio-TC apenas pela dor isolada" in joined
