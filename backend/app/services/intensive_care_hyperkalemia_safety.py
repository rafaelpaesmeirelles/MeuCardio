"""Estação segura de hipercalemia adulta para Cardiologia Intensiva/UCO.

Classifica gravidade e confere amostra, ECG e monitorização sem selecionar ou
calcular tratamento. A causa específica de uma parada cardíaca nunca é inferida
apenas por uma elevação leve do potássio.
"""

from __future__ import annotations

import math

from .calculators import Calculator, Field


REFERENCIAS_HIPERCALEMIA = (
    "UK Kidney Association. Clinical Practice Guideline: Management of Hyperkalaemia in Adults. "
    "Hospital section updated 19 Dec 2023. https://www.ukkidney.org/health-professionals/"
    "guidelines/treatment-acute-hyperkalaemia-adults-0; American Heart Association. 2025 "
    "Guidelines for CPR and ECC, Part 10: Adult and Pediatric Special Circumstances of "
    "Resuscitation. https://cpr.heart.org/en/resuscitation-science/cpr-and-ecc-guidelines/"
    "adult-and-pediatric-special-circumstances-of-resuscitation; Durfey N et al. Severe "
    "Hyperkalemia: Can the Electrocardiogram Risk Stratify for Short-term Adverse Events? "
    "West J Emerg Med. 2017;18:963-971. PMID:28874951; Montague BT et al. Retrospective "
    "Review of the Frequency of ECG Changes in Hyperkalemia. Clin J Am Soc Nephrol. "
    "2008;3:324-330. PMID:18235147."
)


def _numero(dados: dict, chave: str) -> float:
    try:
        valor = float(dados[chave])
    except (KeyError, TypeError, ValueError):
        raise ValueError(f"Informe valor numérico válido em {chave}.") from None
    if not math.isfinite(valor):
        raise ValueError(f"Informe valor finito em {chave}.")
    return valor


