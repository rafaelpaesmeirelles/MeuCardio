"""Heart Team orchestration, accounting, cache and immutable audit."""

from __future__ import annotations

import base64
import hashlib
import json
import unicodedata
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from types import SimpleNamespace
from urllib.parse import quote

from sqlalchemy import func, text

from app.core.config import settings
from app.models.audit import AuditLog
from app.models.heart_team import (
    HeartTeamAnalysisJob, HeartTeamAttachment, HeartTeamAuditEvent, HeartTeamCache, HeartTeamCase,
    HeartTeamCostLedger, HeartTeamFinalReview, HeartTeamOpinion,
    HeartTeamSuggestion, HeartTeamSuggestionReview,
)
from app.models.knowledge import KnowledgeRelation
from app.services.cofre import cifrar_campo, decifrar_campo, guardar, ler
from app.services.heart_team_agents import (
    AGENTS, COORDINATOR_SYSTEM, contestation_prompt, independent_round_inputs,
    selected_agent_keys, specialist_prompt,
)
from app.services.heart_team_evidence import sanitize_registry_for_persistence, source_catalog, verify_source_rows
from app.services.heart_team_safety import (
    deterministic_disagreements, emergency_screen, mandatory_opinion_usable,
    normalize_opinion, validate_deidentified,
)
from app.services.ia.usage_control import ai_operation, input_token_bound, plan_token_budgets
from app.services.knowledge_graph import relacionados_de

PIPELINE_VERSION = "heart-team-v1.2-dedicated-frontier"
HEART_TEAM_MAX_OPINION_BYTES = 32 * 1024
VISUAL_SYSTEM = "Extração clínica preliminar desidentificada; toda interpretação exige validação médica."
VISUAL_INSTRUCTION = (
    "Extraia SOMENTE observações visuais objetivas do exame para revisão médica. "
    "Não diagnostique, não recomende tratamento e não invente medidas. Responda JSON "
    "com image_quality, objective_observations, unreadable_elements e limitations."
)
HUMAN_ONLY = [
    "Confirmar diagnóstico e prognóstico.",
    "Indicar, cancelar ou interpretar exames no contexto assistencial.",
    "Prescrever, ajustar ou suspender tratamento.",
    "Comunicar conclusão clínica ao paciente ou familiar.",
    "Assinar qualquer documento clínico.",
]


class HeartTeamError(RuntimeError): ...
class HeartTeamDisabled(HeartTeamError): ...
class HeartTeamSafetyError(HeartTeamError): ...
class HeartTeamBudgetExceeded(HeartTeamError): ...


def heart_team_model_config() -> dict:
    """Dedicated clinical configuration; never inherit the general chat tier."""
    provider = str(settings.heart_team_ai_provider).strip().lower()
    model = str(settings.heart_team_clinical_model).strip()
    effort = str(settings.heart_team_reasoning_effort).strip()
    output = int(settings.heart_team_max_output_tokens)
    if provider not in {"openai", "anthropic"} or not model or output <= 0:
        raise HeartTeamError("Configuração exclusiva do modelo Heart Team inválida.")
    if (provider == "openai" and model.startswith("claude-")) or (provider == "anthropic" and not model.startswith("claude-")):
        raise HeartTeamError("Modelo Heart Team incompatível com seu provedor exclusivo.")
    if effort not in {"low", "medium", "high"}:
        raise HeartTeamError("Nível de raciocínio Heart Team inválido.")
    return {"provider": provider, "model": model, "max_output_tokens": output,
            "reasoning_effort": effort, "max_opinion_bytes": HEART_TEAM_MAX_OPINION_BYTES}


def obter_provedor_heart_team():
    from app.services.ia.provedor import ProvedorOpenAI, ProvedorAnthropic
    config = heart_team_model_config()
    provider = {"openai": ProvedorOpenAI, "anthropic": ProvedorAnthropic}[config["provider"]]()
    # This instance is never shared with the application's general chat cache.
    provider._modelo = config["model"]
    provider._heart_team_provider_name = config["provider"]
    return provider


def _clinical_system(system: str) -> str:
    return system + "\nProduza JSON estruturado conciso com no máximo 32 KiB em UTF-8. Preserve achados, fontes, limitações e divergências relevantes; evite repetição literal."


def _consensus_message(snapshot: dict, opinions: list[dict], sources: list[dict]) -> dict:
    # Content is complete. Execution metadata and repeated copies of mandatory
    # opinions/claim positions add no clinical evidence to the coordinator.
    return {"case": snapshot, "opinions": [
        {"agent_key": row["agent_key"], "round_name": row["round_name"], "content": row["content"]}
        for row in opinions], "sources": sources}


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def stable_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


def content_hash(value: Any) -> str:
    return hashlib.sha256(stable_json(value).encode()).hexdigest()


def enabled() -> None:
    if not settings.heart_team_enabled:
        raise HeartTeamDisabled("HEART_TEAM_ENABLED está desativada.")


def is_heart_team_physician(user) -> bool:
    if not user or not getattr(user, "is_active", False) or getattr(user, "investidor", False):
        return False
    if getattr(user, "role", None) not in {"medico", "admin"} or getattr(user, "status", None) != "aprovado":
        return False
    profession = unicodedata.normalize("NFKD", str(getattr(user, "profession", "") or "")).encode("ascii", "ignore").decode().casefold()
    council = str(getattr(user, "council_name", "") or "").strip().upper()
    number = str(getattr(user, "council_number", "") or getattr(user, "crm", "") or "").strip()
    state = str(getattr(user, "council_state", "") or "").strip()
    legacy_crm = str(getattr(user, "crm", "") or "").strip()
    return ("medic" in profession and council == "CRM" and bool(number and state)) or bool(legacy_crm and "medic" in profession)


def ensure_heart_team_physician(db, user_id: int):
    from app.models.user import User
    user = db.query(User).filter(User.id == user_id).first()
    if not is_heart_team_physician(user):
        raise HeartTeamSafetyError("Heart Team é restrito a médico com CRM e perfil profissional aprovado.")
    return user


def audit_event(db, case: HeartTeamCase, *, actor_id: int | None, action: str, detail: dict | None = None) -> HeartTeamAuditEvent:
    try:
        db.execute(text("SELECT pg_advisory_xact_lock(:namespace, :case_id)"), {"namespace": 1213486165, "case_id": case.id})
    except Exception:
        if getattr(getattr(getattr(db, "bind", None), "dialect", None), "name", None) == "postgresql":
            raise
    previous = db.query(HeartTeamAuditEvent).filter(HeartTeamAuditEvent.case_id == case.id).order_by(HeartTeamAuditEvent.id.desc()).first()
    created = utcnow()
    payload = {"case_id": case.id, "actor_id": actor_id, "action": action, "detail": detail or {}, "previous_hash": previous.event_hash if previous else "0" * 64, "created_at": created.isoformat()}
    row = HeartTeamAuditEvent(case_id=case.id, actor_id=actor_id, action=action, detail=detail or {}, previous_hash=payload["previous_hash"], event_hash=content_hash(payload), created_at=created)
    db.add(row)
    db.add(AuditLog(user_id=actor_id, action=f"heart_team.{action}"[:80], entity="heart_team_case", entity_id=str(case.id), detail=detail or {}))
    return row


