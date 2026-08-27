"""Segurança eletrolítica-arrítmica para Cardiologia Intensiva/UCO.

Esta engine organiza risco e prioridades quando há hipocalemia, possível
hipomagnesemia e substrato arrítmico. Ela não calcula reposição de potássio ou
magnésio, não escolhe via/velocidade e não substitui o fluxo elétrico de
arritmias ventriculares.
"""

from __future__ import annotations

import math

from .calculators import Calculator, Field


REFERENCIAS_ELETROLITOS_ARRITMIA = (
    "American Heart Association. 2025 Guidelines for CPR and ECC, Part 9: Adult "
    "Advanced Life Support. Circulation. 2025;152(Suppl 2):S538-S577. "
    "doi:10.1161/CIR.0000000000001376 — TV polimórfica sustentada exige choque "
    "não sincronizado imediato; torsades associa-se a QT longo, frequentemente "
    "com bradicardia, fármacos e distúrbios eletrolíticos, e a correção de "
    "hipocalemia é recomendada como causa reversível. "
    "ESC 2022 Guidelines for Ventricular Arrhythmias and Prevention of Sudden "
    "Cardiac Death. Eur Heart J. 2022;43:3997-4126. doi:10.1093/eurheartj/ehac262 "
    "— hipocalemia/hipomagnesemia são causas reversíveis relevantes de VT/VF/TdP. "
    "Kim MJ et al. Potassium Disorders: Hypokalemia and Hyperkalemia. Am Fam "
    "Physician. 2023;107:59-70 — K <=2.5 mEq/L, alterações eletrocardiográficas "
    "ou manifestações neuromusculares graves são características de hipocalemia "
    "que exigem tratamento urgente; ECG normal não exclui risco."
)


def _numero_opcional(dados: dict, chave: str) -> float | None:
    valor = dados.get(chave)
    if valor in (None, ""):
        return None
    try:
        numero = float(valor)
    except (TypeError, ValueError):
        raise ValueError(f"Valor inválido em {chave}.") from None
    if not math.isfinite(numero):
        raise ValueError(f"Informe valor finito em {chave}.")
    return numero


