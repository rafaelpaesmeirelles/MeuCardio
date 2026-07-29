# -*- coding: utf-8 -*-
"""Extrai o texto de um PDF — contraparte de leitura do `pdf.py`.

Escrito para ler bula profissional publicada em PDF, que é onde está o dado
regulatório brasileiro. Faz o mínimo necessário e o declara: descomprime os
fluxos de conteúdo, junta os operadores de texto (Tj, TJ, ', ") e, quando a
fonte é subconjunto com codificação própria, traduz pelo /ToUnicode do próprio
arquivo. Sem ToUnicode e com fonte simbólica, o texto sai ilegível — e nesse
caso é melhor saber que saiu do que receber lixo achando que é conteúdo.
"""
import re, sys, zlib


def _objetos(b):
    fora = {}
    for m in re.finditer(rb"(\d+)\s+0\s+obj\b(.*?)\bendobj", b, re.S):
        fora[int(m.group(1))] = m.group(2)
    return fora


def _fluxo(corpo):
    # A quebra de linha ANTES de `endstream` é opcional na prática: há PDF em
    # que o fluxo termina colado nele. Exigi-la aqui fazia o casamento falhar e
    # o objeto ser descartado em silêncio — 16 dos 17 blocos de texto de uma
    # bula sumiam assim, e o resultado era arquivo vazio em vez de erro.
    m = re.search(rb"stream\r?\n(.*?)endstream", corpo, re.S)
    if not m:
        return b""
    d = m.group(1)
    if b"/FlateDecode" not in corpo:
        return d
    # A captura pode ter levado junto o EOL que separa o fluxo do `endstream`.
    # Tenta o dado como veio e depois sem o terminador — nesta ordem, sem
    # adivinhar nada: ou o zlib descomprime, ou não.
    for dado in (d, d[:-2] if d.endswith(b"\r\n") else None,
                 d[:-1] if d[-1:] in (b"\n", b"\r") else None):
        if dado is None:
            continue
        try:
            return zlib.decompress(dado)
        except zlib.error:
            try:
                # Fluxo truncado ainda rende o que já foi lido — melhor do que
                # perder a página inteira.
                parcial = zlib.decompressobj().decompress(dado)
                if parcial:
                    return parcial
            except zlib.error:
                pass
    return b""


