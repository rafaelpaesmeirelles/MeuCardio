"""Surgical Outcome Risk Tool (SORT) com coeficientes da fonte primária.

Fonte de produção: ChatGPT.
Modelo: Protopapa et al., BJS 2014, Table 4; constante -7.366.
"""

from __future__ import annotations

import math

from app.services.calculators import Calculator, Field

SOURCE_PRODUCTION = "chatgpt"


_SORT_ASA = {1: 0.0, 2: 0.0, 3: 1.411, 4: 2.388, 5: 4.081}
_SORT_URGENCIA = {
    "eletiva": 0.0,
    "expedited": 1.236,
    "urgente": 1.657,
    "imediata": 2.452,
}


def _sort(d: dict) -> dict:
    idade = float(d["idade"])
    asa = int(d["asa"])
    if asa not in _SORT_ASA:
        raise ValueError("Classe ASA inválida para SORT.")
    urgencia = d["urgencia"]
    if urgencia not in _SORT_URGENCIA:
        raise ValueError("Categoria de urgência inválida para SORT.")

    x = -7.366
    x += _SORT_ASA[asa]
    x += _SORT_URGENCIA[urgencia]
    x += 0.712 if d.get("especialidade_alto_risco") else 0.0
    x += 0.381 if d.get("xmajor_complexa") else 0.0
    x += 0.667 if d.get("cancer") else 0.0
    if idade >= 80:
        x += 1.591
    elif idade >= 65:
        x += 0.777

    risco = 1.0 / (1.0 + math.exp(-x))
    return {
        "risco_pct": round(risco * 100.0, 2),
        "endpoint": "mortalidade por todas as causas em 30 dias",
    }


def _sort_txt(r: dict) -> str:
    return (
        f"SORT: risco estimado de mortalidade por todas as causas em 30 dias de "
        f"{r['risco_pct']}%. O modelo original apresentou AUROC 0,91 na coorte de validação. "
        "O resultado é de mortalidade global, não de MICA/MACE; deve ser apresentado ao lado, "
        "e não somado, aos escores cardiovasculares."
    )


SORT_PERIOPERATIVE_REGISTRY: dict[str, Calculator] = {
    "sort": Calculator(
        slug="sort",
        name="SORT — Surgical Outcome Risk Tool",
        theme="Perioperatório",
        purpose="Estimar risco percentual de mortalidade em 30 dias após cirurgia não cardíaca.",
        fields=[
            Field("idade", "Idade", "number", "anos", min=18, max=120),
            Field("asa", "Classe ASA", "select", options=[
                {"value": 1, "label": "ASA I"},
                {"value": 2, "label": "ASA II"},
                {"value": 3, "label": "ASA III"},
                {"value": 4, "label": "ASA IV"},
                {"value": 5, "label": "ASA V"},
            ]),
            Field("urgencia", "Urgência da cirurgia", "select", options=[
                {"value": "eletiva", "label": "Eletiva"},
                {"value": "expedited", "label": "Expedited / acelerada"},
                {"value": "urgente", "label": "Urgente"},
                {"value": "imediata", "label": "Imediata"},
            ]),
            Field(
                "especialidade_alto_risco",
                "Especialidade de alto risco no SORT: gastrointestinal, torácica ou vascular",
                "boolean",
            ),
            Field(
                "xmajor_complexa",
                "Cirurgia extra-major/complexa na classificação de severidade usada pelo SORT",
                "boolean",
            ),
            Field("cancer", "Câncer", "boolean"),
        ],
        reference=(
            "Protopapa KL, Simpson JC, Smith NCE, Moonesinghe SR. Development and validation "
            "of the Surgical Outcome Risk Tool (SORT). Br J Surg. 2014;101(13):1774-1783. "
            "PMID: 25388883. PMCID: PMC4240514. DOI: 10.1002/bjs.9638. "
            "Coeficientes: Table 4; constante -7.366."
        ),
        compute=_sort,
        interpret=_sort_txt,
        limitations=[
            "Endpoint: mortalidade global em 30 dias, não complicação cardíaca específica.",
            "A categoria 'extra-major/complexa' depende da classificação de severidade cirúrgica usada no estudo original.",
            "A urgência 'expedited' deve ser diferenciada de urgente e imediata conforme a taxonomia do SORT.",
            "Não somar ou promediar o percentual com RCRI, Gupta MICA, GSCRI ou AUB-HAS2.",
        ],
    ),
}