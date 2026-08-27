"""Registro de calculadoras clínicas.

Regra do projeto: nenhuma fórmula é implementada sem origem verificável.
Escores cujo coeficiente oficial não esteja confirmado ficam com
`status = "verificacao_humana_necessaria"` e NÃO são calculados.
"""

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class Field:
    name: str
    label: str
    type: str  # boolean | number | select
    unit: str | None = None
    options: list[dict] = field(default_factory=list)
    min: float | None = None
    max: float | None = None
    help: str | None = None
    required: bool = True


@dataclass
class Calculator:
    slug: str
    name: str
    theme: str
    purpose: str
    fields: list[Field]
    reference: str
    interpret: Callable[[Any], str] | None = None
    compute: Callable[[dict], dict] | None = None
    limitations: list[str] = field(default_factory=list)
    status: str = "implementada"
    # "escore": resultado é um número/classificação só (score/max, egfr etc.).
    # "dose": dose/taxa, agrupada no catálogo de dose e infusão. "assessment":
    # avaliação estruturada com múltiplos achados em prosa, fora do catálogo de
    # doses. O frontend renderiza "dose" e "assessment" como resultado composto.
    kind: str = "escore"


# -------------------------------------------------------------------- RCRI
def _rcri(d: dict) -> dict:
    keys = [
        "cirurgia_alto_risco", "cardiopatia_isquemica", "insuficiencia_cardiaca_congestiva",
        "doenca_cerebrovascular", "diabetes_em_uso_de_insulina", "creatinina_maior_2",
    ]
    score = sum(1 for k in keys if d.get(k))
    classe, evento_pct = (
        ("I", "0,4") if score == 0 else
        ("II", "0,9") if score == 1 else
        ("III", "7,0") if score == 2 else
        ("IV", "11,0")
    )
    return {"pontos": score, "classe": classe, "evento_pct": evento_pct}


def _rcri_txt(r: dict) -> str:
    return (
        f"{r['pontos']} ponto(s) — Classe {r['classe']} de risco, com taxa de evento cardíaco "
        f"grave (infarto, edema pulmonar, fibrilação ventricular/parada cardíaca ou bloqueio "
        f"AV total) de aproximadamente {r['evento_pct']}% na coorte original de derivação/"
        "validação. Não substitui a avaliação clínica global nem a capacidade funcional."
    )


# --------------------------------------------------------- Avaliação Pré-Operatória
# (função nova pedida pelo Rafael, 07/08/2026 — reúne conteúdo científico e as
# calculadoras validadas de risco cirúrgico numa função própria; ver
# `app/api/avaliacao_preoperatoria.py`)

_GUPTA_PROCEDIMENTOS = {
    "hernia": ("Hérnia", 0.0),
    "anorretal": ("Anorretal", -0.16),
    "aortica": ("Aórtica", 1.6),
    "bariatrica": ("Bariátrica", -0.25),
    "encefalica": ("Encefálica (neurocirurgia)", 1.4),
    "mama": ("Mama", -1.61),
    "cardiaca": ("Cardíaca", 1.01),
    "orl": ("Otorrinolaringológica", 0.71),
    "foregut_hpb": ("Trato gastrointestinal alto / hepatopancreatobiliar", 1.39),
    "vesicula_apendice_adrenal_baco": ("Vesícula biliar, apêndice, adrenal ou baço", 0.59),
    "intestinal": ("Intestinal", 1.14),
    "pescoco": ("Pescoço (tireoide/paratireoide)", 0.18),
    "obstetrica_ginecologica": ("Obstétrica ou ginecológica", 0.76),
    "ortopedica": ("Ortopédica não vertebral", 0.8),
    "abdome_outro": ("Abdominal, outra", 1.13),
    "vascular_periferica": ("Vascular periférica", 0.86),
    "pele": ("Pele/tecido subcutâneo", 0.54),
    "coluna": ("Coluna vertebral", 0.21),
    "toracica": ("Torácica não cardíaca", 0.4),
    "veias": ("Veias (varizes etc.)", -1.09),
    "urologia": ("Urológica", -0.26),
}


def _gupta_mica(d: dict) -> dict:
    idade = float(d["idade"])
    status_funcional = d["status_funcional"]  # independente | parcialmente_dependente | totalmente_dependente
    asa = int(d["asa"])
    creatinina_maior_1_5 = bool(d.get("creatinina_maior_1_5"))
    procedimento = d["tipo_procedimento"]

    coef_status = {"independente": 0.0, "parcialmente_dependente": 0.65, "totalmente_dependente": 1.03}[status_funcional]
    coef_asa = {1: -5.17, 2: -3.29, 3: -1.92, 4: -0.95, 5: 0.0}[asa]
    coef_creatinina = 0.61 if creatinina_maior_1_5 else 0.0
    nome_procedimento, coef_procedimento = _GUPTA_PROCEDIMENTOS[procedimento]

    x = idade * 0.02 + coef_status + coef_asa + coef_creatinina + coef_procedimento - 5.25
    risco = (2.718281828459045 ** x) / (1 + 2.718281828459045 ** x)
    return {"risco_pct": round(risco * 100, 2), "procedimento": nome_procedimento}


def _gupta_mica_txt(r: dict) -> str:
    faixa = "risco elevado — considerar avaliação/otimização perioperatória adicional" if r["risco_pct"] >= 1 else "risco baixo"
    return (
        f"Risco estimado de infarto do miocárdio ou parada cardíaca em até 30 dias: "
        f"{r['risco_pct']}% (procedimento: {r['procedimento']}) — {faixa} pelo corte de 1% "
        "usado na validação original."
    )


# ---------------------------------------------------------------- CHA2DS2-VASc
def _cha2ds2vasc(d: dict) -> dict:
    age = float(d["idade"])
    score = 0
    score += 1 if d.get("ic_disfuncao_ve") else 0
    score += 1 if d.get("hipertensao") else 0
    score += 2 if age >= 75 else (1 if 65 <= age <= 74 else 0)
    score += 1 if d.get("diabetes") else 0
    score += 2 if d.get("avc_ait_tromboembolismo") else 0
    score += 1 if d.get("doenca_vascular") else 0
    score += 1 if d.get("sexo") == "F" else 0
    return {"score": score, "max": 9}


def _cha2ds2vasc_txt(r: dict) -> str:
    return (
        f"Pontuação {r['score']}/9. O escore estratifica risco tromboembólico na fibrilação "
        "atrial não valvar. A decisão de anticoagular deve considerar o escore, o risco "
        "hemorrágico, preferência do paciente e a diretriz adotada pelo serviço — os pontos "
        "de corte diferem entre ESC, AHA/ACC/HRS e SBC."
    )


# -------------------------------------------------------------------- HAS-BLED
def _hasbled(d: dict) -> dict:
    keys = [
        "hipertensao_nao_controlada",
        "funcao_renal_alterada",
        "funcao_hepatica_alterada",
        "avc_previo",
        "sangramento_previo_ou_predisposicao",
        "inr_labil",
        "idade_maior_65",
        "farmacos_de_risco",
        "alcool",
    ]
    return {"score": sum(1 for k in keys if d.get(k)), "max": 9}


def _hasbled_txt(r: dict) -> str:
    return (
        f"Pontuação {r['score']}/9. Escore alto não contraindica anticoagulação: sinaliza "
        "fatores de risco hemorrágico modificáveis (PA, INR lábil, AINE/antiagregante, álcool) "
        "que devem ser corrigidos e reavaliados."
    )


# ---------------------------------------------------------------- CKD-EPI 2021
def _ckdepi2021(d: dict) -> dict:
    scr = float(d["creatinina"])
    age = float(d["idade"])
    female = d["sexo"] == "F"
    k = 0.7 if female else 0.9
    a = -0.241 if female else -0.302
    egfr = (
        142
        * (min(scr / k, 1) ** a)
        * (max(scr / k, 1) ** -1.200)
        * (0.9938**age)
        * (1.012 if female else 1)
    )
    return {"egfr": round(egfr, 1), "unidade": "mL/min/1,73 m²"}


