# -*- coding: utf-8 -*-
"""Receita de Controle Especial física — modelo Anvisa versão 2.

O modelo vigente foi publicado em 16/03/2026 e tornou-se obrigatório para
impressões realizadas desde 18/05/2026. A saída contém as duas vias e omite o
verso de impressão opcional destinado ao preenchimento da farmácia. Quando a
prescrição excede uma frente, são geradas páginas de continuação explicitamente
numeradas em cada via.
Os demais modelos controlados permanecem fail-closed até existir numeração
oficial/integração SNCR aplicável.
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
    logo_path,
    professional_name,
)
from app.services.pdf.marca import LOGO, logo_disponivel
from app.services.pdf.identidade_institucional import desenhar_identidade_institucional
from app.services.pdf.wrapping import wrap_text

log = logging.getLogger("meucardio.receita_controle_especial")

LARGURA, ALTURA = A4
MARGEM_X = 14 * mm
MARGEM_Y = 13 * mm
FUSO = ZoneInfo("America/Sao_Paulo")
MODELO_VERSAO = "ANVISA-RCE-V2-2026-03-16"
ALTURA_PRESCRICAO_UTIL = 84 * mm
ALTURA_LINHA_OBSERVACAO = 3.8 * mm
LARGURA_MARCA_CORVIA = 60 * mm
ALTURA_MARCA_CORVIA = 24 * mm
LARGURA_MARCA_PROFISSIONAL = 38 * mm
ALTURA_MARCA_PROFISSIONAL = 34 * mm


def _valor(source: Any, nome: str) -> Any:
    if isinstance(source, dict):
        return source.get(nome)
    return getattr(source, nome, None)


def _texto(value: Any) -> str:
    return str(value or "").strip()


def _registro_legado_completo(valor: str) -> tuple[str, str, str] | None:
    """Interpreta apenas registros legados que contenham conselho, número e UF."""
    texto = _texto(valor).upper()
    if not texto:
        return None
    padrao = re.compile(
        r"^(?P<conselho>[A-Z]{2,10})\s*"
        r"(?:[-/]\s*(?P<uf_antes>[A-Z]{2}))?\s*"
        r"(?P<numero>\d[0-9A-Z.\-]*)\s*"
        r"(?:[/\-\s]+(?P<uf_depois>[A-Z]{2}))?$"
    )
    match = padrao.fullmatch(texto)
    if not match:
        return None
    conselho = match.group("conselho")
    numero = match.group("numero")
    uf = match.group("uf_antes") or match.group("uf_depois")
    if not (conselho and numero and uf):
        return None
    return conselho, numero, uf


def _registro_componentes(medico: Any) -> tuple[str, str, str]:
    conselho = _texto(_valor(medico, "council_name")).upper()
    numero = _texto(_valor(medico, "council_number"))
    uf = _texto(_valor(medico, "council_state")).upper()
    if conselho or numero or uf:
        return conselho, numero, uf
    legado = _registro_legado_completo(_texto(_valor(medico, "crm")))
    return legado or ("", "", "")


def _registro(medico: Any) -> str:
    conselho, numero, uf = _registro_componentes(medico)
    if not all((conselho, numero, uf)):
        return ""
    return f"{conselho} {numero}/{uf}"


def _endereco_estruturado_completo(endereco: dict | None) -> bool:
    """A RCE exige endereço profissional completo, não apenas algum texto."""
    return bool(
        endereco
        and all(_texto(endereco.get(campo)) for campo in ("logradouro", "numero", "cidade", "uf"))
    )


def _endereco_paciente_completo(endereco: str | None) -> bool:
    """Confere os componentes que precisam acompanhar uma RCE.

    O destinatário continua cifrado em um único campo para preservar o schema e
    documentos existentes. Novas receitas serializam o endereço no formato
    canônico ``logradouro, número - bairro - cidade/UF - CEP 00000-000``.
    """
    texto = _texto(endereco)
    return bool(
        re.search(r"\b\d{5}-?\d{3}\b", texto)
        and re.search(r"/\s*[A-Z]{2}\b", texto.upper())
        and re.search(r",\s*\S+", texto)
        and texto.count(" - ") >= 3
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
    return wrap_text(texto, largura, lambda linha: stringWidth(linha, fonte, tamanho))


def _secao(c: canvas.Canvas, y: float, titulo: str) -> float:
    c.setLineWidth(0.7)
    c.rect(MARGEM_X, y - 7 * mm, LARGURA - 2 * MARGEM_X, 7 * mm, fill=0, stroke=1)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(LARGURA / 2, y - 5.1 * mm, titulo)
    return y - 10 * mm


def _campo(c: canvas.Canvas, y: float, rotulo: str, valor: str = "", *, tamanho: float = 9,
           negrito_rotulo: bool = False, recuo: float = 0, max_linhas: int | None = None) -> float:
    x = MARGEM_X + recuo
    c.setFont("Helvetica-Bold" if negrito_rotulo else "Helvetica", tamanho)
    c.drawString(x, y, rotulo)
    largura_rotulo = stringWidth(rotulo, "Helvetica-Bold" if negrito_rotulo else "Helvetica", tamanho)
    if valor:
        fonte = "Helvetica"
        largura = LARGURA - MARGEM_X - (x + largura_rotulo + 2 * mm)
        linhas = _linhas(valor, fonte, tamanho, largura)
        for indice, linha in enumerate(linhas):
            c.setFont(fonte, tamanho)
            c.drawString(x + (largura_rotulo + 2 * mm if indice == 0 else 0), y - indice * 4.2 * mm, linha)
        return y - max(1, len(linhas)) * 5 * mm
    return y - 5 * mm


def _logo_profissional(c: canvas.Canvas, medico: Any, x: float, y_topo: float,
                       *, altura_area: float = ALTURA_MARCA_PROFISSIONAL) -> float:
    caminho: Path | None = logo_path(_valor(medico, "document_logo_url"))
    if not caminho:
        return 0.0
    try:
        img = ImageReader(str(caminho))
        largura_px, altura_px = img.getSize()
        escala = min(LARGURA_MARCA_PROFISSIONAL / max(1, largura_px),
                     ALTURA_MARCA_PROFISSIONAL / max(1, altura_px))
        largura, altura = largura_px * escala, altura_px * escala
        y_topo -= max(0, altura_area - altura) / 2
        x -= largura / 2
        c.setFillColorRGB(1, 1, 1)
        c.rect(x, y_topo - altura, largura, altura, fill=1, stroke=0)
        c.drawImage(img, x, y_topo - altura,
                    width=largura, height=altura, preserveAspectRatio=True, mask="auto")
        c.setFillColorRGB(0, 0, 0)
        return altura
    except (OSError, ValueError):
        log.warning("Logo profissional ilegível em %s; RCE gerada sem a imagem.", caminho)
        return 0.0


def _logo_corvia(c: canvas.Canvas, x: float, y_topo: float,
                 *, altura_area: float = ALTURA_MARCA_PROFISSIONAL) -> float:
    """Desenha a marca e retorna sua altura real, sem mudar a escala dos callers."""
    if not logo_disponivel():
        return 0.0
    try:
        img = ImageReader(str(LOGO))
        largura_px, altura_px = img.getSize()
        largura_maxima = LARGURA_MARCA_CORVIA
        altura_maxima = ALTURA_MARCA_CORVIA
        escala = min(largura_maxima / max(1, largura_px), altura_maxima / max(1, altura_px))
        largura = largura_px * escala
        altura = altura_px * escala
        y_topo -= max(0, altura_area - altura) / 2
        c.drawImage(
            img, x, y_topo - altura, width=largura, height=altura,
            preserveAspectRatio=True, mask="auto",
        )
        return altura
    except (OSError, ValueError):
        log.warning("Logo institucional ilegível; RCE gerada sem a marca Corvia.")
        return 0.0


def _texto_item(indice: int, item: dict) -> tuple[str, str]:
    descricao = _texto(item.get("descricao") or item.get("substancia"))
    apresentacao = _texto(item.get("apresentacao"))
    primeira = f"{indice}) {descricao}"
    if apresentacao:
        primeira += f" - {apresentacao}"
    quantidade = _texto(item.get("quantidade"))
    if quantidade:
        primeira += f" - Quantidade: {quantidade}"
    orientacao = _texto(item.get("orientacao"))
    instrucoes = [_texto(item.get("posologia"))]
    if orientacao:
        instrucoes.append(f"Orientações: {orientacao}")
    return primeira, "\n".join(filter(None, instrucoes))


def _linhas_item(indice: int, item: dict, largura: float) -> tuple[list[str], list[str]]:
    if "_linhas_titulo" in item:
        return item["_linhas_titulo"], item["_linhas_posologia"]
    primeira, posologia = _texto_item(indice, item)
    return (_linhas(primeira, "Helvetica-Bold", 9.2, largura),
            _linhas(posologia, "Helvetica", 8.7, largura - 7 * mm) if posologia else [])


def _altura_item(indice: int, item: dict, largura: float) -> float:
    titulo, posologia = _linhas_item(indice, item, largura)
    return len(titulo) * 4.3 * mm + len(posologia) * 4 * mm + 2 * mm


def _paginar_prescricao(itens: list[dict], observacoes: str, *, c5: bool,
                       capacidade: float = ALTURA_PRESCRICAO_UTIL,
                       altura_c5: float = 27 * mm) -> list[dict]:
    """Mede e reparte inclusive um único item maior que a página."""
    largura = LARGURA - 2 * MARGEM_X - 4 * mm
    if capacidade < 20 * mm or (c5 and altura_c5 > capacidade):
        raise ValueError("A identificação excede o espaço do formulário. Revise os dados e o endereço antes de emitir.")
    paginas: list[dict] = []

    def nova():
        pagina = {"itens": [], "altura_usada": 0.0, "c5": False, "observacoes": []}
        paginas.append(pagina)
        return pagina

    pagina = nova()
    for indice, item in enumerate(itens, start=1):
        titulos, doses = _linhas_item(indice, item, largura)
        altura = _altura_item(indice, item, largura)
        if pagina["altura_usada"] and pagina["altura_usada"] + min(altura, capacidade) > capacidade:
            pagina = nova()
        linhas = [(True, linha, 4.3 * mm) for linha in titulos]
        linhas += [(False, linha, 4 * mm) for linha in doses]
        continuacao = False
        while linhas:
            titulo = [f"{indice}) Continuação do item"] if continuacao else []
            posologia: list[str] = []
            usada = 2 * mm + (4.3 * mm if continuacao else 0)
            while linhas and pagina["altura_usada"] + usada + linhas[0][2] <= capacidade:
                negrito, linha, altura_linha = linhas.pop(0)
                (titulo if negrito else posologia).append(linha)
                usada += altura_linha
            pagina["itens"].append((indice, {"_linhas_titulo": titulo, "_linhas_posologia": posologia}))
            pagina["altura_usada"] += usada
            if linhas:
                pagina = nova()
                continuacao = True

    if c5:
        if pagina["altura_usada"] + altura_c5 > capacidade:
            pagina = nova()
        pagina["c5"] = True
        pagina["altura_usada"] += altura_c5

    linhas = _linhas(observacoes, "Helvetica", 8.3, largura) if _texto(observacoes) else []
    while linhas:
        disponivel = capacidade - pagina["altura_usada"] - 8 * mm
        quantidade = int(disponivel // ALTURA_LINHA_OBSERVACAO)
        if quantidade <= 0:
            pagina = nova()
            continue
        trecho, linhas = linhas[:quantidade], linhas[quantidade:]
        pagina["observacoes"].extend(trecho)
        pagina["altura_usada"] += 8 * mm + len(trecho) * ALTURA_LINHA_OBSERVACAO
    return paginas


def _prescricao(c: canvas.Canvas, y: float, itens: list[tuple[int, dict]],
                observacoes_linhas: list[str], *, c5: bool,
                destinatario: dict, cid: str | None) -> float:
    x = MARGEM_X + 2 * mm
    largura = LARGURA - 2 * MARGEM_X - 4 * mm
    for indice, item in itens:
        titulos, posologia = _linhas_item(indice, item, largura)
        for linha in titulos:
            c.setFont("Helvetica-Bold", 9.2)
            c.drawString(x, y, linha)
            y -= 4.3 * mm
        if posologia:
            for linha in posologia:
                c.setFont("Helvetica", 8.7)
                c.drawString(x + 7 * mm, y, linha)
                y -= 4 * mm
        y -= 2 * mm

    if c5:
        c.setFont("Helvetica-Bold", 8.7)
        c.drawString(x, y, "PRESCRIÇÃO DE ESTEROIDE/PEPTÍDEO ANABOLIZANTE - LISTA C5")
        y -= 4.5 * mm
        y = _campo(c, y, "ENDEREÇO COMPLETO DO PACIENTE:", _texto(destinatario.get("endereco")), tamanho=8.4)
        y = _campo(c, y, "CID:", _texto(cid), tamanho=8.4)
        c.setFont("Helvetica", 7.5)
        c.drawString(x, y, "1ª via retida no estabelecimento por cinco anos, conforme Lei nº 9.965/2000.")
        y -= 4.5 * mm

    if observacoes_linhas:
        c.setFont("Helvetica-Bold", 8.3)
        c.drawString(x, y, "OBSERVAÇÕES:")
        y -= 4 * mm
        for linha in observacoes_linhas:
            c.setFont("Helvetica", 8.3)
            c.drawString(x, y, linha)
            y -= ALTURA_LINHA_OBSERVACAO
    return y


def _cabecalho_receita(c: canvas.Canvas, *, medico: Any, destinatario: dict,
                      endereco_profissional: dict | None, c5: bool,
                      pagina: int, total_paginas: int) -> float:
    y = ALTURA - MARGEM_Y
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(LARGURA / 2, y - 3 * mm, "RECEITA DE CONTROLE ESPECIAL")
    c.setFont("Helvetica-Bold", 8.2)
    c.drawRightString(LARGURA - MARGEM_X, y - 3 * mm, f"PÁGINA {pagina}/{total_paginas}")
    if pagina > 1:
        c.setFont("Helvetica-Bold", 8.2)
        c.drawCentredString(LARGURA / 2, y - 8 * mm, "CONTINUAÇÃO")
    y -= 13 * mm

    y = _secao(c, y, "IDENTIFICAÇÃO DO EMITENTE")
    topo_identidade = y
    direita = LARGURA - MARGEM_X - 3 * mm
    largura_texto = 66 * mm
    campos = [
        (professional_name(medico), "Helvetica-Bold", 8.8),
        (_registro(medico), "Helvetica", 8.2),
        (_texto(_valor(medico, "profession")), "Helvetica", 8.2),
        (_texto(_valor(medico, "specialty")), "Helvetica", 8.2),
    ]
    if bool(_valor(medico, "include_workplace_on_documents")):
        campos.extend((_texto(_valor(medico, chave)), "Helvetica", 8.2)
                      for chave in ("workplace_name", "workplace_department", "workplace_role", "workplace_notes"))
    campos.append((_endereco_completo(endereco_profissional), "Helvetica", 8.2))
    telefone = _texto((endereco_profissional or {}).get("telefone"))
    if telefone:
        campos.append((f"TELEFONE: {telefone}", "Helvetica", 8.2))
    if c5:
        campos.append((f"CPF DO PRESCRITOR: {_texto(_valor(medico, 'cpf'))}", "Helvetica", 8.2))
    linhas_identidade = []
    for texto, fonte, tamanho in campos:
        if texto:
            for linha in _linhas(texto, fonte, tamanho, largura_texto):
                linhas_identidade.append((linha, fonte, tamanho))
    # The operator's legal text belongs directly below its own logo, entirely
    # within the left column. Both marks share the same vertical image center;
    # the frame grows to the tallest complete column, not to a full-width band.
    esquerda = MARGEM_X + 3 * mm
    topo_marcas = topo_identidade + 1 * mm
    altura_corvia = _logo_corvia(c, esquerda, topo_marcas)
    base_corvia = topo_marcas - altura_corvia
    if altura_corvia:
        base_corvia -= max(0, ALTURA_MARCA_PROFISSIONAL - altura_corvia) / 2
    base_empresa = desenhar_identidade_institucional(
        c, esquerda, base_corvia - 4 * mm, LARGURA_MARCA_CORVIA,
    )
    altura_identidade = max(
        ALTURA_MARCA_PROFISSIONAL, len(linhas_identidade) * 4 * mm,
        topo_identidade - base_empresa,
    )
    centro_profissional = MARGEM_X + 3 * mm + LARGURA_MARCA_CORVIA + 6 * mm + LARGURA_MARCA_PROFISSIONAL / 2
    _logo_profissional(c, medico, centro_profissional, topo_marcas)
    for linha, fonte, tamanho in linhas_identidade:
        c.setFont(fonte, tamanho)
        c.drawRightString(direita, y, linha)
        y -= 4 * mm
    y = min(y, topo_identidade - altura_identidade - 2 * mm)
    c.rect(MARGEM_X, y, LARGURA - 2 * MARGEM_X,
           topo_identidade + 3 * mm - y, fill=0, stroke=1)

    y = _secao(c, y, "IDENTIFICAÇÃO DO PACIENTE")
    y = _campo(c, y, "NOME COMPLETO:", _texto(destinatario.get("nome")), tamanho=9)
    y = _campo(c, y, "ENDEREÇO COMPLETO:", _texto(destinatario.get("endereco")), tamanho=9)
    y = _campo(c, y, "CPF ou, se estrangeiro, PASSAPORTE Nº:",
               _texto(destinatario.get("documento")), tamanho=9)

    y = _secao(c, y - 1 * mm, "PRESCRIÇÃO")
    return y


def _frente(c: canvas.Canvas, *, via: int, pagina: int, total_paginas: int,
            destinatario: dict, itens: list[tuple[int, dict]], observacoes_linhas: list[str],
            medico: Any, endereco_profissional: dict | None, data_emissao: datetime,
            cid: str | None, c5: bool, assinatura_digital: bool, emitente_c5: bool = False) -> None:
    y = _cabecalho_receita(c, medico=medico, destinatario=destinatario,
                           endereco_profissional=endereco_profissional, c5=emitente_c5,
                           pagina=pagina, total_paginas=total_paginas)
    _prescricao(
        c, y, itens, observacoes_linhas, c5=c5,
        destinatario=destinatario, cid=cid,
    )

    assinatura_y = 76 * mm
    c.rect(MARGEM_X, assinatura_y, LARGURA - 2 * MARGEM_X, 20 * mm, fill=0, stroke=1)
    c.setFont("Helvetica-Bold", 8.8)
    data_local = data_emissao.astimezone(FUSO).strftime("%d/%m/%Y")
    c.drawString(MARGEM_X + 2 * mm, assinatura_y + 14 * mm, f"DATA: {data_local}")
    identificacao = f"PRESCRITOR: {professional_name(medico)}"
    largura_identificacao = 78 * mm if assinatura_digital else LARGURA - 2 * MARGEM_X - 4 * mm
    c.setFont("Helvetica", 8.8)
    for indice, linha in enumerate(_linhas(
        identificacao, "Helvetica", 8.8, largura_identificacao,
    )[:2]):
        c.drawString(MARGEM_X + 2 * mm, assinatura_y + (7 - indice * 3.7) * mm, linha)
    if assinatura_digital:
        c.setFont("Helvetica", 6.6)
        aviso_assinatura = (
            "O selo ao lado integra a assinatura qualificada deste PDF."
            if via == 1
            else "Esta via integra o mesmo PDF assinado; valide a assinatura no arquivo digital."
        )
        c.drawString(MARGEM_X + 2 * mm, assinatura_y + 1.8 * mm, aviso_assinatura)

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
    c.drawString(MARGEM_X, 10 * mm, f"DATA DE IMPRESSÃO DESTE RECEITUÁRIO: {data_local} (recomendável)")
    c.setFont("Helvetica", 5.8)
    c.drawString(
        MARGEM_X, 6 * mm,
        f"Modelo {MODELO_VERSAO} · via {via}/2 · PÁGINA {pagina}/{total_paginas}",
    )


def _verso(c: canvas.Canvas, *, via: int, pagina: int, total_paginas: int) -> None:
    y = ALTURA - MARGEM_Y
    c.setFont("Helvetica-Bold", 8.2)
    c.drawRightString(LARGURA - MARGEM_X, y, f"PÁGINA {pagina}/{total_paginas}")
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
    c.drawString(
        MARGEM_X, 8 * mm,
        f"Modelo {MODELO_VERSAO} · verso da via {via}/2 · PÁGINA {pagina}/{total_paginas}",
    )


def validar_requisitos_rce(*, medico: Any, destinatario: dict, itens: list[dict],
                           endereco_profissional: dict | None, cid: str | None) -> list[str]:
    """Retorna todos os bloqueios antes de gerar a RCE; não corrige silenciosamente."""
    erros: list[str] = []
    if not _texto(_valor(medico, "full_name")):
        erros.append("Complete o nome do prescritor em Minha conta.")
    conselho, numero, uf = _registro_componentes(medico)
    if not all((conselho, numero, uf)):
        erros.append("Complete conselho profissional, número de registro e UF.")
    if not _texto(destinatario.get("nome")):
        erros.append("Informe o nome completo do paciente.")
    if not _endereco_paciente_completo(destinatario.get("endereco")):
        erros.append(
            "Informe logradouro, número, bairro, cidade, UF e CEP do paciente."
        )
    if not _texto(destinatario.get("documento")):
        erros.append("Informe o CPF do paciente.")
    if not itens:
        erros.append("A receita precisa conter ao menos um medicamento.")
    for indice, item in enumerate(itens, start=1):
        if item.get("uso_continuo"):
            erros.append(
                f"Uso contínuo não dispensa a quantidade regulamentar do item {indice} "
                "em Receita de Controle Especial."
            )
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
                              data_emissao: datetime, cid: str | None = None,
                              metodo_assinatura: str = "MANUAL") -> bytes:
    """Gera as duas vias, sem o verso opcional de uso do dispensador."""
    c5 = any(_texto(item.get("lista")).upper() == "C5" for item in itens)
    bloqueios = validar_requisitos_rce(
        medico=medico, destinatario=destinatario, itens=itens,
        endereco_profissional=endereco_profissional, cid=cid,
    )
    if bloqueios:
        raise ValueError(" | ".join(bloqueios))

    medicao = canvas.Canvas(io.BytesIO(), pagesize=A4)
    topo_prescricao = _cabecalho_receita(
        medicao, medico=medico, destinatario=destinatario,
        endereco_profissional=endereco_profissional, c5=c5, pagina=1, total_paginas=1,
    )
    # The signature box starts at 96 mm. Keep a full line of clearance above it.
    capacidade = min(ALTURA_PRESCRICAO_UTIL, topo_prescricao - 101 * mm)
    altura_c5 = -_prescricao(medicao, 0, [], [], c5=c5, destinatario=destinatario, cid=cid)
    paginas = _paginar_prescricao(itens, observacoes, c5=c5,
                                 capacidade=capacidade, altura_c5=altura_c5)
    total_paginas = len(paginas)
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4, pageCompression=1)
    pdf.setTitle("Receita de Controle Especial")
    pdf.setAuthor(professional_name(medico))
    pdf.setSubject(MODELO_VERSAO)
    for via in (1, 2):
        for numero_pagina, conteudo in enumerate(paginas, start=1):
            _frente(
                pdf, via=via, pagina=numero_pagina, total_paginas=total_paginas,
                destinatario=destinatario, itens=conteudo["itens"],
                observacoes_linhas=conteudo["observacoes"], medico=medico,
                endereco_profissional=endereco_profissional, data_emissao=data_emissao,
                cid=cid, c5=bool(conteudo["c5"]),
                assinatura_digital=metodo_assinatura == "A1_ARQUIVO", emitente_c5=c5,
            )
            pdf.showPage()
    pdf.save()
    return buffer.getvalue()
