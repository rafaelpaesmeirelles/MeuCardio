"""Paid egress tests use fake providers and wallets; no database or API calls."""
from io import BytesIO
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from PIL import Image

from app.services import ai_wallet
from app.services.ia import usage_control as usage


@pytest.fixture(autouse=True)
def _banco_limpo():
    yield  # Override the integration suite's database fixture for this module.


@pytest.fixture(autouse=True)
def wallet(monkeypatch):
    fake = SimpleNamespace(
        reserve=Mock(return_value={"created": True, "state": "reserved"}),
        settle=Mock(), mark_unknown=Mock(), fail=Mock(),
    )
    for name in vars(fake):
        monkeypatch.setattr(ai_wallet, name, getattr(fake, name))
    return fake


def request(model="gpt-4o-mini", **extra):
    return {"model": model, "messages": [{"role": "user", "content": "Pergunta"}],
            "max_tokens": 200, **extra}


def response(inputs=20, outputs=5, **extra):
    return SimpleNamespace(usage=SimpleNamespace(prompt_tokens=inputs, completion_tokens=outputs), **extra)


def client_with_response(result=None):
    create = Mock(return_value=result or response())
    raw = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
    return usage.MeteredSDK(raw, "openai"), create


def test_no_account_and_unknown_model_never_reach_network(wallet):
    client, create = client_with_response()
    with pytest.raises(usage.AIUsageError):
        client.chat.completions.create(**request())
    with usage.ai_usage_scope(7):
        with pytest.raises(usage.AIUsageError):
            client.chat.completions.create(**request("unpriced-frontier"))
    create.assert_not_called()
    wallet.reserve.assert_not_called()


def test_budget_rejection_happens_before_provider(wallet):
    wallet.reserve.side_effect = usage.AIUsageError("Saldo insuficiente")
    client, create = client_with_response()
    with pytest.raises(usage.AIUsageError), usage.ai_usage_scope(7):
        client.chat.completions.create(**request())
    create.assert_not_called()


def test_single_request_reserves_only_quote_and_settles_measured_tokens(wallet):
    client, create = client_with_response(response(100, 10))
    with usage.ai_usage_scope(7):
        client.chat.completions.create(**request())
    assert wallet.reserve.call_args.kwargs["max_cost_micros"] < usage.BUDGETS["clinical_ai"]
    assert wallet.settle.call_args.kwargs["actual_cost_micros"] == usage.cost_micros("gpt-4o-mini", 100, 10)
    assert wallet.settle.call_args.kwargs["tokens_input"] == 100
    assert wallet.settle.call_args.kwargs["tokens_output"] == 10
    assert create.call_count == 1
    wallet.mark_unknown.assert_not_called()


def test_multistep_journey_reserves_once_and_includes_every_call(wallet):
    client, create = client_with_response(response(100, 10))
    with usage.ai_usage_scope(7, "scientific_document_ai"):
        usage.plan_requests("openai", [request(), request()])
        client.chat.completions.create(**request())
        client.chat.completions.create(**request())
    assert create.call_count == 2
    assert wallet.reserve.call_count == wallet.settle.call_count == 1
    assert wallet.settle.call_args.kwargs["tokens_input"] == 200
    assert wallet.settle.call_args.kwargs["actual_cost_micros"] == 2 * usage.cost_micros("gpt-4o-mini", 100, 10)


def test_provider_timeout_keeps_reservation_and_prevents_next_call(wallet):
    client, create = client_with_response()
    create.side_effect = TimeoutError("unknown outcome")
    with usage.ai_usage_scope(7):
        with pytest.raises(TimeoutError):
            client.chat.completions.create(**request())
        with pytest.raises(usage.AIUsageError):
            client.chat.completions.create(**request())
    assert create.call_count == 1
    wallet.settle.assert_not_called()
    wallet.mark_unknown.assert_called_once()


def test_explicit_validation_rejection_releases_without_charge(wallet):
    class Rejected(Exception):
        status_code = 400
    client, create = client_with_response()
    create.side_effect = Rejected()
    with usage.ai_usage_scope(7):
        with pytest.raises(Rejected):
            client.chat.completions.create(**request())
    assert wallet.settle.call_args.kwargs["actual_cost_micros"] == 0
    wallet.mark_unknown.assert_not_called()


def test_missing_usage_is_not_treated_as_free(wallet):
    client, create = client_with_response(SimpleNamespace(usage=None))
    with pytest.raises(usage.AIUsageError), usage.ai_usage_scope(7):
        client.chat.completions.create(**request())
    create.assert_called_once()
    wallet.mark_unknown.assert_called_once()
    wallet.settle.assert_not_called()


