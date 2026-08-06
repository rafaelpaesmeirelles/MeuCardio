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

from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.sign import fields, signers


class FalhaAoAssinar(RuntimeError):
    """pyhanko recusou assinar — chave/certificado incompatíveis, senha
    errada nesse ponto (não deveria acontecer, já validada antes), ou o PDF
    de entrada está corrompido. Nunca capturado para fingir sucesso."""


def assinar_pdf(pdf_bytes: bytes, *, pfx_bytes: bytes, senha: str, motivo: str, local: str) -> bytes:
    """Assinatura PAdES-B (certificado embutido, sem carimbo de tempo).
    Devolve os bytes do PDF já assinado. `pfx_bytes`/`senha` são os mesmos
    que `certificado_a1.carregar_para_assinar()` decifra do cofre."""
    try:
        signer = signers.SimpleSigner.load_pkcs12_data(
            pfx_bytes, other_certs=[], passphrase=senha.encode("utf-8"),
        )
        if signer is None:
            raise FalhaAoAssinar("Não foi possível carregar o certificado para assinar.")
        escritor = IncrementalPdfFileWriter(io.BytesIO(pdf_bytes))
        metadados = signers.PdfSignatureMetadata(
            field_name="AssinaturaCorvia",
            reason=motivo[:200],
            location=local[:200],
        )
        saida = signers.sign_pdf(
            escritor, metadados, signer=signer,
            new_field_spec=fields.SigFieldSpec(sig_field_name="AssinaturaCorvia"),
        )
    except FalhaAoAssinar:
        raise
    except Exception as exc:  # noqa: BLE001 — pyhanko levanta vários tipos próprios; traduzimos todos pra um erro nosso
        raise FalhaAoAssinar(f"Falha ao aplicar a assinatura digital: {exc}") from exc
    return saida.getvalue()
