"""Diagramação de texto corrido sobre o `pdf.py`.

Separado do gerador de PDF de propósito: `pdf.py` sabe desenhar numa
coordenada, este arquivo sabe onde a coordenada fica. Cuida de fluxo — quebra
de linha pela largura real do glifo, quebra de página, cabeçalho e rodapé,
e a regra de não deixar título órfão no pé da página.

As cores vêm de `frontend/src/styles/tokens.css`. Estão repetidas aqui porque o
PDF não lê CSS; se a paleta mudar lá, muda aqui também — é o quarto lugar fora
do CSS que acompanha troca de paleta, junto do tema do mermaid, do `theme_color`
do PWA e da meta `theme-color` do index.html.
"""

from __future__ import annotations

from pdf import A4, PDF, largura_texto

NAVY = (0x0B / 255, 0x2E / 255, 0x45 / 255)
NAVY_ESCURO = (0x08 / 255, 0x1E / 255, 0x30 / 255)
TEAL = (0x1C / 255, 0x72 / 255, 0x93 / 255)
TEAL_CLARO = (0x6F / 255, 0xB4 / 255, 0xCC / 255)
VERMELHO = (0xD5 / 255, 0x00 / 255, 0x1D / 255)
TINTA = (0x26 / 255, 0x33 / 255, 0x3B / 255)
NEUTRO = (0x55 / 255, 0x66 / 255, 0x6F / 255)
FIO = (0xE4 / 255, 0xE8 / 255, 0xEA / 255)
BRANCO = (1.0, 1.0, 1.0)
TINTA_TEAL = (0xEF / 255, 0xF5 / 255, 0xF8 / 255)
TINTA_VERMELHA = (0xFD / 255, 0xEE / 255, 0xF0 / 255)

MARGEM = 62.0
TOPO = A4[1] - 74.0
BASE = 76.0
LARGURA_UTIL = A4[0] - 2 * MARGEM


def quebrar(texto: str, largura: float, tamanho: float, negrito: bool = False) -> list[str]:
    """Quebra em linhas pela largura real do texto, não por contagem de caracteres."""
    linhas, atual = [], ""
    for palavra in texto.split():
        tentativa = f"{atual} {palavra}".strip()
        if largura_texto(tentativa, tamanho, negrito) <= largura or not atual:
            atual = tentativa
        else:
            linhas.append(atual)
            atual = palavra
    if atual:
        linhas.append(atual)
    return linhas


