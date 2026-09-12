"""Diagramação sobre o `nucleo`: documento em retrato e apresentação em paisagem.

Separado do escritor de PDF de propósito: `nucleo.py` sabe desenhar numa
coordenada, este arquivo sabe onde a coordenada fica. Cuida de fluxo — quebra
de linha pela largura real do glifo, quebra de página, cabeçalho, rodapé e a
regra de não deixar título órfão no pé da página.

Duas classes porque são dois problemas diferentes:

- `Documento` — A4 retrato, texto corrido. É o material que o paciente leva
  para casa: precisa caber no bolso da pasta e ser lido de perto.
- `Apresentacao` — A4 paisagem, um assunto por página, corpo grande. É o que
  vai no projetor do round: precisa ser legível do fundo da sala, o que
  significa pouco texto por página e nada de parágrafo longo.
"""

from __future__ import annotations

from .marca import (
    BRANCO, COBRE, COBRE_CLARO, FIO, LOGO, NAVY, NEUTRO, OFF_WHITE, TEAL, TINTA,
    TINTA_TEAL, logo_disponivel,
)
from .nucleo import A4, PDF, largura_texto
from .wrapping import wrap_text
from app.services.export_links import linked_lines

A4_PAISAGEM = (A4[1], A4[0])


def quebrar(texto: str, largura: float, tamanho: float, negrito: bool = False) -> list[str]:
    """Quebra pela largura real, inclusive identificadores sem espaços."""
    return wrap_text(texto, largura, lambda linha: largura_texto(linha, tamanho, negrito))


class _Base:
    """O que retrato e paisagem compartilham: caneta, página e medida."""

    largura = A4[0]
    altura = A4[1]
    margem = 62.0
    topo = A4[1] - 74.0
    base = 76.0

    def __init__(self, titulo: str, autor: str, assunto: str, rodape: str):
        self.pdf = PDF(self.largura, self.altura)
        self.pdf.metadados = {"titulo": titulo, "autor": autor, "assunto": assunto}
        self.rodape = rodape
        self.y = self.topo
        self.pagina = 0

    @property
    def util(self) -> float:
        return self.largura - 2 * self.margem

    def _garantir(self, altura: float) -> None:
        if self.y - altura < self.base:
            self.abrir_pagina()

    def espaco(self, altura: float) -> None:
        self.y -= altura

    def _logo(self, x: float, y: float, larg: float) -> float:
        """Desenha a logo e devolve a altura ocupada (0 se o arquivo não existir)."""
        if not logo_disponivel():
            return 0.0
        caminho = str(LOGO)
        self.pdf.imagem("Logo", caminho, 0, 0, 0, 0)   # registra para medir
        self.pdf.atual.pop()                            # descarta o desenho de medição
        img = self.pdf.imagens["Logo"]
        alt = larg * img["altura"] / img["largura"]
        self.pdf.imagem("Logo", caminho, x, y - alt, larg, alt)
        return alt

    def salvar_bytes(self) -> bytes:
        from pathlib import Path
        import tempfile

        # O núcleo escreve em arquivo; a rota devolve bytes. Um temporário evita
        # duplicar a serialização só para mudar o destino.
        with tempfile.TemporaryDirectory() as pasta:
            caminho = Path(pasta) / "documento.pdf"
            self.pdf.salvar(str(caminho))
            return caminho.read_bytes()


