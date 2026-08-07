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


def test_dasi_34_e_ruim_34_25_e_acima_do_corte():
    c = PERIOPERATIVE_REGISTRY["dasi"]

    # 8 + 8 + 7.5 + 5.5 + 5 = impossível porque não existe item 5;
    # usa combinação exata 34,00: 8 + 8 + 7,5 + 5,5 + 3,5 + 1,5 não existe.
    # Em vez de fabricar combinação, valida o comportamento do ponto de decisão
    # diretamente pela função de interpretação com resultados controlados.
    assert "capacidade funcional ruim" in c.interpret({"score": 34, "max": 58.2})
    assert "acima do ponto de decisão" in c.interpret({"score": 34.01, "max": 58.2})


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
