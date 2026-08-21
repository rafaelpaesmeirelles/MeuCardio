"""Validação pública e download seguro do PDF clínico efetivamente emitido.

O QR/código público é uma capability não enumerável derivada de HMAC. Códigos
novos usam 128 bits (32 hex) e podem liberar o download do PDF original
assinado; os códigos legados de 64 bits (16 hex) continuam válidos para
consulta de autenticidade, mas NÃO liberam o arquivo clínico.

Formato: R<id>-<MAC> para receituário e D<id>-<MAC> para documento clínico.
O MAC inclui tipo, referência e emissor e usa segredo de servidor, portanto não
pode ser fabricado conhecendo apenas um id sequencial.
"""
from __future__ import annotations

import hashlib
import hmac
import re
from dataclasses import dataclass
from datetime import datetime

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
_MAC_HEX_ATUAL = 32
_CODIGO_RE = re.compile(r"^([RD])(\d+)-([0-9A-F]{16}|[0-9A-F]{32})$")


def _mac_completo(tipo: str, referencia_id: int, criado_por: int) -> str:
    segredo_base = settings.storage_encryption_key or settings.jwt_secret
    segredo = segredo_base.encode("utf-8")
    payload = f"corvia-documento-v1:{tipo}:{referencia_id}:{criado_por}".encode("utf-8")
    return hmac.new(segredo, payload, hashlib.sha256).hexdigest().upper()


def _mac(tipo: str, referencia_id: int, criado_por: int, *, tamanho: int = _MAC_HEX_ATUAL) -> str:
    return _mac_completo(tipo, referencia_id, criado_por)[:tamanho]


def normalizar_codigo(codigo: str) -> str:
    return (codigo or "").strip().upper().replace(" ", "")


def codigo_documento(*, tipo: str, referencia_id: int, criado_por: int) -> str:
    """Gera o código forte atual. Códigos legados continuam aceitos em localizar()."""
    prefixo = _PREFIXOS.get(tipo)
    if prefixo is None:
        raise ValueError(f"Tipo de documento não suportado para validação pública: {tipo}")
    return f"{prefixo}{referencia_id}-{_mac(tipo, referencia_id, criado_por)}"


def url_documento(*, tipo: str, referencia_id: int, criado_por: int) -> str:
    codigo = codigo_documento(tipo=tipo, referencia_id=referencia_id, criado_por=criado_por)
    return f"{settings.public_url.rstrip('/')}/validar/{codigo}"


def codigo_permite_download(codigo: str) -> bool:
    """Só capability de 128 bits libera o PDF; QR legado permanece validação-only."""
    match = _CODIGO_RE.fullmatch(normalizar_codigo(codigo))
    return bool(match and len(match.group(3)) == _MAC_HEX_ATUAL)


def localizar(db: Session, codigo: str) -> DocumentoEmitido | None:
    normalizado = normalizar_codigo(codigo)
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
    # Compatibilidade: valida o prefixo do HMAC com o mesmo tamanho do código
    # recebido. Novo = 32 hex; legado = 16 hex.
    esperado = _mac(tipo, referencia_id, registro.criado_por, tamanho=len(mac_recebido))
    if not hmac.compare_digest(esperado, mac_recebido):
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
        certificado_valido_no_momento = bool(
            assinatura.valido_de <= assinado_em <= assinatura.valido_ate
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
