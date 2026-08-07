"""Testes das calculadoras perioperatórias produzidas pelo ChatGPT.

Os casos exercitam apenas aritmética publicada/explicitamente verificável.
Fonte: ChatGPT.
"""

from app.services.perioperative_calculators import PERIOPERATIVE_REGISTRY


def test_dasi_todas_atividades_soma_58_2():
    c = PERIOPERATIVE_REGISTRY["dasi"]
    payload = {f.name: True for f in c.fields}
    r = c.compute(payload)
    assert r["score"] == 58.2
    assert r["max"] == 58.2
    assert r["capacidade_funcional"] == "adequada_pelo_ponto_de_decisao_aha_acc_2024"


def test_dasi_zero_e_capacidade_ruim():
    c = PERIOPERATIVE_REGISTRY["dasi"]
    payload = {f.name: False for f in c.fields}
    r = c.compute(payload)
    assert r["score"] == 0
    assert r["capacidade_funcional"] == "ruim"


def test_dasi_exatamente_34_permanece_capacidade_ruim():
    c = PERIOPERATIVE_REGISTRY["dasi"]
    payload = {f.name: False for f in c.fields}
    for key in (
        "correr_curto", "trabalho_domestico_pesado", "quintal_jardim",
        "recreacao_moderada", "esporte_extenuante",
    ):
        payload[key] = True
    r = c.compute(payload)
    assert r["score"] == 34.0
    assert r["capacidade_funcional"] == "ruim"


def test_dasi_acima_de_34_muda_classificacao():
    c = PERIOPERATIVE_REGISTRY["dasi"]
    payload = {f.name: False for f in c.fields}
    for key in (
        "correr_curto", "trabalho_domestico_pesado", "quintal_jardim",
        "recreacao_moderada", "esporte_extenuante", "caminhar_casa",
    ):
        payload[key] = True
    r = c.compute(payload)
    assert r["score"] == 35.75
    assert r["capacidade_funcional"] == "adequada_pelo_ponto_de_decisao_aha_acc_2024"


def test_aub_has2_zero_um_baixo_dois_tres_intermediario_quatro_mais_alto():
    c = PERIOPERATIVE_REGISTRY["aub-has2"]
    keys = [f.name for f in c.fields]

    def calc(n: int):
        payload = {k: i < n for i, k in enumerate(keys)}
        return c.compute(payload)

    assert calc(0)["categoria"] == "baixo"
    assert calc(1)["categoria"] == "baixo"
    assert calc(2)["categoria"] == "intermediario"
    assert calc(3)["categoria"] == "intermediario"
    assert calc(4)["categoria"] == "alto"
    assert calc(6)["score"] == 6


def test_aub_has2_cada_item_vale_um_ponto():
    c = PERIOPERATIVE_REGISTRY["aub-has2"]
    for field in c.fields:
        payload = {f.name: False for f in c.fields}
        payload[field.name] = True
        assert c.compute(payload)["score"] == 1


def test_vsg_cri_pontuacao_e_classes_sbc_2024():
    c = PERIOPERATIVE_REGISTRY["vsg-cri"]
    base = {
        "idade": 50, "doenca_arterial_coronariana": False,
        "insuficiencia_cardiaca": False, "dpoc": False,
        "creatinina_maior_1_8": False, "tabagismo": False,
        "diabetes_insulina": False, "betabloqueador_cronico": False,
        "revascularizacao_coronaria_previa": False,
    }

    r_baixo = c.compute(base)
    assert r_baixo["score"] == 0
    assert r_baixo["categoria"] == "baixo"
    assert r_baixo["evento_original_pct_verificado"] is True

    intermediario = {**base, "idade": 70, "doenca_arterial_coronariana": True}
    r = c.compute(intermediario)
    assert r["score"] == 5
    assert r["categoria"] == "intermediario"
    assert r["evento_original_pct"] == 6.0
    assert r["evento_original_pct_verificado"] is False

    alto = {**base, "idade": 80, "doenca_arterial_coronariana": True, "tabagismo": True}
    r = c.compute(alto)
    assert r["score"] == 7
    assert r["categoria"] == "alto"
    assert r["evento_original_pct"] == 8.9
    assert r["evento_original_pct_verificado"] is False

    extremo_alto = {**base, "idade": 80, "doenca_arterial_coronariana": True, "insuficiencia_cardiaca": True, "dpoc": True}
    r = c.compute(extremo_alto)
    assert r["score"] >= 8
    assert r["evento_original_pct"] == 14.3
    assert r["evento_original_pct_verificado"] is True


def test_vsg_cri_revascularizacao_previa_subtrai_um_ponto():
    c = PERIOPERATIVE_REGISTRY["vsg-cri"]
    payload = {
        "idade": 60, "doenca_arterial_coronariana": True,
        "insuficiencia_cardiaca": False, "dpoc": False,
        "creatinina_maior_1_8": False, "tabagismo": False,
        "diabetes_insulina": False, "betabloqueador_cronico": False,
        "revascularizacao_coronaria_previa": True,
    }
    assert c.compute(payload)["score"] == 3


def test_sort_v1_baseline_reproduz_intercepto_original():
    c = PERIOPERATIVE_REGISTRY["sort-v1"]
    r = c.compute({
        "idade": 50,
        "asa": 1,
        "urgencia": "eletiva",
        "especialidade_alto_risco": False,
        "cirurgia_xmajor_complexa": False,
        "cancer": False,
    })
    assert r["preditor_linear"] == -7.366
    assert r["risco_mortalidade_30d_pct"] == 0.06


def test_sort_v1_soma_coeficientes_publicados():
    c = PERIOPERATIVE_REGISTRY["sort-v1"]
    r = c.compute({
        "idade": 70,
        "asa": 3,
        "urgencia": "urgente",
        "especialidade_alto_risco": True,
        "cirurgia_xmajor_complexa": True,
        "cancer": True,
    })
    # -7,366 + 1,411 + 1,657 + 0,712 + 0,381 + 0,667 + 0,777 = -1,761.
    assert r["preditor_linear"] == -1.761
    assert r["risco_mortalidade_30d_pct"] == 14.67


def test_sort_v1_asa_i_e_ii_mesmo_coeficiente_zero():
    c = PERIOPERATIVE_REGISTRY["sort-v1"]
    base = {
        "idade": 50, "urgencia": "eletiva", "especialidade_alto_risco": False,
        "cirurgia_xmajor_complexa": False, "cancer": False,
    }
    assert c.compute({**base, "asa": 1})["preditor_linear"] == c.compute({**base, "asa": 2})["preditor_linear"]
