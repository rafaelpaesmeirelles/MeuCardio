"""Resolve explicit local Markdown links without inferring clinical meaning."""
from __future__ import annotations

import re
from urllib.parse import unquote


_SCHEME = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")
_SLUG = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9_-]*\Z")


def parse_clinical_markdown_target(
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
    if path.startswith("/calculadoras/"):
        slug = path.removeprefix("/calculadoras/").rstrip("/")
        return (("calculadora",), slug) if _SLUG.fullmatch(slug) else None
    if path.startswith("/biblioteca/"):
        slug = path.removeprefix("/biblioteca/").strip("/")
        return (("documento", "fluxograma"), slug) if slug else None
    if path.casefold().endswith(".md"):
        slug = path.rsplit("/", 1)[-1][:-3]
        return (("documento", "fluxograma"), slug) if slug else None
    return None
