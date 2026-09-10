"""Resolve explicit local Markdown links without inferring clinical meaning."""
from __future__ import annotations

import re
from urllib.parse import unquote

from app.services.clinical_link_availability import (
    unavailable_clinical_link_reason, unavailable_clinical_link_label,
)


_SCHEME = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")
_SLUG = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9_-]*\Z")


# Exact entity/study identities documented with PMID/DOI and approved catalog
# membership in docs/tct-missing-link-destination-review-20260910.json.
# This is a navigation mapping, not permission to publish historical documents.
_TYPED_LIBRARY_ALIASES = {
    'exposicao-cronica-a-arsenico-inorganico-e-doenca-cardiovascular': (
        'doenca',
        'cardiotoxicidade-cronica-por-arsenico',
        '/doencas/cardiotoxicidade-cronica-por-arsenico',
    ),
    'intoxicacao-cronica-por-chumbo-saturnismo-e-risco-cardiovascular': (
        'doenca',
        'saturnismo-cardiovascular',
        '/doencas/saturnismo-cardiovascular',
    ),
    'policondrite-recidivante-e-acometimento-cardiovascular-aortite-insuficiencia-valvar-e-aneurisma': (
        'doenca',
        'policondrite-recidivante-cardiovascular',
        '/doencas/policondrite-recidivante-cardiovascular',
    ),
    'pseudoxantoma-elastico-acometimento-cardiovascular-calcificacao-arterial-e-rastreio-estruturado': (
        'doenca',
        'pseudoxantoma-elastico',
        '/doencas/pseudoxantoma-elastico',
    ),
    'quartet-combinacao-quadrupla-em-dose-baixa-como-tratamento-inicial-da-hipertensao': (
        'estudo',
        'quartet-quadripill-de-quarto-de-dose-versus-monoterapia-na-has',
        '/estudos/quartet-quadripill-de-quarto-de-dose-versus-monoterapia-na-has',
    ),
    'sifilis-cardiovascular-terciaria-aortite-aneurisma-e-estenose-ostial': (
        'doenca',
        'sifilis-cardiovascular-terciaria',
        '/doencas/sifilis-cardiovascular-terciaria',
    ),
    'terapia-genica-doenca-de-danon-rp-a501-aav9-lamp2b-fase-1': (
        'estudo',
        'terapia-genica-aav9-lamp2b-na-doenca-de-danon-fase-1',
        '/estudos/terapia-genica-aav9-lamp2b-na-doenca-de-danon-fase-1',
    ),
}


def _declared_markdown_target(
    destination: str,
) -> tuple[tuple[str, ...], str] | None:
    """Return allowed entity types and exact slug for a declared link.

    This only identifies a reference. The caller must resolve published
    entities and register target -> document as ``mentioned_in``. It must
    never derive indication, monitoring, or other strong clinical relations.
    """
    path = unquote(destination).split("#", 1)[0].split("?", 1)[0].strip()
    if _SCHEME.match(path) or path.startswith("//"):
        return None
    for prefix, entity_type in (("/calculadoras/", "calculadora"),
                                ("/doencas/", "doenca"), ("/estudos/", "estudo")):
        if path.startswith(prefix):
            slug = path.removeprefix(prefix).rstrip("/")
            return ((entity_type,), slug) if _SLUG.fullmatch(slug) else None
    if path.startswith("/biblioteca/"):
        slug = path.removeprefix("/biblioteca/").strip("/")
        return (("documento", "fluxograma"), slug) if slug else None
    if path.casefold().endswith(".md"):
        slug = path.rsplit("/", 1)[-1][:-3]
        return (("documento", "fluxograma"), slug) if slug else None
    return None


def parse_clinical_markdown_target(destination: str) -> tuple[tuple[str, ...], str] | None:
    """Shared typed reference for graph and audit; unavailable links have no edge."""
    if unavailable_clinical_link_reason(destination):
        return None
    reference = _declared_markdown_target(destination)
    if reference and reference[0] == ("documento", "fluxograma"):
        alias = _TYPED_LIBRARY_ALIASES.get(reference[1])
        if alias:
            return ((alias[0],), alias[1])
    return reference


def resolve_clinical_markdown_destination(destination: str) -> str:
    """Resolve only proven aliases and existing relative Markdown convention."""
    if unavailable_clinical_link_reason(destination):
        return destination  # The renderer below removes its href explicitly.
    reference = _declared_markdown_target(destination)
    if not reference or reference[0] != ("documento", "fluxograma"):
        return destination
    alias = _TYPED_LIBRARY_ALIASES.get(reference[1])
    suffix = re.search(r"[?#].*$", destination)
    suffix_text = suffix.group(0) if suffix else ""
    if alias:
        return alias[2] + suffix_text
    if not destination.startswith("/") and unquote(destination).split("#", 1)[0].split("?", 1)[0].casefold().endswith(".md"):
        return "/biblioteca/" + reference[1] + suffix_text
    return destination


_LINK = re.compile(r"(?<!!)\[([^\]]+)\]\(([^()\s]+)\)")
_CODE = re.compile(r"(```.*?```|~~~.*?~~~|`[^`\n]*`)", re.DOTALL)


def rewrite_clinical_markdown_links(body: str) -> str:
    """Render live canonical URLs or explicit unavailability without editing sources."""
    def replace(match):
        label, destination = match.groups()
        unavailable = unavailable_clinical_link_label(label, destination)
        if unavailable is not None:
            return unavailable
        target = resolve_clinical_markdown_destination(destination)
        return f"[{label}]({target})"
    return "".join(part if index % 2 else _LINK.sub(replace, part)
                   for index, part in enumerate(_CODE.split(body)))
