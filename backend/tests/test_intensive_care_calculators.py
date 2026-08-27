"""Testes puros da central de Cardiologia Intensiva e UCO."""

import pytest

from app.services import calculators
from app.services.intensive_care_calculators import INTENSIVE_CARE_CALCULATOR_REGISTRY


def _calc():
    return INTENSIVE_CARE_CALCULATOR_REGISTRY["ventilacao-protetora-uco"]


def _dados(**mudancas):
    dados = {
        "sexo_biologico": "masculino",
        "altura_cm": 170,
        "volume_corrente_ml": 400,
        "pressao_plato_cmh2o": 25,
        "peep_total_cmh2o": 10,
    }
    dados.update(mudancas)
    return dados


def test_homem_170_cm_calcula_peso_predito_volume_e_pressao_distensao():
    resultado = _calc().compute(_dados())

    assert resultado["peso_predito_kg"] == 66.02
    assert resultado["vt_referencia_6_ml_kg"] == 396.1
    assert resultado["faixa_vt_4_a_8_ml_kg"] == "264.1–528.1 mL"
    assert resultado["vt_atual_ml_kg"] == 6.06
    assert resultado["pressao_distensao_cmh2o"] == 15.0
    assert resultado["fora_da_faixa"] is False


def test_mulher_usa_constante_especifica_da_equacao_ardsnet():
    resultado = _calc().compute(_dados(sexo_biologico="feminino", altura_cm=160))

    assert resultado["peso_predito_kg"] == 52.42
    assert resultado["vt_referencia_6_ml_kg"] == 314.5


def test_volume_e_plato_altos_geram_alertas_sem_prescrever_peep():
    resultado = _calc().compute(
        _dados(volume_corrente_ml=700, pressao_plato_cmh2o=32, peep_total_cmh2o=12)
    )

    assert resultado["fora_da_faixa"] is True
    assert "acima de 8" in resultado["alerta_volume"]
    assert "≥30" in resultado["alerta_plato"]
    assert resultado["pressao_distensao_cmh2o"] == 20.0


def test_plato_menor_que_peep_e_rejeitada():
    with pytest.raises(ValueError, match="platô não pode ser menor"):
        _calc().compute(_dados(pressao_plato_cmh2o=8, peep_total_cmh2o=10))


def test_calculadora_esta_registrada_no_tema_exato_tudo_com_tudo():
    calculadora = calculators.REGISTRY["ventilacao-protetora-uco"]

    assert calculadora.theme == "Terapia intensiva"
    assert calculadora.status == "implementada"
    assert calculadora.kind == "dose"
