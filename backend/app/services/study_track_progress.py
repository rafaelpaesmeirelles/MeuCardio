"""Identidade e compatibilidade do progresso das trilhas de estudo.

Historicamente ``study_track_progress.concluidas`` guardava apenas o slug do
conteudo. Isso deixa de ser suficiente quando uma trilha usa, por exemplo, um
documento e uma calculadora com o mesmo slug. O formato atual e composto e
permanece dentro do JSONB existente, portanto nao exige migracao de schema::

    documento:has-bled
    calculadora:has-bled

Slugs legados continuam sendo reconhecidos. Na primeira escrita da trilha eles
sao expandidos para todas as etapas atuais que antes representavam, preservando
o estado que o assinante via antes da correcao sem manter a ambiguidade nas
gravacoes seguintes.
"""

from __future__ import annotations

from collections.abc import Iterable

from app.services.study_slug_aliases import canonical_study_slug


STAGE_TYPES = frozenset({
    "documento",
    "medicamento",
    "estudo",
    "calculadora",
    "checklist",
    "evidencia",
    "caso_clinico",
})


def canonical_stage_slug(item_type: str, item_slug: str) -> str:
    """Canonicaliza apenas os slugs de estudo, cujo alias e versionado."""
    return canonical_study_slug(item_slug) if item_type == "estudo" else item_slug


def stage_identity(item_type: str, item_slug: str) -> str:
    """Identidade estavel de uma etapa, independente da sua ordem editorial."""
    return f"{item_type}:{canonical_stage_slug(item_type, item_slug)}"


def split_stage_identity(value: str) -> tuple[str, str] | None:
    """Le uma identidade composta; slugs legados continuam sem separador."""
    item_type, separator, item_slug = value.partition(":")
    if not separator or item_type not in STAGE_TYPES or not item_slug:
        return None
    return item_type, canonical_stage_slug(item_type, item_slug)


def canonicalize_progress_tokens(values: Iterable[str] | None) -> list[str]:
    """Canonicaliza aliases e remove duplicatas sem descartar tokens legados."""
    canonical: set[str] = set()
    for raw in values or []:
        value = str(raw)
        parsed = split_stage_identity(value)
        if parsed is None:
            # Este era o comportamento historico: como o tipo nao era salvo,
            # aliases de estudo eram canonicalizados pelo slug isolado.
            canonical.add(canonical_study_slug(value))
        else:
            canonical.add(stage_identity(*parsed))
    return sorted(canonical)


def expand_legacy_progress_tokens(
    values: Iterable[str] | None,
    stages: Iterable[dict],
) -> list[str]:
    """Expande slugs legados para identidades das etapas atuais.

    Um slug legado que hoje corresponde a documento e calculadora e expandido
    para ambos, pois era exatamente assim que o estado anterior era exibido.
    Tokens sem correspondencia sao mantidos: se a curadoria retirar e depois
    restaurar uma etapa, o historico nao desaparece silenciosamente.
    """
    current_by_slug: dict[str, set[str]] = {}
    for stage in stages:
        item_type = str(stage.get("item_type") or "")
        item_slug = str(stage.get("item_slug") or "")
        if item_type not in STAGE_TYPES or not item_slug:
            continue
        canonical_slug = canonical_stage_slug(item_type, item_slug)
        current_by_slug.setdefault(canonical_slug, set()).add(
            stage_identity(item_type, canonical_slug)
        )

    expanded: set[str] = set()
    for token in canonicalize_progress_tokens(values):
        if split_stage_identity(token) is not None:
            expanded.add(token)
            continue
        matches = current_by_slug.get(token)
        if matches:
            expanded.update(matches)
        else:
            expanded.add(token)
    return sorted(expanded)


def completed_stage_ids(values: Iterable[str] | None, stages: Iterable[dict]) -> set[str]:
    """Identidades das etapas atuais que estao concluidas."""
    stage_list = list(stages)
    expanded = set(expand_legacy_progress_tokens(values, stage_list))
    return {
        stage_identity(str(stage.get("item_type") or ""), str(stage.get("item_slug") or ""))
        for stage in stage_list
        if stage.get("item_type") in STAGE_TYPES
        and stage.get("item_slug")
        and stage_identity(str(stage["item_type"]), str(stage["item_slug"])) in expanded
    }
