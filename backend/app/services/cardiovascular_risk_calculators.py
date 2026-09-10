"""Framingham 2008 general CVD risk: independently implemented published equations.

Primary source and coefficient tables:
https://www.framinghamheartstudy.org/fhs-for-researchers/fhs-risk-functions/cardiovascular-disease-10-year-risk/
D'Agostino et al. Circulation 2008;117:743-753. DOI 10.1161/CIRCULATIONAHA.107.699579.
No spreadsheet, source implementation, or copyrighted explanatory text is bundled.
"""
from __future__ import annotations

import math
import re

from app.services.calculators import Calculator, Field

SOURCE_URL = (
    "https://www.framinghamheartstudy.org/fhs-for-researchers/"
    "fhs-risk-functions/cardiovascular-disease-10-year-risk/"
)
REFERENCE = (
    "D'Agostino RB et al. General cardiovascular risk profile for use in primary care. "
    "Circulation. 2008;117:743–753. DOI: 10.1161/CIRCULATIONAHA.107.699579. "
    "Coeficientes e sobrevivência basal: " + SOURCE_URL
)
ENDPOINT = (
    "doença cardiovascular global: morte coronariana, infarto, insuficiência coronariana, "
    "angina, AVC isquêmico ou hemorrágico, AIT, doença arterial periférica e insuficiência cardíaca"
)
# Published order: ln(age), ln(TC or BMI), ln(HDL, lipids only),
# ln(SBP untreated), ln(SBP treated), smoker, diabetes, mean, S0(10).
_LIPIDS = {
    "M": (3.06117, 1.12370, -0.93263, 1.93303, 1.99881, 0.65451, 0.57367, 23.9802, 0.88936),
    "F": (2.32888, 1.20904, -0.70833, 2.76157, 2.82263, 0.52873, 0.69154, 26.1931, 0.95012),
}
_BMI = {
    "M": (3.11296, 0.79277, 0.0, 1.85508, 1.92672, 0.70953, 0.53160, 23.9388, 0.88431),
    "F": (2.72107, 0.51125, 0.0, 2.81291, 2.88267, 0.61868, 0.77763, 26.0145, 0.94833),
}
# Operational input safeguards, NOT a claim of validated cohort ranges.
_LIMITS = {
    "idade": (30, 74), "pas": (60, 300), "colesterol_total": (100, 600),
    "hdl": (10, 150), "imc": (10, 70),
}


def _number(data: dict, key: str) -> float:
    value = data.get(key)
    # Existing HTML number inputs arrive as JSON strings. Parse only the
    # ASCII decimal syntax accepted by number inputs, never blanks or NaN/Inf.
    if isinstance(value, str):
        if len(value) > 128 or re.fullmatch(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?", value) is None:
            raise ValueError(f"Informe {key} como número decimal válido, sem texto ou valor ausente.")
        value = float(value)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"Informe {key} como número, sem texto ou valor ausente.")
    low, high = _LIMITS[key]
    if not low <= value <= high or not math.isfinite(value):
        raise ValueError(f"{key}: informe valor finito entre {low} e {high}; não extrapolar.")
    return float(value)


def _boolean(data: dict, key: str) -> bool:
    value = data.get(key)
    if type(value) is not bool:
        raise ValueError(f"Responda explicitamente Sim ou Não para {key}.")
    return value


def _calculate(data: dict, *, bmi: bool) -> dict:
    age = _number(data, "idade")
    sex = data.get("sexo")
    if not isinstance(sex, str) or sex not in ("M", "F"):
        raise ValueError("Informe o sexo usado na equação: masculino ou feminino.")
    if _boolean(data, "doenca_cardiovascular_previa"):
        raise ValueError("Framingham 2008 é destinado à prevenção primária, sem doença cardiovascular prévia.")
    treated = _boolean(data, "tratamento_hipertensao")
    smoker = _boolean(data, "tabagismo")
    diabetes = _boolean(data, "diabetes")
    sbp = _number(data, "pas")
    c = (_BMI if bmi else _LIPIDS)[sex]
    predictor = c[0] * math.log(age) + c[4 if treated else 3] * math.log(sbp)
    predictor += c[5] * smoker + c[6] * diabetes
    if bmi:
        predictor += c[1] * math.log(_number(data, "imc"))
    else:
        total, hdl = _number(data, "colesterol_total"), _number(data, "hdl")
        if hdl >= total:
            raise ValueError("HDL deve ser menor que o colesterol total; confira valores e unidades mg/dL.")
        predictor += c[1] * math.log(total) + c[2] * math.log(hdl)
    # Stable equivalent of 100 * (1 - S0 ** exp(sum(beta*x) - mean)).
    risk = -100.0 * math.expm1(math.log(c[8]) * math.exp(predictor - c[7]))
    return {
        "risco_pct": round(risk, 2),
        "horizonte_anos": 10,
        "desfecho": ENDPOINT,
        "modelo": "Framingham 2008 — IMC" if bmi else "Framingham 2008 — lipídios",
        "populacao": "Prevenção primária; 30–74 anos; sem doença cardiovascular prévia",
    }


