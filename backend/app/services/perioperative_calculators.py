"""Calculadoras perioperatórias adicionais produzidas pelo ChatGPT.

Governança: somente fórmulas/itens explicitamente verificáveis em fonte primária
ou diretriz foram implementados. GSCRI permanece sem cálculo porque a regressão
completa não foi validada nesta sessão contra a fonte primária; ACS-NSQIP deve
usar o calculador oficial dinâmico.

Fonte: ChatGPT
"""

from __future__ import annotations

from app.services.calculators import Calculator, Field


# ---------------------------------------------------------------------- DASI
# Hlatky MA et al. Am J Cardiol. 1989;64(10):651-654.
# PMID: 2782256. DOI: 10.1016/0002-9149(89)90496-7.
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


# -------------------------------------------------------------------- VSG-CRI
# Bertges DJ et al. J Vasc Surg. 2010;52(3):674-683.e1-3.
# PMID: 20570467. DOI: 10.1016/j.jvs.2010.03.031.
# Pontuação reproduzida também na Diretriz SBC 2024, Tabelas 6 e 7.
def _vsg_cri(d: dict) -> dict:
    idade = float(d["idade"])
    if idade >= 80:
        score = 4
    elif idade >= 70:
        score = 3
    elif idade >= 60:
        score = 2
    else:
        score = 0

    score += 2 if d.get("doenca_arterial_coronariana") else 0
    score += 2 if d.get("insuficiencia_cardiaca") else 0
    score += 2 if d.get("dpoc") else 0
    score += 2 if d.get("creatinina_maior_1_8") else 0
    score += 1 if d.get("tabagismo") else 0
    score += 1 if d.get("diabetes_insulina") else 0
    score += 1 if d.get("betabloqueador_cronico") else 0
    score -= 1 if d.get("revascularizacao_coronaria_previa") else 0

    categoria = "baixo" if score <= 4 else ("intermediario" if score <= 6 else "alto")
    if score <= 3:
        evento_original_pct = 2.6
    elif score == 4:
        evento_original_pct = 3.5
    elif score == 5:
        evento_original_pct = 6.0
    elif score == 6:
        evento_original_pct = 6.6
    elif score == 7:
        evento_original_pct = 8.9
    else:
        evento_original_pct = 14.3
    return {
        "score": score,
        "categoria": categoria,
        "evento_original_pct": evento_original_pct,
    }


def _vsg_cri_txt(r: dict) -> str:
    return (
        f"VSG-CRI {r['score']} ponto(s) — risco {r['categoria']} pela classificação adotada pela "
        f"SBC 2024 (0–4 baixo, 5–6 intermediário, ≥7 alto). Na coorte original, a faixa correspondente "
        f"teve taxa de complicações cardíacas de aproximadamente {r['evento_original_pct']}%. "
        "Essas taxas históricas não equivalem a probabilidade individual contemporânea e o escore "
        "deve ser usado especificamente em cirurgia vascular arterial."
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
    "vsg-cri": Calculator(
        slug="vsg-cri",
        name="VSG-CRI — Cirurgia vascular arterial",
        theme="Perioperatório",
        purpose="Estratificar complicações cardíacas em pacientes submetidos a cirurgia vascular arterial.",
        fields=[
            Field(name="idade", label="Idade", type="number", unit="anos", min=18, max=120),
            Field(name="doenca_arterial_coronariana", label="Doença arterial coronariana", type="boolean"),
            Field(name="insuficiencia_cardiaca", label="Insuficiência cardíaca", type="boolean"),
            Field(name="dpoc", label="DPOC", type="boolean"),
            Field(name="creatinina_maior_1_8", label="Creatinina >1,8 mg/dL", type="boolean"),
            Field(name="tabagismo", label="Tabagismo atual ou prévio conforme variável do modelo", type="boolean"),
            Field(name="diabetes_insulina", label="Diabetes em uso de insulina", type="boolean"),
            Field(name="betabloqueador_cronico", label="Uso crônico de betabloqueador", type="boolean"),
            Field(name="revascularizacao_coronaria_previa", label="Revascularização coronária prévia (CABG/PCI) — −1 ponto", type="boolean"),
        ],
        reference=(
            "Bertges DJ, Goodney PP, Zhao Y, et al. J Vasc Surg. 2010;52(3):674-683.e1-3. "
            "PMID 20570467. DOI 10.1016/j.jvs.2010.03.031. Classificação operacional: "
            "Diretriz SBC 2024, DOI 10.36660/abc.20240590."
        ),
        compute=_vsg_cri,
        interpret=_vsg_cri_txt,
        limitations=[
            "Usar especificamente em cirurgia vascular arterial; não extrapolar para cirurgia não vascular.",
            "As taxas absolutas de evento são da coorte original e podem não refletir risco contemporâneo individual.",
            "Uso crônico de betabloqueador é variável prognóstica do modelo e não implica causalidade.",
        ],
    ),
}
