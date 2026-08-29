from __future__ import annotations

"""CorVIA Intelligence: síntese em português + atualização clínica versionada.

A rotina não substitui silenciosamente o corpus. Quando uma publicação nova traz
mudança explícita, o CorVIA cria um *override* prevalente, auditável e reversível
no item clínico afetado. O conteúdo anterior continua preservado para histórico.

Diretrizes são obras protegidas: a saída é uma síntese original em português,
nunca tradução/reprodução integral do documento.
"""

import json
import logging
import re
import threading
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlsplit

import httpx
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.checklist import DischargeChecklist
from app.models.content import Document, DocumentRevision
from app.models.drug import Drug
from app.models.evidence import EvidenceRecord
from app.models.guideline import Guideline, GuidelineLink
from app.models.specialty_guide import SpecialtyDisease, SymptomTriageGuide

log = logging.getLogger("corvia.guideline_clinical_update")

RESPONSES_URL = "https://api.openai.com/v1/responses"
DEFAULT_MODEL = "gpt-5.6"
PROCESS_LIMIT = 20
ANALYSIS_ITEM_TYPE = "analysis"
ANALYSIS_ITEM_ID = 0
SUMMARY_ITEM_TYPE = "intelligence_document"
ORIGIN = "intelligence"

TRUSTED_DOMAINS = (
    "doi.org", "pubmed.ncbi.nlm.nih.gov", "ncbi.nlm.nih.gov", "europepmc.org",
    "escardio.org", "academic.oup.com", "acc.org", "heart.org", "ahajournals.org",
    "portal.cardiol.br", "abccardiol.org", "jacc.org", "nejm.org", "thelancet.com",
    "bmj.com", "nature.com", "hrsonline.org", "hfsa.org", "scai.org", "asecho.org",
    "asnc.org", "j-circ.or.jp", "nice.org.uk", "who.int", "cochranelibrary.com",
)

UPDATEABLE_TYPES = {"document", "evidence", "disease", "drug", "checklist", "triage"}

ANALYSIS_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "title_pt": {"type": "string"},
        "summary_pt": {"type": "string"},
        "theme": {"type": "string"},
        "topics": {"type": "array", "items": {"type": "string"}},
        "entities": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "properties": {
                "type": {"type": "string", "enum": ["doenca", "medicamento", "procedimento", "exame", "outro"]},
                "name": {"type": "string"},
            },
            "required": ["type", "name"],
        }},
        "supersedes": {"type": "array", "items": {"type": "string"}},
        "requires_site_update": {"type": "boolean"},
        "key_changes": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "properties": {
                "category": {"type": "string", "enum": [
                    "definicao", "diagnostico", "tratamento", "fluxograma", "monitorizacao",
                    "seguranca", "prevencao", "procedimento", "outro",
                ]},
                "change_pt": {"type": "string"},
                "previous_pt": {"type": ["string", "null"]},
                "practical_impact_pt": {"type": "string"},
                "explicit_in_source": {"type": "boolean"},
                "source_url": {"type": "string"},
            },
            "required": ["category", "change_pt", "previous_pt", "practical_impact_pt", "explicit_in_source", "source_url"],
        }},
        "limitations": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["title_pt", "summary_pt", "theme", "topics", "entities", "supersedes",
                 "requires_site_update", "key_changes", "limitations"],
}

IMPACT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "impacts": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "properties": {
                "item_type": {"type": "string", "enum": sorted(UPDATEABLE_TYPES)},
                "item_id": {"type": "integer"},
                "target_section": {"type": "string"},
                "change_summary_pt": {"type": "string"},
                "override_pt": {"type": "string"},
                "source_url": {"type": "string"},
                "confidence": {"type": "string", "enum": ["alta", "moderada", "baixa"]},
                "explicit_support": {"type": "boolean"},
                "supersedes_existing_guidance": {"type": "boolean"},
            },
            "required": ["item_type", "item_id", "target_section", "change_summary_pt", "override_pt",
                         "source_url", "confidence", "explicit_support", "supersedes_existing_guidance"],
        }},
    },
    "required": ["impacts"],
}

VERIFY_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "verifications": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "properties": {
                "item_type": {"type": "string", "enum": sorted(UPDATEABLE_TYPES)},
                "item_id": {"type": "integer"},
                "verified": {"type": "boolean"},
                "reason_pt": {"type": "string"},
            },
            "required": ["item_type", "item_id", "verified", "reason_pt"],
        }},
    },
    "required": ["verifications"],
}

_PROCESS_LOCK = threading.Lock()


def _model() -> str:
    return (settings.ai_cardiovascular_exam_model or "").strip() or DEFAULT_MODEL


