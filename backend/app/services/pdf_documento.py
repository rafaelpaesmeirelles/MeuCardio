# -*- coding: utf-8 -*-
"""Geração de PDF dos documentos clínicos — receita, atestado e laudo.

Renderizador escolhido pelo Rafael em 29/07/2026: **ReportLab**, para todos os
documentos do sistema. Python puro, sem biblioteca de sistema, e com controle de
coordenada — que é o que formulário regulado exige, porque os modelos oficiais
têm layout fixo a reproduzir.

Nota de arquitetura que evita uma decisão errada depois: **este módulo não sabe
assinar, e não precisa saber.** A assinatura PAdES é aplicada sobre o PDF pronto,
com `pyHanko` em modo de assinatura interrompida — prepara o campo, entrega o
hash ao assinante remoto e embute o CMS de volta, que é o fluxo do certificado em
nuvem VIDAAS. Renderizar e assinar são camadas separadas de propósito.

O que este módulo **não** faz hoje, e a razão:

- **Não desenha a Notificação de Receita nem a Receita de Controle Especial.**
  Os modelos oficiais têm layout fixo publicado pela Anvisa, e reproduzi-los de
  memória produziria um formulário parecido e inválido. Enquanto o modelo não
  for lido do documento oficial, só o receituário comum é gerado.
- **Não imprime numeração.** Ela vem do SNCR, e o prescritor ainda não está
  cadastrado.
"""
from __future__ import annotations

import io
from datetime import datetime
from zoneinfo import ZoneInfo

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

FUSO = ZoneInfo("America/Sao_Paulo")

# Paleta oficial da Corvia. O `tokens.css` é a fonte da verdade; estes valores
# são a cópia para o PDF, que não consome CSS. Trocar a paleta exige mexer aqui
# também — está registrado no CLAUDE.md junto dos outros três lugares.
NAVY = (0x0B / 255, 0x2E / 255, 0x45 / 255)
CINZA = (0.42, 0.42, 0.42)
LINHA = (0.80, 0.80, 0.80)

MARGEM = 20 * mm
LARGURA, ALTURA = A4


def _cabecalho(c: canvas.Canvas, medico: dict, titulo: str) -> float:
    y = ALTURA - MARGEM
    c.setFillColorRGB(*NAVY)
    c.setFont("Helvetica-Bold", 15)
    c.drawString(MARGEM, y, titulo)

    y -= 7 * mm
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(MARGEM, y, medico.get("full_name") or "")

    y -= 5 * mm
    c.setFillColorRGB(*CINZA)
    c.setFont("Helvetica", 9)
    # Conselho e RQE dão peso ao documento fora da plataforma — é o registro do
    # especialista, e o médico já o preencheu em Minha Conta.
    partes = []
    if medico.get("council_name"):
        partes.append(f"{medico['council_name']}-{medico.get('council_state', '')} "
                      f"{medico.get('council_number', '')}".strip())
    if medico.get("rqe"):
        partes.append(f"RQE {medico['rqe']}")
    if medico.get("specialty"):
        partes.append(medico["specialty"])
    if partes:
        c.drawString(MARGEM, y, "  ·  ".join(partes))

    y -= 4 * mm
    c.setStrokeColorRGB(*LINHA)
    c.setLineWidth(0.7)
    c.line(MARGEM, y, LARGURA - MARGEM, y)
    return y - 9 * mm


def _bloco_paciente(c: canvas.Canvas, y: float, destinatario: dict) -> float:
    c.setFillColorRGB(*CINZA)
    c.setFont("Helvetica", 8.5)
    c.drawString(MARGEM, y, "PACIENTE")
    y -= 5 * mm
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica", 11)
    c.drawString(MARGEM, y, destinatario.get("nome") or "")
    if destinatario.get("endereco"):
        y -= 5 * mm
        c.setFont("Helvetica", 9)
        c.setFillColorRGB(*CINZA)
        c.drawString(MARGEM, y, destinatario["endereco"])
    return y - 9 * mm


