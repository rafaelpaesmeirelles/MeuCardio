"""Pure Heart Team budget regressions; run with pytest --noconftest."""
from types import SimpleNamespace
from io import BytesIO

import pytest
from PIL import Image

from app.services import heart_team as ht
from app.services.ia import usage_control as accounting
from app.services.ia.provedor import ProvedorOpenAI


@pytest.fixture
def context():
    return {"case": {"question": "Discussão de insuficiência cardíaca"}, "missing_data": [],
            "risk": {}, "attachments": [], "sources": []}


@pytest.fixture
def capture_plan(monkeypatch):
    result = []
    monkeypatch.setattr(ht, "plan_token_budgets", lambda provider, budgets: result.extend(budgets))
    monkeypatch.setattr(ht.settings, "heart_team_clinical_model", "gpt-4o-mini")
    monkeypatch.setattr(ht.settings, "heart_team_ai_provider", "openai")
    monkeypatch.setattr(ht.settings, "heart_team_max_output_tokens", 2200)
    monkeypatch.setattr(ht.settings, "ai_provider", "openai")
    return result


def test_journey_reserves_all_rounds_and_scales_with_selected_agents(context, capture_plan):
    provider = SimpleNamespace(_modelo="gpt-4o-mini")
    selected = ht.selected_agent_keys(["imaging"])
    ht._plan_journey(None, SimpleNamespace(owner_id=42), provider, context, selected)
    assert len(capture_plan) == 2 * len(selected) - 1 == 5
    assert all(row["model"] == "gpt-4o-mini" for row in capture_plan)
    assert all(row["max_output_tokens"] == 2200 for row in capture_plan)
    first_cost = sum(accounting.cost_micros(**{
        "model": row["model"], "input_tokens": row["input_tokens"],
        "output_tokens": row["max_output_tokens"]}) for row in capture_plan)
    assert 0 < first_cost < 10_000_000
    capture_plan.clear()
    selected = ht.selected_agent_keys(None)
    ht._plan_journey(None, SimpleNamespace(owner_id=42), provider, context, selected)
    assert len(capture_plan) == 13
    assert sum(accounting.cost_micros(row["model"], row["input_tokens"], row["max_output_tokens"])
               for row in capture_plan) > first_cost


def test_visual_default_and_fallback_are_in_same_preflight(context, capture_plan, monkeypatch):
    stream = BytesIO()
    Image.new("RGB", (800, 600)).save(stream, format="PNG")
    monkeypatch.setattr(ht, "_visual_bytes", lambda *args: stream.getvalue())
    monkeypatch.setattr(ht.settings, "ai_clinical_multimodal_enabled", True)
    monkeypatch.setattr(ht.settings, "ai_clinical_data_controls_approved", True)
    provider = object.__new__(ProvedorOpenAI)
    provider._modelo = "gpt-4o-mini"
    monkeypatch.setattr(ht.settings, "heart_team_clinical_model", "gpt-5.6-sol")
    context["attachments"] = [{"id": 1, "media_type": "image/png", "objective_extract": {}}]
    ht._plan_journey(None, SimpleNamespace(owner_id=42), provider, context, ht.selected_agent_keys(["imaging"]))
    assert len(capture_plan) == 9
    assert [row["model"] for row in capture_plan[-4:]] == ["gpt-5.6-sol", "gpt-5.6-sol", "gpt-4o", "gpt-4o"]
    assert all(row["max_output_tokens"] == 2200 for row in capture_plan[-4:])
    assert all(row["input_tokens"] > 4096 for row in capture_plan[-4:])


def _orchestrator_stubs(monkeypatch, cached=None):
    db = SimpleNamespace(commit=lambda: None, refresh=lambda row: None)
    case = SimpleNamespace(id=7, owner_id=42, input_data={"question": "Teste"},
                           selected_agents=["imaging"], reserved_cost_micros=0)
    monkeypatch.setattr(ht, "enabled", lambda: None)
    monkeypatch.setattr(ht, "_enforce_case_limits", lambda *args: None)
    monkeypatch.setattr(ht, "validate_deidentified", lambda *args: [])
    monkeypatch.setattr(ht, "attachment_descriptors", lambda *args: [])
    monkeypatch.setattr(ht, "_apply_accepted_budget", lambda *args: None)
    monkeypatch.setattr(ht, "_knowledge_graph_fingerprint", lambda *args: "test")
    monkeypatch.setattr(ht, "purge_expired_cache", lambda *args: None)
    monkeypatch.setattr(ht, "_cache_get", lambda *args: cached)
    monkeypatch.setattr(ht, "source_catalog", lambda *args, **kwargs: [])
    monkeypatch.setattr(ht, "verify_source_rows", lambda rows: rows)
    monkeypatch.setattr(ht, "audit_event", lambda *args, **kwargs: None)
    monkeypatch.setattr(ht, "_materialize_cached_opinions", lambda *args: None)
    monkeypatch.setattr(ht, "_materialize_suggestions", lambda *args: None)
    return db, case


