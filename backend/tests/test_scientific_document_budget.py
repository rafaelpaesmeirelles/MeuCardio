"""Document quotes exercise the real planner with fake storage/wallet; no paid API."""
import asyncio
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from app.api import scientific_documents_ai as api
from app.services.ia import usage_control as usage


@pytest.fixture(autouse=True)
def _banco_limpo():
    yield


@pytest.fixture
def env(monkeypatch):
    row = SimpleNamespace(id=8, owner_id=7, sha256="file-digest", storage_key="private",
                          media_type="text/plain", analysis_status="pendente")
    user = SimpleNamespace(id=7)
    db = SimpleNamespace(add=Mock(), flush=Mock(), commit=Mock())
    db.flush.side_effect = lambda: setattr(db.add.call_args.args[0], "id", 91)
    monkeypatch.setattr(api, "_row_for_user", lambda *a, **kw: row)
    monkeypatch.setattr(api.cofre, "ler", lambda *a, **kw: b"original")
    monkeypatch.setattr(api.engine, "extract_text", lambda *a: "Document in English")
    monkeypatch.setattr(api.engine, "_model", lambda: "gpt-4o-mini")
    reserve, settle = Mock(), Mock()
    monkeypatch.setattr(api.ai_wallet, "reserve", reserve)
    monkeypatch.setattr(api.ai_wallet, "settle", settle)
    monkeypatch.setattr(api.ai_wallet, "quote_cost", lambda **kw: {"maximum_credit_centavos": 123})
    monkeypatch.setattr(api.ai_wallet, "wallet_summary", lambda *a: {"available_credit_centavos": 4000})
    analyze = Mock(side_effect=AssertionError("Quote must never call AI"))
    translate = Mock(side_effect=AssertionError("Quote must never translate"))
    monkeypatch.setattr(api.engine, "analyze_text", analyze)
    monkeypatch.setattr(api.engine, "translate_full_text", translate)
    return SimpleNamespace(row=row, user=user, db=db, reserve=reserve, settle=settle,
                           analyze=analyze, translate=translate)


def quoted_event(env):
    result = asyncio.run(api.estimate_document(8, env.db, env.user))
    event = env.db.add.call_args.args[0]
    return result, event


def approval_db(event, *, used=False):
    query = Mock()
    query.filter.return_value.first.side_effect = [event, object() if used else None]
    return SimpleNamespace(query=Mock(return_value=query))


def test_document_estimate_is_free_and_uses_exact_analysis_translation_plan(env):
    result, event = quoted_event(env)
    with usage.quote_scope(7, "scientific_document_ai") as scope:
        planned = api.engine.plan_document("Document in English")
        assert planned == scope.planned_cost == event.detail["maximum_cost_micros"]
    assert result["quote_id"] == 91
    assert result["maximum_credit_centavos"] == 123
    assert result["available_credit_centavos"] == 4000
    assert result["includes_translation"] is True
    assert "Document in English" not in str(event.detail)
    env.analyze.assert_not_called(); env.translate.assert_not_called()
    env.reserve.assert_not_called(); env.settle.assert_not_called()


def test_valid_document_approval_applies_exact_credit_ceiling(env):
    _, event = quoted_event(env)
    approval = api.DocumentBudgetApproval(quote_id=91, approved_max_credit_centavos=123)
    with usage.ai_usage_scope(7, "scientific_document_ai") as scope:
        api._validate_document_budget(approval_db(event), env.row, env.user, approval,
                                      "Document in English", event.detail["maximum_cost_micros"])
        assert scope.approved_credit_centavos == 123
    env.reserve.assert_not_called()


@pytest.mark.parametrize("change", ["expired", "content", "model", "amount", "cost", "foreign_quote", "replayed"])
def test_changed_expired_foreign_or_replayed_quote_blocks_before_ai(env, monkeypatch, change):
    _, event = quoted_event(env)
    amount, text, cost = 123, "Document in English", event.detail["maximum_cost_micros"]
    if change == "expired": event.detail["expires_at"] = (datetime.now(timezone.utc)-timedelta(seconds=1)).isoformat()
    if change == "content": text += " modified"
    if change == "model": monkeypatch.setattr(api.engine, "_model", lambda: "gpt-4o")
    if change == "amount": amount = 122
    if change == "cost": cost += 1
    db = approval_db(None if change == "foreign_quote" else event, used=change == "replayed")
    approval = api.DocumentBudgetApproval(quote_id=91, approved_max_credit_centavos=amount)
    with usage.ai_usage_scope(7, "scientific_document_ai"), pytest.raises(HTTPException) as error:
        api._validate_document_budget(db, env.row, env.user, approval, text, cost)
    assert error.value.status_code == 409
    env.reserve.assert_not_called(); env.analyze.assert_not_called()


def test_analyze_rejects_wrong_quote_before_changing_status(env, monkeypatch):
    query = Mock()
    query.filter.return_value.first.return_value = None
    env.db.query = Mock(return_value=query)
    approval = api.DocumentBudgetApproval(quote_id=91, approved_max_credit_centavos=123)
    with pytest.raises(HTTPException) as error:
        asyncio.run(api.analyze_document(8, approval, env.db, env.user))
    assert error.value.status_code == 409
    assert env.row.analysis_status == "pendente"
    env.analyze.assert_not_called(); env.reserve.assert_not_called()
    env.db.commit.assert_not_called()


def test_document_approval_rejects_boolean_or_negative_credit():
    for value in (True, -1, "123"):
        with pytest.raises(ValidationError):
            api.DocumentBudgetApproval(quote_id=91, approved_max_credit_centavos=value)
    assert api.DocumentBudgetApproval(quote_id=91, approved_max_credit_centavos=0).approved_max_credit_centavos == 0


def test_document_approved_scope_survives_awaited_threadpool_and_settles_once(env, monkeypatch):
    _, event = quoted_event(env)
    env.db.query = approval_db(event).query
    env.reserve.return_value = {"created": True, "reserved_credit_micros": 123 * 10_000}
    network = Mock(return_value=SimpleNamespace(usage=SimpleNamespace(prompt_tokens=20, completion_tokens=10)))
    client = usage.MeteredSDK(SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=network))), "openai")
    def analyze_in_worker(text):
        current = usage._scope.get()
        assert current.owner_id == 7
        assert current.approved_credit_centavos == 123
        client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": text}], max_tokens=100)
        return {"title": "Private title", "needs_translation": False, "adds_to_corvia": False}
    monkeypatch.setattr(api.engine, "analyze_text", analyze_in_worker)
    monkeypatch.setattr(api.engine, "find_duplicate", lambda *a: None)
    monkeypatch.setattr(api.engine, "has_traceable_source", lambda *a: False)
    monkeypatch.setattr(api.cofre, "cifrar_campo", lambda value, owner: b"encrypted")
    monkeypatch.setattr(api, "_dump", lambda row, **kw: {"analysis_status": row.analysis_status})
    approval = api.DocumentBudgetApproval(quote_id=91, approved_max_credit_centavos=123)
    result = asyncio.run(api.analyze_document(8, approval, env.db, env.user))
    assert result["analysis_status"] == "concluido"
    assert network.call_count == env.reserve.call_count == env.settle.call_count == 1
    assert env.settle.call_args.kwargs["tokens_input"] == 20
    assert env.settle.call_args.kwargs["tokens_output"] == 10
    assert env.db.add.call_args_list[-2].args[0].detail["quote_id"] == 91
