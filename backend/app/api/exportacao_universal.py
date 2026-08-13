"""Exportação universal e montagem de PDF do CorVIA.

A API recebe apenas identificadores de objetos canônicos. O texto exportado é
resolvido novamente no servidor a partir do conteúdo publicado; nunca recebe
HTML/prosa clínica do cliente. Isso mantém a mesma barreira editorial da UI.
"""
from __future__ import annotations

import re
import unicodedata
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user
from app.models.audit import AuditLog
from app.services.exportacao_conteudo import TIPOS_EXPORTAVEIS, catalogo, gerar_pdf, resolver_conteudo

router = APIRouter(prefix="/api/exportar", tags=["exportação"])


class ItemExportacao(BaseModel):
    tipo: str = Field(min_length=2, max_length=40)
    slug: str = Field(min_length=1, max_length=255)

    @field_validator("tipo")
    @classmethod
    def tipo_valido(cls, valor: str) -> str:
        valor = valor.strip().lower()
        if valor not in TIPOS_EXPORTAVEIS:
            raise ValueError(f"Tipo não exportável. Use um de: {', '.join(sorted(TIPOS_EXPORTAVEIS))}")
        return valor

    @field_validator("slug")
    @classmethod
    def slug_valido(cls, valor: str) -> str:
        valor = valor.strip()
        if not valor:
            raise ValueError("Identificador vazio.")
        return valor


class PedidoExportacao(BaseModel):
    itens: list[ItemExportacao] = Field(min_length=1, max_length=50)
    incluir_dados_assinante: bool = False
    titulo: str | None = Field(default=None, max_length=180)

    @field_validator("itens")
    @classmethod
    def sem_duplicatas(cls, itens: list[ItemExportacao]) -> list[ItemExportacao]:
        vistos: set[tuple[str, str]] = set()
        saida: list[ItemExportacao] = []
        for item in itens:
            chave = (item.tipo, item.slug)
            if chave in vistos:
                continue
            vistos.add(chave)
            saida.append(item)
        if not saida:
            raise ValueError("Selecione pelo menos um conteúdo.")
        return saida


def _arquivo(nome: str) -> str:
    valor = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode()
    valor = re.sub(r"[^A-Za-z0-9]+", "-", valor).strip("-").lower()[:90]
    return f"{valor or 'conteudo-corvia'}.pdf"


@router.get("/catalogo")
def catalogo_exportavel(
    q: str | None = Query(None, max_length=160),
    tipo: str | None = Query(None, max_length=40),
    slug: str | None = Query(None, max_length=255),
    limite: int = Query(120, ge=1, le=200),
    db: Session = Depends(get_db),
    _=Depends(current_user),
):
    if tipo is not None and tipo not in TIPOS_EXPORTAVEIS:
        raise HTTPException(status_code=422, detail="Tipo de conteúdo não exportável.")
    itens = catalogo(db, q=q, tipo=tipo, slug=slug, limite=limite)
    return {"total": len(itens), "itens": itens, "tipos": sorted(TIPOS_EXPORTAVEIS)}


@router.post("/conteudo")
def exportar_conteudo(
    dados: PedidoExportacao,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    uf = (user.council_state or "").strip().upper() or None
    resolvidos = []
    ausentes = []
    for pedido in dados.itens:
        item = resolver_conteudo(db, pedido.tipo, pedido.slug, uf=uf)
        if item is None:
            ausentes.append({"tipo": pedido.tipo, "slug": pedido.slug})
        else:
            resolvidos.append(item)

    # Fail closed: não gera um arquivo parcial silenciosamente. Se o usuário
    # selecionou 8 itens e um foi despublicado entre a seleção e o clique,
    # precisa saber; omitir esse item sem aviso faria o PDF parecer completo.
    if ausentes:
        raise HTTPException(
            status_code=409,
            detail={
                "erro": "Um ou mais conteúdos deixaram de estar disponíveis para exportação.",
                "itens": [f"{item['tipo']}:{item['slug']}" for item in ausentes],
            },
        )

    try:
        arquivo = gerar_pdf(
            resolvidos,
            user=user,
            incluir_dados_assinante=dados.incluir_dados_assinante,
            titulo=dados.titulo,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    titulo = (dados.titulo or (resolvidos[0].titulo if len(resolvidos) == 1 else "Seleção de conteúdo CorVIA")).strip()
    db.add(AuditLog(
        user_id=user.id,
        action="exportar_conteudo",
        entity="content_export",
        detail={
            "quantidade": len(resolvidos),
            "itens": [{"tipo": item.tipo, "slug": item.slug} for item in resolvidos],
            "incluir_dados_assinante": dados.incluir_dados_assinante,
            "bytes": len(arquivo),
        },
    ))
    db.commit()
    return Response(
        content=arquivo,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{_arquivo(titulo)}"'},
    )
