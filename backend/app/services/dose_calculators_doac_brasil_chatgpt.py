"""Calculadoras de dose de anticoagulantes orais diretos conforme bulas brasileiras vigentes.

Fontes efetivamente consultadas em 07/08/2026:
- Eliquis® (apixabana), bula profissional Pfizer Brasil, revisão 22/Out/2025.
- Xarelto® (rivaroxabana), Bulário Bayer, bula aprovada pela Anvisa em 22/12/2025.

Fonte de produção: ChatGPT.
"""

from __future__ import annotations

from .calculators import Calculator, Field

FONTE_PRODUCAO = "chatgpt"

ELIQUIS_BR_2025 = (
    "Eliquis® (apixabana). Bula profissional Pfizer Brasil. "
    "LLD_Bra_CCDS_27Jun2019_SMPC_17May2021_v13_ELICOR_33_VPS. 22/Out/2025."
)

XARELTO_BR_2025 = (
    "Xarelto® (rivaroxabana). Bula profissional Bayer S.A., Bulário Bayer; "
    "2,5mg/10mg CCDS19 e 15mg/20mg CCDS17, aprovada pela Anvisa em 22/12/2025."
)


def _apixabana_brasil(d: dict) -> dict:
    indicacao = d["indicacao"]
    idade = float(d["idade"])
    peso = float(d["peso"])
    creatinina = float(d["creatinina"])
    clcr = float(d["clcr"])
    dialise = bool(d.get("dialise"))

    if min(idade, peso, creatinina) <= 0 or clcr < 0:
        raise ValueError("Revise idade, peso, creatinina e ClCr.")

    if dialise or clcr < 15:
        return {
            "farmaco": "Apixabana",
            "conduta": "nao_recomendada_pela_bula_brasileira",
            "motivo": "ClCr <15 mL/min ou diálise: experiência clínica limitada/ausência de dados",
        }

    cautela_renal = 15 <= clcr < 30

    if indicacao == "fa_nvalvular":
        criterios = {
            "idade_ge_80": idade >= 80,
            "peso_le_60": peso <= 60,
            "creatinina_ge_1_5": creatinina >= 1.5,
        }
        n = sum(criterios.values())
        dose = "2,5 mg VO 2x/dia" if n >= 2 else "5 mg VO 2x/dia"
        return {
            "farmaco": "Apixabana",
            "indicacao": "FA não valvular — prevenção de AVC/embolia sistêmica",
            "dose": dose,
            "criterios_reducao_presentes": n,
            "criterios": criterios,
            "cautela_clcr_15_29": cautela_renal,
        }

    if indicacao == "tev_dias_1_7":
        return {
            "farmaco": "Apixabana",
            "indicacao": "TVP/EP — dias 1 a 7",
            "dose": "10 mg VO 2x/dia",
            "cautela_clcr_15_29": cautela_renal,
        }

    if indicacao == "tev_dia_8_em_diante":
        return {
            "farmaco": "Apixabana",
            "indicacao": "TVP/EP — após os primeiros 7 dias",
            "dose": "5 mg VO 2x/dia",
            "cautela_clcr_15_29": cautela_renal,
        }

    if indicacao == "prevencao_recorrencia_apos_6m":
        return {
            "farmaco": "Apixabana",
            "indicacao": "Prevenção de TVP/EP recorrentes após pelo menos 6 meses",
            "dose": "2,5 mg VO 2x/dia",
            "cautela_clcr_15_29": cautela_renal,
        }

    if indicacao == "artroplastia_quadril":
        return {
            "farmaco": "Apixabana",
            "indicacao": "Profilaxia de TEV após artroplastia eletiva de quadril",
            "dose": "2,5 mg VO 2x/dia",
            "inicio": "12-24 h após a cirurgia",
            "duracao": "32-38 dias",
            "cautela_clcr_15_29": cautela_renal,
        }

    return {
        "farmaco": "Apixabana",
        "indicacao": "Profilaxia de TEV após artroplastia eletiva de joelho",
        "dose": "2,5 mg VO 2x/dia",
        "inicio": "12-24 h após a cirurgia",
        "duracao": "10-14 dias",
        "cautela_clcr_15_29": cautela_renal,
    }


def _apixabana_brasil_txt(r: dict) -> str:
    if r.get("conduta") == "nao_recomendada_pela_bula_brasileira":
        return f"Apixabana: NÃO recomendada pela bula brasileira neste cenário — {r['motivo']}."
    texto = f"{r['farmaco']} — {r['indicacao']}: {r['dose']}"
    if r.get("inicio"):
        texto += f"; iniciar {r['inicio']}"
    if r.get("duracao"):
        texto += f"; duração {r['duracao']}"
    if r.get("criterios_reducao_presentes") is not None:
        texto += f". Critérios de redução presentes: {r['criterios_reducao_presentes']}/3"
    if r.get("cautela_clcr_15_29"):
        texto += ". ClCr 15-29 mL/min: usar com cautela segundo a bula profissional brasileira"
    return texto + "."


