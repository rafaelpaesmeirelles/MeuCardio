"""SORT com coeficientes da Table 4 da fonte primária. Fonte: ChatGPT."""
from __future__ import annotations
import math
from app.services.calculators import Calculator, Field

_SORT_ASA = {1: 0.0, 2: 0.0, 3: 1.411, 4: 2.388, 5: 4.081}
_SORT_URGENCIA = {"eletiva": 0.0, "expedited": 1.236, "urgente": 1.657, "imediata": 2.452}


def _sort(d: dict) -> dict:
    idade, asa, urg = float(d["idade"]), int(d["asa"]), d["urgencia"]
    if asa not in _SORT_ASA or urg not in _SORT_URGENCIA:
        raise ValueError("Dados categóricos inválidos para SORT.")
    x = -7.366 + _SORT_ASA[asa] + _SORT_URGENCIA[urg]
    x += 0.712 if d.get("especialidade_alto_risco") else 0.0
    x += 0.381 if d.get("xmajor_complexa") else 0.0
    x += 0.667 if d.get("cancer") else 0.0
    x += 1.591 if idade >= 80 else (0.777 if idade >= 65 else 0.0)
    return {"risco_pct": round((1.0 / (1.0 + math.exp(-x))) * 100.0, 2), "endpoint": "mortalidade por todas as causas em 30 dias"}


def _sort_txt(r: dict) -> str:
    return f"SORT: mortalidade estimada em 30 dias {r['risco_pct']}%. AUROC 0,91 na validação original. É mortalidade global, não MICA/MACE."


SORT_PERIOPERATIVE_REGISTRY = {
    "sort": Calculator(
        slug="sort", name="SORT — Surgical Outcome Risk Tool", theme="Perioperatório",
        purpose="Risco percentual de mortalidade em 30 dias após cirurgia não cardíaca.",
        fields=[
            Field("idade", "Idade", "number", "anos", min=18, max=120),
            Field("asa", "Classe ASA", "select", options=[{"value": i, "label": f"ASA {i}"} for i in range(1, 6)]),
            Field("urgencia", "Urgência da cirurgia", "select", options=[{"value": "eletiva", "label": "Eletiva"}, {"value": "expedited", "label": "Expedited / acelerada"}, {"value": "urgente", "label": "Urgente"}, {"value": "imediata", "label": "Imediata"}]),
            Field("especialidade_alto_risco", "Especialidade de alto risco no SORT: gastrointestinal, torácica ou vascular", "boolean"),
            Field("xmajor_complexa", "Cirurgia extra-major/complexa pela taxonomia do SORT", "boolean"),
            Field("cancer", "Câncer", "boolean"),
        ],
        reference="Protopapa KL, Simpson JC, Smith NCE, Moonesinghe SR. Br J Surg. 2014;101(13):1774-1783. PMID: 25388883. PMCID: PMC4240514. DOI: 10.1002/bjs.9638. Table 4; constante -7.366.",
        compute=_sort, interpret=_sort_txt,
        limitations=["Endpoint: mortalidade global em 30 dias.", "Extra-major/complexa e categorias de urgência devem seguir a taxonomia original.", "Não somar/promediar com escores cardiovasculares."],
    )
}