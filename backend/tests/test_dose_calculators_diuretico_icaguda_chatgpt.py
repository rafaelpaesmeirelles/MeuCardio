"""Testes da calculadora que reproduz a metodologia do ensaio DOSE.

Fonte: ChatGPT.
"""

from app.services.dose_calculators_diuretico_icaguda_chatgpt import DIURETICO_IC_AGUDA_DOSE_REGISTRY


def _calc():
    return DIURETICO_IC_AGUDA_DOSE_REGISTRY["furosemida-iv-ic-aguda-estrategia-dose-trial"]


def test_equivalencias_do_dose_trial():
    furo = _calc().compute({"farmaco_casa": "furosemida", "dose_oral_dia": 80, "estrategia": "baixa", "modo": "bolus_q12"})
    tors = _calc().compute({"farmaco_casa": "torsemida", "dose_oral_dia": 40, "estrategia": "baixa", "modo": "bolus_q12"})
    bume = _calc().compute({"farmaco_casa": "bumetanida", "dose_oral_dia": 2, "estrategia": "baixa", "modo": "bolus_q12"})
    assert furo["equivalente_furosemida_oral_mg_dia"] == 80.0
    assert tors["equivalente_furosemida_oral_mg_dia"] == 80.0
    assert bume["equivalente_furosemida_oral_mg_dia"] == 80.0


def test_baixa_dose_bolus_q12_divide_total_em_duas_doses():
    r = _calc().compute({"farmaco_casa": "furosemida", "dose_oral_dia": 120, "estrategia": "baixa", "modo": "bolus_q12"})
    assert r["total_iv_furosemida_mg_dia"] == 120.0
    assert r["bolus_mg_q12h"] == 60.0


def test_alta_dose_multiplica_por_2_5():
    r = _calc().compute({"farmaco_casa": "furosemida", "dose_oral_dia": 120, "estrategia": "alta", "modo": "bolus_q12"})
    assert r["total_iv_furosemida_mg_dia"] == 300.0
    assert r["bolus_mg_q12h"] == 150.0


def test_infusao_continua_converte_total_dia_em_mg_h():
    r = _calc().compute({"farmaco_casa": "furosemida", "dose_oral_dia": 96, "estrategia": "alta", "modo": "continua"})
    assert r["total_iv_furosemida_mg_dia"] == 240.0
    assert r["infusao_mg_h"] == 10.0


def test_avisa_quando_equivalente_fora_da_populacao_80_240():
    baixo = _calc().compute({"farmaco_casa": "furosemida", "dose_oral_dia": 40, "estrategia": "alta", "modo": "bolus_q12"})
    alto = _calc().compute({"farmaco_casa": "furosemida", "dose_oral_dia": 300, "estrategia": "baixa", "modo": "bolus_q12"})
    assert baixo["dentro_populacao_dose_trial"] is False
    assert alto["dentro_populacao_dose_trial"] is False
