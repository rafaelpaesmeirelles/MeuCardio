"""Testes das doses vasoativas no choque cardiogênico ACC 2025.

Fonte: ChatGPT.
"""

from app.services.dose_calculators_choque_cardiogenico2025_chatgpt import CHOQUE_CARDIOGENICO_2025_DOSE_REGISTRY


def _calc():
    return CHOQUE_CARDIOGENICO_2025_DOSE_REGISTRY["vasoativos-choque-cardiogenico-acc-2025"]


def test_norepinefrina_01_mcgkgmin_em_4mg_250ml():
    r = _calc().compute({
        "agente": "norepinefrina", "peso": 70, "dose_alvo": 0.1,
        "quantidade_soluto": 4, "volume_ml": 250,
        "hipotensao": True, "piora_renal": False,
    })
    assert r["ml_h"] == 26.25
    assert r["fora_da_faixa"] is False
    assert any("escolha inicial" in x for x in r["alertas"])


def test_dobutamina_10_e_limite_superior_acc_2025():
    r = _calc().compute({
        "agente": "dobutamina", "peso": 80, "dose_alvo": 10,
        "quantidade_soluto": 250, "volume_ml": 250,
        "hipotensao": False, "piora_renal": False,
    })
    assert r["faixa_acc_2025"] == "2.0-10.0 mcg/kg/min"
    assert r["fora_da_faixa"] is False

    alto = _calc().compute({
        "agente": "dobutamina", "peso": 80, "dose_alvo": 12,
        "quantidade_soluto": 250, "volume_ml": 250,
        "hipotensao": False, "piora_renal": False,
    })
    assert alto["fora_da_faixa"] is True


def test_milrinona_piora_renal_emite_alerta():
    r = _calc().compute({
        "agente": "milrinona", "peso": 70, "dose_alvo": 0.25,
        "quantidade_soluto": 20, "volume_ml": 100,
        "hipotensao": False, "piora_renal": True,
    })
    assert any("eliminação renal" in x for x in r["alertas"])


def test_vasopressina_usa_unidades_e_nao_peso():
    r = _calc().compute({
        "agente": "vasopressina", "peso": 70, "dose_alvo": 0.03,
        "quantidade_soluto": 20, "volume_ml": 100,
        "hipotensao": True, "piora_renal": False,
    })
    assert r["unidade_dose"] == "U/min"
    assert r["ml_h"] == 9.0


def test_nitroglicerina_50_mcgmin_em_50mg_250ml():
    r = _calc().compute({
        "agente": "nitroglicerina", "peso": 70, "dose_alvo": 50,
        "quantidade_soluto": 50, "volume_ml": 250,
        "hipotensao": False, "piora_renal": False,
    })
    assert r["ml_h"] == 15.0


def test_fenilefrina_emite_alerta_de_nao_primeira_linha_isolada():
    r = _calc().compute({
        "agente": "fenilefrina", "peso": 70, "dose_alvo": 1,
        "quantidade_soluto": 10, "volume_ml": 100,
        "hipotensao": True, "piora_renal": False,
    })
    assert any("desencoraja fortemente" in x for x in r["alertas"])
