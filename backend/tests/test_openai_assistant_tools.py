"""Personal assistant tools use real metering and fake network/wallet boundaries."""
from datetime import date
from types import SimpleNamespace as NS
from unittest.mock import Mock
import json

import pytest

from app.services import ai_wallet
from app.services.ia import usage_control as usage
from app.services.ia.provedor import ProvedorOpenAI

TOOLS = [{"name": "listar_agenda", "description": "Consultar agenda do usuário",
          "input_schema": {"type": "object", "properties": {"data": {"type": "string"}}, "required": ["data"]}}]


@pytest.fixture(autouse=True)
def _banco_limpo():
    yield


@pytest.fixture
def wallet(monkeypatch):
    result = NS(reserve=Mock(return_value={"created": True, "state": "reserved"}),
                settle=Mock(), mark_unknown=Mock(), fail=Mock())
    for name, mock in vars(result).items():
        monkeypatch.setattr(ai_wallet, name, mock)
    return result


def call(identity="call_1", name="listar_agenda", arguments='{"data":"2026-09-10"}'):
    return NS(id=identity, type="function", function=NS(name=name, arguments=arguments))


def response(tool=None, text="", reason=None):
    return NS(choices=[NS(message=NS(content=text, tool_calls=[tool] if tool else []),
                          finish_reason=reason or ("tool_calls" if tool else "stop"))],
              usage=NS(prompt_tokens=50, completion_tokens=10))


def provider(results):
    create = Mock(side_effect=results)
    raw = NS(chat=NS(completions=NS(create=create)))
    p = ProvedorOpenAI.__new__(ProvedorOpenAI)
    p._cliente = usage.MeteredSDK(raw, "openai")
    p._modelo = "gpt-4o-mini"
    return p, create


def test_tools_execute_and_return_serialized_results_with_all_rounds_metered(wallet):
    p, create = provider([response(call()), response(text="Consulta encontrada.")])
    execute = Mock(return_value={"data": date(2026, 9, 10), "eventos": []})
    messages = [{"role": "user", "content": "Consultar minha agenda"}]
    with usage.ai_usage_scope(7):
        result = p.responder("Assistente pessoal", messages, ferramentas=TOOLS, executor_ferramenta=execute)
    execute.assert_called_once_with("listar_agenda", {"data": "2026-09-10"})
    assert result.texto == "Consulta encontrada."
    assert (result.tokens_entrada, result.tokens_saida) == (100, 20)
    assert create.call_args_list[0].kwargs["parallel_tool_calls"] is False
    assert create.call_args_list[0].kwargs["tools"][0]["function"]["parameters"] == TOOLS[0]["input_schema"]
    tool_result = create.call_args_list[1].kwargs["messages"][-1]
    assert tool_result["tool_call_id"] == "call_1"
    assert json.loads(tool_result["content"])["data"] == "2026-09-10"
    assert len(messages) == 1
    wallet.reserve.assert_called_once()
    wallet.settle.assert_called_once()
    assert wallet.settle.call_args.kwargs["tokens_input"] == 100


def chunk(*, text=None, tool=None, finish=None, usage_value=None):
    return NS(usage=usage_value, choices=[] if usage_value else [NS(
        delta=NS(content=text, tool_calls=[tool] if tool else []), finish_reason=finish)])


def streamed_call():
    return iter([
        chunk(tool=NS(index=0, id="call_1", function=NS(name="listar_agenda", arguments='{"data":'))),
        chunk(tool=NS(index=0, id=None, function=NS(name=None, arguments='"2026-09-10"}'))),
        chunk(finish="tool_calls"),
        chunk(usage_value=NS(prompt_tokens=50, completion_tokens=10)),
    ])


def test_stream_assembles_tool_arguments_and_returns_status_delta_and_final(wallet):
    p, create = provider([streamed_call(), iter([
        chunk(text="Agenda "), chunk(text="consultada."), chunk(finish="stop"),
        chunk(usage_value=NS(prompt_tokens=70, completion_tokens=20)),
    ])])
    execute = Mock(return_value=[])
    with usage.ai_usage_scope(7):
        events = list(p.responder_stream("Pessoal", [], ferramentas=TOOLS, executor_ferramenta=execute))
    assert [e["delta"] for e in events if "delta" in e] == ["Agenda ", "consultada."]
    assert any("status" in e for e in events)
    assert events[-1]["final"].texto == "Agenda consultada."
    assert events[-1]["final"].tokens_entrada == 120
    execute.assert_called_once_with("listar_agenda", {"data": "2026-09-10"})
    assert all(c.kwargs["stream_options"] == {"include_usage": True} for c in create.call_args_list)
    assert wallet.settle.call_args.kwargs["tokens_input"] == 120
    wallet.mark_unknown.assert_not_called()


