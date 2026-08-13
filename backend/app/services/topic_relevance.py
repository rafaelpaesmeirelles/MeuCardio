"""Canonical topic cohesion for CorVIA's "Tudo com Tudo".

The rule is intentionally conservative: a relationship may be omitted when
metadata is insufficient, but it must never be invented merely because two
texts share a loose keyword. Existing content fronts remain joined by their
structured `theme`/`tema` field. Drugs, which have no theme column, may enter a
clinical topic only when their already-reviewed structured indications contain
an explicit phrase for that topic.
"""
from __future__ import annotations

import unicodedata
from collections.abc import Iterable

# Known historical labels found in the versioned corpus. These aliases repair
# connectivity without rewriting or silently changing the scientific source.
THEME_ALIASES: dict[str, str] = {
    "Doença arterial coronariana": "Doença coronariana",
    "Choque cardiogênico": "Terapia intensiva",
}

# Only topics with an indication phrase sufficiently specific to be used as a
# structural drug relation are listed. Absence from this map means "do not
# infer a drug relation". This is stricter than a search engine by design.
DRUG_TOPIC_PHRASES: dict[str, tuple[str, ...]] = {
    "Insuficiência cardíaca": (
        "insuficiencia cardiaca", "icfer", "icfep", "insuficiencia ventricular esquerda",
    ),
    "Hipertensão": (
        "hipertensao arterial", "hipertensao resistente", "emergencia hipertensiva",
    ),
    "Hipertensão pulmonar": (
        "hipertensao arterial pulmonar", "hipertensao pulmonar",
    ),
    "Fibrilação atrial": (
        "fibrilacao atrial", "flutter atrial",
    ),
    "Tromboembolismo": (
        "tromboembolismo venoso", "trombose venosa profunda", "embolia pulmonar",
        "profilaxia de tvp", "profilaxia de tep",
    ),
    "Doença coronariana": (
        "sindrome coronariana", "doenca coronariana", "angina pectoris", "angina estavel",
        "angina instavel", "infarto agudo do miocardio", "infarto do miocardio",
    ),
    "Prevenção e lipídios": (
        "hipercolesterolemia", "dislipidemia", "reducao do colesterol", "colesterol ldl",
        "prevencao cardiovascular",
    ),
    "Arritmias": (
        "taquicardia ventricular", "taquicardia supraventricular", "arritmia ventricular",
        "arritmias ventriculares", "bradicardia sintomatica",
    ),
    "Pericárdio": (
        "pericardite", "derrame pericardico",
    ),
    "Aorta e doença arterial periférica": (
        "doenca arterial periferica", "doenca arterial obstrutiva periferica",
    ),
}

SUPPORTED_DRUG_TOPICS = frozenset(DRUG_TOPIC_PHRASES)


def normalize_text(value: str | None) -> str:
    normalized = unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode().lower()
    return " ".join(normalized.replace("/", " ").replace("-", " ").split())


def canonical_theme(theme: str | None) -> str:
    value = (theme or "").strip()
    return THEME_ALIASES.get(value, value)


def theme_variants(theme: str | None) -> tuple[str, ...]:
    canonical = canonical_theme(theme)
    if not canonical:
        return ()
    variants = [canonical]
    variants.extend(alias for alias, target in THEME_ALIASES.items() if target == canonical)
    return tuple(dict.fromkeys(variants))


def indication_text(indications: Iterable[str] | None) -> str:
    return normalize_text(" | ".join(str(item) for item in (indications or []) if item))


def drug_matches_theme(drug, theme: str | None) -> bool:
    canonical = canonical_theme(theme)
    if canonical == "Farmacologia":
        return True
    phrases = DRUG_TOPIC_PHRASES.get(canonical)
    if not phrases:
        return False
    haystack = indication_text(getattr(drug, "indications", None))
    if not haystack:
        return False
    return any(normalize_text(phrase) in haystack for phrase in phrases)