def _quebrar(c: canvas.Canvas, texto: str, fonte: str, tam: float, largura: float) -> list[str]:
    """Quebra por largura real do glifo, não por contagem de caractere — nome de
    medicamento e posologia variam demais para estimativa por média."""
    palavras, linhas, atual = texto.split(), [], ""
    for p in palavras:
        teste = f"{atual} {p}".strip()
        if c.stringWidth(teste, fonte, tam) <= largura:
            atual = teste
        else:
            if atual:
                linhas.append(atual)
            atual = p
    if atual:
        linhas.append(atual)
    return linhas or [""]


def _itens(c: canvas.Canvas, y: float, itens: list[dict]) -> float:
    util = LARGURA - 2 * MARGEM
    for n, item in enumerate(itens, start=1):
        if y < 55 * mm:                       # não deixa o item colar no rodapé
            c.showPage()
            y = ALTURA - MARGEM
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica-Bold", 10.5)
        titulo = item.get("descricao") or item.get("substancia") or ""
        if item.get("apresentacao"):
            titulo = f"{titulo} — {item['apresentacao']}"
        for linha in _quebrar(c, f"{n}. {titulo}", "Helvetica-Bold", 10.5, util):
            c.drawString(MARGEM, y, linha)
            y -= 5 * mm
        if item.get("posologia"):
            c.setFont("Helvetica", 10)
            c.setFillColorRGB(0.2, 0.2, 0.2)
            for linha in _quebrar(c, item["posologia"], "Helvetica", 10, util - 6 * mm):
                c.drawString(MARGEM + 6 * mm, y, linha)
                y -= 4.6 * mm
        y -= 3 * mm
    return y


def _rodape(c: canvas.Canvas, medico: dict, via: str | None, aviso: str | None) -> None:
    y = 40 * mm
    c.setStrokeColorRGB(*LINHA)
    c.line(LARGURA / 2 - 35 * mm, y, LARGURA / 2 + 35 * mm, y)
    c.setFillColorRGB(*CINZA)
    c.setFont("Helvetica", 8.5)
    c.drawCentredString(LARGURA / 2, y - 5 * mm, medico.get("full_name") or "")
    c.drawCentredString(LARGURA / 2, y - 9.5 * mm,
                        "Assinatura do prescritor")

    c.setFont("Helvetica", 7.5)
    c.drawString(MARGEM, 22 * mm,
                 datetime.now(FUSO).strftime("Emitido em %d/%m/%Y às %H:%M"))
    if via:
        c.drawRightString(LARGURA - MARGEM, 22 * mm, via)
    if aviso:
        c.setFillColorRGB(0.55, 0.15, 0.15)
        c.setFont("Helvetica-Bold", 7.5)
        c.drawString(MARGEM, 16 * mm, aviso)


def receituario_comum(destinatario: dict, itens: list[dict], medico: dict,
                      observacoes: str = "") -> bytes:
    """Receituário comum, uma via. Retorna os bytes do PDF.

    O aviso de rodapé é deliberado e não deve ser removido enquanto a assinatura
    digital não existir: um PDF com aparência de receita, sem assinatura válida,
    é pior que nenhum documento — o médico precisa saber que ainda tem de assinar.
    """
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    c.setTitle("Receituário")

    y = _cabecalho(c, medico, "Receituário")
    y = _bloco_paciente(c, y, destinatario)
    y = _itens(c, y, itens)

    if observacoes:
        y -= 2 * mm
        c.setFillColorRGB(*CINZA)
        c.setFont("Helvetica", 8.5)
        c.drawString(MARGEM, y, "OBSERVAÇÕES")
        y -= 5 * mm
        c.setFillColorRGB(0.2, 0.2, 0.2)
        c.setFont("Helvetica", 9.5)
        for linha in _quebrar(c, observacoes, "Helvetica", 9.5, LARGURA - 2 * MARGEM):
            c.drawString(MARGEM, y, linha)
            y -= 4.6 * mm

    _rodape(c, medico, None,
            "Documento sem assinatura digital — requer assinatura do prescritor.")
    c.showPage()
    c.save()
    return buf.getvalue()
