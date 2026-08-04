"""Tarefa 16 — modo apresentação: exporta conteúdo existente para aula e round.

O que esta tarefa é: **formatação e exportação**. O conteúdo sai do que já está
publicado e verificado; nada é criado aqui. O que muda é o registro visual —
paisagem, corpo grande, um assunto por página, pronto para projetar.

Duas decisões que valem registro:

1. **O fluxograma vira diagrama de verdade**, não uma imagem nem uma lista. O
   mermaid não roda fora do browser, então a árvore é redesenhada a partir do
   mesmo texto-fonte (ver `pdf/arvore.py`). Quando a árvore não cabe legível na
   página, cai para lista indentada — que preserva o caminho até cada conduta.

2. **A anotação do médico nunca entra no conteúdo.** Ela é pedida na exportação,
   vai numa página própria, marcada como anotação de quem exportou, e não toca
   o documento verificado. Misturar as duas coisas faria a observação de um
   round específico virar conteúdo da plataforma na próxima leitura.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone

from app.models.content import Document
from app.services.professional_profile import (
    professional_name, rendered_logo_png, workplace_lines,
)

from .pdf import Apresentacao
from .pdf import arvore as arv
from .pdf.marca import NAVY, NEUTRO, TEAL, TINTA, TINTA_TEAL, TINTA_VERMELHA, VERMELHO

# Limite por página. Vem da projeção, não da estética: acima disso o corpo teria
# de encolher a ponto de não ser lido do fundo de uma sala.
MARCADORES_POR_PAGINA = 6


def _limpar(texto: str) -> str:
    """Tira a marcação inline que o desenhador de texto não representa.

    O renderizador escreve uma linha com uma fonte só, então `**negrito**` no
    meio da frase não tem como sair em negrito. Remover os asteriscos é melhor
    que imprimi-los: o leitor projetado veria `**dose**` literalmente.
    """
    texto = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", texto)          # imagem
    texto = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", texto)      # link -> rótulo
    texto = re.sub(r"\*\*([^*]+)\*\*", r"\1", texto)
    texto = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"\1", texto)
    texto = re.sub(r"`([^`]+)`", r"\1", texto)
    return re.sub(r"\s+", " ", texto).strip()


def _secoes(markdown: str) -> list[tuple[str, list[tuple[str, str]]]]:
    """Divide o corpo em seções por título de nível 2 ou 3.

    Devolve [(título, [(tipo, texto)])], com tipo em {"item", "paragrafo"}.
    O bloco ```mermaid``` é retirado daqui — ele tem tratamento próprio.
    """
    markdown = re.sub(r"```mermaid.*?```", "", markdown, flags=re.S)
    secoes: list[tuple[str, list[tuple[str, str]]]] = []
    atual_titulo, atual_corpo = "", []

    for linha in markdown.splitlines():
        cab = re.match(r"^(#{2,4})\s+(.*)$", linha.strip())
        if cab:
            if atual_titulo or atual_corpo:
                secoes.append((atual_titulo, atual_corpo))
            atual_titulo, atual_corpo = _limpar(cab.group(2)), []
            continue
        crua = linha.strip()
        if not crua or crua.startswith("```"):
            continue
        item = re.match(r"^[-*+]\s+(.*)$|^\d+[.)]\s+(.*)$", crua)
        if item:
            conteudo = _limpar(item.group(1) or item.group(2) or "")
            if conteudo:
                atual_corpo.append(("item", conteudo))
        elif crua.startswith("|") or set(crua) <= set("|-: "):
            continue          # tabela: não cabe em slide, fica no documento original
        else:
            conteudo = _limpar(crua)
            if conteudo:
                atual_corpo.append(("paragrafo", conteudo))

    if atual_titulo or atual_corpo:
        secoes.append((atual_titulo, atual_corpo))
    return [s for s in secoes if s[0] or s[1]]


def gerar(doc: Document, medico: dict, anotacao: str = "") -> bytes:
    """Monta a apresentação de um documento publicado."""
    nome = professional_name(medico)
    conselho = " ".join(
        x for x in (
            medico.get("council_name"), medico.get("council_number"),
            medico.get("council_state"),
        ) if x
    )
    registro = " · ".join(
        p for p in (
            conselho,
            f"RQE {medico['rqe']}" if medico.get("rqe") else "",
            *workplace_lines(medico),
        ) if p
    )
    logo_profissional = rendered_logo_png(medico.get("document_logo_url"))

    a = Apresentacao(
        titulo=doc.title,
        autor=nome or "Corvia",
        assunto=f"Material de apresentação — {doc.theme}",
        rodape=f"Corvia · {doc.theme} · corvia.med.br",
    )
    a.capa(
        doc.title, doc.summary or "", nome, registro,
        logo_profissional=str(logo_profissional) if logo_profissional else None,
    )

    # --- fluxograma: a árvore é o conteúdo principal, vai logo após a capa ---
    fonte = arv.extrair_mermaid(doc.body_md or "")
    if fonte:
        if not arv.render(a, fonte, "Árvore de decisão"):
            raiz = arv.montar(fonte)
            a.slide("Árvore de decisão")
            if raiz is None:
                a.corpo("O diagrama deste documento não pôde ser redesenhado para "
                        "projeção. Consulte o fluxograma na plataforma.", 12)
            else:
                for linha in arv.em_lista(raiz):
                    a.corpo(linha, 10.5)

    # --- seções ---
    for titulo, corpo in _secoes(doc.body_md or ""):
        if not corpo:
            continue
        blocos = [corpo[i:i + MARCADORES_POR_PAGINA]
                  for i in range(0, len(corpo), MARCADORES_POR_PAGINA)]
        for n, bloco in enumerate(blocos, start=1):
            rotulo = titulo or doc.title
            if len(blocos) > 1:
                rotulo = f"{rotulo} ({n}/{len(blocos)})"
            a.slide(rotulo)
            for tipo, texto in bloco:
                if tipo == "item":
                    a.marcador(texto)
                else:
                    a.corpo(texto)

    # --- anotação do médico, sempre em página própria e identificada ---
    if anotacao.strip():
        a.slide("Anotação do apresentador")
        a.pdf.retangulo(a.margem, a.base + 30, a.util, a.y - a.base - 20, TINTA_TEAL)
        a.pdf.retangulo(a.margem, a.base + 30, 4, a.y - a.base - 20, TEAL)
        a.y -= 18
        for paragrafo in anotacao.strip().splitlines():
            if paragrafo.strip():
                a.corpo(_limpar(paragrafo), 12)
        a.pdf.texto(a.margem + 18, a.base + 40,
                    "Anotação de quem exportou — não faz parte do conteúdo "
                    "verificado da plataforma.", 8, NEUTRO, italico=True)

    # --- procedência: última página, sempre ---
    a.slide("Procedência")
    a.corpo(f"Documento: {doc.title}", 11)
    a.corpo(f"Tema: {doc.theme} · nível de fonte: {doc.source_tier} · "
            f"revisão: {doc.review_status}", 10.5)
    if doc.source_refs:
        a.y -= 4
        for ref in doc.source_refs[:8]:
            a.marcador(_limpar(ref), 9.5)
        if len(doc.source_refs) > 8:
            a.corpo(f"e mais {len(doc.source_refs) - 8} referência(s) no documento "
                    f"original.", 9.5)
    if doc.gaps:
        a.pdf.retangulo(a.margem, a.y - 34, a.util, 30, TINTA_VERMELHA)
        a.pdf.retangulo(a.margem, a.y - 34, 4, 30, VERMELHO)
        a.pdf.texto(a.margem + 16, a.y - 22,
                    f"Este documento declara {len(doc.gaps)} ponto(s) pendente(s) de "
                    f"verificação humana.", 10, TINTA)
        a.y -= 44
    a.corpo(f"Exportado da Corvia em "
            f"{datetime.now(timezone.utc).astimezone().strftime('%d/%m/%Y')}"
            + (f" por {nome}." if nome else "."), 9.5)

    return a.salvar_bytes()