@pytest.mark.parametrize("bad", [call(name="enviar_email_nao_autorizado"), call(arguments="not json"), call(arguments="[]")])
def test_unknown_or_invalid_tool_never_runs_executor(wallet, bad):
    p, create = provider([response(bad)])
    execute = Mock()
    with usage.ai_usage_scope(7), pytest.raises(usage.AIUsageError):
        p.responder("Pessoal", [], ferramentas=TOOLS, executor_ferramenta=execute)
    execute.assert_not_called()
    assert create.call_count == 1


def test_missing_account_or_budget_never_calls_provider_or_executor(wallet):
    p, create = provider([response(call())])
    execute = Mock()
    with pytest.raises(usage.AIUsageError):
        p.responder("Pessoal", [], ferramentas=TOOLS, executor_ferramenta=execute)
    wallet.reserve.side_effect = usage.AIUsageError("Saldo insuficiente")
    with usage.ai_usage_scope(7), pytest.raises(usage.AIUsageError):
        p.responder("Pessoal", [], ferramentas=TOOLS, executor_ferramenta=execute)
    create.assert_not_called()
    execute.assert_not_called()


def test_repeated_tool_id_does_not_repeat_side_effect(wallet):
    p, create = provider([response(call()), response(call()), response(text="Concluído")])
    execute = Mock(return_value={"ok": True})
    with usage.ai_usage_scope(7):
        p.responder("Pessoal", [], ferramentas=TOOLS, executor_ferramenta=execute)
    execute.assert_called_once()
    assert create.call_count == 3


def test_final_round_does_not_execute_new_action(wallet):
    p, create = provider([response(call(identity=f"call_{i}")) for i in range(6)])
    execute = Mock(return_value=[])
    with usage.ai_usage_scope(7):
        result = p.responder("Pessoal", [], ferramentas=TOOLS, executor_ferramenta=execute)
    assert create.call_count == 6
    assert execute.call_count == 5
    assert create.call_args.kwargs["tool_choice"] == "none"
    assert result.truncado is True


def test_stream_cancellation_before_tool_execution_does_not_run_action(wallet):
    p, create = provider([streamed_call()])
    execute = Mock()
    with usage.ai_usage_scope(7):
        events = p.responder_stream("Pessoal", [], ferramentas=TOOLS, executor_ferramenta=execute)
        assert "status" in next(events)
        events.close()
    execute.assert_not_called()
    create.assert_called_once()
    assert wallet.settle.call_args.kwargs["tokens_input"] == 50


def test_same_write_with_new_id_is_not_executed_twice(wallet):
    name = "agenda_criar_compromisso"
    definitions = [{**TOOLS[0], "name": name}]
    p, create = provider([response(call("first", name)), response(call("second", name)), response(text="Criado")])
    execute = Mock(return_value={"appointment_id": 25})
    with usage.ai_usage_scope(7):
        p.responder("Pessoal", [], ferramentas=definitions, executor_ferramenta=execute)
    execute.assert_called_once()
    assert create.call_count == 3
    returned = create.call_args.kwargs["messages"][-1]
    assert returned["tool_call_id"] == "second"
    assert json.loads(returned["content"])["appointment_id"] == 25


def test_dedicated_reasoning_is_sent_without_changing_global_chat_model(wallet):
    p, create = provider([response(text="Parecer")])
    with usage.ai_usage_scope(7):
        result = p.responder("Clínico", [], modelo="gpt-5.6-sol", max_output_tokens=8192, reasoning_effort="medium")
    assert create.call_args.kwargs["model"] == "gpt-5.6-sol"
    assert create.call_args.kwargs["max_completion_tokens"] == 8192
    assert create.call_args.kwargs["reasoning_effort"] == "medium"
    assert "temperature" not in create.call_args.kwargs
    assert result.modelo == "gpt-5.6-sol"
    assert p._modelo == "gpt-4o-mini"


def test_reasoning_rejects_incompatible_model_before_any_call(wallet):
    p, create = provider([])
    with usage.ai_usage_scope(7), pytest.raises(usage.AIUsageError):
        p.responder("Pessoal", [], reasoning_effort="medium")
    create.assert_not_called()
    wallet.reserve.assert_not_called()
