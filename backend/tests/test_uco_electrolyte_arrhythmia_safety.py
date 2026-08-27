import pytest

from app.services.intensive_care_electrolyte_safety import (
    INTENSIVE_CARE_ELECTROLYTE_SAFETY_REGISTRY,
)


CALC = INTENSIVE_CARE_ELECTROLYTE_SAFETY_REGISTRY["seguranca-eletrolitica-arritmica-uco"]


def base(**overrides):
    data = {
        "potassio_mmol_l": 4.0,
        "alteracao_ecg_compativel": False,
        "ectopia_complexa_ou_tvns": False,
        "tv_polimorfica_sustentada": False,
        "sintoma_neuromuscular_grave": False,
        "hipomagnesemia_documentada": False,
        "bradicardia_ou_pausas": False,
        "farmaco_prolonga_qt": False,
        "uso_ou_toxicidade_digoxina_suspeita": False,
        "isquemia_aguda_suspeita": False,
        "lra_ou_disfuncao_renal_relevante": False,
        "oliguria": False,
        "perdas_ou_shift_em_curso": False,
    }
    data.update(overrides)
    return data


def test_k_2_5_ou_menor_e_critico_sem_calcular_reposicao():
    result = CALC.compute(base(potassio_mmol_l=2.4))
    assert result["risco"] == "critico"
    assert result["hipocalemia_grave"] is True
    assert "não calcula dose, via ou velocidade" in result["prioridade"]


def test_ecg_alterado_torna_hipocalemia_prioridade_critica_mesmo_acima_2_5():
    result = CALC.compute(base(potassio_mmol_l=3.1, alteracao_ecg_compativel=True))
    assert result["risco"] == "critico"
    assert "alterações eletrocardiográficas compatíveis" in result["gatilhos"]


def test_tv_polimorfica_sustentada_nunca_espera_correcao_eletrolitica():
    result = CALC.compute(base(potassio_mmol_l=2.8, tv_polimorfica_sustentada=True))
    assert result["risco"] == "emergencia_eletrica"
    assert "choque não sincronizado imediato" in result["prioridade"]
    assert "não deve atrasar desfibrilação" in result["prioridade"]
    assert result["proximo_fluxo"] == "torsades-qt-longo-magnesio-uco"


def test_hipocalemia_com_qtc_alto_ou_hipomagnesemia_amplifica_risco():
    result = CALC.compute(base(
        potassio_mmol_l=3.2,
        qtc_ms=520,
        hipomagnesemia_documentada=True,
    ))
    assert result["risco"] == "prioritario"
    assert result["qtc_alto_risco"] is True
    assert "hipomagnesemia" in result["fenotipo"]
    assert "hipocalemia refratária" in result["papel_do_magnesio"]


def test_funcao_renal_aumenta_cautela_sem_rebaixar_emergencia():
    result = CALC.compute(base(
        potassio_mmol_l=2.2,
        lra_ou_disfuncao_renal_relevante=True,
        oliguria=True,
    ))
    assert result["risco"] == "critico"
    assert "não reduz a urgência" in result["funcao_renal"]
    assert "sobrecorreção" in result["funcao_renal"]


def test_k_normal_nao_neutraliza_qt_alto_ou_hipomagnesemia():
    result = CALC.compute(base(
        potassio_mmol_l=4.1,
        qtc_ms=530,
        hipomagnesemia_documentada=True,
    ))
    assert result["risco"] == "risco_arrtimico_sem_hipocalemia"
    assert "não declarar segurança apenas pelo K" in result["prioridade"]


def test_perdas_em_curso_exigem_tendencia_seriada():
    result = CALC.compute(base(potassio_mmol_l=3.3, perdas_ou_shift_em_curso=True))
    assert "valor isolado não encerra o risco" in result["monitorizacao"]


def test_hipercalemia_redireciona_sem_extrapolar_regras():
    result = CALC.compute(base(potassio_mmol_l=6.2))
    assert result["risco"] == "fora_do_escopo"
    assert result["proximo_fluxo"] == "hipercalemia-seguranca-uco"
    assert "não extrapole" in result["prioridade"]


def test_rejeita_valores_nao_finitos_e_fora_da_faixa():
    with pytest.raises(ValueError):
        CALC.compute(base(potassio_mmol_l=float("nan")))
    with pytest.raises(ValueError):
        CALC.compute(base(potassio_mmol_l=0.4))
    with pytest.raises(ValueError):
        CALC.compute(base(qtc_ms=900))


def test_limitacoes_nao_embutem_posologia_ou_parametro_eletrico():
    text = " ".join(CALC.limitations).casefold()
    for forbidden in ("meq/h", "mmol/h", "mg/kg", "joule", "j/kg", "bpm de pacing"):
        assert forbidden not in text
