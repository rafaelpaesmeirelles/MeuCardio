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
}



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
