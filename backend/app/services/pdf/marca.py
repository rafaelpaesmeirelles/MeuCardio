"""Identidade visual compartilhada pelos arquivos gerados no servidor.

O PNG empacotado no backend é uma renderização determinística do SVG Atelier
em cobre polido, idêntica à cópia pública em /atelier/corvia-logo-atelier.png.
A base branca mantém a legibilidade em impressão e capas escuras. O asset
fica dentro do build para que novas emissões PDF, Office e e-mails não
dependam de arquivo temporário nem reconstruam a marca em runtime. Documentos
já persistidos ou assinados nunca são regravados por este módulo.
"""

from pathlib import Path

# Nomes NAVY mantidos por compatibilidade; a identidade atual usa grafite.
NAVY = (0x24 / 255, 0x34 / 255, 0x3A / 255)
NAVY_ESCURO = (0x18 / 255, 0x28 / 255, 0x2D / 255)
TEAL = (0x16 / 255, 0x77 / 255, 0x6D / 255)
TEAL_CLARO = (0xA6 / 255, 0xCE / 255, 0xC6 / 255)
COBRE = (0xB6 / 255, 0x6D / 255, 0x48 / 255)
# Reflexo claro: decoração ou texto sobre grafite, nunca texto sobre papel.
COBRE_CLARO = (0xD3 / 255, 0x97 / 255, 0x70 / 255)
# Cores semânticas clínicas não acompanham a troca decorativa de marca.
VERMELHO = (0xD5 / 255, 0x00 / 255, 0x1D / 255)
TINTA = NAVY_ESCURO
NEUTRO = (0x54 / 255, 0x63 / 255, 0x67 / 255)
FIO = (0xDE / 255, 0xDC / 255, 0xD4 / 255)
BRANCO = (1.0, 1.0, 1.0)
OFF_WHITE = (0xFF / 255, 0xFD / 255, 0xFA / 255)
TINTA_TEAL = (0xF6 / 255, 0xF3 / 255, 0xEB / 255)
TINTA_VERMELHA = (0xFD / 255, 0xEE / 255, 0xF0 / 255)
VERDE_CONDUTA = (0xEE / 255, 0xF6 / 255, 0xEF / 255)
VERDE_TRACO = (0x2F / 255, 0x7A / 255, 0x4F / 255)

LOGO = Path(__file__).resolve().parents[2] / "assets" / "corvia-logo-atelier.png"


def rgb8(cor: tuple[float, float, float]) -> tuple[int, int, int]:
    """Converte o mesmo token PDF para Office sem cópias locais da paleta."""
    return round(cor[0] * 255), round(cor[1] * 255), round(cor[2] * 255)


def cor_hex(cor: tuple[float, float, float]) -> str:
    return "".join(f"{canal:02X}" for canal in rgb8(cor))


def logo_disponivel() -> bool:
    return LOGO.is_file()
