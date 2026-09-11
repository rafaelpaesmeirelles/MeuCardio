"""Identidade da operadora da plataforma, distinta do profissional emitente.

Dados fornecidos pelo Rafael em 30/07/2026, transferidos sem alteração de
``pdf_documento.EMPRESA``. Não dependem do médico, do paciente ou do banco.
"""
from reportlab.lib.units import mm

from app.services.pdf.wrapping import wrap_text


EMPRESA = {
    "razao_social": "Meirelles e Maluf Serviços Médicos e Biomédicos Ltda.",
    "cnpj": "53.382.596/0001-06",
    "logradouro": "Av. 11",
    "numero": "423",
    "bairro": "Centro",
    "cidade": "Itapagipe",
    "uf": "MG",
    "cep": "38240-000",
}

ROTULO_OPERADORA = "Operadora da plataforma CorVIA"


def desenhar_identidade_institucional(c, x: float, y: float, largura: float) -> float:
    """Draw the canonical operator identification; return the next free baseline.

    ``y`` is the first baseline. All lines wrap by actual glyph width so the
    caller can reserve the complete block before drawing clinical content.
    """
    endereco = (
        f"{EMPRESA['logradouro']}, {EMPRESA['numero']} — {EMPRESA['bairro']} · "
        f"{EMPRESA['cidade']}/{EMPRESA['uf']} · CEP {EMPRESA['cep']}"
    )
    campos = (
        (ROTULO_OPERADORA, "Helvetica-Bold", 8),
        (EMPRESA["razao_social"], "Helvetica", 8.2),
        (f"CNPJ {EMPRESA['cnpj']} · {endereco}", "Helvetica", 8),
    )
    c.saveState()
    c.setFillColorRGB(0.20, 0.24, 0.25)
    for texto, fonte, tamanho in campos:
        c.setFont(fonte, tamanho)
        linhas = wrap_text(texto, largura, lambda linha: c.stringWidth(linha, fonte, tamanho))
        for linha in linhas:
            c.drawString(x, y, linha)
            y -= 3.6 * mm
    c.restoreState()
    return y
