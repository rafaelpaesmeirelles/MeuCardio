"""Canonical topic cohesion for CorVIA's "Tudo com Tudo".

The rule is intentionally conservative: a relationship may be omitted when
metadata is insufficient, but it must never be invented merely because two
texts share a loose keyword. Existing content fronts remain joined by their
structured `theme`/`tema` field. Drugs, which have no theme column, may enter a
clinical topic only when their already-reviewed structured indications contain
an explicit phrase for that topic.
"""
from __future__ import annotations

import re
import unicodedata
from collections.abc import Iterable
from dataclasses import dataclass


# A broad clinical word is useful for search, but it is not evidence that two
# items discuss the same clinical decision. These tokens are excluded from the
# contextual relation score altogether. A shared word such as "pressão",
# "risco" or "diagnóstico" can therefore never create a relation by itself.
GENERIC_RELATION_TOKENS = frozenset({
    "cardiologia", "cardiovascular", "cardiaco", "cardiaca", "doenca", "sindrome",
    "manejo", "tratamento", "terapia", "avaliacao", "diagnostico", "risco", "estudo",
    "evidencia", "diretriz", "clinico", "clinica", "paciente", "adulto", "adultos",
    "crianca", "criancas", "adolescente", "agudo", "aguda", "cronico", "cronica",
    "grave", "graves", "arterial", "arteriais", "atrial", "atriais", "ventricular",
    "ventriculares", "atleta", "atletas", "esporte", "esportes", "exercicio",
    "exercicios", "cardiomiopatia", "cardiomiopatias", "pressao", "pressoes",
    "frequencia", "frequencias", "insuficiencia", "insuficiencias", "prevencao",
    "prevencoes", "dor", "dores", "imagem", "imagens", "controle", "controles",
    "conduta", "condutas", "protocolo", "protocolos", "seguimento", "seguimentos",
    "monitorizacao", "monitorizacoes", "prognostico", "prognosticos", "recomendacao",
    "recomendacoes", "abordagem", "abordagens", "indicacao", "indicacoes", "associacao",
    "associacoes", "seguranca", "eficacia", "primaria", "primarias", "secundaria",
    "secundarias", "orientacao", "orientacoes", "cuidado", "cuidados", "reabilitacao",
    "para", "pela", "pelo", "pelos", "pelas", "com", "sem", "entre", "versus",
    "apos", "antes", "durante", "como", "quando", "qual", "quais", "uma", "umas",
    "uns", "sobre", "este", "esta", "esse", "essa", "dos", "das", "nas", "nos",
})

# One discriminative title/slug token is enough (3 points); a structured study
# tag is a stronger signal (5 points). Generic tokens above are worth zero and
# never enter the explanation.
CONTEXT_TITLE_TOKEN_WEIGHT = 3
CONTEXT_TAG_TOKEN_WEIGHT = 5
CONTEXT_MIN_RELEVANCE_SCORE = 3

# Two-character terms are normally unsafe after case folding. FA is retained
# as a closed, clinically specific acronym; arbitrary short tokens remain out.
_DISCRIMINATIVE_SHORT_TOKENS = frozenset({"fa"})


def _is_generic_relation_token(token: str) -> bool:
    """Recognize common Portuguese plural forms without broad stemming."""
    variants = {token}
    if token.endswith("oes") and len(token) > 4:
        variants.add(f"{token[:-3]}ao")
    if token.endswith("ais") and len(token) > 4:
        variants.add(f"{token[:-3]}al")
    if token.endswith("eis") and len(token) > 4:
        variants.add(f"{token[:-3]}el")
    if token.endswith("zes") and len(token) > 4:
        variants.add(token[:-2])
    if token.endswith("ns") and len(token) > 3:
        variants.add(f"{token[:-2]}m")
    if token.endswith("s") and len(token) > 3:
        variants.add(token[:-1])
    return not variants.isdisjoint(GENERIC_RELATION_TOKENS)


