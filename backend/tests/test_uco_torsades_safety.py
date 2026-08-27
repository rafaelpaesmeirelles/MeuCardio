from app.services.intensive_care_arrhythmia_safety import INTENSIVE_CARE_ARRHYTHMIA_SAFETY_REGISTRY


CALC = INTENSIVE_CARE_ARRHYTHMIA_SAFETY_REGISTRY["torsades-qt-longo-magnesio-uco"]


def base(**overrides):
    data = {
        "tv_polimorfica_atual": False,
        "episodio_sustentado": False,
        "qt_longo_conhecido_ou_suspeito": False,
        "bradicardia_ou_pausa_precipitante": False,
        "hipocalemia_documentada": False,
        "hipomagnesemia_documentada": False,
        "farmaco_prolonga_qt": False,
        "isquemia_aguda_suspeita": False,
        "lqts_congenito_conhecido": False,
    }
    data.update(overrides)
    return data


def test_tv_polimorfica_sustentada_prioriza_desfibrilacao():
    result = CALC.compute(base(tv_polimorfica_atual=True, episodio_sustentado=True))
    assert result["risco"] == "emergencia"
    assert "choque não sincronizado imediato" in result["prioridade"]


def test_torsades_qt_longo_permite_magnesio_sem_exigir_hipomagnesemia():
    result = CALC.compute(base(
        tv_polimorfica_atual=True,
        qt_longo_conhecido_ou_suspeito=True,
        hipomagnesemia_documentada=False,
    ))
    assert "compatível com torsades" in result["fenotipo"]
    assert "não depende da presença de hipomagnesemia" in result["papel_do_magnesio"]


def test_tv_polimorfica_qt_normal_nao_recebe_magnesio_reflexo():
    result = CALC.compute(base(tv_polimorfica_atual=True, isquemia_aguda_suspeita=True))
    assert "não rotular automaticamente como torsades" in result["fenotipo"]
    assert "Magnésio rotineiro não é recomendado" in result["papel_do_magnesio"]


def test_pause_dependent_adquirida_e_congenita_nao_sao_fundidas():
    acquired = CALC.compute(base(
        tv_polimorfica_atual=True,
        qt_longo_conhecido_ou_suspeito=True,
        bradicardia_ou_pausa_precipitante=True,
    ))
    assert "overdrive pacing ou isoproterenol" in acquired["estrategia_frequencia"]

    congenital = CALC.compute(base(
        tv_polimorfica_atual=True,
        qt_longo_conhecido_ou_suspeito=True,
        bradicardia_ou_pausa_precipitante=True,
        lqts_congenito_conhecido=True,
    ))
    assert "não extrapolar isoproterenol" in congenital["estrategia_frequencia"]


def test_qtc_maior_500_com_pausa_gera_alerta_sem_diagnosticar_torsades():
    result = CALC.compute(base(qtc_ms=520, bradicardia_ou_pausa_precipitante=True))
    assert result["qtc_alto_risco"] is True
    assert "QTc >500 ms" in result["prioridade"]
    assert "sem TV polimórfica atual" in result["fenotipo"]


def test_nao_contem_dose_energia_ou_parametro_pacing():
    text = " ".join(CALC.limitations).casefold()
    for forbidden in ("mg/kg", "mcg/kg/min", "joule", "j/kg", "bpm de pacing"):
        assert forbidden not in text
