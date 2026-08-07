"""Testes das calculadoras de enoxaparina na SCA/ICP.

Fonte: ChatGPT.
"""

from app.services.dose_calculators_enoxaparina_sca_chatgpt import ENOXAPARINA_SCA_DOSE_REGISTRY


def test_nstemi_1mgkg_12h_e_24h_se_clcr_menor_30():
    c = ENOXAPARINA_SCA_DOSE_REGISTRY["enoxaparina-sca-idade-renal-bula-brasil"]
    normal = c.compute({"indicacao": "ua_nstemi", "idade": 65, "peso": 80, "clcr": 60})
    renal = c.compute({"indicacao": "ua_nstemi", "idade": 65, "peso": 80, "clcr": 29})
    assert normal["dose_sc_mg"] == 80.0
    assert normal["intervalo"] == "a cada 12 h"
    assert renal["dose_sc_mg"] == 80.0
    assert renal["intervalo"] == "a cada 24 h"


def test_stemi_menor_75_funcao_renal_preservada_bolus_e_teto_100():
    c = ENOXAPARINA_SCA_DOSE_REGISTRY["enoxaparina-sca-idade-renal-bula-brasil"]
    r = c.compute({"indicacao": "stemi", "idade": 74, "peso": 120, "clcr": 60})
    assert r["bolus_iv_mg"] == 30.0
    assert r["dose_sc_inicial_mg"] == 100.0
    assert r["intervalo"] == "a cada 12 h"


def test_stemi_menor_75_clcr_menor_30_muda_para_24h_mantendo_bolus():
    c = ENOXAPARINA_SCA_DOSE_REGISTRY["enoxaparina-sca-idade-renal-bula-brasil"]
    r = c.compute({"indicacao": "stemi", "idade": 74, "peso": 90, "clcr": 20})
    assert r["bolus_iv_mg"] == 30.0
    assert r["dose_sc_inicial_mg"] == 90.0
    assert r["intervalo"] == "a cada 24 h"


def test_stemi_75_ou_mais_sem_bolus_e_075mgkg_com_teto75():
    c = ENOXAPARINA_SCA_DOSE_REGISTRY["enoxaparina-sca-idade-renal-bula-brasil"]
    r = c.compute({"indicacao": "stemi", "idade": 75, "peso": 120, "clcr": 60})
    assert r["bolus_iv_mg"] == 0
    assert r["dose_sc_inicial_mg"] == 75.0
    assert r["intervalo"] == "a cada 12 h"


def test_stemi_75_ou_mais_e_clcr_menor30_1mgkg_24h_sem_bolus_teto100():
    c = ENOXAPARINA_SCA_DOSE_REGISTRY["enoxaparina-sca-idade-renal-bula-brasil"]
    r = c.compute({"indicacao": "stemi", "idade": 80, "peso": 120, "clcr": 20})
    assert r["bolus_iv_mg"] == 0
    assert r["dose_sc_inicial_mg"] == 100.0
    assert r["intervalo"] == "a cada 24 h"


def test_pci_menos_8h_sem_dose_adicional_mais_8h_03mgkg():
    c = ENOXAPARINA_SCA_DOSE_REGISTRY["enoxaparina-stemi-dose-adicional-icp"]
    sem = c.compute({"peso": 80, "horas_desde_ultima_sc": 7.9})
    com = c.compute({"peso": 80, "horas_desde_ultima_sc": 8.1})
    assert sem["conduta"] == "sem_dose_adicional"
    assert com["conduta"] == "bolus_iv_adicional"
    assert com["dose_mg"] == 24.0


def test_pci_exatamente_8h_nao_inventa_regra():
    c = ENOXAPARINA_SCA_DOSE_REGISTRY["enoxaparina-stemi-dose-adicional-icp"]
    r = c.compute({"peso": 80, "horas_desde_ultima_sc": 8.0})
    assert r["conduta"] == "VERIFICAÇÃO HUMANA NECESSÁRIA"