def _avaliar_seguranca_eletrolitica(dados: dict) -> dict:
    potassio = _numero_opcional(dados, "potassio_mmol_l")
    qtc = _numero_opcional(dados, "qtc_ms")

    if potassio is None:
        raise ValueError("Informe o potássio sérico atual.")
    if not 1.0 <= potassio <= 8.0:
        raise ValueError("Informe potássio entre 1,0 e 8,0 mmol/L.")
    if qtc is not None and not 250 <= qtc <= 800:
        raise ValueError("Informe QTc entre 250 e 800 ms.")

    tv_polimorfica_sustentada = bool(dados.get("tv_polimorfica_sustentada"))
    arritmia_ventricular = bool(dados.get("ectopia_complexa_ou_tvns"))
    alteracao_ecg_hipocalemia = bool(dados.get("alteracao_ecg_compativel"))
    sintoma_grave = bool(dados.get("sintoma_neuromuscular_grave"))
    hipomagnesemia = bool(dados.get("hipomagnesemia_documentada"))
    bradicardia_pausa = bool(dados.get("bradicardia_ou_pausas"))
    farmaco_qt = bool(dados.get("farmaco_prolonga_qt"))
    digoxina = bool(dados.get("uso_ou_toxicidade_digoxina_suspeita"))
    isquemia = bool(dados.get("isquemia_aguda_suspeita"))
    lra = bool(dados.get("lra_ou_disfuncao_renal_relevante"))
    oliguria = bool(dados.get("oliguria"))
    perdas = bool(dados.get("perdas_ou_shift_em_curso"))

    qtc_alto_risco = qtc is not None and qtc > 500
    hipocalemia = potassio < 3.5
    hipocalemia_grave = potassio <= 2.5
    fora_por_hipercalemia = potassio > 5.0

    if fora_por_hipercalemia:
        return {
            "risco": "fora_do_escopo",
            "prioridade": (
                "Potássio acima de 5,0 mmol/L: esta estação é dedicada à segurança da hipocalemia. "
                "Use o fluxo específico de hipercalemia; não extrapole regras de reposição desta ferramenta."
            ),
            "fenotipo": "potássio elevado — redirecionar para hipercalemia",
            "gatilhos": ["potássio acima do escopo de hipocalemia"],
            "monitorizacao": "Aplicar o protocolo específico de hipercalemia e ECG conforme contexto clínico.",
            "funcao_renal": _mensagem_funcao_renal(lra, oliguria),
            "proximo_fluxo": "hipercalemia-seguranca-uco",
            "qtc_alto_risco": qtc_alto_risco,
            "hipocalemia_grave": False,
        }

    gatilhos: list[str] = []
    if hipocalemia_grave:
        gatilhos.append("K <=2,5 mmol/L — hipocalemia grave")
    elif hipocalemia:
        gatilhos.append(f"hipocalemia atual (K {potassio:.2f} mmol/L)")
    if alteracao_ecg_hipocalemia:
        gatilhos.append("alterações eletrocardiográficas compatíveis")
    if sintoma_grave:
        gatilhos.append("manifestação neuromuscular grave")
    if arritmia_ventricular:
        gatilhos.append("ectopia ventricular complexa ou TV não sustentada")
    if tv_polimorfica_sustentada:
        gatilhos.append("TV polimórfica sustentada")
    if hipomagnesemia:
        gatilhos.append("hipomagnesemia documentada")
    if qtc_alto_risco:
        gatilhos.append("QTc >500 ms")
    if bradicardia_pausa:
        gatilhos.append("bradicardia/pausas")
    if farmaco_qt:
        gatilhos.append("exposição a fármaco que prolonga QT")
    if digoxina:
        gatilhos.append("uso ou toxicidade por digoxina suspeita")
    if isquemia:
        gatilhos.append("isquemia aguda suspeita")
    if perdas:
        gatilhos.append("perdas ou redistribuição intracelular ainda em curso")
    if not gatilhos:
        gatilhos.append("nenhum amplificador de risco declarado")

    if tv_polimorfica_sustentada:
        risco = "emergencia_eletrica"
        prioridade = (
            "EMERGÊNCIA ELÉTRICA: TV polimórfica sustentada exige choque não sincronizado imediato. "
            "A investigação/correção eletrolítica ocorre em paralelo e não deve atrasar desfibrilação."
        )
        proximo_fluxo = "torsades-qt-longo-magnesio-uco"
    elif hipocalemia_grave or alteracao_ecg_hipocalemia or sintoma_grave:
        risco = "critico"
        prioridade = (
            "HIPOCALIEMIA DE ALTO RISCO: K <=2,5 mmol/L, alteração de ECG ou manifestação "
            "neuromuscular grave exige correção urgente e monitorização conforme protocolo institucional. "
            "A estação não calcula dose, via ou velocidade."
        )
        proximo_fluxo = "hipocalemia-grave-risco-arritmico-e-reposicao-segura"
    elif hipocalemia and (arritmia_ventricular or qtc_alto_risco or hipomagnesemia or digoxina):
        risco = "prioritario"
        prioridade = (
            "HIPOCALIEMIA COM AMPLIFICADORES ARRÍTMICOS: priorizar correção da causa reversível, "
            "telemetria/ECG e reavaliação laboratorial. QT, magnésio, digoxina e arritmias modificam "
            "o risco; não são gatilhos para uma dose automática."
        )
        proximo_fluxo = "hipocalemia-grave-risco-arritmico-e-reposicao-segura"
    elif hipocalemia:
        risco = "vigilancia_intensificada"
        prioridade = (
            "Hipocalemia sem marcador grave declarado: identificar perdas/shift, revisar exposições e "
            "corrigir conforme protocolo, com rechecagem definida pela tendência e pelo contexto cardíaco."
        )
        proximo_fluxo = "hipocalemia-grave-risco-arritmico-e-reposicao-segura"
    elif hipomagnesemia or qtc_alto_risco or arritmia_ventricular:
        risco = "risco_arrtimico_sem_hipocalemia"
        prioridade = (
            "Potássio não está baixo, mas há substrato arrítmico/eletrolítico relevante. Não declarar "
            "segurança apenas pelo K: revisar magnésio, QT, ritmo, isquemia e fármacos conforme o fenótipo."
        )
        proximo_fluxo = "torsades-qt-longo-magnesio-uco" if qtc_alto_risco else "avaliacao-clinica"
    else:
        risco = "contextual"
        prioridade = (
            "Sem hipocalemia ou marcador arrítmico de alto risco declarado neste recorte. Manter "
            "vigilância orientada pela doença de base, tendência laboratorial e terapias em curso."
        )
        proximo_fluxo = "avaliacao-clinica"

    if hipomagnesemia and hipocalemia:
        magnesio = (
            "Hipomagnesemia pode aumentar risco arrítmico e contribuir para hipocalemia refratária; "
            "corrigir ambos conforme função renal e protocolo. Nenhuma dose é inferida."
        )
    elif hipomagnesemia:
        magnesio = (
            "Hipomagnesemia documentada exige avaliação/correção conforme contexto e função renal; "
            "se houver TV polimórfica/QT longo, usar o fluxo específico de Torsades."
        )
    else:
        magnesio = (
            "Sem hipomagnesemia declarada. Em hipocalemia persistente/refratária ou fenótipo de QT longo, "
            "confirmar magnésio em vez de assumir normalidade."
        )

    if perdas:
        tendencia = (
            "Há mecanismo de perda/shift ainda ativo: um valor isolado não encerra o risco; programar "
            "rechecagem laboratorial e tratar a causa em paralelo."
        )
    else:
        tendencia = (
            "Sem perda/shift ativo declarado. Ainda assim, usar tendência seriada quando houver correção "
            "em curso, doença crítica ou risco arrítmico."
        )

    return {
        "risco": risco,
        "prioridade": prioridade,
        "fenotipo": _fenotipo(potassio, qtc_alto_risco, hipomagnesemia, arritmia_ventricular),
        "gatilhos": gatilhos,
        "monitorizacao": tendencia,
        "papel_do_magnesio": magnesio,
        "funcao_renal": _mensagem_funcao_renal(lra, oliguria),
        "proximo_fluxo": proximo_fluxo,
        "qtc_alto_risco": qtc_alto_risco,
        "hipocalemia_grave": hipocalemia_grave,
    }


