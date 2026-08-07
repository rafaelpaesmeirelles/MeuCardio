"""Testes da anticoagulação parenteral na SCA 2025.

Fonte: ChatGPT.
"""

from app.services.dose_calculators_anticoagulacao_sca2025_chatgpt import ANTICOAGULACAO_SCA_2025_DOSE_REGISTRY


def test_hnf_inicial_aplica_tetos_4000_e_1000():
    c = ANTICOAGULACAO_SCA_2025_DOSE_REGISTRY["hnf-sca-pci-fibrinolise-acc-aha-2025"]
    r = c.compute({"peso": 100, "cenario": "terapia_inicial", "anticoagulante_previo": False})
    assert r["bolus_ui"] == 4000
    assert r["infusao_ui_h"] == 1000
    assert r["alvo_aptt"] == "60-80 s"


def test_hnf_inicial_sem_tetos_em_peso_baixo():
    c = ANTICOAGULACAO_SCA_2025_DOSE_REGISTRY["hnf-sca-pci-fibrinolise-acc-aha-2025"]
    r = c.compute({"peso": 50, "cenario": "com_fibrinolitico", "anticoagulante_previo": False})
    assert r["bolus_ui"] == 3000
    assert r["infusao_ui_h"] == 600


def test_hnf_pci_sem_anticoagulacao_previa_70_100_u_kg():
    c = ANTICOAGULACAO_SCA_2025_DOSE_REGISTRY["hnf-sca-pci-fibrinolise-acc-aha-2025"]
    r = c.compute({"peso": 80, "cenario": "pci", "anticoagulante_previo": False})
    assert r["bolus_min_ui"] == 5600
    assert r["bolus_max_ui"] == 8000
    assert r["alvo_act"] == "250-300 s"


def test_hnf_pci_com_anticoagulacao_previa_nao_inventa_bolus():
    c = ANTICOAGULACAO_SCA_2025_DOSE_REGISTRY["hnf-sca-pci-fibrinolise-acc-aha-2025"]
    r = c.compute({"peso": 80, "cenario": "pci", "anticoagulante_previo": True})
    assert r["conduta"] == "titular_por_act"


def test_bivalirudina_pci_normal_e_clcr_menor_30():
    c = ANTICOAGULACAO_SCA_2025_DOSE_REGISTRY["bivalirudina-pci-acc-aha-2025"]
    normal = c.compute({"peso": 80, "clcr": 60})
    renal = c.compute({"peso": 80, "clcr": 29})
    assert normal["bolus_mg"] == 60.0
    assert normal["infusao_mg_kg_h"] == 1.75
    assert normal["infusao_mg_h"] == 140.0
    assert renal["infusao_mg_kg_h"] == 1.0
    assert renal["infusao_mg_h"] == 80.0


def test_fondaparinux_inicial_e_fibrinolise():
    c = ANTICOAGULACAO_SCA_2025_DOSE_REGISTRY["fondaparinux-sca-fibrinolise-pci-2025"]
    inicial = c.compute({"cenario": "inicial", "clcr": 60})
    litico = c.compute({"cenario": "fibrinolise", "clcr": 60})
    assert inicial["dose"] == "2,5 mg SC 1x/dia"
    assert litico["inicial"] == "2,5 mg IV"
    assert "dia seguinte" in litico["depois"]


def test_fondaparinux_bloqueia_clcr_menor30_e_pci_isolada():
    c = ANTICOAGULACAO_SCA_2025_DOSE_REGISTRY["fondaparinux-sca-fibrinolise-pci-2025"]
    renal = c.compute({"cenario": "inicial", "clcr": 29})
    pci = c.compute({"cenario": "pci", "clcr": 60})
    assert renal["conduta"] == "contraindicado_neste_esquema"
    assert pci["conduta"] == "nao_usar_isoladamente_para_suporte_da_pci"
