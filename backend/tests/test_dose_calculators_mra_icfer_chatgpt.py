"""Testes da calculadora de MRA na ICFER.

Fonte: ChatGPT.
"""

from app.services.dose_calculators_mra_icfer_chatgpt import MRA_ICFER_DOSE_REGISTRY


def _calc():
    return MRA_ICFER_DOSE_REGISTRY["mra-icfer-egfr-potassio-aha-2022"]


def test_mra_bloqueia_egfr_30_ou_menos():
    r30 = _calc().compute({"farmaco": "espironolactona", "egfr": 30, "potassio": 4.5})
    r20 = _calc().compute({"farmaco": "eplerenona", "egfr": 20, "potassio": 4.5})
    assert r30["conduta"] == "nao_iniciar"
    assert r20["conduta"] == "nao_iniciar"


def test_mra_bloqueia_k_5_ou_mais():
    r = _calc().compute({"farmaco": "espironolactona", "egfr": 60, "potassio": 5.0})
    assert r["conduta"] == "nao_iniciar"


def test_espironolactona_egfr_31_49_reduz_metade():
    r = _calc().compute({"farmaco": "espironolactona", "egfr": 45, "potassio": 4.5})
    assert r["dose_inicial"] == "12,5 mg VO 1x/dia"
    assert r["egfr_31_49"] is True


def test_eplerenona_egfr_31_49_expressa_metade_matematica():
    r = _calc().compute({"farmaco": "eplerenona", "egfr": 45, "potassio": 4.5})
    assert r["dose_inicial"].startswith("12,5 mg")
    assert r["egfr_31_49"] is True


def test_mra_egfr_50_ou_mais_dose_padrao():
    esp = _calc().compute({"farmaco": "espironolactona", "egfr": 50, "potassio": 4.9})
    epl = _calc().compute({"farmaco": "eplerenona", "egfr": 50, "potassio": 4.9})
    assert esp["dose_inicial"] == "25 mg VO 1x/dia"
    assert epl["dose_inicial"] == "25 mg VO 1x/dia"
