"""Testes das calculadoras ACLS 2025 produzidas pelo ChatGPT.

Fonte: ChatGPT.
"""

from app.services.dose_calculators_acls2025_chatgpt import ACLS_2025_DOSE_REGISTRY


def test_pcr_adulto_epinefrina_e_amiodarona_doses_fixas():
    c = ACLS_2025_DOSE_REGISTRY["acls-pcr-adulto-doses-fixas-2025"]
    epi = c.compute({"terapia": "epinefrina"})
    assert epi["dose"] == "1 mg IV/IO"
    assert epi["intervalo"] == "a cada 3-5 min"

    amio1 = c.compute({"terapia": "amiodarona_1"})
    amio2 = c.compute({"terapia": "amiodarona_2"})
    assert amio1["dose"] == "300 mg IV/IO em bolus"
    assert amio2["dose"] == "150 mg IV/IO em bolus"


def test_lidocaina_pcr_adulto_calcula_faixas_por_peso():
    c = ACLS_2025_DOSE_REGISTRY["lidocaina-pcr-adulto-2025"]
    primeira = c.compute({"peso": 80, "etapa": "primeira"})
    segunda = c.compute({"peso": 80, "etapa": "segunda"})
    assert primeira["dose_min_mg"] == 80.0
    assert primeira["dose_max_mg"] == 120.0
    assert segunda["dose_min_mg"] == 40.0
    assert segunda["dose_max_mg"] == 60.0


def test_adenosina_adulto_primeira_6_segunda_12():
    c = ACLS_2025_DOSE_REGISTRY["adenosina-tsv-adulto-2025"]
    assert c.compute({"etapa": "primeira"})["dose_mg"] == 6
    assert c.compute({"etapa": "segunda"})["dose_mg"] == 12


def test_atropina_adulto_respeita_teto_total_3mg():
    c = ACLS_2025_DOSE_REGISTRY["atropina-bradicardia-adulto-2025"]
    r = c.compute({"doses_previas": 2})
    assert r["proxima_dose_mg"] == 1.0
    assert r["total_apos_mg"] == 3.0

    teto = c.compute({"doses_previas": 3})
    assert teto["proxima_dose_mg"] == 0.0
    assert teto["total_apos_mg"] == 3.0


def test_dopamina_bradicardia_conversao_para_ml_h():
    c = ACLS_2025_DOSE_REGISTRY["dopamina-bradicardia-adulto-infusao-2025"]
    r = c.compute({"peso": 70, "dose_alvo": 10, "quantidade_mg": 400, "volume_ml": 250})
    assert r["ml_h"] == 26.25
    assert r["fora_da_faixa"] is False


def test_epinefrina_bradicardia_dose_fixa_nao_usa_peso():
    c = ACLS_2025_DOSE_REGISTRY["epinefrina-bradicardia-adulto-infusao-2025"]
    r = c.compute({"dose_alvo": 5, "quantidade_mg": 4, "volume_ml": 250})
    assert r["ml_h"] == 18.75
    assert r["fora_da_faixa"] is False


def test_procainamida_calcula_teto_17mgkg_e_tempo():
    c = ACLS_2025_DOSE_REGISTRY["procainamida-tv-estavel-adulto-2025"]
    r = c.compute({"peso": 70, "taxa_mg_min": 50})
    assert r["dose_maxima_17mg_kg_mg"] == 1190.0
    assert r["tempo_ate_dose_maxima_min"] == 23.8
    assert r["fora_da_faixa"] is False


def test_controle_frequencia_fa_diltiazem_por_peso():
    c = ACLS_2025_DOSE_REGISTRY["controle-frequencia-fa-flutter-agudo-adulto-2025"]
    r = c.compute({
        "peso": 80,
        "farmaco": "diltiazem",
        "instavel": False,
        "preexcitacao": False,
        "ic_sistolica_descompensada": False,
    })
    assert r["bolus_mg"] == 20.0
    assert r["infusao"] == "5-10 mg/h"


def test_controle_frequencia_fa_bloqueia_instabilidade_e_preexcitacao():
    c = ACLS_2025_DOSE_REGISTRY["controle-frequencia-fa-flutter-agudo-adulto-2025"]
    base = {
        "peso": 80,
        "farmaco": "metoprolol",
        "ic_sistolica_descompensada": False,
    }
    instavel = c.compute({**base, "instavel": True, "preexcitacao": False})
    assert instavel["conduta"] == "cardioversao_eletrica_imediata"

    preexc = c.compute({**base, "instavel": False, "preexcitacao": True})
    assert preexc["conduta"] == "nao_usar_bloqueadores_nodais_ou_amiodarona_iv"


def test_controle_frequencia_fa_bloqueia_ccb_beta_em_ic_descompensada():
    c = ACLS_2025_DOSE_REGISTRY["controle-frequencia-fa-flutter-agudo-adulto-2025"]
    r = c.compute({
        "peso": 80,
        "farmaco": "diltiazem",
        "instavel": False,
        "preexcitacao": False,
        "ic_sistolica_descompensada": True,
    })
    assert r["conduta"] == "farmaco_selecionado_nao_recomendado"
