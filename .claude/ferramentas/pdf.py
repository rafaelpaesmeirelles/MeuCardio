"""Gerador de PDF em Python puro — só stdlib (zlib, struct, unicodedata).

Existe porque o servidor não tem nenhuma ferramenta de PDF instalada e não há
`pip` disponível: reportlab, weasyprint, fpdf, pandoc, wkhtmltopdf, chromium e
libreoffice estão todos ausentes. Em vez de pedir instalação de dependência
para gerar dois documentos, o formato PDF é escrito diretamente.

Escopo deliberadamente pequeno — é o necessário para documentos de texto com
identidade visual, não uma biblioteca de diagramação:

- fontes base-14 (Helvetica/Helvetica-Bold/Oblique), que não precisam ser
  embutidas porque todo leitor de PDF as tem;
- texto em WinAnsiEncoding, que é cp1252 e cobre o português inteiro;
- imagem PNG com canal alfa, decodificada aqui mesmo (o alfa vira /SMask, para
  a logo funcionar tanto sobre branco quanto sobre a capa navy);
- quebra de linha por largura real do glifo, lida da tabela métrica da fonte.

O que NÃO faz, e é bom saber antes de tentar: hifenização, kerning, colunas,
imagem JPEG, fonte fora das base-14 e caractere fora do cp1252 (emoji, por
exemplo, é substituído em vez de quebrar o arquivo).
"""

from __future__ import annotations

import struct
import unicodedata
import zlib

# ---------------------------------------------------------------------------
# Métricas
# ---------------------------------------------------------------------------

# Larguras oficiais das AFM da Adobe, em 1/1000 do corpo. Só os códigos ASCII
# imprimíveis estão aqui; acentuado é resolvido por decomposição (ver _largura).
_HELV = (
    "278 278 355 556 556 889 667 191 333 333 389 584 278 333 278 278 "
    "556 556 556 556 556 556 556 556 556 556 278 278 584 584 584 556 "
    "1015 667 667 722 722 667 611 778 722 278 500 667 556 833 722 778 "
    "667 778 722 667 611 722 667 944 667 667 611 278 278 278 469 556 "
    "333 556 556 500 556 556 278 556 556 222 222 500 222 833 556 556 "
    "556 556 333 500 278 556 500 722 500 500 500 334 260 334 584"
)
_HELV_B = (
    "278 333 474 556 556 889 722 238 333 333 389 584 278 333 278 278 "
    "556 556 556 556 556 556 556 556 556 556 333 333 584 584 584 611 "
    "975 722 722 722 722 667 611 778 722 278 556 722 611 833 722 778 "
    "667 778 722 667 611 722 667 944 667 667 611 333 278 333 584 556 "
    "333 556 611 556 611 556 333 611 611 278 278 556 278 889 611 611 "
    "611 611 389 556 333 611 556 778 556 556 500 389 280 389 584"
)

# Pontuação do cp1252 fora do ASCII. Letra acentuada não entra aqui de
# propósito: na Helvetica ela tem a mesma largura da letra-base, então a
# decomposição Unicode resolve sem tabela.
_PONTUACAO = {
    "–": (556, 556), "—": (1000, 1000), "‘": (222, 278),
    "’": (222, 278), "“": (333, 500), "”": (333, 500),
    "•": (350, 350), "…": (1000, 1000), " ": (278, 278),
    "°": (400, 400), "º": (365, 365), "ª": (370, 370),
    "·": (278, 278), "§": (556, 556), "®": (737, 737),
    "©": (737, 737), "×": (584, 584), "±": (584, 584),
    "½": (834, 834), "¼": (834, 834), "≥": (549, 549),
    "≤": (549, 549), "€": (556, 556), "→": (1000, 1000),
}

_TABELA = {
    False: [int(v) for v in _HELV.split()],
    True: [int(v) for v in _HELV_B.split()],
}


def _largura(ch: str, negrito: bool) -> int:
    codigo = ord(ch)
    if 32 <= codigo <= 126:
        return _TABELA[negrito][codigo - 32]
    if ch in _PONTUACAO:
        return _PONTUACAO[ch][1 if negrito else 0]
    # Acentuado: a Helvetica dá à letra acentuada a largura da letra-base.
    base = unicodedata.normalize("NFD", ch)[0]
    if base != ch and 32 <= ord(base) <= 126:
        return _TABELA[negrito][ord(base) - 32]
    return 556


