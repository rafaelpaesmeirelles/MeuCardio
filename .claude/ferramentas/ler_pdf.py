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
    m = re.search(rb"stream\r?\n(.*?)\r?\nendstream", corpo, re.S)
    if not m:
        return b""
    d = m.group(1)
    if b"/FlateDecode" in corpo:
        try:
            return zlib.decompress(d)
        except zlib.error:
            try:
                return zlib.decompressobj().decompress(d)
            except Exception:
                return b""
    return d


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
    """Percorre o fluxo juntando os operadores de texto na ordem em que saem."""
    saida, atual = [], None
    for m in re.finditer(
            rb"/([A-Za-z0-9_.+-]+)\s+[\d.]+\s+Tf|\((?:\\.|[^\\()])*\)|<([0-9A-Fa-f\s]+)>"
            rb"|\bT[Jj]\b|\bTd\b|\bTD\b|\bT\*\b|\bTm\b|'|\"", conteudo, re.S):
        txt = m.group(0)
        if txt.endswith(b"Tf"):
            atual = cmaps.get(fontes.get(m.group(1)))
        elif txt.startswith(b"("):
            corpo = txt[1:-1]
            corpo = re.sub(rb"\\([nrtbf()\\])",
                           lambda x: {b"n": b"\n", b"r": b"\r", b"t": b"\t",
                                      b"b": b"", b"f": b"", b"(": b"(", b")": b")",
                                      b"\\": b"\\"}[x.group(1)], corpo)
            corpo = re.sub(rb"\\([0-7]{1,3})",
                           lambda x: bytes([int(x.group(1), 8) & 0xFF]), corpo)
            saida.append(_decodificar(corpo, atual))
        elif txt.startswith(b"<") and m.group(2):
            hexa = re.sub(rb"\s", b"", m.group(2))
            if len(hexa) % 2:
                hexa += b"0"
            saida.append(_decodificar(bytes.fromhex(hexa.decode()), atual))
        elif txt in (b"Td", b"TD", b"T*", b"Tm", b"'", b'"'):
            saida.append("\n")
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

    partes = []
    for n, corpo in objs.items():
        if n in cmaps or b"/Image" in corpo:
            continue
        d = _fluxo(corpo)
        if d and (b"Tj" in d or b"TJ" in d):
            partes.append(_strings(d, cmaps, fontes))
    t = "\n".join(partes)
    t = re.sub(r"[ \t]+", " ", t)
    return re.sub(r"\n{3,}", "\n\n", t)


if __name__ == "__main__":
    print(texto(sys.argv[1]))