def test_insufficient_journey_budget_stops_before_visual_or_text_calls(monkeypatch):
    db, case = _orchestrator_stubs(monkeypatch)
    observed = []
    def reject(*args):
        scope = accounting._scope.get()
        assert scope.owner_id == 42 and scope.feature == "heart_team"
        observed.append("preflight")
        raise accounting.AIUsageError("Saldo insuficiente")
    monkeypatch.setattr(ht, "_plan_journey", reject)
    monkeypatch.setattr(ht, "_enrich_visual_attachments", lambda *args: pytest.fail("paid visual started"))
    provider = SimpleNamespace(responder=lambda **kwargs: pytest.fail("paid text started"))
    with pytest.raises(accounting.AIUsageError):
        ht.HeartTeamOrchestrator(db, provider).analyze(case, actor_id=99)
    assert observed == ["preflight"]
    assert case.status == "failed" and case.result == {}
    assert accounting._scope.get() is None


def test_cached_journey_does_not_reserve_or_generate(monkeypatch):
    cached = {"schema": "heart-team-cache-bundle-v2", "opinions": [],
              "result": {"summary": "Revisão anterior"}, "model_versions": {}}
    db, case = _orchestrator_stubs(monkeypatch, cached)
    monkeypatch.setattr(ht, "_plan_journey", lambda *args: pytest.fail("cache must not reserve"))
    monkeypatch.setattr(ht, "_enrich_visual_attachments", lambda *args: pytest.fail("cache must not generate"))
    result = ht.HeartTeamOrchestrator(db, object()).analyze(case, actor_id=99)
    assert result.result == cached["result"]
    assert result.status == "awaiting_review"


def test_structural_output_bound_uses_utf8_and_never_truncates():
    accepted = {"summary": "Conclusão objetiva"}
    ht._check_response_envelope(accepted)
    assert accepted == {"summary": "Conclusão objetiva"}
    oversized = {"summary": "á" * ht._response_envelope_limit()}
    with pytest.raises(ht.HeartTeamSafetyError):
        ht._check_response_envelope(oversized)


def test_provider_typeerror_is_not_retried_without_output_cap(monkeypatch):
    calls = []
    def fail(**kwargs):
        calls.append(kwargs)
        raise TypeError("post-provider failure")
    provider = SimpleNamespace(responder=fail)
    db = SimpleNamespace(commit=lambda: None)
    case = SimpleNamespace(reserved_cost_micros=11)
    monkeypatch.setattr(ht, "_reserve_call", lambda *args, **kwargs: SimpleNamespace(reserved_micros=11))
    with pytest.raises(TypeError):
        ht._call(db, case, provider=provider, agent_key="imaging", round_name="independent",
                 system="system", message={}, registry={})
    assert len(calls) == 1 and calls[0]["max_output_tokens"] > 0
    assert case.reserved_cost_micros == 0

def test_visual_enrichment_still_reuses_existing_deliberation_cache(monkeypatch):
    cached = {"schema": "heart-team-cache-bundle-v2", "opinions": [],
              "result": {"summary": "Parecer em cache"}, "model_versions": {}}
    db, case = _orchestrator_stubs(monkeypatch)
    events = []
    def get_cache(*args):
        events.append("cache")
        return cached if events.count("cache") == 2 else None
    monkeypatch.setattr(ht, "_cache_get", get_cache)
    monkeypatch.setattr(ht, "_plan_journey", lambda *args: events.append("plan"))
    monkeypatch.setattr(ht, "_enrich_visual_attachments", lambda *args: [{"sha256": "enriched"}])
    monkeypatch.setattr(ht, "_call", lambda *args, **kwargs: pytest.fail("cached deliberation regenerated"))
    result = ht.HeartTeamOrchestrator(db, object()).analyze(case, actor_id=99)
    assert events == ["cache", "plan", "cache"]
    assert result.result == cached["result"]

