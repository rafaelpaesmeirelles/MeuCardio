"""Overrides e novas calculadoras de doses PALS 2025.

Substitui no registry as versões PALS 2020 já existentes pelos mesmos slugs,
preservando compatibilidade de URLs e atualizando referência/detalhes para a
AHA/AAP 2025. Fonte de produção: ChatGPT.
"""

from __future__ import annotations

from .calculators import Calculator, Field

FONTE_PRODUCAO = "chatgpt"

PALS_2025 = (
    "Lasa JJ, Dhillon GS, Duff JP, et al. Part 8: Pediatric Advanced Life Support: "
    "2025 American Heart Association Guidelines for Cardiopulmonary Resuscitation "
    "and Emergency Cardiovascular Care. Circulation. 2025;152(Suppl 2):S479-S537. "
    "doi:10.1161/CIR.0000000000001368."
)


def _epinefrina_pcr_ped(d: dict) -> dict:
    peso = float(d["peso"])
    if peso <= 0:
        raise ValueError("Peso precisa ser maior que zero.")
    dose_mg = min(peso * 0.01, 1.0)
    volume_ml = dose_mg / 0.1  # concentração do algoritmo: 0,1 mg/mL
    return {
        "farmaco": "Epinefrina",
        "dose_mg": round(dose_mg, 3),
        "volume_ml_0_1mg_ml": round(volume_ml, 2),
        "intervalo": "a cada 3-5 min durante a PCR",
    }


def _epinefrina_pcr_ped_txt(r: dict) -> str:
    return (
        f"Epinefrina {r['dose_mg']} mg IV/IO ({r['volume_ml_0_1mg_ml']} mL da concentração "
        f"0,1 mg/mL), {r['intervalo']}. Dose máxima por administração: 1 mg."
    )


_EPINEFRINA_PCR_PED = Calculator(
    slug="adrenalina-pcr-pediatrica",
    name="Epinefrina — parada cardiorrespiratória pediátrica (PALS 2025)",
    theme="Doses — Cardiologia Pediátrica",
    purpose="Dose IV/IO por peso na PCR pediátrica, conforme AHA/AAP 2025.",
    fields=[Field("peso", "Peso da criança", "number", "kg", min=1, max=150)],
    compute=_epinefrina_pcr_ped,
    interpret=_epinefrina_pcr_ped_txt,
    reference=PALS_2025,
    kind="dose",
    limitations=[
        "Em ritmo não chocável, a dose inicial deve ser administrada tão cedo quanto possível; em ritmo chocável, priorizar desfibrilação.",
        "Não usar esta calculadora como substituto do algoritmo completo de PCR pediátrica.",
    ],
)


def _amiodarona_pcr_ped(d: dict) -> dict:
    peso = float(d["peso"])
    numero_dose = int(d["numero_dose"])
    if peso <= 0:
        raise ValueError("Peso precisa ser maior que zero.")
    teto = 300.0 if numero_dose == 1 else 150.0
    dose = min(peso * 5.0, teto)
    return {
        "farmaco": "Amiodarona",
        "numero_dose": numero_dose,
        "dose_mg": round(dose, 1),
        "dose_por_peso": "5 mg/kg",
        "teto_desta_dose_mg": teto,
    }


def _amiodarona_pcr_ped_txt(r: dict) -> str:
    return (
        f"Amiodarona — {r['numero_dose']}ª dose: {r['dose_mg']} mg IV/IO em bolus "
        f"(5 mg/kg; teto desta dose {r['teto_desta_dose_mg']} mg). O PALS 2025 permite "
        "até 3 doses no algoritmo de FV/TV sem pulso refratária."
    )


