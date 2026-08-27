"""Fenotipagem segura da falência aguda de ventrículo direito na UCO.

O módulo organiza gravidade, estado volêmico qualitativo e gatilhos de pós-carga
sem escolher fármaco, volume, ventilador ou dispositivo de suporte mecânico.
"""

from __future__ import annotations

from .calculators import Calculator, Field


REFERENCIAS_VD = (
    "Harjola VP et al. Contemporary management of acute right ventricular failure. "
    "Eur J Heart Fail. 2016;18:226-241. doi:10.1002/ejhf.478; "
    "Arrigo M et al. Diagnosis and treatment of right ventricular failure secondary to "
    "acutely increased right ventricular afterload (acute cor pulmonale): ACVC/ESC clinical "
    "consensus statement. Eur Heart J Acute Cardiovasc Care. 2024;13:304-312. "
    "doi:10.1093/ehjacc/zuad157. PMID:38135288."
)


def _avaliar_vd(dados: dict) -> dict:
    disfuncao_vd = bool(dados.get("disfuncao_vd_documentada"))
    choque = bool(dados.get("choque_ou_hipoperfusao"))
    congestao = bool(dados.get("congestao_venosa_ou_pressao_direita_elevada"))
    baixo_enchimento = bool(dados.get("baixo_enchimento_sem_congestao_suspeito"))
    sobrecarga_pressao = bool(dados.get("sobrecarga_aguda_pos_carga_vd_suspeita"))
    pressao_positiva = bool(dados.get("ventilacao_pressao_positiva"))
    hipoxemia_hipercapnia = bool(dados.get("hipoxemia_ou_hipercapnia"))
    tep = bool(dados.get("tep_agudo_suspeito"))
    iam_vd = bool(dados.get("infarto_vd_suspeito"))
    tamponamento = bool(dados.get("tamponamento_suspeito"))
    hp = bool(dados.get("hipertensao_pulmonar_descompensada"))

    gatilhos: list[str] = []
    if disfuncao_vd:
        gatilhos.append("disfunção/dilatação aguda de VD documentada")
    if choque:
        gatilhos.append("choque ou hipoperfusão")
    if congestao:
        gatilhos.append("congestão venosa/pressões direitas elevadas")
    if baixo_enchimento:
        gatilhos.append("baixo enchimento sem congestão suspeito")
    if sobrecarga_pressao:
        gatilhos.append("sobrecarga aguda de pós-carga do VD")
    if pressao_positiva:
        gatilhos.append("ventilação com pressão positiva")
    if hipoxemia_hipercapnia:
        gatilhos.append("hipoxemia/hipercapnia")
    if tep:
        gatilhos.append("TEP agudo suspeito")
    if iam_vd:
        gatilhos.append("infarto de VD suspeito")
    if tamponamento:
        gatilhos.append("tamponamento suspeito")
    if hp:
        gatilhos.append("hipertensão pulmonar descompensada")

    if choque and (disfuncao_vd or sobrecarga_pressao or tep or iam_vd or tamponamento or hp):
        risco = "emergencia_hemodinamica"
        prioridade = (
            "Falência/hemodinâmica direita com choque ou hipoperfusão: estabilização e identificação da causa "
            "devem ocorrer em paralelo. O fenótipo de VD não autoriza atraso de reperfusão, drenagem ou outro "
            "tratamento tempo-dependente quando indicado."
        )
    elif disfuncao_vd or sobrecarga_pressao or tep or iam_vd or tamponamento or hp:
        risco = "avaliacao_prioritaria"
        prioridade = "Há contexto compatível com falência aguda de VD; definir causa, perfusão e estado de enchimento antes de intervir no volume."
    else:
        risco = "informacao_insuficiente"
        prioridade = "Não há confirmação suficiente de falência aguda de VD nesta entrada; correlacionar clínica, ecocardiografia e hemodinâmica."

    if congestao and baixo_enchimento:
        fenotipo_volume = "dados_volumetricos_discordantes"
        volume = (
            "Há marcadores conflitantes de congestão e baixo enchimento. Não recomendar bolus nem restrição por regra; "
            "reavaliar com ecocardiografia/hemodinâmica seriada e contexto ventilatório."
        )
    elif congestao:
        fenotipo_volume = "vd_congesto"
        volume = (
            "Há congestão/pressões direitas elevadas. Expansão volêmica reflexa pode piorar dilatação do VD, "
            "interdependência ventricular e débito; a estratégia de volume deve privilegiar reavaliação de congestão, "
            "sem volume fixo ou diurético automático nesta ferramenta."
        )
    elif baixo_enchimento:
        fenotipo_volume = "possivel_subpreenchimento"
        volume = (
            "Há suspeita de baixo enchimento sem congestão. Reposição cautelosa pode ser considerada apenas com "
            "reavaliação hemodinâmica/eco da resposta; a ferramenta não define volume, velocidade ou alvo de pressão."
        )
    else:
        fenotipo_volume = "volemia_nao_definida"
        volume = (
            "Estado de enchimento não definido. Falência de VD isoladamente não autoriza nem expansão nem restrição de volume."
        )

    if pressao_positiva:
        ventilacao = (
            "Pressão positiva pode reduzir preload e aumentar afterload do VD. Rever impacto de pressões intratorácicas e "
            "oxigenação/ventilação com equipe de terapia intensiva; nenhum ajuste de PEEP, volume corrente ou pressão é calculado aqui."
        )
    else:
        ventilacao = "Sem pressão positiva declarada; manter vigilância para fatores que elevem resistência vascular pulmonar."

    if hipoxemia_hipercapnia:
        ventilacao += " Hipoxemia e hipercapnia podem aumentar resistência vascular pulmonar e agravar pós-carga direita."

    causas: list[str] = []
    if tep:
        causas.append("TEP agudo: manter fluxo diagnóstico/reperfusão específico conforme risco")
    if iam_vd:
        causas.append("infarto de VD: manter fluxo de síndrome coronariana/reperfusão e evitar decisões volêmicas reflexas")
    if tamponamento:
        causas.append("tamponamento: causa obstrutiva tempo-dependente; fluxo específico de drenagem/estabilização")
    if hp:
        causas.append("hipertensão pulmonar descompensada: considerar crise de pós-carga direita e terapia especializada")
    if sobrecarga_pressao and not causas:
        causas.append("procurar causa de aumento agudo de pós-carga: TEP, SDRA/hipóxia, ventilação, pneumonia ou agudo sobre crônico")
    if not causas:
        causas.append("causa precipitante ainda não definida")

    return {
        "risco": risco,
        "prioridade": prioridade,
        "fenotipo_volume": fenotipo_volume,
        "volume": volume,
        "ventilacao": ventilacao,
        "causas_prioritarias": causas,
        "gatilhos": gatilhos or ["nenhum marcador principal declarado"],
        "nodos_relacionados": [
            "falencia-aguda-do-ventriculo-direito-cor-pulmonale-agudo-consenso-acvc-esc-2024",
            "fluxograma-falencia-aguda-de-ventriculo-direito",
        ],
    }


