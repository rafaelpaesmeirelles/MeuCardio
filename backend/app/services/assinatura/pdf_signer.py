"""Assinatura PAdES de fato — aplica a assinatura criptográfica sobre o PDF
já renderizado, usando `pyhanko` (padrão de fato em Python para PAdES,
usa `cryptography` como backend, já dependência do projeto).

Separado de `certificado_a1.py` de propósito: aquele módulo cuida de
guardar/validar o certificado (com `cryptography`, pra extrair CN/validade
pros metadados do banco); este só assina bytes já prontos, usando a API
própria do pyhanko (`SimpleSigner.load_pkcs12_data`, que lê o PKCS#12
direto — não aceita os objetos `cryptography.x509.Certificate`/chave que
`certificado_a1.analisar()` devolve, são bibliotecas com tipos internos
diferentes). Validado manualmente (script em scratchpad, 06/08/2026): PDF
gerado pelo reportlab, assinado aqui, revalidado pelo próprio pyhanko com
`intact=True, valid=True`.

Sem carimbo de tempo (TSA) nesta primeira versão — exigiria configurar um
servidor de carimbo de tempo, que ninguém contratou ainda. Sem isso, a
assinatura é válida (PAdES-B), mas perde validade de longo prazo (LTV) se o
certificado expirar depois — registrado como limitação conhecida, não como
simulação: a assinatura em si é real, só não tem timestamp independente.
"""

from __future__ import annotations

import io
from datetime import datetime

from asn1crypto import x509 as asn1_x509
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.pdf_utils.layout import BoxConstraints
from pyhanko.pdf_utils.text import TextBoxStyle
from pyhanko.sign import fields, signers
from pyhanko.stamp import QRStampStyle, TextStampStyle


class FalhaAoAssinar(RuntimeError):
    """pyhanko recusou assinar — chave/certificado incompatíveis, senha
    errada nesse ponto (não deveria acontecer, já validada antes), ou o PDF
    de entrada está corrompido. Nunca capturado para fingir sucesso."""


# Aparencia VISIVEL da mesma assinatura PAdES. O widget da primeira pagina e
# os selos das paginas adicionais sao criados antes do calculo do hash e
# integram a revisao assinada. Qualquer alteracao no texto, QR ou no restante
# do documento invalida a assinatura.
_CAMPO_VISIVEL_PADRAO = (170, 20, 425, 88)
# A RCE já possui um quadro regulamentar de identificação/assinatura. O selo
# deve ocupar a metade direita desse quadro, sem cobrir comprador ou rodapé.
_CAMPO_VISIVEL_RCE = (285, 220, 545, 270)


class _PdfSignerComInstanteFixo(signers.PdfSigner):
    """Mantém idêntico o horário exibido e o gravado na assinatura.

    Os selos das páginas adicionais são conteúdo normal do PDF, inserido antes
    do cálculo do hash. Fixar o instante no ``PdfSigningSession`` evita que o
    selo da primeira página e os demais divirjam ao atravessar um segundo.
    """

    def __init__(self, *args, instante_assinatura: datetime, **kwargs):
        super().__init__(*args, **kwargs)
        self._instante_assinatura = instante_assinatura

    def init_signing_session(self, pdf_out, existing_fields_only=False):
        sessao = super().init_signing_session(pdf_out, existing_fields_only)
        sessao.system_time = self._instante_assinatura
        return sessao


def _selo_visivel(codigo_validacao: str | None, url_validacao: str | None):
    """Aparência assinada com caminho verificável fora do consultório.

    Quando existe URL pública, usa ``QRStampStyle`` do próprio pyHanko. O QR,
    endereço e código são parte da appearance stream da assinatura e entram
    no byte range assinado; não são desenhados depois da assinatura.
    """
    linhas = [
        "ASSINATURA DIGITAL ICP-BRASIL",
        "%(signer)s",
        "%(ts)s",
    ]
    if url_validacao:
        curto = url_validacao.removeprefix("https://").removeprefix("http://")
        linhas.append(f"Validar: {curto}")
    if codigo_validacao:
        linhas.append(f"Codigo: {codigo_validacao}")
    if not codigo_validacao and not url_validacao:
        linhas.append("Assinatura criptografica embutida neste PDF")

    comum = dict(
        border_width=1,
        border_color=(0.043, 0.180, 0.271),
        background=None,
        background_opacity=1,
        text_box_style=TextBoxStyle(
            # QRStampStyle calcula proporções internamente com Fraction e
            # requer dimensões racionais. Um font_size fracionário (5.3)
            # vira float no box natural e quebra o layout no pyHanko 0.36.2.
            font_size=5 if url_validacao else 6,
            text_color=(0.043, 0.180, 0.271),
        ),
        stamp_text="\n".join(linhas),
        timestamp_format="%d/%m/%Y %H:%M:%S %Z",
    )
    if url_validacao:
        return QRStampStyle(
            **comum,
            qr_inner_size=36,
            innsep=4,
        )
    return TextStampStyle(**comum)


