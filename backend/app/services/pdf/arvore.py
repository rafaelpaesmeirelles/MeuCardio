"""Desenha a árvore de decisão de um fluxograma direto no PDF.

O fluxograma da plataforma é escrito em ```mermaid``` e renderizado no browser
pela própria lib. No servidor isso não existe: o mermaid precisa de um DOM e de
`getBBox`, que jsdom não implementa — é a mesma limitação já registrada para os
validadores da sessão. Então, para o modo apresentação, a árvore é
**redesenhada aqui**, a partir do mesmo texto-fonte.

Isso só é viável porque o formato dos fluxogramas é estrito e verificável: uma
raiz, cada nó não-raiz com exatamente um pai, sem ciclo, folha sempre conduta.
Ou seja, é literalmente uma árvore — e árvore tem algoritmo de layout simples e
determinístico. Se o formato fosse grafo livre, isto não caberia num módulo.

Formas, iguais às da tela:
- retângulo  `X["..."]`      passo
- losango    `D{"...?"}`     decisão, com rótulo em toda aresta que sai
- estádio    `C(["..."])`    conduta, sempre folha (desenhada com cantos redondos)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .marca import (
    BRANCO, FIO, NAVY, NEUTRO, TEAL, TINTA, TINTA_TEAL, VERDE_CONDUTA,
    VERDE_TRACO,
)
from .nucleo import largura_texto

# Formas: `C(["..."])` precisa vir antes de `[...]`, senão o colchete simples
# casaria primeiro e a conduta viraria passo.
_FORMA = r"(?:\(\[[^\]]*\]\)|\{[^}]*\}|\[[^\]]*\])"
NO = re.compile(
    r'(\w+)\s*(?:'
    r'\(\[\s*"?(?P<conduta>.*?)"?\s*\]\)'
    r'|\{\s*"?(?P<decisao>.*?)"?\s*\}'
    r'|\[\s*"?(?P<passo>.*?)"?\s*\]'
    r')'
)
# `A --> B`, `A -->|Não| B`, `A -->|"Alto risco"| B` — e, principalmente, a
# forma em que os nós são declarados na própria linha da aresta:
# `R0["..."] --> P1["..."]`. Sem tolerar a declaração no meio, nenhuma aresta
# dos fluxogramas reais casava.
ARESTA = re.compile(
    rf'(\w+)\s*{_FORMA}?\s*--+>\s*(?:\|\s*"?(.*?)"?\s*\|\s*)?(\w+)'
)


def _texto_do_no(m: re.Match) -> tuple[str, str]:
    """Devolve (texto, forma) a partir do casamento de `NO`."""
    for nome in ("conduta", "decisao", "passo"):
        valor = m.group(nome)
        if valor is not None:
            return valor.strip(), nome
    return "", "passo"


@dataclass
class No:
    id: str
    texto: str
    forma: str                      # passo | decisao | conduta
    filhos: list[tuple[str, "No"]] = field(default_factory=list)   # (rótulo, nó)
    # preenchidos no layout
    x: float = 0.0
    y: float = 0.0
    largura: float = 0.0
    altura: float = 0.0
    linhas: list[str] = field(default_factory=list)


def extrair_mermaid(markdown: str) -> str | None:
    """Devolve o conteúdo do primeiro bloco ```mermaid``` do documento."""
    m = re.search(r"```mermaid\s*\n(.*?)```", markdown, re.S)
    return m.group(1) if m else None


def montar(fonte: str) -> No | None:
    """Constrói a árvore a partir do texto mermaid. Devolve None se não for árvore.

    Não tenta consertar grafo: se houver mais de uma raiz ou um nó com dois pais,
    devolve None e quem chamou cai para a representação textual. Desenhar um
    grafo com algoritmo de árvore produziria um diagrama silenciosamente errado,
    que é pior do que não desenhar.
    """
    nos: dict[str, No] = {}
    for m in NO.finditer(fonte):
        ident = m.group(1)
        texto, forma = _texto_do_no(m)
        # Um id pode reaparecer sem a forma (só como destino de outra aresta);
        # a primeira declaração com texto é a que vale.
        if ident not in nos or (not nos[ident].texto and texto):
            nos[ident] = No(id=ident, texto=texto, forma=forma)
    if not nos:
        return None

    com_pai: set[str] = set()
    for origem, rotulo, destino in (m.groups() for m in ARESTA.finditer(fonte)):
        if origem not in nos or destino not in nos:
            return None
        if destino in com_pai:          # dois pais: não é árvore
            return None
        com_pai.add(destino)
        nos[origem].filhos.append(((rotulo or "").strip(), nos[destino]))

    raizes = [n for i, n in nos.items() if i not in com_pai]
    if len(raizes) != 1:
        return None

    # Ciclo com raiz única é possível em teoria; a contagem de nós alcançáveis
    # a partir da raiz denuncia.
    vistos: set[str] = set()

    def caminhar(n: No) -> None:
        if n.id in vistos:
            return
        vistos.add(n.id)
        for _, f in n.filhos:
            caminhar(f)

    caminhar(raizes[0])
    return raizes[0] if len(vistos) == len(nos) else None


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

def _medir(n: No, largura_max: float, corpo: float) -> None:
    """Mede a caixa de um nó **pela forma que ele realmente tem**.

    Retângulo é o caso fácil: largura do texto mais folga. As outras duas formas
    perdem área útil onde o texto está, e ignorar isso foi o defeito relatado —
    as frases não vazavam do retângulo envolvente, mas encostavam ou saíam da
    silhueta desenhada:

    - **Losango**: a largura disponível diminui conforme se afasta do centro
      vertical. A primeira e a última linha caem justamente onde a forma já
      estreitou, então a largura é calculada a partir da linha mais exigente,
      cada uma medida na altura em que ela de fato fica.
    - **Estádio**: as duas pontas são arredondadas. O texto precisa de folga
      maior que a do retângulo para não encostar na curva.
    """
    from .layout import quebrar

    # O `<br/>` do mermaid é quebra deliberada de quem escreveu o fluxograma,
    # pensada para manter a caixa estreita. Honrar isso e reagrupar cada trecho
    # dá caixas muito mais próximas do que se vê na tela.
    bruto = re.sub(r"\*\*|__", "", n.texto)
    segmentos = [t.strip() for t in re.split(r"<br\s*/?>", bruto) if t.strip()]
    n.linhas = []
    for seg in segmentos or [""]:
        n.linhas.extend(quebrar(seg, largura_max - 20, corpo) or [""])
    n.linhas = n.linhas or [""]

    entrelinha = corpo * 1.32
    larguras = [largura_texto(l, corpo) for l in n.linhas]
    altura_texto = len(n.linhas) * entrelinha

    if n.forma == "decisao":
        n.altura = altura_texto * 1.45 + 26
        # Para cada linha, a fração da largura total ainda disponível na altura
        # em que ela cai. `1 - 2|dy|/H` é a meia-largura do losango naquele nível.
        precisa = []
        for i, larg in enumerate(larguras):
            dy = altura_texto / 2 - (i + 0.5) * entrelinha
            fracao = max(0.25, 1 - 2 * abs(dy) / n.altura)
            precisa.append((larg + 14) / fracao)
        n.largura = min(largura_max * 1.7, max(precisa))
    elif n.forma == "conduta":
        n.altura = altura_texto + 16
        raio = min(n.altura / 2, 14)
        # Folga = padding normal + o que as duas pontas arredondadas consomem.
        n.largura = min(largura_max + 2 * raio, max(larguras) + 22 + 1.6 * raio)
    else:
        n.altura = altura_texto + 16
        n.largura = min(largura_max, max(larguras) + 22)

    for _, f in n.filhos:
        _medir(f, largura_max, corpo)


def _extensao(n: No, folga: float) -> float:
    """Largura horizontal que a subárvore ocupa."""
    if not n.filhos:
        return n.largura + folga
    return max(n.largura + folga, sum(_extensao(f, folga) for _, f in n.filhos))


def _posicionar(n: No, esquerda: float, topo: float, folga: float,
                altura_nivel: float) -> None:
    largura_total = _extensao(n, folga)
    n.x = esquerda + largura_total / 2
    n.y = topo
    cursor = esquerda
    for _, f in n.filhos:
        sub = _extensao(f, folga)
        _posicionar(f, cursor, topo - altura_nivel, folga, altura_nivel)
        cursor += sub


def _profundidade(n: No) -> int:
    return 1 + max((_profundidade(f) for _, f in n.filhos), default=0)


def _altura_maxima(n: No) -> float:
    """Caixa mais alta da árvore — define se um nível cabe na faixa disponível."""
    return max([n.altura] + [_altura_maxima(f) for _, f in n.filhos])


# ---------------------------------------------------------------------------
# Desenho
# ---------------------------------------------------------------------------

def _forma(pdf, n: No, corpo: float) -> None:
    x, y, w, h = n.x - n.largura / 2, n.y - n.altura, n.largura, n.altura
    if n.forma == "decisao":
        cx, cy = n.x, n.y - n.altura / 2
        pdf.poligono(
            [(cx, cy + h / 2), (cx + w / 2, cy), (cx, cy - h / 2), (cx - w / 2, cy)],
            preenchimento=TINTA_TEAL, traco=TEAL, espessura=1.1,
        )
        cor = NAVY
    elif n.forma == "conduta":
        # Estádio: retângulo com duas meias-cabeças. Aproximado por um retângulo
        # central e dois octógonos laterais — o núcleo não tem curva de Bézier,
        # e a silhueta resultante é indistinguível na projeção.
        r = min(h / 2, 14)
        pdf.retangulo_traco(x + r, y, w - 2 * r, h, VERDE_CONDUTA, VERDE_TRACO, 1.1)
        for lado in (x + r, x + w - r):
            sinal = -1 if lado == x + r else 1
            pdf.poligono(
                [(lado, y), (lado + sinal * r * 0.8, y + h * 0.18),
                 (lado + sinal * r, y + h / 2),
                 (lado + sinal * r * 0.8, y + h * 0.82), (lado, y + h)],
                preenchimento=VERDE_CONDUTA, traco=VERDE_TRACO, espessura=1.1,
            )
        cor = (0x12 / 255, 0x30 / 255, 0x1F / 255)
    else:
        pdf.retangulo_traco(x, y, w, h, BRANCO, NAVY, 1.1)
        cor = TINTA

    ty = n.y - (n.altura - len(n.linhas) * corpo * 1.32) / 2 - corpo
    for linha in n.linhas:
        pdf.texto(n.x - largura_texto(linha, corpo) / 2, ty, linha, corpo, cor)
        ty -= corpo * 1.32


def _arestas(pdf, n: No, corpo: float) -> None:
    for rotulo, f in n.filhos:
        x1, y1 = n.x, n.y - n.altura
        x2, y2 = f.x, f.y
        meio = (y1 + y2) / 2
        pdf.linha(x1, y1, x1, meio, NEUTRO, 0.9)
        pdf.linha(x1, meio, x2, meio, NEUTRO, 0.9)
        pdf.linha(x2, meio, x2, y2, NEUTRO, 0.9)
        # seta
        pdf.poligono([(x2, y2), (x2 - 3.2, y2 + 6), (x2 + 3.2, y2 + 6)],
                     preenchimento=NEUTRO)
        if rotulo:
            t = corpo * 0.82
            w = largura_texto(rotulo, t, True) + 8
            pdf.retangulo(x2 - w / 2, meio - t * 0.55, w, t * 1.5, BRANCO)
            pdf.texto(x2 - largura_texto(rotulo, t, True) / 2, meio - t * 0.15,
                      rotulo, t, TEAL, negrito=True)
        _arestas(pdf, f, corpo)


def _desenhar(pdf, n: No, corpo: float) -> None:
    _arestas(pdf, n, corpo)          # arestas primeiro, para as caixas cobrirem
    def caixas(x: No) -> None:
        _forma(pdf, x, corpo)
        for _, f in x.filhos:
            caixas(f)
    caixas(n)


def render(apres, fonte: str, titulo: str) -> bool:
    """Desenha a árvore numa página da apresentação. Devolve False se não couber
    como árvore — nesse caso o chamador usa a versão em lista."""
    raiz = montar(fonte)
    if raiz is None:
        return False

    from .layout import quebrar

    apres.abrir_pagina()
    for linha in quebrar(titulo, apres.util, 17, True):
        apres.pdf.texto(apres.margem, apres.y, linha, 17, NAVY, negrito=True)
        apres.y -= 22
    apres.y -= 6

    disponivel_larg = apres.util
    disponivel_alt = apres.y - apres.base

    # Três degraus de corpo, do mais legível ao mínimo aceitável para projeção.
    # Abaixo do último o diagrama deixaria de ser lido de longe e vira lista —
    # que perde o desenho mas preserva o caminho até cada conduta.
    # Os degraus **alargam** a caixa conforme o corpo diminui, em vez de
    # estreitá-la. A página é paisagem: sobra largura e falta altura, e caixa
    # estreita produz mais linhas de texto, que é justamente o que consome
    # altura. Estreitar para "caber" empurrava na direção errada — medido:
    # com caixas estreitas, 5 dos 16 fluxogramas viravam diagrama; alargando,
    # 12. O que continua sem caber é árvore de 7 níveis ou mais, e essa cai
    # para lista por limite real de página, não por escolha de tamanho.
    for corpo, largura_max, folga in ((9.5, 176, 24), (8.5, 210, 18),
                                      (7.5, 240, 12), (7.0, 268, 10)):
        _medir(raiz, largura_max, corpo)
        niveis = _profundidade(raiz)
        # A altura de nível se adapta à profundidade em vez de ter piso fixo:
        # com piso, árvore de 9 níveis nunca caberia, mesmo com caixas baixas.
        # O espaçamento entre níveis é ditado pela caixa mais alta da árvore —
        # tipicamente um losango, que é 1,7x mais alto que um retângulo. Dividir
        # a altura igualmente entre os níveis ignorava isso e fazia losango
        # invadir o nível de baixo.
        mais_alto = _altura_maxima(raiz)
        minimo = mais_alto + 12
        largura = _extensao(raiz, folga)
        cabe_em_altura = niveis * minimo <= disponivel_alt
        altura_nivel = min(96.0, disponivel_alt / max(niveis, 1)) if cabe_em_altura else minimo
        if largura <= disponivel_larg and cabe_em_altura:
            _posicionar(raiz, apres.margem + (disponivel_larg - largura) / 2,
                        apres.y, folga, altura_nivel)
            _desenhar(apres.pdf, raiz, corpo)
            apres.y = apres.base
            return True
    return False


def em_lista(raiz: No, prefixo: str = "") -> list[str]:
    """Árvore como texto indentado — usado quando o diagrama não cabe na página.

    Perde a leitura visual, mas preserva a informação que importa: o caminho da
    raiz até cada conduta, com o rótulo de cada decisão.
    """
    saida: list[str] = []
    marca = {"decisao": "?", "conduta": "→", "passo": ""}[raiz.forma]
    saida.append(f"{prefixo}{raiz.texto}{marca}".rstrip())
    for rotulo, f in raiz.filhos:
        cabeca = f"{prefixo}    " + (f"[{rotulo}] " if rotulo else "")
        saida.extend(em_lista(f, cabeca))
    return saida
