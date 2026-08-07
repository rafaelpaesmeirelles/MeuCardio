"""Testes da FRAIL Scale adicionada ao módulo perioperatório.

Fonte: ChatGPT.
"""

from app.services.perioperative_calculators_frailty import FRAILTY_PERIOPERATIVE_REGISTRY


def test_frail_zero_robusto():
    c = FRAILTY_PERIOPERATIVE_REGISTRY["frail-scale-perioperatorio"]
    payload = {f.name: False for f in c.fields}
    r = c.compute(payload)
    assert r == {"score": 0, "max": 5, "categoria": "robusto"}


def test_frail_um_dois_pre_fragil():
    c = FRAILTY_PERIOPERATIVE_REGISTRY["frail-scale-perioperatorio"]
    payload = {f.name: False for f in c.fields}
    payload["fadiga"] = True
    assert c.compute(payload)["categoria"] == "pre_fragil"
    payload["resistencia"] = True
    assert c.compute(payload)["score"] == 2
    assert c.compute(payload)["categoria"] == "pre_fragil"


def test_frail_tres_a_cinco_fragil():
    c = FRAILTY_PERIOPERATIVE_REGISTRY["frail-scale-perioperatorio"]
    payload = {f.name: False for f in c.fields}
    for key in ("fadiga", "resistencia", "deambulacao"):
        payload[key] = True
    assert c.compute(payload)["score"] == 3
    assert c.compute(payload)["categoria"] == "fragil"
    payload["cinco_ou_mais_doencas"] = True
    payload["perda_peso_5pct"] = True
    assert c.compute(payload)["score"] == 5
    assert c.compute(payload)["categoria"] == "fragil"
