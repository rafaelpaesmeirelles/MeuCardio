"""Testes das calculadoras de DOAC por bula brasileira.

Fonte: ChatGPT.
"""

from app.services.dose_calculators_doac_brasil_chatgpt import DOAC_BRASIL_DOSE_REGISTRY


def _api_base(**extra):
    d = {
        "indicacao": "fa_nvalvular",
        "idade": 70,
        "peso": 80,
        "creatinina": 1.0,
        "clcr": 70,
        "dialise": False,
    }
    d.update(extra)
    return d


def test_apixabana_fa_dose_padrao_com_zero_ou_um_criterio():
    c = DOAC_BRASIL_DOSE_REGISTRY["apixabana-dose-bula-brasil-2025"]
    assert c.compute(_api_base())["dose"] == "5 mg VO 2x/dia"
    assert c.compute(_api_base(idade=82))["dose"] == "5 mg VO 2x/dia"


def test_apixabana_fa_reduz_com_exatamente_dois_criterios():
    c = DOAC_BRASIL_DOSE_REGISTRY["apixabana-dose-bula-brasil-2025"]
    r = c.compute(_api_base(idade=80, peso=60))
    assert r["criterios_reducao_presentes"] == 2
    assert r["dose"] == "2,5 mg VO 2x/dia"


def test_apixabana_fa_reduz_com_creatinina_e_idade():
    c = DOAC_BRASIL_DOSE_REGISTRY["apixabana-dose-bula-brasil-2025"]
    r = c.compute(_api_base(idade=80, creatinina=1.5))
    assert r["dose"] == "2,5 mg VO 2x/dia"


def test_apixabana_tev_fases_e_prevencao_recorrencia():
    c = DOAC_BRASIL_DOSE_REGISTRY["apixabana-dose-bula-brasil-2025"]
    assert c.compute(_api_base(indicacao="tev_dias_1_7"))["dose"] == "10 mg VO 2x/dia"
    assert c.compute(_api_base(indicacao="tev_dia_8_em_diante"))["dose"] == "5 mg VO 2x/dia"
    assert c.compute(_api_base(indicacao="prevencao_recorrencia_apos_6m"))["dose"] == "2,5 mg VO 2x/dia"


def test_apixabana_clcr_15_29_mantem_esquema_com_cautela_e_abaixo_15_bloqueia():
    c = DOAC_BRASIL_DOSE_REGISTRY["apixabana-dose-bula-brasil-2025"]
    r = c.compute(_api_base(indicacao="tev_dias_1_7", clcr=15))
    assert r["dose"] == "10 mg VO 2x/dia"
    assert r["cautela_clcr_15_29"] is True

    bloqueio = c.compute(_api_base(clcr=14.9))
    assert bloqueio["conduta"] == "nao_recomendada_pela_bula_brasileira"


def test_apixabana_dialise_bloqueia_conforme_bula_brasileira():
    c = DOAC_BRASIL_DOSE_REGISTRY["apixabana-dose-bula-brasil-2025"]
    r = c.compute(_api_base(dialise=True))
    assert r["conduta"] == "nao_recomendada_pela_bula_brasileira"


def test_rivaroxabana_fa_corte_clcr_50():
    c = DOAC_BRASIL_DOSE_REGISTRY["rivaroxabana-dose-bula-brasil-2025"]
    r50 = c.compute({"indicacao": "fa_nvalvular", "clcr": 50, "risco_sangramento_supera_recorrencia": False})
    r49 = c.compute({"indicacao": "fa_nvalvular", "clcr": 49.9, "risco_sangramento_supera_recorrencia": False})
    assert r50["dose"] == "20 mg VO 1x/dia com alimento"
    assert r49["dose"] == "15 mg VO 1x/dia com alimento"


def test_rivaroxabana_tev_primeiros_21_dias_independente_de_reducao_renal_acima_15():
    c = DOAC_BRASIL_DOSE_REGISTRY["rivaroxabana-dose-bula-brasil-2025"]
    r = c.compute({"indicacao": "tev_dias_1_21", "clcr": 20, "risco_sangramento_supera_recorrencia": True})
    assert r["dose"] == "15 mg VO 2x/dia com alimento"
    assert r["dose_diaria_total"] == "30 mg/dia"


def test_rivaroxabana_tev_dia22_reducao_15_nao_e_automatica():
    c = DOAC_BRASIL_DOSE_REGISTRY["rivaroxabana-dose-bula-brasil-2025"]
    padrao = c.compute({"indicacao": "tev_dia_22_em_diante", "clcr": 40, "risco_sangramento_supera_recorrencia": False})
    reduzida = c.compute({"indicacao": "tev_dia_22_em_diante", "clcr": 40, "risco_sangramento_supera_recorrencia": True})
    assert padrao["dose"] == "20 mg VO 1x/dia com alimento"
    assert reduzida["dose"].startswith("15 mg VO 1x/dia")
    assert "farmacocinético" in reduzida["nota_renal"]


def test_rivaroxabana_clcr_15_permitido_com_cautela_e_abaixo_15_bloqueado():
    c = DOAC_BRASIL_DOSE_REGISTRY["rivaroxabana-dose-bula-brasil-2025"]
    r15 = c.compute({"indicacao": "fa_nvalvular", "clcr": 15, "risco_sangramento_supera_recorrencia": False})
    assert r15["dose"] == "15 mg VO 1x/dia com alimento"
    assert r15["cautela_clcr_15_29"] is True

    r14 = c.compute({"indicacao": "fa_nvalvular", "clcr": 14.9, "risco_sangramento_supera_recorrencia": False})
    assert r14["conduta"] == "nao_recomendada_pela_bula_brasileira"
