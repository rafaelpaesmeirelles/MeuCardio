"""Invariantes editoriais compartilhados pelos carregadores científicos.

O manifesto pode retirar um item de circulação, mas nunca autorizar sua
publicação. A promoção continua sendo uma decisão editorial explícita; assim,
uma carga automatizada não transforma conteúdo novo em conteúdo público.
"""

from __future__ import annotations

from typing import Any


REVIEWED_STATUS = "revisado"
PROVENANCE_LABEL = "Proveniência de produção: "


def source_review_note(source: dict[str, Any]) -> str | None:
    """Normaliza os dois nomes legados da nota sem apagar nenhum deles."""
    parts: list[str] = []
    for field in ("revisao", "review_note"):
        value = source.get(field)
        if isinstance(value, str) and value.strip() and value.strip() not in parts:
            parts.append(value.strip())
    return "\n\n".join(parts) or None


def production_provenance(source: dict[str, Any]) -> str | None:
    """Devolve a proveniência versionada apenas quando ela é texto útil."""
    value = source.get("fonte_producao")
    if not isinstance(value, str):
        return None
    return value.strip() or None


def _split_combined_review_note(value: Any) -> tuple[str | None, str | None]:
    if not isinstance(value, str) or not value.strip():
        return None, None
    normalized = value.strip()
    marker = f"\n\n{PROVENANCE_LABEL}"
    if marker in normalized:
        note, provenance = normalized.rsplit(marker, 1)
        return note.strip() or None, provenance.strip() or None
    if normalized.startswith(PROVENANCE_LABEL):
        return None, normalized.removeprefix(PROVENANCE_LABEL).strip() or None
    return normalized, None


def combined_review_note(
    source: dict[str, Any], *, existing: str | None = None
) -> str | None:
    """Atualiza nota/proveniência separadamente em modelos de campo único."""
    previous_note, previous_provenance = _split_combined_review_note(existing)
    note = source_review_note(source) or previous_note
    provenance = production_provenance(source) or previous_provenance

    parts = [note] if note is not None else []
    if provenance is not None:
        parts.append(f"{PROVENANCE_LABEL}{provenance}")
    return "\n\n".join(parts) or None


def source_references(source: dict[str, Any], *, primary: str) -> Any:
    """Lê a chave nativa sem perder o alias usado por outra frente."""
    if primary in source:
        return source[primary]
    alias = "source_refs" if primary == "fontes" else "fontes"
    return source.get(alias)


def enforce_safe_publication(record: Any, source: dict[str, Any], *, is_new: bool) -> None:
    """Aplica somente transições de publicação conservadoras.

    - registro novo nunca é publicado pela carga, mesmo com ``published:true``;
    - ``published:false`` é uma quarentena explícita e precisa chegar ao banco;
    - conteúdo que deixou de estar revisado sai do ar imediatamente;
    - nos demais casos o estado já aprovado no banco é preservado.
    """
    if (
        is_new
        or source.get("published") is False
        or getattr(record, "review_status", None) != REVIEWED_STATUS
    ):
        record.published = False
