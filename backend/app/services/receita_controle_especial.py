# -*- coding: utf-8 -*-
"""Receita de Controle Especial física — modelo Anvisa versão 2.

O modelo vigente foi publicado em 16/03/2026 e tornou-se obrigatório para
impressões realizadas desde 18/05/2026. A saída contém as duas vias, cada uma
com frente e verso. Os demais modelos controlados permanecem fail-closed até
existir numeração oficial/integração SNCR aplicável.
"""
from __future__ import annotations

import io
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas

from app.services.professional_profile import (
    logo_needs_dark_plate_path,
    logo_path,
    professional_name,
)

log = logging.getLogger("meucardio.receita_controle_especial")

LARGURA, ALTURA = A4
MARGEM_X = 14 * mm
MARGEM_Y = 13 * mm
FUSO = ZoneInfo("America/Sao_Paulo")
MODELO_VERSAO = "ANVISA-RCE-V2-2026-03-16"


def _valor(source: Any, nome: str) -> Any:
    if isinstance(source, dict):
        return source.get(nome)
    return getattr(source, nome, None)


def _texto(value: Any) -> str:
    return str(value or "").strip()


def _registro(medico: Any) -> str:
    conselho = _texto(_valor(medico, "council_name"))
    numero = _texto(_valor(medico, "council_number"))
    uf = _texto(_valor(medico, "council_state"))
    if not conselho and _texto(_valor(medico, "crm")):
        return _texto(_valor(medico, "crm"))
    partes = [x for x in (conselho, numero, uf) if x]
    return " ".join(partes)


def _endereco_estruturado_completo(endereco: dict | None) -> bool:
    """A RCE exige endereço profissional completo, não apenas algum texto.

    Logradouro, número, município e UF são o núcleo mínimo verificável do
    endereço estruturado. Bairro, complemento e CEP continuam impressos quando
    cadastrados, mas sua ausência não transforma um endereço identificável em
    inválido.
    """
    return bool(
        endereco
        and all(_texto(endereco.get(campo)) for campo in ("logradouro", "numero", "cidade", "uf"))
    )


def _endereco_completo(endereco: dict | None) -> str:
    if not endereco:
        return ""
    linha = _texto(endereco.get("logradouro"))
    numero = _texto(endereco.get("numero"))
    complemento = _texto(endereco.get("complemento"))
    bairro = _texto(endereco.get("bairro"))
    cidade = _texto(endereco.get("cidade"))
    uf = _texto(endereco.get("uf"))
    cep = _texto(endereco.get("cep"))
    if numero:
        linha = f"{linha}, {numero}" if linha else numero
    if complemento:
        linha = f"{linha} - {complemento}" if linha else complemento
    if bairro:
        linha = f"{linha} - {bairro}" if linha else bairro
    local = f"{cidade}/{uf}" if cidade and uf else cidade or uf
    if cep:
        local = f"{local} - CEP {cep}" if local else f"CEP {cep}"
    return " - ".join(x for x in (linha, local) if x)


def _linhas(texto: str, fonte: str, tamanho: float, largura: float) -> list[str]:
    palavras = texto.split()
    if not palavras:
        return [""]
    resultado: list[str] = []
    atual = ""
    for palavra in palavras:
        candidato = f"{atual} {palavra}".strip()
        if not atual or stringWidth(candidato, fonte, tamanho) <= largura:
            atual = candidato
        else:
            resultado.append(atual)
            atual = palavra
    if atual:
        resultado.append(atual)
    return resultado


def _secao(c: canvas.Canvas, y: float, titulo: str) -> float:
    c.setLineWidth(0.7)
    c.rect(MARGEM_X, y - 7 * mm, LARGURA - 2 * MARGEM_X, 7 * mm, fill=0, stroke=1)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(LARGURA / 2, y - 5.1 * mm, titulo)
    return y - 10 * mm


