"""Calculadora perioperatória geriátrica com coeficientes da fonte primária.

Fonte de produção: ChatGPT.
Todo coeficiente abaixo foi conferido diretamente na Tabela 3 do artigo
original open-access de Alrezk et al. (JAHA 2017; PMCID PMC5721761).
"""

from __future__ import annotations

import math

from app.services.calculators import Calculator, Field

SOURCE_PRODUCTION = "chatgpt"

_GSCRI_ASA = {1: 0.0, 2: 0.28, 3: 1.34, 4: 2.04, 5: 3.63}
_GSCRI_SURGERY = {
    "hernia": ("Hérnia", 0.0), "anorretal": ("Anorretal", 1.02),
    "aortica": ("Aórtica", 1.32), "bariatrica": ("Bariátrica", 0.31),
    "encefalica": ("Encefálica", 0.24), "mama": ("Mama", -1.14),
    "orl": ("Otorrinolaringológica", 0.32),
    "foregut_hpb": ("Trato gastrointestinal alto / hepatopancreatobiliar", 1.03),
    "gbaas_intestinal": ("Vesícula/apêndice/adrenal/baço ou intestinal", 1.13),
    "pescoco": ("Pescoço — tireoide/paratireoide", -0.04),
    "obstetrica_ginecologica": ("Obstétrica/ginecológica", 0.12),
    "ortopedica": ("Ortopédica / extremidade não vascular", 0.47),
    "abdome_outro": ("Abdominal — outra", 0.16),
    "vascular_periferica": ("Vascular periférica", 0.82),
    "pele": ("Pele/tecido subcutâneo", 0.41), "coluna": ("Coluna", 0.42),
    "toracica": ("Torácica não esofágica", 1.06), "veias": ("Veias", 1.35),
    "urologia": ("Urológica", 0.55),
}
_GSCRI_FUNCTIONAL = {"independente": 0.0, "parcialmente_dependente": 0.23, "totalmente_dependente": 0.72}
_GSCRI_DIABETES = {"nao": 0.0, "sem_insulina": 0.09, "com_insulina": 0.47}


def _gscri(d: dict) -> dict:
    idade = float(d["idade"])
    if idade < 65:
        raise ValueError("O GSCRI foi desenvolvido e validado para pacientes com idade ≥65 anos.")
    asa = int(d["asa"])
    procedimento = d["tipo_procedimento"]
    status_funcional = d["status_funcional"]
    diabetes = d["diabetes"]
    if asa not in _GSCRI_ASA or procedimento not in _GSCRI_SURGERY or status_funcional not in _GSCRI_FUNCTIONAL or diabetes not in _GSCRI_DIABETES:
        raise ValueError("Dados categóricos inválidos para GSCRI.")
    _, coef_procedimento = _GSCRI_SURGERY[procedimento]
    x = -6.79
    x += 2.08 if d.get("avc_previo") else 0.0
    x += _GSCRI_ASA[asa] + coef_procedimento + _GSCRI_FUNCTIONAL[status_funcional]
    x += 0.57 if d.get("creatinina_maior_1_5") else 0.0
    x += 0.60 if d.get("insuficiencia_cardiaca") else 0.0
    x += _GSCRI_DIABETES[diabetes]
    risco_pct = round((1.0 / (1.0 + math.exp(-x))) * 100.0, 2)
    return {"risco_pct": risco_pct, "endpoint": "infarto do miocardio ou parada cardiaca perioperatoria", "idade_minima_validacao": 65, "procedimento": _GSCRI_SURGERY[procedimento][0]}


def _gscri_txt(r: dict) -> str:
    return (
        f"GSCRI: risco estimado de IAM ou parada cardíaca perioperatória de {r['risco_pct']}%. "
        "O modelo foi derivado especificamente em pacientes ≥65 anos. Na validação geriátrica, "
        "AUC 0,76 versus 0,70 para Gupta MICA e 0,63 para RCRI. O percentual não deve ser usado "
        "isoladamente para indicar teste isquêmico, coronariografia ou adiamento cirúrgico."
    )


GERIATRIC_PERIOPERATIVE_REGISTRY: dict[str, Calculator] = {
    "gscri": Calculator(
        slug="gscri", name="GSCRI — Geriatric-Sensitive Cardiac Risk Index", theme="Perioperatório",
        purpose="Risco de IAM ou parada cardíaca perioperatória em pacientes ≥65 anos submetidos a cirurgia não cardíaca.",
        fields=[
            Field("idade", "Idade", "number", "anos", min=65, max=120), Field("avc_previo", "História de AVC", "boolean"),
            Field("asa", "Classe ASA", "select", options=[{"value": i, "label": f"ASA {i}"} for i in range(1, 6)]),
            Field("tipo_procedimento", "Tipo de procedimento", "select", options=[{"value": k, "label": v[0]} for k, v in _GSCRI_SURGERY.items()]),
            Field("status_funcional", "Status funcional", "select", options=[
                {"value": "independente", "label": "Independente"}, {"value": "parcialmente_dependente", "label": "Parcialmente dependente"}, {"value": "totalmente_dependente", "label": "Totalmente dependente"}]),
            Field("creatinina_maior_1_5", "Creatinina >1,5 mg/dL", "boolean"), Field("insuficiencia_cardiaca", "História de insuficiência cardíaca", "boolean"),
            Field("diabetes", "Diabetes mellitus", "select", options=[{"value": "nao", "label": "Não"}, {"value": "sem_insulina", "label": "Sim, sem insulina"}, {"value": "com_insulina", "label": "Sim, com insulina"}]),
        ],
        reference="Alrezk R, Jackson N, Al Rezk M, et al. J Am Heart Assoc. 2017;6(11):e006648. PMID: 29146612. PMCID: PMC5721761. DOI: 10.1161/JAHA.117.006648. Coeficientes: Table 3.",
        compute=_gscri, interpret=_gscri_txt,
        limitations=["Validado especificamente para idade ≥65 anos.", "Endpoint é IAM/parada cardíaca, não mortalidade global.", "ASA e categoria do procedimento precisam ser classificados corretamente.", "Não substitui capacidade funcional, fragilidade, doença cardiovascular ativa ou julgamento clínico."],
    )
}