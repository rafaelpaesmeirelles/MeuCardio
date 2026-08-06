"""Assinatura S/MIME de e-mail (CMS/PKCS#7 detached), pedida pelo Rafael em
06/08/2026 ("assinar digitalmente um email pra enviar"). Reaproveita o
MESMO certificado A1 já usado pra assinar PDF (Trabalho 7) — nenhuma
chave/senha nova, `certificado_a1.carregar_para_assinar()`.

**Só funciona para os caminhos onde a Corvia monta o e-mail bruto por SMTP
— Yahoo e iCloud (`yahoo_mail.py`/`apple_mail.py`).** A caixa nativa do
CorvIA Mail (Mail360) manda por uma API que só aceita campos estruturados
(`fromAddress`/`toAddress`/`content`...) — não existe jeito de injetar um
corpo MIME pré-assinado por ali (verificado em 06/08/2026, lendo o
`enviar_mensagem()` de `app/services/mail360.py`; nenhuma tentativa de
contornar isso foi feita — é limite documentado da API, não bug nosso).

⚠️ **Limite honesto, para não prometer selo verde que não se controla:**
a assinatura produzida aqui é criptograficamente válida — qualquer
adulteração do corpo quebra a verificação, e quem inspecionar o
certificado confirma que veio de quem diz ter vindo. Mas o cliente de
e-mail do destinatário só exibe automaticamente "assinatura verificada"
se a cadeia até a raiz ICP-Brasil estiver na lista de confiança S/MIME
daquele provedor específico (Gmail, Outlook, Apple Mail...) — isso não foi
testado contra nenhum provedor real nesta sessão, porque exigiria uma
caixa de destino de verdade em cada um, e não é algo que a Corvia controle
de qualquer forma. Sem essa confiança, o cliente tende a mostrar "não foi
possível verificar o remetente" em vez de recusar silenciosamente —
comportamento normal de S/MIME com CA não reconhecida, não uma falha desta
implementação.

Técnica: `cryptography.hazmat.primitives.serialization.pkcs7` com
`Encoding.SMIME` já devolve o documento MIME completo (`MIME-Version` +
`Content-Type: multipart/signed...` + corpo) pronto para virar o CORPO da
mensagem — testado manualmente contra a API real desta versão da lib
(`cryptography==50.0.0`) antes de escrever este módulo. Os cabeçalhos de
envelope (`From`/`To`/`Cc`/`Subject`) são concatenados por fora, nunca
dentro da parte assinada — é assim que RFC 1847 define `multipart/signed`.
"""

from __future__ import annotations

from dataclasses import dataclass
from email.message import EmailMessage
from email.utils import formatdate, make_msgid

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.serialization import pkcs7
from sqlalchemy.orm import Session

from app.models.user import User
from app.services.assinatura.certificado_a1 import CertificadoInvalido, carregar_para_assinar, obter


class SmimeIndisponivel(Exception):
    """Sem certificado A1 conectado, ou ele não decifra — quem chama decide
    se isso bloqueia o envio ou cai para o envio sem assinatura S/MIME."""


@dataclass
class AssinanteSmime:
    """Metadados do certificado usado, para exibir no compositor antes de
    enviar (ex.: 'assinado com o certificado de Dr. Fulano, válido até...')."""
    titular_cn: str
    certificadora: str | None
    valido_ate: str


def preparar_assinante(db: Session, user: User) -> AssinanteSmime:
    """Só confere que o certificado existe e decifra — não assina nada
    ainda. Levanta `SmimeIndisponivel` se não houver certificado A1."""
    registro = obter(db, user)
    try:
        cert = carregar_para_assinar(db, user)
    except CertificadoInvalido as exc:
        raise SmimeIndisponivel(str(exc)) from exc
    return AssinanteSmime(
        titular_cn=cert.dados.titular_cn,
        certificadora=registro.certificadora if registro else None,
        valido_ate=cert.dados.valido_ate.isoformat(),
    )


def montar_corpo_assinado(db: Session, user: User, *, html: str) -> bytes:
    """Devolve só o CORPO assinado (multipart/signed completo, com seus
    próprios `MIME-Version`/`Content-Type`) — sem nenhum cabeçalho de
    envelope. `enviar_email_smime()` concatena o envelope por fora.

    Reaproveita `chave_privada`/`certificado`/`cadeia` já decodificados por
    `carregar_para_assinar()` (mesmo objeto `cryptography` nativo que
    `_extrair_cn` já usa) — nunca decodifica o PKCS#12 uma segunda vez."""
    try:
        cert = carregar_para_assinar(db, user)
    except CertificadoInvalido as exc:
        raise SmimeIndisponivel(str(exc)) from exc

    conteudo = EmailMessage()
    conteudo.set_content("Esta mensagem contém conteúdo HTML.")
    conteudo.add_alternative(html, subtype="html")
    dados = conteudo.as_bytes()

    construtor = pkcs7.PKCS7SignatureBuilder().set_data(dados).add_signer(
        cert.dados.certificado, cert.dados.chave_privada, hashes.SHA256(),
    )
    for extra in cert.dados.cadeia:
        construtor = construtor.add_certificate(extra)
    return construtor.sign(serialization.Encoding.SMIME, [pkcs7.PKCS7Options.DetachedSignature])


def montar_mensagem_assinada(
    db: Session, user: User, *, remetente: str, para: list[str], cc: list[str] | None,
    assunto: str, html: str,
) -> bytes:
    """Mensagem crua (bytes), pronta para `smtplib.SMTP.sendmail()` —
    envelope concatenado por fora do corpo assinado, como manda a RFC 1847
    (a parte assinada nunca inclui From/To/Subject)."""
    corpo_assinado = montar_corpo_assinado(db, user, html=html)
    linhas_envelope = [
        f"From: {remetente}",
        f"To: {', '.join(para)}",
    ]
    if cc:
        linhas_envelope.append(f"Cc: {', '.join(cc)}")
    linhas_envelope += [
        f"Subject: {assunto}",
        f"Date: {formatdate(localtime=True)}",
        f"Message-ID: {make_msgid()}",
    ]
    envelope = ("\r\n".join(linhas_envelope) + "\r\n").encode("utf-8")
    return envelope + corpo_assinado