class Documento:
    def __init__(self, titulo: str, autor: str, assunto: str, rodape: str):
        self.pdf = PDF()
        self.pdf.metadados = {"titulo": titulo, "autor": autor, "assunto": assunto}
        self.rodape = rodape
        self.y = TOPO
        self.pagina = 0
        self.secao = ""
        self._sumario: list[tuple[str, int]] = []

    # -- estrutura de página ----------------------------------------------

    def abrir_pagina(self, com_cabecalho: bool = True) -> None:
        self.pdf.nova_pagina()
        self.pagina += 1
        self.y = TOPO
        if com_cabecalho and self.pagina > 1:
            self._cabecalho()
            self._rodape()

    def _cabecalho(self) -> None:
        topo = A4[1] - 46
        self.pdf.texto(MARGEM, topo, "CORVIA", 7.5, NEUTRO, negrito=True, espaco_extra=1.4)
        if self.secao:
            largura = largura_texto(self.secao, 7.5)
            self.pdf.texto(A4[0] - MARGEM - largura, topo, self.secao, 7.5, NEUTRO)
        self.pdf.linha(MARGEM, topo - 9, A4[0] - MARGEM, topo - 9, FIO)

    def _rodape(self) -> None:
        base = 48
        self.pdf.linha(MARGEM, base + 14, A4[0] - MARGEM, base + 14, FIO)
        self.pdf.texto(MARGEM, base, self.rodape, 7.5, NEUTRO)
        numero = str(self.pagina)
        self.pdf.texto(A4[0] - MARGEM - largura_texto(numero, 7.5, True), base,
                       numero, 7.5, NAVY, negrito=True)

    def _garantir(self, altura: float) -> None:
        """Abre página nova se o bloco de `altura` não couber no que resta."""
        if self.y - altura < BASE:
            self.abrir_pagina()

    def espaco(self, altura: float) -> None:
        self.y -= altura

    # -- blocos de conteúdo ------------------------------------------------

    def capitulo(self, titulo: str, numero: str = "") -> None:
        """Título de nível 1 — sempre começa em página nova."""
        # Sem `com_cabecalho=False` aqui, a página de abertura ganharia dois
        # cabeçalhos empilhados no mesmo ponto: o de `abrir_pagina`, com o nome
        # da seção anterior, e o desta, com o novo. A troca de seção tem de
        # acontecer antes do desenho.
        self.abrir_pagina(com_cabecalho=False)
        self.secao = titulo
        self._cabecalho()
        self._rodape()
        self._sumario.append((titulo, self.pagina))

        if numero:
            self.pdf.texto(MARGEM, self.y - 4, numero, 9, VERMELHO,
                           negrito=True, espaco_extra=1.2)
            self.y -= 20
        for linha in quebrar(titulo, LARGURA_UTIL, 22, True):
            self.pdf.texto(MARGEM, self.y - 22, linha, 22, NAVY, negrito=True)
            self.y -= 28
        self.pdf.linha(MARGEM, self.y - 2, MARGEM + 46, self.y - 2, VERMELHO, 2.2)
        self.y -= 26

    def titulo(self, texto: str) -> None:
        """Nível 2. Reserva espaço para duas linhas de corpo — título no pé de
        página, com o texto na página seguinte, é o defeito mais visível de um
        layout automático."""
        self._garantir(58)
        self.espaco(10)
        for linha in quebrar(texto, LARGURA_UTIL, 13.5, True):
            self.pdf.texto(MARGEM, self.y - 13.5, linha, 13.5, NAVY, negrito=True)
            self.y -= 18
        self.y -= 6

    def subtitulo(self, texto: str) -> None:
        self._garantir(46)
        self.espaco(6)
        for linha in quebrar(texto, LARGURA_UTIL, 10.5, True):
            self.pdf.texto(MARGEM, self.y - 10.5, linha, 10.5, TEAL, negrito=True)
            self.y -= 14
        self.y -= 3

    def paragrafo(self, texto: str, tamanho: float = 9.8, cor=TINTA,
                  recuo: float = 0.0, italico: bool = False) -> None:
        largura = LARGURA_UTIL - recuo
        entrelinha = tamanho * 1.55
        for linha in quebrar(texto, largura, tamanho):
            self._garantir(entrelinha)
            self.pdf.texto(MARGEM + recuo, self.y - tamanho, linha, tamanho,
                           cor, italico=italico)
            self.y -= entrelinha
        self.y -= 5

    def itens(self, lista: list[str], marcador: str = "•", cor_marcador=TEAL) -> None:
        for item in lista:
            rotulo, _, resto = item.partition(" — ")
            recuo, tamanho = 16.0, 9.8
            entrelinha = tamanho * 1.5
            self._garantir(entrelinha)
            self.pdf.texto(MARGEM + 3, self.y - tamanho, marcador, tamanho,
                           cor_marcador, negrito=True)

            # Item no formato "Rótulo — texto": o rótulo sai em negrito e o
            # resto continua na mesma linha, então a primeira linha precisa ser
            # medida com as duas larguras somadas.
            #
            # O limite de largura não é estética: sem ele, um travessão no meio
            # de uma frase comum faz a frase inteira virar "rótulo" e ser
            # desenhada numa linha só, vazando centenas de pontos para fora da
            # página. Rótulo é curto por definição; o que passa disso é prosa.
            e_rotulo = resto and largura_texto(rotulo, tamanho, True) <= LARGURA_UTIL * 0.42
            if e_rotulo:
                prefixo = f"{rotulo} — "
                largura_prefixo = largura_texto(prefixo, tamanho, True)
                primeira = quebrar(resto, LARGURA_UTIL - recuo - largura_prefixo, tamanho)
                cabeca = primeira[0] if primeira else ""
                self.pdf.texto(MARGEM + recuo, self.y - tamanho, prefixo, tamanho,
                               NAVY, negrito=True)
                self.pdf.texto(MARGEM + recuo + largura_prefixo, self.y - tamanho,
                               cabeca, tamanho, TINTA)
                self.y -= entrelinha
                sobra = resto[len(cabeca):].strip()
                for linha in quebrar(sobra, LARGURA_UTIL - recuo, tamanho):
                    self._garantir(entrelinha)
                    self.pdf.texto(MARGEM + recuo, self.y - tamanho, linha, tamanho, TINTA)
                    self.y -= entrelinha
            else:
                for linha in quebrar(item, LARGURA_UTIL - recuo, tamanho):
                    self._garantir(entrelinha)
                    self.pdf.texto(MARGEM + recuo, self.y - tamanho, linha, tamanho, TINTA)
                    self.y -= entrelinha
            self.y -= 3
        self.y -= 4

    def destaque(self, texto: str, cor_fundo=TINTA_TEAL, cor_barra=TEAL,
                 rotulo: str = "") -> None:
        """Caixa com barra lateral — usada para o que o leitor precisa levar
        mesmo se ler o documento na diagonal."""
        tamanho = 9.6
        entrelinha = tamanho * 1.5
        linhas = quebrar(texto, LARGURA_UTIL - 44, tamanho)
        altura = len(linhas) * entrelinha + 22 + (14 if rotulo else 0)
        self._garantir(altura + 8)

        topo = self.y
        self.pdf.retangulo(MARGEM, topo - altura, LARGURA_UTIL, altura, cor_fundo)
        self.pdf.retangulo(MARGEM, topo - altura, 3.2, altura, cor_barra)

        y = topo - 16
        if rotulo:
            self.pdf.texto(MARGEM + 18, y - 7.5, rotulo.upper(), 7.5, cor_barra,
                           negrito=True, espaco_extra=1.1)
            y -= 15
        for linha in linhas:
            self.pdf.texto(MARGEM + 18, y - tamanho, linha, tamanho, TINTA)
            y -= entrelinha
        self.y = topo - altura - 12

    def tabela(self, cabecalho: list[str], linhas: list[list[str]],
               larguras: list[float], tamanho: float = 8.8) -> None:
        """Tabela simples. `larguras` são frações que somam 1."""
        cols = [LARGURA_UTIL * f for f in larguras]
        entrelinha = tamanho * 1.42

        def altura_da_linha(celulas: list[str], negrito: bool) -> float:
            maior = max(
                len(quebrar(c, cols[i] - 10, tamanho, negrito))
                for i, c in enumerate(celulas)
            )
            return maior * entrelinha + 9

        def desenhar(celulas: list[str], negrito: bool, cor, fundo=None) -> None:
            altura = altura_da_linha(celulas, negrito)
            self._garantir(altura)
            topo = self.y
            if fundo:
                self.pdf.retangulo(MARGEM, topo - altura, LARGURA_UTIL, altura, fundo)
            x = MARGEM
            for i, celula in enumerate(celulas):
                y = topo - 5
                for linha in quebrar(celula, cols[i] - 10, tamanho, negrito):
                    self.pdf.texto(x + 5, y - tamanho, linha, tamanho, cor, negrito=negrito)
                    y -= entrelinha
                x += cols[i]
            self.y = topo - altura
            self.pdf.linha(MARGEM, self.y, MARGEM + LARGURA_UTIL, self.y, FIO)

        self._garantir(70)
        self.espaco(4)
        desenhar(cabecalho, True, BRANCO, NAVY)
        for i, linha in enumerate(linhas):
            desenhar(linha, False, TINTA, None if i % 2 else (0xFA / 255, 0xFB / 255, 0xFC / 255))
        self.y -= 12

    def numero_grande(self, blocos: list[tuple[str, str]]) -> None:
        """Faixa de números — cada bloco é (valor, legenda)."""
        self._garantir(62)
        largura = LARGURA_UTIL / len(blocos)
        topo = self.y
        self.pdf.retangulo(MARGEM, topo - 52, LARGURA_UTIL, 52, TINTA_TEAL)
        for i, (valor, legenda) in enumerate(blocos):
            x = MARGEM + i * largura
            centro = x + largura / 2
            self.pdf.texto(centro - largura_texto(valor, 19, True) / 2, topo - 26,
                           valor, 19, NAVY, negrito=True)
            for j, linha in enumerate(quebrar(legenda, largura - 12, 7.4)):
                self.pdf.texto(centro - largura_texto(linha, 7.4) / 2,
                               topo - 40 - j * 9.5, linha, 7.4, NEUTRO)
            if i:
                self.pdf.linha(x, topo - 44, x, topo - 8, (0.85, 0.89, 0.91))
        self.y = topo - 52 - 14

    # -- capa ---------------------------------------------------------------

    def capa(self, titulo: str, subtitulo: str, autor: str, registro: str,
             data: str, logo: str, etiqueta: str = "") -> None:
        """Capa clara com âncora escura no pé.

        O fundo NÃO é navy, e isso é decisão de arte, não preferência: a logo é
        desenhada na própria paleta — navy, vermelho e teal — e sobre um fundo
        navy o traço principal desapareceria. Recolorir a logo para branco
        resolveria o contraste e destruiria a marca. Então a página é clara e o
        peso escuro vai para a faixa do rodapé, onde fica o nome do médico.
        """
        self.pdf.nova_pagina()
        self.pagina = 1
        self.pdf.retangulo(0, 0, A4[0], A4[1], (0xFC / 255,) * 3)
        self.pdf.retangulo(0, A4[1] - 7, A4[0], 7, VERMELHO)

        self.pdf.imagem("Logo", logo, 0, 0, 0, 0)   # registra a imagem para medir
        self.pdf.atual.pop()                         # e descarta o desenho de medição
        img = self.pdf.imagens["Logo"]
        larg = 264.0
        alt = larg * img["altura"] / img["largura"]
        self.pdf.imagem("Logo", logo, (A4[0] - larg) / 2, A4[1] - 190 - alt, larg, alt)

        y = A4[1] - 300
        for linha in quebrar(titulo, LARGURA_UTIL - 30, 25, True):
            self.pdf.texto((A4[0] - largura_texto(linha, 25, True)) / 2, y, linha,
                           25, NAVY, negrito=True)
            y -= 32

        y -= 4
        self.pdf.linha((A4[0] - 54) / 2, y + 10, (A4[0] + 54) / 2, y + 10, VERMELHO, 2.4)
        y -= 24

        for linha in quebrar(subtitulo, LARGURA_UTIL - 80, 11.5):
            self.pdf.texto((A4[0] - largura_texto(linha, 11.5)) / 2, y, linha, 11.5, TEAL)
            y -= 17

        if etiqueta:
            y -= 26
            largura_et = largura_texto(etiqueta.upper(), 8, True) + 30
            self.pdf.retangulo((A4[0] - largura_et) / 2, y - 7, largura_et, 22, NAVY)
            self.pdf.texto((A4[0] - largura_et) / 2 + 15, y, etiqueta.upper(), 8,
                           BRANCO, negrito=True, espaco_extra=1.2)

        self.pdf.retangulo(0, 0, A4[0], 132, NAVY)
        self.pdf.retangulo(0, 132, A4[0], 3, VERMELHO)
        for texto, tamanho, cor, negrito, altura in (
            (autor, 12.5, BRANCO, True, 88),
            (registro, 8.8, TEAL_CLARO, False, 70),
            (data, 8, (0.55, 0.66, 0.73), False, 40),
        ):
            self.pdf.texto((A4[0] - largura_texto(texto, tamanho, negrito)) / 2,
                           altura, texto, tamanho, cor, negrito=negrito)

    def sumario(self) -> None:
        """Chamado no fim, mas escrito na página 2 — por isso a lista de
        capítulos só existe depois que o documento inteiro foi construído."""
        pass    # ver `montar_sumario` em gerar_apresentacao.py

    def salvar(self, caminho: str) -> None:
        self.pdf.salvar(caminho)
