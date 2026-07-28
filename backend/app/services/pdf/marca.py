"""Paleta e elementos de marca compartilhados pelos PDFs gerados no servidor.

As cores vêm de `frontend/src/styles/tokens.css`. Estão repetidas aqui porque o
PDF não lê CSS — este é o quinto lugar fora do CSS que precisa acompanhar uma
troca de paleta, junto do tema do mermaid em `Fluxograma.tsx`, do `theme_color`
do PWA em `vite.config.ts`, da meta `theme-color` do `index.html` e do gerador
de apresentação institucional em `.claude/ferramentas/`.

Regra de arte que vale para todo documento gerado aqui: **a logo não vai sobre
fundo navy**. Ela é desenhada na própria paleta — navy, vermelho e teal — e
sobre navy o traço principal desaparece. Recolorir para branco resolveria o
contraste e destruiria a marca. Onde é preciso peso escuro, a faixa escura vai
em outra região da página, não atrás da logo.
"""

from __future__ import annotations

from pathlib import Path

NAVY = (0x0B / 255, 0x2E / 255, 0x45 / 255)
NAVY_ESCURO = (0x08 / 255, 0x1E / 255, 0x30 / 255)
TEAL = (0x1C / 255, 0x72 / 255, 0x93 / 255)
TEAL_CLARO = (0x6F / 255, 0xB4 / 255, 0xCC / 255)
VERMELHO = (0xD5 / 255, 0x00 / 255, 0x1D / 255)
TINTA = (0x26 / 255, 0x33 / 255, 0x3B / 255)
NEUTRO = (0x55 / 255, 0x66 / 255, 0x6F / 255)
FIO = (0xE4 / 255, 0xE8 / 255, 0xEA / 255)
BRANCO = (1.0, 1.0, 1.0)
OFF_WHITE = (0xFC / 255, 0xFC / 255, 0xFC / 255)
TINTA_TEAL = (0xEF / 255, 0xF5 / 255, 0xF8 / 255)
TINTA_VERMELHA = (0xFD / 255, 0xEE / 255, 0xF0 / 255)
VERDE_CONDUTA = (0xEE / 255, 0xF6 / 255, 0xEF / 255)
VERDE_TRACO = (0x2F / 255, 0x7A / 255, 0x4F / 255)

LOGO = Path(__file__).resolve().parent.parent.parent / "assets" / "corvia-logo.png"


def logo_disponivel() -> bool:
    """O PDF continua saindo sem a logo — ausência de arquivo não derruba a
    geração de um documento clínico, só o deixa sem a marca no topo."""
    return LOGO.is_file()
