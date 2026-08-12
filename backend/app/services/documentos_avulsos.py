"""Documentos gerados SEM modelo prévio (12/08/2026, pedido do Rafael):
solicitação de exames, atestado médico rápido e documento em branco.

Os três reaproveitam por inteiro a infraestrutura de `GeneratedDocument` já
existente para documento gerado a partir de `DocumentTemplate`
(`app/api/documents.py`) — mesma tabela, mesmo gerador de PDF
(`app.services.pdf_documento.documento_generico`), mesmo fluxo de
assinatura/e-mail/"recriar baseado neste". Este módulo só monta o TEXTO do
corpo (`rendered_body`); nenhuma função de PDF nova foi criada.

`EXAMES_SUGERIDOS` é uma lista estática de sugestão, agrupada por
categoria — nunca um catálogo fechado: o campo de exame do formulário
sempre aceita texto livre além dela (regra permanente do produto: nunca um
campo clínico dependente de catálogo fixo). Integração com Knowledge Graph
(exames relacionados por doença) e "CorvIA monte a solicitação" ficam de
propósito fora desta rodada — são as duas melhorias futuras citadas no
pedido original.
"""
from __future__ import annotations

from datetime import date

EXAMES_SUGERIDOS: dict[str, list[str]] = {
    "Laboratoriais": [
        "Hemograma completo", "Creatinina", "Ureia", "Sódio", "Potássio",
        "TSH", "T4 livre", "NT-proBNP", "Troponina", "Perfil lipídico completo",
        "Glicemia de jejum", "Hemoglobina glicada (HbA1c)",
        "Coagulograma (TAP/TTPA/INR)", "Proteína C reativa",
    ],
    "Cardiologia": [
        "Eletrocardiograma (ECG)", "Ecocardiograma transtorácico", "Holter 24h",
        "MAPA", "Teste ergométrico", "Ecocardiograma transesofágico",
        "Teste cardiopulmonar de exercício (TCPE)", "Ecocardiograma de estresse",
    ],
    "Radiologia/imagem": [
        "Radiografia de tórax", "Ressonância cardíaca", "Angiotomografia de coronárias",
        "Tomografia de tórax", "Escore de cálcio coronariano",
        "Angiotomografia de aorta",
    ],
    "Ultrassonografia": [
        "Ultrassonografia de abdome total", "Doppler venoso de membros inferiores",
        "Doppler de artérias renais", "Ultrassom com doppler de carótidas e vertebrais",
        "Ecocardiograma fetal",
    ],
    "Medicina nuclear": [
        "Cintilografia miocárdica de perfusão", "PET-CT cardíaco",
    ],
    "Endoscopia": [
        "Endoscopia digestiva alta", "Colonoscopia",
    ],
    "Neurologia": [
        "Eletroencefalograma", "Doppler transcraniano",
    ],
    "Pneumologia": [
        "Espirometria", "Polissonografia",
    ],
    "Outros": [],
}

TITULO_SOLICITACAO_EXAMES = "Solicitação de Exames"


def montar_corpo_solicitacao_exames(
    exames: list[str],
    indicacao: str | None,
    cid: str | None,
    prioridade: str,
    observacoes: str | None,
    patient_name: str | None,
) -> str:
    linhas: list[str] = []
    if patient_name:
        linhas.append(f"Paciente: {patient_name}")
        linhas.append("")
    linhas.append("Solicito a realização dos seguintes exames:")
    linhas.append("")
    linhas.extend(f"- {e}" for e in exames)
    if indicacao:
        linhas.append("")
        linhas.append(f"Indicação clínica: {indicacao}")
    if cid:
        linhas.append(f"CID: {cid}")
    if prioridade == "urgente":
        linhas.append("")
        linhas.append("Prioridade: URGENTE")
    if observacoes:
        linhas.append("")
        linhas.append(f"Observações: {observacoes}")
    return "\n".join(linhas)


def _fmt(d: date) -> str:
    return d.strftime("%d/%m/%Y")


def montar_corpo_atestado(
    patient_name: str | None,
    dias_afastamento: int | None,
    data_inicio: date | None,
    data_fim: date | None,
    cid: str | None,
    observacoes: str | None,
) -> str:
    """`dias_afastamento` (com `data_inicio` opcional) OU `data_inicio` +
    `data_fim` — a validação de que pelo menos um dos dois está presente é
    feita na rota (`AtestadoRapidoIn`), não aqui: este helper só formata o
    que já chegou validado."""
    nome = patient_name or "acima identificado(a)"
    if data_inicio and data_fim:
        dias = (data_fim - data_inicio).days + 1
        periodo = f"no período de {_fmt(data_inicio)} a {_fmt(data_fim)} ({dias} dia(s))"
    elif dias_afastamento:
        periodo = f"por {dias_afastamento} dia(s)"
        if data_inicio:
            periodo += f", a partir de {_fmt(data_inicio)}"
    else:
        periodo = "por período a ser definido"

    linhas = [
        f"Atesto, para os devidos fins, que o(a) paciente {nome} necessita de "
        f"afastamento de suas atividades habituais {periodo}."
    ]
    if cid:
        linhas.append("")
        linhas.append(f"CID: {cid}")
    if observacoes:
        linhas.append("")
        linhas.append(f"Observações: {observacoes}")
    return "\n".join(linhas)
