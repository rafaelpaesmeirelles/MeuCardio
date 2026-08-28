from pathlib import Path

from app.services.disease_manifest import load_disease_records
from app.services.clinical_rule_engine import evaluate_rules


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "doencas/metadados.json"


def _disease():
    return next(item for item in load_disease_records(MANIFEST) if item["slug"] == "doenca-da-aorta")


def _answers(**overrides):
    answers = {
        "sudden_tearing_pain": False,
        "instability_shock": False,
        "pulsatile_abdominal_mass": False,
        "known_aneurysm_surveillance": False,
        "family_history_ctd": False,
        "age_range": "menor_70",
        "comorbidity_relevant": ["nenhuma_relevante"],
    }
    answers.update(overrides)
    return answers


def _evaluate(**overrides):
    disease = _disease()
    return evaluate_rules(
        questions=disease["assistant_questions"],
        rules=disease["assistant_rules"],
        answers=_answers(**overrides),
        context="emergencia",
    )


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
    result = _evaluate(sudden_tearing_pain=True)
    assert result["risk"] == "urgente"
    joined = " ".join(result.get("emergency_flow") or []).casefold()
    assert "não inferir indicação de angio-tc apenas pela dor isolada" in joined


def test_instabilidade_isolada_permanece_emergencia_sem_rotular_ruptura_aortica():
    result = _evaluate(instability_shock=True)
    assert "aorta-instabilidade-ruptura" not in result["matched_rules"]
    assert "aorta-instabilidade-generica-sem-evidencia-especifica" in result["matched_rules"]
    assert result["risk"] == "emergencia"
    joined = " ".join(result.get("emergency_flow") or []).casefold()
    assert "sem inferir ruptura" in joined or "não inferir ruptura" in joined
    assert "acionar cirurgia vascular/cardiovascular" not in joined


def test_instabilidade_com_evidencia_aortica_corrobora_fluxo_especifico():
    result = _evaluate(instability_shock=True, known_aneurysm_surveillance=True)
    assert "aorta-instabilidade-ruptura" in result["matched_rules"]
    assert result["risk"] == "emergencia"


def test_crescimento_toracico_e_fator_de_risco_nao_indicacao_universal():
    disease = _disease()
    blob = str(disease).casefold()
    assert "não é indicação cirúrgica universal isolada" in blob
    assert "≥3-5 mm/ano na aorta torácica — indicação de reparo independente" not in blob


def test_nonagenario_preserva_incerteza_e_nao_declara_equivalencia():
    result = _evaluate(age_range="90_ou_mais")
    supporting = " ".join(result["supporting"]).casefold()
    assert "não detectou associação independente" in supporting
    assert "não demonstra equivalência" in supporting
    assert "mortalidade em 30 dias comparável" not in supporting