_APIXABANA_BRASIL = Calculator(
    slug="apixabana-dose-bula-brasil-2025",
    name="Apixabana — dose por indicação, idade, peso e função renal (bula Brasil 2025)",
    theme="Doses — Cardiologia Geral",
    purpose="Seleciona o esquema de apixabana pela indicação e aplica os critérios brasileiros de redução na FA não valvular.",
    fields=[
        Field("indicacao", "Indicação/fase", "select", options=[
            {"value": "fa_nvalvular", "label": "FA não valvular — prevenção de AVC/embolia sistêmica"},
            {"value": "tev_dias_1_7", "label": "TVP/EP aguda — dias 1 a 7"},
            {"value": "tev_dia_8_em_diante", "label": "TVP/EP — dia 8 em diante"},
            {"value": "prevencao_recorrencia_apos_6m", "label": "Prevenção de recorrência após ≥6 meses de TVP/EP"},
            {"value": "artroplastia_quadril", "label": "Profilaxia após artroplastia eletiva de quadril"},
            {"value": "artroplastia_joelho", "label": "Profilaxia após artroplastia eletiva de joelho"},
        ]),
        Field("idade", "Idade", "number", "anos", min=18, max=120),
        Field("peso", "Peso corporal", "number", "kg", min=20, max=300),
        Field("creatinina", "Creatinina sérica", "number", "mg/dL", min=0.1, max=20),
        Field("clcr", "Clearance de creatinina (preferencialmente Cockcroft-Gault)", "number", "mL/min", min=0, max=250),
        Field("dialise", "Paciente em diálise", "boolean"),
    ],
    compute=_apixabana_brasil,
    interpret=_apixabana_brasil_txt,
    reference=ELIQUIS_BR_2025,
    kind="dose",
    limitations=[
        "Na FA não valvular, reduzir de 5 mg 2x/dia para 2,5 mg 2x/dia apenas quando pelo menos 2 de 3 critérios estiverem presentes: idade ≥80 anos, peso ≤60 kg, creatinina sérica ≥1,5 mg/dL.",
        "ClCr 15-29 mL/min: a bula brasileira mantém os esquemas de TVP/EP e prevenção de recorrência, mas orienta uso com cautela.",
        "ClCr <15 mL/min ou diálise: apixabana não é recomendada pela bula profissional brasileira consultada.",
        "Interações fortes CYP3A4/gpP, sangramento ativo, doença hepática e outros modificadores não são resolvidos apenas por esta calculadora.",
    ],
)


def _rivaroxabana_brasil(d: dict) -> dict:
    indicacao = d["indicacao"]
    clcr = float(d["clcr"])
    risco_sangramento_supera_recorrencia = bool(d.get("risco_sangramento_supera_recorrencia"))
    if clcr < 0:
        raise ValueError("ClCr não pode ser negativo.")

    if clcr < 15:
        return {
            "farmaco": "Rivaroxabana",
            "conduta": "nao_recomendada_pela_bula_brasileira",
            "motivo": "ClCr <15 mL/min",
        }

    renal_15_49 = 15 <= clcr < 50
    renal_grave = 15 <= clcr < 30

    if indicacao == "fa_nvalvular":
        dose = "15 mg VO 1x/dia com alimento" if renal_15_49 else "20 mg VO 1x/dia com alimento"
        return {
            "farmaco": "Rivaroxabana",
            "indicacao": "FA não valvular — prevenção de AVC/embolia sistêmica",
            "dose": dose,
            "cautela_clcr_15_29": renal_grave,
        }

    if indicacao == "tev_dias_1_21":
        return {
            "farmaco": "Rivaroxabana",
            "indicacao": "TVP/EP aguda — dias 1 a 21",
            "dose": "15 mg VO 2x/dia com alimento",
            "dose_diaria_total": "30 mg/dia",
            "cautela_clcr_15_29": renal_grave,
        }

    if indicacao == "tev_dia_22_em_diante":
        if renal_15_49 and risco_sangramento_supera_recorrencia:
            dose = "15 mg VO 1x/dia com alimento — redução pode ser considerada"
            nota = (
                "Bula profissional: considerar redução de 20 para 15 mg/dia quando o risco de "
                "sangramento supera o risco de recorrência; recomendação baseada em modelo "
                "farmacocinético e não estudada neste cenário clínico."
            )
        else:
            dose = "20 mg VO 1x/dia com alimento"
            nota = "Dose usual de continuação."
        return {
            "farmaco": "Rivaroxabana",
            "indicacao": "TVP/EP — dia 22 em diante",
            "dose": dose,
            "nota_renal": nota,
            "cautela_clcr_15_29": renal_grave,
        }

    if indicacao == "prevencao_recorrencia_apos_6m":
        return {
            "farmaco": "Rivaroxabana",
            "indicacao": "Prevenção de TVP/EP recorrentes após pelo menos 6 meses",
            "dose": "10 mg VO 1x/dia OU 20 mg VO 1x/dia, conforme avaliação individual risco de recorrência versus sangramento",
            "alimento": "10 mg pode ser usado com ou sem alimento; 20 mg deve ser usado com alimento",
            "cautela_clcr_15_29": renal_grave,
        }

    return {
        "farmaco": "Rivaroxabana",
        "indicacao": "Profilaxia de TEV após artroplastia de quadril/joelho",
        "dose": "10 mg VO 1x/dia",
        "inicio": "6-10 h após a cirurgia, desde que a hemostasia esteja estabelecida",
        "duracao": "5 semanas após quadril; 2 semanas após joelho",
        "cautela_clcr_15_29": renal_grave,
    }