_AMIODARONA_PCR_PED = Calculator(
    slug="amiodarona-pcr-pediatrica",
    name="Amiodarona — FV/TV sem pulso pediátrica refratária (PALS 2025)",
    theme="Doses — Cardiologia Pediátrica",
    purpose="Calcula cada uma das até 3 doses de amiodarona, com tetos diferentes na 1ª e nas doses subsequentes.",
    fields=[
        Field("peso", "Peso da criança", "number", "kg", min=1, max=150),
        Field("numero_dose", "Qual dose", "select", options=[
            {"value": 1, "label": "1ª dose — máximo 300 mg"},
            {"value": 2, "label": "2ª dose — máximo 150 mg"},
            {"value": 3, "label": "3ª dose — máximo 150 mg"},
        ]),
    ],
    compute=_amiodarona_pcr_ped,
    interpret=_amiodarona_pcr_ped_txt,
    reference=PALS_2025,
    kind="dose",
    limitations=[
        "Somente para FV/TV sem pulso refratária à desfibrilação.",
        "Lidocaína é alternativa aceita pelo PALS 2025; não administrar múltiplos antiarrítmicos empiricamente sem contexto especializado.",
    ],
)


def _lidocaina_pcr_ped(d: dict) -> dict:
    peso = float(d["peso"])
    if peso <= 0:
        raise ValueError("Peso precisa ser maior que zero.")
    return {"farmaco": "Lidocaína", "dose_mg": round(peso * 1.0, 1), "dose_por_peso": "1 mg/kg"}


def _lidocaina_pcr_ped_txt(r: dict) -> str:
    return f"Lidocaína {r['dose_mg']} mg IV/IO (1 mg/kg) para FV/TV sem pulso refratária à desfibrilação."


_LIDOCAINA_PCR_PED = Calculator(
    slug="lidocaina-pcr-pediatrica-2025",
    name="Lidocaína — FV/TV sem pulso pediátrica (PALS 2025)",
    theme="Doses — Cardiologia Pediátrica",
    purpose="Dose IV/IO de lidocaína por peso como alternativa à amiodarona na PCR pediátrica chocável refratária.",
    fields=[Field("peso", "Peso da criança", "number", "kg", min=1, max=150)],
    compute=_lidocaina_pcr_ped,
    interpret=_lidocaina_pcr_ped_txt,
    reference=PALS_2025,
    kind="dose",
    limitations=["Somente para FV/TV sem pulso refratária à desfibrilação."],
)


def _choque_ped(d: dict) -> dict:
    peso = float(d["peso"])
    tipo = d["tipo"]
    if peso <= 0:
        raise ValueError("Peso precisa ser maior que zero.")
    if tipo == "desfibrilacao":
        return {
            "tipo": "desfibrilacao",
            "primeiro_j": round(peso * 2, 1),
            "segundo_j": round(peso * 4, 1),
            "subsequente_min_j": round(peso * 4, 1),
            "teto_peso_j": round(peso * 10, 1),
        }
    return {
        "tipo": "cardioversao",
        "primeiro_min_j": round(peso * 0.5, 1),
        "primeiro_max_j": round(peso * 1.0, 1),
        "segundo_j": round(peso * 2.0, 1),
    }


def _choque_ped_txt(r: dict) -> str:
    if r["tipo"] == "desfibrilacao":
        return (
            f"Desfibrilação: 1º choque {r['primeiro_j']} J (2 J/kg); 2º {r['segundo_j']} J "
            f"(4 J/kg); subsequentes ≥{r['subsequente_min_j']} J (≥4 J/kg), até 10 J/kg "
            "ou a dose de adulto."
        )
    return (
        f"Cardioversão sincronizada: iniciar em {r['primeiro_min_j']}-{r['primeiro_max_j']} J "
        f"(0,5-1 J/kg); se ineficaz, aumentar para {r['segundo_j']} J (2 J/kg)."
    )


_CHOQUE_PED = Calculator(
    slug="choque-eletrico-pediatrico",
    name="Desfibrilação e cardioversão pediátrica — PALS 2025",
    theme="Doses — Cardiologia Pediátrica",
    purpose="Energia por peso para desfibrilação ou cardioversão sincronizada, conforme AHA/AAP 2025.",
    fields=[
        Field("peso", "Peso da criança", "number", "kg", min=1, max=150),
        Field("tipo", "Situação", "select", options=[
            {"value": "desfibrilacao", "label": "Desfibrilação — FV/TV sem pulso"},
            {"value": "cardioversao", "label": "Cardioversão sincronizada — taquiarritmia instável"},
        ]),
    ],
    compute=_choque_ped,
    interpret=_choque_ped_txt,
    reference=PALS_2025,
    kind="dose",
    limitations=[
        "Na cardioversão instável, sedar se necessário e possível, mas não atrasar o choque.",
        "Na desfibrilação, o PALS 2025 estabelece para choques subsequentes ≥4 J/kg, máximo 10 J/kg ou dose de adulto.",
    ],
)