def _ckdepi_txt(r: dict) -> str:
    e = r["egfr"]
    stage = (
        "G1 (≥90)" if e >= 90 else
        "G2 (60–89)" if e >= 60 else
        "G3a (45–59)" if e >= 45 else
        "G3b (30–44)" if e >= 30 else
        "G4 (15–29)" if e >= 15 else
        "G5 (<15)"
    )
    return (
        f"TFG estimada {e} mL/min/1,73 m² — categoria {stage} (KDIGO). Equação CKD-EPI 2021 "
        "sem coeficiente de raça. Para ajuste de dose de anticoagulantes orais diretos, "
        "a bula e os ensaios pivotais usam Cockcroft-Gault, não CKD-EPI."
    )


# ------------------------------------------------------------- Cockcroft-Gault
def _cockcroft(d: dict) -> dict:
    crcl = ((140 - float(d["idade"])) * float(d["peso"])) / (72 * float(d["creatinina"]))
    if d["sexo"] == "F":
        crcl *= 0.85
    return {"clearance": round(crcl, 1), "unidade": "mL/min"}


def _cockcroft_txt(r: dict) -> str:
    return (
        f"Clearance de creatinina estimado {r['clearance']} mL/min. É a equação usada nos "
        "ensaios pivotais e nas bulas dos anticoagulantes orais diretos para ajuste de dose. "
        "Perde acurácia em obesidade, caquexia e função renal instável."
    )


# ----------------------------------------------------------------- HEART score
def _heart(d: dict) -> dict:
    score = sum(int(d[k]) for k in ["historia", "ecg", "idade_pts", "fatores_risco", "troponina"])
    return {"score": score, "max": 10}


def _heart_txt(r: dict) -> str:
    return (
        f"Pontuação {r['score']}/10. Escore desenvolvido para dor torácica indiferenciada no "
        "pronto-socorro. A classificação de risco (baixo / intermediário / alto) e a conduta "
        "correspondente devem seguir o protocolo institucional de dor torácica."
    )


def _grace_pontos_age(v: float) -> int:
    faixas = [(30, 0), (40, 8), (50, 25), (60, 41), (70, 58), (80, 75), (90, 91)]
    for limite, pts in faixas:
        if v < limite:
            return pts
    return 100


def _grace_pontos_fc(v: float) -> int:
    faixas = [(50, 0), (70, 3), (90, 9), (110, 15), (150, 24), (200, 38)]
    for limite, pts in faixas:
        if v < limite:
            return pts
    return 46


def _grace_pontos_pas(v: float) -> int:
    # PAS baixa pontua mais (pior prognóstico) — ordem decrescente de propósito.
    faixas = [(80, 58), (100, 53), (120, 43), (140, 34), (160, 24), (200, 10)]
    for limite, pts in faixas:
        if v < limite:
            return pts
    return 0


def _grace_pontos_creatinina(v: float) -> int:
    faixas = [(0.40, 1), (0.80, 4), (1.20, 7), (1.60, 10), (2.00, 13), (4.00, 21)]
    for limite, pts in faixas:
        if v < limite:
            return pts
    return 28


_GRACE_KILLIP = {"I": 0, "II": 20, "III": 39, "IV": 59}

_GRACE_FAIXAS = {
    # (tipo_sca, horizonte) -> [(limite_superior_exclusivo, categoria, faixa_mortalidade)]
    ("nste", "hospitalar"): [
        (109, "baixo", "< 1%"), (141, "intermediário", "1–3%"), (None, "alto", "> 3%"),
    ],
    ("nste", "6_meses"): [
        (89, "baixo", "< 3%"), (119, "intermediário", "3–8%"), (None, "alto", "> 8%"),
    ],
    ("stemi", "hospitalar"): [
        (126, "baixo", "< 2%"), (155, "intermediário", "2–5%"), (None, "alto", "> 5%"),
    ],
    ("stemi", "6_meses"): [
        (100, "baixo", "< 4,5%"), (128, "intermediário", "4,5–11%"), (None, "alto", "> 11%"),
    ],
}


def _grace_categoria(pontos: int, tipo_sca: str, horizonte: str) -> tuple[str, str]:
    for limite, categoria, faixa in _GRACE_FAIXAS[(tipo_sca, horizonte)]:
        if limite is None or pontos < limite:
            return categoria, faixa
    raise AssertionError("faixa não coberta")  # inatingível — a última faixa é sempre None


def _grace(d: dict) -> dict:
    pontos = (
        _grace_pontos_age(float(d["idade"]))
        + _grace_pontos_fc(float(d["frequencia_cardiaca"]))
        + _grace_pontos_pas(float(d["pas"]))
        + _grace_pontos_creatinina(float(d["creatinina"]))
        + _GRACE_KILLIP[d["killip"]]
        + (39 if d.get("parada_cardiaca") else 0)
        + (28 if d.get("desvio_st") else 0)
        + (14 if d.get("marcadores_elevados") else 0)
    )
    tipo_sca = d["tipo_sca"]
    cat_hosp, faixa_hosp = _grace_categoria(pontos, tipo_sca, "hospitalar")
    cat_6m, faixa_6m = _grace_categoria(pontos, tipo_sca, "6_meses")
    return {
        "score": pontos, "max": 372,
        "categoria_hospitalar": cat_hosp, "mortalidade_hospitalar": faixa_hosp,
        "categoria_6_meses": cat_6m, "mortalidade_6_meses": faixa_6m,
    }


def _grace_txt(r: dict) -> str:
    return (
        f"{r['score']} pontos. Mortalidade hospitalar: risco {r['categoria_hospitalar']} "
        f"({r['mortalidade_hospitalar']}). Mortalidade em 6 meses: risco {r['categoria_6_meses']} "
        f"({r['mortalidade_6_meses']}). As faixas de risco vêm da tabela publicada — não são um "
        "percentual exato calculado por regressão contínua, que exigiria o nomograma original "
        "completo. Uma diferença de poucos pontos perto do limite de uma faixa não muda a "
        "conduta sozinha; use em conjunto com o quadro clínico."
    )


# ------------------------------------------------------ TIMI risk score UA/NSTEMI
# Fonte: Antman EM et al. The TIMI risk score for unstable angina/non-ST elevation
# MI. JAMA. 2000;284(7):835-842. Tabela 2 e Figura 2 (mortalidade/IAM/revascularização
# urgente em 14 dias por número de fatores de risco, coorte TIMI 11B).
_TIMI_UA_MORTALIDADE = {0: "4,7%", 1: "4,7%", 2: "8,3%", 3: "13,2%", 4: "19,9%",
                         5: "26,2%", 6: "40,9%", 7: "40,9%"}


def _timi_ua(d: dict) -> dict:
    keys = [
        "idade_maior_igual_65", "tres_ou_mais_fatores_risco_cad", "estenose_conhecida_50",
        "desvio_st", "angina_grave", "uso_aspirina_7_dias", "marcadores_elevados",
    ]
    score = sum(1 for k in keys if d.get(k))
    return {"score": score, "max": 7, "risco_14_dias": _TIMI_UA_MORTALIDADE[score]}


def _timi_ua_txt(r: dict) -> str:
    return (
        f"Pontuação {r['score']}/7. Risco de óbito, (re)infarto ou revascularização urgente "
        f"em 14 dias: {r['risco_14_dias']} (coorte de derivação/validação TIMI 11B, "
        "Antman et al. JAMA 2000). Escore validado para angina instável/IAM sem supra — "
        "não usar em IAM com supra de ST, que tem escore próprio (TIMI STEMI)."
    )


# --------------------------------------------------------- TIMI risk score STEMI
# Fonte: Morrow DA et al. TIMI Risk Score for ST-Elevation Myocardial Infarction.
# Circulation. 2000;102(17):2031-2037. Tabela 4 (pontuação) e Figura 3 (mortalidade
# em 30 dias por escore, coorte InTIME II, n=14.114).
_TIMI_STEMI_MORTALIDADE = [
    (0, "0,8%"), (1, "1,6%"), (2, "2,2%"), (3, "4,4%"), (4, "7,3%"),
    (5, "12,4%"), (6, "16,1%"), (7, "23,4%"), (8, "26,8%"),
]


def _timi_stemi_mortalidade(score: int) -> str:
    for pts, faixa in _TIMI_STEMI_MORTALIDADE:
        if score == pts:
            return faixa
    return "35,9%"  # >8 pontos


