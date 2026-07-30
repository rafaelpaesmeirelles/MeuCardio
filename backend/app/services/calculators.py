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



# ------------------------------------------------------------------- RCRI
# Índice de Lee — Lee TH et al. Circulation. 1999;100(10):1043-1049.
# PMID 10477528, DOI 10.1161/01.CIR.100.10.1043. Tabela de risco ORIGINAL do
# artigo (conferida contra o abstract em 30/07/2026) — não confundir com a
# reestimativa de Duceppe et al. 2017 (diretriz canadense), que usa outros
# percentuais e não é o escore de Lee na sua forma original.
_RCRI_FAIXAS = [
    (0, "0,5%", "0,4%"),
    (1, "1,3%", "0,9%"),
    (2, "4%", "7%"),
]
_RCRI_FAIXA_3_OU_MAIS = ("≥3", "9%", "11%")


def _rcri(d: dict) -> dict:
    criterios = [
        "cirurgia_alto_risco", "doenca_arterial_coronariana",
        "insuficiencia_cardiaca_congestiva", "doenca_cerebrovascular",
        "diabetes_insulinodependente", "creatinina_maior_2",
    ]
    score = sum(1 for c in criterios if d.get(c))
    if score <= 2:
        _, risco_derivacao, risco_validacao = _RCRI_FAIXAS[score]
        rotulo = str(score)
    else:
        rotulo, risco_derivacao, risco_validacao = _RCRI_FAIXA_3_OU_MAIS
    return {
        "score": score, "max": 6, "faixa": rotulo,
        "risco_coorte_derivacao": risco_derivacao,
        "risco_coorte_validacao": risco_validacao,
    }


def _rcri_txt(r: dict) -> str:
    return (
        f"{r['score']}/6 critérios (faixa {r['faixa']}). Risco de complicação cardíaca maior "
        f"(IAM, edema pulmonar, fibrilação ventricular/parada cardíaca, bloqueio "
        f"atrioventricular total): {r['risco_coorte_derivacao']} na coorte de derivação e "
        f"{r['risco_coorte_validacao']} na coorte de validação do artigo original de Lee et al. "
        "1999. O RCRI segue citado como ferramenta válida pelas diretrizes ESC/ESA 2022 e "
        "ACC/AHA 2024, que desde 2024 não elegem mais um único escore como referência — "
        "convive em pé de igualdade com o Gupta MICA e outras calculadoras validadas."
    )


# --------------------------------------------------------------------- DASI
# Duke Activity Status Index — Hlatky MA et al. Am J Cardiol. 1989;64(10):
# 651-654. PMID 2782256, DOI 10.1016/0002-9149(89)90496-7. Os 12 itens e pesos
# conferidos por duas fontes independentes (soma bate em 58,2, o máximo
# publicado do índice). Corte de 34 pontos: Wijeysundera DN et al. Br J
# Anaesth. 2020;124(3):261-270, PMID 31864719 (estudo METS) — não é do artigo
# de 1989, é o que a diretriz ACC/AHA 2024 usa para as três faixas abaixo.
_DASI_ITENS = [
    ("cuidar_de_si", "Cuidar de si mesmo (comer, vestir-se, tomar banho, usar o banheiro)", 2.75),
    ("caminhar_dentro_de_casa", "Caminhar dentro de casa", 1.75),
    ("caminhar_200m_plano", "Caminhar um ou dois quarteirões (~200 m) em terreno plano", 2.75),
    ("subir_um_lance_escada", "Subir um lance de escada ou caminhar em aclive", 5.50),
    ("correr_curta_distancia", "Correr uma curta distância", 8.00),
    ("trabalho_domestico_leve", "Trabalho doméstico leve (tirar pó, lavar louça)", 2.70),
    ("trabalho_domestico_moderado", "Trabalho doméstico moderado (aspirar, varrer, "
     "carregar compras)", 3.50),
    ("trabalho_domestico_pesado", "Trabalho doméstico pesado (esfregar chão, mover móveis)", 8.00),
    ("jardinagem", "Jardinagem, ancinho, capinar ou caminhar a 6,4 km/h", 4.50),
    ("relacoes_sexuais", "Relações sexuais", 5.25),
    ("recreacao_moderada", "Atividade recreativa moderada (golfe, boliche, dançar, "
     "duplas de tênis)", 6.00),
    ("esporte_extenuante", "Participar de esportes extenuantes (natação, tênis de "
     "simples, futebol, basquete, esqui)", 7.50),
]
_DASI_MAX = round(sum(peso for _, _, peso in _DASI_ITENS), 1)  # 58,2
DASI_CAMPOS = [chave for chave, _, _ in _DASI_ITENS]  # exportado p/ app/services/preop.py