def largura_texto(texto: str, tamanho: float, negrito: bool = False) -> float:
    return sum(_largura(c, negrito) for c in texto) * tamanho / 1000.0


# ---------------------------------------------------------------------------
# Codificação de string para o PDF
# ---------------------------------------------------------------------------

def _para_cp1252(texto: str) -> bytes:
    """Converte para cp1252, que é o WinAnsiEncoding declarado nas fontes.

    Caractere fora do repertório é substituído em vez de levantar exceção: um
    documento com um '?' no lugar de um glifo exótico ainda é entregável, um
    UnicodeEncodeError no meio da geração não é.
    """
    return texto.encode("cp1252", errors="replace")


def _literal(texto: str) -> bytes:
    corpo = _para_cp1252(texto)
    for de, para in ((b"\\", b"\\\\"), (b"(", b"\\("), (b")", b"\\)")):
        corpo = corpo.replace(de, para)
    return b"(" + corpo + b")"


# ---------------------------------------------------------------------------
# PNG
# ---------------------------------------------------------------------------

def _desfiltrar(dados: bytes, largura: int, altura: int, canais: int) -> bytearray:
    """Desfaz os filtros por scanline do PNG (RFC 2083, seção 6)."""
    passo = largura * canais
    saida = bytearray(passo * altura)
    anterior = bytearray(passo)
    pos = 0
    for linha in range(altura):
        filtro = dados[pos]
        pos += 1
        atual = bytearray(dados[pos:pos + passo])
        pos += passo
        if filtro == 1:      # Sub
            for i in range(canais, passo):
                atual[i] = (atual[i] + atual[i - canais]) & 0xFF
        elif filtro == 2:    # Up
            for i in range(passo):
                atual[i] = (atual[i] + anterior[i]) & 0xFF
        elif filtro == 3:    # Average
            for i in range(passo):
                esq = atual[i - canais] if i >= canais else 0
                atual[i] = (atual[i] + ((esq + anterior[i]) >> 1)) & 0xFF
        elif filtro == 4:    # Paeth
            for i in range(passo):
                a = atual[i - canais] if i >= canais else 0
                b = anterior[i]
                c = anterior[i - canais] if i >= canais else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                atual[i] = (atual[i] + pr) & 0xFF
        saida[linha * passo:(linha + 1) * passo] = atual
        anterior = atual
    return saida


