"""Testes das doses de antiagregantes orais na SCA 2025.

Fonte: ChatGPT.
"""

from app.services.dose_calculators_antiagregantes_sca2025_chatgpt import ANTIAGREGANTES_SCA_2025_DOSE_REGISTRY


def _calc():
    return ANTIAGREGANTES_SCA_2025_DOSE_REGISTRY["antiagregante-oral-sca-acc-aha-2025"]


def test_aas_carga_e_manutencao():
    r = _calc().compute({"farmaco": "aas", "fibrinolise": False, "pci": False, "idade": 60, "peso": 80})
    assert r["carga"] == "162-325 mg VO"
    assert r["manutencao"] == "75-100 mg VO 1x/dia"


def test_clopidogrel_sem_fibrinolise():
    r = _calc().compute({"farmaco": "clopidogrel", "fibrinolise": False, "pci": True, "idade": 60, "peso": 80})
    assert r["carga"] == "300 ou 600 mg VO"
    assert r["manutencao"] == "75 mg VO 1x/dia"


def test_clopidogrel_fibrinolise_menor_75_300mg():
    r = _calc().compute({"farmaco": "clopidogrel", "fibrinolise": True, "pci": False, "idade": 74, "peso": 80})
    assert r["carga"] == "300 mg VO"


def test_clopidogrel_fibrinolise_maior_75_sem_carga():
    r = _calc().compute({"farmaco": "clopidogrel", "fibrinolise": True, "pci": False, "idade": 76, "peso": 80})
    assert r["carga"] == "sem dose de ataque; dose inicial 75 mg VO"


def test_clopidogrel_fibrinolise_exatos_75_retorna_verificacao_humana():
    r = _calc().compute({"farmaco": "clopidogrel", "fibrinolise": True, "pci": False, "idade": 75, "peso": 80})
    assert r["conduta"] == "VERIFICAÇÃO HUMANA NECESSÁRIA"
    assert "discrepante" in r["motivo"]


def test_prasugrel_pci_10mg_se_jovem_e_60kg_ou_mais():
    r = _calc().compute({"farmaco": "prasugrel", "fibrinolise": False, "pci": True, "idade": 60, "peso": 80})
    assert r["carga"] == "60 mg VO"
    assert r["manutencao"] == "10 mg VO 1x/dia"


def test_prasugrel_reduz_para_5mg_se_peso_menor_60_ou_idade_75_mais():
    r_peso = _calc().compute({"farmaco": "prasugrel", "fibrinolise": False, "pci": True, "idade": 60, "peso": 59})
    r_idade = _calc().compute({"farmaco": "prasugrel", "fibrinolise": False, "pci": True, "idade": 75, "peso": 80})
    assert r_peso["manutencao"] == "5 mg VO 1x/dia"
    assert r_idade["manutencao"] == "5 mg VO 1x/dia"


def test_prasugrel_bloqueia_se_nao_pci_ou_fibrinolise_imediata():
    sem_pci = _calc().compute({"farmaco": "prasugrel", "fibrinolise": False, "pci": False, "idade": 60, "peso": 80})
    com_litico = _calc().compute({"farmaco": "prasugrel", "fibrinolise": True, "pci": True, "idade": 60, "peso": 80})
    assert sem_pci["conduta"] == "requer_pci_no_cenario_da_tabela"
    assert com_litico["conduta"] == "nao_modelado_como_carga_imediata_pos_fibrinolitico"


def test_ticagrelor_sem_fibrinolise_180_90_bid():
    r = _calc().compute({"farmaco": "ticagrelor", "fibrinolise": False, "pci": True, "idade": 60, "peso": 80})
    assert r["carga"] == "180 mg VO"
    assert r["manutencao"] == "90 mg VO 2x/dia"
    assert "<=100" in r["aas_manutencao"]