def test_local_quote_does_not_call_models_or_external_verification(monkeypatch):
    from app.services import ai_wallet
    db, case = _orchestrator_stubs(monkeypatch)
    db.flush = lambda: None
    case.status = "draft"
    recorded = []
    monkeypatch.setattr(ht, "obter_provedor_heart_team", lambda: SimpleNamespace(_modelo="gpt-4o-mini"))
    monkeypatch.setattr(ht, "verify_source_rows", lambda rows: pytest.fail("quote must remain local"))
    monkeypatch.setattr(ai_wallet, "reserve", lambda **kwargs: pytest.fail("quote must not reserve"))
    monkeypatch.setattr(ai_wallet, "quote_cost", lambda **kwargs: {
        "maximum_credit_centavos": (kwargs["max_cost_micros"] * 4 + 9999) // 10000,
        "currency": "BRL", "pricing_version": "test"})
    monkeypatch.setattr(ai_wallet, "wallet_summary", lambda owner: {"available_credit_centavos": 4000})
    def audit(*args, **kwargs):
        recorded.append(kwargs)
        return SimpleNamespace(id=11)
    monkeypatch.setattr(ht, "audit_event", audit)
    quote = ht.estimate_case_budget(db, case, actor_id=42)
    assert quote["quote_id"] == 11 and quote["maximum_credit_centavos"] > 0
    assert quote["model_config"]["model"] == ht.settings.heart_team_clinical_model
    assert quote["available_credit_centavos"] == 4000
    assert recorded[0]["action"] == "cost_estimated"
    assert "question" not in recorded[0]["detail"]
    assert accounting._scope.get() is None


@pytest.mark.parametrize("change", ["amount", "expired", "content"])
def test_quote_approval_rejects_modified_amount_expiry_or_case(monkeypatch, change):
    case = SimpleNamespace(id=7, owner_id=42, input_data={"question": "Original"}, selected_agents=["imaging"])
    monkeypatch.setattr(ht, "attachment_descriptors", lambda *args: [])
    detail = {"maximum_credit_centavos": 100, "pricing_version": accounting.PRICING_VERSION,
              "expires_at": (ht.utcnow() + ht.timedelta(minutes=15)).isoformat(),
              "case_fingerprint": ht._budget_fingerprint(case, [])}
    amount = 100
    if change == "amount":
        amount = 99
    elif change == "expired":
        detail["expires_at"] = (ht.utcnow() - ht.timedelta(seconds=1)).isoformat()
    else:
        case.input_data = {"question": "Changed"}
    query = SimpleNamespace()
    query.filter = lambda *args: query
    query.first = lambda: SimpleNamespace(detail=detail)
    db = SimpleNamespace(query=lambda *args: query)
    with pytest.raises(ht.HeartTeamError, match="orçamento"):
        ht._validate_budget_approval(db, case, quote_id=9, approved_max_credit_centavos=amount)


def test_worker_restores_accepted_credit_ceiling_from_immutable_audit(monkeypatch):
    case = SimpleNamespace(id=7, owner_id=42, input_data={"question": "Original"}, selected_agents=["imaging"])
    approval = {"approved_max_credit_centavos": 123, "case_fingerprint": ht._budget_fingerprint(case, [])}
    query = SimpleNamespace()
    query.filter = lambda *args: query
    query.order_by = lambda *args: query
    query.first = lambda: SimpleNamespace(detail={"budget_approval": approval})
    db = SimpleNamespace(query=lambda *args: query)
    with accounting.ai_usage_scope(42, "heart_team") as scope:
        ht._apply_accepted_budget(db, case, [])
        assert scope.approved_credit_centavos == 123

@pytest.mark.parametrize("canonical_status", [None, "failed", "running"])
def test_whatsapp_cannot_start_unapproved_or_repeat_failed_analysis(monkeypatch, canonical_status):
    from app.services import whatsapp_jobs
    case = SimpleNamespace(id=7, owner_id=42, status="analyzing")
    canonical = None if canonical_status is None else SimpleNamespace(id=10, status=canonical_status, last_error_code="failed_once")
    query = SimpleNamespace()
    query.filter = lambda *args: query
    query.first = lambda: canonical
    db = SimpleNamespace(query=lambda *args: query)
    monkeypatch.setattr(ht, "process_analysis_job", lambda job: pytest.fail("must not rerun"))
    result = whatsapp_jobs._advance_heart_team_case(db, case)
    assert result["status"] == ("retry" if canonical_status == "running" else "failed")


def test_whatsapp_processes_only_canonical_approved_job_once(monkeypatch):
    from app.services import whatsapp_jobs
    case = SimpleNamespace(id=7, owner_id=42, status="queued")
    canonical = SimpleNamespace(id=10, status="queued", last_error_code=None)
    query = SimpleNamespace()
    query.filter = lambda *args: query
    query.first = lambda: canonical
    db = SimpleNamespace(query=lambda *args: query, refresh=lambda row: None)
    calls = []
    def process(job):
        calls.append(job)
        case.status = "awaiting_review"
        canonical.status = "completed"
    monkeypatch.setattr(ht, "process_analysis_job", process)
    assert whatsapp_jobs._advance_heart_team_case(db, case) == {"status": "ready"}
    assert whatsapp_jobs._advance_heart_team_case(db, case) == {"status": "ready"}
    assert calls == [10]