def _timi_stemi(d: dict) -> dict:
    age = float(d["idade"])
    pts_idade = 3 if age >= 75 else (2 if age >= 65 else 0)
    score = (
        pts_idade
        + (1 if d.get("diabetes_hipertensao_ou_angina") else 0)
        + (3 if d.get("pas_menor_100") else 0)
        + (2 if d.get("fc_maior_100") else 0)
        + (2 if d.get("killip_ii_iv") else 0)
        + (1 if d.get("peso_menor_67kg") else 0)
        + (1 if d.get("supra_anterior_ou_bre") else 0)
        + (1 if d.get("tempo_tratamento_maior_4h") else 0)
    )
    return {"score": score, "max": 14, "mortalidade_30_dias": _timi_stemi_mortalidade(score)}


def _timi_stemi_txt(r: dict) -> str:
    return (
        f"Pontuação {r['score']}/14. Mortalidade em 30 dias: {r['mortalidade_30_dias']} "
        "(coorte InTIME II, Morrow et al. Circulation 2000). Validado para IAM com supra de "
        "ST — usar o TIMI de UA/NSTEMI para síndrome coronariana sem supra."
    )


# ----------------------------------------------------------------- Wells — TEP
# Fonte: Wells PS et al. Thromb Haemost. 2000;83(3):416-420.
def _wells_pe(d: dict) -> dict:
    score = (
        (3.0 if d.get("sinais_clinicos_tvp") else 0)
        + (3.0 if d.get("diagnostico_alternativo_menos_provavel") else 0)
        + (1.5 if d.get("fc_maior_100") else 0)
        + (1.5 if d.get("imobilizacao_ou_cirurgia_4_semanas") else 0)
        + (1.5 if d.get("tep_tvp_previo") else 0)
        + (1.0 if d.get("hemoptise") else 0)
        + (1.0 if d.get("neoplasia") else 0)
    )
    categoria = "alto" if score > 6 else ("moderado" if score >= 2 else "baixo")
    dicotomico = "TEP provável" if score > 4 else "TEP improvável"
    return {"score": score, "categoria_3_niveis": categoria, "categoria_2_niveis": dicotomico}


def _wells_pe_txt(r: dict) -> str:
    return (
        f"Pontuação {r['score']:g}. Classificação de 3 níveis: probabilidade {r['categoria_3_niveis']}. "
        f"Classificação dicotômica (a mais usada na prática, com corte em 4): {r['categoria_2_niveis']}. "
        "'TEP improvável' com D-dímero negativo afasta TEP sem necessidade de imagem; "
        "'TEP provável' ou D-dímero positivo indica angiotomografia."
    )


# ----------------------------------------------------------------- Wells — TVP
# Fonte: Wells PS et al. Lancet. 1997;350(9094):1795-1798.
def _wells_dvt(d: dict) -> dict:
    keys = [
        "cancer_ativo", "paralisia_paresia_imobilizacao_gesso", "acamado_3_dias_ou_cirurgia_12_semanas",
        "dor_localizada_trajeto_venoso", "perna_toda_inchada", "panturrilha_maior_3cm",
        "edema_depressivel_perna_sintomatica", "veias_colaterais_superficiais", "tvp_previa_documentada",
    ]
    score = sum(1 for k in keys if d.get(k))
    if d.get("diagnostico_alternativo_tao_provavel_quanto_tvp"):
        score -= 2
    categoria = "alta" if score >= 3 else ("moderada" if score >= 1 else "baixa")
    dicotomico = "TVP provável" if score >= 2 else "TVP improvável"
    return {"score": score, "categoria_3_niveis": categoria, "categoria_2_niveis": dicotomico}


def _wells_dvt_txt(r: dict) -> str:
    return (
        f"Pontuação {r['score']}. Probabilidade pré-teste (3 níveis): {r['categoria_3_niveis']}. "
        f"Classificação dicotômica (corte em 2): {r['categoria_2_niveis']}. Combinar sempre com "
        "D-dímero e/ou ultrassonografia com compressão — não usar isoladamente."
    )


# ------------------------------------------------------- Genebra revisado (TEP)
# Fonte: Le Gal G et al. Ann Intern Med. 2006;144(3):165-171.
def _geneva_revisado(d: dict) -> dict:
    fc = float(d["frequencia_cardiaca"])
    pts_fc = 5 if fc >= 95 else (3 if fc >= 75 else 0)
    score = (
        (1 if d.get("idade_maior_65") else 0)
        + (3 if d.get("tvp_tep_previo") else 0)
        + (2 if d.get("cirurgia_ou_fratura_1_mes") else 0)
        + (2 if d.get("neoplasia_ativa") else 0)
        + (3 if d.get("dor_unilateral_mmii") else 0)
        + (2 if d.get("hemoptise") else 0)
        + pts_fc
        + (4 if d.get("dor_palpacao_profunda_e_edema_unilateral") else 0)
    )
    categoria = "alta" if score >= 11 else ("intermediária" if score >= 4 else "baixa")
    return {"score": score, "max": 22, "categoria": categoria}


def _geneva_revisado_txt(r: dict) -> str:
    return (
        f"Pontuação {r['score']}/22. Probabilidade clínica: {r['categoria']} "
        "(baixa 0-3: prevalência de TEP <10% na coorte de validação; intermediária 4-10: "
        "~20-30%; alta ≥11: ~74%). Le Gal et al., Ann Intern Med 2006."
    )


# ------------------------------------------------- Genebra simplificado (TEP)
# Fonte: Klok FA et al. Arch Intern Med. 2008;168(19):2131-2136 — mesmos 8 itens
# do Genebra revisado, cada um valendo 1 ponto, exceto FC ≥95 (2 pontos).
def _geneva_simplificado(d: dict) -> dict:
    fc = float(d["frequencia_cardiaca"])
    pts_fc = 2 if fc >= 95 else (1 if fc >= 75 else 0)
    score = (
        (1 if d.get("idade_maior_65") else 0)
        + (1 if d.get("tvp_tep_previo") else 0)
        + (1 if d.get("cirurgia_ou_fratura_1_mes") else 0)
        + (1 if d.get("neoplasia_ativa") else 0)
        + (1 if d.get("dor_unilateral_mmii") else 0)
        + (1 if d.get("hemoptise") else 0)
        + pts_fc
        + (1 if d.get("dor_palpacao_profunda_e_edema_unilateral") else 0)
    )
    categoria = "alta" if score >= 5 else ("intermediária" if score >= 2 else "baixa")
    dicotomico = "TEP provável" if score >= 3 else "TEP improvável"
    return {"score": score, "max": 9, "categoria_3_niveis": categoria, "categoria_2_niveis": dicotomico}


def _geneva_simplificado_txt(r: dict) -> str:
    return (
        f"Pontuação {r['score']}/9. Classificação de 3 níveis: {r['categoria_3_niveis']}. "
        f"Classificação dicotômica (corte em 3): {r['categoria_2_niveis']}. Klok et al., "
        "Arch Intern Med 2008 — versão simplificada do Genebra revisado, mesmos 8 critérios."
    )


# ----------------------------------------------------------------------- PESI
# Fonte: Aujesky D et al. Am J Respir Crit Care Med. 2005;172(8):1041-1046.
def _pesi(d: dict) -> dict:
    score = int(d["idade"])
    score += 10 if d.get("sexo") == "M" else 0
    score += 30 if d.get("cancer") else 0
    score += 10 if d.get("insuficiencia_cardiaca") else 0
    score += 10 if d.get("doenca_pulmonar_cronica") else 0
    score += 20 if d.get("fc_maior_igual_110") else 0
    score += 30 if d.get("pas_menor_100") else 0
    score += 20 if d.get("fr_maior_igual_30") else 0
    score += 20 if d.get("temperatura_menor_36") else 0
    score += 60 if d.get("alteracao_estado_mental") else 0
    score += 20 if d.get("saturacao_menor_90") else 0
    if score <= 65:
        classe, mortalidade = "I (muito baixo)", "0-1,6%"
    elif score <= 85:
        classe, mortalidade = "II (baixo)", "1,7-3,5%"
    elif score <= 105:
        classe, mortalidade = "III (intermediário)", "3,2-7,1%"
    elif score <= 125:
        classe, mortalidade = "IV (alto)", "4,0-11,4%"
    else:
        classe, mortalidade = "V (muito alto)", "10,0-24,5%"
    return {"score": score, "classe": classe, "mortalidade_30_dias_faixa": mortalidade}


