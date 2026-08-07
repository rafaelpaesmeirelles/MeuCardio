"""Calculadora de Doses Cardiológicas (pedido do Rafael, 07/08/2026).

Sem fixture de banco de propósito: `calculators.py`/`dose_calculators.py` não
têm dependência nenhuma de SQLAlchemy/FastAPI — são funções puras, e testá-las
assim é o que o próprio histórico do projeto já registrou como necessário
("erro em calculadora clínica é pior que lacuna de conteúdo", TAREFA ESPECIAL
corvia2, calculadoras testadas fora do Docker por não haver bind-mount de
código-fonte no container de produção).

Cada valor esperado abaixo foi conferido à mão por análise dimensional (para
`infusao-continua-peso`) ou por multiplicação direta peso × dose/kg (para as
demais) antes de escrever o teste — não o inverso.
"""

from app.services import calculators as calc


def test_registro_tem_as_nove_calculadoras_de_dose():
    doses = [c for c in calc.REGISTRY.values() if c.kind == "dose"]
    assert len(doses) == 9
    areas = {c.theme for c in doses}
    assert areas == {
        "Doses — Cardiologia Geral",
        "Doses — Cardiologia Pediátrica",
        "Doses — Medicina Intensiva",
    }


def test_infusao_noradrenalina_peso_ajustada():
    # 0,1 mcg/kg/min × 70 kg × 60 min = 420 mcg/h; concentração 4 mg/250 mL =
    # 16 mcg/mL; 420 / 16 = 26,25 mL/h.
    r = calc.run("infusao-continua-peso", {
        "droga": "noradrenalina", "peso": 70, "dose_alvo": 0.1,
        "quantidade_no_frasco": 4, "volume_da_solucao": 250,
    })
    assert r["result"]["ml_h"] == 26.25
    assert r["result"]["fora_da_faixa"] is False


def test_infusao_avisa_fora_da_faixa_sem_bloquear():
    r = calc.run("infusao-continua-peso", {
        "droga": "noradrenalina", "peso": 70, "dose_alvo": 2.0,
        "quantidade_no_frasco": 4, "volume_da_solucao": 250,
    })
    assert r["result"]["fora_da_faixa"] is True
    assert "FORA da faixa" in r["interpretation"]


def test_infusao_vasopressina_por_minuto_nao_por_peso():
    # 0,03 U/min × 60 / (20 U/100 mL = 0,2 U/mL) = 9 mL/h — vasopressina não
    # usa peso, e a concentração é em U/mL, não mg/mL.
    r = calc.run("infusao-continua-peso", {
        "droga": "vasopressina", "dose_alvo": 0.03,
        "quantidade_no_frasco": 20, "volume_da_solucao": 100,
    })
    assert r["result"]["ml_h"] == 9.0


def test_infusao_fentanil_dose_por_hora_nao_por_minuto():
    # 1,5 mcg/kg/h × 80 kg = 120 mcg/h; concentração 2,5 mg/50 mL = 50 mcg/mL;
    # 120 / 50 = 2,4 mL/h (fator de tempo 1, não 60 — dose já é por hora).
    r = calc.run("infusao-continua-peso", {
        "droga": "fentanil", "peso": 80, "dose_alvo": 1.5,
        "quantidade_no_frasco": 2.5, "volume_da_solucao": 50,
    })
    assert r["result"]["ml_h"] == 2.4


def test_infusao_sem_peso_em_droga_peso_dependente_levanta_erro():
    import pytest
    with pytest.raises(ValueError):
        calc.run("infusao-continua-peso", {
            "droga": "noradrenalina", "dose_alvo": 0.1,
            "quantidade_no_frasco": 4, "volume_da_solucao": 250,
        })


def test_heparina_nao_fracionada_80kg():
    r = calc.run("heparina-nao-fracionada-nomograma", {"peso": 80})
    assert r["result"]["bolus_ui"] == 6400  # 80 × 80
    assert r["result"]["infusao_ui_h"] == 1440  # 80 × 18


