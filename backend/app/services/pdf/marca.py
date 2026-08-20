"""Identidade visual compartilhada pelos arquivos gerados no servidor.

O PNG empacotado no backend é uma cópia byte a byte do asset canônico usado
pelo frontend. Ele fica dentro do contexto de build do backend para que PDFs,
apresentações e e-mails nunca dependam de arquivo temporário nem reconstruam a
marca em runtime.
"""

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

LOGO = Path(__file__).resolve().parents[2] / "assets" / "corvia-logo-canonical.png"


def logo_disponivel() -> bool:
    return LOGO.is_file()
