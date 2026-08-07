"""Seleção de dose inicial e titulação de Entresto® segundo bula brasileira atual.

Fonte efetivamente consultada: bula profissional Novartis Brasil VPS15,
publicada no portal profissional em 2025 e referente a versão aprovada pela
ANVISA. Regras modeladas: dose inicial 100 mg 2x/dia; 50 mg 2x/dia em grupos
específicos; alvo 200 mg 2x/dia; titulação 2-4 semanas; washout de IECA 36 h;
limites de PAS, potássio, função renal e hepática.

Fonte de produção: ChatGPT.
"""

from __future__ import annotations

from .calculators import Calculator, Field

FONTE_PRODUCAO = "chatgpt"

ENTRESTO_BR_2025 = (
    "Entresto® (sacubitril valsartana sódica hidratada). Bula profissional Novartis Brasil, "
    "VPS15 Entresto_Bula_Profissional, portal NovartisPro Brasil, versão publicada em 2025."
)


def _entresto_inicial(d: dict) -> dict:
    tfge = float(d["tfge"])
    potassio = float(d["potassio"])
    pas = float(d["pas"])
    terapia_sraa = d["terapia_sraa"]
    horas_desde_ieca = float(d.get("horas_desde_ieca") or 0)
    child_pugh = d["child_pugh"]
    doenca_renal_terminal = bool(d.get("doenca_renal_terminal"))

    if tfge < 0 or potassio < 0 or pas <= 0 or horas_desde_ieca < 0:
        raise ValueError("Revise TFGe, potássio, PAS e intervalo desde IECA.")

    if child_pugh == "C":
        return {
            "conduta": "contraindicado",
            "motivo": "insuficiência hepática grave/Child-Pugh C; a bula também contraindica cirrose biliar e colestase",
        }
    if doenca_renal_terminal:
        return {
            "conduta": "nao_recomendado",
            "motivo": "não há estudos em doença renal em estágio terminal e a bula não recomenda o uso",
        }
    if potassio > 5.4:
        return {"conduta": "nao_iniciar", "motivo": "potássio sérico >5,4 mmol/L"}
    if pas < 100:
        return {"conduta": "nao_iniciar", "motivo": "PAS <100 mmHg"}

    usa_ieca = terapia_sraa in {"ieca", "ieca_baixa_dose"}
    if usa_ieca and horas_desde_ieca < 36:
        return {
            "conduta": "aguardar_washout_ieca",
            "horas_minimas": 36,
            "horas_informadas": horas_desde_ieca,
            "horas_restantes": round(36 - horas_desde_ieca, 1),
            "motivo": "risco de angioedema com sobreposição IECA/ARNI",
        }

    fatores_50 = []
    if terapia_sraa == "nenhum":
        fatores_50.append("não está usando IECA/BRA")
    elif terapia_sraa == "ieca_baixa_dose":
        fatores_50.append("uso prévio de baixa dose de IECA")
    elif terapia_sraa == "bra_baixa_dose":
        fatores_50.append("uso prévio de baixa dose de BRA")
    if tfge < 60:
        fatores_50.append("TFGe <60 mL/min/1,73 m²")
    if child_pugh == "B":
        fatores_50.append("Child-Pugh B")
    if 100 <= pas <= 110:
        fatores_50.append("PAS entre 100 e 110 mmHg")

    dose_inicial = "50 mg VO 2x/dia" if fatores_50 else "100 mg VO 2x/dia"
    return {
        "farmaco": "Entresto® (sacubitril/valsartana)",
        "dose_inicial": dose_inicial,
        "dose_alvo": "200 mg VO 2x/dia",
        "titulacao": "dobrar a dose a cada 2-4 semanas, conforme tolerância",
        "fatores_para_inicio_50mg": fatores_50,
        "tfge_grave_menor_30": tfge < 30,
        "suspender_bra_concomitante": terapia_sraa in {"bra", "bra_baixa_dose"},
    }