def _framingham_global(data: dict) -> dict:
    return _calculate(data, bmi=False)


def _framingham_imc(data: dict) -> dict:
    return _calculate(data, bmi=True)


def _interpret(result: dict) -> str:
    return (
        f"{result['modelo']}: risco estimado de doença cardiovascular global em 10 anos "
        f"de {result['risco_pct']:.2f}%. Inclui insuficiência cardíaca, angina e AIT, além "
        "de eventos ateroscleróticos. Este percentual não equivale ao de PREVENT-ASCVD, "
        "PCE ou SCORE2 e não define, isoladamente, uma prescrição ou meta terapêutica."
    )


def _yes_no(name: str, label: str, help_text: str | None = None) -> Field:
    return Field(name, label, "select", options=[
        {"value": True, "label": "Sim"}, {"value": False, "label": "Não"},
    ], help=help_text)


def _fields(*, bmi: bool) -> list[Field]:
    common = [
        Field("idade", "Idade", "number", "anos", min=30, max=74),
        Field("sexo", "Sexo usado na equação original", "select", options=[
            {"value": "M", "label": "Masculino"}, {"value": "F", "label": "Feminino"},
        ]),
        _yes_no("doenca_cardiovascular_previa", "Doença cardiovascular prévia",
                "Inclui doença coronariana, AVC/AIT, doença arterial periférica e insuficiência cardíaca. "
                "Se presente, esta equação de prevenção primária não se aplica."),
        Field("pas", "Pressão arterial sistólica", "number", "mmHg", min=60, max=300,
              help="Use a pressão medida, mesmo durante tratamento; valores extremos exigem avaliação clínica."),
        _yes_no("tratamento_hipertensao", "Em tratamento medicamentoso para hipertensão"),
        _yes_no("tabagismo", "Tabagismo atual"),
        _yes_no("diabetes", "Diabetes mellitus"),
    ]
    if bmi:
        return common + [Field("imc", "Índice de massa corporal", "number", "kg/m²", min=10, max=70)]
    return common + [
        Field("colesterol_total", "Colesterol total", "number", "mg/dL", min=100, max=600),
        Field("hdl", "HDL-colesterol", "number", "mg/dL", min=10, max=150),
    ]


_LIMITATIONS = [
    "Modelo histórico/comparativo de 2008, para pessoas de 30–74 anos sem doença cardiovascular estabelecida; "
    "não usar em prevenção secundária nem extrapolar idades.",
    "Desfecho de DCV global mais amplo que ASCVD. Não transferir pontos de corte de PREVENT, PCE ou SCORE2.",
    "Derivado de uma coorte norte-americana; calibração e transportabilidade para o Brasil são limitadas. "
    "Não equivale a recomendação preferencial atual da SBC, AHA/ACC ou ESC. A SBC 2025 recomenda PREVENT-ASCVD para pessoas de 30–79 anos sem DCV prévia (recomendação forte; certeza alta; DOI: 10.36660/abc.20250640).",
    "Faixas numéricas do formulário são barreiras operacionais de entrada, não intervalos de validação "
    "da coorte. Resultados extremos exigem julgamento clínico; não truncamos entradas para obter um risco.",
    "Diabetes pode ser informado, mas doença renal, hipercolesterolemia familiar e outros modificadores "
    "podem definir risco e tratamento independentemente deste percentual.",
    "Sexo binário conforme a derivação original; desempenho não estabelecido para todas as identidades "
    "e situações de terapia hormonal. A equação não substitui avaliação individual.",
]

CARDIOVASCULAR_RISK_REGISTRY: dict[str, Calculator] = {
    "framingham-global": Calculator(
        slug="framingham-global",
        name="Framingham — risco cardiovascular global em 10 anos",
        theme="Prevenção e lipídios",
        purpose="Modelo histórico/comparativo: estimar DCV global em prevenção primária com idade, pressão, lipídios, diabetes e tabagismo.",
        fields=_fields(bmi=False), reference=REFERENCE,
        compute=_framingham_global, interpret=_interpret,
        limitations=list(_LIMITATIONS), kind="assessment",
    ),
    "framingham-imc": Calculator(
        slug="framingham-imc",
        name="Framingham — risco cardiovascular global com IMC",
        theme="Prevenção e lipídios",
        purpose="Modelo histórico/comparativo: estimar DCV global em 10 anos pelo modelo sem laboratório, usando IMC no lugar dos lipídios.",
        fields=_fields(bmi=True), reference=REFERENCE,
        compute=_framingham_imc, interpret=_interpret,
        limitations=list(_LIMITATIONS) + [
            "Modelo distinto da versão laboratorial; não preencher IMC como colesterol ou combinar os percentuais.",
        ], kind="assessment",
    ),
}