def _dasi(d: dict) -> dict:
    score = round(sum(peso for chave, _, peso in _DASI_ITENS if d.get(chave)), 2)
    vo2_pico = 0.43 * score + 9.6
    mets = round(vo2_pico / 3.5, 1)
    faixa = "boa (>34)" if score > 34 else ("intermediária (25–34)" if score >= 25 else "reduzida (<25)")
    return {"score": score, "max": _DASI_MAX, "vo2_pico": round(vo2_pico, 1), "mets": mets, "faixa": faixa}


def _dasi_txt(r: dict) -> str:
    return (
        f"DASI {r['score']}/{r['max']} — capacidade funcional {r['faixa']}. VO2 de pico "
        f"estimado {r['vo2_pico']} mL/kg/min (~{r['mets']} METs), pela conversão "
        "VO2pico = 0,43 × DASI + 9,6 (usada por Wijeysundera et al. 2020/estudo METS — "
        "atribuição da fórmula ao artigo original de 1989 não confirmada em texto primário). "
        "As três faixas (<25 / 25–34 / >34) seguem o corte adotado pela diretriz ACC/AHA 2024, "
        "que passou a preferir o DASI estruturado à estimativa clínica subjetiva de METs — "
        "o mesmo caminho da ESC/ESAIC 2022."
    )


REGISTRY: dict[str, Calculator] = {
    "dasi": Calculator(
        slug="dasi",
        name="DASI (Duke Activity Status Index)",
        theme="Avaliação pré-operatória",
        purpose="Estimativa estruturada de capacidade funcional (substitui a estimativa "
                "clínica subjetiva de METs).",
        fields=[Field(chave, rotulo, "boolean") for chave, rotulo, _ in _DASI_ITENS],
        compute=_dasi,
        interpret=_dasi_txt,
        reference="Hlatky MA et al. Am J Cardiol. 1989;64(10):651-654. PMID 2782256.",
        limitations=[
            "A fórmula de conversão para VO2/METs vem de uso corrente na literatura "
            "perioperatória (estudo METS, Wijeysundera et al. 2020), não confirmada linha a "
            "linha contra o texto completo do artigo original de 1989.",
            "Autorrelato — não substitui teste de esforço quando este já está indicado por "
            "outro motivo clínico.",
        ],
    ),
    "rcri": Calculator(
        slug="rcri",
        name="RCRI (Índice de Lee)",
        theme="Avaliação pré-operatória",
        purpose="Risco de complicação cardíaca maior em cirurgia não-cardíaca eletiva.",
        fields=[
            Field("cirurgia_alto_risco", "Cirurgia de alto risco", "boolean",
                  help="Intraperitoneal, intratorácica ou vascular suprainguinal."),
            Field("doenca_arterial_coronariana", "História de doença arterial coronariana",
                  "boolean"),
            Field("insuficiencia_cardiaca_congestiva", "História de insuficiência cardíaca "
                  "congestiva", "boolean"),
            Field("doenca_cerebrovascular", "História de doença cerebrovascular (AVC ou AIT)",
                  "boolean"),
            Field("diabetes_insulinodependente", "Diabetes em tratamento pré-operatório com "
                  "insulina", "boolean"),
            Field("creatinina_maior_2", "Creatinina sérica pré-operatória > 2,0 mg/dL",
                  "boolean"),
        ],
        compute=_rcri,
        interpret=_rcri_txt,
        reference="Lee TH et al. Circulation. 1999;100(10):1043-1049. PMID 10477528.",
        limitations=[
            "Validado em pacientes ≥50 anos submetidos a cirurgia não-cardíaca eletiva maior; "
            "não valida cirurgia de emergência.",
            "A definição de \"cirurgia de alto risco\" do artigo original (intraperitoneal, "
            "intratorácica ou vascular suprainguinal) é a convenção consagrada na literatura "
            "subsequente — o abstract do artigo não a detalha por extenso.",
            "Desde a diretriz ACC/AHA 2024, o RCRI não é mais apresentado como escore único de "
            "referência — convive com o Gupta MICA e outras ferramentas validadas.",
        ],
    ),
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