def _entresto_inicial_txt(r: dict) -> str:
    conduta = r.get("conduta")
    if conduta == "contraindicado":
        return f"Entresto®: CONTRAINDICADO — {r['motivo']}."
    if conduta in {"nao_recomendado", "nao_iniciar"}:
        return f"Entresto®: não iniciar/não recomendado neste cenário — {r['motivo']}."
    if conduta == "aguardar_washout_ieca":
        return (
            f"Não iniciar Entresto® ainda: aguardar pelo menos 36 h após a última dose de IECA. "
            f"Intervalo informado {r['horas_informadas']} h; faltam aproximadamente {r['horas_restantes']} h."
        )

    texto = f"Entresto®: iniciar {r['dose_inicial']}; alvo {r['dose_alvo']}; {r['titulacao']}."
    if r["fatores_para_inicio_50mg"]:
        texto += " Razões para a dose de 50 mg 2x/dia: " + "; ".join(r["fatores_para_inicio_50mg"]) + "."
    if r["tfge_grave_menor_30"]:
        texto += " TFGe <30: dados clínicos limitados; usar com cuidado segundo a bula."
    if r["suspender_bra_concomitante"]:
        texto += " Não coadministrar com BRA; Entresto já contém valsartana."
    return texto


_ENTRESTO_INICIAL = Calculator(
    slug="entresto-dose-inicial-bula-brasil-2025",
    name="Entresto® — dose inicial, washout de IECA e titulação (bula Brasil)",
    theme="Doses — Insuficiência Cardíaca",
    purpose="Seleciona 50 versus 100 mg 2x/dia e aplica limites explícitos da bula brasileira antes da titulação ao alvo de 200 mg 2x/dia.",
    fields=[
        Field("terapia_sraa", "Terapia atual/prévia com IECA ou BRA", "select", options=[
            {"value": "nenhum", "label": "Não usa IECA nem BRA atualmente"},
            {"value": "ieca_baixa_dose", "label": "Usava/usa IECA em baixa dose"},
            {"value": "bra_baixa_dose", "label": "Usava/usa BRA em baixa dose"},
            {"value": "ieca", "label": "Usa IECA em dose não classificada como baixa"},
            {"value": "bra", "label": "Usa BRA em dose não classificada como baixa"},
        ]),
        Field("horas_desde_ieca", "Horas desde a última dose de IECA", "number", "h", min=0, max=240,
              help="Obrigatório quando a opção é IECA, inclusive IECA em baixa dose; mínimo de 36 h antes de iniciar Entresto."),
        Field("tfge", "TFG estimada", "number", "mL/min/1,73 m²", min=0, max=200),
        Field("potassio", "Potássio sérico", "number", "mmol/L", min=1, max=10),
        Field("pas", "Pressão arterial sistólica", "number", "mmHg", min=50, max=250),
        Field("child_pugh", "Função hepática", "select", options=[
            {"value": "normal", "label": "Sem insuficiência hepática relevante"},
            {"value": "A", "label": "Child-Pugh A — leve"},
            {"value": "B", "label": "Child-Pugh B — moderada"},
            {"value": "C", "label": "Child-Pugh C — grave"},
        ]),
        Field("doenca_renal_terminal", "Doença renal em estágio terminal", "boolean"),
    ],
    compute=_entresto_inicial,
    interpret=_entresto_inicial_txt,
    reference=ENTRESTO_BR_2025,
    kind="dose",
    limitations=[
        "A bula brasileira usa apresentações nominais de Entresto 50/100/200 mg; não confundir com a nomenclatura internacional que frequentemente escreve os componentes como 24/26, 49/51 e 97/103 mg.",
        "Dose inicial padrão: 100 mg 2x/dia; alvo: 200 mg 2x/dia; dobrar a cada 2-4 semanas conforme tolerância.",
        "Considerar/iniciar 50 mg 2x/dia se sem IECA/BRA, uso prévio de baixa dose, TFGe <60, Child-Pugh B ou PAS 100-110 mmHg, conforme as respectivas seções da bula.",
        "Não iniciar se K >5,4 mmol/L ou PAS <100 mmHg.",
        "Após IECA, inclusive em baixa dose, respeitar pelo menos 36 h antes de iniciar Entresto; a terapia com IECA também só deve ser reiniciada 36 h após a última dose de Entresto.",
        "Child-Pugh C, cirrose biliar ou colestase são contraindicações. A calculadora só codifica Child-Pugh C; cirrose biliar/colestase devem ser verificadas clinicamente.",
        "A calculadora não substitui avaliação de hipovolemia, hipotensão sintomática, angioedema prévio, gravidez, alisquireno no diabetes, interações e monitorização de K/creatinina.",
    ],
)


ENTRESTO_BRASIL_DOSE_REGISTRY: dict[str, Calculator] = {_ENTRESTO_INICIAL.slug: _ENTRESTO_INICIAL}
