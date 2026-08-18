"""Identidade visual compartilhada pelos PDFs e e-mails gerados no servidor.

A marca canônica é gerada em runtime com Pillow para evitar qualquer dependência
em assets binários legados do repositório. O resultado é um PNG transparente
usado pelos documentos ReportLab e, quando necessário, pelo transporte SMTP.
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

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

LOGO = Path("/tmp/corvia-logo-canonical.png")


def _interp(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int, int]:
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3)) + (255,)


def _bezier(p0, p1, p2, p3, passos: int = 96):
    pontos = []
    for i in range(passos + 1):
        t = i / passos
        u = 1 - t
        x = u**3*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t**3*p3[0]
        y = u**3*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t**3*p3[1]
        pontos.append((x, y))
    return pontos


def _stroke_gradiente(draw: ImageDraw.ImageDraw, pontos, inicio, fim, largura: int) -> None:
    for i in range(len(pontos) - 1):
        t = i / max(1, len(pontos) - 2)
        draw.line([pontos[i], pontos[i + 1]], fill=_interp(inicio, fim, t), width=largura)
    raio = largura // 2
    for ponto, cor in ((pontos[0], inicio), (pontos[-1], fim)):
        x, y = ponto
        draw.ellipse((x-raio, y-raio, x+raio, y+raio), fill=cor + (255,))


def _fonte(tamanho: int, negrito: bool = False):
    candidatos = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if negrito else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf" if negrito else "/usr/share/fonts/dejavu/DejaVuSans.ttf",
    ]
    for caminho in candidatos:
        if Path(caminho).is_file():
            return ImageFont.truetype(caminho, tamanho)
    return ImageFont.load_default()


def _gerar_logo_canonica() -> None:
    """Gera a wordmark CorVIA Clinical OS aprovada, em fundo transparente."""
    try:
        imagem = Image.new("RGBA", (860, 240), (255, 255, 255, 0))
        draw = ImageDraw.Draw(imagem)

        # Símbolo de três laços convergentes, mesma geometria da marca web.
        azul = _bezier((120, 205), (88, 171), (42, 132), (39, 98)) + _bezier((39, 98), (36, 64), (58, 46), (81, 46))[1:] + _bezier((81, 46), (103, 46), (119, 59), (126, 78))[1:]
        rosa = _bezier((120, 205), (109, 168), (96, 124), (95, 83)) + _bezier((95, 83), (94, 50), (108, 29), (130, 29))[1:] + _bezier((130, 29), (153, 29), (165, 46), (164, 67))[1:] + _bezier((164, 67), (163, 89), (145, 111), (120, 136))[1:]
        violeta = _bezier((120, 205), (137, 163), (160, 118), (186, 100)) + _bezier((186, 100), (206, 86), (225, 91), (230, 109))[1:] + _bezier((230, 109), (236, 131), (218, 156), (193, 175))[1:] + _bezier((193, 175), (172, 191), (145, 202), (120, 205))[1:]
        _stroke_gradiente(draw, azul, (20, 189, 235), (23, 109, 255), 15)
        _stroke_gradiente(draw, rosa, (255, 76, 117), (201, 68, 233), 15)
        _stroke_gradiente(draw, violeta, (60, 75, 255), (138, 54, 239), 15)

        cor_font = _fonte(92, negrito=True)
        sub_font = _fonte(43, negrito=False)
        x = 250
        draw.text((x, 43), "Cor", font=cor_font, fill=(7, 22, 43, 255))
        largura_cor = draw.textlength("Cor", font=cor_font)
        draw.text((x + largura_cor - 4, 43), "VIA", font=cor_font, fill=(18, 141, 244, 255))
        draw.text((252, 146), "C l i n i c a l   O S", font=sub_font, fill=(23, 51, 93, 255))

        imagem.save(LOGO, "PNG", optimize=True)
    except Exception:
        # Documento clínico não deve falhar por branding; logo_disponivel()
        # simplesmente retornará False se o runtime não conseguir gerar o asset.
        try:
            LOGO.unlink(missing_ok=True)
        except OSError:
            pass


_gerar_logo_canonica()


def logo_disponivel() -> bool:
    return LOGO.is_file()