def _mensagem_funcao_renal(lra: bool, oliguria: bool) -> str:
    if lra or oliguria:
        return (
            "LRA/disfunção renal ou oligúria aumenta risco de sobrecorreção/acúmulo durante reposição. "
            "Isso não reduz a urgência de uma arritmia ou hipocalemia grave; exige individualização e "
            "rechecagens mais próximas, sem dose automática."
        )
    return "Sem marcador renal de alto risco declarado; confirmar função renal e diurese antes de reposições intensivas."


def _fenotipo(potassio: float, qtc_alto: bool, hipomag: bool, arritmia: bool) -> str:
    partes = []
    if potassio <= 2.5:
        partes.append("hipocalemia grave")
    elif potassio < 3.5:
        partes.append("hipocalemia")
    else:
        partes.append("potássio não baixo")
    if hipomag:
        partes.append("hipomagnesemia")
    if qtc_alto:
        partes.append("QTc >500 ms")
    if arritmia:
        partes.append("atividade ventricular ectópica/TVNS")
    return " + ".join(partes)


def _interpretar(resultado: dict) -> str:
    extras = []
    if resultado.get("papel_do_magnesio"):
        extras.append(resultado["papel_do_magnesio"])
    extras.extend([resultado["monitorizacao"], resultado["funcao_renal"]])
    return (
        f"{resultado['fenotipo']}. {resultado['prioridade']} "
        f"Gatilhos: {'; '.join(resultado['gatilhos'])}. "
        + " ".join(extras)
        + f" Próximo fluxo: {resultado['proximo_fluxo']}."
    )


_ELETROLITOS = Calculator(
    slug="seguranca-eletrolitica-arritmica-uco",
    name="Segurança eletrolítica-arrítmica — K, Mg, QT e função renal",
    theme="Terapia intensiva",
    purpose=(
        "Estratifica prioridade clínica na hipocalemia com amplificadores arrítmicos e renais, "
        "conectando K/Mg/QT/arritmias sem automatizar reposição."
    ),
    fields=[
        Field("potassio_mmol_l", "Potássio sérico atual", "number", "mmol/L", min=1.0, max=8.0),
        Field("qtc_ms", "QTc em ritmo basal", "number", "ms", min=250, max=800, required=False),
        Field("alteracao_ecg_compativel", "Alterações de ECG compatíveis com hipocalemia", "boolean"),
        Field("ectopia_complexa_ou_tvns", "Ectopia ventricular complexa ou TV não sustentada", "boolean"),
        Field("tv_polimorfica_sustentada", "TV polimórfica sustentada", "boolean"),
        Field("sintoma_neuromuscular_grave", "Fraqueza grave, paralisia ou comprometimento respiratório", "boolean"),
        Field("hipomagnesemia_documentada", "Hipomagnesemia documentada", "boolean"),
        Field("bradicardia_ou_pausas", "Bradicardia ou pausas relevantes", "boolean"),
        Field("farmaco_prolonga_qt", "Exposição a fármaco que prolonga QT", "boolean"),
        Field("uso_ou_toxicidade_digoxina_suspeita", "Uso de digoxina ou toxicidade suspeita", "boolean"),
        Field("isquemia_aguda_suspeita", "Isquemia aguda suspeita", "boolean"),
        Field("lra_ou_disfuncao_renal_relevante", "LRA ou disfunção renal relevante", "boolean"),
        Field("oliguria", "Oligúria", "boolean"),
        Field("perdas_ou_shift_em_curso", "Perdas GI/renais ou shift intracelular ainda em curso", "boolean"),
    ],
    compute=_avaliar_seguranca_eletrolitica,
    interpret=_interpretar,
    reference=REFERENCIAS_ELETROLITOS_ARRITMIA,
    kind="assessment",
    limitations=[
        "Não calcula dose, concentração, diluição, via ou velocidade de potássio/magnésio.",
        "TV polimórfica sustentada exige desfibrilação imediata; correção eletrolítica não deve atrasar choque.",
        "ECG normal não exclui risco da hipocalemia e alterações eletrocardiográficas não possuem limiar universal por concentração.",
        "K <=2,5 mmol/L é tratado como característica grave, mas a decisão terapêutica continua dependente do contexto clínico e do protocolo local.",
        "QTc isolado não diagnostica Torsades; usar o fluxo específico para TV polimórfica/QT longo.",
        "Disfunção renal/oligúria exige cautela contra sobrecorreção, mas não reclassifica uma emergência arrítmica como baixa prioridade.",
        "A ferramenta não suspende automaticamente diuréticos, digoxina, antiarrítmicos ou outros fármacos; apenas sinaliza revisão clínica."
    ],
)


INTENSIVE_CARE_ELECTROLYTE_SAFETY_REGISTRY: dict[str, Calculator] = {
    _ELETROLITOS.slug: _ELETROLITOS,
}