def _campo(c: canvas.Canvas, y: float, rotulo: str, valor: str = "", *, tamanho: float = 9,
           negrito_rotulo: bool = False, recuo: float = 0, max_linhas: int = 2) -> float:
    x = MARGEM_X + recuo
    c.setFont("Helvetica-Bold" if negrito_rotulo else "Helvetica", tamanho)
    c.drawString(x, y, rotulo)
    largura_rotulo = stringWidth(rotulo, "Helvetica-Bold" if negrito_rotulo else "Helvetica", tamanho)
    if valor:
        fonte = "Helvetica"
        largura = LARGURA - MARGEM_X - (x + largura_rotulo + 2 * mm)
        linhas = _linhas(valor, fonte, tamanho, largura)[:max_linhas]
        for indice, linha in enumerate(linhas):
            c.setFont(fonte, tamanho)
            c.drawString(x + (largura_rotulo + 2 * mm if indice == 0 else 0), y - indice * 4.2 * mm, linha)
        return y - max(1, len(linhas)) * 5 * mm
    return y - 5 * mm


def _logo_profissional(c: canvas.Canvas, medico: Any, x: float, y_topo: float) -> float:
    caminho: Path | None = logo_path(_valor(medico, "document_logo_url"))
    if not caminho:
        return 0.0
    try:
        img = ImageReader(str(caminho))
        largura_px, altura_px = img.getSize()
        largura = 25 * mm
        altura = min(14 * mm, largura * altura_px / max(1, largura_px))
        largura = altura * largura_px / max(1, altura_px)
        escura = logo_needs_dark_plate_path(caminho)
        c.setFillColorRGB(*(0.043, 0.18, 0.27) if escura else (1, 1, 1))
        c.roundRect(x, y_topo - altura - 1.5 * mm, largura + 3 * mm, altura + 3 * mm,
                    2 * mm, fill=1, stroke=0)
        c.drawImage(img, x + 1.5 * mm, y_topo - altura,
                    width=largura, height=altura, preserveAspectRatio=True, mask="auto")
        c.setFillColorRGB(0, 0, 0)
        return largura + 5 * mm
    except (OSError, ValueError):
        log.warning("Logo profissional ilegível em %s; RCE gerada sem a imagem.", caminho)
        return 0.0


def _prescricao(c: canvas.Canvas, y: float, itens: list[dict], observacoes: str,
                *, c5: bool, destinatario: dict, cid: str | None) -> float:
    x = MARGEM_X + 2 * mm
    largura = LARGURA - 2 * MARGEM_X - 4 * mm
    for indice, item in enumerate(itens[:12], start=1):
        descricao = _texto(item.get("descricao") or item.get("substancia"))
        apresentacao = _texto(item.get("apresentacao"))
        posologia = _texto(item.get("posologia"))
        primeira = f"{indice}) {descricao}"
        if apresentacao:
            primeira += f" - {apresentacao}"
        quantidade = _texto(item.get("quantidade"))
        if quantidade:
            primeira += f" - Quantidade: {quantidade}"
        for linha in _linhas(primeira, "Helvetica-Bold", 9.2, largura):
            c.setFont("Helvetica-Bold", 9.2)
            c.drawString(x, y, linha)
            y -= 4.3 * mm
        if posologia:
            for linha in _linhas(posologia, "Helvetica", 8.7, largura - 7 * mm):
                c.setFont("Helvetica", 8.7)
                c.drawString(x + 7 * mm, y, linha)
                y -= 4 * mm
        y -= 2 * mm
        if y < 92 * mm:
            break

    if c5:
        c.setFont("Helvetica-Bold", 8.7)
        c.drawString(x, y, "PRESCRIÇÃO DE ESTEROIDE/PEPTÍDEO ANABOLIZANTE - LISTA C5")
        y -= 4.5 * mm
        y = _campo(c, y, "ENDEREÇO COMPLETO DO PACIENTE:", _texto(destinatario.get("endereco")), tamanho=8.4)
        y = _campo(c, y, "CID:", _texto(cid), tamanho=8.4)
        c.setFont("Helvetica", 7.5)
        c.drawString(x, y, "1ª via retida no estabelecimento por cinco anos, conforme Lei nº 9.965/2000.")
        y -= 4.5 * mm

    if observacoes:
        c.setFont("Helvetica-Bold", 8.3)
        c.drawString(x, y, "OBSERVAÇÕES:")
        y -= 4 * mm
        for linha in _linhas(observacoes, "Helvetica", 8.3, largura):
            c.setFont("Helvetica", 8.3)
            c.drawString(x, y, linha)
            y -= 3.8 * mm
            if y < 88 * mm:
                break
    return y


