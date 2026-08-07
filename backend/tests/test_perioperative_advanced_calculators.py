import pytest

from app.services.perioperative_calculators_geriatria import _gscri
from app.services.perioperative_calculators_mortalidade import _smpm
from app.services.perioperative_calculators_sort import _sort


def test_gscri_referencia_minima():
    r = _gscri({
        "idade": 65,
        "avc_previo": False,
        "asa": 1,
        "tipo_procedimento": "hernia",
        "status_funcional": "independente",
        "creatinina_maior_1_5": False,
        "insuficiencia_cardiaca": False,
        "diabetes": "nao",
    })
    assert r["risco_pct"] == pytest.approx(0.11, abs=0.01)
    assert r["idade_minima_validacao"] == 65


def test_gscri_rejeita_menor_65():
    with pytest.raises(ValueError, match="≥65"):
        _gscri({
            "idade": 64,
            "avc_previo": False,
            "asa": 1,
            "tipo_procedimento": "hernia",
            "status_funcional": "independente",
            "creatinina_maior_1_5": False,
            "insuficiencia_cardiaca": False,
            "diabetes": "nao",
        })


def test_gscri_cenario_multiplos_fatores():
    r = _gscri({
        "idade": 80,
        "avc_previo": True,
        "asa": 5,
        "tipo_procedimento": "veias",
        "status_funcional": "totalmente_dependente",
        "creatinina_maior_1_5": True,
        "insuficiencia_cardiaca": True,
        "diabetes": "com_insulina",
    })
    # x = -6.79 + 2.08 + 3.63 + 1.35 + 0.72 + 0.57 + 0.60 + 0.47 = 2.63
    assert r["risco_pct"] == pytest.approx(93.28, abs=0.01)


def test_sort_referencia_minima():
    r = _sort({
        "idade": 40,
        "asa": 1,
        "urgencia": "eletiva",
        "especialidade_alto_risco": False,
        "xmajor_complexa": False,
        "cancer": False,
    })
    assert r["risco_pct"] == pytest.approx(0.06, abs=0.01)


def test_sort_cenario_com_coeficientes_publicados():
    r = _sort({
        "idade": 70,
        "asa": 3,
        "urgencia": "urgente",
        "especialidade_alto_risco": True,
        "xmajor_complexa": True,
        "cancer": True,
    })
    # x = -7.366 + 1.411 + 1.657 + 0.712 + 0.381 + 0.667 + 0.777 = -1.761
    assert r["risco_pct"] == pytest.approx(14.67, abs=0.01)


def test_smpm_classes_originais():
    assert _smpm({"asa": 1, "risco_procedimento": "baixo", "emergencia": False}) == {
        "score": 0, "max": 9, "classe": "I", "mortalidade_30d": "<0,5%", "endpoint": "mortalidade por todas as causas em 30 dias"
    }
    r2 = _smpm({"asa": 3, "risco_procedimento": "intermediario", "emergencia": True})
    assert r2["score"] == 6 and r2["classe"] == "II" and r2["mortalidade_30d"] == "1,5–4,0%"
    r3 = _smpm({"asa": 5, "risco_procedimento": "alto", "emergencia": True})
    assert r3["score"] == 9 and r3["classe"] == "III" and r3["mortalidade_30d"] == ">10%"