def _domains_for(guideline: Guideline) -> list[str]:
    domains = list(TRUSTED_DOMAINS)
    if guideline.url:
        host = (urlsplit(guideline.url).hostname or "").lower().removeprefix("www.")
        if host and host not in domains:
            domains.append(host)
    return domains[:30]


def _canonical_host(url: str) -> str:
    try:
        return (urlsplit(url).hostname or "").lower().removeprefix("www.")
    except ValueError:
        return ""


def _trusted_url(url: str, allowed_domains: list[str]) -> bool:
    host = _canonical_host(url)
    return bool(host and any(host == domain or host.endswith(f".{domain}") for domain in allowed_domains))


def _response_text_and_sources(payload: dict) -> tuple[str, list[str], int]:
    texts: list[str] = []
    sources: list[str] = []
    searches = 0
    for output in payload.get("output") or []:
        if output.get("type") == "web_search_call":
            searches += 1
            for source in (output.get("action") or {}).get("sources") or []:
                url = str(source.get("url") or "").strip()
                if url and url not in sources:
                    sources.append(url)
        if output.get("type") != "message":
            continue
        for content in output.get("content") or []:
            if content.get("type") != "output_text":
                continue
            texts.append(str(content.get("text") or ""))
            for annotation in content.get("annotations") or []:
                if annotation.get("type") != "url_citation":
                    continue
                url = str(annotation.get("url") or "").strip()
                if url and url not in sources:
                    sources.append(url)
    return "".join(texts).strip(), sources[:80], searches


def _responses_json(*, instructions: str, user_text: str, schema: dict,
                    schema_name: str, allowed_domains: list[str]) -> tuple[dict, list[str]]:
    if not settings.ai_enabled or settings.ai_provider != "openai" or not settings.openai_api_key.strip():
        raise RuntimeError("CorVIA Intelligence sem provedor de IA configurado.")
    request = {
        "model": _model(),
        "max_output_tokens": max(4096, settings.ai_max_output_tokens),
        "store": False,
        "instructions": instructions,
        "input": [{"role": "user", "content": [{"type": "input_text", "text": user_text}]}],
        "tools": [{"type": "web_search", "search_context_size": "high",
                   "filters": {"allowed_domains": allowed_domains}}],
        "tool_choice": "auto",
        "include": ["web_search_call.action.sources"],
        "text": {"format": {"type": "json_schema", "name": schema_name,
                            "strict": True, "schema": schema}},
    }
    with httpx.Client(timeout=httpx.Timeout(220.0, connect=20.0)) as client:
        response = client.post(
            RESPONSES_URL,
            headers={"Authorization": f"Bearer {settings.openai_api_key}", "Content-Type": "application/json"},
            json=request,
        )
    response.raise_for_status()
    payload = response.json()
    if payload.get("status") != "completed" or payload.get("error"):
        raise ValueError("Análise da diretriz não foi concluída pelo provedor.")
    text, sources, searches = _response_text_and_sources(payload)
    if searches == 0:
        raise ValueError("A análise não consultou fonte científica na web.")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError("O provedor não devolveu JSON válido para a diretriz.") from exc
    return data, sources


def _analysis_link(db: Session, guideline_id: int) -> GuidelineLink | None:
    return db.query(GuidelineLink).filter(
        GuidelineLink.guideline_id == guideline_id,
        GuidelineLink.item_type == ANALYSIS_ITEM_TYPE,
        GuidelineLink.item_id == ANALYSIS_ITEM_ID,
    ).first()