def test_enoxaparina_tratamento_sem_ajuste():
    r = calc.run("enoxaparina-dose", {"peso": 70, "indicacao": "tratamento_tev_sca", "clcr_menor_30": False})
    assert r["result"]["dose_mg"] == 70.0


def test_enoxaparina_profilaxia_com_ajuste_renal():
    r = calc.run("enoxaparina-dose", {"peso": 70, "indicacao": "profilaxia", "clcr_menor_30": True})
    assert r["result"]["dose_mg"] == 20


def test_digoxina_impregnacao_e_manutencao():
    r = calc.run("digoxina-dose", {"peso": 70, "clcr_reduzido": False})
    assert r["result"]["impregnacao_min_mcg"] == 560.0  # 70 × 8
    assert r["result"]["impregnacao_max_mcg"] == 840.0  # 70 × 12
    assert r["result"]["manutencao_min_mcg"] == 210.0  # 70 × 3
    assert r["result"]["manutencao_max_mcg"] == 350.0  # 70 × 5


def test_digoxina_manutencao_reduzida_na_disfuncao_renal():
    r = calc.run("digoxina-dose", {"peso": 70, "clcr_reduzido": True})
    assert r["result"]["manutencao_min_mcg"] == 105.0  # metade de 210


def test_adrenalina_pcr_pediatrica_dose_e_volume():
    # 0,01 mg/kg × 20 kg = 0,2 mg; diluição 1:10.000 (0,1 mg/mL) => 2 mL.
    r = calc.run("adrenalina-pcr-pediatrica", {"peso": 20})
    assert r["result"]["dose_mg"] == 0.2
    assert r["result"]["volume_ml"] == 2.0


def test_adrenalina_pcr_pediatrica_respeita_teto_de_1mg():
    r = calc.run("adrenalina-pcr-pediatrica", {"peso": 150})
    assert r["result"]["dose_mg"] == 1.0


def test_amiodarona_pcr_pediatrica():
    r = calc.run("amiodarona-pcr-pediatrica", {"peso": 20})
    assert r["result"]["dose_mg"] == 100.0  # 5 × 20
    assert r["result"]["dose_mg_maxima_dia"] == 300.0  # 15 × 20


def test_choque_pediatrico_desfibrilacao():
    r = calc.run("choque-eletrico-pediatrico", {"peso": 20, "tipo": "desfibrilacao"})
    assert r["result"]["primeira"] == 40.0  # 2 J/kg
    assert r["result"]["subsequente"] == 80.0  # 4 J/kg
    assert r["result"]["teto"] == 200.0  # 10 J/kg


def test_choque_pediatrico_cardioversao():
    r = calc.run("choque-eletrico-pediatrico", {"peso": 20, "tipo": "cardioversao"})
    assert r["result"]["subsequente"] == 40.0  # 2 J/kg
    assert "10.0–20.0 J" in r["interpretation"]  # faixa 0,5-1 J/kg


def test_adenosina_pediatrica_respeita_teto_por_dose():
    # 0,1 mg/kg × 80 kg = 8 mg, capado em 6 mg (teto da 1ª dose).
    r = calc.run("adenosina-tsv-pediatrica", {"peso": 80, "numero_dose": 1})
    assert r["result"]["dose_mg"] == 6
    # 0,2 mg/kg × 20 kg = 4 mg, dentro do teto de 12 mg da 2ª dose.
    r2 = calc.run("adenosina-tsv-pediatrica", {"peso": 20, "numero_dose": 2})
    assert r2["result"]["dose_mg"] == 4.0


def test_atropina_pediatrica_respeita_piso_de_0_1mg():
    r = calc.run("atropina-bradicardia-pediatrica", {"peso": 3})
    assert r["result"]["dose_mg"] == 0.1  # 0,02 × 3 = 0,06, elevado ao piso


def test_atropina_pediatrica_respeita_teto_de_0_5mg():
    r = calc.run("atropina-bradicardia-pediatrica", {"peso": 40})
    assert r["result"]["dose_mg"] == 0.5  # 0,02 × 40 = 0,8, reduzido ao teto