def test_interrupted_stream_preserves_reservation(wallet):
    raw_stream = iter([SimpleNamespace(usage=None, text="partial"),
                       SimpleNamespace(usage=SimpleNamespace(prompt_tokens=40, completion_tokens=10))])
    client, _ = client_with_response(raw_stream)
    with usage.ai_usage_scope(7):
        stream = client.chat.completions.create(**request(stream=True))
        next(stream)
        stream.close()
    wallet.mark_unknown.assert_called_once()
    wallet.settle.assert_not_called()


def test_complete_stream_settles_final_usage(wallet):
    raw_stream = iter([SimpleNamespace(usage=None),
                       SimpleNamespace(usage=SimpleNamespace(prompt_tokens=40, completion_tokens=10))])
    client, _ = client_with_response(raw_stream)
    with usage.ai_usage_scope(7):
        assert len(list(client.chat.completions.create(**request(stream=True)))) == 2
    assert wallet.settle.call_args.kwargs["tokens_input"] == 40
    wallet.mark_unknown.assert_not_called()


def test_inflight_requests_cannot_double_spend_same_reservation(wallet):
    with usage.ai_usage_scope(7):
        with usage.paid_request("openai", request()) as first:
            with pytest.raises(usage.AIUsageError):
                with usage.paid_request("openai", request()):
                    pytest.fail("A second concurrent request bypassed the reservation")
            first.finish({"input_tokens": 20, "output_tokens": 5})
    wallet.reserve.assert_called_once()


def test_actual_overrun_records_complete_liability(wallet):
    client, _ = client_with_response(response(1_000_000, 10))
    with pytest.raises(usage.AIUsageError), usage.ai_usage_scope(7):
        client.chat.completions.create(**request())
    assert wallet.settle.call_args.kwargs["actual_cost_micros"] == usage.cost_micros("gpt-4o-mini", 1_000_000, 10)
    wallet.mark_unknown.assert_not_called()


def test_image_tokens_use_dimensions_and_preserve_original_detail():
    image = BytesIO()
    Image.new("RGB", (1024, 1024)).save(image, format="PNG")
    assert usage.image_tokens(image.getvalue(), "gpt-5.6-sol", "original") == 1231
    assert usage.image_tokens(image.getvalue(), "gpt-4o", "high") == 765


def test_institutional_retrieval_is_separate_from_user_generation(wallet):
    client, _ = client_with_response()
    with usage.ai_usage_scope(7):
        with usage.ai_usage_scope(None, "retrieval", cost_center="retrieval"):
            client.chat.completions.create(**request())
        client.chat.completions.create(**request())
    calls = wallet.reserve.call_args_list
    assert [(c.kwargs["owner_id"], c.kwargs["cost_center"]) for c in calls] == [(None, "retrieval"), (7, None)]
    assert calls[0].kwargs["operation_key"] != calls[1].kwargs["operation_key"]


def test_duplicate_reservation_does_not_repeat_sdk(wallet):
    wallet.reserve.return_value = {"created": False, "state": "reserved"}
    client, create = client_with_response()
    with pytest.raises(usage.AIUsageError), usage.ai_usage_scope(7):
        client.chat.completions.create(**request())
    create.assert_not_called()


def test_generator_scope_is_created_in_consuming_worker(wallet):
    client, _ = client_with_response()
    @usage.ai_operation("clinical_ai")
    def generate(user):
        yield client.chat.completions.create(**request())
    values = list(generate(SimpleNamespace(id=71)))
    assert len(values) == 1
    assert wallet.reserve.call_args.kwargs["owner_id"] == 71


def test_transcription_cannot_escape_accounting(monkeypatch, wallet):
    monkeypatch.setattr(usage, "audio_duration", lambda *args: 60)
    create = Mock(return_value=SimpleNamespace(usage={"input_tokens": 1000, "output_tokens": 100}, text="Texto"))
    client = SimpleNamespace(audio=SimpleNamespace(transcriptions=SimpleNamespace(create=create)))
    with usage.ai_usage_scope(7, "whatsapp_ai"):
        result = usage.metered_transcription(client, model="gpt-4o-mini-transcribe", content=b"test", filename="audio.ogg", media_type="audio/ogg")
    assert result.text == "Texto"
    assert wallet.settle.call_args.kwargs["tokens_input"] == 1000
    create.assert_called_once()


def test_web_search_usage_is_included(wallet):
    create = Mock(return_value=SimpleNamespace(usage={"input_tokens": 100, "output_tokens": 10,
        "server_tool_use": {"web_search_requests": 1}}, content=[]))
    client = usage.MeteredSDK(SimpleNamespace(messages=SimpleNamespace(create=create)), "anthropic")
    with usage.ai_usage_scope(7, "scientific_document_ai"):
        client.messages.create(**request("claude-haiku-4-5", tools=[{"type": "web_search_20260209", "max_uses": 1}]))
    assert wallet.settle.call_args.kwargs["actual_cost_micros"] == usage.cost_micros("claude-haiku-4-5", 100, 10, 1)