def _interpretar(resultado: dict) -> str:
    return (
        f"{resultado['prioridade']} Fenótipo de volume: {resultado['fenotipo_volume']}. "
        f"{resultado['volume']} {resultado['ventilacao']} "
        f"Causas/fluxos: {'; '.join(resultado['causas_prioritarias'])}."
    )


_FALENCIA_VD = Calculator(
    slug="falencia-vd-fenotipo-hemodinamico-uco",
    name="Falência aguda de VD — fenótipo hemodinâmico seguro",
    theme="Terapia intensiva",
    purpose=(
        "Organiza gravidade, volume e pós-carga na falência aguda de ventrículo direito, evitando expansão ou restrição volêmica reflexa."
    ),
    fields=[
        Field("disfuncao_vd_documentada", "Disfunção/dilatação aguda de VD documentada", "boolean"),
        Field("choque_ou_hipoperfusao", "Choque ou hipoperfusão", "boolean"),
        Field("congestao_venosa_ou_pressao_direita_elevada", "Congestão venosa ou pressões direitas elevadas", "boolean"),
        Field("baixo_enchimento_sem_congestao_suspeito", "Baixo enchimento sem congestão suspeito", "boolean"),
        Field("sobrecarga_aguda_pos_carga_vd_suspeita", "Sobrecarga aguda de pós-carga do VD suspeita", "boolean"),
        Field("ventilacao_pressao_positiva", "Ventilação com pressão positiva", "boolean"),
        Field("hipoxemia_ou_hipercapnia", "Hipoxemia ou hipercapnia", "boolean"),
        Field("tep_agudo_suspeito", "TEP agudo suspeito", "boolean"),
        Field("infarto_vd_suspeito", "Infarto de VD suspeito", "boolean"),
        Field("tamponamento_suspeito", "Tamponamento cardíaco suspeito", "boolean"),
        Field("hipertensao_pulmonar_descompensada", "Hipertensão pulmonar descompensada", "boolean"),
    ],
    compute=_avaliar_vd,
    interpret=_interpretar,
    reference=REFERENCIAS_VD,
    kind="assessment",
    limitations=[
        "Não calcula volume de fluido, velocidade de infusão, meta de pressão ou dose de diurético.",
        "Não seleciona vasopressor, inotrópico, vasodilatador pulmonar ou suporte circulatório mecânico.",
        "Falência de VD não implica expansão nem restrição universal de volume; estado de enchimento deve ser reavaliado serialmente.",
        "Pressão positiva pode modificar preload e afterload; a ferramenta não prescreve PEEP, volume corrente ou pressão inspiratória.",
        "TEP, infarto de VD, tamponamento e outras causas tempo-dependentes mantêm seus fluxos específicos e não devem aguardar esta fenotipagem.",
        "A decisão de suporte mecânico depende de causa, fenótipo, oxigenação, hemodinâmica, reversibilidade e expertise do centro; não é inferida por esta avaliação.",
    ],
)


INTENSIVE_CARE_RV_FAILURE_SAFETY_REGISTRY = {_FALENCIA_VD.slug: _FALENCIA_VD}