class Documento(_Base):
    """A4 retrato, texto corrido — material educativo do paciente."""

    reservar_assinatura = False

    def abrir_pagina(self, com_cabecalho: bool = True) -> None:
        self.pdf.nova_pagina()
        self.pagina += 1
        self.y = self.topo
        self.pdf.retangulo(0, 0, self.largura, self.altura, OFF_WHITE)
        if com_cabecalho and self.pagina > 1:
            self._cabecalho()
        self._rodape()

    def _cabecalho(self) -> None:
        t = self.altura - 46
        self.pdf.texto(self.margem, t, "CORVIA", 7.5, NEUTRO, negrito=True, espaco_extra=1.4)
        self.pdf.linha(self.margem, t - 9, self.largura - self.margem, t - 9, FIO)

    def _rodape(self) -> None:
        b = 108 if self.reservar_assinatura else 48
        self.pdf.linha(self.margem, b + 14, self.largura - self.margem, b + 14, FIO)
        self.pdf.texto(self.margem, b, self.rodape, 7.2, NEUTRO)
        n = str(self.pagina)
        self.pdf.texto(self.largura - self.margem - largura_texto(n, 7.5, True), b,
                       n, 7.5, NAVY, negrito=True)

    # -- blocos ------------------------------------------------------------

    def capa_simples(self, titulo: str, subtitulo: str, etiqueta: str = "") -> None:
        """Abertura na primeira página, sem folha de rosto própria — material de
        paciente com capa isolada desperdiça uma folha impressa."""
        self.abrir_pagina(com_cabecalho=False)
        self.pdf.retangulo(0, self.altura - 7, self.largura, 7, COBRE)
        alt = self._logo(self.margem, self.altura - 40, 132)
        self.y = self.altura - 40 - alt - 26

        for linha in quebrar(titulo, self.util, 21, True):
            self._garantir(40)
            self.pdf.texto(self.margem, self.y - 21, linha, 21, NAVY, negrito=True)
            self.y -= 27
        self.pdf.linha(self.margem, self.y - 2, self.margem + 46, self.y - 2, COBRE, 2.2)
        self.y -= 20

        if subtitulo:
            for linha in quebrar(subtitulo, self.util, 11):
                self._garantir(24)
                self.pdf.texto(self.margem, self.y - 11, linha, 11, TEAL)
                self.y -= 16
        if etiqueta:
            self.y -= 7
            for linha in wrap_text(etiqueta.upper(), self.util - 22,
                                   lambda texto: largura_texto(texto, 7.5, True) + len(texto) * 1.1):
                self._garantir(23)
                larg = largura_texto(linha, 7.5, True) + len(linha) * 1.1 + 22
                self.pdf.retangulo(self.margem, self.y - 19, larg, 19, TINTA_TEAL)
                self.pdf.texto(self.margem + 11, self.y - 13, linha, 7.5, TEAL,
                               negrito=True, espaco_extra=1.1)
                self.y -= 23
        self.y -= 14

    def titulo(self, texto: str) -> None:
        # Reserva espaço para duas linhas de corpo: título no pé da página, com o
        # texto na página seguinte, é o defeito mais visível de layout automático.
        self._garantir(56)
        self.espaco(10)
        for linha in quebrar(texto, self.util, 13, True):
            self._garantir(45)
            self.pdf.texto(self.margem, self.y - 13, linha, 13, NAVY, negrito=True)
            self.y -= 17
        self.y -= 5

    def paragrafo(self, texto: str, tamanho: float = 10.2, cor=TINTA) -> None:
        entrelinha = tamanho * 1.58
        for linha in quebrar(texto, self.util, tamanho):
            self._garantir(entrelinha)
            self.pdf.texto(self.margem, self.y - tamanho, linha, tamanho, cor)
            self.y -= entrelinha
        self.y -= 6

    def itens(self, lista: list[str]) -> None:
        recuo, tamanho = 16.0, 10.2
        entrelinha = tamanho * 1.5
        for item in lista:
            self._garantir(entrelinha)
            self.pdf.texto(self.margem + 3, self.y - tamanho, "•", tamanho, TEAL, negrito=True)
            for linha in quebrar(item, self.util - recuo, tamanho):
                self._garantir(entrelinha)
                self.pdf.texto(self.margem + recuo, self.y - tamanho, linha, tamanho, TINTA)
                self.y -= entrelinha
            self.y -= 3
        self.y -= 5

    def paragrafo_com_links(self, texto: str, *, item: bool = False, tamanho: float = 10.2) -> None:
        recuo = 16 if item else 0
        x = self.margem + recuo
        entrelinha = tamanho * (1.5 if item else 1.58)
        primeira = True
        for linha, spans in linked_lines(texto, lambda valor: quebrar(valor, self.util - recuo, tamanho)):
            self._garantir(entrelinha)
            if item and primeira:
                self.pdf.texto(self.margem + 3, self.y - tamanho, "•", tamanho, TEAL, negrito=True)
            primeira = False
            self.pdf.texto(x, self.y - tamanho, linha, tamanho, TINTA)
            for a, b, url in spans:
                inicio = x + largura_texto(linha[:a], tamanho)
                largura = largura_texto(linha[a:b], tamanho)
                self.pdf.linha(inicio, self.y - tamanho - 1, inicio + largura, self.y - tamanho - 1, TEAL, .4)
                self.pdf.link(inicio, self.y - tamanho - 2, largura, tamanho + 3, url)
            self.y -= entrelinha
        self.y -= 3 if item else 6

    def destaque(self, texto: str, cor_fundo=TINTA_TEAL, cor_barra=TEAL,
                 rotulo: str = "", links: bool = False) -> None:
        tamanho = 10.0
        entrelinha = tamanho * 1.5
        linhas = list(linked_lines(texto, lambda valor: quebrar(valor, self.util - 44, tamanho))) if links else [(linha, []) for linha in quebrar(texto, self.util - 44, tamanho)]
        rotulos = quebrar(rotulo.upper(), self.util - 44, 7.5, True) if rotulo else []
        reserva = 26 + 15 * len(rotulos)
        while linhas:
            self._garantir(reserva + entrelinha + 12)
            capacidade = max(1, int((self.y - self.base - reserva - 12) // entrelinha))
            trecho, linhas = linhas[:capacidade], linhas[capacidade:]
            alt = len(trecho) * entrelinha + reserva
            topo = self.y
            self.pdf.retangulo(self.margem, topo - alt, self.util, alt, cor_fundo)
            self.pdf.retangulo(self.margem, topo - alt, 3.2, alt, cor_barra)
            y = topo - 16
            for linha in rotulos:
                self.pdf.texto(self.margem + 18, y - 7.5, linha, 7.5, cor_barra, negrito=True)
                y -= 15
            for linha, spans in trecho:
                self.pdf.texto(self.margem + 18, y - tamanho, linha, tamanho, TINTA)
                for a, b, url in spans:
                    inicio = self.margem + 18 + largura_texto(linha[:a], tamanho)
                    largura = largura_texto(linha[a:b], tamanho)
                    self.pdf.linha(inicio, y - tamanho - 1, inicio + largura, y - tamanho - 1, TEAL, .4)
                    self.pdf.link(inicio, y - tamanho - 2, largura, tamanho + 3, url)
                y -= entrelinha
            self.y = topo - alt - 12


class Apresentacao(_Base):
    """A4 paisagem, um assunto por página — modo aula e round.

    O corpo é grande e o texto por página é pouco de propósito: o alvo é a
    projeção, e slide com parágrafo é slide que ninguém lê de longe.
    """

    largura = A4_PAISAGEM[0]
    altura = A4_PAISAGEM[1]
    margem = 56.0
    topo = A4_PAISAGEM[1] - 96.0
    base = 62.0

    def __init__(self, titulo: str, autor: str, assunto: str, rodape: str):
        super().__init__(titulo, autor, assunto, rodape)
        self.total_previsto = 0

    def abrir_pagina(self, com_cabecalho: bool = True) -> None:
        self.pdf.nova_pagina()
        self.pagina += 1
        self.y = self.topo
        self.pdf.retangulo(0, 0, self.largura, self.altura, OFF_WHITE)
        if com_cabecalho:
            self.pdf.retangulo(0, self.altura - 5, self.largura, 5, COBRE)
            self._rodape()

    def _rodape(self) -> None:
        b = 30
        self.pdf.linha(self.margem, b + 16, self.largura - self.margem, b + 16, FIO)
        self.pdf.texto(self.margem, b, self.rodape, 7.5, NEUTRO)
        n = str(self.pagina)
        self.pdf.texto(self.largura - self.margem - largura_texto(n, 8, True), b,
                       n, 8, NAVY, negrito=True)

    def capa(
        self, titulo: str, subtitulo: str, autor: str, registro: str,
        logo_profissional: str | None = None,
    ) -> None:
        self.pdf.nova_pagina()
        self.pagina = 1
        self.pdf.retangulo(0, 0, self.largura, self.altura, OFF_WHITE)
        self.pdf.retangulo(0, self.altura - 7, self.largura, 7, COBRE)
        self._logo(self.margem, self.altura - 58, 160)
        if logo_profissional:
            try:
                nome_logo = "LogoProfissional"
                self.pdf.imagem(nome_logo, logo_profissional, 0, 0, 0, 0)
                self.pdf.atual.pop()
                imagem = self.pdf.imagens[nome_logo]
                largura_logo = 132.0
                altura_logo = largura_logo * imagem["altura"] / max(1, imagem["largura"])
                if altura_logo > 82.0:
                    altura_logo = 82.0
                    largura_logo = altura_logo * imagem["largura"] / max(1, imagem["altura"])
                self.pdf.imagem(
                    nome_logo, logo_profissional,
                    self.largura - self.margem - largura_logo,
                    self.altura - 48 - altura_logo,
                    largura_logo, altura_logo,
                )
            except (OSError, ValueError):
                pass

        y = self.altura - 230
        for linha in quebrar(titulo, self.util - 40, 30, True):
            self.pdf.texto(self.margem, y, linha, 30, NAVY, negrito=True)
            y -= 38
        self.pdf.linha(self.margem, y + 12, self.margem + 60, y + 12, COBRE, 2.6)
        y -= 16
        if subtitulo:
            for linha in quebrar(subtitulo, self.util - 60, 13):
                self.pdf.texto(self.margem, y, linha, 13, TEAL)
                y -= 19

        self.pdf.retangulo(0, 0, self.largura, 78, NAVY)
        self.pdf.texto(self.margem, 46, autor, 12, BRANCO, negrito=True)
        if registro:
            self.pdf.texto(self.margem, 28, registro, 8.6, COBRE_CLARO)

    def slide(self, titulo: str) -> None:
        self.abrir_pagina()
        for linha in quebrar(titulo, self.util, 20, True):
            self.pdf.texto(self.margem, self.y, linha, 20, NAVY, negrito=True)
            self.y -= 26
        self.pdf.linha(self.margem, self.y + 8, self.margem + 46, self.y + 8, COBRE, 2.2)
        self.y -= 18

    def marcador(self, texto: str, tamanho: float = 13.5) -> None:
        recuo = 22.0
        entrelinha = tamanho * 1.45
        self._garantir(entrelinha * 1.5)
        self.pdf.texto(self.margem + 4, self.y - tamanho, "•", tamanho, TEAL, negrito=True)
        for linha in quebrar(texto, self.util - recuo, tamanho):
            self._garantir(entrelinha)
            self.pdf.texto(self.margem + recuo, self.y - tamanho, linha, tamanho, TINTA)
            self.y -= entrelinha
        self.y -= 7

    def corpo(self, texto: str, tamanho: float = 12.5) -> None:
        entrelinha = tamanho * 1.5
        for linha in quebrar(texto, self.util, tamanho):
            self._garantir(entrelinha)
            self.pdf.texto(self.margem, self.y - tamanho, linha, tamanho, TINTA)
            self.y -= entrelinha
        self.y -= 8