@dataclass(frozen=True)
class ContextualRelevance:
    """Deterministic, inspectable score for one contextual candidate."""

    score: int
    title_or_slug_terms: tuple[str, ...]
    tag_terms: tuple[str, ...]

    @property
    def accepted(self) -> bool:
        return self.score >= CONTEXT_MIN_RELEVANCE_SCORE

    def reasons(self) -> list[dict[str, object]]:
        tag_terms = set(self.tag_terms)
        reasons: list[dict[str, object]] = []
        for term in sorted(set(self.title_or_slug_terms) | tag_terms):
            source = "structured_tag" if term in tag_terms else "title_or_slug"
            reasons.append({
                "source": source,
                "term": term,
                "weight": (
                    CONTEXT_TAG_TOKEN_WEIGHT
                    if source == "structured_tag"
                    else CONTEXT_TITLE_TOKEN_WEIGHT
                ),
            })
        return reasons

# Known historical labels found in the versioned corpus. These aliases repair
# connectivity without rewriting or silently changing the scientific source.
THEME_ALIASES: dict[str, str] = {
    "Doença arterial coronariana": "Doença coronariana",
    "Choque cardiogênico": "Terapia intensiva",
    "avc": "Terapia intensiva",
    "avc_agudo": "Terapia intensiva",
    "arritmia": "Arritmias",
    "Cardiogenética": "Cardiomiopatias",
    "Cardiologia do esporte": "Cardiologia do Esporte e do Exercício",
    "Cardiomiopatias hereditárias": "Cardiomiopatias",
    "Cardiorrenal": "Insuficiência cardíaca",
    "cirurgia-cardiaca": "Perioperatório",
    "cuidados-intensivos": "Terapia intensiva",
    "dislipidemia": "Prevenção e lipídios",
    "doenca-coronariana": "Doença coronariana",
    "doenca_coronariana": "Doença coronariana",
    "doenca-renal": "Geral",
    "fibrilacao-atrial": "Fibrilação atrial",
    "Gestação e cardiopatia": "Gravidez",
    "hipertensao": "Hipertensão",
    "Imagem cardiovascular": "Geral",
    "insuficiencia-cardiaca": "Insuficiência cardíaca",
    "insuficiencia_cardiaca": "Insuficiência cardíaca",
    "parada-cardiorrespiratoria": "Terapia intensiva",
    "parada_cardiorrespiratoria": "Terapia intensiva",
    "Populações especiais": "Geral",
    "Perioperatório cardiovascular": "Perioperatório",
    "prevencao": "Prevenção e lipídios",
    "sindrome-coronariana-aguda": "Doença coronariana",
    "sindrome_coronariana_aguda": "Doença coronariana",
    "Métodos gráficos e funcionais": "Geral",
    "valvopatia": "Valvopatias",
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
    return " ".join(re.sub(r"[^a-z0-9]+", " ", normalized).split())


def relevance_tokens(value: object) -> set[str]:
    """Return only terms that may justify a clinical contextual relation."""
    if isinstance(value, (list, tuple, set, frozenset)):
        text = " ".join(str(item) for item in value if item)
    else:
        text = str(value or "")
    return {
        token
        for token in normalize_text(text).split()
        if (
            (len(token) >= 3 or token in _DISCRIMINATIVE_SHORT_TOKENS)
            and not token.isdigit()
            and not _is_generic_relation_token(token)
        )
    }


def score_contextual_relevance(
    origin_terms: set[str],
    *,
    title_or_slug: object,
    tags: object = None,
) -> ContextualRelevance:
    """Score overlap using the strongest structured source for each term.

    Terms present in both title and tags count once, at the structured-tag
    weight. This prevents duplicate metadata from inflating relevance.
    """
    title_overlap = origin_terms & relevance_tokens(title_or_slug)
    tag_overlap = origin_terms & relevance_tokens(tags)
    score = sum(
        CONTEXT_TAG_TOKEN_WEIGHT if term in tag_overlap else CONTEXT_TITLE_TOKEN_WEIGHT
        for term in title_overlap | tag_overlap
    )
    return ContextualRelevance(
        score=score,
        title_or_slug_terms=tuple(sorted(title_overlap)),
        tag_terms=tuple(sorted(tag_overlap)),
    )


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
