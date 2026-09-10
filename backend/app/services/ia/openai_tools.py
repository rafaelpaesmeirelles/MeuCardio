"""Bounded, metered Chat Completions tools for the personal assistant.

The caller supplies the existing consent/ownership-checked executor. This module
only translates the tool transport; it does not grant permissions or send mail.
"""
from __future__ import annotations

import json

from app.services.ia.usage_control import AIUsageError, plan_rounds

MAX_ROUNDS = 6


def _get(value, key, default=None):
    return value.get(key, default) if isinstance(value, dict) else getattr(value, key, default)


def _tools(definitions):
    result = []
    names = set()
    for tool in definitions:
        name = tool.get("name")
        schema = tool.get("input_schema")
        if not isinstance(name, str) or not name or name in names or not isinstance(schema, dict):
            raise AIUsageError("Ferramenta do assistente sem contrato válido.", 422)
        names.add(name)
        result.append({"type": "function", "function": {
            "name": name, "description": tool.get("description", ""),
            "parameters": schema,
        }})
    return result, names


def _call_payload(call):
    function = _get(call, "function")
    return {"id": _get(call, "id"), "type": "function", "function": {
        "name": _get(function, "name"), "arguments": _get(function, "arguments", ""),
    }}


def run_tools(client, request, definitions, executor, *, stream, serialize):
    """Yield existing delta/status/final events; every SDK call remains metered."""
    from app.services.ia.provedor import Resposta
    from app.services.ia.assistant_tools import _TOOLS_DE_ESCRITA

    if executor is None:
        raise AIUsageError("Ferramentas indisponíveis para este usuário.", 403)
    tools, allowed_names = _tools(definitions)
    kwargs = {**request, "tools": tools, "parallel_tool_calls": False, "store": False}
    plan_rounds("openai", kwargs, MAX_ROUNDS, tool_result_bytes=20_000)
    messages = list(kwargs.pop("messages"))
    texts = []
    inputs = outputs = 0
    truncated = False
    completed = {}
    completed_writes = {}
    for round_index in range(MAX_ROUNDS):
        current = {**kwargs, "messages": list(messages)}
        # Leave one paid round for a final explanation, without new side effects.
        if round_index == MAX_ROUNDS - 1:
            current["tool_choice"] = "none"
        if stream:
            current.update(stream=True, stream_options={"include_usage": True})
            response = client.chat.completions.create(**current)
            fragments = {}
            content = []
            finish = None
            try:
                for chunk in response:
                    usage = _get(chunk, "usage")
                    if usage is not None:
                        inputs += _get(usage, "prompt_tokens", 0) or 0
                        outputs += _get(usage, "completion_tokens", 0) or 0
                    choices = _get(chunk, "choices", [])
                    if not choices:
                        continue
                    choice = choices[0]
                    finish = _get(choice, "finish_reason") or finish
                    delta = _get(choice, "delta")
                    text = _get(delta, "content")
                    if text:
                        content.append(text)
                        yield {"delta": text}
                    for call in _get(delta, "tool_calls", []) or []:
                        index = _get(call, "index")
                        if index != 0:
                            raise AIUsageError("O provedor excedeu o limite de ferramentas por rodada.", 422)
                        entry = fragments.setdefault(index, {"id": "", "type": "function", "function": {"name": "", "arguments": ""}})
                        entry["id"] += _get(call, "id", "") or ""
                        function = _get(call, "function")
                        entry["function"]["name"] += _get(function, "name", "") or ""
                        entry["function"]["arguments"] += _get(function, "arguments", "") or ""
            finally:
                close = getattr(response, "close", None)
                if close:
                    close()
            text = "".join(content)
            calls = [fragments[index] for index in sorted(fragments)]
        else:
            response = client.chat.completions.create(**current)
            usage = response.usage
            inputs += _get(usage, "prompt_tokens", 0) or 0
            outputs += _get(usage, "completion_tokens", 0) or 0
            choice = response.choices[0]
            text = _get(choice.message, "content", "") or ""
            calls = [_call_payload(call) for call in _get(choice.message, "tool_calls", []) or []]
            finish = choice.finish_reason
        texts.append(text)
        truncated = finish == "length"
        if not calls:
            break
        if len(calls) != 1 or finish != "tool_calls":
            raise AIUsageError("Resposta de ferramenta incompleta; nenhuma ação foi executada nesta rodada.", 422)
        if round_index == MAX_ROUNDS - 1:
            truncated = True
            break
        call = calls[0]
        name = call["function"]["name"]
        identity = call["id"]
        arguments = call["function"]["arguments"]
        if not isinstance(identity, str) or not identity or name not in allowed_names:
            raise AIUsageError("Ferramenta não autorizada para esta conversa.", 403)
        try:
            parsed = json.loads(arguments)
        except (ValueError, TypeError):
            raise AIUsageError("Argumentos inválidos; a ferramenta não foi executada.", 422) from None
        if not isinstance(parsed, dict):
            raise AIUsageError("Argumentos inválidos; a ferramenta não foi executada.", 422)
        signature = (name, json.dumps(parsed, sort_keys=True, ensure_ascii=False))
        if identity in completed:
            previous_signature, result = completed[identity]
            if signature != previous_signature:
                raise AIUsageError("Identificador de ferramenta reutilizado com argumentos diferentes.", 422)
        elif name in _TOOLS_DE_ESCRITA and signature in completed_writes:
            result = completed_writes[signature]
            completed[identity] = (signature, result)
        else:
            yield {"status": f"Executando {name.replace('_', ' ')}…"}
            result = serialize(executor(name, parsed))
            completed[identity] = (signature, result)
            if name in _TOOLS_DE_ESCRITA:
                completed_writes[signature] = result
        messages.extend([
            {"role": "assistant", "content": text or None, "tool_calls": calls},
            {"role": "tool", "tool_call_id": identity, "content": result},
        ])
    yield {"final": Resposta(texto="".join(texts), tokens_entrada=inputs,
                             tokens_saida=outputs, modelo=request["model"], truncado=truncated)}
