#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Varre o repositório inteiro atrás de fonte fraca, em qualquer lugar.

POR QUE ISTO EXISTE, e não basta a lista do importador:
`derivar_tier()` em backend/app/services/importer.py devolve "C" apenas quando
**todas** as referências de um documento são fracas. Basta uma boa ao lado — um
DOI, o nome de uma sociedade — para o documento virar "A" e a fonte fraca
passar sem ser vista.

Foi assim que `droracle.ai`, site de respostas geradas por IA, sustentou dose de
milrinona e de colchicina em quatro documentos publicados. A colchicina citava
uma revisão do JACC com DOI **no mesmo campo**: tier A, nenhum alarme, 15
ocorrências no acervo. Descoberto em 29/07/2026 por leitura manual, não pelo
sistema.

Este script não olha tier. Procura a string, diz onde está, e é isso.

Uso:
    python3 .claude/ferramentas/varre_fontes_fracas.py [raiz]

Saída: uma linha por ocorrência, agrupada por arquivo, e um resumo no fim.
Código de saída 1 se achou algo — serve para usar em verificação automática.
"""
import io
import json
import os
import re
import sys

# Espelha FONTES_FRACAS de backend/app/services/importer.py. Mantida aqui em
# separado de propósito: este script roda fora do container, sem importar o
# backend. Se a lista de lá mudar, atualize esta também.
FONTES_FRACAS = (
    "consultaremedios", "consulta remédios", "guiafarmaceutico", "hsl.org.br",
    "sírio-libanês", "sirio-libanes", "health.ucsd.edu", "medscape", "mdcalc",
    "drugs.com", "wikipedia", "wikipédia", "wikidoc", "sanarmed", "sanar",
    "pebmed", "medicinanet", "tuasaude", "youtube", "empendium", "rdocumentation",
    "doccheck", "flexikon", "slideshare", "scribd", "conduta.med.br", "medicpulse",
    "droracle", "perplexity.ai", "chat.openai", "chatgpt", "copilot.microsoft",
    "healthline", "webmd", "medicalnewstoday", "minutosaudavel",
    "quora", "reddit", "brainly",
    "passeidireto", "studocu", "docsity",
)

# Onde procurar. Conteúdo clínico e os JSON das frentes — não o código.
ALVOS = ("content", "medicamentos", "evidencias", "estudos", "galeria",
         "exames", "checklists", "trilhas", "material-paciente", "emergencia")

IGNORAR_DIR = {".git", "node_modules", "__pycache__", ".venv", "dist", "build"}


def _ocorrencias(texto: str):
    baixo = texto.lower()
    for f in FONTES_FRACAS:
        inicio = 0
        while True:
            i = baixo.find(f, inicio)
            if i < 0:
                break
            yield f, i
            inicio = i + len(f)


def _contexto(texto: str, i: int, largura: int = 90) -> str:
    ini = max(0, i - largura // 2)
    trecho = texto[ini:i + largura].replace("\n", " ")
    return re.sub(r"\s+", " ", trecho).strip()


# Termos que indicam que a menção é NARRATIVA — o documento está contando que
# aquela fonte foi trocada ou removida —, não uma citação viva. Sem esta
# separação o relatório vira ruído: a primeira varredura devolveu 42
# ocorrências, e boa parte eram notas de correção de revisões anteriores,
# justamente o registro que este projeto pede que se preserve.
NARRATIVA = ("trocado", "trocados", "removido", "removida", "substituíd",
             "substituid", "apoiava-se", "se apoiava", "constava", "vinha do",
             "vinha da", "não deve ser", "deixou de", "saiu", "corrigido")


def _e_citacao_viva(texto: str, i: int) -> bool:
    """Decide se a ocorrência é citação de fonte ou menção narrativa.

    Citação viva: está dentro do `source_refs` do front matter, ou numa linha
    que atribui procedência (`- **fonte**: ...`, `"fonte": "..."`).
    """
    ini_linha = texto.rfind("\n", 0, i) + 1
    fim_linha = texto.find("\n", i)
    linha = texto[ini_linha:fim_linha if fim_linha > 0 else len(texto)].lower()

    janela = texto[max(0, i - 260):i + 120].lower()
    if any(n in janela for n in NARRATIVA):
        return False
    return ("source_refs" in linha or "**fonte**" in linha or '"fonte"' in linha
            or linha.strip().startswith('"') or "· http" in linha)


def varrer(raiz: str):
    achados = {}
    for alvo in ALVOS:
        base = os.path.join(raiz, alvo)
        if not os.path.exists(base):
            continue
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [d for d in dirnames if d not in IGNORAR_DIR]
            for nome in filenames:
                if not nome.endswith((".md", ".json")):
                    continue
                caminho = os.path.join(dirpath, nome)
                try:
                    texto = io.open(caminho, encoding="utf-8").read()
                except (OSError, UnicodeDecodeError):
                    continue
                for fonte, i in _ocorrencias(texto):
                    rel = os.path.relpath(caminho, raiz)
                    achados.setdefault(rel, []).append(
                        (fonte, _contexto(texto, i), _e_citacao_viva(texto, i)))
    return achados


def main():
    raiz = sys.argv[1] if len(sys.argv) > 1 else "/opt/meucardio"
    achados = varrer(raiz)

    if not achados:
        print("Nenhuma fonte fraca encontrada em %d diretórios varridos." % len(ALVOS))
        print("Lista conferida: %d termos." % len(FONTES_FRACAS))
        return 0

    vivas = total = 0
    arquivos_com_citacao = set()
    for caminho in sorted(achados):
        linhas = achados[caminho]
        if not any(v for _, _, v in linhas):
            continue
        arquivos_com_citacao.add(caminho)
        print("\n%s" % caminho)
        for fonte, ctx, viva in linhas:
            total += 1
            if not viva:
                continue
            vivas += 1
            print("   [%s] …%s…" % (fonte, ctx))

    narrativas = total
    for caminho in sorted(set(achados) - arquivos_com_citacao):
        narrativas += len(achados[caminho])
    fontes = sorted({f for v in achados.values() for f, _, viva in v if viva})
    print("\n" + "=" * 70)
    print("%d CITAÇÕES VIVAS em %d arquivos — estas precisam ser trocadas" % (vivas, len(arquivos_com_citacao)))
    print("%d menções restantes são narrativas (o texto conta que a fonte saiu) e ficam" % (
        sum(len(v) for v in achados.values()) - vivas))
    print("termos citados: %s" % ", ".join(fontes))
    print("\nNenhuma destas sustenta conteúdo clínico neste produto. Substitua por")
    print("bula, diretriz ou artigo original — e onde não houver com que substituir,")
    print("marque com VERIFICAÇÃO HUMANA NECESSÁRIA em vez de deixar a citação ruim.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