def _frente(c: canvas.Canvas, *, via: int, destinatario: dict, itens: list[dict],
            observacoes: str, medico: Any, endereco_profissional: dict | None,
            data_emissao: datetime, cid: str | None, c5: bool) -> None:
    y = ALTURA - MARGEM_Y
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(LARGURA / 2, y - 3 * mm, "RECEITA DE CONTROLE ESPECIAL")
    y -= 13 * mm

    y = _secao(c, y, "IDENTIFICAÇÃO DO EMITENTE")
    deslocamento = _logo_profissional(c, medico, MARGEM_X + 2 * mm, y + 1 * mm)
    x_texto = MARGEM_X + 2 * mm + deslocamento
    largura_texto = LARGURA - MARGEM_X - x_texto
    nome_registro = f"{professional_name(medico)} - {_registro(medico)}".strip(" -")
    c.setFont("Helvetica-Bold", 8.8)
    for linha in _linhas(nome_registro, "Helvetica-Bold", 8.8, largura_texto)[:2]:
        c.drawString(x_texto, y, linha)
        y -= 4.2 * mm
    instituicao = _texto(_valor(medico, "workplace_name"))
    if instituicao:
        c.setFont("Helvetica", 8.4)
        for linha in _linhas(instituicao, "Helvetica", 8.4, largura_texto)[:2]:
            c.drawString(x_texto, y, linha)
            y -= 4 * mm
    endereco_linha = _endereco_completo(endereco_profissional)
    if endereco_linha:
        c.setFont("Helvetica", 8.2)
        for linha in _linhas(endereco_linha, "Helvetica", 8.2, largura_texto)[:2]:
            c.drawString(x_texto, y, linha)
            y -= 3.8 * mm
    telefone = _texto((endereco_profissional or {}).get("telefone"))
    if telefone:
        c.setFont("Helvetica", 8.2)
        c.drawString(x_texto, y, f"TELEFONE: {telefone}")
        y -= 3.8 * mm
    if c5:
        c.setFont("Helvetica", 8.2)
        c.drawString(x_texto, y, f"CPF DO PRESCRITOR: {_texto(_valor(medico, 'cpf'))}")
        y -= 4 * mm
    y = min(y, ALTURA - 58 * mm)

    y = _secao(c, y, "IDENTIFICAÇÃO DO PACIENTE")
    y = _campo(c, y, "NOME COMPLETO:", _texto(destinatario.get("nome")), tamanho=9)
    y = _campo(c, y, "ENDEREÇO COMPLETO:", _texto(destinatario.get("endereco")), tamanho=9)
    y = _campo(c, y, "CPF ou, se estrangeiro, PASSAPORTE Nº:",
               _texto(destinatario.get("documento")), tamanho=9)

    y = _secao(c, y - 1 * mm, "PRESCRIÇÃO")
    y = _prescricao(c, y, itens, observacoes, c5=c5, destinatario=destinatario, cid=cid)

    assinatura_y = 76 * mm
    c.rect(MARGEM_X, assinatura_y, LARGURA - 2 * MARGEM_X, 20 * mm, fill=0, stroke=1)
    c.setFont("Helvetica-Bold", 8.8)
    data_local = data_emissao.astimezone(FUSO).strftime("%d/%m/%Y")
    c.drawString(MARGEM_X + 2 * mm, assinatura_y + 14 * mm, f"DATA: {data_local}")
    c.drawString(MARGEM_X + 2 * mm, assinatura_y + 7 * mm,
                 f"IDENTIFICAÇÃO E ASSINATURA DO PRESCRITOR: {professional_name(medico)}")

    y = assinatura_y - 9 * mm
    y = _secao(c, y, "IDENTIFICAÇÃO DO COMPRADOR")
    c.setFont("Helvetica-Oblique", 6.7)
    aviso = ("*IMPRESSÃO OPCIONAL - CONFORME PORTARIA Nº 6/99, ARTIGO 85, ALÍNEA C, "
             "ESSES DADOS PODEM SER APOSTOS MEDIANTE CARIMBO NO VERSO, PELA FARMÁCIA, "
             "NO MOMENTO DA DISPENSAÇÃO.")
    for linha in _linhas(aviso, "Helvetica-Oblique", 6.7, LARGURA - 2 * MARGEM_X):
        c.drawString(MARGEM_X, y, linha)
        y -= 3.1 * mm
    y -= 2 * mm
    for rotulo in ("NOME COMPLETO:", "CPF ou, se estrangeiro, PASSAPORTE Nº:",
                   "ENDEREÇO COMPLETO:", "CIDADE:                                      UF:",
                   "TELEFONE:"):
        y = _campo(c, y, rotulo, tamanho=8.5)

    c.setFont("Helvetica-Oblique", 7.1)
    destino = "1ª via - Retenção pela Farmácia" if via == 1 else "2ª via - Paciente"
    c.drawRightString(LARGURA - MARGEM_X, 14 * mm, destino)
    c.setFont("Helvetica", 6.5)
    c.drawString(
        MARGEM_X, 10 * mm,
        f"DATA DE IMPRESSÃO DESTE RECEITUÁRIO: {data_local} (recomendável)",
    )
    c.setFont("Helvetica", 5.8)
    c.drawString(MARGEM_X, 6 * mm, f"Modelo {MODELO_VERSAO} · via {via}/2")


