"""Reconhecimento de padrão BRASH para Cardiologia Intensiva/UCO.

A engine identifica uma constelação clínica compatível com BRASH sem criar
escore diagnóstico, sem escolher tratamento e sem calcular doses. Instabilidade
hemodinâmica tem prioridade sobre a rotulagem sindrômica.
"""

from __future__ import annotations

import math

from .calculators import Calculator, Field


REFERENCIAS_BRASH = (
    "Farkas JD et al. BRASH Syndrome: Bradycardia, Renal Failure, AV Blockade, Shock, "
    "and Hyperkalemia. J Emerg Med. 2020;59:216-223. doi:10.1016/j.jemermed.2020.05.001. "
    "PMID:32565167; Shah P et al. Clinical characteristics of BRASH syndrome: systematic "
    "scoping review. Eur J Intern Med. 2022;103:57-61. doi:10.1016/j.ejim.2022.06.002. "
    "PMID:35676108; Majeed H et al. BRASH Syndrome: A Systematic Review of Reported Cases. "
    "Curr Probl Cardiol. 2023;48:101663. doi:10.1016/j.cpcardiol.2023.101663. PMID:36842470."
)


def _numero(dados: dict, chave: str) -> float:
    try:
        valor = float(dados[chave])
    except (KeyError, TypeError, ValueError):
        raise ValueError(f"Informe valor numérico válido em {chave}.") from None
    if not math.isfinite(valor):
        raise ValueError(f"Informe valor finito em {chave}.")
    return valor


def _avaliar_brash(dados: dict) -> dict:
    fc = _numero(dados, "frequencia_cardiaca_bpm")
    potassio = _numero(dados, "potassio_mmol_l")
    if not 20 <= fc <= 220:
        raise ValueError("Informe frequência cardíaca entre 20 e 220 bpm.")
    if not 2.0 <= potassio <= 9.0:
        raise ValueError("Informe potássio entre 2,0 e 9,0 mmol/L.")

    renal = bool(dados.get("lra_ou_agudizacao_drc"))
    bloqueador = bool(dados.get("uso_bloqueador_nodal_av"))
    choque = bool(dados.get("choque_ou_hipoperfusao"))
    dose_excessiva = bool(dados.get("dose_excessiva_ou_overdose_suspeita"))
    ecg_hipercalemia = bool(dados.get("ecg_compativel_hipercalemia"))
    oliguria = bool(dados.get("oliguria"))
    gatilho_agudo = bool(dados.get("gatilho_agudo_desidratacao_infeccao_ou_nefrotoxico"))

    bradicardia = fc < 50
    hipercalemia = potassio >= 5.0
    nucleo = bradicardia and renal and bloqueador and hipercalemia
    pentade = nucleo and choque

    gatilhos: list[str] = []
    if bradicardia:
        gatilhos.append(f"bradicardia (FC {fc:.0f} bpm)")
    if renal:
        gatilhos.append("LRA ou agudização de DRC")
    if bloqueador:
        gatilhos.append("uso de bloqueador nodal AV")
    if hipercalemia:
        gatilhos.append(f"hipercalemia (K {potassio:.2f} mmol/L)")
    if choque:
        gatilhos.append("choque/hipoperfusão")
    if oliguria:
        gatilhos.append("oligúria")
    if gatilho_agudo:
        gatilhos.append("gatilho agudo renal/hemodinâmico declarado")
    if ecg_hipercalemia:
        gatilhos.append("ECG compatível com efeito da hipercalemia")

    if choque and bradicardia:
        risco = "emergencia_hemodinamica"
        prioridade = (
            "BRADICARDIA COM CHOQUE/HIPOPERFUSÃO: priorizar estabilização e avaliação de causas reversíveis. "
            "A identificação de BRASH ocorre em paralelo e não deve atrasar o manejo da instabilidade."
        )
    elif pentade:
        risco = "alta_suspeita"
        prioridade = "Constelação completa compatível com BRASH; correlacionar clinicamente e revisar causas concorrentes."
    elif nucleo:
        risco = "fortemente_sugestivo"
        prioridade = (
            "Há bradicardia + disfunção renal + bloqueador nodal AV + hipercalemia, sem choque declarado. "
            "O padrão é fortemente sugestivo, mas BRASH não possui escore diagnóstico validado."
        )
    elif bradicardia and hipercalemia and not bloqueador:
        risco = "diferencial_hipercalemia"
        prioridade = (
            "Bradicardia com hipercalemia sem bloqueador nodal AV declarado: priorizar o diferencial de "
            "hipercalemia e outras causas de bradicardia; não rotular BRASH automaticamente."
        )
    elif bradicardia and bloqueador and dose_excessiva and not renal and not hipercalemia:
        risco = "diferencial_toxicidade"
        prioridade = (
            "Bradicardia com suspeita de dose excessiva/overdose e sem disfunção renal ou hipercalemia: "
            "toxicidade por bloqueador nodal ganha peso no diferencial."
        )
    elif renal and bloqueador and hipercalemia and not bradicardia:
        risco = "substrato_sem_bradicardia"
        prioridade = (
            "Existe substrato renal-farmacológico-metabólico, mas não há bradicardia atual. "
            "Reavaliar tendência e não diagnosticar BRASH sem o componente bradicárdico."
        )
    else:
        risco = "constelacao_incompleta"
        prioridade = "Constelação incompleta para BRASH; interpretar cada componente e seus diferenciais de forma independente."

    if dose_excessiva:
        diferencial_farmaco = (
            "Dose excessiva/overdose foi declarada: considerar toxicidade farmacológica em paralelo; "
            "a ferramenta não escolhe antídoto, cronotrópico ou suporte."
        )
    else:
        diferencial_farmaco = (
            "Sem dose excessiva declarada. BRASH pode ocorrer em uso terapêutico de bloqueador nodal quando "
            "disfunção renal e hipercalemia amplificam a bradicardia."
        )

    return {
        "risco": risco,
        "prioridade": prioridade,
        "constelacao_completa": pentade,
        "nucleo_brash": nucleo,
        "bradicardia": bradicardia,
        "hipercalemia": hipercalemia,
        "gatilhos": gatilhos or ["nenhum componente principal declarado"],
        "diferencial_farmacologico": diferencial_farmaco,
        "ecg": (
            "ECG compatível aumenta a preocupação, mas sua ausência não exclui a interação BRASH/hipercalemia."
            if ecg_hipercalemia
            else "ECG típico de hipercalemia não foi declarado; isso não exclui BRASH nem risco relacionado ao potássio."
        ),
        "nodos_relacionados": [
            "sindrome-brash-bradicardia-insuficiencia-renal-bloqueio-av-choque-e-hipercalemia",
            "fluxograma-sindrome-brash",
            "fluxograma-bradicardia-sintomatica-manejo-agudo",
            "fluxograma-hipercalemia-grave",
            "fluxograma-intoxicacao-por-betabloqueador-ou-antagonista-de-calcio",
        ],
    }


