# -*- coding: utf-8 -*-
"""Avaliação cardiológica de risco cirúrgico (pré-operatória) — Tarefa 30.

Pedido do Rafael em 30/07/2026: um modelo de documento que não é só texto
fixo com variáveis — o sistema calcula o risco a partir do que o médico
informa (RCRI hoje; Gupta MICA fica com as variáveis coletadas, mas SEM
cálculo automático — ver nota abaixo) e monta a base do laudo, que o médico
então ajusta antes de emitir.

Fontes, todas lidas em fonte primária nesta sessão (30/07/2026):
- RCRI: Lee TH et al. Circulation. 1999;100(10):1043-1049. PMID 10477528.
- Gupta MICA: Gupta PK et al. Circulation. 2011;124(4):381-387. PMID 21730309,
  DOI 10.1161/CIRCULATIONAHA.110.015701.
- ESC/ESAIC 2022: Halvorsen S et al. Eur Heart J. 2022;43(39):3826-3924.
  PMID 36017553, DOI 10.1093/eurheartj/ehac270.
- ACC/AHA 2024: Thompson A et al. Circulation. 2024;150(19):e351-e442.
  PMID 39316661, DOI 10.1161/CIR.0000000000001285.
- SBC 2024: Gualandro DM et al. Arq Bras Cardiol. 2024;121(9):e20240590.
  PMID 39442131, DOI 10.36660/abc.20240590.

**Por que o Gupta MICA entra com as variáveis mas sem probabilidade
calculada:** o artigo original (Circulation 2011) está atrás de paywall —
a pesquisa desta sessão confirmou as 5 variáveis de entrada e os
C-statistics reportados no abstract, mas os COEFICIENTES da regressão
logística só foram encontrados em calculadoras de terceiro (MDCalc,
Omni Calculator), nunca conferidos contra a Tabela do artigo. Regra do
projeto: não computar fórmula não confirmada em fonte primária. As
variáveis do Gupta entram no laudo como registro clínico — sem
percentual —, com o texto literal `VERIFICAÇÃO HUMANA NECESSÁRIA` até
alguém conferir os coeficientes contra o PDF do artigo.
"""
from __future__ import annotations

from app.services import calculators

# Tabela 5 da diretriz ESC/ESAIC 2022 (Eur Heart J. 2022;43(39):3826-3924,
# PMID 36017553) — risco de morte cardiovascular, IAM e AVC em 30 dias,
# considerando só o tipo de procedimento, sem comorbidade do paciente
# (ressalva textual da própria tabela, reproduzida no laudo).
RISCO_CIRURGICO = {
    "baixo": {
        "faixa": "< 1%",
        "procedimentos": [
            "Mama", "Odontológica", "Endócrina (tireoide)", "Oftalmológica",
            "Ginecológica menor", "Ortopédica menor (ex.: meniscectomia)",
            "Reconstrutiva", "Cirurgia superficial",
            "Urológica menor (ex.: RTU de próstata)",
            "Torácica videoassistida — ressecção pulmonar menor",
        ],
    },
    "intermediario": {
        "faixa": "1–5%",
        "procedimentos": [
            "Carótida assintomática (endarterectomia ou stent)",
            "Carótida sintomática (endarterectomia)",
            "Reparo endovascular de aneurisma de aorta (EVAR)",
            "Cirurgia de cabeça e pescoço",
            "Intraperitoneal (esplenectomia, hérnia de hiato, colecistectomia)",
            "Intratorácica não-major", "Neurológica ou ortopédica major (quadril, coluna)",
            "Angioplastia arterial periférica", "Transplante renal",
            "Urológica ou ginecológica major",
        ],
    },
    "alto": {
        "faixa": "> 5%",
        "procedimentos": [
            "Ressecção adrenal", "Cirurgia aórtica e vascular maior",
            "Carótida sintomática (stent)", "Cirurgia duodeno-pancreática",
            "Ressecção hepática, cirurgia de vias biliares", "Esofagectomia",
            "Revascularização aberta de membro por isquemia aguda, ou amputação",
            "Pneumonectomia", "Transplante pulmonar ou hepático",
            "Correção de perfuração intestinal", "Cistectomia total",
        ],
    },
}

CAPACIDADE_FUNCIONAL_OPCOES = {
    "boa": "≥4 METs — sobe dois lances de escada ou equivalente sem sintomas limitantes",
    "reduzida": "<4 METs — não sobe dois lances de escada sem sintomas limitantes",
    "indeterminada": "não avaliável (ex.: limitação ortopédica/neurológica que impede a estimativa)",
}

# Gupta MICA — as 5 variáveis do artigo (Gupta PK et al. Circulation 2011),
# SEM cálculo de probabilidade — ver nota do módulo.
GUPTA_STATUS_FUNCIONAL = ["independente", "parcialmente dependente", "totalmente dependente"]
GUPTA_ASA = ["I", "II", "III", "IV", "V"]


def _linha_rcri(dados: dict) -> str:
    payload = {k: dados.get(k, False) for k in [
        "cirurgia_alto_risco", "doenca_arterial_coronariana",
        "insuficiencia_cardiaca_congestiva", "doenca_cerebrovascular",
        "diabetes_insulinodependente", "creatinina_maior_2",
    ]}
    resultado = calculators.run("rcri", payload)
    return f"RCRI (Índice de Lee): {resultado['interpretation']}", resultado