def _aplicar_selo_nas_paginas_adicionais(
    escritor: IncrementalPdfFileWriter,
    *,
    estilo: QRStampStyle | TextStampStyle,
    nome_assinante: str,
    instante_assinatura: datetime,
    url_validacao: str | None,
) -> None:
    """Repete a aparência verificável nas páginas 2..N antes de assinar.

    A primeira página recebe o widget PAdES real em ``PdfSigner``. Nas demais,
    o mesmo selo é aplicado como conteúdo da página *antes* do hash. Assim há
    uma única assinatura criptográfica cobrindo o arquivo inteiro, e cada
    página impressa também conserva identificação, horário, QR/URL e código.
    """
    total_paginas = int(escritor.root["/Pages"]["/Count"])
    if total_paginas <= 1:
        return

    x1, y1, x2, y2 = _CAMPO_VISIVEL_PADRAO
    parametros = {
        "signer": nome_assinante,
        "ts": instante_assinatura.strftime(estilo.timestamp_format),
    }
    if url_validacao:
        parametros["url"] = url_validacao
    selo = estilo.create_stamp(
        escritor,
        BoxConstraints(width=x2 - x1, height=y2 - y1),
        parametros,
    )
    for indice_pagina in range(1, total_paginas):
        selo.apply(indice_pagina, x1, y1)


def assinar_pdf(
    pdf_bytes: bytes, *, pfx_bytes: bytes, senha: str, motivo: str, local: str,
    cadeia_der: list[bytes] | None = None, layout: str | None = None,
    codigo_validacao: str | None = None, url_validacao: str | None = None,
) -> bytes:
    """Assinatura PAdES-B (certificado embutido, sem carimbo de tempo).
    Devolve os bytes do PDF já assinado. `pfx_bytes`/`senha` são os mesmos
    que `certificado_a1.carregar_para_assinar()` decifra do cofre."""
    try:
        certificados_intermediarios = [
            asn1_x509.Certificate.load(certificado)
            for certificado in (cadeia_der or [])
        ]
        signer = signers.SimpleSigner.load_pkcs12_data(
            pfx_bytes,
            other_certs=certificados_intermediarios,
            passphrase=senha.encode("utf-8"),
        )
        if signer is None:
            raise FalhaAoAssinar("Não foi possível carregar o certificado para assinar.")
        escritor = IncrementalPdfFileWriter(io.BytesIO(pdf_bytes))
        metadados = signers.PdfSignatureMetadata(
            field_name="AssinaturaCorvia",
            reason=motivo[:200],
            location=local[:200],
            subfilter=fields.SigSeedSubFilter.PADES,
        )
        campo_visivel = fields.SigFieldSpec(
            sig_field_name="AssinaturaCorvia",
            on_page=0,
            box=_CAMPO_VISIVEL_RCE if layout == "RCE" else _CAMPO_VISIVEL_PADRAO,
            readable_field_name="Assinatura digital CorVIA",
        )
        estilo_selo = _selo_visivel(codigo_validacao, url_validacao)
        instante_assinatura = datetime.now().astimezone()
        _aplicar_selo_nas_paginas_adicionais(
            escritor,
            estilo=estilo_selo,
            nome_assinante=signer.subject_name or "Assinante do certificado",
            instante_assinatura=instante_assinatura,
            url_validacao=url_validacao,
        )
        pdf_signer = _PdfSignerComInstanteFixo(
            metadados,
            signer=signer,
            stamp_style=estilo_selo,
            new_field_spec=campo_visivel,
            instante_assinatura=instante_assinatura,
        )
        appearance_text_params = {"url": url_validacao} if url_validacao else None
        saida = pdf_signer.sign_pdf(
            escritor,
            appearance_text_params=appearance_text_params,
        )
    except FalhaAoAssinar:
        raise
    except Exception as exc:  # noqa: BLE001 — pyhanko levanta vários tipos próprios; traduzimos todos pra um erro nosso
        raise FalhaAoAssinar(f"Falha ao aplicar a assinatura digital: {exc}") from exc
    return saida.getvalue()