def _interpretar(resultado: dict) -> str:
    return (
        f"{resultado['prioridade']} Gatilhos: {'; '.join(resultado['gatilhos'])}. "
        f"{resultado['ecg']} {resultado['diferencial_farmacologico']}"
    )


_BRASH = Calculator(
    slug="brash-reconhecimento-padrao-uco",
    name="BRASH — reconhecimento de padrão e diferenciais",
    theme="Terapia intensiva",
    purpose=(
        "Reconhece a constelação bradicardia–disfunção renal–bloqueio nodal AV–choque–hipercalemia e "
        "organiza diferenciais sem transformar o acrônimo em escore diagnóstico."
    ),
    fields=[
        Field("frequencia_cardiaca_bpm", "Frequência cardíaca", "number", "bpm", min=20, max=220),
        Field("potassio_mmol_l", "Potássio sérico", "number", "mmol/L", min=2.0, max=9.0),
        Field("lra_ou_agudizacao_drc", "LRA ou agudização de DRC", "boolean"),
        Field("uso_bloqueador_nodal_av", "Uso de bloqueador nodal AV", "boolean"),
        Field("choque_ou_hipoperfusao", "Choque ou hipoperfusão", "boolean"),
        Field("dose_excessiva_ou_overdose_suspeita", "Dose excessiva/overdose suspeita", "boolean"),
        Field("ecg_compativel_hipercalemia", "ECG compatível com efeito da hipercalemia", "boolean"),
        Field("oliguria", "Oligúria", "boolean"),
        Field("gatilho_agudo_desidratacao_infeccao_ou_nefrotoxico", "Gatilho agudo renal/hemodinâmico", "boolean"),
    ],
    compute=_avaliar_brash,
    interpret=_interpretar,
    reference=REFERENCIAS_BRASH,
    kind="assessment",
    limitations=[
        "BRASH não possui escore diagnóstico universalmente validado; esta ferramenta reconhece padrão clínico e não confirma diagnóstico.",
        "Instabilidade hemodinâmica e bradicardia sintomática devem ser manejadas sem aguardar a rotulagem sindrômica.",
        "A ferramenta não calcula dose, concentração, diluição, energia, frequência de pacing ou parâmetros de suporte.",
        "Não seleciona antídoto, cronotrópico, vasopressor, diálise ou terapia para hipercalemia.",
        "Uso de bloqueador nodal não autoriza suspensão definitiva ou reintrodução automática; revisar indicação, função renal e contexto após estabilização.",
        "Hipercalemia isolada e intoxicação por bloqueador nodal permanecem diferenciais concorrentes e podem exigir fluxos próprios em paralelo.",
    ],
)


INTENSIVE_CARE_BRASH_SAFETY_REGISTRY = {_BRASH.slug: _BRASH}
