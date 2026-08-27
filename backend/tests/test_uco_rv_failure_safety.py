from app.services.intensive_care_rv_failure_safety import INTENSIVE_CARE_RV_FAILURE_SAFETY_REGISTRY


CALC = INTENSIVE_CARE_RV_FAILURE_SAFETY_REGISTRY["falencia-vd-fenotipo-hemodinamico-uco"]


def base(**overrides):
    data = {
        "disfuncao_vd_documentada": False,
        "choque_ou_hipoperfusao": False,
        "congestao_venosa_ou_pressao_direita_elevada": False,
        "baixo_enchimento_sem_congestao_suspeito": False,
        "sobrecarga_aguda_pos_carga_vd_suspeita": False,
        "ventilacao_pressao_positiva": False,
        "hipoxemia_ou_hipercapnia": False,
        "tep_agudo_suspeito": False,
        "infarto_vd_suspeito": False,
        "tamponamento_suspeito": False,
        "hipertensao_pulmonar_descompensada": False,
    }
    data.update(overrides)
    return data


def test_choque_com_disfuncao_vd_e_emergencia_hemodinamica():
    result = CALC.compute(base(disfuncao_vd_documentada=True, choque_ou_hipoperfusao=True))
    assert result["risco"] == "emergencia_hemodinamica"
    assert "não autoriza atraso" in result["prioridade"]


def test_congestao_bloqueia_expansao_reflexa_sem_prescrever_diuretico():
    result = CALC.compute(base(disfuncao_vd_documentada=True, congestao_venosa_ou_pressao_direita_elevada=True))
    assert result["fenotipo_volume"] == "vd_congesto"
    assert "expansão volêmica reflexa" in result["volume"]
    assert "sem volume fixo ou diurético automático" in result["volume"]


def test_subpreenchimento_permite_apenas_reposicao_cautelosa_reavaliada():
    result = CALC.compute(base(disfuncao_vd_documentada=True, baixo_enchimento_sem_congestao_suspeito=True))
    assert result["fenotipo_volume"] == "possivel_subpreenchimento"
    assert "reposição cautelosa pode ser considerada" in result["volume"].casefold()
    assert "não define volume" in result["volume"]


def test_dados_volumetricos_conflitantes_nao_geram_conduta_automatica():
    result = CALC.compute(base(
        disfuncao_vd_documentada=True,
        congestao_venosa_ou_pressao_direita_elevada=True,
        baixo_enchimento_sem_congestao_suspeito=True,
    ))
    assert result["fenotipo_volume"] == "dados_volumetricos_discordantes"
    assert "não recomendar bolus nem restrição" in result["volume"].casefold()


def test_pressao_positiva_expoe_risco_sem_programar_ventilador():
    result = CALC.compute(base(disfuncao_vd_documentada=True, ventilacao_pressao_positiva=True, hipoxemia_ou_hipercapnia=True))
    assert "reduzir preload" in result["ventilacao"]
    assert "aumentar afterload" in result["ventilacao"]
    assert "nenhum ajuste de peep" in result["ventilacao"].casefold()
    assert "resistência vascular pulmonar" in result["ventilacao"]


def test_tep_tamponamento_e_infarto_mantem_fluxos_causais():
    result = CALC.compute(base(
        choque_ou_hipoperfusao=True,
        tep_agudo_suspeito=True,
        infarto_vd_suspeito=True,
        tamponamento_suspeito=True,
    ))
    text = " ".join(result["causas_prioritarias"]).casefold()
    assert "tep agudo" in text
    assert "infarto de vd" in text
    assert "tamponamento" in text
    assert result["risco"] == "emergencia_hemodinamica"


def test_falencia_vd_sem_dados_de_volemia_nao_autoriza_volume_ou_restricao():
    result = CALC.compute(base(disfuncao_vd_documentada=True))
    assert result["fenotipo_volume"] == "volemia_nao_definida"
    assert "não autoriza nem expansão nem restrição" in result["volume"]


def test_tudo_com_tudo_reutiliza_protocolo_e_fluxograma_existentes():
    result = CALC.compute(base())
    assert set(result["nodos_relacionados"]) == {
        "falencia-aguda-do-ventriculo-direito-cor-pulmonale-agudo-consenso-acvc-esc-2024",
        "fluxograma-falencia-aguda-de-ventriculo-direito",
    }


def test_limitacoes_impedem_volume_droga_ventilador_e_mcs_automaticos():
    text = " ".join(CALC.limitations).casefold()
    assert "não calcula volume" in text
    assert "não seleciona vasopressor" in text
    assert "não prescreve peep" in text
    assert "não é inferida" in text
    for forbidden in ("mg/kg", "mcg/kg", "ml/kg", "j/kg", "rpm"):
        assert forbidden not in text