def _pesi_txt(r: dict) -> str:
    return (
        f"Pontuação {r['score']} (idade em anos + pontos por variável). Classe {r['classe']} — "
        f"mortalidade em 30 dias na faixa de {r['mortalidade_30_dias_faixa']} nas coortes de "
        "derivação/validação. Classes I-II (baixo risco) são candidatas a tratamento "
        "ambulatorial em contexto clínico e social favorável. Aujesky et al. 2005."
    )


# ---------------------------------------------------------------------- sPESI
# Fonte: Jiménez D et al. Arch Intern Med. 2010;170(15):1383-1389.
def _spesi(d: dict) -> dict:
    keys = [
        "idade_maior_80", "cancer", "doenca_cardiopulmonar_cronica",
        "fc_maior_igual_110", "pas_menor_100", "saturacao_menor_90",
    ]
    score = sum(1 for k in keys if d.get(k))
    baixo_risco = score == 0
    return {"score": score, "risco": "baixo" if baixo_risco else "alto"}


def _spesi_txt(r: dict) -> str:
    return (
        f"Pontuação {r['score']}/6. Risco {r['risco']} — sPESI 0 pontos: mortalidade em 30 dias "
        "em torno de 1%; ≥1 ponto: em torno de 10,9% (coorte de validação, Jiménez et al. 2010). "
        "Versão simplificada do PESI original, mesma finalidade de identificar candidato a "
        "tratamento ambulatorial."
    )


# --------------------------------------------------------------------- CRUSADE
# Fonte: Subherwal S et al. Circulation. 2009;119(14):1873-1882. Table 4
# (algoritmo de pontuação) e texto (faixas de risco por quintil).
def _crusade_pontos_hct(v: float) -> int:
    if v < 31:
        return 9
    if v < 34:
        return 7
    if v < 37:
        return 3
    if v < 40:
        return 2
    return 0


def _crusade_pontos_crcl(v: float) -> int:
    v = min(v, 120)
    if v <= 15:
        return 39
    if v <= 30:
        return 35
    if v <= 60:
        return 28
    if v <= 90:
        return 17
    if v <= 120:
        return 7
    return 0


def _crusade_pontos_fc(v: float) -> int:
    v = max(v, 70)
    if v <= 70:
        return 0
    if v <= 80:
        return 1
    if v <= 90:
        return 3
    if v <= 100:
        return 6
    if v <= 110:
        return 8
    if v <= 120:
        return 10
    return 11


def _crusade_pontos_pas(v: float) -> int:
    if v <= 90:
        return 10
    if v <= 100:
        return 8
    if v <= 120:
        return 5
    if v <= 180:
        return 1
    if v <= 200:
        return 3
    return 5


def _crusade(d: dict) -> dict:
    score = (
        _crusade_pontos_hct(float(d["hematocrito"]))
        + _crusade_pontos_crcl(float(d["clearance_creatinina"]))
        + _crusade_pontos_fc(float(d["frequencia_cardiaca"]))
        + (8 if d.get("sexo") == "F" else 0)
        + (7 if d.get("sinais_chf") else 0)
        + (6 if d.get("doenca_vascular_previa") else 0)
        + (6 if d.get("diabetes") else 0)
        + _crusade_pontos_pas(float(d["pas"]))
    )
    if score <= 20:
        categoria = "muito baixo"
    elif score <= 30:
        categoria = "baixo"
    elif score <= 40:
        categoria = "moderado"
    elif score <= 50:
        categoria = "alto"
    else:
        categoria = "muito alto"
    return {"score": score, "max": 100, "categoria": categoria}


def _crusade_txt(r: dict) -> str:
    return (
        f"Pontuação {r['score']}/100. Risco de sangramento maior intra-hospitalar: "
        f"{r['categoria']} (muito baixo ≤20, baixo 21-30, moderado 31-40, alto 41-50, "
        "muito alto >50 — quintis da coorte de derivação, Subherwal et al. 2009). "
        "Clearance de creatinina pela fórmula de Cockcroft-Gault, não CKD-EPI."
    )


# ------------------------------------------------------------------ DAPT score
# Fonte: Yeh RW et al. JAMA. 2016;315(16):1735-1749.
def _dapt(d: dict) -> dict:
    age = float(d["idade"])
    pts_idade = -2 if age >= 75 else (-1 if age >= 65 else 0)
    score = (
        pts_idade
        + (1 if d.get("tabagismo_atual") else 0)
        + (1 if d.get("diabetes") else 0)
        + (1 if d.get("iam_na_apresentacao") else 0)
        + (1 if d.get("icp_ou_iam_previo") else 0)
        + (1 if d.get("diametro_stent_menor_3mm") else 0)
        + (1 if d.get("stent_paclitaxel") else 0)
        + (2 if d.get("ic_ou_feve_menor_30") else 0)
        + (2 if d.get("icp_em_enxerto_venoso") else 0)
    )
    beneficio = score >= 2
    return {"score": score, "min": -2, "max": 10, "favorece_dapt_prolongada": beneficio}


def _dapt_txt(r: dict) -> str:
    conduta = (
        "escore ≥2 — o benefício de isquemia reduzida da DAPT prolongada (>12 meses) tende a "
        "superar o risco de sangramento"
        if r["favorece_dapt_prolongada"] else
        "escore <2 — o risco de sangramento da DAPT prolongada tende a superar o benefício "
        "isquêmico; favorece duração padrão (12 meses)"
    )
    return (
        f"Pontuação {r['score']} (variando de -2 a 10). {conduta.capitalize()}. "
        "Aplicável a pacientes que completaram 12 meses de DAPT sem evento isquêmico ou "
        "hemorrágico maior, para decidir prolongar ou não. Yeh et al., JAMA 2016."
    )


# ---------------------------------------------------------------- ORBIT score
# Fonte: O'Brien EC et al. Eur Heart J. 2015;36(46):3258-3264.
def _orbit(d: dict) -> dict:
    score = (
        (1 if d.get("idade_maior_74") else 0)
        + (2 if d.get("hemoglobina_baixa_ou_anemia") else 0)
        + (2 if d.get("historia_sangramento") else 0)
        + (1 if d.get("tfg_menor_60") else 0)
        + (1 if d.get("uso_antiagregante") else 0)
    )
    if score <= 2:
        categoria = "baixo"
    elif score == 3:
        categoria = "médio"
    else:
        categoria = "alto"
    return {"score": score, "max": 7, "categoria": categoria}


def _orbit_txt(r: dict) -> str:
    return (
        f"Pontuação {r['score']}/7. Risco hemorrágico {r['categoria']} (baixo 0-2, médio 3, "
        "alto ≥4 — ORBIT-AF registry, O'Brien et al. 2015). Desenvolvido especificamente para "
        "fibrilação atrial em uso de anticoagulante oral; anemia definida por hemoglobina "
        "<13 g/dL (homem) ou <12 g/dL (mulher), ou hematócrito <40%/<36%, ou história de anemia."
    )


# --------------------------------------------------------------------- QTc
# Fórmulas clássicas de correção do QT pela frequência cardíaca. RR em segundos.
# Fontes: Bazett HC. Heart. 1920;7:353-70. · Fridericia LS. Acta Med Scand.
# 1920;53:469-86. · Sagie A et al. (Framingham). Am J Cardiol. 1992;70(7):797-801.
# · Hodges M et al. J Electrocardiol. 1983;16(1):17-24.
def _qtc(d: dict) -> dict:
    qt_ms = float(d["qt"])
    fc = float(d["frequencia_cardiaca"])
    rr_s = 60.0 / fc
    bazett = qt_ms / (rr_s**0.5)
    fridericia = qt_ms / (rr_s ** (1 / 3))
    framingham = qt_ms + 154 * (1 - rr_s)
    hodges = qt_ms + 1.75 * (fc - 60)
    return {
        "bazett": round(bazett, 1), "fridericia": round(fridericia, 1),
        "framingham": round(framingham, 1), "hodges": round(hodges, 1),
        "unidade": "ms",
    }


