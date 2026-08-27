from app.services.intensive_care_perfusion import INTENSIVE_CARE_PERFUSION_REGISTRY


CALC = INTENSIVE_CARE_PERFUSION_REGISTRY["trajetoria-perfusao-lactato-uco"]


def test_lactato_isolado_nao_define_choque():
    result = CALC.compute({
        "lactato_atual_mmol_l": 4.5,
        "hipoperfusao_clinica": False,
        "suporte_em_escalada": False,
        "oliguria_ou_lra": False,
        "catecolamina_beta": True,
        "pos_parada": False,
        "sepse_ou_choque_misto": False,
        "disfuncao_hepatica": False,
    })
    assert "SEM CONCORDÂNCIA CLÍNICA" in result["prioridade"]
    assert "beta-adrenérgico" in " ".join(result["modificadores_lactato"])


def test_lactato_normal_nao_exclui_hipoperfusao():
    result = CALC.compute({
        "lactato_atual_mmol_l": 1.4,
        "pam_mmhg": 58,
        "diurese_ml_kg_h": 0.3,
        "hipoperfusao_clinica": True,
        "suporte_em_escalada": True,
        "oliguria_ou_lra": True,
        "catecolamina_beta": False,
        "pos_parada": False,
        "sepse_ou_choque_misto": False,
        "disfuncao_hepatica": False,
    })
    assert result["fora_da_faixa"] is True
    assert "REAVALIAÇÃO PRIORITÁRIA" in result["prioridade"]


def test_trajetoria_calcula_variacao_sem_transformar_em_meta():
    result = CALC.compute({
        "lactato_atual_mmol_l": 2.0,
        "lactato_anterior_mmol_l": 4.0,
        "intervalo_horas": 6,
        "hipoperfusao_clinica": False,
        "suporte_em_escalada": False,
        "oliguria_ou_lra": False,
        "catecolamina_beta": False,
        "pos_parada": False,
        "sepse_ou_choque_misto": False,
        "disfuncao_hepatica": False,
    })
    assert result["variacao_percentual"] == 50.0
    assert "não usar como meta terapêutica isolada" in result["trajetoria"]


def test_lactato_anterior_exige_intervalo():
    try:
        CALC.compute({
            "lactato_atual_mmol_l": 3.0,
            "lactato_anterior_mmol_l": 4.0,
            "hipoperfusao_clinica": False,
            "suporte_em_escalada": False,
            "oliguria_ou_lra": False,
            "catecolamina_beta": False,
            "pos_parada": False,
            "sepse_ou_choque_misto": False,
            "disfuncao_hepatica": False,
        })
    except ValueError as exc:
        assert "informe lactato anterior e intervalo conjuntamente" in str(exc)
    else:
        raise AssertionError("deveria rejeitar trajetória sem intervalo")


def test_calculadora_permanece_nao_prescritiva():
    text = " ".join(CALC.limitations).casefold()
    assert "não seleciona" in text
    for forbidden in ("mg/kg", "mcg/kg/min", "j/kg"):
        assert forbidden not in text
