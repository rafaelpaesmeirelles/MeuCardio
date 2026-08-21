"""Validação pública e download seguro do PDF clínico efetivamente emitido.

Há dois formatos compatíveis:
- legado: ``R<ref>-<16hex>`` / ``D<ref>-<16hex>``, HMAC determinístico usado
  nas emissões anteriores; continua autenticando metadados, mas não libera PDF;
- atual: ``R<ref>-<32hex>`` / ``D<ref>-<32hex>``, capability aleatória de
  128 bits gerada POR EMISSÃO. O banco guarda somente SHA-256 da capability.

O formato atual amarra o QR a um ``DocumentoEmitido`` imutável específico.
Assim, duas assinaturas/emissões da mesma referência recebem códigos diferentes
e um QR antigo nunca passa silenciosamente a apontar para uma emissão posterior.
"""
from __future__ import annotations

import hashlib
import hmac
import re
import secrets
from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.assinatura import DocumentoEmitido
from app.services.assinatura import catalogo, emissao, verificacao_pdf

_PREFIXOS = {
    emissao.TIPO_RECEITA: "R",
    emissao.TIPO_DOCUMENTO: "D",
}
_TIPOS = {valor: chave for chave, valor in _PREFIXOS.items()}
_MAC_HEX_LEGADO = 16
_TOKEN_HEX_ATUAL = 32
_CODIGO_RE = re.compile(r"^([RD])(\d+)-([0-9A-F]{16}|[0-9A-F]{32})$")


def normalizar_codigo(codigo: str) -> str:
    return (codigo or "").strip().upper().replace(" ", "")


def _mac_legado(tipo: str, referencia_id: int, criado_por: int) -> str:
    segredo_base = settings.storage_encryption_key or settings.jwt_secret
    segredo = segredo_base.encode("utf-8")
    payload = f"corvia-documento-v1:{tipo}:{referencia_id}:{criado_por}".encode("utf-8")
    return hmac.new(segredo, payload, hashlib.sha256).hexdigest().upper()[:_MAC_HEX_LEGADO]


def _hash_capability(codigo: str) -> str:
    return hashlib.sha256(normalizar_codigo(codigo).encode("ascii")).hexdigest()


def codigo_documento(*, tipo: str, referencia_id: int, criado_por: int) -> str:
    """Reconstitui o código LEGADO de 64 bits para compatibilidade histórica."""
    prefixo = _PREFIXOS.get(tipo)
    if prefixo is None:
        raise ValueError(f"Tipo de documento não suportado para validação pública: {tipo}")
    return f"{prefixo}{referencia_id}-{_mac_legado(tipo, referencia_id, criado_por)}"


def url_documento(*, tipo: str, referencia_id: int, criado_por: int) -> str:
    """URL histórica; novas emissões usam ``novo_codigo_documento``."""
    codigo = codigo_documento(tipo=tipo, referencia_id=referencia_id, criado_por=criado_por)
    return url_para_codigo(codigo)


@dataclass(frozen=True)
class CodigoNovo:
    codigo: str
    hash_persistido: str


def novo_codigo_documento(*, tipo: str, referencia_id: int) -> CodigoNovo:
    prefixo = _PREFIXOS.get(tipo)
    if prefixo is None:
        raise ValueError(f"Tipo de documento não suportado para validação pública: {tipo}")
    token = secrets.token_hex(16).upper()  # 128 bits não enumeráveis
    codigo = f"{prefixo}{referencia_id}-{token}"
    return CodigoNovo(codigo=codigo, hash_persistido=_hash_capability(codigo))


def url_para_codigo(codigo: str) -> str:
    return f"{settings.public_url.rstrip('/')}/validar/{normalizar_codigo(codigo)}"


def codigo_permite_download(codigo: str) -> bool:
    """Somente a capability aleatória atual pode liberar conteúdo clínico."""
    match = _CODIGO_RE.fullmatch(normalizar_codigo(codigo))
    return bool(match and len(match.group(3)) == _TOKEN_HEX_ATUAL)