def _qtc_txt(r: dict) -> str:
    return (
        f"Bazett: {r['bazett']} ms · Fridericia: {r['fridericia']} ms · "
        f"Framingham: {r['framingham']} ms · Hodges: {r['hodges']} ms. Bazett superestima em "
        "frequências altas e subestima em frequências baixas — Fridericia e Framingham são "
        "geralmente preferidas fora da faixa de FC 60-100 bpm. QTc prolongado: geralmente "
        "≥450 ms (homem) ou ≥460 ms (mulher); ≥500 ms associa-se a maior risco de torsades."
    )



REGISTRY: dict[str, Calculator] = {
    "cha2ds2-vasc": Calculator(
        slug="cha2ds2-vasc",
        name="CHA₂DS₂-VASc",
        theme="Fibrilação atrial",
        purpose="Risco tromboembólico na fibrilação atrial não valvar.",
        fields=[
            Field("idade", "Idade", "number", "anos", min=0, max=120),
            Field("sexo", "Sexo", "select", options=[
                {"value": "M", "label": "Masculino"}, {"value": "F", "label": "Feminino"}]),
            Field("ic_disfuncao_ve", "Insuficiência cardíaca ou disfunção de VE", "boolean"),
            Field("hipertensao", "Hipertensão arterial", "boolean"),
            Field("diabetes", "Diabetes mellitus", "boolean"),
            Field("avc_ait_tromboembolismo", "AVC, AIT ou tromboembolismo prévio", "boolean"),
            Field("doenca_vascular", "Doença vascular (IAM prévio, DAP ou placa aórtica)",
                  "boolean"),
        ],
        compute=_cha2ds2vasc,
        interpret=_cha2ds2vasc_txt,
        reference="Lip GYH et al. Chest. 2010;137(2):263-72.",
        limitations=[
            "Validado para fibrilação atrial não valvar.",
            "Não se aplica a estenose mitral reumática moderada/grave ou prótese mecânica.",
        ],
    ),
    "has-bled": Calculator(
        slug="has-bled",
        name="HAS-BLED",
        theme="Fibrilação atrial",
        purpose="Risco hemorrágico em paciente anticoagulado.",
        fields=[
            Field("hipertensao_nao_controlada", "Hipertensão não controlada (PAS > 160 mmHg)",
                  "boolean"),
            Field("funcao_renal_alterada", "Função renal alterada", "boolean",
                  help="Diálise, transplante ou creatinina ≥ 2,26 mg/dL"),
            Field("funcao_hepatica_alterada", "Função hepática alterada", "boolean",
                  help="Cirrose ou bilirrubina > 2× e TGO/TGP/FA > 3× o normal"),
            Field("avc_previo", "AVC prévio", "boolean"),
            Field("sangramento_previo_ou_predisposicao", "Sangramento prévio ou predisposição",
                  "boolean"),
            Field("inr_labil", "INR lábil", "boolean", help="Apenas para varfarina; TTR < 60%"),
            Field("idade_maior_65", "Idade > 65 anos", "boolean"),
            Field("farmacos_de_risco", "Antiagregantes ou AINEs em uso", "boolean"),
            Field("alcool", "Consumo de álcool ≥ 8 doses/semana", "boolean"),
        ],
        compute=_hasbled,
        interpret=_hasbled_txt,
        reference="Pisters R et al. Chest. 2010;138(5):1093-100.",
        limitations=["O item INR lábil não se aplica a anticoagulantes orais diretos."],
    ),
    "ckd-epi-2021": Calculator(
        slug="ckd-epi-2021",
        name="CKD-EPI 2021 (TFG estimada)",
        theme="Função renal",
        purpose="Estimativa de taxa de filtração glomerular sem coeficiente de raça.",
        fields=[
            Field("creatinina", "Creatinina sérica", "number", "mg/dL", min=0.1, max=25),
            Field("idade", "Idade", "number", "anos", min=18, max=120),
            Field("sexo", "Sexo", "select", options=[
                {"value": "M", "label": "Masculino"}, {"value": "F", "label": "Feminino"}]),
        ],
        compute=_ckdepi2021,
        interpret=_ckdepi_txt,
        reference="Inker LA et al. N Engl J Med. 2021;385(19):1737-49.",
        limitations=[
            "Validada em adultos; não usar em menores de 18 anos.",
            "Não confiável em função renal instável (lesão renal aguda).",
        ],
    ),
    "cockcroft-gault": Calculator(
        slug="cockcroft-gault",
        name="Cockcroft-Gault (clearance de creatinina)",
        theme="Função renal",
        purpose="Ajuste de dose de fármacos, incluindo anticoagulantes orais diretos.",
        fields=[
            Field("idade", "Idade", "number", "anos", min=18, max=120),
            Field("peso", "Peso corporal", "number", "kg", min=20, max=300),
            Field("creatinina", "Creatinina sérica", "number", "mg/dL", min=0.1, max=25),
            Field("sexo", "Sexo", "select", options=[
                {"value": "M", "label": "Masculino"}, {"value": "F", "label": "Feminino"}]),
        ],
        compute=_cockcroft,
        interpret=_cockcroft_txt,
        reference="Cockcroft DW, Gault MH. Nephron. 1976;16(1):31-41.",
        limitations=["Superestima em obesidade; considerar peso ajustado conforme protocolo."],
    ),
    "heart": Calculator(
        slug="heart",
        name="HEART score",
        theme="Dor torácica",
        purpose="Estratificação de risco na dor torácica do pronto-socorro.",
        fields=[
            Field("historia", "História", "select", options=[
                {"value": 0, "label": "Pouco suspeita"},
                {"value": 1, "label": "Moderadamente suspeita"},
                {"value": 2, "label": "Altamente suspeita"}]),
            Field("ecg", "ECG", "select", options=[
                {"value": 0, "label": "Normal"},
                {"value": 1, "label": "Alteração inespecífica de repolarização"},
                {"value": 2, "label": "Desvio significativo do segmento ST"}]),
            Field("idade_pts", "Idade", "select", options=[
                {"value": 0, "label": "< 45 anos"},
                {"value": 1, "label": "45–64 anos"},
                {"value": 2, "label": "≥ 65 anos"}]),
            Field("fatores_risco", "Fatores de risco", "select", options=[
                {"value": 0, "label": "Nenhum"},
                {"value": 1, "label": "1 a 2 fatores"},
                {"value": 2, "label": "≥ 3 fatores ou aterosclerose conhecida"}]),
            Field("troponina", "Troponina", "select", options=[
                {"value": 0, "label": "≤ limite de referência"},
                {"value": 1, "label": "1 a 3× o limite"},
                {"value": 2, "label": "> 3× o limite"}]),
        ],
        compute=_heart,
        interpret=_heart_txt,
        reference="Six AJ et al. Neth Heart J. 2008;16(6):191-6.",
        limitations=[
            "Não se aplica a supradesnivelamento de ST ou instabilidade hemodinâmica.",
            "Desenvolvido com troponina convencional; protocolos com troponina "
            "ultrassensível usam algoritmos próprios.",
        ],
    ),
    "grace": Calculator(
        slug="grace",
        name="GRACE",
        theme="Síndrome coronariana aguda",
        purpose="Risco de mortalidade hospitalar e em 6 meses na SCA.",
        fields=[
            Field("idade", "Idade", "number", "anos", min=18, max=110),
            Field("frequencia_cardiaca", "Frequência cardíaca", "number", "bpm", min=20, max=300),
            Field("pas", "Pressão arterial sistólica", "number", "mmHg", min=50, max=300),
            Field("creatinina", "Creatinina sérica", "number", "mg/dL", min=0.1, max=15),
            Field("killip", "Classe de Killip", "select", options=[
                {"value": "I", "label": "I — sem sinais de IC"},
                {"value": "II", "label": "II — estertores ou turgência jugular"},
                {"value": "III", "label": "III — edema agudo de pulmão"},
                {"value": "IV", "label": "IV — choque cardiogênico"},
            ]),
            Field("parada_cardiaca", "Parada cardíaca na admissão", "boolean"),
            Field("desvio_st", "Desvio do segmento ST", "boolean"),
            Field("marcadores_elevados", "Marcadores cardíacos elevados", "boolean"),
            Field("tipo_sca", "Tipo de SCA", "select", options=[
                {"value": "nste", "label": "Sem supra de ST (SCASSST)"},
                {"value": "stemi", "label": "Com supra de ST (SCACSST/IAMCSST)"},
            ], help="As faixas de risco publicadas são diferentes para cada tipo de SCA."),
        ],
        compute=_grace,
        interpret=_grace_txt,
        reference=(
            "Fox KA, Dabbous OH, Goldberg RJ et al. Prediction of risk of death and myocardial "
            "infarction in the six months after presentation with acute coronary syndrome: "
            "prospective multinational observational study (GRACE). BMJ. 2006;333(7578):1091. "
            "Derivado de: Granger CB, Goldberg RJ, Dabbous O et al. Predictors of hospital "
            "mortality in the Global Registry of Acute Coronary Events. "
            "Arch Intern Med. 2003;163(19):2345-2353."
        ),
        limitations=[
            "As faixas de mortalidade vêm de categorias publicadas em tabela, não de um "
            "percentual contínuo por regressão — não dá o mesmo número que a calculadora "
            "oficial da GRACE (que usa o nomograma completo), mas a categoria de risco bate.",
            "Desenvolvido e validado em população adulta com síndrome coronariana aguda "
            "confirmada; não usar para dor torácica indiferenciada sem diagnóstico de SCA.",
            "Não incorpora variáveis adicionais de escores mais recentes (GRACE 2.0).",
        ],
    ),
    "timi-ua-nstemi": Calculator(
        slug="timi-ua-nstemi",
        name="TIMI (UA/NSTEMI)",
        theme="Síndrome coronariana aguda",
        purpose="Risco de morte, (re)infarto ou revascularização urgente em 14 dias na "
                "angina instável/IAM sem supra de ST.",
        fields=[
            Field("idade_maior_igual_65", "Idade ≥ 65 anos", "boolean"),
            Field("tres_ou_mais_fatores_risco_cad", "≥ 3 fatores de risco para DAC", "boolean",
                  help="História familiar, hipertensão, hipercolesterolemia, diabetes, tabagismo atual"),
            Field("estenose_conhecida_50", "Estenose coronariana conhecida ≥ 50%", "boolean"),
            Field("desvio_st", "Desvio do segmento ST ≥ 0,5 mm na admissão", "boolean"),
            Field("angina_grave", "≥ 2 episódios de angina em 24 horas", "boolean"),
            Field("uso_aspirina_7_dias", "Uso de AAS nos últimos 7 dias", "boolean"),
            Field("marcadores_elevados", "Marcadores cardíacos séricos elevados", "boolean"),
        ],
        compute=_timi_ua,
        interpret=_timi_ua_txt,
        reference="Antman EM et al. JAMA. 2000;284(7):835-842.",
        limitations=[
            "Validado para angina instável/IAM sem supra de ST — não usar em IAM com supra.",
            "Derivado das coortes TIMI 11B e ESSENCE, população selecionada de ensaio clínico.",
        ],
    ),
    "timi-stemi": Calculator(
        slug="timi-stemi",
        name="TIMI (STEMI)",
        theme="Síndrome coronariana aguda",
        purpose="Mortalidade em 30 dias no infarto agudo do miocárdio com supra de ST.",
        fields=[
            Field("idade", "Idade", "number", "anos", min=18, max=110),
            Field("diabetes_hipertensao_ou_angina", "Diabetes, hipertensão ou angina prévia", "boolean"),
            Field("pas_menor_100", "Pressão arterial sistólica < 100 mmHg", "boolean"),
            Field("fc_maior_100", "Frequência cardíaca > 100 bpm", "boolean"),
            Field("killip_ii_iv", "Classe de Killip II a IV", "boolean"),
            Field("peso_menor_67kg", "Peso < 67 kg", "boolean"),
            Field("supra_anterior_ou_bre", "Supra de ST em parede anterior ou BRE novo", "boolean"),
            Field("tempo_tratamento_maior_4h", "Tempo até o tratamento > 4 horas", "boolean"),
        ],
        compute=_timi_stemi,
        interpret=_timi_stemi_txt,
        reference="Morrow DA et al. Circulation. 2000;102(17):2031-2037.",
        limitations=[
            "Validado para IAM com supra de ST — não usar em SCA sem supra.",
            "Derivado da coorte InTIME II; validação mais recente existe (TIMI dinâmico) mas "
            "não é a mesma escala.",
        ],
    ),
    "wells-tep": Calculator(
        slug="wells-tep",
        name="Wells (TEP)",
        theme="Tromboembolismo",
        purpose="Probabilidade clínica pré-teste de tromboembolismo pulmonar.",
        fields=[
            Field("sinais_clinicos_tvp", "Sinais clínicos de TVP (edema + dor à palpação venosa)", "boolean"),
            Field("diagnostico_alternativo_menos_provavel", "Diagnóstico alternativo menos provável que TEP", "boolean"),
            Field("fc_maior_100", "Frequência cardíaca > 100 bpm", "boolean"),
            Field("imobilizacao_ou_cirurgia_4_semanas", "Imobilização ou cirurgia nas últimas 4 semanas", "boolean"),
            Field("tep_tvp_previo", "TEP ou TVP prévios", "boolean"),
            Field("hemoptise", "Hemoptise", "boolean"),
            Field("neoplasia", "Neoplasia (em tratamento, tratada nos últimos 6 meses ou paliativa)", "boolean"),
        ],
        compute=_wells_pe,
        interpret=_wells_pe_txt,
        reference="Wells PS et al. Thromb Haemost. 2000;83(3):416-420.",
        limitations=[
            "O item 'diagnóstico alternativo menos provável' depende de julgamento clínico, "
            "não de critério objetivo — variabilidade entre avaliadores é esperada.",
            "Sempre combinar com D-dímero e/ou exame de imagem; não usar isoladamente.",
        ],
    ),
    "wells-tvp": Calculator(
        slug="wells-tvp",
        name="Wells (TVP)",
        theme="Tromboembolismo",
        purpose="Probabilidade clínica pré-teste de trombose venosa profunda de membro inferior.",
        fields=[
            Field("cancer_ativo", "Câncer ativo (tratamento em curso, últimos 6 meses ou paliativo)", "boolean"),
            Field("paralisia_paresia_imobilizacao_gesso", "Paralisia, paresia ou imobilização gessada recente", "boolean"),
            Field("acamado_3_dias_ou_cirurgia_12_semanas", "Acamado ≥ 3 dias ou cirurgia grande nas últimas 12 semanas", "boolean"),
            Field("dor_localizada_trajeto_venoso", "Dor localizada no trajeto do sistema venoso profundo", "boolean"),
            Field("perna_toda_inchada", "Perna toda inchada", "boolean"),
            Field("panturrilha_maior_3cm", "Panturrilha sintomática > 3 cm maior que a assintomática", "boolean"),
            Field("edema_depressivel_perna_sintomatica", "Edema depressível confinado à perna sintomática", "boolean"),
            Field("veias_colaterais_superficiais", "Veias colaterais superficiais não varicosas", "boolean"),
            Field("tvp_previa_documentada", "TVP previamente documentada", "boolean"),
            Field("diagnostico_alternativo_tao_provavel_quanto_tvp", "Diagnóstico alternativo tão ou mais provável que TVP", "boolean"),
        ],
        compute=_wells_dvt,
        interpret=_wells_dvt_txt,
        reference="Wells PS et al. Lancet. 1997;350(9094):1795-1798.",
        limitations=[
            "O item de diagnóstico alternativo subtrai 2 pontos e depende de julgamento clínico.",
            "Sempre combinar com D-dímero e/ou ultrassonografia com compressão.",
        ],
    ),
    "geneva-revisado": Calculator(
        slug="geneva-revisado",
        name="Genebra revisado",
        theme="Tromboembolismo",
        purpose="Probabilidade clínica de TEP com critérios inteiramente objetivos (sem julgamento subjetivo).",
        fields=[
            Field("idade_maior_65", "Idade > 65 anos", "boolean"),
            Field("tvp_tep_previo", "TVP ou TEP prévios", "boolean"),
            Field("cirurgia_ou_fratura_1_mes", "Cirurgia ou fratura no último mês", "boolean"),
            Field("neoplasia_ativa", "Neoplasia ativa", "boolean"),
            Field("dor_unilateral_mmii", "Dor unilateral em membro inferior", "boolean"),
            Field("hemoptise", "Hemoptise", "boolean"),
            Field("frequencia_cardiaca", "Frequência cardíaca", "number", "bpm", min=30, max=250),
            Field("dor_palpacao_profunda_e_edema_unilateral", "Dor à palpação venosa profunda E edema unilateral", "boolean"),
        ],
        compute=_geneva_revisado,
        interpret=_geneva_revisado_txt,
        reference="Le Gal G et al. Ann Intern Med. 2006;144(3):165-171.",
        limitations=[
            "Diferente do Wells, todos os itens são objetivos — útil quando se quer reduzir "
            "variabilidade entre avaliadores.",
            "Sempre combinar com D-dímero e/ou exame de imagem.",
        ],
    ),
    "geneva-simplificado": Calculator(
        slug="geneva-simplificado",
        name="Genebra simplificado",
        theme="Tromboembolismo",
        purpose="Versão simplificada do Genebra revisado, mesmos critérios com pontuação uniforme.",
        fields=[
            Field("idade_maior_65", "Idade > 65 anos", "boolean"),
            Field("tvp_tep_previo", "TVP ou TEP prévios", "boolean"),
            Field("cirurgia_ou_fratura_1_mes", "Cirurgia ou fratura no último mês", "boolean"),
            Field("neoplasia_ativa", "Neoplasia ativa", "boolean"),
            Field("dor_unilateral_mmii", "Dor unilateral em membro inferior", "boolean"),
            Field("hemoptise", "Hemoptise", "boolean"),
            Field("frequencia_cardiaca", "Frequência cardíaca", "number", "bpm", min=30, max=250),
            Field("dor_palpacao_profunda_e_edema_unilateral", "Dor à palpação venosa profunda E edema unilateral", "boolean"),
        ],
        compute=_geneva_simplificado,
        interpret=_geneva_simplificado_txt,
        reference="Klok FA et al. Arch Intern Med. 2008;168(19):2131-2136.",
        limitations=[
            "Mesmos 8 critérios do Genebra revisado, com pontuação uniforme (1 ponto cada, "
            "exceto FC ≥95 bpm com 2 pontos) — não confundir os dois totais.",
        ],
    ),
    "pesi": Calculator(
        slug="pesi",
        name="PESI",
        theme="Tromboembolismo",
        purpose="Estratificação de gravidade/mortalidade do TEP agudo já diagnosticado.",
        fields=[
            Field("idade", "Idade", "number", "anos", min=18, max=110),
            Field("sexo", "Sexo", "select", options=[
                {"value": "M", "label": "Masculino"}, {"value": "F", "label": "Feminino"}]),
            Field("cancer", "Câncer", "boolean"),
            Field("insuficiencia_cardiaca", "Insuficiência cardíaca", "boolean"),
            Field("doenca_pulmonar_cronica", "Doença pulmonar crônica", "boolean"),
            Field("fc_maior_igual_110", "Frequência cardíaca ≥ 110 bpm", "boolean"),
            Field("pas_menor_100", "Pressão arterial sistólica < 100 mmHg", "boolean"),
            Field("fr_maior_igual_30", "Frequência respiratória ≥ 30/min", "boolean"),
            Field("temperatura_menor_36", "Temperatura < 36°C", "boolean"),
            Field("alteracao_estado_mental", "Alteração do estado mental", "boolean"),
            Field("saturacao_menor_90", "Saturação de O₂ < 90%", "boolean"),
        ],
        compute=_pesi,
        interpret=_pesi_txt,
        reference="Aujesky D et al. Am J Respir Crit Care Med. 2005;172(8):1041-1046.",
        limitations=[
            "Diferente de escores de PROBABILIDADE diagnóstica (Wells, Genebra) — o PESI "
            "pressupõe TEP já confirmado e estima prognóstico, não probabilidade diagnóstica.",
            "Não substitui avaliação de disfunção de VD (biomarcador/imagem) na estratificação "
            "completa de risco do TEP.",
        ],
    ),
    "spesi": Calculator(
        slug="spesi",
        name="sPESI (simplificado)",
        theme="Tromboembolismo",
        purpose="Versão simplificada do PESI para triagem rápida de candidato a tratamento ambulatorial do TEP.",
        fields=[
            Field("idade_maior_80", "Idade > 80 anos", "boolean"),
            Field("cancer", "Câncer", "boolean"),
            Field("doenca_cardiopulmonar_cronica", "Doença cardiopulmonar crônica", "boolean"),
            Field("fc_maior_igual_110", "Frequência cardíaca ≥ 110 bpm", "boolean"),
            Field("pas_menor_100", "Pressão arterial sistólica < 100 mmHg", "boolean"),
            Field("saturacao_menor_90", "Saturação de O₂ < 90%", "boolean"),
        ],
        compute=_spesi,
        interpret=_spesi_txt,
        reference="Jiménez D et al. Arch Intern Med. 2010;170(15):1383-1389.",
        limitations=[
            "0 pontos não significa ausência de qualquer risco — significa risco baixo o "
            "suficiente, na coorte de validação, para considerar tratamento ambulatorial.",
            "Não substitui avaliação de disfunção de VD quando disponível.",
        ],
    ),
    "crusade": Calculator(
        slug="crusade",
        name="CRUSADE",
        theme="Síndrome coronariana aguda",
        purpose="Risco de sangramento maior intra-hospitalar na síndrome coronariana sem supra de ST.",
        fields=[
            Field("hematocrito", "Hematócrito basal", "number", "%", min=10, max=60),
            Field("clearance_creatinina", "Clearance de creatinina (Cockcroft-Gault)", "number", "mL/min", min=1, max=200),
            Field("frequencia_cardiaca", "Frequência cardíaca", "number", "bpm", min=20, max=250),
            Field("sexo", "Sexo", "select", options=[
                {"value": "M", "label": "Masculino"}, {"value": "F", "label": "Feminino"}]),
            Field("sinais_chf", "Sinais de insuficiência cardíaca na apresentação", "boolean"),
            Field("doenca_vascular_previa", "Doença vascular prévia (AVC ou DAP)", "boolean"),
            Field("diabetes", "Diabetes mellitus", "boolean"),
            Field("pas", "Pressão arterial sistólica", "number", "mmHg", min=40, max=300),
        ],
        compute=_crusade,
        interpret=_crusade_txt,
        reference="Subherwal S et al. Circulation. 2009;119(14):1873-1882.",
        limitations=[
            "Usa especificamente a fórmula de Cockcroft-Gault para clearance de creatinina, "
            "não CKD-EPI — usar a calculadora de Cockcroft-Gault desta base antes.",
            "Desenvolvido e validado em síndrome coronariana SEM supra de ST.",
        ],
    ),
    "dapt-score": Calculator(
        slug="dapt-score",
        name="DAPT score",
        theme="Farmacologia",
        purpose="Decisão de prolongar (>12 meses) ou não a dupla antiagregação após angioplastia coronariana.",
        fields=[
            Field("idade", "Idade", "number", "anos", min=18, max=110),
            Field("tabagismo_atual", "Tabagismo atual", "boolean"),
            Field("diabetes", "Diabetes mellitus", "boolean"),
            Field("iam_na_apresentacao", "IAM na apresentação do procedimento índice", "boolean"),
            Field("icp_ou_iam_previo", "ICP ou IAM prévios", "boolean"),
            Field("diametro_stent_menor_3mm", "Diâmetro do stent < 3 mm", "boolean"),
            Field("stent_paclitaxel", "Stent farmacológico com paclitaxel", "boolean"),
            Field("ic_ou_feve_menor_30", "Insuficiência cardíaca ou FEVE < 30%", "boolean"),
            Field("icp_em_enxerto_venoso", "ICP em enxerto venoso safena", "boolean"),
        ],
        compute=_dapt,
        interpret=_dapt_txt,
        reference="Yeh RW et al. JAMA. 2016;315(16):1735-1749.",
        limitations=[
            "Aplicável só a quem completou 12 meses de DAPT sem sangramento maior nem evento "
            "isquêmico — não é ferramenta para decidir a duração inicial da DAPT.",
            "Derivado majoritariamente de população com stent farmacológico de 1ª/2ª geração; "
            "aplicação a stents mais recentes exige julgamento clínico adicional.",
        ],
    ),
    "orbit": Calculator(
        slug="orbit",
        name="ORBIT",
        theme="Fibrilação atrial",
        purpose="Risco hemorrágico em paciente anticoagulado por fibrilação atrial — alternativa ao HAS-BLED.",
        fields=[
            Field("idade_maior_74", "Idade > 74 anos", "boolean"),
            Field("hemoglobina_baixa_ou_anemia", "Hemoglobina baixa ou história de anemia", "boolean",
                  help="Hb < 13 g/dL (homem) ou < 12 g/dL (mulher), ou Ht < 40%/36%, ou anemia conhecida"),
            Field("historia_sangramento", "História de sangramento", "boolean"),
            Field("tfg_menor_60", "TFG estimada < 60 mL/min/1,73 m²", "boolean"),
            Field("uso_antiagregante", "Uso concomitante de antiagregante plaquetário", "boolean"),
        ],
        compute=_orbit,
        interpret=_orbit_txt,
        reference="O'Brien EC et al. Eur Heart J. 2015;36(46):3258-3264.",
        limitations=[
            "Desenvolvido especificamente para fibrilação atrial em anticoagulante oral — não "
            "validado para outras indicações de anticoagulação.",
            "Derivado do registro ORBIT-AF, predominantemente pacientes em uso de varfarina; "
            "desempenho em DOAC foi avaliado em coortes de validação posteriores, não na "
            "derivação original.",
        ],
    ),
    "qtc": Calculator(
        slug="qtc",
        name="QTc (Bazett/Fridericia/Framingham/Hodges)",
        theme="Farmacologia",
        purpose="Correção do intervalo QT pela frequência cardíaca, por quatro fórmulas clássicas.",
        fields=[
            Field("qt", "Intervalo QT medido", "number", "ms", min=200, max=800),
            Field("frequencia_cardiaca", "Frequência cardíaca", "number", "bpm", min=20, max=250),
        ],
        compute=_qtc,
        interpret=_qtc_txt,
        reference=(
            "Bazett HC. Heart. 1920;7:353-370. · Fridericia LS. Acta Med Scand. 1920;53:469-486. "
            "· Sagie A et al. Am J Cardiol. 1992;70(7):797-801 (fórmula de Framingham). "
            "· Hodges M et al. J Electrocardiol. 1983;16(1):17-24."
        ),
        limitations=[
            "Bazett (a mais usada na prática) superestima o QTc em frequências altas e "
            "subestima em frequências baixas — fora da faixa de 60-100 bpm, prefira "
            "Fridericia ou Framingham.",
            "Nenhuma fórmula substitui medição cuidadosa do QT (derivação II ou V5, batimento "
            "sem onda U proeminente sobreposta).",
        ],
    ),
    "rcri": Calculator(
        slug="rcri",
        name="RCRI — Índice de Risco Cardíaco Revisado (Lee)",
        theme="Perioperatório",
        purpose="Risco de evento cardíaco grave em cirurgia não cardíaca — 6 critérios, 1 ponto cada.",
        fields=[
            Field("cirurgia_alto_risco", "Cirurgia de alto risco", "boolean",
                  help="Intraperitoneal, intratorácica ou vascular suprainguinal."),
            Field("cardiopatia_isquemica", "Cardiopatia isquêmica", "boolean",
                  help="IAM prévio, teste de esforço positivo, angina, uso de nitrato ou onda Q no ECG."),
            Field("insuficiencia_cardiaca_congestiva", "Insuficiência cardíaca congestiva", "boolean"),
            Field("doenca_cerebrovascular", "Doença cerebrovascular", "boolean", help="AVC ou AIT prévio."),
            Field("diabetes_em_uso_de_insulina", "Diabetes em uso de insulina", "boolean"),
            Field("creatinina_maior_2", "Creatinina sérica pré-operatória > 2,0 mg/dL", "boolean"),
        ],
        compute=_rcri,
        interpret=_rcri_txt,
        reference="Lee TH et al. Derivation and prospective validation of a simple index for prediction of cardiac risk of major noncardiac surgery. Circulation. 1999;100(10):1043-1049.",
        limitations=[
            "Validado para cirurgia não cardíaca eletiva/urgência em adultos — desempenho inferior "
            "ao Gupta MICA em coortes ACS-NSQIP mais recentes, sobretudo em pacientes de baixo risco.",
            "Não incorpora capacidade funcional (METs) nem idade como variáveis contínuas.",
        ],
    ),
    "gupta-mica": Calculator(
        slug="gupta-mica",
        name="Gupta MICA — risco de infarto ou parada cardíaca perioperatória",
        theme="Perioperatório",
        purpose="Risco percentual individualizado de IAM ou PCR em até 30 dias após cirurgia não cardíaca.",
        fields=[
            Field("idade", "Idade", "number", "anos", min=18, max=110),
            Field("status_funcional", "Status funcional", "select", options=[
                {"value": "independente", "label": "Independente para atividades da vida diária"},
                {"value": "parcialmente_dependente", "label": "Parcialmente dependente"},
                {"value": "totalmente_dependente", "label": "Totalmente dependente"},
            ]),
            Field("asa", "Classe ASA", "select", options=[
                {"value": 1, "label": "ASA I — saudável"},
                {"value": 2, "label": "ASA II — doença sistêmica leve"},
                {"value": 3, "label": "ASA III — doença sistêmica grave"},
                {"value": 4, "label": "ASA IV — doença sistêmica grave, ameaça constante à vida"},
                {"value": 5, "label": "ASA V — moribundo, sobrevida improvável sem a cirurgia"},
            ]),
            Field("creatinina_maior_1_5", "Creatinina sérica pré-operatória > 1,5 mg/dL", "boolean"),
            Field("tipo_procedimento", "Tipo de procedimento cirúrgico", "select", options=[
                {"value": k, "label": v[0]} for k, v in _GUPTA_PROCEDIMENTOS.items()
            ]),
        ],
        compute=_gupta_mica,
        interpret=_gupta_mica_txt,
        reference=(
            "Gupta PK et al. Development and validation of a risk calculator for prediction of "
            "cardiac risk after surgery. Circulation. 2011;124(4):381-387. Coeficientes conferidos "
            "contra duas calculadoras de terceiros que reproduzem a tabela original "
            "(omnicalculator.com/health/mica e mdapp.co), convergentes em status funcional, classe "
            "ASA, creatinina e nos coeficientes de procedimento verificados em ambas as fontes."
        ),
        limitations=[
            "Coeficiente de cada procedimento vem da categoria mais próxima da lista original "
            "ACS-NSQIP — procedimento não listado aqui deve ser aproximado pelo tipo mais "
            "semelhante, com julgamento clínico.",
            "Desenvolvido e validado em cirurgia não cardíaca; não usar para cirurgia cardíaca "
            "eletiva (a categoria 'Cardíaca' aqui refere-se a procedimentos card­íacos dentro do "
            "escopo NSQIP geral, não à cirurgia cardíaca de rotina avaliada por outros escores).",
            "Desempenho superior ao RCRI em coortes de validação (estatística C 0,87 vs 0,75), "
            "mas ainda é estimativa populacional — não substitui julgamento clínico individual.",
        ],
    ),
}

# Calculadora de Doses Cardiológicas (pedido do Rafael, 07/08/2026) — módulo
# separado por serem calculadoras de DOSE, não de escore/risco; importado no
# fim do arquivo porque `dose_calculators.py` importa `Calculator`/`Field`
# daqui, e essas duas classes já existem no namespace do módulo neste ponto.
from .dose_calculators import DOSE_REGISTRY  # noqa: E402

REGISTRY.update(DOSE_REGISTRY)


def run(slug: str, payload: dict) -> dict:
    calc = REGISTRY.get(slug)
    if calc is None:
        raise KeyError(slug)
    if calc.status != "implementada" or calc.compute is None:
        raise ValueError(
            "Calculadora ainda não liberada: aguarda validação dos coeficientes oficiais."
        )
    result = calc.compute(payload)
    return {
        "slug": calc.slug,
        "name": calc.name,
        "result": result,
        "interpretation": calc.interpret(result) if calc.interpret else None,
        "reference": calc.reference,
        "limitations": calc.limitations,
    }
