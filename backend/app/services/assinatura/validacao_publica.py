"""Código público, estável e não enumerável para validar documento emitido.

O código não é uma senha do paciente nem concede acesso ao PDF. Ele serve
somente para localizar o registro de emissão e conferir, no servidor, o hash
dos bytes persistidos e a assinatura PAdES realmente embutida no arquivo.

Formato: R<id>-<MAC> para receituário e D<id>-<MAC> para documento clínico.
O MAC usa JWT_SECRET e inclui tipo, referência e emissor, portanto não pode ser
fabricado apenas conhecendo um id sequencial.
"""
from __future__ import annotations

import hashlib
import hmac
import re
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.assinatura import DocumentoEmitido
from app.services.assinatura import emissao, verificacao_pdf

_PREFIXOS = {
    emissao.TIPO_RECEITA: "R",
    emissao.TIPO_DOCUMENTO: "D",
}
_TIPOS = {valor: chave for chave, valor in _PREFIXOS.items()}
_CODIGO_RE = re.compile(r"^([RD])(\d+)-([0-9A-F]{16})$")


def _mac(tipo: str, referencia_id: int, criado_por: int) -> str:
    segredo_base = settings.storage_encryption_key or settings.jwt_secret
    segredo = segredo_base.encode("utf-8")
    payload = f"corvia-documento-v1:{tipo}:{referencia_id}:{criado_por}".encode("utf-8")
    return hmac.new(segredo, payload, hashlib.sha256).hexdigest().upper()[:16]


def codigo_documento(*, tipo: str, referencia_id: int, criado_por: int) -> str:
    prefixo = _PREFIXOS.get(tipo)
    if prefixo is None:
        raise ValueError(f"Tipo de documento não suportado para validação pública: {tipo}")
    return f"{prefixo}{referencia_id}-{_mac(tipo, referencia_id, criado_por)}"


def url_documento(*, tipo: str, referencia_id: int, criado_por: int) -> str:
    codigo = codigo_documento(tipo=tipo, referencia_id=referencia_id, criado_por=criado_por)
    return f"{settings.public_url.rstrip('/')}/validar/{codigo}"


def localizar(db: Session, codigo: str) -> DocumentoEmitido | None:
    normalizado = (codigo or "").strip().upper()
    match = _CODIGO_RE.fullmatch(normalizado)
    if not match:
        return None
    prefixo, referencia, mac_recebido = match.groups()
    tipo = _TIPOS[prefixo]
    referencia_id = int(referencia)
    registro = (
        db.query(DocumentoEmitido)
        .filter(
            DocumentoEmitido.tipo == tipo,
            DocumentoEmitido.referencia_id == referencia_id,
        )
        .order_by(DocumentoEmitido.id.desc())
        .first()
    )
    if registro is None:
        return None
    esperado = _mac(tipo, referencia_id, registro.criado_por)
    if not hmac.compare_digest(esperado, mac_recebido):
        return None
    return registro


@dataclass(frozen=True)
class ResultadoValidacao:
    valido: bool
    integridade_hash: bool
    assinatura_encontrada: bool
    assinatura_intacta: bool
    estrutura_valida: bool
    cobre_documento_inteiro: bool
    titular: str | None
    emissor_certificado: str | None
    assinado_em: object | None
    qualificada_icp_brasil: bool
    sha256: str


def validar(registro: DocumentoEmitido) -> ResultadoValidacao:
    pdf = emissao.ler_bytes(registro)
    hash_atual = hashlib.sha256(pdf).hexdigest()
    integridade_hash = hmac.compare_digest(hash_atual, registro.sha256)
    assinatura = verificacao_pdf.verificar(pdf) if registro.assinado_em is not None else None
    assinatura_ok = bool(
        assinatura
        and assinatura.intacta
        and assinatura.estrutura_valida
        and assinatura.cobre_documento_inteiro
    )
    return ResultadoValidacao(
        valido=bool(integridade_hash and assinatura_ok),
        integridade_hash=integridade_hash,
        assinatura_encontrada=assinatura is not None,
        assinatura_intacta=bool(assinatura and assinatura.intacta),
        estrutura_valida=bool(assinatura and assinatura.estrutura_valida),
        cobre_documento_inteiro=bool(assinatura and assinatura.cobre_documento_inteiro),
        titular=assinatura.titular_cn if assinatura else None,
        emissor_certificado=assinatura.emissor_cn if assinatura else None,
        assinado_em=assinatura.assinado_em if assinatura else registro.assinado_em,
        qualificada_icp_brasil=bool(assinatura and assinatura.qualificada_icp_brasil),
        sha256=registro.sha256,
    )
