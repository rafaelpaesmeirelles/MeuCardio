"""Modo apresentação: exporta conteúdo publicado para aula e round.

A exportação altera somente a diagramação. O texto clínico continua vindo do
registro publicado; a anotação do apresentador fica em página própria e nunca é
persistida como conteúdo da plataforma.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

from app.models.content import Document
from app.services.professional_profile import (
    professional_name, rendered_logo_png, workplace_lines,
)

from .pdf import Apresentacao
from .pdf import arvore as arv
from .pdf.marca import NAVY, NEUTRO, TEAL, TINTA, TINTA_TEAL, TINTA_VERMELHA, VERMELHO

MARCADORES_POR_PAGINA = 6


def _limpar(texto: str) -> str:
    texto = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", texto)
    texto = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", texto)
    texto = re.sub(r"\*\*([^*]+)\*\*", r"\1", texto)
    texto = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"\1", texto)
    texto = re.sub(r"`([^`]+)`", r"\1", texto)
    texto = re.sub(r"<br\s*/?>", " · ", texto, flags=re.I)
    return re.sub(r"\s+", " ", texto).strip()


def _fragmentar(texto: str, limite: int = 300) -> list[str]:
    """Divide parágrafos longos sem cortar palavras ou nomes de fármacos."""
    texto = _limpar(texto)
    if len(texto) <= limite:
        return [texto] if texto else []
    frases = [f.strip() for f in re.split(r"(?<=[.!?;:])\s+", texto) if f.strip()]
    saida: list[str] = []
    atual = ""
    for frase in frases or [texto]:
        candidato = f"{atual} {frase}".strip()
        if atual and len(candidato) > limite:
            saida.append(atual)
            atual = frase
        else:
            atual = candidato
    if atual:
        saida.append(atual)
    return saida


def _linha_tabela(cabecalho: list[str], celulas: list[str]) -> str:
    pares = []
    for indice, valor in enumerate(celulas):
        valor = _limpar(valor)
        if not valor:
            continue
        rotulo = _limpar(cabecalho[indice]) if indice < len(cabecalho) else ""
        pares.append(f"{rotulo}: {valor}" if rotulo else valor)
    return " · ".join(pares)


def _secoes(markdown: str) -> list[tuple[str, list[tuple[str, str]]]]:
    """Converte Markdown em blocos projetáveis, incluindo tabelas GFM."""
    markdown = re.sub(r"```mermaid.*?```", "", markdown, flags=re.S | re.I)
    secoes: list[tuple[str, list[tuple[str, str]]]] = []
    atual_titulo = ""
    atual_corpo: list[tuple[str, str]] = []
    cabecalho_tabela: list[str] = []

    def fechar() -> None:
        nonlocal atual_titulo, atual_corpo, cabecalho_tabela
        if atual_titulo or atual_corpo:
            secoes.append((atual_titulo, atual_corpo))
        atual_titulo, atual_corpo, cabecalho_tabela = "", [], []

    for linha in markdown.splitlines():
        crua = linha.strip()
        cab = re.match(r"^(#{1,4})\s+(.*)$", crua)
        if cab:
            fechar()
            atual_titulo = _limpar(cab.group(2))
            continue
        if not crua or crua.startswith("```"):
            continue

        if crua.startswith("|"):
            celulas = [c.strip() for c in crua.strip("|").split("|")]
            if all(re.fullmatch(r":?-{3,}:?", c.replace(" ", "")) for c in celulas if c):
                continue
            if not cabecalho_tabela:
                cabecalho_tabela = celulas
                continue
            convertido = _linha_tabela(cabecalho_tabela, celulas)
            if convertido:
                atual_corpo.append(("item", convertido))
            continue

        cabecalho_tabela = []
        item = re.match(r"^[-*+]\s+(.*)$|^\d+[.)]\s+(.*)$", crua)
        if item:
            conteudo = _limpar(item.group(1) or item.group(2) or "")
            if conteudo:
                atual_corpo.append(("item", conteudo))
            continue

        for fragmento in _fragmentar(crua):
            atual_corpo.append(("paragrafo", fragmento))

    fechar()
    return [secao for secao in secoes if secao[0] or secao[1]]


def _logo_profissional_na_pagina(a: Apresentacao, caminho: Path | None) -> None:
    if not caminho:
        return
    try:
        nome = "LogoProfissionalInterna"
        a.pdf.imagem(nome, str(caminho), 0, 0, 0, 0)
        a.pdf.atual.pop()
        imagem = a.pdf.imagens[nome]
        largura = 72.0
        altura = largura * imagem["altura"] / max(1, imagem["largura"])
        if altura > 34:
            altura = 34.0
            largura = altura * imagem["largura"] / max(1, imagem["altura"])
        a.pdf.imagem(
            nome, str(caminho),
            a.largura - a.margem - largura,
            a.altura - 18 - altura,
            largura, altura,
        )
    except (OSError, ValueError):
        return


def _marca_pagina(a: Apresentacao, logo_profissional: Path | None, nome: str, registro_curto: str) -> None:
    """Identifica cada página interna sem competir com o conteúdo clínico."""
    a._logo(a.margem, a.altura - 16, 82)  # noqa: SLF001 — componente interno do mesmo pacote PDF
    _logo_profissional_na_pagina(a, logo_profissional)
    identificacao = " · ".join(parte for parte in (nome, registro_curto) if parte)
    if identificacao:
        a.pdf.texto(a.margem, 51, identificacao, 7.2, NEUTRO)


def gerar(doc: Document, medico: dict, anotacao: str = "") -> bytes:
    nome = professional_name(medico)
    conselho = " ".join(
        parte for parte in (
            medico.get("council_name"), medico.get("council_number"),
        ) if parte
    )
    if medico.get("council_state"):
        conselho = f"{conselho}/{medico['council_state']}".strip("/")
    registro = " · ".join(
        parte for parte in (
            conselho,
            f"RQE {medico['rqe']}" if medico.get("rqe") else "",
            *workplace_lines(medico),
        ) if parte
    )
    logo_profissional = rendered_logo_png(medico.get("document_logo_url"))

    a = Apresentacao(
        titulo=doc.title,
        autor=nome or "Corvia",
        assunto=f"Material de apresentação — {doc.theme}",
        rodape=f"Corvia · {doc.theme} · corvia.med.br",
    )
    a.capa(
        doc.title, doc.summary or "", nome or "Corvia", registro,
        logo_profissional=str(logo_profissional) if logo_profissional else None,
    )

    paginas_conteudo = 0

    def abrir_slide(titulo: str) -> None:
        nonlocal paginas_conteudo
        a.slide(titulo)
        _marca_pagina(a, logo_profissional, nome, conselho)
        paginas_conteudo += 1

    fonte = arv.extrair_mermaid(doc.body_md or "")
    if fonte:
        if arv.render(a, fonte, "Árvore de decisão"):
            _marca_pagina(a, logo_profissional, nome, conselho)
            paginas_conteudo += 1
        else:
            raiz = arv.montar(fonte)
            abrir_slide("Árvore de decisão")
            if raiz is None:
                a.corpo(
                    "O diagrama não pôde ser redesenhado com fidelidade. "
                    "Consulte o fluxograma original na Corvia.", 12,
                )
            else:
                for linha in arv.em_lista(raiz):
                    a.corpo(linha, 10.5)

    secoes = _secoes(doc.body_md or "")
    for titulo, corpo in secoes:
        if not corpo:
            continue
        blocos = [
            corpo[indice:indice + MARCADORES_POR_PAGINA]
            for indice in range(0, len(corpo), MARCADORES_POR_PAGINA)
        ]
        for numero, bloco in enumerate(blocos, start=1):
            rotulo = titulo or doc.title
            if len(blocos) > 1:
                rotulo = f"{rotulo} ({numero}/{len(blocos)})"
            abrir_slide(rotulo)
            for tipo, texto in bloco:
                if tipo == "item":
                    a.marcador(texto)
                else:
                    a.corpo(texto)

    if paginas_conteudo == 0:
        abrir_slide("Resumo")
        resumo = _limpar(doc.summary or "")
        if resumo:
            for fragmento in _fragmentar(resumo):
                a.corpo(fragmento)
        else:
            a.corpo(
                "O documento publicado não contém corpo textual projetável. "
                "Consulte o conteúdo original e suas referências na Biblioteca científica.",
                12,
            )

    if anotacao.strip():
        abrir_slide("Anotação do apresentador")
        a.pdf.retangulo(a.margem, a.base + 30, a.util, a.y - a.base - 20, TINTA_TEAL)
        a.pdf.retangulo(a.margem, a.base + 30, 4, a.y - a.base - 20, TEAL)
        a.y -= 18
        for paragrafo in anotacao.strip().splitlines():
            if paragrafo.strip():
                a.corpo(_limpar(paragrafo), 12)
        a.pdf.texto(
            a.margem + 18, a.base + 40,
            "Anotação de quem exportou — não faz parte do conteúdo verificado da plataforma.",
            8, NEUTRO, italico=True,
        )

    abrir_slide("Procedência")
    a.corpo(f"Documento: {doc.title}", 11)
    a.corpo(
        f"Tema: {doc.theme} · nível de fonte: {doc.source_tier} · revisão: {doc.review_status}",
        10.5,
    )
    if doc.source_refs:
        a.y -= 4
        for referencia in doc.source_refs[:8]:
            a.marcador(_limpar(referencia), 9.5)
        if len(doc.source_refs) > 8:
            a.corpo(
                f"e mais {len(doc.source_refs) - 8} referência(s) no documento original.",
                9.5,
            )
    if doc.gaps:
        a.pdf.retangulo(a.margem, a.y - 34, a.util, 30, TINTA_VERMELHA)
        a.pdf.retangulo(a.margem, a.y - 34, 4, 30, VERMELHO)
        a.pdf.texto(
            a.margem + 16, a.y - 22,
            f"Este documento declara {len(doc.gaps)} ponto(s) pendente(s) de verificação humana.",
            10, TINTA,
        )
        a.y -= 44
    hoje = datetime.now(timezone.utc).astimezone().strftime("%d/%m/%Y")
    a.corpo(
        f"Exportado da Corvia em {hoje}" + (f" por {nome}." if nome else "."),
        9.5,
    )

    return a.salvar_bytes()