def _avaliar(dados: dict) -> dict:
    potassio = _numero(dados, "potassio_mmol_l")
    if not 2.0 <= potassio <= 10.0:
        raise ValueError("Informe potássio entre 2,0 e 10,0 mmol/L.")

    qualidade = dados.get("qualidade_amostra")
    if qualidade not in {"desconhecida", "confirmada", "hemolise_suspeita"}:
        raise ValueError("Selecione a qualidade da amostra.")

    ecg_realizado = bool(dados.get("ecg_realizado"))
    ecg_compativel = bool(dados.get("alteracao_ecg_compativel"))
    instabilidade = bool(dados.get("instabilidade_ou_arritmia_grave"))
    parada = bool(dados.get("parada_cardiorrespiratoria"))
    atribuicao_parada = bool(dados.get("forte_suspeita_hipercalemia_na_parada"))
    lra_oliguria = bool(dados.get("lra_oliguria_ou_anuria"))
    insulina_glicose = bool(dados.get("insulina_glicose_administrada"))
    glicemia_seriada = bool(dados.get("glicemia_seriada_programada"))
    potassio_seriado = bool(dados.get("potassio_seriado_programado"))
    toxicidade_digitalica = bool(dados.get("suspeita_toxicidade_digitalica"))

    if ecg_compativel and not ecg_realizado:
        raise ValueError("Não marque alteração eletrocardiográfica sem ECG de 12 derivações realizado.")
    if atribuicao_parada and not parada:
        raise ValueError("Atribuição de hipercalemia à parada só pode ser marcada quando há parada em curso.")

    if potassio < 5.5:
        faixa = "abaixo do limiar de hipercalemia desta estação"
    elif potassio < 6.0:
        faixa = "hipercalemia leve (5,5–5,9 mmol/L)"
    elif potassio < 6.5:
        faixa = "hipercalemia moderada (6,0–6,4 mmol/L)"
    else:
        faixa = "hipercalemia grave (≥6,5 mmol/L)"

    if parada:
        if atribuicao_parada:
            prioridade = (
                "RESSUSCITAÇÃO — ALS padrão em primeiro plano. Há forte suspeita declarada de "
                "hipercalemia como causa reversível: abrir em paralelo o protocolo específico de "
                "parada/hipercalemia. Esta estação não seleciona nem calcula terapias."
            )
            nivel = "emergencia"
        else:
            prioridade = (
                "RESSUSCITAÇÃO — ALS padrão. Não atribuir a parada automaticamente à hipercalemia; "
                "correlacionar valor, trajetória, ECG/ritmo, contexto renal e outras causas reversíveis."
            )
            nivel = "emergencia"
    elif potassio >= 6.5:
        prioridade = (
            "EMERGÊNCIA: K ≥6,5 mmol/L permanece hipercalemia grave mesmo sem alteração marcante "
            "no ECG. Ativar avaliação/tratamento emergencial conforme protocolo local; a estação não calcula doses."
        )
        nivel = "emergencia"
    elif potassio >= 5.5 and (ecg_compativel or instabilidade):
        prioridade = (
            "EMERGÊNCIA: hipercalemia com alteração eletrocardiográfica compatível e/ou instabilidade. "
            "Ativar o fluxo local sem aguardar progressão laboratorial."
        )
        nivel = "emergencia"
    elif potassio >= 6.0:
        prioridade = (
            "URGENTE: K 6,0–6,4 mmol/L requer avaliação imediata, monitorização, ECG, confirmação da "
            "amostra, investigação de causa e decisão terapêutica pelo protocolo local."
        )
        nivel = "urgente"
    elif potassio >= 5.5:
        prioridade = (
            "HIPERCALEMIA LEVE: confirmar valor e tendência, revisar causas e risco de progressão; "
            "não aplicar automaticamente o pacote de emergência."
        )
        nivel = "prioritario"
    else:
        prioridade = (
            "FORA DO ESCOPO: o valor informado não define hipercalemia. Instabilidade ou alteração do "
            "ritmo deve ser investigada por outras causas sem ser atribuída automaticamente ao potássio."
        )
        nivel = "informativo"

    if qualidade == "hemolise_suspeita":
        if potassio >= 6.5:
            amostra = (
                "Hemólise/pseudo-hipercalemia é possível: repetir imediatamente em coleta adequada, em "
                "paralelo ao reconhecimento de K ≥6,5 como valor grave; não rebaixar a urgência só pela hemólise."
            )
        else:
            amostra = "Hemólise possível: repetir a amostra prontamente e correlacionar antes de normalizar ou escalar o valor isolado."
    elif qualidade == "confirmada":
        amostra = "Amostra declarada como conferida e sem hemólise relevante."
    else:
        amostra = (
            "Qualidade da amostra ainda não conferida: verificar hemólise, método, coleta e horário; "
            "não assumir amostra confiável por padrão."
        )

    if not ecg_realizado:
        if parada:
            ecg = (
                "Não há ECG de 12 derivações documentado. O monitor/ritmo da ressuscitação não deve ser "
                "descrito como 'ECG normal'; obter traçado de 12 derivações quando clinicamente apropriado."
            )
        else:
            ecg = "ECG de 12 derivações não realizado: não inferir ausência de alterações eletrocardiográficas."
    elif ecg_compativel:
        ecg = "ECG compatível aumenta a preocupação e a prioridade; documentar ritmo, frequência, PR, QRS e evolução seriada."
    else:
        ecg = "ECG sem alteração compatível declarada não exclui hipercalemia clinicamente relevante nem neutraliza K ≥6,5 mmol/L."

    alertas: list[str] = []
    if insulina_glicose and not glicemia_seriada:
        alertas.append("Insulina/glicose foi administrada sem glicemia seriada programada: fechar o gate por risco de hipoglicemia tardia.")
    if (potassio >= 6.0 or insulina_glicose) and not potassio_seriado:
        alertas.append("Potássio seriado não está programado: documentar trajetória/resposta e vigiar rebote, independentemente do uso de insulina/glicose.")
    if lra_oliguria:
        alertas.append("LRA/oligúria/anúria reduz eliminação de potássio; discutir estratégia de remoção definitiva/suporte renal sem transformar estágio renal isolado em indicação automática de diálise.")
    if toxicidade_digitalica:
        alertas.append("Suspeita de toxicidade digitálica: ativar avaliação toxicológica/Fab específica; esta estação não decide cálcio nem antídoto.")
    if not alertas:
        alertas.append("Sem pendência adicional declarada; manter reavaliação clínica e laboratorial conforme gravidade e tratamento realizado.")

    return {
        "faixa": faixa,
        "nivel": nivel,
        "prioridade": prioridade,
        "conferencia_amostra": amostra,
        "avaliacao_ecg": ecg,
        "alertas_seguranca": alertas,
        "fora_da_faixa": potassio >= 5.5 or ecg_compativel or instabilidade or parada,
    }


