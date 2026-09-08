"""Relações transversais curadas, sem inferência lexical ou temática."""
from __future__ import annotations

import json
from pathlib import Path

from app.services.knowledge_relation_policy import validar_relacao_clinica


def load_transversal_relations(path: Path) -> list[dict]:
    records = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(records, list):
        raise ValueError("Manifesto transversal deve ser lista.")
    seen = set()
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("Relação transversal deve ser objeto.")
        for field in (
            "source_type", "source_slug", "target_type", "target_slug",
            "relation_type", "evidence_source", "review_note",
        ):
            if not isinstance(record.get(field), str) or not record[field].strip():
                raise ValueError(f"Campo transversal inválido: {field}")
        if record.get("review_status") != "revisado" or record.get("confidence") != "explicit":
            raise ValueError("Manifesto transversal exige revisão explícita.")
        if record.get("provenance_type") != "editorial":
            raise ValueError("Manifesto transversal exige proveniência editorial.")
        key = tuple(record[field] for field in (
            "source_type", "source_slug", "relation_type", "target_type", "target_slug",
        ))
        if key in seen or key[:2] == key[3:]:
            raise ValueError(f"Relação transversal duplicada ou reflexiva: {key}")
        seen.add(key)
        validar_relacao_clinica(**{field: record[field] for field in (
            "source_type", "target_type", "relation_type", "relevance_score",
            "provenance_type", "confidence", "review_status", "evidence_source",
        )})
    return records


def resolve_transversal_relations(records, entities, published):
    """Resolve contra a publicação desta rodada; nós antigos não bastam."""
    resolved, unresolved = [], []
    for record in records:
        source = (record["source_type"], record["source_slug"])
        target = (record["target_type"], record["target_slug"])
        reason = (
            "origem_nao_publicada" if source not in published else
            "destino_nao_publicado" if target not in published else
            "no_ativo_ausente" if source not in entities or target not in entities else None
        )
        if reason:
            unresolved.append({**record, "motivo": reason})
        else:
            resolved.append((record, entities[source], entities[target]))
    return resolved, unresolved
