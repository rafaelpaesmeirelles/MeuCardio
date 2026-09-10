"""Dedicated frontier Heart Team selection and truthful bounded preflight; no network."""
from types import SimpleNamespace
import json
import pytest

from app.services import heart_team as ht
from app.services.ia import provedor
from app.services.ia import usage_control as accounting


@pytest.fixture(autouse=True)
def dedicated_settings(monkeypatch):
    monkeypatch.setattr(ht.settings, "heart_team_ai_provider", "openai")
    monkeypatch.setattr(ht.settings, "heart_team_clinical_model", "gpt-5.6-sol")
    monkeypatch.setattr(ht.settings, "heart_team_max_output_tokens", 8192)
    monkeypatch.setattr(ht.settings, "heart_team_reasoning_effort", "medium")
    monkeypatch.setattr(ht.settings, "ai_clinical_multimodal_enabled", False)


def test_factory_never_inherits_or_changes_general_chat(monkeypatch):
    global_provider = object()
    monkeypatch.setattr(provedor, "_cache", global_provider)
    monkeypatch.setattr(ht.settings, "ai_provider", "anthropic")
    monkeypatch.setattr(ht.settings, "openai_model", "gpt-4o-mini")
    class Dedicated:
        def __init__(self):
            self._modelo = ht.settings.openai_model
    monkeypatch.setattr(provedor, "ProvedorOpenAI", Dedicated)
    provider = ht.obter_provedor_heart_team()
    assert provider._modelo == "gpt-5.6-sol"
    assert provider._heart_team_provider_name == "openai"
    assert provedor._cache is global_provider
    assert ht.settings.openai_model == "gpt-4o-mini"


def test_preflight_and_actual_calls_use_dedicated_model_output_and_reasoning(monkeypatch):
    planned = []
    monkeypatch.setattr(ht.settings, "ai_provider", "anthropic")
    monkeypatch.setattr(ht, "plan_token_budgets", lambda p, b: planned.append((p, b)))
    context = {"case": {}, "sources": [], "attachments": [], "missing_data": [], "risk": {}}
    ht._plan_journey(None, SimpleNamespace(owner_id=42), SimpleNamespace(_modelo="gpt-4o-mini"),
                     context, ht.selected_agent_keys(["imaging"]))
    assert planned[0][0] == "openai"
    assert len(planned[0][1]) == 5
    assert all(b["model"] == "gpt-5.6-sol" and b["max_output_tokens"] == 8192 for b in planned[0][1])
    calls = []
    def responder(**kwargs):
        calls.append(kwargs)
        raise TypeError("stop after inspecting exact request")
    monkeypatch.setattr(ht, "_reserve_call", lambda *a, **k: SimpleNamespace(reserved_micros=0))
    with pytest.raises(TypeError):
        ht._call(SimpleNamespace(commit=lambda: None), SimpleNamespace(reserved_cost_micros=0),
                 provider=SimpleNamespace(responder=responder), agent_key="imaging",
                 round_name="independent", system="Clinical system", message={}, registry={})
    assert calls[0]["modelo"] == planned[0][1][0]["model"]
    assert calls[0]["max_output_tokens"] == 8192
    assert calls[0]["reasoning_effort"] == "medium"
    assert "32 KiB" in calls[0]["sistema"]


@pytest.mark.parametrize("setting,value", [
    ("heart_team_clinical_model", "gpt-4o"),
    ("heart_team_max_output_tokens", 16384),
    ("heart_team_reasoning_effort", "high"),
])
def test_worker_rejects_changed_model_configuration_after_approval(monkeypatch, setting, value):
    case = SimpleNamespace(id=9, owner_id=42, input_data={}, selected_agents=["imaging"])
    fingerprint = ht._budget_fingerprint(case, [])
    query = SimpleNamespace()
    query.filter = lambda *a: query
    query.order_by = lambda *a: query
    query.first = lambda: SimpleNamespace(detail={"budget_approval": {
        "approved_max_credit_centavos": 4000, "case_fingerprint": fingerprint}})
    monkeypatch.setattr(ht.settings, setting, value)
    monkeypatch.setattr(accounting, "set_approved_credit_limit", lambda *a: pytest.fail("stale approval"))
    with pytest.raises(ht.HeartTeamError, match="confirmação"):
        ht._apply_accepted_budget(SimpleNamespace(query=lambda *a: query), case, [])


def test_consensus_preserves_each_full_opinion_once_and_budget_covers_actual_shape(monkeypatch):
    planned = []
    monkeypatch.setattr(ht, "plan_token_budgets", lambda p, b: planned.extend(b))
    agents = ht.selected_agent_keys(None)
    context = {"case": {"question": "Review"}, "sources": [], "attachments": []}
    ht._plan_journey(None, None, SimpleNamespace(), context, agents)
    content = {"summary": "á\\\" " * 1000, "claims": [
        {"statement": "Important finding", "position": "oppose", "source_ids": ["s1"]}],
        "alerts": ["Must preserve"], "limitations": ["No invented conclusions"]}
    ht._check_response_envelope(content)
    opinions = [{"agent_key": agent, "round_name": phase, "content": content,
                 "position": {"claims": content["claims"]}, "tokens_input": 100, "id": 9}
                for phase, group in [("independent", agents), ("contestation", agents[:-2])]
                for agent in group]
    message = ht._consensus_message(context["case"], opinions, [])
    assert len(message["opinions"]) == len(opinions)
    assert all(row["content"] == content for row in message["opinions"])
    assert all(set(row) == {"agent_key", "round_name", "content"} for row in message["opinions"])
    assert "red_team" not in message and "deterministic_disagreements" not in message
    actual_request = {"model": "gpt-5.6-sol", "max_completion_tokens": 8192,
        "reasoning_effort": "medium", "messages": [
            {"role": "system", "content": ht._clinical_system(ht.COORDINATOR_SYSTEM)},
            {"role": "user", "content": ht.stable_json(message)}]}
    assert accounting.input_token_bound(actual_request, "gpt-5.6-sol") + 256 <= planned[-1]["input_tokens"]


def test_32kib_limit_is_independent_of_reasoning_budget_and_does_not_truncate(monkeypatch):
    content = {"summary": "x" * (32 * 1024)}
    before = json.dumps(content)
    assert ht._response_envelope_limit() == 32 * 1024
    with pytest.raises(ht.HeartTeamSafetyError):
        ht._check_response_envelope(content)
    assert json.dumps(content) == before
    monkeypatch.setattr(ht.settings, "heart_team_max_output_tokens", 32768)
    assert ht._response_envelope_limit() == 32 * 1024
