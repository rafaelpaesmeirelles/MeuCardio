"""Verificação REAL da assinatura digital embutida num PDF já assinado —
pedido do Rafael em 06/08/2026: em vez de confiar em metadado do banco (o
certificado ATUAL do médico, que pode já ter sido trocado), lê o PDF de
verdade e extrai o que está de fato gravado na assinatura PAdES — usado
por `divulgacao_email.py` para qualquer caminho de envio (CorvIA Mail
nativo, Yahoo, iCloud, Google, Microsoft), tanto para receituário quanto
para documento gerado.

Usa `pyhanko.sign.validation.validate_pdf_signature`, a mesma função que
`test_pdf_signer.py` já usa para conferir a própria assinatura depois de
assinar (`status.intact`/`status.valid`) — aqui só lemos mais campos do
mesmo objeto de status, testado manualmente contra um PDF assinado de
verdade antes de escrever este módulo.

⚠️ **Limite honesto:** `validate_pdf_signature()` tenta construir a cadeia
de confiança até uma raiz reconhecida e, sem `signer_validation_context`
configurado com as raízes ICP-Brasil, ela não CONSEGUE — isso gera um erro
de "certificate is self-signed"/"no issuer found" **logado internamente
pelo pyhanko** (não levantado para quem chama; `status.intact`/`status.
valid` continuam preenchidos, porque medem a integridade CRIPTOGRÁFICA do
documento, não a confiança na cadeia). Ou seja: este módulo confirma que o
PDF não foi alterado desde a assinatura e identifica quem assinou — não
confirma que a Autoridade Certificadora é genuína, que é responsabilidade
de quem verifica com uma ferramenta que tenha a raiz ICP-Brasil carregada
(Adobe Reader, o validador do ITI). Mesma ressalva já registrada em
`DigitalCertificate` (`models/assinatura.py`).
"""

from __future__ import annotations

import io
import logging
from dataclasses import dataclass
from datetime import datetime

log = logging.getLogger("meucardio.verificacao_pdf")


@dataclass
class AssinaturaEncontrada:
    intacta: bool
    """Integridade criptográfica do documento — `False` significa que o
    arquivo foi alterado depois de assinado."""
    estrutura_valida: bool
    cobre_documento_inteiro: bool
    titular_cn: str
    emissor_cn: str
    valido_de: datetime
    valido_ate: datetime
    numero_serie: str
    assinado_em: datetime | None
    politicas_certificado: tuple[str, ...]
    qualificada_icp_brasil: bool


_PREFIXOS_POLITICA_ICP_BRASIL = (
    "2.16.76.1.2.1.",  # A1
    "2.16.76.1.2.2.",  # A2
    "2.16.76.1.2.3.",  # A3
    "2.16.76.1.2.4.",  # A4
)


def _politicas_certificado(certificado_asn1) -> tuple[str, ...]:
    """Extrai as Certificate Policies sem inferir pelo nome do emissor.

    Os prefixos são os OIDs oficiais das políticas A1/A2/A3/A4 da
    ICP-Brasil (DOC-ICP-04.01). A cadeia/revogação continua sendo uma
    validação distinta, conforme a ressalva do módulo.
    """
    from cryptography import x509
    from cryptography.x509.oid import ExtensionOID

    try:
        certificado = x509.load_der_x509_certificate(certificado_asn1.dump())
        extensao = certificado.extensions.get_extension_for_oid(
            ExtensionOID.CERTIFICATE_POLICIES
        )
    except (ValueError, x509.ExtensionNotFound):
        return ()
    return tuple(
        politica.policy_identifier.dotted_string
        for politica in extensao.value
    )


def verificar(pdf_bytes: bytes) -> AssinaturaEncontrada | None:
    """`None` quando o PDF não tem nenhuma assinatura embutida (emissão
    MANUAL, sem certificado) ou não pôde ser lido — nunca inventa dado."""
    from pyhanko.pdf_utils.reader import PdfFileReader
    from pyhanko.sign.validation import validate_pdf_signature
    from pyhanko.sign.validation.status import SignatureCoverageLevel

    try:
        leitor = PdfFileReader(io.BytesIO(pdf_bytes))
        assinaturas = leitor.embedded_signatures
    except Exception:
        log.exception("Falha ao abrir PDF para verificar assinatura embutida.")
        return None
    if not assinaturas:
        return None

    try:
        status = validate_pdf_signature(assinaturas[0])
    except Exception:
        log.exception("Falha ao validar assinatura embutida no PDF.")
        return None

    cert = status.signing_cert
    politicas = _politicas_certificado(cert)
    return AssinaturaEncontrada(
        intacta=status.intact,
        estrutura_valida=status.valid,
        cobre_documento_inteiro=status.coverage == SignatureCoverageLevel.ENTIRE_FILE,
        titular_cn=cert.subject.native.get("common_name", "desconhecido"),
        emissor_cn=cert.issuer.native.get("common_name", "desconhecido"),
        valido_de=cert.not_valid_before,
        valido_ate=cert.not_valid_after,
        numero_serie=str(cert.serial_number),
        assinado_em=status.signer_reported_dt,
        politicas_certificado=politicas,
        qualificada_icp_brasil=any(
            oid.startswith(_PREFIXOS_POLITICA_ICP_BRASIL)
            for oid in politicas
        ),
    )
