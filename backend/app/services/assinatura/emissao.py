"""Ponto único de "assinar e persistir" um documento clínico (Tarefa 4).

Os quatro pontos de emissão (`api/receituario.py`, `api/documents.py` × 2,
`api/documentos_publicos.py` × 2) compartilham a mesma necessidade: validar
o método escolhido, pedir ao provedor (`assinatura/provedor.py`) para
assinar (ou não) o PDF já renderizado, e gravar o resultado — cifrado no
cofre, referenciado por `DocumentoEmitido` — para que o link público reabra
exatamente os mesmos bytes depois, em vez de regerar.

`tipo` segue o mesmo vocabulário que `DocumentShareLink` já usa (ver
`models/compartilhamento.py`): "prescription_document" para receita,
"generated_document" para atestado/laudo.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.assinatura import DocumentoEmitido
from app.services import cofre
from app.services.assinatura import catalogo
from app.services.assinatura.provedor import ProvedorAssinatura, obter_provedor

TIPO_RECEITA = "prescription_document"
TIPO_DOCUMENTO = "generated_document"


class MetodoInvalido(ValueError):
    """Código de método que não existe no catálogo — vira 422, não 500."""


def _raiz() -> Path:
    return Path(settings.documentos_dir)


def preparar(metodo: str) -> tuple[ProvedorAssinatura, catalogo.ProvedorInfo]:
    """Resolve o provedor e a info do catálogo, ou recusa com `MetodoInvalido`
    — quem chama decide se isso é 422 (parâmetro errado) ou outra coisa."""
    info = catalogo.info(metodo)
    if info is None:
        raise MetodoInvalido(f"Método de assinatura desconhecido: {metodo}")
    return obter_provedor(metodo), info


@dataclass
class Emitido:
    pdf: bytes
    registro: DocumentoEmitido


def assinar_e_persistir(
    db: Session, *, tipo: str, referencia_id: int, metodo: str,
    provedor: ProvedorAssinatura, info: catalogo.ProvedorInfo,
    pdf_visual: bytes, medico: dict, criado_por: int, data_emissao: datetime,
) -> Emitido:
    """Chama `provedor.assinar()` sobre o PDF já renderizado (com a legenda e
    o aviso já corretos para `metodo` — ver `pdf_documento._assinatura_
    rodape`) e persiste o resultado. Só chame depois de confirmar
    `provedor.disponivel()` — esta função não repete a checagem, porque cada
    chamador já monta sua própria lista de `bloqueios` a partir dela."""
    resultado = provedor.assinar(pdf_visual, medico, {"tipo": tipo, "referencia_id": referencia_id})
    if resultado.estado == "indisponivel":
        # Defensivo: não deveria acontecer se o chamador checou disponivel()
        # antes, mas nada aqui pode arriscar persistir um PDF de mentira.
        raise RuntimeError(resultado.motivo or f"{metodo} recusou assinar sem motivo.")

    pdf_final = resultado.pdf if resultado.pdf is not None else pdf_visual
    sha256 = hashlib.sha256(pdf_final).hexdigest()
    nome_arquivo = cofre.guardar(pdf_final, criado_por, raiz=_raiz())

    registro = DocumentoEmitido(
        tipo=tipo, referencia_id=referencia_id, metodo=metodo, nivel=info.nivel,
        arquivo_nome=nome_arquivo, sha256=sha256, bytes_tam=len(pdf_final),
        assinado_em=data_emissao if resultado.estado == "assinado" else None,
        criado_por=criado_por,
    )
    db.add(registro)
    return Emitido(pdf=pdf_final, registro=registro)


def buscar(db: Session, *, tipo: str, referencia_id: int) -> DocumentoEmitido | None:
    return (
        db.query(DocumentoEmitido)
        .filter(DocumentoEmitido.tipo == tipo, DocumentoEmitido.referencia_id == referencia_id)
        .first()
    )


def ler_bytes(registro: DocumentoEmitido) -> bytes:
    return cofre.ler(registro.arquivo_nome, registro.criado_por, raiz=_raiz())


def servir_ou_regerar(db: Session, *, tipo: str, referencia_id: int,
                      regerar: Callable[[], bytes]) -> bytes:
    """Usado pelos pontos de LEITURA (`GET .../pdf`, link público): se o
    documento já foi emitido depois da Tarefa 4, serve os bytes exatos que o
    médico assinou/viu, lendo do cofre. Documento emitido ANTES da migração
    não tem `DocumentoEmitido` — regera como sempre foi feito, via a
    função `regerar` que o chamador já tinha."""
    registro = buscar(db, tipo=tipo, referencia_id=referencia_id)
    if registro is None:
        return regerar()
    return ler_bytes(registro)