def _rivaroxabana_brasil_txt(r: dict) -> str:
    if r.get("conduta") == "nao_recomendada_pela_bula_brasileira":
        return f"Rivaroxabana: NÃO recomendada pela bula brasileira neste cenário — {r['motivo']}."
    texto = f"{r['farmaco']} — {r['indicacao']}: {r['dose']}"
    if r.get("nota_renal"):
        texto += f". {r['nota_renal']}"
    if r.get("inicio"):
        texto += f"; iniciar {r['inicio']}"
    if r.get("duracao"):
        texto += f"; duração {r['duracao']}"
    if r.get("alimento"):
        texto += f". {r['alimento']}"
    if r.get("cautela_clcr_15_29"):
        texto += ". ClCr 15-29 mL/min: dados clínicos limitados; usar com cautela"
    return texto + "."


_RIVAROXABANA_BRASIL = Calculator(
    slug="rivaroxabana-dose-bula-brasil-2025",
    name="Rivaroxabana — dose por indicação e função renal (bula Brasil 2025)",
    theme="Doses — Cardiologia Geral",
    purpose="Seleciona o esquema de rivaroxabana por indicação e ClCr, preservando a ressalva brasileira para redução no TEV.",
    fields=[
        Field("indicacao", "Indicação/fase", "select", options=[
            {"value": "fa_nvalvular", "label": "FA não valvular — prevenção de AVC/embolia sistêmica"},
            {"value": "tev_dias_1_21", "label": "TVP/EP aguda — dias 1 a 21"},
            {"value": "tev_dia_22_em_diante", "label": "TVP/EP — dia 22 em diante"},
            {"value": "prevencao_recorrencia_apos_6m", "label": "Prevenção de recorrência após ≥6 meses de TVP/EP"},
            {"value": "profilaxia_artroplastia", "label": "Profilaxia após artroplastia de quadril/joelho"},
        ]),
        Field("clcr", "Clearance de creatinina (preferencialmente Cockcroft-Gault)", "number", "mL/min", min=0, max=250),
        Field("risco_sangramento_supera_recorrencia", "No TEV após 21 dias com ClCr 15-49, o risco de sangramento avaliado supera o risco de recorrência", "boolean",
              help="Só é usado na fase de continuação. A opção 15 mg/dia é baseada em modelo farmacocinético e não foi estudada clinicamente nesse cenário."),
    ],
    compute=_rivaroxabana_brasil,
    interpret=_rivaroxabana_brasil_txt,
    reference=XARELTO_BR_2025,
    kind="dose",
    limitations=[
        "ClCr <15 mL/min: uso não recomendado pela bula brasileira consultada.",
        "ClCr 15-29 mL/min: dados clínicos limitados e uso com cautela.",
        "No tratamento de TVP/EP, a redução de 20 para 15 mg/dia após o dia 21 em ClCr 15-49 mL/min NÃO é automática: só deve ser considerada quando o risco de sangramento supera o de recorrência e é baseada em modelo farmacocinético, não em estudo clínico desse regime.",
        "Comprimidos de 15 e 20 mg devem ser administrados com alimento; 10 mg pode ser administrado com ou sem alimento.",
        "Interações, doença hepática, gravidez, próteses valvares e síndrome antifosfolípide exigem avaliação própria além desta calculadora.",
    ],
)


DOAC_BRASIL_DOSE_REGISTRY: dict[str, Calculator] = {
    c.slug: c for c in [_APIXABANA_BRASIL, _RIVAROXABANA_BRASIL]
}
