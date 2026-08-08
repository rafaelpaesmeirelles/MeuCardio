"""Testes das calculadoras PALS 2025 produzidas pelo ChatGPT.

Fonte: ChatGPT.
"""

from app.services.dose_calculators_pals2025_chatgpt import PALS_2025_DOSE_REGISTRY


def test_epinefrina_pcr_pediatrica_001_mgkg_com_teto_1mg():
    c = PALS_2025_DOSE_REGISTRY["adrenalina-pcr-pediatrica"]
    assert c.compute({"peso": 20})["dose_mg"] == 0.2
    assert c.compute({"peso": 120})["dose_mg"] == 1.0


def test_amiodarona_pediatrica_teto_primeira_300_subsequentes_150():
    c = PALS_2025_DOSE_REGISTRY["amiodarona-pcr-pediatrica"]
    primeira = c.compute({"peso": 80, "numero_dose": 1})
    segunda = c.compute({"peso": 80, "numero_dose": 2})
    terceira = c.compute({"peso": 80, "numero_dose": 3})
    assert primeira["dose_mg"] == 300.0
    assert segunda["dose_mg"] == 150.0
    assert terceira["dose_mg"] == 150.0


def test_lidocaina_pcr_pediatrica_1mgkg():
    c = PALS_2025_DOSE_REGISTRY["lidocaina-pcr-pediatrica-2025"]
    assert c.compute({"peso": 22})["dose_mg"] == 22.0


def test_desfibrilacao_pediatrica_2_4_ate_10_jkg():
    c = PALS_2025_DOSE_REGISTRY["choque-eletrico-pediatrico"]
    r = c.compute({"peso": 15, "tipo": "desfibrilacao"})
    assert r["primeiro_j"] == 30.0
    assert r["segundo_j"] == 60.0
    assert r["subsequente_min_j"] == 60.0
    assert r["teto_peso_j"] == 150.0


def test_cardioversao_pediatrica_05_a_1_depois_2_jkg():
    c = PALS_2025_DOSE_REGISTRY["choque-eletrico-pediatrico"]
    r = c.compute({"peso": 20, "tipo": "cardioversao"})
    assert r["primeiro_min_j"] == 10.0
    assert r["primeiro_max_j"] == 20.0
    assert r["segundo_j"] == 40.0


def test_adenosina_pediatrica_tetos_6_e_12mg():
    c = PALS_2025_DOSE_REGISTRY["adenosina-tsv-pediatrica"]
    assert c.compute({"peso": 80, "numero_dose": 1})["dose_mg"] == 6.0
    assert c.compute({"peso": 80, "numero_dose": 2})["dose_mg"] == 12.0


def test_atropina_pediatrica_piso_01_e_teto_05mg():
    c = PALS_2025_DOSE_REGISTRY["atropina-bradicardia-pediatrica"]
    assert c.compute({"peso": 2})["dose_mg"] == 0.1
    assert c.compute({"peso": 40})["dose_mg"] == 0.5
