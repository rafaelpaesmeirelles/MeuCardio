"""Testes das calculadoras de fibrinolíticos no STEMI.

Fonte: ChatGPT.
"""

from app.services.dose_calculators_fibrinoliticos_stemi_chatgpt import FIBRINOLITICOS_STEMI_DOSE_REGISTRY


def test_tenecteplase_faixas_nominais_bula():
    c = FIBRINOLITICOS_STEMI_DOSE_REGISTRY["tenecteplase-stemi-peso-idoso"]
    casos = [
        (59.9, 30.0, 6.0),
        (60, 35.0, 7.0),
        (70, 40.0, 8.0),
        (80, 45.0, 9.0),
        (90, 50.0, 10.0),
    ]
    for peso, dose, volume in casos:
        r = c.compute({"peso": peso, "idade": 60, "usar_meia_dose_idoso": False})
        assert r["dose_nominal_bula_mg"] == dose
        assert r["volume_nominal_bula_ml"] == volume
        assert r["dose_a_administrar_mg"] == dose


def test_tenecteplase_meia_dose_idoso_explicitamente_selecionada():
    c = FIBRINOLITICOS_STEMI_DOSE_REGISTRY["tenecteplase-stemi-peso-idoso"]
    r = c.compute({"peso": 85, "idade": 80, "usar_meia_dose_idoso": True})
    assert r["dose_nominal_bula_mg"] == 45.0
    assert r["dose_a_administrar_mg"] == 22.5
    assert r["volume_a_administrar_ml"] == 4.5
    assert r["meia_dose_selecionada"] is True


def test_tenecteplase_nao_permite_meia_dose_idoso_em_menor_75():
    c = FIBRINOLITICOS_STEMI_DOSE_REGISTRY["tenecteplase-stemi-peso-idoso"]
    try:
        c.compute({"peso": 85, "idade": 74, "usar_meia_dose_idoso": True})
    except ValueError as exc:
        assert "<75" in str(exc)
    else:
        raise AssertionError("Deveria bloquear meia-dose de idoso em paciente <75 anos")


def test_tenecteplase_75_anos_sinaliza_stream_sem_reduzir_automaticamente():
    c = FIBRINOLITICOS_STEMI_DOSE_REGISTRY["tenecteplase-stemi-peso-idoso"]
    r = c.compute({"peso": 75, "idade": 75, "usar_meia_dose_idoso": False})
    assert r["idoso_ge_75_stream"] is True
    assert r["dose_nominal_bula_mg"] == 40.0
    assert r["dose_a_administrar_mg"] == 40.0


def test_alteplase_stemi_67kg_resulta_100mg_total():
    c = FIBRINOLITICOS_STEMI_DOSE_REGISTRY["alteplase-stemi-esquema-acelerado-90min-2025"]
    r = c.compute({"peso": 67})
    assert r["bolus_iv_mg"] == 15.0
    assert r["infusao_primeiros_30min_mg"] == 50.0
    assert r["infusao_30_a_90min_mg"] == 33.5
    assert r["dose_total_mg"] == 98.5


def test_alteplase_stemi_acima_70kg_atinge_tetos_e_100mg_total():
    c = FIBRINOLITICOS_STEMI_DOSE_REGISTRY["alteplase-stemi-esquema-acelerado-90min-2025"]
    r = c.compute({"peso": 80})
    assert r["bolus_iv_mg"] == 15.0
    assert r["infusao_primeiros_30min_mg"] == 50.0
    assert r["infusao_30_a_90min_mg"] == 35.0
    assert r["dose_total_mg"] == 100.0


def test_alteplase_stemi_60kg_peso_ajustado_90mg_total():
    c = FIBRINOLITICOS_STEMI_DOSE_REGISTRY["alteplase-stemi-esquema-acelerado-90min-2025"]
    r = c.compute({"peso": 60})
    assert r["infusao_primeiros_30min_mg"] == 45.0
    assert r["infusao_30_a_90min_mg"] == 30.0
    assert r["dose_total_mg"] == 90.0
