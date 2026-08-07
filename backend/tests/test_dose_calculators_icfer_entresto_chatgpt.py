"""Testes das calculadoras de ICFER/Entresto produzidas pelo ChatGPT.

Fonte: ChatGPT.
"""

from app.services.dose_calculators_entresto_brasil_chatgpt import ENTRESTO_BRASIL_DOSE_REGISTRY
from app.services.dose_calculators_icfer_chatgpt import ICFER_DOSE_REGISTRY


def test_tabela_icfer_carvedilol_metoprolol_mra_sglt2():
    c = ICFER_DOSE_REGISTRY["icfer-doses-iniciais-e-alvo-aha-2022"]
    carvedilol = c.compute({"farmaco": "carvedilol"})
    metoprolol = c.compute({"farmaco": "metoprolol_succinato"})
    esp = c.compute({"farmaco": "espironolactona"})
    dapa = c.compute({"farmaco": "dapagliflozina"})
    assert carvedilol["dose_inicial"] == "3,125 mg VO 2x/dia"
    assert carvedilol["dose_alvo"] == "25-50 mg VO 2x/dia"
    assert metoprolol["dose_alvo"] == "200 mg VO 1x/dia"
    assert esp["dose_alvo"] == "25-50 mg VO 1x/dia"
    assert dapa["dose_inicial"] == dapa["dose_alvo"] == "10 mg VO 1x/dia"


def _entresto_base(**extra):
    d = {
        "terapia_sraa": "bra",
        "horas_desde_ieca": 0,
        "tfge": 70,
        "potassio": 4.5,
        "pas": 120,
        "child_pugh": "normal",
        "doenca_renal_terminal": False,
    }
    d.update(extra)
    return d


def test_entresto_inicio_padrao_100_bid_e_alvo_200_bid():
    c = ENTRESTO_BRASIL_DOSE_REGISTRY["entresto-dose-inicial-bula-brasil-2025"]
    r = c.compute(_entresto_base())
    assert r["dose_inicial"] == "100 mg VO 2x/dia"
    assert r["dose_alvo"] == "200 mg VO 2x/dia"
    assert r["suspender_bra_concomitante"] is True


def test_entresto_sem_ieca_bra_inicia_50_bid():
    c = ENTRESTO_BRASIL_DOSE_REGISTRY["entresto-dose-inicial-bula-brasil-2025"]
    r = c.compute(_entresto_base(terapia_sraa="nenhum"))
    assert r["dose_inicial"] == "50 mg VO 2x/dia"
    assert any("não está usando" in x for x in r["fatores_para_inicio_50mg"])


def test_entresto_ieca_baixa_dose_ainda_exige_36h():
    c = ENTRESTO_BRASIL_DOSE_REGISTRY["entresto-dose-inicial-bula-brasil-2025"]
    r = c.compute(_entresto_base(terapia_sraa="ieca_baixa_dose", horas_desde_ieca=24))
    assert r["conduta"] == "aguardar_washout_ieca"
    assert r["horas_restantes"] == 12


def test_entresto_ieca_36h_libera_e_baixa_dose_puxa_inicio_50():
    c = ENTRESTO_BRASIL_DOSE_REGISTRY["entresto-dose-inicial-bula-brasil-2025"]
    r = c.compute(_entresto_base(terapia_sraa="ieca_baixa_dose", horas_desde_ieca=36))
    assert r["dose_inicial"] == "50 mg VO 2x/dia"


def test_entresto_tfge_moderada_grave_e_pas_100_110_puxam_50_bid():
    c = ENTRESTO_BRASIL_DOSE_REGISTRY["entresto-dose-inicial-bula-brasil-2025"]
    renal = c.compute(_entresto_base(tfge=45))
    renal_grave = c.compute(_entresto_base(tfge=25))
    pa = c.compute(_entresto_base(pas=105))
    assert renal["dose_inicial"] == "50 mg VO 2x/dia"
    assert renal_grave["dose_inicial"] == "50 mg VO 2x/dia"
    assert renal_grave["tfge_grave_menor_30"] is True
    assert pa["dose_inicial"] == "50 mg VO 2x/dia"


def test_entresto_child_pugh_b_50_e_c_contraindicado():
    c = ENTRESTO_BRASIL_DOSE_REGISTRY["entresto-dose-inicial-bula-brasil-2025"]
    b = c.compute(_entresto_base(child_pugh="B"))
    cc = c.compute(_entresto_base(child_pugh="C"))
    assert b["dose_inicial"] == "50 mg VO 2x/dia"
    assert cc["conduta"] == "contraindicado"


def test_entresto_bloqueia_pas_menor100_e_k_maior54():
    c = ENTRESTO_BRASIL_DOSE_REGISTRY["entresto-dose-inicial-bula-brasil-2025"]
    hipot = c.compute(_entresto_base(pas=99))
    hiperK = c.compute(_entresto_base(potassio=5.5))
    assert hipot["conduta"] == "nao_iniciar"
    assert "PAS" in hipot["motivo"]
    assert hiperK["conduta"] == "nao_iniciar"
    assert "5,4" in hiperK["motivo"]


def test_entresto_drc_terminal_nao_recomendado():
    c = ENTRESTO_BRASIL_DOSE_REGISTRY["entresto-dose-inicial-bula-brasil-2025"]
    r = c.compute(_entresto_base(doenca_renal_terminal=True))
    assert r["conduta"] == "nao_recomendado"
