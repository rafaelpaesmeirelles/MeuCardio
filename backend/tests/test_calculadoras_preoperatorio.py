"""RCRI e Gupta MICA — calculadoras da Avaliação Cardiológica Pré-Operatória
(pedido do Rafael, 07/08/2026). Mesma disciplina de sempre: valor esperado
conferido à mão (Lee 1999 para RCRI; dois calculadores de terceiros
convergentes para os coeficientes do Gupta MICA, ver `reference` no registro)
antes de escrever o teste, não o inverso.
"""

from app.services import calculators as calc


def test_rcri_zero_pontos_classe_i():
    r = calc.run("rcri", {})
    assert r["result"] == {"pontos": 0, "classe": "I", "evento_pct": "0,4"}


def test_rcri_um_ponto_classe_ii():
    r = calc.run("rcri", {"diabetes_em_uso_de_insulina": True})
    assert r["result"]["pontos"] == 1
    assert r["result"]["classe"] == "II"


def test_rcri_dois_pontos_classe_iii():
    r = calc.run("rcri", {"cirurgia_alto_risco": True, "cardiopatia_isquemica": True})
    assert r["result"]["classe"] == "III"


def test_rcri_tres_ou_mais_pontos_classe_iv():
    r = calc.run("rcri", {
        "cirurgia_alto_risco": True, "cardiopatia_isquemica": True,
        "insuficiencia_cardiaca_congestiva": True,
    })
    assert r["result"]["classe"] == "IV"


def test_gupta_mica_paciente_de_baixo_risco():
    # 60 anos, independente, ASA 2, creatinina normal, hérnia:
    # x = 60*0.02 + 0 + (-3.29) + 0 + 0 - 5.25 = -7.34 -> risco ~0,065%
    r = calc.run("gupta-mica", {
        "idade": 60, "status_funcional": "independente", "asa": 2,
        "creatinina_maior_1_5": False, "tipo_procedimento": "hernia",
    })
    assert 0 < r["result"]["risco_pct"] < 1
    assert r["result"]["procedimento"] == "Hérnia"


def test_gupta_mica_paciente_de_alto_risco():
    # 80 anos, totalmente dependente, ASA 4, creatinina elevada, aórtica:
    # x = 80*0.02 + 1.03 + (-0.95) + 0.61 + 1.6 - 5.25 = -1.36 -> risco ~20,4%
    r = calc.run("gupta-mica", {
        "idade": 80, "status_funcional": "totalmente_dependente", "asa": 4,
        "creatinina_maior_1_5": True, "tipo_procedimento": "aortica",
    })
    assert r["result"]["risco_pct"] == 20.42


def test_gupta_mica_cresce_com_asa_pior():
    base = {"idade": 60, "status_funcional": "independente", "creatinina_maior_1_5": False, "tipo_procedimento": "hernia"}
    r1 = calc.run("gupta-mica", {**base, "asa": 1})["result"]["risco_pct"]
    r3 = calc.run("gupta-mica", {**base, "asa": 3})["result"]["risco_pct"]
    r5 = calc.run("gupta-mica", {**base, "asa": 5})["result"]["risco_pct"]
    assert r1 < r3 < r5