def _interpretar(resultado: dict) -> str:
    return (
        f"{resultado['faixa']}. {resultado['prioridade']} {resultado['conferencia_amostra']} "
        f"{resultado['avaliacao_ecg']} Alertas: {' '.join(resultado['alertas_seguranca'])}"
    )


_HIPERCALEMIA = Calculator(
    slug="hipercalemia-seguranca-uco",
    name="Hipercalemia na UCO — gravidade, ECG e gates de segurança",
    theme="Terapia intensiva",
    purpose=(
        "Classifica gravidade e confere amostra, ECG, parada, função renal e monitorização "
        "sem selecionar cálcio, insulina, glicose, beta-agonista, quelante, diurético ou diálise."
    ),
    fields=[
        Field("potassio_mmol_l", "Potássio sérico/plasmático", "number", "mmol/L", min=2.0, max=10.0),
        Field(
            "qualidade_amostra",
            "Qualidade da amostra",
            "select",
            options=[
                {"value": "desconhecida", "label": "Ainda não conferida"},
                {"value": "confirmada", "label": "Conferida, sem hemólise relevante"},
                {"value": "hemolise_suspeita", "label": "Hemólise/pseudo-hipercalemia possível"},
            ],
        ),
        Field("ecg_realizado", "ECG de 12 derivações realizado", "boolean"),
        Field("alteracao_ecg_compativel", "ECG com alteração compatível com hipercalemia", "boolean"),
        Field("instabilidade_ou_arritmia_grave", "Instabilidade ou arritmia grave", "boolean"),
        Field("parada_cardiorrespiratoria", "Parada cardiorrespiratória em curso", "boolean"),
        Field(
            "forte_suspeita_hipercalemia_na_parada",
            "Hipercalemia é fortemente suspeita como causa reversível da parada",
            "boolean",
            help="Marque apenas quando o contexto clínico/laboratorial sustentar atribuição; K levemente elevado isolado não basta.",
        ),
        Field("lra_oliguria_ou_anuria", "LRA, oligúria ou anúria relevante", "boolean"),
        Field("insulina_glicose_administrada", "Insulina/glicose já administrada", "boolean"),
        Field("glicemia_seriada_programada", "Glicemia seriada programada", "boolean"),
        Field("potassio_seriado_programado", "Potássio seriado programado", "boolean"),
        Field("suspeita_toxicidade_digitalica", "Suspeita de toxicidade digitálica", "boolean"),
    ],
    compute=_avaliar,
    interpret=_interpretar,
    reference=REFERENCIAS_HIPERCALEMIA,
    kind="assessment",
    limitations=[
        "Ferramenta adulta de triagem/conferência; não seleciona nem calcula tratamento, dose, concentração, diluição ou indicação individual de diálise.",
        "Faixas 5,5–5,9, 6,0–6,4 e ≥6,5 mmol/L seguem a UK Kidney Association 2023; contexto pode exigir resposta mais precoce.",
        "ECG tem sensibilidade insuficiente para excluir hipercalemia e ECG ausente nunca é interpretado como normal.",
        "Hemólise exige repetição, mas não rebaixa automaticamente K ≥6,5 mmol/L.",
        "Parada cardíaca recebe ALS padrão; o fluxo específico de hipercalemia só é aberto quando há forte suspeita/atribuição clínica declarada.",
    ],
)


INTENSIVE_CARE_HYPERKALEMIA_SAFETY_REGISTRY = {_HIPERCALEMIA.slug: _HIPERCALEMIA}