def localizar(db: Session, codigo: str) -> DocumentoEmitido | None:
    normalizado = normalizar_codigo(codigo)
    match = _CODIGO_RE.fullmatch(normalizado)
    if not match:
        return None
    prefixo, referencia, segredo_recebido = match.groups()
    tipo = _TIPOS[prefixo]
    referencia_id = int(referencia)

    if len(segredo_recebido) == _TOKEN_HEX_ATUAL:
        # Nova capability: localiza exatamente a emissão que criou aquele QR.
        return (
            db.query(DocumentoEmitido)
            .filter(
                DocumentoEmitido.tipo == tipo,
                DocumentoEmitido.referencia_id == referencia_id,
                DocumentoEmitido.validation_token_hash == _hash_capability(normalizado),
            )
            .first()
        )

    # Compatibilidade com QR legado. Como o formato antigo não tinha identidade
    # por emissão, só pode continuar como validação de autenticidade, nunca como
    # credencial de download do PDF.
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
    esperado = _mac_legado(tipo, referencia_id, registro.criado_por)
    if not hmac.compare_digest(esperado, segredo_recebido):
        return None
    return registro


def _fluxo_assinatura(registro: DocumentoEmitido) -> tuple[str, str]:
    if registro.metodo == "A1_ARQUIVO" and registro.assinado_em is not None:
        return (
            "corvia_local",
            "Assinatura criptográfica realizada dentro do CorVIA com o certificado A1 conectado pelo prescritor.",
        )
    if registro.assinado_em is not None:
        return (
            "externo_reimportado",
            "PDF assinado fora do CorVIA e reimportado; o CorVIA conferiu a assinatura embutida e a integridade do arquivo.",
        )
    return "sem_assinatura", "Documento sem assinatura digital concluída."


def _utc(valor: datetime) -> datetime:
    if valor.tzinfo is None:
        return valor.replace(tzinfo=timezone.utc)
    return valor.astimezone(timezone.utc)


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
    numero_serie: str | None
    certificado_valido_de: datetime | None
    certificado_valido_ate: datetime | None
    certificado_valido_no_momento_assinatura: bool | None
    politicas_certificado: tuple[str, ...]
    assinado_em: object | None
    qualificada_icp_brasil: bool
    sha256: str
    registrado_corvia_em: datetime
    metodo_codigo: str
    metodo_nome: str
    metodo_familia: str
    fluxo_assinatura: str
    fluxo_assinatura_descricao: str


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
    assinado_em = assinatura.assinado_em if assinatura else registro.assinado_em
    certificado_valido_no_momento: bool | None = None
    if assinatura and assinado_em is not None:
        momento = _utc(assinado_em)
        certificado_valido_no_momento = bool(
            _utc(assinatura.valido_de) <= momento <= _utc(assinatura.valido_ate)
        )
    info = catalogo.info(registro.metodo)
    fluxo, fluxo_descricao = _fluxo_assinatura(registro)
    return ResultadoValidacao(
        valido=bool(integridade_hash and assinatura_ok),
        integridade_hash=integridade_hash,
        assinatura_encontrada=assinatura is not None,
        assinatura_intacta=bool(assinatura and assinatura.intacta),
        estrutura_valida=bool(assinatura and assinatura.estrutura_valida),
        cobre_documento_inteiro=bool(assinatura and assinatura.cobre_documento_inteiro),
        titular=assinatura.titular_cn if assinatura else None,
        emissor_certificado=assinatura.emissor_cn if assinatura else None,
        numero_serie=assinatura.numero_serie if assinatura else None,
        certificado_valido_de=assinatura.valido_de if assinatura else None,
        certificado_valido_ate=assinatura.valido_ate if assinatura else None,
        certificado_valido_no_momento_assinatura=certificado_valido_no_momento,
        politicas_certificado=assinatura.politicas_certificado if assinatura else (),
        assinado_em=assinado_em,
        qualificada_icp_brasil=bool(assinatura and assinatura.qualificada_icp_brasil),
        sha256=registro.sha256,
        registrado_corvia_em=registro.criado_em,
        metodo_codigo=registro.metodo,
        metodo_nome=info.nome if info else registro.metodo,
        metodo_familia=info.familia if info else "desconhecida",
        fluxo_assinatura=fluxo,
        fluxo_assinatura_descricao=fluxo_descricao,
    )
