"""Dose inicial de antagonista mineralocorticoide na ICFER por eGFR e K.

Fonte: 2022 AHA/ACC/HFSA HF guideline, seção 7.3.3 e Tabela 14.
A calculadora implementa apenas a decisão de INÍCIO e a redução renal descrita
na diretriz; não transforma um valor isolado de K durante seguimento em ordem
automática de suspensão.

Fonte de produção: ChatGPT.
"""

from __future__ import annotations

from .calculators import Calculator, Field

FONTE_PRODUCAO = "chatgpt"

AHA_HF_2022 = (
    "Heidenreich PA, Bozkurt B, Aguilar D, et al. 2022 AHA/ACC/HFSA Guideline for the "
    "Management of Heart Failure. Circulation. 2022;145:e895-e1032. "
    "doi:10.1161/CIR.0000000000001063. Section 7.3.3 and Table 14."
)


def _mra_icfer(d: dict) -> dict:
    farmaco = d["farmaco"]
    egfr = float(d["egfr"])
    potassio = float(d["potassio"])
    if egfr < 0 or potassio < 0:
        raise ValueError("eGFR e potássio não podem ser negativos.")

    if egfr <= 30:
        return {
            "conduta": "nao_iniciar",
            "motivo": "eGFR <=30 mL/min/1,73 m² — contraindicação à iniciação de MRA na diretriz AHA/ACC/HFSA 2022",
        }
    if potassio >= 5.0:
        return {
            "conduta": "nao_iniciar",
            "motivo": "K >=5,0 mEq/L — contraindicação à iniciação de MRA na diretriz AHA/ACC/HFSA 2022",
        }

    renal_reduzida = 31 <= egfr <= 49
    if farmaco == "espironolactona":
        dose_inicial = "12,5 mg VO 1x/dia" if renal_reduzida else "25 mg VO 1x/dia"
        dose_alvo = "25 mg VO 1x/dia inicialmente; considerar até 50 mg/dia conforme tolerância e monitorização" if renal_reduzida else "25-50 mg VO 1x/dia"
        nome = "Espironolactona"
    else:
        dose_inicial = "12,5 mg VO 1x/dia (metade de 25 mg)" if renal_reduzida else "25 mg VO 1x/dia"
        dose_alvo = "25 mg VO 1x/dia como alvo renal reduzido inicial; reavaliar titulação pela função renal/K" if renal_reduzida else "50 mg VO 1x/dia"
        nome = "Eplerenona"

    return {
        "farmaco": nome,
        "dose_inicial": dose_inicial,
        "dose_alvo_referencia": dose_alvo,
        "egfr_31_49": renal_reduzida,
        "monitorizacao": "K e função renal aproximadamente em 1 semana, 4 semanas e depois a cada 6 meses, com maior frequência se instabilidade clínica",
    }


def _mra_icfer_txt(r: dict) -> str:
    if r.get("conduta") == "nao_iniciar":
        return f"MRA: NÃO iniciar — {r['motivo']}."
    renal = " Dose reduzida pela metade porque eGFR está entre 31 e 49." if r["egfr_31_49"] else ""
    return (
        f"{r['farmaco']}: iniciar {r['dose_inicial']}; referência de alvo {r['dose_alvo_referencia']}."
        f"{renal} Monitorização: {r['monitorizacao']}."
    )


_MRA_ICFER = Calculator(
    slug="mra-icfer-egfr-potassio-aha-2022",
    name="MRA na ICFER — espironolactona/eplerenona por eGFR e potássio",
    theme="Doses — Insuficiência Cardíaca",
    purpose="Bloqueia início quando eGFR/K não permitem e reduz pela metade a dose em eGFR 31-49.",
    fields=[
        Field("farmaco", "MRA", "select", options=[
            {"value": "espironolactona", "label": "Espironolactona"},
            {"value": "eplerenona", "label": "Eplerenona"},
        ]),
        Field("egfr", "eGFR", "number", "mL/min/1,73 m²", min=0, max=200),
        Field("potassio", "Potássio sérico", "number", "mEq/L", min=1, max=10),
    ],
    compute=_mra_icfer,
    interpret=_mra_icfer_txt,
    reference=AHA_HF_2022,
    kind="dose",
    limitations=[
        "Não iniciar MRA se eGFR <=30 mL/min/1,73 m² ou K >=5,0 mEq/L.",
        "O texto de suporte recomenda iniciar espironolactona/eplerenona em 25 mg/dia e dobrar para 50 mg após um mês; em eGFR 31-49, reduzir a dose pela metade.",
        "Para espironolactona, a Tabela 14 também aceita 12,5-25 mg/dia como faixa inicial.",
        "A apresentação prática de eplerenona que permita 12,5 mg deve ser conferida no produto disponível; esta calculadora expressa a metade matemática da dose da diretriz, não uma apresentação comercial.",
        "Durante tratamento, a diretriz recomenda descontinuar MRA se o potássio não puder ser mantido <5,5 mEq/L; isso exige avaliação seriada e não é automatizado aqui a partir de um único valor.",
    ],
)


MRA_ICFER_DOSE_REGISTRY: dict[str, Calculator] = {_MRA_ICFER.slug: _MRA_ICFER}