def audit_sensitive_read(db, case: HeartTeamCase, actor_id: int, surface: str) -> None:
    audit_event(db, case, actor_id=actor_id, action="sensitive_read", detail={"surface": surface})
    db.commit()


def build_snapshot(payload: dict) -> dict:
    return {
        "question": payload.get("question"), "analysis_scope": payload.get("analysis_scope", "global"),
        "case_text": payload.get("case_text"), "age": payload.get("age"), "sex": payload.get("sex"),
        "symptoms": payload.get("symptoms") or [], "vital_signs": payload.get("vital_signs") or {},
        "comorbidities": payload.get("comorbidities") or [], "medications": payload.get("medications") or [],
        "allergies": payload.get("allergies") or [], "laboratory_tests": payload.get("laboratory_tests") or [],
        "attachments": payload.get("attachments") or [],
        "source_patient_id": payload.get("source_patient_id"),
        "source_patient_authorized": bool(payload.get("source_patient_authorized")),
        "patient_context_imported": bool(payload.get("patient_context_imported")),
    }


def structure_case(snapshot: dict) -> tuple[dict, list[str]]:
    missing = [name for name in ("age", "sex", "symptoms", "medications", "allergies") if snapshot.get(name) in (None, "", [])]
    return deepcopy(snapshot), missing


def _merge_patient_context(payload: dict, context: str) -> dict:
    merged = dict(payload)
    existing = str(merged.get("case_text") or "").strip()
    merged["case_text"] = "\n\n".join(part for part in (existing, context.strip()) if part)
    merged["patient_context_imported"] = True
    return merged


def _import_patient_context(db, *, owner_id: int, patient_id: int, authorized: bool) -> str:
    if not authorized:
        raise HeartTeamSafetyError("Importação do prontuário exige autorização explícita do médico.")
    from app.models.patient_profile import PatientProfile
    profile = db.query(PatientProfile).filter(PatientProfile.id == patient_id, PatientProfile.owner_id == owner_id).first()
    if not profile:
        raise HeartTeamSafetyError("Prontuário não encontrado para este assinante.")
    # Reuse the existing owner-scoped/deidentifying chart projection instead
    # of introducing a second interpretation of the longitudinal record.
    from app.api.patient_multimodal_ai import _chart_context
    return _chart_context(patient_id, db, SimpleNamespace(id=owner_id))


def create_case_draft(db, *, owner_id: int, created_by_id: int, payload: dict, origin: str = "corvia") -> HeartTeamCase:
    ensure_heart_team_physician(db, created_by_id)
    if payload.get("source_patient_id") is not None:
        context = _import_patient_context(db, owner_id=owner_id, patient_id=int(payload["source_patient_id"]), authorized=bool(payload.get("source_patient_authorized")))
        payload = _merge_patient_context(payload, context)
    snapshot = build_snapshot(payload)
    case = HeartTeamCase(owner_id=owner_id, created_by_id=created_by_id, question=payload.get("question"), analysis_scope=payload.get("analysis_scope", "global"), selected_agents=selected_agent_keys(payload.get("selected_agents")), input_data=snapshot, pipeline_version=PIPELINE_VERSION)
    db.add(case); db.flush()
    for reference in snapshot.get("attachments") or []:
        if not isinstance(reference, dict) or reference.get("kind") == "upload":
            continue
        reference_id = str(reference.get("reference_id") or "")
        db.add(HeartTeamAttachment(
            case_id=case.id, owner_id=owner_id, kind=str(reference.get("kind")),
            reference_id=reference_id, media_type=str(reference.get("media_type") or "application/octet-stream"),
            size_bytes=0, sha256=str(reference.get("sha256") or content_hash({"kind": reference.get("kind"), "reference_id": reference_id})),
            objective_extract={},
        ))
    audit_event(db, case, actor_id=created_by_id, action="draft_created", detail={"origin": origin, "input_hash": content_hash(snapshot)})
    db.commit(); db.refresh(case)
    return case


def _json_response(text_value: str) -> dict:
    raw = (text_value or "").strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[-1].rsplit("```", 1)[0]
    try:
        value = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return {"summary": "evidência insuficiente", "claims": [], "source_ids": [], "confidence": "insufficient", "limitations": ["Resposta do provedor não aderiu ao contrato estruturado."]}
    return value if isinstance(value, dict) else {"summary": "evidência insuficiente", "claims": [], "source_ids": [], "confidence": "insufficient"}


