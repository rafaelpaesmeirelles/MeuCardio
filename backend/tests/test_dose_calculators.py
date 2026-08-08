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


def test_registro_tem_pelo_menos_as_nove_calculadoras_de_dose_originais():
    """As 9 originais (07/08/2026) nunca deveriam sumir do registro, mas o
    total só cresce — produção contínua (ChatGPT/Grupo B) já acrescentou
    árvores de dose novas (ACLS/PALS 2025, antiagregantes e anticoagulação
    na SCA, fibrinolíticos, bulas brasileiras) em temas que não existiam em
    07/08. Fixar `== 9` deixava o teste furado a cada calculadora nova
    legítima — por isso a checagem vira "nunca encolhe" e "os slugs
    originais continuam existindo", não uma contagem exata."""
    doses = [c for c in calc.REGISTRY.values() if c.kind == "dose"]
    assert len(doses) >= 9
    areas = {c.theme for c in doses}
    assert areas.issuperset({
        "Doses — Cardiologia Geral",
        "Doses — Cardiologia Pediátrica",
        "Doses — Medicina Intensiva",
    })
    slugs_originais = {
        "infusao-continua-peso", "heparina-nao-fracionada-nomograma",
        "enoxaparina-dose", "digoxina-dose", "adrenalina-pcr-pediatrica",
        "amiodarona-pcr-pediatrica", "choque-eletrico-pediatrico",
        "adenosina-tsv-pediatrica", "atropina-bradicardia-pediatrica",
    }
    assert slugs_originais.issubset({c.slug for c in doses})


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
    # PALS 2025 (dose_calculators_pals2025_chatgpt.py, substituiu a versão
    # PALS 2020 pelo mesmo slug, 08/08/2026): o campo de volume ganhou o
    # nome `volume_ml_0_1mg_ml`, deixando a concentração explícita na
    # própria chave em vez de só no texto interpretativo.
    r = calc.run("adrenalina-pcr-pediatrica", {"peso": 20})
    assert r["result"]["dose_mg"] == 0.2
    assert r["result"]["volume_ml_0_1mg_ml"] == 2.0


def test_adrenalina_pcr_pediatrica_respeita_teto_de_1mg():
    r = calc.run("adrenalina-pcr-pediatrica", {"peso": 150})
    assert r["result"]["dose_mg"] == 1.0


def test_amiodarona_pcr_pediatrica():
    # PALS 2025 substituiu o teto diário único (15 mg/kg/dia) por um teto
    # POR DOSE, diferente na 1ª (300 mg) e nas subsequentes (150 mg) — por
    # isso `numero_dose` passou a ser obrigatório e `dose_mg_maxima_dia`
    # não existe mais.
    r = calc.run("amiodarona-pcr-pediatrica", {"peso": 20, "numero_dose": 1})
    assert r["result"]["dose_mg"] == 100.0  # 5 × 20
    assert r["result"]["teto_desta_dose_mg"] == 300.0

    r2 = calc.run("amiodarona-pcr-pediatrica", {"peso": 40, "numero_dose": 2})
    assert r2["result"]["dose_mg"] == 150.0  # 5 × 40 = 200, capado em 150
    assert r2["result"]["teto_desta_dose_mg"] == 150.0


def test_choque_pediatrico_desfibrilacao():
    # PALS 2025 renomeou as chaves do resultado (primeiro_j/segundo_j/
    # subsequente_min_j/teto_peso_j, no lugar de primeira/subsequente/teto)
    # e passou a distinguir 1º e 2º choque, além do piso dos subsequentes.
    r = calc.run("choque-eletrico-pediatrico", {"peso": 20, "tipo": "desfibrilacao"})
    assert r["result"]["primeiro_j"] == 40.0  # 2 J/kg
    assert r["result"]["segundo_j"] == 80.0  # 4 J/kg
    assert r["result"]["subsequente_min_j"] == 80.0  # ≥4 J/kg
    assert r["result"]["teto_peso_j"] == 200.0  # 10 J/kg


def test_choque_pediatrico_cardioversao():
    r = calc.run("choque-eletrico-pediatrico", {"peso": 20, "tipo": "cardioversao"})
    assert r["result"]["primeiro_min_j"] == 10.0  # 0,5 J/kg
    assert r["result"]["primeiro_max_j"] == 20.0  # 1 J/kg
    assert r["result"]["segundo_j"] == 40.0  # 2 J/kg
    assert "10.0-20.0 J" in r["interpretation"]  # faixa 0,5-1 J/kg


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