def _verso(c: canvas.Canvas, *, via: int) -> None:
    y = ALTURA - MARGEM_Y
    c.setFont("Helvetica-Oblique", 7.1)
    aviso = ("VERSO *IMPRESSÃO OPCIONAL - CONFORME PORTARIA Nº 6/99, ARTIGO 85, ALÍNEA C, "
             "ESSES DADOS PODEM SER APOSTOS MEDIANTE CARIMBO PELA FARMÁCIA NO MOMENTO "
             "DA DISPENSAÇÃO.")
    for linha in _linhas(aviso, "Helvetica-Oblique", 7.1, LARGURA - 2 * MARGEM_X):
        c.drawString(MARGEM_X, y, linha)
        y -= 3.5 * mm
    y -= 6 * mm
    y = _secao(c, y, "DADOS DOS PRODUTOS DISPENSADOS")
    for indice in range(1, 4):
        y -= 2 * mm
        y = _campo(c, y, f"{indice})  NOME DO MEDICAMENTO E APRESENTAÇÃO:", tamanho=8.8)
        y = _campo(c, y, "NÚMERO DO LOTE:                                      QUANTIDADE DE CAIXAS:", tamanho=8.6)
        y = _campo(c, y, "NÚMERO DO REGISTRO DA RECEITA NO LIVRO DE RECEITUÁRIO:", tamanho=8.6)
        c.setFont("Helvetica-Oblique", 7.2)
        c.drawString(MARGEM_X + 12 * mm, y + 1.5 * mm, "(QUANDO MEDICAMENTO MANIPULADO)")
        y -= 10 * mm

    y = _secao(c, y, "IDENTIFICAÇÃO DO ESTABELECIMENTO DISPENSADOR")
    y -= 4 * mm
    for rotulo in ("NOME COMPLETO:", "CNPJ ou CNES:",
                   "NOME DO RESPONSÁVEL PELA DISPENSAÇÃO:", "ASSINATURA:", "DATA:"):
        y = _campo(c, y, rotulo, tamanho=8.8)
    c.setFont("Helvetica", 5.8)
    c.drawString(MARGEM_X, 8 * mm, f"Modelo {MODELO_VERSAO} · verso da via {via}/2")