def _linha_capacidade_funcional(dados: dict) -> str:
    """Prefere o DASI estruturado (12 itens, ACC/AHA 2024 e ESC/ESAIC 2022
    recomendam-no sobre a estimativa clínica subjetiva) quando algum item foi
    respondido; cai para a seleção simples (boa/reduzida/indeterminada)
    quando não."""
    if any(dados.get(c) for c in calculators.DASI_CAMPOS):
        payload = {c: bool(dados.get(c)) for c in calculators.DASI_CAMPOS}
        resultado = calculators.run("dasi", payload)
        return f"Capacidade funcional (DASI): {resultado['interpretation']}"

    capacidade = dados.get("capacidade_funcional", "indeterminada")
    descricao = CAPACIDADE_FUNCIONAL_OPCOES.get(capacidade, "não informada")
    if capacidade == "reduzida":
        nota = (
            " Capacidade funcional reduzida é sinalizada como fator relevante tanto pela "
            "ESC/ESAIC 2022 quanto pela ACC/AHA 2024 na decisão de solicitar avaliação "
            "adicional antes de cirurgia de risco intermediário/alto."
        )
    elif capacidade == "boa":
        nota = " Capacidade funcional adequada — ambas as diretrizes dispensam teste adicional de rotina por este critério isolado."
    else:
        nota = ""
    return f"Capacidade funcional (estimativa clínica): {descricao}.{nota}"


def _linha_risco_cirurgico(categoria: str, procedimento: str) -> str:
    info = RISCO_CIRURGICO.get(categoria)
    if not info:
        return "Risco cirúrgico do procedimento: não classificado."
    return (
        f"Risco cirúrgico do procedimento ({procedimento}): {categoria} "
        f"(risco de morte cardiovascular/IAM/AVC em 30 dias {info['faixa']}, "
        "estimativa baseada só no tipo de procedimento, sem considerar comorbidades — "
        "Tabela 5, ESC/ESAIC 2022)."
    )


def _linha_gupta(dados: dict) -> str | None:
    # `gupta_creatinina_elevada` é booleano com padrão False — não serve de
    # sinal de "seção preenchida" (False de campo nunca tocado é
    # indistinguível de "respondeu que não está elevada"). Só os campos de
    # texto/seleção abaixo indicam que o médico preencheu o bloco do Gupta.
    campos_sinal = ["gupta_idade", "gupta_status_funcional", "gupta_asa",
                    "gupta_tipo_procedimento"]
    if not any((dados.get(c) or "") != "" for c in campos_sinal):
        return None
    partes = [
        f"idade {dados.get('gupta_idade') or 'não informada'} anos",
        f"status funcional {dados.get('gupta_status_funcional') or 'não informado'}",
        f"ASA {dados.get('gupta_asa') or 'não informado'}",
        f"creatinina {'elevada (>1,5 mg/dL)' if dados.get('gupta_creatinina_elevada') else 'não elevada'}",
        f"procedimento: {dados.get('gupta_tipo_procedimento') or 'não informado'}",
    ]
    return (
        "Gupta MICA — variáveis registradas (" + "; ".join(partes) + "). "
        "VERIFICAÇÃO HUMANA NECESSÁRIA: os coeficientes da regressão logística publicada "
        "(Gupta PK et al. Circulation 2011;124(4):381-387) não foram confirmados contra a "
        "fonte primária nesta sessão — o percentual de risco não é calculado automaticamente. "
        "Conferir a Tabela do artigo original antes de estimar a probabilidade."
    )


def montar_rascunho(dados: dict) -> str:
    """Monta o texto-base do laudo, em português, para o médico revisar e ajustar
    antes de emitir. Nunca chamado sem revisão humana — é rascunho, não produto
    final."""
    linhas_rcri, resultado_rcri = _linha_rcri(dados)
    partes = [
        "AVALIAÇÃO CARDIOLÓGICA DE RISCO CIRÚRGICO (PRÉ-OPERATÓRIA)",
        "",
        _linha_risco_cirurgico(dados.get("categoria_risco_cirurgico", ""),
                                dados.get("procedimento_planejado", "não informado")),
        "",
        linhas_rcri,
        "",
        _linha_capacidade_funcional(dados),
    ]

    gupta = _linha_gupta(dados)
    if gupta:
        partes += ["", gupta]

    observacoes = (dados.get("observacoes_adicionais") or "").strip()
    if observacoes:
        partes += ["", f"Observações adicionais: {observacoes}"]

    partes += [
        "",
        "Conduta sugerida (a critério do médico assistente, conforme diretriz adotada pelo "
        "serviço): otimizar terapia medicamentosa recomendada por diretriz antes da cirurgia "
        "quando o tempo permitir; manter betabloqueador e estatina em uso crônico; considerar "
        "avaliação cardiológica adicional (biomarcadores, ecocardiograma) conforme risco "
        "cirúrgico e capacidade funcional, de acordo com ESC/ESAIC 2022 (Eur Heart J. "
        "2022;43(39):3826-3924, PMID 36017553), ACC/AHA 2024 (Circulation. 2024;150(19):"
        "e351-e442, PMID 39316661) e SBC 2024 (Arq Bras Cardiol. 2024;121(9):e20240590, "
        "PMID 39442131).",
        "",
        "Este texto é um rascunho gerado a partir de dados informados pelo médico solicitante "
        "e das referências acima — revisão e ajuste do médico assistente são obrigatórios "
        "antes da emissão.",
    ]
    return "\n".join(partes), resultado_rcri
