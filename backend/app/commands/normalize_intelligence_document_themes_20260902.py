"""Parte C da correção coordenada de 02/09/2026: normaliza o `theme` dos
documentos do pipeline "corvia-intelligence" que foram publicados antes da
correção do schema (`guideline_clinical_update.ANALYSIS_SCHEMA` passou a
restringir `theme` à taxonomia canônica — ver `canonical_themes.py`).

Escopo: qualquer `documents` publicado cujo `theme` atual não está em
`TEMAS_CANONICOS`. Não hardcoda slug nenhum — reclassifica pelo texto (tema
livre atual + título) usando o mesmo classificador genérico que qualquer
conteúdo futuro no mesmo estado usaria. Hoje isso são os 22 documentos
`corvia-intelligence-*` de 02/09/2026, mas o comando não assume isso.

Rodar:
    python -m app.commands.normalize_intelligence_document_themes_20260902
"""
from __future__ import annotations

import json

from app.core.db import SessionLocal
from app.models.content import Document
from app.services.canonical_themes import TEMAS_CANONICOS, classificar_tema_canonico


def normalizar() -> list[dict]:
    alterados: list[dict] = []
    with SessionLocal() as db:
        candidatos = db.query(Document).filter(
            Document.published.is_(True),
            ~Document.theme.in_(TEMAS_CANONICOS),
        ).all()
        for doc in candidatos:
            tema_anterior = doc.theme
            novo_tema = classificar_tema_canonico(doc.theme, doc.title)
            doc.theme = novo_tema
            alterados.append({
                "slug": doc.slug,
                "tema_anterior": tema_anterior,
                "tema_novo": novo_tema,
            })
        db.commit()
    return alterados


if __name__ == "__main__":
    print(json.dumps(normalizar(), ensure_ascii=False, indent=2))
