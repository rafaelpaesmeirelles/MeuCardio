"""Testes puros da central de Cardiologia Intensiva e UCO."""

import math

import pytest

from app.services import calculators
from app.services.intensive_care_calculators import INTENSIVE_CARE_CALCULATOR_REGISTRY


def _calc():
    return INTENSIVE_CARE_CALCULATOR_REGISTRY["ventilacao-protetora-uco"]


def _calc_bomba():
    return INTENSIVE_CARE_CALCULATOR_REGISTRY["conferencia-bomba-infusao-uco"]


def _calc_scai():
    return INTENSIVE_CARE_CALCULATOR_REGISTRY["estadiamento-scai-choque-cardiogenico"]


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


def _dados_bomba(**mudancas):
    dados = {
        "agente": "norepinefrina",
        "peso_kg": 70,
        "dose_pretendida": 0.1,
        "quantidade_soluto": 4,
        "volume_total_ml": 250,
        "velocidade_bomba_ml_h": 26.25,
        "tolerancia_percentual": "5",
        "contexto_choque_cardiogenico": False,
    }
    dados.update(mudancas)
    return dados


def _dados_scai(**mudancas):
    dados = {
        "em_risco_sem_instabilidade": False,
        "instabilidade_sem_hipoperfusao": False,
        "hipoperfusao_requer_intervencao": True,
        "deterioracao_apos_intervencao": False,
        "colapso_extremis": False,
        "parada_com_risco_anoxico": False,
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


def test_conferencia_reversa_norepinefrina_fecha_dose_e_velocidade():
    resultado = _calc_bomba().compute(_dados_bomba())

    assert resultado["concentracao_calculada"] == "16.00 mcg/mL"
    assert resultado["dose_entregue_calculada"] == 0.1
    assert resultado["velocidade_esperada_ml_h"] == 26.25
    assert resultado["desvio_percentual_absoluto"] == 0
    assert resultado["fora_da_faixa"] is False


def test_conferencia_calcula_agente_ponderal_e_nao_ponderal():
    dobutamina = _calc_bomba().compute(
        _dados_bomba(
            agente="dobutamina",
            peso_kg=80,
            dose_pretendida=2.083333,
            quantidade_soluto=250,
            volume_total_ml=250,
            velocidade_bomba_ml_h=10,
        )
    )
    nitroglicerina = _calc_bomba().compute(
        _dados_bomba(
            agente="nitroglicerina",
            dose_pretendida=50,
            quantidade_soluto=50,
            volume_total_ml=250,
            velocidade_bomba_ml_h=15,
        )
    )

    assert dobutamina["dose_entregue_calculada"] == 2.083333
    assert nitroglicerina["dose_entregue_calculada"] == 50


def test_vasopressina_usa_unidades_por_minuto_sem_dividir_pelo_peso():
    resultado = _calc_bomba().compute(
        _dados_bomba(
            agente="vasopressina",
            peso_kg=1,
            dose_pretendida=0.03,
            quantidade_soluto=20,
            volume_total_ml=100,
            velocidade_bomba_ml_h=9,
        )
    )

    assert resultado["concentracao_calculada"] == "0.2000 U/mL"
    assert resultado["dose_entregue_calculada"] == 0.03
    assert resultado["unidade_dose"] == "U/min"


def test_peso_pode_ser_omitido_em_agente_nao_ponderal():
    dados = _dados_bomba(
        agente="vasopressina",
        dose_pretendida=0.03,
        quantidade_soluto=20,
        volume_total_ml=100,
        velocidade_bomba_ml_h=9,
    )
    dados.pop("peso_kg")

    resultado = _calc_bomba().compute(dados)

    assert resultado["dose_entregue_calculada"] == 0.03


def test_divergencia_operacional_gera_gate_mesmo_sem_faixa_terapeutica():
    resultado = _calc_bomba().compute(
        _dados_bomba(velocidade_bomba_ml_h=30, tolerancia_percentual="5")
    )

    assert resultado["desvio_percentual_absoluto"] == 14.29
    assert resultado["fora_da_faixa"] is True
    assert "DIVERGÊNCIA" in resultado["status_conferencia"]
    assert "não avaliada" in resultado["alerta_contextual"]


def test_limite_exato_da_tolerancia_nao_diverge_por_erro_binario():
    resultado = _calc_bomba().compute(
        _dados_bomba(velocidade_bomba_ml_h=24.9375, tolerancia_percentual="5")
    )

    assert math.isclose(resultado["dose_entregue_calculada"], 0.095)
    assert resultado["desvio_percentual_absoluto"] == 5.0
    assert resultado["fora_da_faixa"] is False


def test_faixa_acc_so_e_aplicada_quando_contexto_e_declarado():
    sem_contexto = _calc_bomba().compute(
        _dados_bomba(dose_pretendida=1.2, velocidade_bomba_ml_h=315)
    )
    com_contexto = _calc_bomba().compute(
        _dados_bomba(
            dose_pretendida=1.2,
            velocidade_bomba_ml_h=315,
            contexto_choque_cardiogenico=True,
        )
    )

    assert sem_contexto["fora_da_faixa"] is False
    assert "não aplicada" in sem_contexto["faixa_acc_2025"]
    assert com_contexto["fora_da_faixa"] is True
    assert "fora da faixa contextual" in com_contexto["alerta_contextual"]


@pytest.mark.parametrize(
    "mudanca, mensagem",
    [
        ({"quantidade_soluto": 0}, "devem ser positivos"),
        ({"volume_total_ml": 0}, "devem ser positivos"),
        ({"velocidade_bomba_ml_h": -1}, "não pode ser negativa"),
        ({"tolerancia_percentual": "3"}, "2%, 5% ou 10%"),
        ({"peso_kg": 0}, "peso entre 1 e 400"),
        ({"dose_pretendida": "NaN"}, "valores numéricos finitos"),
        ({"quantidade_soluto": "Infinity"}, "valores numéricos finitos"),
    ],
)
def test_conferencia_rejeita_entradas_invalidas(mudanca, mensagem):
    with pytest.raises(ValueError, match=mensagem):
        _calc_bomba().compute(_dados_bomba(**mudanca))


def test_conferencia_bomba_esta_registrada_no_tema_exato_tudo_com_tudo():
    calculadora = calculators.REGISTRY["conferencia-bomba-infusao-uco"]

    assert calculadora.theme == "Terapia intensiva"
    assert calculadora.status == "implementada"
    assert calculadora.kind == "dose"


@pytest.mark.parametrize(
    "campo, estagio",
    [
        ("em_risco_sem_instabilidade", "A — em risco"),
        ("instabilidade_sem_hipoperfusao", "B — choque iniciando"),
        ("hipoperfusao_requer_intervencao", "C — choque clássico"),
        ("deterioracao_apos_intervencao", "D — deteriorando"),
        ("colapso_extremis", "E — extremis"),
    ],
)
def test_scai_mapeia_padrao_clinico_predominante_de_a_a_e(campo, estagio):
    dados = _dados_scai(hipoperfusao_requer_intervencao=False)
    dados[campo] = True

    resultado = _calc_scai().compute(dados)

    assert resultado["estagio_sugerido"] == estagio
    assert resultado["rotulo_para_documentacao"] == f"SCAI {estagio[0]}"


def test_scai_usa_maior_gravidade_quando_mais_de_um_padrao_e_marcado():
    resultado = _calc_scai().compute(
        _dados_scai(
            instabilidade_sem_hipoperfusao=True,
            deterioracao_apos_intervencao=True,
        )
    )

    assert resultado["estagio_sugerido"] == "D — deteriorando"


def test_scai_modificador_a_exige_declaracao_de_risco_anoxico():
    sem_modificador = _calc_scai().compute(_dados_scai())
    com_modificador = _calc_scai().compute(
        _dados_scai(parada_com_risco_anoxico=True)
    )

    assert sem_modificador["rotulo_para_documentacao"] == "SCAI C"
    assert com_modificador["rotulo_para_documentacao"] == "SCAI C+A"
    assert "potencial lesão cerebral anóxica" in com_modificador["modificador_a"]


def test_scai_medidas_opcionais_nao_substituem_padrao_clinico():
    with pytest.raises(ValueError, match="não pode ser inferido apenas por números"):
        _calc_scai().compute(
            _dados_scai(
                hipoperfusao_requer_intervencao=False,
                lactato_mmol_l=5,
                pas_mmhg=80,
            )
        )


def test_scai_sinaliza_discordancia_sem_promover_estagio_automaticamente():
    resultado = _calc_scai().compute(
        _dados_scai(
            hipoperfusao_requer_intervencao=False,
            instabilidade_sem_hipoperfusao=True,
            lactato_mmol_l=9,
            ph_arterial=7.1,
        )
    )

    assert resultado["estagio_sugerido"] == "B — choque iniciando"
    assert resultado["fora_da_faixa"] is True
    assert "reavaliar antes de manter A/B" in resultado["alerta_de_consistencia"]
    assert "avaliar o conjunto clínico para estágio E" in resultado["alerta_de_consistencia"]


def test_scai_documenta_medidas_e_reavaliacao_seriada():
    resultado = _calc_scai().compute(
        _dados_scai(pas_mmhg=85, pam_mmhg=58, frequencia_cardiaca_bpm=110, lactato_mmol_l=3)
    )

    assert resultado["medidas_de_apoio"] == "PAS 85 mmHg, PAM 58 mmHg, FC 110 bpm, lactato 3 mmol/L"
    assert "estágio inicial e máximo" in resultado["reavaliacao"]


@pytest.mark.parametrize(
    "mudanca, mensagem",
    [
        ({"lactato_mmol_l": "NaN"}, "valores numéricos finitos"),
        ({"lactato_mmol_l": 31}, "lactato entre 0 e 30"),
        ({"ph_arterial": 8}, "pH arterial entre"),
        ({"pas_mmhg": -1}, "PAS deve estar entre 0 e 400"),
        ({"frequencia_cardiaca_bpm": 351}, "frequência cardíaca deve estar entre 0 e 350"),
    ],
)
def test_scai_rejeita_medidas_invalidas(mudanca, mensagem):
    with pytest.raises(ValueError, match=mensagem):
        _calc_scai().compute(_dados_scai(**mudanca))


def test_scai_esta_registrado_no_tema_e_expoe_numeros_opcionais():
    calculadora = calculators.REGISTRY["estadiamento-scai-choque-cardiogenico"]
    opcionais = {campo.name for campo in calculadora.fields if not campo.required}

    assert calculadora.theme == "Terapia intensiva"
    assert calculadora.status == "implementada"
    assert calculadora.kind == "assessment"
    assert opcionais == {
        "pas_mmhg",
        "pam_mmhg",
        "frequencia_cardiaca_bpm",
        "lactato_mmol_l",
        "ph_arterial",
    }


def test_scai_c_exclui_hipoperfusao_resolvida_com_volume_isolado():
    calculadora = calculators.REGISTRY["estadiamento-scai-choque-cardiogenico"]
    campo_c = next(
        campo for campo in calculadora.fields if campo.name == "hipoperfusao_requer_intervencao"
    )
    resultado = calculadora.compute(_dados_scai())

    assert "além de volume isolado" in campo_c.label
    assert "resolve apenas com reposição volêmica não preenche" in campo_c.help
    assert "além de reposição volêmica isolada" in resultado["criterio_determinante"]