def _adenosina_ped(d: dict) -> dict:
    peso = float(d["peso"])
    numero_dose = int(d["numero_dose"])
    if peso <= 0:
        raise ValueError("Peso precisa ser maior que zero.")
    if numero_dose == 1:
        dose = min(peso * 0.1, 6.0)
        teto = 6.0
    else:
        dose = min(peso * 0.2, 12.0)
        teto = 12.0
    return {"farmaco": "Adenosina", "numero_dose": numero_dose, "dose_mg": round(dose, 2), "teto_mg": teto}


def _adenosina_ped_txt(r: dict) -> str:
    return (
        f"Adenosina — {r['numero_dose']}ª dose: {r['dose_mg']} mg IV/IO em push rápido, "
        f"seguido de flush; teto desta etapa {r['teto_mg']} mg."
    )


_ADENOSINA_PED = Calculator(
    slug="adenosina-tsv-pediatrica",
    name="Adenosina — TSV pediátrica (PALS 2025)",
    theme="Doses — Cardiologia Pediátrica",
    purpose="1ª e 2ª dose por peso na TSV pediátrica.",
    fields=[
        Field("peso", "Peso da criança", "number", "kg", min=1, max=150),
        Field("numero_dose", "Qual dose", "select", options=[
            {"value": 1, "label": "1ª dose — 0,1 mg/kg, máximo 6 mg"},
            {"value": 2, "label": "2ª dose — 0,2 mg/kg, máximo 12 mg"},
        ]),
    ],
    compute=_adenosina_ped,
    interpret=_adenosina_ped_txt,
    reference=PALS_2025,
    kind="dose",
    limitations=[
        "Em taquiarritmia com comprometimento cardiopulmonar, cardioversão sincronizada não deve ser atrasada.",
        "Em QRS largo, só considerar adenosina quando o ritmo for regular e monomórfico.",
    ],
)


def _atropina_ped(d: dict) -> dict:
    peso = float(d["peso"])
    if peso <= 0:
        raise ValueError("Peso precisa ser maior que zero.")
    dose = max(peso * 0.02, 0.1)
    dose = min(dose, 0.5)
    return {"farmaco": "Atropina", "dose_mg": round(dose, 3), "pode_repetir": "1 vez"}


def _atropina_ped_txt(r: dict) -> str:
    return (
        f"Atropina {r['dose_mg']} mg IV/IO (0,02 mg/kg; mínimo 0,1 mg; máximo por dose 0,5 mg). "
        "Pode repetir uma vez."
    )


_ATROPINA_PED = Calculator(
    slug="atropina-bradicardia-pediatrica",
    name="Atropina — bradicardia pediátrica (PALS 2025)",
    theme="Doses — Cardiologia Pediátrica",
    purpose="Dose IV/IO por peso para bradicardia com aumento de tônus vagal ou bloqueio AV primário.",
    fields=[Field("peso", "Peso da criança", "number", "kg", min=1, max=150)],
    compute=_atropina_ped,
    interpret=_atropina_ped_txt,
    reference=PALS_2025,
    kind="dose",
    limitations=[
        "No algoritmo de bradicardia pediátrica, atropina é indicada para aumento de tônus vagal ou bloqueio AV primário; hipóxia exige correção de via aérea/ventilação.",
        "O mínimo de 0,1 mg aplica-se ao algoritmo de bradicardia; a AHA/AAP 2025 não estabelece mínimo quando atropina é usada como pré-medicação para intubação.",
    ],
)


PALS_2025_DOSE_REGISTRY: dict[str, Calculator] = {
    c.slug: c for c in [
        _EPINEFRINA_PCR_PED,
        _AMIODARONA_PCR_PED,
        _LIDOCAINA_PCR_PED,
        _CHOQUE_PED,
        _ADENOSINA_PED,
        _ATROPINA_PED,
    ]
}
