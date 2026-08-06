"""Certificado A1 (.pfx/.p12) do próprio médico — provedor `A1_ARQUIVO`
(Trabalho 7, 06/08/2026).

Por que este caminho e não os provedores em nuvem (VIDaaS, Bird ID, ...):
todos exigem uma relação comercial que ninguém abriu ainda (ver ADR em
docs/, e o histórico de pesquisa registrado no handoff) — contato com
`produtos.certificadora@valid.com`, KYC por videoconferência, etc. O A1 é
puramente técnico: o médico já tem (ou compra de qualquer Autoridade
Certificadora credenciada ICP-Brasil) um arquivo `.pfx`/`.p12` com a própria
chave privada, e a Corvia só precisa saber assinar PDF com ele — sem
depender de nenhum terceiro integrado.

O QUE ESTE MÓDULO NÃO FAZ, DE PROPÓSITO: não valida a cadeia de certificação
até a raiz ICP-Brasil. Verificar se o emissor é uma AC credenciada de
verdade é trabalho de quem VALIDA a assinatura depois (Adobe Reader, o
validador do ITI, o futuro SNCR) — é o mesmo modelo de confiança de
qualquer verificador de PAdES no mundo: quem assina prova que tem a chave
privada; quem verifica decide se confia na cadeia. Fazer essa validação
aqui exigiria embutir e manter atualizado o repositório de certificados
raiz da ICP-Brasil, e mesmo assim não substituiria a verificação de quem
recebe o documento. O que este módulo garante, de verdade: o arquivo é um
PKCS#12 válido, a senha abre, a chave privada corresponde ao certificado —
e falha alto (nunca finge sucesso) se qualquer uma dessas checagens falhar.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509.oid import NameOID
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.assinatura import DigitalCertificate
from app.models.user import User
from app.services import cofre


class CertificadoInvalido(ValueError):
    """Arquivo não é PKCS#12 válido, senha errada, ou faltou chave/certificado
    — nunca deixa passar um certificado que a Corvia não consiga de fato usar
    para assinar depois."""


@dataclass
class DadosCertificado:
    chave_privada: object
    certificado: x509.Certificate
    cadeia: list[x509.Certificate]
    titular_cn: str
    numero_serie: str
    valido_ate: datetime


def _extrair_cn(certificado: x509.Certificate) -> str:
    atributos = certificado.subject.get_attributes_for_oid(NameOID.COMMON_NAME)
    if not atributos:
        return certificado.subject.rfc4514_string()
    return str(atributos[0].value)


def analisar(arquivo_bytes: bytes, senha: str) -> DadosCertificado:
    """Só analisa e valida — não persiste nada. Usado tanto no upload (com
    persistência em seguida) quanto para eventual pré-visualização."""
    try:
        chave, certificado, cadeia = pkcs12.load_key_and_certificates(
            arquivo_bytes, senha.encode("utf-8"),
        )
    except ValueError as exc:
        raise CertificadoInvalido(
            "Não foi possível abrir o certificado — confira o arquivo e a senha."
        ) from exc
    if chave is None or certificado is None:
        raise CertificadoInvalido(
            "O arquivo não contém chave privada e certificado juntos — não é um .pfx/.p12 válido para assinatura."
        )
    agora = datetime.now(timezone.utc)
    valido_ate = certificado.not_valid_after_utc
    if valido_ate < agora:
        raise CertificadoInvalido(
            f"Este certificado venceu em {valido_ate:%d/%m/%Y} — gere um novo na sua Autoridade Certificadora antes de conectar."
        )
    return DadosCertificado(
        chave_privada=chave,
        certificado=certificado,
        cadeia=list(cadeia or []),
        titular_cn=_extrair_cn(certificado),
        numero_serie=format(certificado.serial_number, "x").upper(),
        valido_ate=valido_ate,
    )


def _raiz() -> Path:
    return Path(settings.certificados_dir)


def salvar(db: Session, user: User, arquivo_bytes: bytes, senha: str, certificadora: str | None) -> DigitalCertificate:
    """Substitui o certificado anterior do médico, se houver — um por
    usuário. O arquivo velho é apagado do cofre, não fica órfão cifrado sem
    referência nenhuma."""
    dados = analisar(arquivo_bytes, senha)  # falha alto antes de tocar no banco/cofre

    existente = db.query(DigitalCertificate).filter(DigitalCertificate.owner_id == user.id).first()
    nome_antigo = existente.arquivo_nome if existente else None

    nome_arquivo = cofre.guardar(arquivo_bytes, user.id, raiz=_raiz())
    senha_cifrada = cofre.cifrar_campo(senha, user.id)

    registro = existente or DigitalCertificate(owner_id=user.id)
    registro.arquivo_nome = nome_arquivo
    registro.senha_cifrada = senha_cifrada
    registro.titular_cn = dados.titular_cn
    registro.numero_serie = dados.numero_serie
    registro.valido_ate = dados.valido_ate
    registro.certificadora = certificadora
    if not existente:
        db.add(registro)
    db.flush()

    if nome_antigo:
        cofre.apagar(nome_antigo, raiz=_raiz())
    return registro


def remover(db: Session, user: User) -> bool:
    registro = db.query(DigitalCertificate).filter(DigitalCertificate.owner_id == user.id).first()
    if not registro:
        return False
    cofre.apagar(registro.arquivo_nome, raiz=_raiz())
    db.delete(registro)
    db.flush()
    return True


def obter(db: Session, user: User) -> DigitalCertificate | None:
    return db.query(DigitalCertificate).filter(DigitalCertificate.owner_id == user.id).first()


@dataclass
class CertificadoParaAssinar:
    pfx_bytes: bytes
    senha: str
    dados: DadosCertificado


def carregar_para_assinar(db: Session, user: User) -> CertificadoParaAssinar:
    """Decifra o arquivo e a senha uma única vez, e reanalisa — nunca confia
    cegamente nos metadados gravados no banco (ex.: se o cofre foi trocado
    de chave, o erro aparece aqui, na hora de assinar, não em silêncio
    depois). Devolve também os bytes/senha em claro porque `pdf_signer.py`
    precisa deles de novo para `pyhanko` (tipos internos diferentes dos que
    `analisar()` devolve — ver docstring de `pdf_signer.py`), e decifrar
    duas vezes seria redundante."""
    registro = obter(db, user)
    if not registro:
        raise CertificadoInvalido("Nenhum certificado A1 conectado.")
    arquivo_bytes = cofre.ler(registro.arquivo_nome, user.id, raiz=_raiz())
    senha = cofre.decifrar_campo(registro.senha_cifrada, user.id)
    dados = analisar(arquivo_bytes, senha)
    return CertificadoParaAssinar(pfx_bytes=arquivo_bytes, senha=senha, dados=dados)
