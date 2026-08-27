"""Avaliação multimodal de perfusão para Cardiologia Intensiva/UCO.

A ferramenta usa lactato como marcador seriado dentro de um conjunto fisiológico.
Não trata lactato isolado como diagnóstico de hipoperfusão, não define meta de
"clearance" e não seleciona fármaco, dispositivo ou intensidade de suporte.
"""

from __future__ import annotations

import math

from .calculators import Calculator, Field


REFERENCIAS_PERFUSAO = (
    "Sinha SS, Morrow DA, Kapur NK, Kataria R, Roswell RO. 2025 Concise Clinical "
    "Guidance: An ACC Expert Consensus Statement on the Evaluation and Management "
    "of Cardiogenic Shock. J Am Coll Cardiol. 2025;85:1618-1641. "
    "doi:10.1016/j.jacc.2025.02.018 — recomenda reavaliação estruturada com exame, "
    "sinais vitais, diurese, creatinina, bicarbonato, pH, saturação venosa, lactato, "
    "função hepática, imagem e hemodinâmica; laboratórios podem ser repetidos a cada "
    "2-4 h na fase precoce/grave e espaçados para 6-8 h quando estabilizado. "
    "Marbach JA et al. Lactate Clearance Is Associated With Improved Survival in "
    "Cardiogenic Shock: A Systematic Review and Meta-Analysis of Prognostic Factor "
    "Studies. J Card Fail. 2021;27:1082-1089. doi:10.1016/j.cardfail.2021.08.012; "
    "PMID:34625128 — associação prognóstica observacional, não alvo terapêutico. "
    "Lindholm MG et al. Serum Lactate and A Relative Change in Lactate as Predictors "
    "of Mortality in Patients With Cardiogenic Shock — CardShock Study. Shock. "
    "2020;53:43-49. doi:10.1097/SHK.0000000000001353; PMID:30973460. "
    "Marbach JA et al. Lactate Clearance as a Surrogate for Mortality in Cardiogenic "
    "Shock: Insights From the DOREMI Trial. J Am Heart Assoc. 2022;11:e023322. "
    "doi:10.1161/JAHA.121.023322; PMID:35261289."
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


def _avaliacao_perfusao(dados: dict) -> dict:
    lactato_atual = float(dados["lactato_atual_mmol_l"])
    lactato_anterior = _numero_opcional(dados, "lactato_anterior_mmol_l")
    intervalo_horas = _numero_opcional(dados, "intervalo_horas")
    pam = _numero_opcional(dados, "pam_mmhg")
    diurese = _numero_opcional(dados, "diurese_ml_kg_h")
    ph = _numero_opcional(dados, "ph")
    scvo2 = _numero_opcional(dados, "scvo2_svo2_pct")

    if not math.isfinite(lactato_atual) or not 0 <= lactato_atual <= 30:
        raise ValueError("Informe lactato atual entre 0 e 30 mmol/L.")
    if lactato_anterior is not None and not 0 <= lactato_anterior <= 30:
        raise ValueError("Informe lactato anterior entre 0 e 30 mmol/L.")
    if (lactato_anterior is None) != (intervalo_horas is None):
        raise ValueError("Para avaliar trajetória, informe lactato anterior e intervalo conjuntamente.")
    if intervalo_horas is not None and not 0.25 <= intervalo_horas <= 48:
        raise ValueError("Informe intervalo entre 0,25 e 48 horas.")
    if pam is not None and not 20 <= pam <= 200:
        raise ValueError("Informe PAM entre 20 e 200 mmHg.")
    if diurese is not None and not 0 <= diurese <= 10:
        raise ValueError("Informe diurese entre 0 e 10 mL/kg/h.")
    if ph is not None and not 6.5 <= ph <= 7.8:
        raise ValueError("Informe pH entre 6,50 e 7,80.")
    if scvo2 is not None and not 20 <= scvo2 <= 100:
        raise ValueError("Informe ScvO₂/SvO₂ entre 20% e 100%.")

    hipoperfusao_clinica = bool(dados.get("hipoperfusao_clinica"))
    suporte_em_escalada = bool(dados.get("suporte_em_escalada"))
    oliguria_lra = bool(dados.get("oliguria_ou_lra"))
    disfuncao_hepatica = bool(dados.get("disfuncao_hepatica"))
    catecolamina_beta = bool(dados.get("catecolamina_beta"))
    pos_parada = bool(dados.get("pos_parada"))
    sepse_choque_misto = bool(dados.get("sepse_ou_choque_misto"))

    variacao_absoluta: float | str = "não calculada"
    variacao_percentual: float | str = "não calculada"
    trajetoria = "sem valor anterior comparável; interpretar o lactato atual no contexto multimodal"

    if lactato_anterior is not None and intervalo_horas is not None:
        variacao = lactato_atual - lactato_anterior
        variacao_absoluta = round(variacao, 2)
        if lactato_anterior > 0:
            pct = (lactato_anterior - lactato_atual) / lactato_anterior * 100
            variacao_percentual = round(pct, 1)
            if pct > 10:
                trajetoria = (
                    f"lactato caiu {pct:.1f}% em {intervalo_horas:g} h; melhora prognóstica possível, "
                    "mas não usar como meta terapêutica isolada"
                )
            elif pct < -10:
                trajetoria = (
                    f"lactato subiu {abs(pct):.1f}% em {intervalo_horas:g} h; sinal de piora ou "
                    "produção/depuração alterada que exige reavaliação multimodal"
                )
            else:
                trajetoria = (
                    f"variação pequena do lactato ({pct:+.1f}%) em {intervalo_horas:g} h; tendência "
                    "isolada é insuficiente para concluir estabilidade"
                )
        else:
            trajetoria = (
                f"lactato anterior zero e atual {lactato_atual:g} mmol/L em {intervalo_horas:g} h; "
                "variação percentual não é matematicamente apropriada"
            )

    sinais_preocupantes: list[str] = []
    if hipoperfusao_clinica:
        sinais_preocupantes.append("hipoperfusão clínica declarada")
    if suporte_em_escalada:
        sinais_preocupantes.append("necessidade de escalada de suporte")
    if oliguria_lra or (diurese is not None and diurese < 0.5):
        sinais_preocupantes.append("oligúria/LRA ou diurese baixa")
    if pam is not None and pam < 65:
        sinais_preocupantes.append("PAM <65 mmHg")
    if ph is not None and ph < 7.30:
        sinais_preocupantes.append("acidemia importante")
    if scvo2 is not None and scvo2 < 60:
        sinais_preocupantes.append("saturação venosa baixa")

    modificadores: list[str] = []
    if catecolamina_beta:
        modificadores.append("estímulo beta-adrenérgico pode elevar produção de lactato")
    if pos_parada:
        modificadores.append("pós-parada pode manter lactato elevado por mecanismo multifatorial")
    if sepse_choque_misto:
        modificadores.append("sepse/choque misto altera produção e utilização de lactato")
    if disfuncao_hepatica:
        modificadores.append("disfunção hepática pode reduzir depuração de lactato")

    lactato_elevado = lactato_atual >= 2
    lactato_muito_elevado = lactato_atual >= 4

    if sinais_preocupantes and (lactato_elevado or suporte_em_escalada):
        prioridade = (
            "REAVALIAÇÃO PRIORITÁRIA: há concordância entre marcador laboratorial e/ou necessidade "
            "de suporte com sinais de perfusão desfavorável. Reclassificar gravidade do choque e "
            "rever exame, causa, hemodinâmica, órgãos e resposta às intervenções."
        )
        fora_da_faixa = True
    elif lactato_muito_elevado and not sinais_preocupantes:
        prioridade = (
            "LACTATO MUITO ELEVADO, MAS SEM CONCORDÂNCIA CLÍNICA DECLARADA: não assumir choque por "
            "um número isolado. Confirmar amostra/tempo e procurar modificadores, mantendo vigilância."
        )
        fora_da_faixa = True
    elif lactato_elevado:
        prioridade = (
            "LACTATO ELEVADO: interpretar a trajetória junto de exame, PAM, diurese, pH, saturação "
            "venosa, função hepática, imagem e hemodinâmica."
        )
        fora_da_faixa = True
    elif sinais_preocupantes:
        prioridade = (
            "SINAIS DE PERFUSÃO DESFAVORÁVEL COM LACTATO NÃO ELEVADO: lactato normal não exclui "
            "choque/hipoperfusão. Priorizar o quadro clínico e a reavaliação estruturada."
        )
        fora_da_faixa = True
    else:
        prioridade = (
            "SEM SINAL MULTIMODAL DE ALARME NOS DADOS INFORMADOS. Isso não equivale a resolução "
            "do choque; manter reavaliação seriada conforme fase clínica."
        )
        fora_da_faixa = False

    if sinais_preocupantes or suporte_em_escalada or lactato_muito_elevado:
        janela_reavaliacao = (
            "Fase precoce/grave: o ACC 2025 admite repetir métricas laboratoriais de perfusão "
            "aproximadamente a cada 2–4 h, individualizando pela instabilidade."
        )
    else:
        janela_reavaliacao = (
            "Quando a condição estabiliza, o ACC 2025 admite espaçar métricas laboratoriais de "
            "perfusão para aproximadamente 6–8 h; mudanças clínicas antecipam a reavaliação."
        )

    return {
        "lactato_atual_mmol_l": round(lactato_atual, 2),
        "variacao_absoluta_mmol_l": variacao_absoluta,
        "variacao_percentual": variacao_percentual,
        "trajetoria": trajetoria,
        "prioridade": prioridade,
        "sinais_multimodais": sinais_preocupantes or ["nenhum sinal adicional informado"],
        "modificadores_lactato": modificadores or ["nenhum modificador declarado"],
        "janela_reavaliacao": janela_reavaliacao,
        "fora_da_faixa": fora_da_faixa,
    }


def _interpretar_perfusao(resultado: dict) -> str:
    return (
        f"Lactato atual {resultado['lactato_atual_mmol_l']} mmol/L. {resultado['trajetoria']}. "
        f"{resultado['prioridade']} Sinais multimodais: "
        f"{'; '.join(resultado['sinais_multimodais'])}. Modificadores: "
        f"{'; '.join(resultado['modificadores_lactato'])}. {resultado['janela_reavaliacao']}"
    )


_TRAJETORIA_PERFUSAO = Calculator(
    slug="trajetoria-perfusao-lactato-uco",
    name="Choque cardiogênico — trajetória de perfusão e lactato seriado",
    theme="Terapia intensiva",
    purpose=(
        "Integra lactato atual e seriado com sinais clínicos e marcadores de perfusão para apoiar "
        "reavaliação do choque sem transformar lactato ou clearance em alvo terapêutico isolado."
    ),
    fields=[
        Field("lactato_atual_mmol_l", "Lactato atual", "number", "mmol/L", min=0, max=30),
        Field("lactato_anterior_mmol_l", "Lactato anterior", "number", "mmol/L", min=0, max=30, required=False),
        Field("intervalo_horas", "Intervalo entre lactatos", "number", "h", min=0.25, max=48, required=False),
        Field("pam_mmhg", "Pressão arterial média", "number", "mmHg", min=20, max=200, required=False),
        Field("diurese_ml_kg_h", "Diurese", "number", "mL/kg/h", min=0, max=10, required=False),
        Field("ph", "pH arterial ou venoso", "number", min=6.5, max=7.8, required=False),
        Field("scvo2_svo2_pct", "ScvO₂ ou SvO₂", "number", "%", min=20, max=100, required=False),
        Field("hipoperfusao_clinica", "Há sinais clínicos de hipoperfusão", "boolean", help="Ex.: alteração do sensório, extremidades frias, enchimento capilar prolongado ou moteamento."),
        Field("suporte_em_escalada", "Há necessidade de escalada de suporte hemodinâmico", "boolean"),
        Field("oliguria_ou_lra", "Há oligúria ou LRA relevante", "boolean"),
        Field("catecolamina_beta", "Uso relevante de estímulo beta-adrenérgico/inotrópico", "boolean"),
        Field("pos_parada", "Contexto pós-parada cardiorrespiratória", "boolean"),
        Field("sepse_ou_choque_misto", "Sepse ou choque misto possível", "boolean"),
        Field("disfuncao_hepatica", "Disfunção hepática relevante", "boolean"),
    ],
    compute=_avaliacao_perfusao,
    interpret=_interpretar_perfusao,
    reference=REFERENCIAS_PERFUSAO,
    kind="assessment",
    limitations=[
        "Lactato elevado é marcador prognóstico e fisiológico inespecífico; não diagnostica sozinho hipoperfusão nem choque cardiogênico.",
        "A variação percentual é exibida como descrição de trajetória. Estudos associam maior queda a melhor prognóstico, mas não validam uma meta universal de clearance como estratégia terapêutica.",
        "Catecolaminas beta-adrenérgicas, pós-parada, sepse/choque misto e disfunção hepática podem modificar produção ou depuração e precisam ser explicitados.",
        "Lactato normal não exclui choque quando exame, diurese, pressão, saturação venosa, função orgânica ou hemodinâmica são desfavoráveis.",
        "A ferramenta não seleciona noradrenalina, inotrópico, vasodilatador, fluido, diurético, Impella, ECMO-VA, BIA, revascularização ou qualquer dose/dispositivo.",
        "A frequência de 2–4 h na fase precoce/grave e 6–8 h após estabilização é referência de reavaliação do ACC 2025, não cronograma rígido; deterioração exige avaliação imediata."
    ],
)


INTENSIVE_CARE_PERFUSION_REGISTRY: dict[str, Calculator] = {
    _TRAJETORIA_PERFUSAO.slug: _TRAJETORIA_PERFUSAO,
}
