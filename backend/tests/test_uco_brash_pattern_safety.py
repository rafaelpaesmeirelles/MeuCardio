import pytest

from app.services.intensive_care_brash_safety import INTENSIVE_CARE_BRASH_SAFETY_REGISTRY


CALC = INTENSIVE_CARE_BRASH_SAFETY_REGISTRY["brash-reconhecimento-padrao-uco"]


def base(**overrides):
    data = {
        "frequencia_cardiaca_bpm": 72,
        "potassio_mmol_l": 4.3,
        "lra_ou_agudizacao_drc": False,
        "uso_bloqueador_nodal_av": False,
        "choque_ou_hipoperfusao": False,
        "dose_excessiva_ou_overdose_suspeita": False,
        "ecg_compativel_hipercalemia": False,
        "oliguria": False,
        "gatilho_agudo_desidratacao_infeccao_ou_nefrotoxico": False,
    }
    data.update(overrides)
    return data


def test_constelacao_completa_prioriza_instabilidade_sem_atrasar_manejo():
    result = CALC.compute(base(
        frequencia_cardiaca_bpm=32,
        potassio_mmol_l=5.7,
        lra_ou_agudizacao_drc=True,
        uso_bloqueador_nodal_av=True,
        choque_ou_hipoperfusao=True,
    ))
    assert result["constelacao_completa"] is True
    assert result["nucleo_brash"] is True
    assert result["risco"] == "emergencia_hemodinamica"
    assert "não deve atrasar" in result["prioridade"]


def test_hipercalemia_moderada_pode_compor_padrao_brash():
    result = CALC.compute(base(
        frequencia_cardiaca_bpm=42,
        potassio_mmol_l=5.2,
        lra_ou_agudizacao_drc=True,
        uso_bloqueador_nodal_av=True,
    ))
    assert result["nucleo_brash"] is True
    assert result["risco"] == "fortemente_sugestivo"
    assert "não possui escore diagnóstico validado" in result["prioridade"]


def test_ecg_nao_tipico_nao_exclui_padrao():
    result = CALC.compute(base(
        frequencia_cardiaca_bpm=38,
        potassio_mmol_l=5.4,
        lra_ou_agudizacao_drc=True,
        uso_bloqueador_nodal_av=True,
        ecg_compativel_hipercalemia=False,
    ))
    assert result["nucleo_brash"] is True
    assert "não exclui BRASH" in result["ecg"]


def test_sem_bloqueador_nodal_redireciona_diferencial_para_hipercalemia():
    result = CALC.compute(base(
        frequencia_cardiaca_bpm=39,
        potassio_mmol_l=6.3,
        lra_ou_agudizacao_drc=True,
        uso_bloqueador_nodal_av=False,
    ))
    assert result["risco"] == "diferencial_hipercalemia"
    assert result["nucleo_brash"] is False
    assert "não rotular BRASH" in result["prioridade"]


def test_overdose_sem_renal_ou_hipercalemia_pesa_para_toxicidade():
    result = CALC.compute(base(
        frequencia_cardiaca_bpm=36,
        uso_bloqueador_nodal_av=True,
        dose_excessiva_ou_overdose_suspeita=True,
    ))
    assert result["risco"] == "diferencial_toxicidade"
    assert "toxicidade" in result["prioridade"].casefold()


def test_substrato_sem_bradicardia_nao_vira_brash():
    result = CALC.compute(base(
        frequencia_cardiaca_bpm=68,
        potassio_mmol_l=5.5,
        lra_ou_agudizacao_drc=True,
        uso_bloqueador_nodal_av=True,
    ))
    assert result["risco"] == "substrato_sem_bradicardia"
    assert result["nucleo_brash"] is False


def test_bradicardia_com_choque_e_emergencia_mesmo_sem_constelacao_completa():
    result = CALC.compute(base(
        frequencia_cardiaca_bpm=34,
        potassio_mmol_l=4.6,
        choque_ou_hipoperfusao=True,
    ))
    assert result["risco"] == "emergencia_hemodinamica"
    assert result["constelacao_completa"] is False


def test_nodos_tudo_com_tudo_sao_os_fluxos_diretos_esperados():
    result = CALC.compute(base())
    expected = {
        "sindrome-brash-bradicardia-insuficiencia-renal-bloqueio-av-choque-e-hipercalemia",
        "fluxograma-sindrome-brash",
        "fluxograma-bradicardia-sintomatica-manejo-agudo",
        "fluxograma-hipercalemia-grave",
        "fluxograma-intoxicacao-por-betabloqueador-ou-antagonista-de-calcio",
    }
    assert set(result["nodos_relacionados"]) == expected


def test_rejeita_valores_invalidos():
    with pytest.raises(ValueError):
        CALC.compute(base(frequencia_cardiaca_bpm=5))
    with pytest.raises(ValueError):
        CALC.compute(base(potassio_mmol_l=float("nan")))
    with pytest.raises(ValueError):
        CALC.compute(base(potassio_mmol_l=10))


def test_limitacoes_preservam_decisao_humana_e_nao_embutem_posologia():
    text = " ".join(CALC.limitations).casefold()
    assert "não possui escore diagnóstico" in text
    assert "não seleciona antídoto" in text
    for forbidden in ("mg/kg", "mcg/kg", "meq/h", "mmol/h", "j/kg"):
        assert forbidden not in text