def _cmaps(objs):
    """Monta o mapa código->caractere de cada fonte que traz /ToUnicode."""
    mapas = {}
    for n, corpo in objs.items():
        if b"beginbfchar" not in corpo and b"beginbfrange" not in corpo:
            continue
        t = _fluxo(corpo) or corpo
        m = {}
        for bloco in re.findall(rb"beginbfchar(.*?)endbfchar", t, re.S):
            for src, dst in re.findall(rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", bloco):
                m[int(src, 16)] = "".join(
                    chr(int(dst[i:i + 4], 16)) for i in range(0, len(dst), 4))
        for bloco in re.findall(rb"beginbfrange(.*?)endbfrange", t, re.S):
            for a, b_, c in re.findall(
                    rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", bloco):
                ini, fim, base = int(a, 16), int(b_, 16), int(c, 16)
                for k in range(ini, min(fim, ini + 65535) + 1):
                    m[k] = chr(base + k - ini)
        if m:
            mapas[n] = m
    return mapas


def _decodificar(bruto, cmap):
    if cmap:
        # Fonte com ToUnicode neste arquivo usa código de 2 bytes.
        pares = [bruto[i:i + 2] for i in range(0, len(bruto) - 1, 2)]
        return "".join(cmap.get(int.from_bytes(p, "big"), "") for p in pares)
    return bruto.decode("cp1252", "replace")


def _strings(conteudo, cmaps, fontes):
    """Percorre o fluxo juntando os operadores de texto na ordem em que saem.

    A quebra de linha vem da **mudança de Y**, não da presença de um operador de
    posicionamento. Bula costuma ser composta glifo a glifo, cada um com seu
    próprio Td: quebrar em todo Td transformava "SELOZOK" em "S E L O Z O K".
    """
    saida, atual, y, x = [], None, None, None
    padrao = re.compile(
        rb"/([A-Za-z0-9_.+-]+)\s+[\d.]+\s+Tf"
        rb"|\((?:\\.|[^\\()])*\)"
        rb"|<([0-9A-Fa-f\s]+)>"
        rb"|([-\d.]+)\s+([-\d.]+)\s+(?:Td|TD)\b"
        rb"|([-\d.]+)\s+([-\d.]+)\s+(?:Tm)\b"
        rb"|\bT\*\b|'|\"", re.S)
    for m in padrao.finditer(conteudo):
        txt = m.group(0)
        if txt.endswith(b"Tf"):
            atual = cmaps.get(fontes.get(m.group(1)))
        elif txt.startswith(b"("):
            corpo = txt[1:-1]
            corpo = re.sub(rb"\\([nrtbf()\\])",
                           lambda z: {b"n": b"\n", b"r": b"\r", b"t": b"\t",
                                      b"b": b"", b"f": b"", b"(": b"(", b")": b")",
                                      b"\\": b"\\"}[z.group(1)], corpo)
            corpo = re.sub(rb"\\([0-7]{1,3})",
                           lambda z: bytes([int(z.group(1), 8) & 0xFF]), corpo)
            saida.append(_decodificar(corpo, atual))
        elif txt.startswith(b"<") and m.group(2):
            hexa = re.sub(rb"\s", b"", m.group(2))
            if len(hexa) % 2:
                hexa += b"0"
            saida.append(_decodificar(bytes.fromhex(hexa.decode()), atual))
        elif txt.endswith(b"*") or txt in (b"'", b'"'):
            saida.append("\n")
        else:
            nx, ny = (m.group(3), m.group(4)) if m.group(3) else (m.group(5), m.group(6))
            nx, ny = float(nx), float(ny)
            if y is not None and abs(ny - y) > 0.9:
                saida.append("\n")
            elif x is not None and nx - x > 1.2:
                saida.append(" ")
            # Td é relativo e Tm absoluto; para decidir quebra de linha, o que
            # importa é ter mudado de altura, e ambos revelam isso.
            y, x = ny, nx
    return "".join(saida)


def texto(caminho):
    b = open(caminho, "rb").read()
    objs = _objetos(b)
    cmaps = _cmaps(objs)

    # /Font << /F1 12 0 R >> — liga o apelido usado no fluxo ao objeto da fonte,
    # e daí ao /ToUnicode correspondente.
    fontes = {}
    for corpo in objs.values():
        for bloco in re.findall(rb"/Font\s*<<(.*?)>>", corpo, re.S):
            for apelido, ref in re.findall(rb"/([A-Za-z0-9_.+-]+)\s+(\d+)\s+0\s+R", bloco):
                alvo = objs.get(int(ref), b"")
                tu = re.search(rb"/ToUnicode\s+(\d+)\s+0\s+R", alvo)
                if tu:
                    fontes[apelido] = int(tu.group(1))

    # Programa de fonte embutido (/FontFile*) é um binário que contém as
    # sequências "Tj"/"TJ" por acaso, dentro das tabelas glyf e hmtx. Sem esta
    # exclusão ele entra no texto como lixo — foi o que sujou a extração de uma
    # bula inteira. /Length1 é o marcador que todo fluxo de fonte carrega.
    def _e_fonte(corpo, dados):
        return (b"/FontFile" in corpo or b"/Length1" in corpo
                or dados[:4] in (b"\x00\x01\x00\x00", b"OTTO", b"true", b"ttcf")
                or b"glyf" in dados[:600] or dados[:2] == b"%!")

    partes = []
    for n, corpo in objs.items():
        if n in cmaps or b"/Image" in corpo:
            continue
        d = _fluxo(corpo)
        if d and (b"Tj" in d or b"TJ" in d) and not _e_fonte(corpo, d):
            partes.append(_strings(d, cmaps, fontes))
    t = "\n".join(partes)
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    _avisar_se_ilegivel(t)
    return t


PALAVRAS = ("de ", "da ", "do ", "com", "para", "que", "não", " mg", "em ",
            "uma", "por", "ção", "dose")


def _avisar_se_ilegivel(t):
    """Avisa quando o texto saiu ilegível, em vez de tentar adivinhar.

    Há PDFs cuja fonte é subconjunto com codificação própria e sem /ToUnicode:
    não existe no arquivo o mapa que traduziria os códigos, e o texto sai
    embaralhado. Houve aqui uma tentativa de descobrir o deslocamento por
    tentativa e erro, pontuando qual candidato parecia mais português — **foi
    removida de propósito**. Um extrator que adivinha produz texto plausível e
    errado, que é o pior resultado possível para dose e valor de referência.
    Quando isto dispara, o certo é buscar o documento em outra fonte.
    """
    if len(t) > 500 and sum(t.lower().count(w) for w in PALAVRAS) < len(t) / 400:
        print("AVISO: texto ilegivel — fonte sem /ToUnicode. Use outra fonte para "
              "este documento; nao confie no que saiu.", file=sys.stderr)


if __name__ == "__main__":
    print(texto(sys.argv[1]))
