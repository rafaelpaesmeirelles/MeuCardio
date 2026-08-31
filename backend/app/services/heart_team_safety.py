"""Deterministic clinical and privacy gates for Heart Team outputs."""

from __future__ import annotations

import re
from copy import deepcopy

from app.services.heart_team_evidence import _required_overlap, exact_facts_supported, validate_claim_support
from app.services.ia.clinical_file_sanitizer import contains_identifier

PII_PATTERNS = {
    "cpf": re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b"),
    "telefone": re.compile(r"(?<!\d)(?:\+?55\s*)?\(?\d{2}\)?\s*9?\d{4}[-\s]?\d{4}(?!\d)"),
    "email": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
    "cep": re.compile(r"\b\d{5}-?\d{3}\b"),
    "cns": re.compile(r"\b\d{15}\b"),
    "rg": re.compile(r"\b(?:rg|registro\s+geral)\s*[:#-]?\s*[0-9.x-]{5,20}\b", re.I),
    "nome": re.compile(r"\b(?:nome|paciente|patient)\s*[:#-]?\s+[A-ZÀ-ÖØ-Ý][A-Za-zÀ-ÖØ-öø-ÿ'-]+(?:\s+(?:[A-ZÀ-ÖØ-Ý][A-Za-zÀ-ÖØ-öø-ÿ'-]+|da|de|do|das|dos|e)){1,6}\b", re.I),
    "nascimento": re.compile(r"\b(?:data\s+de\s+nascimento|nasc(?:imento)?\.?|dob)\s*[:#-]?\s*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", re.I),
    "endereco": re.compile(r"\b(?:endere[cç]o|logradouro|rua|avenida)\s*[:#-]\s*[^,;\n]{4,120}", re.I),
    "prontuario": re.compile(r"\b(?:prontu[aá]rio|mrn|medical\s+record)\s*[:#-]?\s*[A-Z0-9-]{4,20}\b", re.I),
}

CLINICAL_FIELDS = (
    "summary", "alerts", "differential_diagnoses", "additional_tests",
    "therapeutic_options", "safety",
)


def detected_identifiers(value) -> list[str]:
    text = str(value or "")
    findings = [name for name, pattern in PII_PATTERNS.items() if pattern.search(text)]
    # Canonical detector is shared with the attachment sanitizer and includes
    # additional conservative patterns (uppercase names, labeled identifiers).
    if contains_identifier(text) and not findings:
        findings.append("identificador_clinico")
    return findings


def validate_deidentified(snapshot: dict) -> list[str]:
    findings: set[str] = set()
    stack = [snapshot]
    while stack:
        current = stack.pop()
        if isinstance(current, dict):
            stack.extend(current.values())
        elif isinstance(current, list):
            stack.extend(current)
        elif isinstance(current, str):
            findings.update(detected_identifiers(current))
    return sorted(findings)


def emergency_screen(snapshot: dict) -> dict:
    text = str(snapshot).lower()
    markers = {
        "dor torácica em curso": ("dor torac", "dor no peito"),
        "síncope/instabilidade": ("sincope", "síncope", "instavel", "instável"),
        "choque": ("choque", "hipotens"),
        "dispneia grave": ("dispneia grave", "saturacao baixa", "saturação baixa"),
    }
    hits = [label for label, words in markers.items() if any(word in text for word in words)]
    return {
        "level": "emergency_possible" if hits else "not_identified",
        "signals": hits,
        "notice": "Possível emergência: aplicar protocolo assistencial local imediatamente." if hits else "Triagem textual não exclui emergência.",
    }


def normalize_opinion(raw: dict, registry: dict[str, dict]) -> tuple[dict, list[str]]:
    output = deepcopy(raw if isinstance(raw, dict) else {})
    blocks: list[str] = []
    claims = output.get("claims") if isinstance(output.get("claims"), list) else []
    normalized_claims = []
    for claim in claims:
        if not isinstance(claim, dict):
            blocks.append("claim inválida")
            continue
        statement = str(claim.get("statement") or "").strip()
        ids = [str(value) for value in (claim.get("source_ids") or [])]
        ok, reason = validate_claim_support(statement, ids, registry)
        if not ok:
            blocks.append(f"{statement[:120]}: {reason}")
            normalized_claims.append({**claim, "statement": "evidência insuficiente", "source_ids": [], "validation": "blocked"})
        else:
            normalized_claims.append({**claim, "statement": statement, "source_ids": ids, "validation": "verified"})
    output["claims"] = normalized_claims

    # Narrative clinical assertions also require a supported claim.  If none
    # survived, fail closed instead of letting an uncited paragraph through.
    verified = [c for c in normalized_claims if c.get("validation") == "verified"]
    verified_statements = [str(c.get("statement") or "") for c in verified]

    def supported_narrative(value) -> bool:
        if isinstance(value, dict):
            statement = str(value.get("statement") or value.get("text") or value.get("recommendation") or "")
            ids = value.get("source_ids") or []
            return bool(statement and validate_claim_support(statement, ids, registry)[0])
        statement = str(value or "").strip()
        return bool(statement and any(_required_overlap(statement, claim) and exact_facts_supported(statement, claim)[0] for claim in verified_statements))

    for field in CLINICAL_FIELDS:
        value = output.get(field)
        if value in (None, "", [], {}):
            continue
        if isinstance(value, list):
            sanitized = [item if supported_narrative(item) else "evidência insuficiente" for item in value]
            if sanitized != value: blocks.append(f"{field}: narrativa sem claim verificada")
            output[field] = sanitized
        elif not supported_narrative(value):
            output[field] = "evidência insuficiente"
            blocks.append(f"{field}: narrativa sem claim verificada")
    if not verified:
        blocks.append("nenhuma afirmação clínica verificável")
    output["safety_blocks"] = sorted(set(blocks))
    output["confidence"] = output.get("confidence") if verified and not blocks else "insufficient"
    output.setdefault("limitations", ["Apoio por IA; requer validação integral do médico."])
    output.setdefault("human_decisions", ["Diagnóstico, prognóstico, exames, tratamento e comunicação permanecem decisões humanas."])
    return output, output["safety_blocks"]


def mandatory_opinion_usable(agent_key: str, content: dict) -> bool:
    if agent_key not in {"evidence", "red_team", "coordinator"}:
        return True
    summary = content.get("summary") or content.get("final_consensus")
    return bool(
        summary and summary != "evidência insuficiente"
        and content.get("confidence") not in {None, "insufficient"}
        and not content.get("safety_blocks")
        and content.get("source_ids")
    )


def deterministic_disagreements(opinions: list[dict]) -> list[dict]:
    positions: dict[str, list[dict]] = {}
    for opinion in opinions:
        for claim in opinion.get("content", {}).get("claims", []):
            key = re.sub(r"\W+", " ", str(claim.get("statement") or "").lower()).strip()
            if key:
                positions.setdefault(key, []).append({"agent": opinion.get("agent_key"), "position": claim.get("position", "uncertain"), "statement": claim.get("statement")})
    result = []
    for key, items in positions.items():
        explicit = {item["position"] for item in items}
        if "support" in explicit and "oppose" in explicit:
            result.append({"topic": key, "positions": items})
    return result