def _estimate_cost_micros(input_chars: int, max_output_tokens: int, *, media_bytes: int = 0) -> int:
    input_tokens = max(1, input_chars // 4) + (media_bytes // 1500)
    # Conservative configurable ceiling: cost ledger uses micros of account currency.
    return input_tokens * int(getattr(settings, "heart_team_input_token_cost_micros", 2)) + max_output_tokens * int(getattr(settings, "heart_team_output_token_cost_micros", 12))


def _monthly_spend(db, owner_id: int) -> int:
    start = utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return int(db.query(func.coalesce(func.sum(HeartTeamCostLedger.actual_micros), 0)).filter(HeartTeamCostLedger.owner_id == owner_id, HeartTeamCostLedger.created_at >= start).scalar() or 0)


def _enforce_case_limits(db, case: HeartTeamCase) -> None:
    now = utcnow(); day = now.replace(hour=0, minute=0, second=0, microsecond=0); month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    try:
        db.execute(text("SELECT pg_advisory_xact_lock(:namespace, :owner)"), {"namespace": 1213486164, "owner": case.owner_id})
    except Exception:
        if getattr(getattr(getattr(db, "bind", None), "dialect", None), "name", None) == "postgresql": raise
    terminal = {"analyzing", "awaiting_review", "completed", "rejected", "failed", "unusable"}
    daily = db.query(HeartTeamCase).filter(HeartTeamCase.owner_id == case.owner_id, HeartTeamCase.created_at >= day, HeartTeamCase.status.in_(terminal)).count()
    monthly = db.query(HeartTeamCase).filter(HeartTeamCase.owner_id == case.owner_id, HeartTeamCase.created_at >= month, HeartTeamCase.status.in_(terminal)).count()
    if daily >= int(getattr(settings, "heart_team_daily_case_limit", 10)) or monthly >= int(getattr(settings, "heart_team_monthly_case_limit", 100)):
        raise HeartTeamBudgetExceeded("Limite de análises do Heart Team atingido.")


def _reserve_call(db, case: HeartTeamCase, *, agent_key: str, phase: str, input_chars: int, media_bytes: int = 0) -> HeartTeamCostLedger:
    max_output = int(getattr(settings, "heart_team_max_output_tokens", 8192))
    reserve = _estimate_cost_micros(input_chars, max_output, media_bytes=media_bytes)
    try:
        db.execute(text("SELECT pg_advisory_xact_lock(:namespace, :owner)"), {"namespace": 1213486164, "owner": case.owner_id})
    except Exception:
        # Tests may use a non-Postgres fake; production is PostgreSQL and locks.
        if getattr(db.bind.dialect, "name", None) == "postgresql":
            raise
    # The shared AI wallet reserves the complete journey before the first paid
    # request. Keep this legacy ledger for clinical audit, not a second tariff gate.
    case.reserved_cost_micros = int(case.reserved_cost_micros or 0) + reserve
    row = HeartTeamCostLedger(case_id=case.id, owner_id=case.owner_id, agent_key=agent_key, phase=phase, reserved_micros=reserve)
    db.add(row); db.commit(); db.refresh(row)
    return row


def _reconcile_call(db, case: HeartTeamCase, ledger: HeartTeamCostLedger, response) -> None:
    actual = int(response.tokens_entrada or 0) * int(getattr(settings, "heart_team_input_token_cost_micros", 2)) + int(response.tokens_saida or 0) * int(getattr(settings, "heart_team_output_token_cost_micros", 12))
    # Ledger is append-only: reconciliation is a second ledger event.
    db.add(HeartTeamCostLedger(case_id=case.id, owner_id=case.owner_id, agent_key=ledger.agent_key, phase=f"{ledger.phase}:actual", actual_micros=actual, tokens_input=int(response.tokens_entrada or 0), tokens_output=int(response.tokens_saida or 0), model_name=response.modelo or ""))
    case.reserved_cost_micros = max(0, int(case.reserved_cost_micros or 0) - ledger.reserved_micros)
    case.estimated_cost_micros = int(case.estimated_cost_micros or 0) + actual
    case.tokens_input = int(case.tokens_input or 0) + int(response.tokens_entrada or 0)
    case.tokens_output = int(case.tokens_output or 0) + int(response.tokens_saida or 0)
    versions = dict(case.model_versions or {}); versions[f"{ledger.phase}:{ledger.agent_key}"] = response.modelo; case.model_versions = versions
    db.commit()


def _call(db, case: HeartTeamCase, *, provider, agent_key: str, round_name: str, system: str, message: dict, registry: dict[str, dict]) -> dict:
    serialized = stable_json(message)
    ledger = _reserve_call(db, case, agent_key=agent_key, phase=round_name, input_chars=len(system) + len(serialized))
    try:
        config = heart_team_model_config()
        response = provider.responder(sistema=_clinical_system(system), mensagens=[{"role": "user", "content": serialized}], modelo=config["model"], usar_internet=False, max_output_tokens=config["max_output_tokens"], reasoning_effort=config["reasoning_effort"])
    except Exception:
        case.reserved_cost_micros = max(0, int(case.reserved_cost_micros or 0) - ledger.reserved_micros); db.commit(); raise
    _reconcile_call(db, case, ledger, response)
    if getattr(response, "truncado", False):
        raise HeartTeamSafetyError("O modelo atingiu o limite de saída; nenhuma conclusão clínica foi emitida.")
    raw = _json_response(response.texto)
    content, _blocks = normalize_opinion(raw, registry)
    ids = sorted({sid for claim in content.get("claims", []) for sid in claim.get("source_ids", [])})
    content["source_ids"] = ids
    _check_response_envelope(content)
    opinion = HeartTeamOpinion(case_id=case.id, agent_key=agent_key, round_name=round_name, position={"claims": [{"statement": c.get("statement"), "position": c.get("position", "uncertain")} for c in content.get("claims", [])]}, content=content, source_ids=ids, confidence=content.get("confidence", "insufficient"), content_hash=content_hash(content), model_name=response.modelo, tokens_input=response.tokens_entrada, tokens_output=response.tokens_saida)
    db.add(opinion); db.commit(); db.refresh(opinion)
    result = {"id": opinion.id, "agent_key": agent_key, "round_name": round_name, "content": content, "position": opinion.position, "source_ids": ids, "confidence": opinion.confidence, "content_hash": opinion.content_hash, "model_name": opinion.model_name, "tokens_input": opinion.tokens_input, "tokens_output": opinion.tokens_output}
    return result


def _knowledge_graph_fingerprint(db) -> str:
    count, updated = db.query(func.count(KnowledgeRelation.id), func.max(KnowledgeRelation.updated_at)).one()
    return content_hash({"relations": int(count or 0), "updated_at": updated.isoformat() if updated else None})


def _cache_key(case: HeartTeamCase, snapshot: dict, attachments: list[dict], *, graph_fingerprint: str = "unknown") -> str:
    return content_hash({"owner_id": case.owner_id, "snapshot": snapshot, "attachments": [{k: a.get(k) for k in ("source_sha256", "sha256", "media_type", "size_bytes", "kind", "reference_id", "sanitization_report", "objective_extract")} for a in attachments], "agents": case.selected_agents, "pipeline": PIPELINE_VERSION, "knowledge_graph": graph_fingerprint, "model_config": heart_team_model_config()})


def purge_expired_cache(db, *, now: datetime | None = None) -> int:
    count = db.query(HeartTeamCache).filter(HeartTeamCache.expires_at <= (now or utcnow())).delete(synchronize_session=False)
    db.commit()
    return int(count)


def _cache_get(db, owner_id: int, key: str) -> dict | None:
    row = db.query(HeartTeamCache).filter(HeartTeamCache.owner_id == owner_id, HeartTeamCache.cache_key == key, HeartTeamCache.expires_at > utcnow()).first()
    if not row:
        return None
    try:
        return json.loads(decifrar_campo(row.encrypted_payload, owner_id))
    except Exception:
        return None


def _cache_put(db, owner_id: int, key: str, payload: dict) -> None:
    ttl = int(getattr(settings, "heart_team_cache_ttl_seconds", 3600))
    db.add(HeartTeamCache(owner_id=owner_id, cache_key=key, encrypted_payload=cifrar_campo(stable_json(payload), owner_id), expires_at=utcnow() + timedelta(seconds=ttl))); db.commit()


def _materialize_suggestions(db, case: HeartTeamCase, result: dict) -> None:
    for category in ("additional_tests", "therapeutic_options", "safety"):
        values = result.get(category) or []
        if isinstance(values, str):
            values = [values]
        for value in values:
            text_value = stable_json(value) if isinstance(value, (dict, list)) else str(value)
            if text_value and text_value != "evidência insuficiente":
                db.add(HeartTeamSuggestion(case_id=case.id, category=category, original_text=text_value, original_hash=content_hash(text_value)))


def _materialize_cached_opinions(db, case: HeartTeamCase, opinions: list[dict]) -> None:
    """Replay a verified encrypted cache bundle into this case's immutable rows."""
    for item in opinions:
        content = item.get("content") if isinstance(item, dict) else None
        if not isinstance(content, dict) or not item.get("agent_key") or not item.get("round_name"):
            raise HeartTeamSafetyError("Bundle clínico em cache inválido.")
        expected_hash = content_hash(content)
        if item.get("content_hash") != expected_hash:
            raise HeartTeamSafetyError("Integridade do parecer em cache inválida.")
        db.add(HeartTeamOpinion(
            case_id=case.id, agent_key=str(item["agent_key"]), round_name=str(item["round_name"]),
            position=item.get("position") or {}, content=content,
            source_ids=list(item.get("source_ids") or []), confidence=str(item.get("confidence") or "insufficient"),
            content_hash=expected_hash, model_name=str(item.get("model_name") or "unknown-cached-model"),
            tokens_input=int(item.get("tokens_input") or 0), tokens_output=int(item.get("tokens_output") or 0),
        ))


def resolve_related_content(db, verified_sources: list[dict], *, per_type: int = 5) -> list[dict]:
    """Resolve only cited sources and reviewed persisted graph edges.

    A private case is deliberately never registered as a global graph node.
    The public cited nodes are traversal anchors, preserving tenant/PHI
    isolation while still applying Tudo com Tudo.
    """
    items: list[dict] = []
    seen: set[tuple[str, str]] = set()
    counts: dict[str, int] = {}

    def add(item: dict) -> None:
        kind, href = str(item.get("type") or ""), str(item.get("href") or "")
        if not kind or not href or (kind, href) in seen or counts.get(kind, 0) >= per_type:
            return
        seen.add((kind, href)); counts[kind] = counts.get(kind, 0) + 1; items.append(item)

    for source in verified_sources:
        if not source.get("reviewed"):
            continue
        source_id = str(source.get("id") or "")
        entity_type, slug = source.get("entity_type"), source.get("slug")
        if source.get("route"):
            add({"type": entity_type, "slug": slug, "title": source.get("title"), "href": source["route"], "relation_type": "cited_source", "source_id": source_id, "review_status": "revisado", "confidence": "explicit"})
        theme = str(source.get("theme") or "").strip()
        if theme and entity_type in {"evidencia", "estudo", "diretriz"}:
            add({"type": "timeline", "slug": theme, "title": f"Linha do tempo · {theme}", "href": f"/trilhas/timeline?tema={quote(theme)}", "relation_type": "timeline_for_cited_source", "source_id": source_id, "review_status": "revisado", "confidence": "explicit"})
        if entity_type not in {"documento", "fluxograma", "evidencia", "estudo", "medicamento", "exame", "caso_clinico", "trilha", "galeria", "checklist", "material_paciente", "protocolo_emergencia", "calculadora", "doenca", "triagem_sintoma"} or not slug:
            continue
        graph = relacionados_de(db, entity_type=entity_type, slug=slug, limite_por_tipo=per_type, incluir_contexto_tematico=False)
        if not graph:
            continue
        for group in graph.get("grupos", []):
            for related in group.get("itens", []):
                if related.get("review_status") != "revisado":
                    continue
                add({"type": group.get("tipo"), "slug": related.get("slug"), "title": related.get("titulo"), "href": related.get("rota"), "relation_type": related.get("relation_type"), "source_id": source_id, "review_status": related.get("review_status"), "confidence": related.get("confidence"), "provenance_type": related.get("provenance_type")})
    return items


def attachment_descriptors(db, case: HeartTeamCase) -> list[dict]:
    rows = db.query(HeartTeamAttachment).filter(HeartTeamAttachment.case_id == case.id, HeartTeamAttachment.owner_id == case.owner_id).order_by(HeartTeamAttachment.id).all()
    for row in rows:
        if row.kind == "scientific_document" and row.reference_id:
            from app.models.scientific_user_document import ScientificUserDocument
            try: ref_id = int(row.reference_id)
            except ValueError: raise HeartTeamSafetyError("Referência científica inválida.") from None
            document = db.query(ScientificUserDocument).filter(ScientificUserDocument.id == ref_id, ScientificUserDocument.owner_id == case.owner_id, ScientificUserDocument.analysis_status == "concluido").first()
            if not document:
                raise HeartTeamSafetyError("Documento científico não pertence ao assinante ou não foi analisado.")
            extracted = decifrar_campo(document.extracted_text_cifrado, document.id) if document.extracted_text_cifrado else ""
            row.sha256 = document.sha256; row.media_type = document.media_type; row.size_bytes = document.size_bytes
            row.objective_extract = {"type": "scientific_document", "text": extracted[:24000], "document_id": document.id}
        elif row.kind == "patient_exam" and row.reference_id:
            if not (case.input_data or {}).get("source_patient_authorized"):
                raise HeartTeamSafetyError("Importação do prontuário exige autorização explícita do médico.")
            from app.models.prontuario import PatientECGRecord, PatientExamResult
            kind, _, raw_id = row.reference_id.partition(":")
            if not raw_id: kind, raw_id = "result", kind
            try: ref_id = int(raw_id)
            except ValueError: raise HeartTeamSafetyError("Referência de exame inválida.") from None
            if kind == "ecg":
                record = db.query(PatientECGRecord).filter(PatientECGRecord.id == ref_id, PatientECGRecord.owner_id == case.owner_id).first()
                if not record: raise HeartTeamSafetyError("ECG não pertence ao assinante.")
                binary = ler(record.storage_key, case.owner_id)
                row.sha256 = hashlib.sha256(binary).hexdigest(); row.media_type = record.media_type; row.size_bytes = record.size_bytes
                row.objective_extract = {"type": "patient_ecg", "record_id": record.id, "sha256": row.sha256}
            else:
                result = db.query(PatientExamResult).filter(PatientExamResult.id == ref_id, PatientExamResult.owner_id == case.owner_id).first()
                if not result: raise HeartTeamSafetyError("Exame não pertence ao assinante.")
                payload = decifrar_campo(result.payload_cifrado, result.id)
                row.sha256 = hashlib.sha256(payload.encode()).hexdigest(); row.media_type = "application/json"; row.size_bytes = len(payload.encode())
                row.objective_extract = {"type": "patient_exam", "exam_kind": result.exam_kind, "performed_at": result.performed_at.isoformat(), "payload": payload[:24000]}
    db.commit()
    return [{"id": row.id, "kind": row.kind, "reference_id": row.reference_id, "media_type": row.media_type, "size_bytes": row.size_bytes, "source_sha256": row.source_sha256, "sha256": row.sha256, "sanitization_report": row.sanitization_report or {}, "objective_extract": row.objective_extract or {}} for row in rows]


def _visual_bytes(db, case: HeartTeamCase, descriptor: dict) -> bytes | None:
    row = db.query(HeartTeamAttachment).filter(HeartTeamAttachment.id == descriptor["id"], HeartTeamAttachment.case_id == case.id, HeartTeamAttachment.owner_id == case.owner_id).first()
    if not row:
        return None
    if row.storage_key:
        return ler(row.storage_key, case.owner_id, raiz=Path(settings.heart_team_files_dir))
    if row.kind == "patient_exam" and (row.reference_id or "").startswith("ecg:"):
        from app.models.prontuario import PatientECGRecord
        try: record_id = int(row.reference_id.split(":", 1)[1])
        except (ValueError, IndexError): return None
        record = db.query(PatientECGRecord).filter(PatientECGRecord.id == record_id, PatientECGRecord.owner_id == case.owner_id).first()
        return ler(record.storage_key, case.owner_id) if record else None
    return None



def _response_envelope_limit(output_tokens: int | None = None) -> int:
    """Bound structural expansion of normalized answers, without truncation."""
    return HEART_TEAM_MAX_OPINION_BYTES


def _check_response_envelope(value: dict, *, output_tokens: int | None = None) -> None:
    if len(stable_json(value).encode("utf-8")) > _response_envelope_limit(output_tokens):
        raise HeartTeamSafetyError("Resposta estruturada excede o limite da análise; nenhuma conclusão foi emitida.")


def _visual_candidates(descriptors: list[dict]) -> list[dict]:
    return [item for item in descriptors if (
        str(item.get("media_type") or "").startswith("image/")
        or (item.get("media_type") == "application/pdf" and not str((item.get("objective_extract") or {}).get("text") or "").strip())
    ) and not (item.get("objective_extract") or {}).get("multimodal_extract")]


def _plan_journey(db, case: HeartTeamCase, provider, context: dict, agent_keys: list[str], *, extra_input_bytes: int = 0) -> None:
    """Authorize all 2N-1 deliberations and visual work before any paid request.

    Future structured replies are bounded by _check_response_envelope. Input
    bytes conservatively bound tokenizer input. The consensus allowance also
    follows the exact compact message shape used by the coordinator. No patient
    payload is persisted by the accounting layer.
    """
    config = heart_team_model_config()
    provider_name, model, max_output = config["provider"], config["model"], config["max_output_tokens"]
    envelope = _response_envelope_limit(max_output)
    extract_output = max_output
    candidates = _visual_candidates(context["attachments"])
    visual_requests = []
    future_extract_bytes = 0
    if settings.ai_clinical_multimodal_enabled and settings.ai_clinical_data_controls_approved:
        for descriptor in candidates:
            binary = _visual_bytes(db, case, descriptor)
            if not binary:
                raise HeartTeamSafetyError("Arquivo visual não pôde ser lido com segurança.")
            visual_requests.extend(provider._clinical_file_request_variants(
                VISUAL_SYSTEM, VISUAL_INSTRUCTION, binary, descriptor["media_type"],
                modelo=model, max_output_tokens=extract_output))
            # JSON escaping plus new extraction metadata in the existing descriptor.
            future_extract_bytes += 2 * _response_envelope_limit(extract_output) + 4096
    # A fixed wrapper allowance covers provider SDK keys and message framing.
    context_bytes = len(stable_json(context).encode("utf-8")) + future_extract_bytes + extra_input_bytes
    base_bytes = len(stable_json({"case": context["case"], "sources": context["sources"]}).encode("utf-8")) + extra_input_bytes
    def budget(system: str, message_bytes: int) -> dict:
        return {"model": model, "input_tokens": len(_clinical_system(system).encode("utf-8")) + message_bytes + 4096,
                "max_output_tokens": max_output}
    budgets = [budget(specialist_prompt(key), context_bytes) for key in agent_keys]
    specialists = [key for key in agent_keys if key not in {"evidence", "red_team"}]
    # Original opinion plus two complete mandatory reviews; each has an enforced byte bound.
    budgets += [budget(contestation_prompt(key), base_bytes + 3 * envelope) for key in specialists]
    total_opinions = len(agent_keys) + len(specialists)
    # Coordinator receives each complete opinion once, including mandatory reviews.
    # Divergences are recoverable from the preserved claims and positions.
    budgets.append(budget(COORDINATOR_SYSTEM, base_bytes + total_opinions * (envelope + 256)))
    budgets.extend({"model": request["model"],
                    "input_tokens": input_token_bound(request, request["model"]) + 4096,
                    "max_output_tokens": int(request.get("max_completion_tokens", request.get("max_tokens", extract_output)))} for request in visual_requests)
    plan_token_budgets(provider_name, budgets)


def _enrich_visual_attachments(db, case: HeartTeamCase, descriptors: list[dict], provider) -> list[dict]:
    textual_report_present = any(str((item.get("objective_extract") or {}).get("text") or "").strip() for item in descriptors)
    candidates = _visual_candidates(descriptors)
    for descriptor in candidates:
        if not (settings.ai_clinical_multimodal_enabled and settings.ai_clinical_data_controls_approved):
            if not textual_report_present:
                raise HeartTeamSafetyError("ECG/imagem não pode ser ignorado. Habilite o multimodal clínico homologado ou anexe laudo textual/PDF.")
            continue
        binary = _visual_bytes(db, case, descriptor)
        if not binary:
            raise HeartTeamSafetyError("Arquivo visual não pôde ser lido com segurança.")
        instruction = VISUAL_INSTRUCTION
        ledger = _reserve_call(db, case, agent_key="multimodal_extractor", phase="attachment_extract", input_chars=len(instruction), media_bytes=len(binary))
        try:
            response = provider.analisar_arquivo_clinico(
                sistema=VISUAL_SYSTEM,
                instrucao=instruction, conteudo=binary, media_type=descriptor["media_type"],
                modelo=getattr(settings, "heart_team_clinical_model", "") or None,
                max_output_tokens=int(getattr(settings, "heart_team_max_output_tokens", 8192)),
            )
        except Exception as exc:
            case.reserved_cost_micros = max(0, int(case.reserved_cost_micros or 0) - ledger.reserved_micros); db.commit()
            if textual_report_present:
                descriptor["objective_extract"] = {**(descriptor.get("objective_extract") or {}), "multimodal_error": type(exc).__name__, "requires_medical_review": True}
                continue
            raise HeartTeamSafetyError("O provedor multimodal não conseguiu interpretar o formato; anexe um laudo textual/PDF.") from exc
        _reconcile_call(db, case, ledger, response)
        extract = _json_response(response.texto)
        _check_response_envelope(extract, output_tokens=int(getattr(settings, "heart_team_max_output_tokens", 8192)))
        if not isinstance(extract.get("objective_observations"), list):
            if not textual_report_present:
                raise HeartTeamSafetyError("Extração multimodal inválida; anexe um laudo textual/PDF.")
            continue
        objective = {**(descriptor.get("objective_extract") or {}), "multimodal_extract": extract, "multimodal_model": response.modelo, "requires_medical_review": True}
        descriptor["objective_extract"] = objective
        row = db.query(HeartTeamAttachment).filter(HeartTeamAttachment.id == descriptor["id"], HeartTeamAttachment.owner_id == case.owner_id).first()
        if row: row.objective_extract = objective
        db.commit()
    return descriptors


def analyze_case_by_id(db, *, case_id: int, owner_id: int, actor_id: int, confirm_deidentified: bool, confirm_medical_review: bool, origin: str = "internal_worker") -> HeartTeamCase:
    enabled()
    ensure_heart_team_physician(db, actor_id)
    case = db.query(HeartTeamCase).filter(HeartTeamCase.id == case_id, HeartTeamCase.owner_id == owner_id).with_for_update().first()
    if not case:
        raise HeartTeamError("Caso não encontrado.")
    if not confirm_deidentified or not confirm_medical_review:
        raise HeartTeamSafetyError("As duas confirmações médicas são obrigatórias.")
    now = utcnow(); case.deidentified_confirmed_at = now; case.medical_review_confirmed_at = now
    audit_event(db, case, actor_id=actor_id, action="analysis_confirmed", detail={"deidentified": True, "medical_review": True, "origin": origin}); db.commit()
    return HeartTeamOrchestrator(db).analyze(case, actor_id=actor_id)



def _budget_fingerprint(case: HeartTeamCase, attachments: list[dict]) -> str:
    return content_hash({
        "input": case.input_data or {}, "selected_agents": case.selected_agents,
        "model_config": heart_team_model_config(),
        "attachments": [{key: item.get(key) for key in ("id", "kind", "reference_id", "sha256", "source_sha256", "media_type", "size_bytes")} for item in attachments],
    })


def estimate_case_budget(db, case: HeartTeamCase, *, actor_id: int) -> dict:
    """Free, local estimate; persist only prices, hashes and expiry in audit."""
    from app.services.ai_wallet import quote_cost, wallet_summary
    from app.services.ia.usage_control import PRICING_VERSION, quote_scope
    if case.status != "draft":
        raise HeartTeamError("Somente rascunhos podem receber novo orçamento.")
    snapshot, missing = structure_case(case.input_data or {})
    if validate_deidentified(snapshot):
        raise HeartTeamSafetyError("Anonimize o caso antes de estimar a análise.")
    attachments = attachment_descriptors(db, case)
    fingerprint = _budget_fingerprint(case, attachments)
    key = _cache_key(case, snapshot, attachments, graph_fingerprint=_knowledge_graph_fingerprint(db))
    cached = _cache_get(db, case.owner_id, key)
    cache_hit = bool(cached and cached.get("schema") == "heart-team-cache-bundle-v2" and isinstance(cached.get("opinions"), list) and isinstance(cached.get("result"), dict))
    maximum_cost = 0
    if not cache_hit:
        rows = source_catalog(db, query=stable_json(snapshot), limit=int(getattr(settings, "heart_team_source_limit", 16)))
        context = {"case": snapshot, "missing_data": missing, "risk": emergency_screen(snapshot),
                   "attachments": attachments, "sources": sanitize_registry_for_persistence(rows)}
        # The worker reopens bibliography. Its abstracts never enter the model
        # context; allow extra bibliographic metadata without external HTTP here.
        with quote_scope(case.owner_id, "heart_team") as scope:
            _plan_journey(db, case, obter_provedor_heart_team(), context, selected_agent_keys(case.selected_agents),
                          extra_input_bytes=8192 * len(rows))
            maximum_cost = scope.planned_cost
    quoted = quote_cost(owner_id=case.owner_id, max_cost_micros=maximum_cost)
    detail = {
        "maximum_credit_centavos": quoted["maximum_credit_centavos"],
        "maximum_cost_micros": maximum_cost, "currency": "BRL",
        "pricing_version": PRICING_VERSION, "case_fingerprint": fingerprint,
        "expires_at": (utcnow() + timedelta(minutes=15)).isoformat(),
        "cache_hit": cache_hit, "model_config": heart_team_model_config(),
    }
    event = audit_event(db, case, actor_id=actor_id, action="cost_estimated", detail=detail)
    db.flush()
    quote_id = event.id
    db.commit()
    return {**detail, "quote_id": quote_id,
            "available_credit_centavos": wallet_summary(case.owner_id)["available_credit_centavos"]}


def _validate_budget_approval(db, case: HeartTeamCase, *, quote_id: int | None, approved_max_credit_centavos: int | None) -> dict:
    if not quote_id or approved_max_credit_centavos is None:
        raise HeartTeamError("Solicite e confirme o orçamento antes de iniciar o Heart Team.")
    quote = db.query(HeartTeamAuditEvent).filter(
        HeartTeamAuditEvent.id == quote_id, HeartTeamAuditEvent.case_id == case.id,
        HeartTeamAuditEvent.action == "cost_estimated").first()
    detail = dict(quote.detail or {}) if quote else {}
    try:
        expires = datetime.fromisoformat(detail["expires_at"])
        amount = detail["maximum_credit_centavos"]
    except (KeyError, ValueError, TypeError):
        raise HeartTeamError("Orçamento inválido; solicite uma nova estimativa.") from None
    from app.services.ia.usage_control import PRICING_VERSION
    if (expires <= utcnow() or detail.get("pricing_version") != PRICING_VERSION
            or isinstance(approved_max_credit_centavos, bool)
            or approved_max_credit_centavos != amount
            or detail.get("case_fingerprint") != _budget_fingerprint(case, attachment_descriptors(db, case))):
        raise HeartTeamError("O orçamento expirou ou o caso mudou; solicite uma nova estimativa.")
    return {"quote_id": quote_id, "approved_max_credit_centavos": amount,
            "pricing_version": detail["pricing_version"], "case_fingerprint": detail["case_fingerprint"]}


def _apply_accepted_budget(db, case: HeartTeamCase, attachments: list[dict]) -> None:
    from app.services.ia.usage_control import set_approved_credit_limit
    event = db.query(HeartTeamAuditEvent).filter(
        HeartTeamAuditEvent.case_id == case.id, HeartTeamAuditEvent.action == "analysis_queued"
    ).order_by(HeartTeamAuditEvent.id.desc()).first()
    detail = event.detail or {} if event else {}
    approval = detail.get("budget_approval") or {}
    if (approval.get("approved_max_credit_centavos") is None
            or approval.get("case_fingerprint") != _budget_fingerprint(case, attachments)):
        raise HeartTeamError("A análise exige confirmação de orçamento para este conteúdo.")
    set_approved_credit_limit(approval["approved_max_credit_centavos"])


def enqueue_analysis_job(db, *, case_id: int, owner_id: int, actor_id: int, confirm_deidentified: bool, confirm_medical_review: bool, quote_id: int | None = None, approved_max_credit_centavos: int | None = None) -> HeartTeamAnalysisJob:
    """Queue exactly one durable analysis per case; never run models in HTTP."""
    enabled(); ensure_heart_team_physician(db, actor_id)
    if not confirm_deidentified or not confirm_medical_review:
        raise HeartTeamSafetyError("As duas confirmações médicas são obrigatórias.")
    case = db.query(HeartTeamCase).filter(HeartTeamCase.id == case_id, HeartTeamCase.owner_id == owner_id).with_for_update().first()
    if not case:
        raise HeartTeamError("Caso não encontrado.")
    existing = db.query(HeartTeamAnalysisJob).filter(HeartTeamAnalysisJob.case_id == case.id).first()
    if existing:
        return existing
    if case.status != "draft":
        raise HeartTeamError("Somente rascunho pode ser enfileirado para análise.")
    approval = _validate_budget_approval(db, case, quote_id=quote_id, approved_max_credit_centavos=approved_max_credit_centavos)
    now = utcnow()
    case.deidentified_confirmed_at = now; case.medical_review_confirmed_at = now; case.status = "queued"
    job = HeartTeamAnalysisJob(case_id=case.id, owner_id=owner_id, actor_id=actor_id, status="queued", next_attempt_at=now)
    db.add(job); db.flush()
    audit_event(db, case, actor_id=actor_id, action="analysis_queued", detail={"job_id": job.id, "deidentified": True, "medical_review": True, "budget_approval": approval})
    db.commit(); db.refresh(job)
    return job


def process_analysis_job(job_id: int) -> dict:
    """Worker entry point with fail-closed recovery and bounded state."""
    from app.core.db import SessionLocal
    db = SessionLocal()
    try:
        job = db.query(HeartTeamAnalysisJob).filter(HeartTeamAnalysisJob.id == job_id).with_for_update().first()
        if not job:
            return {"status": "not_found"}
        if job.status != "queued":
            return {"status": job.status, "case_id": job.case_id}
        job.status = "running"; job.attempts += 1; job.started_at = utcnow(); db.commit()
        try:
            case = analyze_case_by_id(db, case_id=job.case_id, owner_id=job.owner_id, actor_id=job.actor_id, confirm_deidentified=True, confirm_medical_review=True, origin="heart_team_worker")
        except Exception as exc:
            db.rollback()
            job = db.query(HeartTeamAnalysisJob).filter(HeartTeamAnalysisJob.id == job_id).with_for_update().first()
            job.status = "failed"; job.last_error_code = type(exc).__name__[:80]; job.completed_at = utcnow()
            failed_case = db.query(HeartTeamCase).filter(HeartTeamCase.id == job.case_id, HeartTeamCase.owner_id == job.owner_id).with_for_update().first()
            if failed_case:
                failed_case.status = "failed"; failed_case.result = {}; failed_case.reserved_cost_micros = 0; failed_case.finished_at = utcnow()
                audit_event(db, failed_case, actor_id=job.actor_id, action="analysis_job_failed", detail={"job_id": job.id, "error_code": job.last_error_code})
            db.commit()
            return {"status": "failed", "case_id": job.case_id, "error_code": job.last_error_code}
        job = db.query(HeartTeamAnalysisJob).filter(HeartTeamAnalysisJob.id == job_id).with_for_update().first()
        job.status = "completed"; job.completed_at = utcnow(); db.commit()
        return {"status": "completed", "case_id": case.id, "case_status": case.status}
    finally:
        db.close()


def process_pending_analysis_jobs(limit: int = 2) -> dict:
    """Recover safe leases and process queued cases outside request workers."""
    if not settings.heart_team_enabled:
        return {"status": "feature_disabled", "processed": []}
    from app.core.db import SessionLocal
    db = SessionLocal(); now = utcnow(); lease = now - timedelta(minutes=30)
    try:
        stale = db.query(HeartTeamAnalysisJob).filter(HeartTeamAnalysisJob.status == "running", HeartTeamAnalysisJob.updated_at <= lease).all()
        for job in stale:
            case = db.query(HeartTeamCase).filter(HeartTeamCase.id == job.case_id).first()
            if case and case.status == "queued":
                job.status = "queued"; job.last_error_code = "lease_recovered_pre_analysis"
            else:
                job.status = "failed"; job.last_error_code = "lease_lost_partial_quarantined"; job.completed_at = now
                if case: case.status = "failed"; case.result = {}; case.finished_at = now
        db.commit()
        ids = [row[0] for row in db.query(HeartTeamAnalysisJob.id).filter(HeartTeamAnalysisJob.status == "queued", HeartTeamAnalysisJob.next_attempt_at <= now).order_by(HeartTeamAnalysisJob.id).limit(limit).all()]
    finally:
        db.close()
    return {"processed": [process_analysis_job(job_id) for job_id in ids]}


class HeartTeamOrchestrator:
    def __init__(self, db, provider=None):
        self.db = db; self.provider = provider

    def _restore_cache(self, case: HeartTeamCase, *, actor_id: int, key: str) -> bool:
        cached = _cache_get(self.db, case.owner_id, key)
        if not cached or cached.get("schema") != "heart-team-cache-bundle-v2" or not isinstance(cached.get("opinions"), list) or not isinstance(cached.get("result"), dict):
            return False
        case.result = cached["result"]
        case.model_versions = dict(cached.get("model_versions") or {})
        _materialize_cached_opinions(self.db, case, cached["opinions"])
        case.status = "awaiting_review"; case.finished_at = utcnow()
        _materialize_suggestions(self.db, case, case.result)
        audit_event(self.db, case, actor_id=actor_id, action="cache_hit", detail={"cache_key": key, "opinion_hashes": [item.get("content_hash") for item in cached["opinions"]], "model_versions": case.model_versions})
        self.db.commit()
        return True

    @ai_operation("heart_team", owner="case.owner_id")
    def analyze(self, case: HeartTeamCase, *, actor_id: int) -> HeartTeamCase:
        enabled()
        _enforce_case_limits(self.db, case)
        snapshot, missing = structure_case(case.input_data or {})
        pii = validate_deidentified(snapshot)
        if pii:
            case.status = "failed"; audit_event(self.db, case, actor_id=actor_id, action="pii_blocked", detail={"identifier_types": pii}); self.db.commit(); raise HeartTeamSafetyError("Identificadores detectados; anonimize os dados antes da análise.")
        case.structured_case = snapshot; case.missing_data = missing; case.risk_classification = emergency_screen(snapshot); case.started_at = utcnow(); case.status = "analyzing"; self.db.commit()
        provider = self.provider or obter_provedor_heart_team()
        attachments = attachment_descriptors(self.db, case)
        _apply_accepted_budget(self.db, case, attachments)
        key = _cache_key(case, snapshot, attachments, graph_fingerprint=_knowledge_graph_fingerprint(self.db)); case.input_hash = key; self.db.commit()
        purge_expired_cache(self.db)
        if self._restore_cache(case, actor_id=actor_id, key=key):
            return case

        registry_rows = verify_source_rows(source_catalog(self.db, query=stable_json(snapshot), limit=int(getattr(settings, "heart_team_source_limit", 16))))
        registry = {row["id"]: row for row in registry_rows}
        context = {"case": snapshot, "missing_data": missing, "risk": case.risk_classification, "attachments": attachments, "sources": sanitize_registry_for_persistence(registry_rows)}
        opinions: list[dict] = []
        try:
            agent_keys = selected_agent_keys(case.selected_agents)
            _plan_journey(self.db, case, provider, context, agent_keys)
            attachments = _enrich_visual_attachments(self.db, case, attachments, provider)
            context["attachments"] = attachments
            enriched_key = _cache_key(case, snapshot, attachments, graph_fingerprint=_knowledge_graph_fingerprint(self.db))
            case.input_hash = enriched_key
            if enriched_key != key and self._restore_cache(case, actor_id=actor_id, key=enriched_key):
                return case
            key = enriched_key
            isolated = independent_round_inputs(context, agent_keys)
            for agent_key in agent_keys:
                opinions.append(_call(self.db, case, provider=provider, agent_key=agent_key, round_name="independent", system=specialist_prompt(agent_key), message=isolated[agent_key], registry=registry))
            mandatory_first = {o["agent_key"]: o["content"] for o in opinions}
            if any(not mandatory_opinion_usable(key, mandatory_first.get(key, {})) for key in ("evidence", "red_team")):
                case.status = "unusable"; case.result = {}; case.finished_at = utcnow(); audit_event(self.db, case, actor_id=actor_id, action="mandatory_agent_unusable", detail={"agents": ["evidence", "red_team"]}); self.db.commit(); return case
            objections = {"red_team": mandatory_first["red_team"], "evidence": mandatory_first["evidence"]}
            contestations = []
            for agent_key in [key for key in agent_keys if key not in {"evidence", "red_team"}]:
                contestations.append(_call(self.db, case, provider=provider, agent_key=agent_key, round_name="contestation", system=contestation_prompt(agent_key), message={"original": mandatory_first.get(agent_key), "objections": objections, "case": snapshot, "sources": context["sources"]}, registry=registry))
            all_for_consensus = opinions + contestations
            coordinator = _call(self.db, case, provider=provider, agent_key="coordinator", round_name="consensus", system=COORDINATOR_SYSTEM, message=_consensus_message(snapshot, all_for_consensus, context["sources"]), registry=registry)
            if not mandatory_opinion_usable("coordinator", coordinator["content"]):
                case.status = "unusable"; case.result = {}; case.finished_at = utcnow(); audit_event(self.db, case, actor_id=actor_id, action="coordinator_unusable"); self.db.commit(); return case
        except HeartTeamBudgetExceeded:
            case.status = "failed"; case.result = {}; case.reserved_cost_micros = 0; case.finished_at = utcnow(); audit_event(self.db, case, actor_id=actor_id, action="cost_limit_blocked"); self.db.commit(); raise
        except Exception as exc:
            case.status = "failed"; case.result = {}; case.reserved_cost_micros = 0; case.finished_at = utcnow(); audit_event(self.db, case, actor_id=actor_id, action="analysis_failed", detail={"error_type": type(exc).__name__}); self.db.commit(); raise

        c = coordinator["content"]
        disagreements = deterministic_disagreements(all_for_consensus)
        result = {
            "case_summary": c.get("summary", "evidência insuficiente"), "alerts": c.get("alerts", []),
            "differential_diagnoses": c.get("differential_diagnoses", []), "missing_data": missing,
            "additional_tests": c.get("additional_tests", []), "therapeutic_options": c.get("therapeutic_options", []),
            "safety": c.get("safety", []), "individual_opinions": opinions, "contestations": contestations,
            "divergences": disagreements or c.get("divergences", []), "final_consensus": c.get("final_consensus") or c.get("summary"),
            "confidence": c.get("confidence", "insufficient"), "limitations": c.get("limitations", []),
            "evidence_review": objections["evidence"], "red_team_objections": objections["red_team"],
            "sources": context["sources"], "human_decisions": HUMAN_ONLY,
            "related_content": resolve_related_content(self.db, context["sources"]),
            # aliases retained for existing clients
            "differentials": c.get("differential_diagnoses", []), "tests": c.get("additional_tests", []),
            "interactions": c.get("safety", []), "summary": c.get("summary"), "disagreements": disagreements,
            "human_only_decisions": HUMAN_ONLY,
        }
        case.result = result; case.status = "awaiting_review"; case.finished_at = utcnow(); case.reserved_cost_micros = 0
        _materialize_suggestions(self.db, case, result)
        audit_event(self.db, case, actor_id=actor_id, action="analysis_awaiting_review", detail={"model_versions": case.model_versions, "sources": [s["id"] for s in context["sources"]]})
        self.db.commit()
        cache_opinions = opinions + contestations + [coordinator]
        _cache_put(self.db, case.owner_id, key, {"schema": "heart-team-cache-bundle-v2", "result": result, "opinions": cache_opinions, "model_versions": dict(case.model_versions or {})})
        self.db.refresh(case); return case


def usage_summary(db, owner_id: int) -> dict:
    from app.services.ai_wallet import wallet_summary
    start = utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    base = db.query(HeartTeamCase).filter(HeartTeamCase.owner_id == owner_id, HeartTeamCase.created_at >= start)
    return {
        "month_start": start.isoformat(), "cases": base.count(),
        "awaiting_review": base.filter(HeartTeamCase.status == "awaiting_review").count(),
        "completed": base.filter(HeartTeamCase.status == "completed").count(),
        "unusable": base.filter(HeartTeamCase.status == "unusable").count(),
        "accounting": "shared_ai_wallet",
        "wallet": wallet_summary(owner_id),
        "legacy_accounting": {
            "informational_only": True,
            "estimated_cost_micros": _monthly_spend(db, owner_id),
            "reserved_cost_micros": int(base.with_entities(func.coalesce(func.sum(HeartTeamCase.reserved_cost_micros), 0)).scalar() or 0),
        },
    }
