"""Tarefa 15 — Modo Emergência.

Uma rota só, e ela devolve **tudo de uma vez**: a seleção de protocolos com o
corpo completo de cada documento referenciado, o fluxograma quando existir e os
relacionados. É intencionalmente o oposto do resto da API, que é paginada e
carrega sob demanda.

O motivo é o requisito que define a tarefa: **funcionar sem rede**. Uma tela
que busca o protocolo no momento em que o médico toca no cartão é uma tela que
falha exatamente quando é necessária — a emergência e a queda de conexão
acontecem no mesmo lugar, o corredor do hospital. Com uma resposta única, o
cliente guarda o pacote inteiro e passa a funcionar a partir dele.

O custo é uma resposta grande. É o custo certo a pagar aqui, e só aqui.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user
from app.models.content import Document
from app.models.emergency import EmergencyProtocol

router = APIRouter(prefix="/api/emergencia", tags=["emergência"])


def _documento(d: Document) -> dict:
    return {
        "slug": d.slug,
        "title": d.title,
        "theme": d.theme,
        "kind": d.kind,
        "summary": d.summary,
        "body_md": d.body_md,
        "source_refs": list(d.source_refs or []),
        "source_tier": d.source_tier,
        "review_status": d.review_status,
        # Lacuna declarada viaja junto: numa tela de emergência, saber que um
        # ponto do protocolo está pendente de verificação vale mais do que na
        # leitura tranquila — é onde a decisão é tomada sem tempo de conferir.
        "gaps": list(d.gaps or []),
    }


@router.get("")
def pacote_de_emergencia(db: Session = Depends(get_db), _=Depends(current_user)):
    protocolos = (db.query(EmergencyProtocol)
                    .filter(EmergencyProtocol.published.is_(True))
                    .order_by(EmergencyProtocol.titulo)
                    .all())
    if not protocolos:
        return {"protocolos": [], "documentos": {}}

    precisa = set()
    for p in protocolos:
        precisa.add(p.documento_slug)
        if p.fluxograma_slug:
            precisa.add(p.fluxograma_slug)
        precisa.update(p.relacionados or [])

    docs = (db.query(Document)
              .filter(Document.slug.in_(precisa), Document.published.is_(True))
              .all())

    return {
        "protocolos": [
            {
                "slug": p.slug,
                "titulo": p.titulo,
                "gatilho": p.gatilho,
                "documento_slug": p.documento_slug,
                "fluxograma_slug": p.fluxograma_slug,
                "relacionados": list(p.relacionados or []),
            }
            for p in protocolos
        ],
        "documentos": {d.slug: _documento(d) for d in docs},
    }