def get_analysis(db: Session, guideline: Guideline) -> dict | None:
    link = _analysis_link(db, guideline.id)
    if not link or not link.trecho:
        return None
    try:
        payload = json.loads(link.trecho)
    except (TypeError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _save_analysis(db: Session, guideline: Guideline, analysis: dict) -> None:
    link = _analysis_link(db, guideline.id)
    if link is None:
        link = GuidelineLink(
            guideline_id=guideline.id,
            item_type=ANALYSIS_ITEM_TYPE,
            item_id=ANALYSIS_ITEM_ID,
            origem=ORIGIN,
            confirmado=True,
        )
        db.add(link)
    link.trecho = json.dumps(analysis, ensure_ascii=False, sort_keys=True)
    link.origem = ORIGIN
    link.confirmado = True


def _analyze_source(guideline: Guideline) -> dict:
    domains = _domains_for(guideline)
    instructions = """Você integra o CorVIA Intelligence, um sistema de apoio a cardiologistas.
Analise SOMENTE a publicação científica oficial indicada e fontes primárias que a confirmem.
Produza síntese ORIGINAL em português; não traduza nem reproduza integralmente texto protegido.
Não invente classe, nível de evidência, dose, corte numérico ou recomendação. Só descreva mudança
quando ela estiver explicitamente sustentada pela fonte consultada. Se não for possível confirmar,
registre em limitations e marque explicit_in_source=false. Identifique o impacto prático no CorVIA:
definições, diagnóstico, tratamento, fluxogramas, monitorização, segurança, prevenção ou procedimentos.
Use source_url que tenha sido efetivamente consultada. Responda somente no JSON solicitado."""
    user_text = (
        f"Organização: {guideline.org}\n"
        f"Título original: {guideline.titulo}\n"
        f"Ano: {guideline.ano}\n"
        f"DOI: {guideline.doi or 'não informado'}\n"
        f"URL oficial: {guideline.url or 'não informada'}\n"
        f"Data de publicação: {guideline.published_at.isoformat() if guideline.published_at else 'não informada'}\n"
        "Localize o documento, confirme a identidade bibliográfica e descreva em português o que mudou em relação à prática anterior."
    )
    analysis, sources = _responses_json(
        instructions=instructions, user_text=user_text, schema=ANALYSIS_SCHEMA,
        schema_name="corvia_guideline_analysis", allowed_domains=domains,
    )
    for change in analysis.get("key_changes") or []:
        source_url = str(change.get("source_url") or "")
        if not _trusted_url(source_url, domains):
            change["explicit_in_source"] = False
            analysis.setdefault("limitations", []).append(
                f"Fonte da mudança não pertence aos domínios científicos permitidos: {source_url[:120]}"
            )
    analysis["source_urls_seen"] = sources[:40]
    analysis["analyzed_at"] = datetime.now(timezone.utc).isoformat()
    analysis["analysis_model"] = _model()
    analysis["translation_mode"] = "sintese_original_pt_br"
    return analysis


def _topic_terms(analysis: dict) -> list[str]:
    raw: list[str] = []
    raw.extend(str(x) for x in analysis.get("topics") or [])
    raw.extend(str(x.get("name") or "") for x in analysis.get("entities") or [] if isinstance(x, dict))
    terms: list[str] = []
    for value in raw:
        value = re.sub(r"\s+", " ", value).strip()
        if len(value) >= 4 and value.casefold() not in {x.casefold() for x in terms}:
            terms.append(value[:100])
        for token in re.findall(r"[A-Za-zÀ-ÿ0-9-]{5,}", value):
            if token.casefold() not in {x.casefold() for x in terms}:
                terms.append(token[:80])
        if len(terms) >= 12:
            break
    return terms[:12]


def _preview(value: Any, limit: int = 3500) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        text = value
    else:
        text = json.dumps(value, ensure_ascii=False, default=str)
    return text[:limit]


def _candidate_items(db: Session, analysis: dict) -> list[dict]:
    terms = _topic_terms(analysis)
    if not terms:
        return []
    candidates: list[dict] = []

    doc_filters = []
    for term in terms[:8]:
        pattern = f"%{term}%"
        doc_filters.extend((Document.title.ilike(pattern), Document.theme.ilike(pattern),
                            Document.summary.ilike(pattern), Document.body_md.ilike(pattern)))
    docs = db.query(Document).filter(
        Document.published.is_(True),
        ~Document.slug.like("corvia-intelligence-%"),
        or_(*doc_filters),
    ).limit(16).all()
    for item in docs:
        candidates.append({
            "item_type": "document", "item_id": item.id, "slug": item.slug, "label": item.title,
            "current": {"summary": _preview(item.summary, 1200), "body_md": _preview(item.body_md)},
        })

    evidence_filters = []
    for term in terms[:8]:
        pattern = f"%{term}%"
        evidence_filters.extend((EvidenceRecord.statement.ilike(pattern), EvidenceRecord.summary.ilike(pattern),
                                 EvidenceRecord.theme.ilike(pattern), EvidenceRecord.guideline_title.ilike(pattern)))
    evidences = db.query(EvidenceRecord).filter(
        EvidenceRecord.published.is_(True), or_(*evidence_filters)
    ).limit(10).all()
    for item in evidences:
        candidates.append({
            "item_type": "evidence", "item_id": item.id, "slug": item.slug,
            "label": item.statement[:220],
            "current": {"statement": _preview(item.statement, 1600), "summary": _preview(item.summary, 1000),
                        "class": item.recommendation_class, "level": item.evidence_level,
                        "guideline": item.guideline_title, "year": item.year},
        })

    disease_filters = []
    for term in terms[:8]:
        pattern = f"%{term}%"
        disease_filters.extend((SpecialtyDisease.name.ilike(pattern), SpecialtyDisease.summary.ilike(pattern),
                                SpecialtyDisease.category.ilike(pattern), SpecialtyDisease.treatment_summary.ilike(pattern)))
    diseases = db.query(SpecialtyDisease).filter(
        SpecialtyDisease.published.is_(True), or_(*disease_filters)
    ).limit(8).all()
    for item in diseases:
        candidates.append({
            "item_type": "disease", "item_id": item.id, "slug": item.slug, "label": item.name,
            "current": {"summary": _preview(item.summary, 1800),
                        "treatment_summary": _preview(item.treatment_summary, 1800),
                        "ambulatory_flow": _preview(item.ambulatory_flow, 1200),
                        "emergency_flow": _preview(item.emergency_flow, 1200)},
        })

    checklist_filters = []
    for term in terms[:8]:
        pattern = f"%{term}%"
        checklist_filters.extend((DischargeChecklist.condicao.ilike(pattern), DischargeChecklist.resumo.ilike(pattern),
                                  DischargeChecklist.theme.ilike(pattern)))
    checklists = db.query(DischargeChecklist).filter(
        DischargeChecklist.published.is_(True), or_(*checklist_filters)
    ).limit(6).all()
    for item in checklists:
        candidates.append({
            "item_type": "checklist", "item_id": item.id, "slug": item.slug, "label": item.condicao[:220],
            "current": {"resumo": _preview(item.resumo, 1600), "itens": _preview(item.itens, 2200)},
        })

    triage_filters = []
    for term in terms[:8]:
        pattern = f"%{term}%"
        triage_filters.extend((SymptomTriageGuide.name.ilike(pattern), SymptomTriageGuide.summary.ilike(pattern)))
    triages = db.query(SymptomTriageGuide).filter(
        SymptomTriageGuide.published.is_(True), or_(*triage_filters)
    ).limit(6).all()
    for item in triages:
        candidates.append({
            "item_type": "triage", "item_id": item.id, "slug": item.slug, "label": item.name,
            "current": {"summary": _preview(item.summary, 1600), "rules": _preview(item.rules, 1800),
                        "emergency_flow": _preview(item.emergency_flow, 1800)},
        })

    drug_names = [
        str(entity.get("name") or "").strip()
        for entity in analysis.get("entities") or []
        if isinstance(entity, dict) and entity.get("type") == "medicamento"
    ]
    if drug_names:
        drug_filters = [Drug.generic_name.ilike(f"%{name}%") for name in drug_names if name]
        if drug_filters:
            drugs = db.query(Drug).filter(Drug.published.is_(True), or_(*drug_filters)).limit(8).all()
            for item in drugs:
                candidates.append({
                    "item_type": "drug", "item_id": item.id, "slug": item.slug, "label": item.generic_name,
                    "current": {"dosing": _preview(item.dosing, 1600),
                                "indications": _preview(item.indications, 1000),
                                "monitoring": _preview(item.monitoring, 1000),
                                "contraindications": _preview(item.contraindications, 1000),
                                "notes": _preview(item.notes, 1400)},
                })

    # Mantém a janela do segundo modelo previsível.
    return candidates[:36]


def _propose_impacts(guideline: Guideline, analysis: dict, candidates: list[dict]) -> tuple[list[dict], list[str]]:
    if not analysis.get("requires_site_update") or not candidates:
        return [], []
    domains = _domains_for(guideline)
    instructions = """Você é o segundo estágio do CorVIA Intelligence. Recebe mudanças já extraídas de uma
publicação oficial e uma lista FECHADA de itens clínicos existentes. Selecione somente itens realmente
afetados. Não reescreva o conteúdo inteiro. Produza um override curto em português que deve aparecer no
topo do item e prevalecer sobre orientação antiga quando houver conflito. Só proponha override se a mudança
for explícita na fonte e se o item atual realmente estiver relacionado. Nunca invente item_id. Não use
conhecimento geral para completar lacunas. source_url precisa ser fonte primária efetivamente consultada.
Responda somente no JSON solicitado."""
    user_text = json.dumps({
        "guideline": {"org": guideline.org, "title": guideline.titulo, "doi": guideline.doi, "url": guideline.url},
        "analysis": analysis,
        "candidates": candidates,
    }, ensure_ascii=False, default=str)
    payload, sources = _responses_json(
        instructions=instructions, user_text=user_text, schema=IMPACT_SCHEMA,
        schema_name="corvia_guideline_impacts", allowed_domains=domains,
    )
    valid_ids = {(item["item_type"], int(item["item_id"])) for item in candidates}
    impacts = []
    for impact in payload.get("impacts") or []:
        key = (impact.get("item_type"), int(impact.get("item_id") or 0))
        if key not in valid_ids:
            continue
        if impact.get("confidence") != "alta" or not impact.get("explicit_support"):
            continue
        source_url = str(impact.get("source_url") or "")
        if not _trusted_url(source_url, domains):
            continue
        impact["override_pt"] = re.sub(r"\s+", " ", str(impact.get("override_pt") or "")).strip()[:2400]
        impact["change_summary_pt"] = re.sub(r"\s+", " ", str(impact.get("change_summary_pt") or "")).strip()[:900]
        if impact["override_pt"]:
            impacts.append(impact)
    return impacts[:20], sources


def _verify_impacts(guideline: Guideline, analysis: dict, impacts: list[dict]) -> list[dict]:
    if not impacts:
        return []
    domains = _domains_for(guideline)
    instructions = """Atue como verificador independente de segurança científica. Reabra a publicação oficial e
verifique cada override proposto pelo estágio anterior. Marque verified=true SOMENTE quando a recomendação
nova estiver explicitamente sustentada pela fonte e o resumo não extrapolar o texto. Não aprove por
plausibilidade clínica. Em dúvida, false. Responda somente no JSON solicitado."""
    user_text = json.dumps({
        "guideline": {"org": guideline.org, "title": guideline.titulo, "doi": guideline.doi, "url": guideline.url},
        "analysis": analysis,
        "impacts": impacts,
    }, ensure_ascii=False, default=str)
    payload, _ = _responses_json(
        instructions=instructions, user_text=user_text, schema=VERIFY_SCHEMA,
        schema_name="corvia_guideline_impact_verification", allowed_domains=domains,
    )
    verified = {
        (item.get("item_type"), int(item.get("item_id") or 0)): bool(item.get("verified"))
        for item in payload.get("verifications") or []
    }
    return [item for item in impacts if verified.get((item.get("item_type"), int(item.get("item_id") or 0))) is True]


def _source_ref(guideline: Guideline, impact: dict) -> str:
    parts = [guideline.org, guideline.titulo]
    if guideline.doi:
        parts.append(f"DOI {guideline.doi}")
    if impact.get("source_url"):
        parts.append(str(impact["source_url"]))
    return " · ".join(parts)


def _plain_override(guideline: Guideline, impact: dict) -> str:
    date = guideline.published_at.date().isoformat() if guideline.published_at else str(guideline.ano)
    return (
        f"[Atualização CorVIA Intelligence — {date}] {impact['override_pt']} "
        f"Esta atualização prevalece sobre orientação anterior deste item em caso de conflito. "
        f"Fonte oficial: {impact['source_url']}"
    )


def _markdown_override(guideline: Guideline, impact: dict) -> str:
    date = guideline.published_at.date().isoformat() if guideline.published_at else str(guideline.ano)
    return (
        f"<!-- corvia-intelligence:{guideline.slug}:start -->\n"
        f"> **Atualização CorVIA Intelligence — {date}**  \n"
        f"> {impact['override_pt']}  \n"
        f"> **Prevalência:** esta atualização prevalece sobre orientação anterior abaixo em caso de conflito.  \n"
        f"> **Fonte oficial:** {impact['source_url']}\n"
        f"<!-- corvia-intelligence:{guideline.slug}:end -->\n\n"
    )


def _strip_markdown_override(text: str, guideline_slug: str) -> str:
    pattern = re.compile(
        rf"<!-- corvia-intelligence:{re.escape(guideline_slug)}:start -->.*?"
        rf"<!-- corvia-intelligence:{re.escape(guideline_slug)}:end -->\s*",
        re.S,
    )
    return pattern.sub("", text or "").lstrip()


def _strip_plain_override(text: str | None, guideline_slug: str) -> str:
    if not text:
        return ""
    # Overrides planos ficam sempre na primeira linha/parágrafo e carregam a URL da fonte.
    prefix = "[Atualização CorVIA Intelligence —"
    if text.startswith(prefix):
        parts = text.split("\n\n", 1)
        if len(parts) == 2:
            return parts[1]
    return text


def _target_label(item_type: str, item: Any) -> str:
    return {
        "document": getattr(item, "title", "Documento"),
        "evidence": getattr(item, "statement", "Evidência"),
        "disease": getattr(item, "name", "Doença"),
        "drug": getattr(item, "generic_name", "Medicamento"),
        "checklist": getattr(item, "condicao", "Checklist"),
        "triage": getattr(item, "name", "Triagem"),
    }.get(item_type, item_type)[:300]


def _get_target(db: Session, item_type: str, item_id: int) -> Any | None:
    model = {
        "document": Document,
        "evidence": EvidenceRecord,
        "disease": SpecialtyDisease,
        "drug": Drug,
        "checklist": DischargeChecklist,
        "triage": SymptomTriageGuide,
    }.get(item_type)
    return db.get(model, item_id) if model else None


def _apply_override(db: Session, guideline: Guideline, impact: dict, *, record: bool = True) -> bool:
    item_type = str(impact["item_type"])
    item_id = int(impact["item_id"])
    target = _get_target(db, item_type, item_id)
    if target is None:
        return False
    before: dict[str, Any] = {}
    source_ref = _source_ref(guideline, impact)
    changed = False

    if item_type == "document":
        before = {"body_md": target.body_md, "summary": target.summary, "version": target.version}
        cleaned = _strip_markdown_override(target.body_md, guideline.slug)
        new_body = _markdown_override(guideline, impact) + cleaned
        if new_body != target.body_md:
            db.add(DocumentRevision(document_id=target.id, version=target.version,
                                    body_md=target.body_md, author_id=None))
            target.body_md = new_body
            target.summary = _plain_override(guideline, impact) + (f"\n\n{_strip_plain_override(target.summary, guideline.slug)}" if target.summary else "")
            target.source_refs = list(dict.fromkeys([*(target.source_refs or []), source_ref]))
            target.version += 1
            changed = True

    elif item_type == "evidence":
        before = {"summary": target.summary, "review_note": target.review_note, "reference": target.reference}
        base = _strip_plain_override(target.summary, guideline.slug)
        target.summary = _plain_override(guideline, impact) + (f"\n\n{base}" if base else "")
        target.review_note = f"CorVIA Intelligence: {impact['change_summary_pt']}"
        if str(impact.get("source_url")) not in (target.reference or ""):
            target.reference = f"{target.reference}\n{source_ref}".strip()
        changed = True

    elif item_type == "disease":
        before = {"summary": target.summary, "treatment_summary": target.treatment_summary,
                  "source_refs": list(target.source_refs or []), "source_urls": list(target.source_urls or []),
                  "version": target.version}
        field = "treatment_summary" if str(impact.get("target_section") or "").casefold() in {
            "tratamento", "treatment", "therapy", "terapia"
        } else "summary"
        current = getattr(target, field) or ""
        base = _strip_plain_override(current, guideline.slug)
        setattr(target, field, _plain_override(guideline, impact) + (f"\n\n{base}" if base else ""))
        target.source_refs = list(dict.fromkeys([*(target.source_refs or []), source_ref]))
        target.source_urls = list(dict.fromkeys([*(target.source_urls or []), str(impact["source_url"])]))
        target.review_note = f"CorVIA Intelligence: {impact['change_summary_pt']}"
        target.version += 1
        changed = True

    elif item_type == "drug":
        before = {"notes": target.notes, "references": list(target.references or [])}
        notes = dict(target.notes or {})
        updates = [x for x in (notes.get("corvia_intelligence_updates") or [])
                   if not isinstance(x, dict) or x.get("guideline_slug") != guideline.slug]
        updates.insert(0, {
            "guideline_slug": guideline.slug,
            "published_at": guideline.published_at.isoformat() if guideline.published_at else None,
            "change": impact["override_pt"],
            "prevalece_em_conflito": True,
            "source_url": impact["source_url"],
        })
        notes["corvia_intelligence_updates"] = updates[:12]
        target.notes = notes
        target.references = list(dict.fromkeys([*(target.references or []), source_ref]))
        changed = True

    elif item_type == "checklist":
        before = {"resumo": target.resumo, "revisao": target.revisao, "source_refs": target.source_refs}
        base = _strip_plain_override(target.resumo, guideline.slug)
        target.resumo = _plain_override(guideline, impact) + (f"\n\n{base}" if base else "")
        refs = list(target.source_refs or [])
        if source_ref not in refs:
            refs.append(source_ref)
        target.source_refs = refs
        target.revisao = f"CorVIA Intelligence: {impact['change_summary_pt']}"
        changed = True

    elif item_type == "triage":
        before = {"summary": target.summary, "source_refs": list(target.source_refs or []),
                  "source_urls": list(target.source_urls or []), "version": target.version}
        base = _strip_plain_override(target.summary, guideline.slug)
        target.summary = _plain_override(guideline, impact) + (f"\n\n{base}" if base else "")
        target.source_refs = list(dict.fromkeys([*(target.source_refs or []), source_ref]))
        target.source_urls = list(dict.fromkeys([*(target.source_urls or []), str(impact["source_url"])]))
        target.review_note = f"CorVIA Intelligence: {impact['change_summary_pt']}"
        target.version += 1
        changed = True

    if not changed:
        return False

    if record:
        link = db.query(GuidelineLink).filter(
            GuidelineLink.guideline_id == guideline.id,
            GuidelineLink.item_type == item_type,
            GuidelineLink.item_id == item_id,
        ).first()
        if link is None:
            link = GuidelineLink(guideline_id=guideline.id, item_type=item_type,
                                 item_id=item_id, origem=ORIGIN, confirmado=True)
            db.add(link)
        link.origem = ORIGIN
        link.confirmado = True
        link.trecho = json.dumps({
            **impact,
            "target_label": _target_label(item_type, target),
            "before": before,
            "applied_at": datetime.now(timezone.utc).isoformat(),
            "mode": "prevalent_override_non_destructive",
        }, ensure_ascii=False, default=str, sort_keys=True)
    return True


def _summary_body(guideline: Guideline, analysis: dict, impacts: list[dict]) -> str:
    changes = "\n".join(
        f"- **{str(item.get('category', 'mudança')).capitalize()}:** {item.get('change_pt')} — {item.get('practical_impact_pt')}"
        for item in analysis.get("key_changes") or [] if item.get("explicit_in_source")
    ) or "- Nenhuma mudança de prática explicitamente confirmada na análise automatizada."
    applied = "\n".join(
        f"- {item.get('change_summary_pt')}"
        for item in impacts
    ) or "- Nenhum override clínico automático foi necessário ou pôde ser confirmado com segurança."
    source = guideline.url or (f"https://doi.org/{guideline.doi}" if guideline.doi else "")
    return f"""# {analysis.get('title_pt') or guideline.titulo}

> **Síntese CorVIA Intelligence.** Texto original em português, não tradução integral da publicação.
> A publicação original permanece como fonte primária e deve ser consultada para detalhes completos.

## Resumo clínico

{analysis.get('summary_pt') or 'Resumo indisponível.'}

## O que mudou

{changes}

## O que mudou no CorVIA

{applied}

## Fonte original

- Organização: {guideline.org}
- DOI: {guideline.doi or 'não informado'}
- Publicação original: {source or 'URL não informada'}

## Limitações da síntese

""" + "\n".join(f"- {item}" for item in analysis.get("limitations") or ["Nenhuma limitação adicional registrada."])


def _ensure_summary_document(db: Session, guideline: Guideline, analysis: dict, impacts: list[dict]) -> Document:
    slug = f"corvia-intelligence-{guideline.slug}"[:255]
    body = _summary_body(guideline, analysis, impacts)
    doc = db.query(Document).filter(Document.slug == slug).first()
    source_refs = [x for x in [guideline.url, f"https://doi.org/{guideline.doi}" if guideline.doi else None] if x]
    tags = list(dict.fromkeys(["corvia-intelligence", "atualizacao-clinica", *(analysis.get("topics") or [])]))[:30]
    if doc is None:
        doc = Document(
            slug=slug,
            title=str(analysis.get("title_pt") or guideline.titulo)[:500],
            kind="diretriz",
            theme=str(analysis.get("theme") or guideline.tema or "Cardiologia")[:80],
            summary=str(analysis.get("summary_pt") or "")[:12000],
            body_md=body,
            tags=tags,
            source_refs=source_refs,
            source_tier="A",
            review_status="revisado",
            published=True,
            reviewed_by=None,
            reviewed_at=datetime.now(timezone.utc),
            gaps=[],
        )
        db.add(doc)
        db.flush()
    elif doc.body_md != body:
        db.add(DocumentRevision(document_id=doc.id, version=doc.version,
                                body_md=doc.body_md, author_id=None))
        doc.title = str(analysis.get("title_pt") or guideline.titulo)[:500]
        doc.theme = str(analysis.get("theme") or guideline.tema or "Cardiologia")[:80]
        doc.summary = str(analysis.get("summary_pt") or "")[:12000]
        doc.body_md = body
        doc.tags = tags
        doc.source_refs = source_refs
        doc.source_tier = "A"
        doc.review_status = "revisado"
        doc.published = True
        doc.version += 1
        doc.reviewed_at = datetime.now(timezone.utc)
    link = db.query(GuidelineLink).filter(
        GuidelineLink.guideline_id == guideline.id,
        GuidelineLink.item_type == SUMMARY_ITEM_TYPE,
        GuidelineLink.item_id == doc.id,
    ).first()
    if link is None:
        db.add(GuidelineLink(guideline_id=guideline.id, item_type=SUMMARY_ITEM_TYPE,
                             item_id=doc.id, origem=ORIGIN, confirmado=True,
                             trecho="Síntese em português publicada no conhecimento CorVIA."))
    return doc


def process_guideline(db: Session, guideline: Guideline) -> dict:
    existing = get_analysis(db, guideline)
    analysis = existing or _analyze_source(guideline)
    if not existing:
        guideline.tema = str(analysis.get("theme") or guideline.tema or "")[:120] or guideline.tema
        _save_analysis(db, guideline, analysis)
        db.commit()

    candidates = _candidate_items(db, analysis)
    proposed, _ = _propose_impacts(guideline, analysis, candidates)
    verified = _verify_impacts(guideline, analysis, proposed)

    applied: list[dict] = []
    for impact in verified:
        if _apply_override(db, guideline, impact, record=True):
            applied.append(impact)

    _ensure_summary_document(db, guideline, analysis, applied)
    if applied:
        guideline.detection_status = "aplicada_auto"
    elif analysis.get("requires_site_update"):
        guideline.detection_status = "revisao_necessaria"
    else:
        guideline.detection_status = "analisada"
    db.commit()

    # Documento de síntese é novo/alterado e precisa entrar no RAG imediatamente.
    try:
        from app.services import rag
        summary_doc = db.query(Document).filter(Document.slug == f"corvia-intelligence-{guideline.slug}"[:255]).first()
        if summary_doc:
            rag.indexar_documento(db, summary_doc)
    except Exception as exc:  # conteúdo/alerta continuam válidos mesmo se embedding falhar
        log.warning("Falha ao indexar síntese da diretriz %s: %s", guideline.slug, type(exc).__name__)

    return {
        "guideline_id": guideline.id,
        "slug": guideline.slug,
        "status": guideline.detection_status,
        "candidates": len(candidates),
        "proposed": len(proposed),
        "verified": len(verified),
        "applied": len(applied),
    }


def process_pending_guidelines(db: Session, *, limit: int = PROCESS_LIMIT) -> dict:
    if not settings.ai_enabled or settings.ai_provider != "openai" or not settings.openai_api_key.strip():
        return {"processed": 0, "skipped": "ai_unavailable", "items": [], "failures": []}
    statuses = ("detected", "aguardando_revisao", "revisao_necessaria")
    guidelines = db.query(Guideline).filter(Guideline.detection_status.in_(statuses)).order_by(
        Guideline.published_at.desc().nullslast(), Guideline.discovered_at.asc()
    ).limit(limit).all()
    items: list[dict] = []
    failures: list[dict] = []
    with _PROCESS_LOCK:
        for guideline in guidelines:
            try:
                items.append(process_guideline(db, guideline))
            except Exception as exc:
                db.rollback()
                log.exception("Falha ao analisar/aplicar diretriz %s", guideline.slug)
                failures.append({"guideline_id": guideline.id, "slug": guideline.slug,
                                 "error": type(exc).__name__})
    return {"processed": len(items), "items": items, "failures": failures}


def list_impacts(db: Session, guideline: Guideline) -> list[dict]:
    links = db.query(GuidelineLink).filter(
        GuidelineLink.guideline_id == guideline.id,
        GuidelineLink.origem == ORIGIN,
        GuidelineLink.confirmado.is_(True),
        GuidelineLink.item_type.in_(tuple(UPDATEABLE_TYPES)),
    ).order_by(GuidelineLink.item_type, GuidelineLink.item_id).all()
    items: list[dict] = []
    for link in links:
        try:
            payload = json.loads(link.trecho or "{}")
        except json.JSONDecodeError:
            continue
        items.append({
            "item_type": link.item_type,
            "item_id": link.item_id,
            "target_label": payload.get("target_label"),
            "target_section": payload.get("target_section"),
            "change_summary_pt": payload.get("change_summary_pt"),
            "source_url": payload.get("source_url"),
            "applied_at": payload.get("applied_at"),
            "mode": payload.get("mode"),
        })
    return items


def reapply_confirmed_updates(db: Session) -> dict:
    """Restaura overrides depois que o deploy reconciliou arquivos -> PostgreSQL."""
    links = db.query(GuidelineLink).filter(
        GuidelineLink.origem == ORIGIN,
        GuidelineLink.confirmado.is_(True),
        GuidelineLink.item_type.in_(tuple(UPDATEABLE_TYPES)),
    ).order_by(GuidelineLink.guideline_id, GuidelineLink.id).all()
    reapplied = 0
    missing = 0
    for link in links:
        guideline = db.get(Guideline, link.guideline_id)
        if not guideline:
            missing += 1
            continue
        try:
            impact = json.loads(link.trecho or "{}")
        except json.JSONDecodeError:
            missing += 1
            continue
        if _apply_override(db, guideline, impact, record=False):
            reapplied += 1
    # Sínteses também podem ser removidas pela reconciliação por não existirem em /content.
    for guideline in db.query(Guideline).all():
        analysis = get_analysis(db, guideline)
        if analysis:
            _ensure_summary_document(db, guideline, analysis, list_impacts(db, guideline))
    db.commit()
    return {"reapplied": reapplied, "missing": missing}