def ler_png(caminho: str) -> dict:
    """Lê um PNG de 8 bits e devolve RGB + alfa separados, prontos para o PDF."""
    with open(caminho, "rb") as f:
        bruto = f.read()
    if bruto[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{caminho}: não é PNG")

    pos, idat, paleta, trns = 8, bytearray(), None, None
    largura = altura = profundidade = tipo = 0
    while pos < len(bruto):
        tam = struct.unpack(">I", bruto[pos:pos + 4])[0]
        tag = bruto[pos + 4:pos + 8]
        corpo = bruto[pos + 8:pos + 8 + tam]
        if tag == b"IHDR":
            largura, altura, profundidade, tipo = struct.unpack(">IIBB", corpo[:10])
        elif tag == b"PLTE":
            paleta = corpo
        elif tag == b"tRNS":
            trns = corpo
        elif tag == b"IDAT":
            idat += corpo
        elif tag == b"IEND":
            break
        pos += 12 + tam

    if profundidade != 8:
        raise ValueError(f"{caminho}: só 8 bits por canal (veio {profundidade})")

    canais = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[tipo]
    pixels = _desfiltrar(zlib.decompress(idat), largura, altura, canais)

    total = largura * altura
    rgb, alfa = bytearray(total * 3), None

    if tipo == 2:
        rgb = pixels
    elif tipo == 6:
        alfa = bytearray(total)
        for i in range(total):
            rgb[i * 3:i * 3 + 3] = pixels[i * 4:i * 4 + 3]
            alfa[i] = pixels[i * 4 + 3]
    elif tipo == 0:
        for i in range(total):
            rgb[i * 3:i * 3 + 3] = bytes([pixels[i]]) * 3
    elif tipo == 4:
        alfa = bytearray(total)
        for i in range(total):
            rgb[i * 3:i * 3 + 3] = bytes([pixels[i * 2]]) * 3
            alfa[i] = pixels[i * 2 + 1]
    elif tipo == 3:
        if paleta is None:
            raise ValueError(f"{caminho}: PNG indexado sem PLTE")
        if trns:
            alfa = bytearray(total)
        for i in range(total):
            idx = pixels[i]
            rgb[i * 3:i * 3 + 3] = paleta[idx * 3:idx * 3 + 3]
            if alfa is not None:
                alfa[i] = trns[idx] if idx < len(trns) else 255

    return {"largura": largura, "altura": altura, "rgb": bytes(rgb),
            "alfa": bytes(alfa) if alfa else None}


# ---------------------------------------------------------------------------
# Documento
# ---------------------------------------------------------------------------

A4 = (595.28, 841.89)


class PDF:
    """Acumula páginas e serializa o arquivo.

    Cada página é uma lista de operadores de conteúdo; o layout (posição,
    quebra de linha, nova página) é responsabilidade de quem chama — ver
    `documento.py`, que constrói o texto corrido em cima disto.
    """

    def __init__(self, largura: float = A4[0], altura: float = A4[1]):
        self.largura, self.altura = largura, altura
        self.paginas: list[list[bytes]] = []
        self.atual: list[bytes] = []
        self.imagens: dict[str, dict] = {}
        self.metadados = {"titulo": "", "autor": "", "assunto": ""}

    # -- página ------------------------------------------------------------

    def nova_pagina(self) -> None:
        if self.atual:
            self.paginas.append(self.atual)
        self.atual = []

    def _op(self, linha: bytes) -> None:
        self.atual.append(linha)

    # -- desenho -----------------------------------------------------------

    def retangulo(self, x: float, y: float, larg: float, alt: float,
                  cor: tuple[float, float, float]) -> None:
        r, g, b = cor
        self._op(f"{r:.4f} {g:.4f} {b:.4f} rg {x:.2f} {y:.2f} {larg:.2f} {alt:.2f} re f".encode())

    def linha(self, x1: float, y1: float, x2: float, y2: float,
              cor: tuple[float, float, float], espessura: float = 0.6) -> None:
        r, g, b = cor
        self._op(
            f"{r:.4f} {g:.4f} {b:.4f} RG {espessura:.2f} w "
            f"{x1:.2f} {y1:.2f} m {x2:.2f} {y2:.2f} l S".encode()
        )

    def texto(self, x: float, y: float, conteudo: str, tamanho: float,
              cor: tuple[float, float, float] = (0, 0, 0),
              negrito: bool = False, italico: bool = False,
              espaco_extra: float = 0.0) -> None:
        if not conteudo:
            return
        fonte = "FB" if negrito else ("FI" if italico else "F1")
        r, g, b = cor
        tc = f"{espaco_extra:.2f} Tc " if espaco_extra else ""
        self._op(
            f"BT {tc}/{fonte} {tamanho:.2f} Tf {r:.4f} {g:.4f} {b:.4f} rg "
            f"{x:.2f} {y:.2f} Td ".encode() + _literal(conteudo) + b" Tj ET"
        )

    def imagem(self, nome: str, caminho: str, x: float, y: float,
               larg: float, alt: float) -> None:
        if nome not in self.imagens:
            self.imagens[nome] = ler_png(caminho)
        self._op(
            f"q {larg:.2f} 0 0 {alt:.2f} {x:.2f} {y:.2f} cm /{nome} Do Q".encode()
        )

    # -- serialização ------------------------------------------------------

    def salvar(self, caminho: str) -> None:
        if self.atual:
            self.paginas.append(self.atual)
            self.atual = []

        objetos: list[bytes] = []

        def add(corpo: bytes) -> int:
            objetos.append(corpo)
            return len(objetos)          # números de objeto começam em 1

        # Fontes base-14: não são embutidas porque todo leitor as tem, e
        # WinAnsiEncoding é o que faz o acento do português sair certo.
        fontes = {}
        for apelido, nome_base in (("F1", "Helvetica"), ("FB", "Helvetica-Bold"),
                                   ("FI", "Helvetica-Oblique")):
            fontes[apelido] = add(
                b"<< /Type /Font /Subtype /Type1 /BaseFont /" + nome_base.encode()
                + b" /Encoding /WinAnsiEncoding >>"
            )

        # Imagens. O alfa vai como /SMask num XObject próprio em /DeviceGray —
        # é o que permite a logo transparente cair sobre a capa navy sem moldura.
        xobjs = {}
        for nome, img in self.imagens.items():
            mascara = None
            if img["alfa"]:
                mascara = add(
                    b"<< /Type /XObject /Subtype /Image /Width " + str(img["largura"]).encode()
                    + b" /Height " + str(img["altura"]).encode()
                    + b" /ColorSpace /DeviceGray /BitsPerComponent 8 /Filter /FlateDecode"
                    + b" /Length " + str(len(zlib.compress(img["alfa"], 9))).encode()
                    + b" >>\nstream\n" + zlib.compress(img["alfa"], 9) + b"\nendstream"
                )
            dados = zlib.compress(img["rgb"], 9)
            xobjs[nome] = add(
                b"<< /Type /XObject /Subtype /Image /Width " + str(img["largura"]).encode()
                + b" /Height " + str(img["altura"]).encode()
                + b" /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /FlateDecode"
                + (b" /SMask " + str(mascara).encode() + b" 0 R" if mascara else b"")
                + b" /Length " + str(len(dados)).encode()
                + b" >>\nstream\n" + dados + b"\nendstream"
            )

        recursos = (
            b"<< /Font << " + b" ".join(
                f"/{a} {n} 0 R".encode() for a, n in fontes.items()
            ) + b" >>"
            + (b" /XObject << " + b" ".join(
                f"/{a} {n} 0 R".encode() for a, n in xobjs.items()
            ) + b" >>" if xobjs else b"")
            + b" >>"
        )

        # As páginas precisam saber o número do /Pages e vice-versa; reservo o
        # número do /Pages antes de criar as páginas.
        n_pages = len(objetos) + 2 * len(self.paginas) + 1
        refs_pagina = []
        for ops in self.paginas:
            fluxo = zlib.compress(b"\n".join(ops), 9)
            n_conteudo = add(
                b"<< /Filter /FlateDecode /Length " + str(len(fluxo)).encode()
                + b" >>\nstream\n" + fluxo + b"\nendstream"
            )
            refs_pagina.append(add(
                b"<< /Type /Page /Parent " + str(n_pages).encode() + b" 0 R"
                + f" /MediaBox [0 0 {self.largura:.2f} {self.altura:.2f}]".encode()
                + b" /Resources " + recursos
                + b" /Contents " + str(n_conteudo).encode() + b" 0 R >>"
            ))

        add(b"<< /Type /Pages /Count " + str(len(refs_pagina)).encode()
            + b" /Kids [" + b" ".join(f"{n} 0 R".encode() for n in refs_pagina) + b"] >>")
        assert len(objetos) == n_pages, "número do /Pages não bateu"

        n_info = add(
            b"<< /Title " + _literal(self.metadados["titulo"])
            + b" /Author " + _literal(self.metadados["autor"])
            + b" /Subject " + _literal(self.metadados["assunto"])
            + b" /Creator " + _literal("Corvia") + b" >>"
        )
        n_raiz = add(b"<< /Type /Catalog /Pages " + str(n_pages).encode() + b" 0 R >>")

        # Montagem final com a tabela de referência cruzada.
        saida = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        posicoes = []
        for i, corpo in enumerate(objetos, start=1):
            posicoes.append(len(saida))
            saida += str(i).encode() + b" 0 obj\n" + corpo + b"\nendobj\n"

        inicio_xref = len(saida)
        saida += b"xref\n0 " + str(len(objetos) + 1).encode() + b"\n"
        saida += b"0000000000 65535 f \n"
        for p in posicoes:
            saida += f"{p:010d} 00000 n \n".encode()
        saida += (
            b"trailer\n<< /Size " + str(len(objetos) + 1).encode()
            + b" /Root " + str(n_raiz).encode() + b" 0 R"
            + b" /Info " + str(n_info).encode() + b" 0 R >>\n"
            + b"startxref\n" + str(inicio_xref).encode() + b"\n%%EOF\n"
        )

        with open(caminho, "wb") as f:
            f.write(bytes(saida))
