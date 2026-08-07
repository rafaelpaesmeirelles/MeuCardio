"""Calculadoras perioperatórias adicionais produzidas pelo ChatGPT.

Governança: somente fórmulas/itens explicitamente verificáveis em fonte primária
ou diretriz foram implementados. GSCRI e ACS-NSQIP permanecem fora deste módulo
porque a regressão completa não foi validada nesta sessão contra a fonte primária
(GSCRI) e o ACS exige uso do calculador oficial dinâmico (NSQIP).

Fonte: ChatGPT
"""

from __future__ import annotations

from app.services.calculators import Calculator, Field


# ---------------------------------------------------------------------- DASI
# Hlatky MA et al. Am J Cardiol. 1989;64(10):651-654.
# PMID: 2782256. DOI: 10.1016/0002-9149(89)90496-7.
# Os pesos abaixo também constam do material oficial da AHA/ACC 2024.
_DASI_ITEMS: tuple[tuple[str, str, float], ...] = (
    ("autocuidado", "Cuida de si mesmo (alimentar-se, vestir-se, banho e banheiro)", 2.75),
    ("caminhar_casa", "Caminha dentro de casa", 1.75),
    ("caminhar_quarteiroes", "Caminha 1–2 quarteirões em terreno plano", 2.75),
    ("escada_ladeira", "Sobe um lance de escadas ou uma ladeira", 5.50),
    ("correr_curto", "Corre uma curta distância", 8.00),
    ("trabalho_domestico_leve", "Faz trabalho doméstico leve", 2.70),
    ("trabalho_domestico_moderado", "Faz trabalho doméstico moderado", 3.50),
    ("trabalho_domestico_pesado", "Faz trabalho doméstico pesado", 8.00),
    ("quintal_jardim", "Faz trabalho no quintal/jardim", 4.50),
    ("relacoes_sexuais", "Mantém relações sexuais", 5.25),
    ("recreacao_moderada", "Realiza atividade recreativa moderada", 6.00),
    ("esporte_extenuante", "Pratica esporte extenuante", 7.50),
)


def _dasi(d: dict) -> dict:
    score = round(sum(weight for key, _, weight in _DASI_ITEMS if bool(d.get(key))), 2)
    return {
        "score": score,
        "max": 58.2,
        "capacidade_funcional": "ruim" if score <= 34 else "adequada_pelo_ponto_de_decisao_aha_acc_2024",
        "ponto_decisao": 34,
    }


def _dasi_txt(r: dict) -> str:
    if r["score"] <= 34:
        return (
            f"DASI {r['score']}/58,2 — capacidade funcional ruim pelo ponto de decisão "
            "DASI ≤34 do algoritmo AHA/ACC 2024. Esse resultado não indica teste isquêmico "
            "automaticamente: deve ser integrado ao risco perioperatório e à possibilidade de "
            "o exame adicional modificar a conduta."
        )
    return (
        f"DASI {r['score']}/58,2 — acima do ponto de decisão de 34 usado no algoritmo "
        "AHA/ACC 2024. Em paciente clinicamente estável, isso favorece prosseguir sem teste "
        "isquêmico de rotina, salvo indicação cardiovascular independente."
    )


# ------------------------------------------------------------------ AUB-HAS2
# Dakik HA et al. J Am Coll Cardiol. 2019;73(24):3067-3078.
# PMID: 31221255. DOI: 10.1016/j.jacc.2019.04.023.
_AUB_HAS2_ITEMS: tuple[tuple[str, str], ...] = (
    ("historia_doenca_cardiaca", "História de doença cardíaca"),
    ("sintomas_cardiacos", "Angina ou dispneia sugestiva de doença cardíaca"),
    ("idade_maior_igual_75", "Idade ≥75 anos"),
    ("hemoglobina_menor_12", "Hemoglobina <12 g/dL"),
    ("cirurgia_vascular", "Cirurgia vascular"),
    ("cirurgia_emergencia", "Cirurgia de emergência"),
)


def _aub_has2(d: dict) -> dict:
    score = sum(1 for key, _ in _AUB_HAS2_ITEMS if bool(d.get(key)))
    if score <= 1:
        categoria = "baixo"
    elif score <= 3:
        categoria = "intermediario"
    else:
        categoria = "alto"
    return {"score": score, "max": 6, "categoria": categoria}


def _aub_has2_txt(r: dict) -> str:
    return (
        f"AUB-HAS2 {r['score']}/6 — risco {r['categoria']}. No estudo original, 0–1 ponto "
        "foi classificado como baixo risco, 2–3 como intermediário e >3 como alto risco para "
        "o composto de morte, infarto do miocárdio ou AVC em 30 dias. O escore não substitui "
        "avaliação de doença cardiovascular ativa, capacidade funcional ou modificadores de risco."
    )


PERIOPERATIVE_REGISTRY: dict[str, Calculator] = {
    "dasi": Calculator(
        slug="dasi",
        name="DASI — Duke Activity Status Index",
        theme="Perioperatório",
        purpose=(
            "Avaliação estruturada da capacidade funcional no pré-operatório. O algoritmo "
            "AHA/ACC 2024 usa DASI ≤34 como capacidade funcional ruim."
        ),
        fields=[Field(name=key, label=f"{label} (+{weight:g})", type="boolean") for key, label, weight in _DASI_ITEMS],
        reference=(
            "Hlatky MA, Boineau RE, Higginbotham MB, et al. Am J Cardiol. 1989;64:651-654. "
            "PMID 2782256. DOI 10.1016/0002-9149(89)90496-7. Ponto de decisão perioperatório: "
            "2024 AHA/ACC Guideline, PMID 39316661, DOI 10.1161/CIR.0000000000001285."
        ),
        compute=_dasi,
        interpret=_dasi_txt,
        limitations=[
            "Autorrelato; limitações ortopédicas/neurológicas podem reduzir o escore sem refletir reserva cardiovascular isoladamente.",
            "Não diagnostica isquemia e não deve disparar teste de estresse automaticamente.",
            "Usar a pontuação DASI diretamente; conversões históricas para METs/VO2 não são necessárias para o ponto de decisão AHA/ACC 2024.",
        ],
    ),
    "aub-has2": Calculator(
        slug="aub-has2",
        name="AUB-HAS2 — Risco cardiovascular pré-operatório",
        theme="Perioperatório",
        purpose="Estratificar risco de morte, IAM ou AVC em 30 dias com seis critérios binários.",
        fields=[Field(name=key, label=label, type="boolean") for key, label in _AUB_HAS2_ITEMS],
        reference=(
            "Dakik HA, Chehab O, Eldirani M, et al. J Am Coll Cardiol. 2019;73(24):3067-3078. "
            "PMID 31221255. DOI 10.1016/j.jacc.2019.04.023."
        ),
        compute=_aub_has2,
        interpret=_aub_has2_txt,
        limitations=[
            "O desfecho do modelo é morte, IAM ou AVC em 30 dias; não é idêntico aos desfechos do RCRI ou Gupta MICA.",
            "Não indicar teste cardíaco apenas pela categoria do escore.",
            "Anemia é definida no modelo por hemoglobina <12 g/dL, independentemente do sexo.",
        ],
    ),
}