def test_partial_success_before_timeout_is_persisted_without_releasing_hold(wallet):
    client, create = client_with_response()
    create.side_effect = [response(100, 10), TimeoutError("unknown")]
    with usage.ai_usage_scope(7, "scientific_document_ai"):
        usage.plan_requests("openai", [request(), request()])
        client.chat.completions.create(**request())
        with pytest.raises(TimeoutError):
            client.chat.completions.create(**request())
    partial = wallet.mark_unknown.call_args.kwargs
    assert partial["known_cost_micros"] == usage.cost_micros("gpt-4o-mini", 100, 10)
    assert partial["known_tokens_input"] == 100
    assert partial["known_tokens_output"] == 10
    wallet.settle.assert_not_called()


def test_quote_never_reserves_or_calls_provider_even_in_nested_service_scope(wallet):
    client, create = client_with_response()
    with usage.quote_scope(7, "heart_team") as quote:
        assert usage.plan_requests("openai", [request()]) > 0
        assert quote.planned_cost > 0
        with pytest.raises(usage.AIUsageError):
            client.chat.completions.create(**request())
        with usage.ai_usage_scope(None, "retrieval", cost_center="retrieval"):
            with pytest.raises(usage.AIUsageError):
                client.chat.completions.create(**request())
    create.assert_not_called()
    wallet.reserve.assert_not_called()


def test_changed_quote_and_zero_credit_approval_stop_before_sdk(wallet):
    wallet.reserve.return_value = {"created": True, "state": "reserved", "reserved_credit_micros": 50_000}
    client, create = client_with_response()
    with pytest.raises(usage.AIUsageError), usage.ai_usage_scope(7):
        usage.set_approved_credit_limit(0)
        client.chat.completions.create(**request())
    create.assert_not_called()
    assert wallet.settle.call_args.kwargs["actual_cost_micros"] == 0


def test_whatsapp_heart_team_quotes_before_confirmation_and_queues_accepted_budget(monkeypatch, wallet):
    from app.services import whatsapp_assistant as wa, heart_team as ht
    monkeypatch.setattr(wa.settings, "heart_team_enabled", True)
    monkeypatch.setattr(wa, "_permission", lambda *args: True)
    monkeypatch.setattr(wa, "_encrypt", lambda value, owner: dict(value))
    monkeypatch.setattr(wa, "payload_requires_level4", lambda *args: False)
    draft = SimpleNamespace(id=71)
    create = Mock(return_value=draft)
    quote = Mock(return_value={"quote_id": 92, "maximum_credit_centavos": 375,
                              "expires_at": "2026-09-09T15:00:00Z"})
    enqueue = Mock()
    monkeypatch.setattr(ht, "create_case_draft", create)
    monkeypatch.setattr(ht, "estimate_case_budget", quote)
    monkeypatch.setattr(ht, "enqueue_analysis_job", enqueue)
    db = SimpleNamespace(flush=Mock(), add=Mock())
    user = SimpleNamespace(id=7)
    cmd = SimpleNamespace(id=81, link_id=9, kind="heart_team_start", level=3)
    payload = {"text": "Caso anonimizado", "arguments": {"quote_id": 999, "maximum_credit_centavos": 1}}
    prepared = wa._prepare_heart_team_budget(db, user, cmd, payload)
    assert "3.75 créditos" in prepared["mensagem"]
    assert payload["heart_team_budget"] == {"quote_id": 92, "maximum_credit_centavos": 375}
    enqueue.assert_not_called()
    wallet.reserve.assert_not_called()
    result = wa._execute(db, user, cmd, payload)
    assert result["case_id"] == 71
    assert enqueue.call_args.kwargs["quote_id"] == 92
    assert enqueue.call_args.kwargs["approved_max_credit_centavos"] == 375
    assert db.add.call_args.args[0].case_id == 71


def test_whatsapp_heart_team_missing_budget_never_queues(monkeypatch, wallet):
    from app.services import whatsapp_assistant as wa, heart_team as ht
    monkeypatch.setattr(wa.settings, "heart_team_enabled", True)
    monkeypatch.setattr(wa, "_permission", lambda *args: True)
    monkeypatch.setattr(wa, "payload_requires_level4", lambda *args: False)
    enqueue = Mock()
    monkeypatch.setattr(ht, "enqueue_analysis_job", enqueue)
    cmd = SimpleNamespace(id=81, link_id=9, kind="heart_team_start", level=3)
    with pytest.raises(Exception) as exc:
        wa._execute(SimpleNamespace(), SimpleNamespace(id=7), cmd, {"text": "Caso", "arguments": {}})
    assert getattr(exc.value, "status_code", None) == 409
    enqueue.assert_not_called()
    wallet.reserve.assert_not_called()