def validar_requisitos_rce(*, medico: Any, destinatario: dict, itens: list[dict],
                           endereco_profissional: dict | None, cid: str | None) -> list[str]:
    """Retorna todos os bloqueios antes de gerar a RCE; não corrige silenciosamente."""
    erros: list[str] = []
    if not _texto(_valor(medico, "full_name")):
        erros.append("Complete o nome do prescritor em Minha conta.")
    if not _registro(medico):
        erros.append("Complete conselho profissional, número de registro e UF.")
    if not _texto(destinatario.get("nome")):
        erros.append("Informe o nome completo do paciente.")
    if not _texto(destinatario.get("endereco")):
        erros.append("Informe o endereço completo do paciente.")
    if not _texto(destinatario.get("documento")):
        erros.append("Informe CPF ou passaporte do paciente.")
    if not itens:
        erros.append("A receita precisa conter ao menos um medicamento.")
    for indice, item in enumerate(itens, start=1):
        quantidade = _texto(item.get("quantidade"))
        extenso = quantidade.split("(", 1)[1].rsplit(")", 1)[0] if "(" in quantidade and ")" in quantidade else ""
        if not re.search(r"\d", quantidade) or not re.search(r"[A-Za-zÀ-ÿ]", extenso):
            erros.append(
                f"Informe a quantidade do item {indice} em algarismos e por extenso "
                "(ex.: 60 comprimidos / sessenta comprimidos)."
            )
    total_c1 = sum(_texto(item.get("lista")).upper() == "C1" for item in itens)
    if total_c1 > 3:
        erros.append(
            "A Receita de Controle Especial pode conter no máximo três substâncias "
            "da Lista C1 (Portaria SVS/MS nº 344/1998, art. 57)."
        )
    if not _endereco_estruturado_completo(endereco_profissional):
        erros.append(
            "Cadastre logradouro, número, município e UF do endereço profissional "
            "para a Receita de Controle Especial."
        )

    tem_c5 = any(_texto(item.get("lista")).upper() == "C5" for item in itens)
    if tem_c5:
        conselho = _texto(_valor(medico, "council_name")).upper()
        if conselho not in {"CRM", "CRO"}:
            erros.append("A Lei nº 9.965/2000 restringe a prescrição de anabolizantes a médico ou dentista (CRM/CRO).")
        if not _texto(_valor(medico, "cpf")):
            erros.append("Cadastre o CPF do prescritor para receita de anabolizantes.")
        if not _texto(cid):
            erros.append("Informe o CID para receita de anabolizantes.")
        if not _texto((endereco_profissional or {}).get("telefone")):
            erros.append("Cadastre o telefone profissional para receita de anabolizantes.")
    return erros


def receita_controle_especial(*, destinatario: dict, itens: list[dict], observacoes: str,
                              medico: Any, endereco_profissional: dict | None,
                              data_emissao: datetime, cid: str | None = None) -> bytes:
    """Gera quatro páginas: frente/verso da via da farmácia e frente/verso da via do paciente."""
    c5 = any(_texto(item.get("lista")).upper() == "C5" for item in itens)
    bloqueios = validar_requisitos_rce(
        medico=medico, destinatario=destinatario, itens=itens,
        endereco_profissional=endereco_profissional, cid=cid,
    )
    if bloqueios:
        raise ValueError(" | ".join(bloqueios))

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4, pageCompression=1)
    pdf.setTitle("Receita de Controle Especial")
    pdf.setAuthor(professional_name(medico))
    pdf.setSubject(MODELO_VERSAO)
    for via in (1, 2):
        _frente(pdf, via=via, destinatario=destinatario, itens=itens,
                observacoes=observacoes, medico=medico,
                endereco_profissional=endereco_profissional,
                data_emissao=data_emissao, cid=cid, c5=c5)
        pdf.showPage()
        _verso(pdf, via=via)
        pdf.showPage()
    pdf.save()
    return buffer.getvalue()
