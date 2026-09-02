"""Comando único pós-crédito para fechar as Partes D e E da correção
coordenada de 02/09/2026, quando a conta do provedor de embedding (OpenAI,
`text-embedding-3-small`) voltar a ter crédito — hoje bloqueada
(`insufficient_quota` / `credit_balance_exhausted`, confirmado ao vivo em
produção em 02/09/2026, sem gravar nada parcial).

Faz, nesta ordem:
1. Parte E — reprocessa o backlog de `documents` publicados sem chunk
   (503 no momento da auditoria, concentrados em 30/08/2026).
2. Parte D — indexa as 12 frentes fora de `documents` + calculadoras,
   pela primeira vez (`knowledge_chunks` está vazia até este comando rodar).

`apenas_pendentes=True` nos dois — idempotente, seguro rodar de novo se
faltar crédito no meio (só reprocessa quem ainda não tem chunk).

Rodar:
    python -m app.commands.reindex_rag_completo_20260902
"""
from __future__ import annotations

import json

from app.core.db import SessionLocal
from app.services.rag import indexar_tudo
from app.services.rag_multi import indexar_tudo_multi


def rodar() -> dict:
    with SessionLocal() as db:
        backlog_documentos = indexar_tudo(db, apenas_pendentes=True)
    with SessionLocal() as db:
        demais_frentes = indexar_tudo_multi(db, apenas_pendentes=True)
    return {"documents_backlog": backlog_documentos, "demais_frentes": demais_frentes}


if __name__ == "__main__":
    print(json.dumps(rodar(), ensure_ascii=False, indent=2))
