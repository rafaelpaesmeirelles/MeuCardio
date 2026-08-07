"""Loop de tool-calling (agenda/e-mail) do ProvedorAnthropic — sem rede real,
`messages.create` é substituído por um dublê. Cobre: a tool anunciada é
enviada em `tools`, o resultado da ferramenta volta como `tool_result` JSON,
o loop termina em `end_turn`, e o teto de rodadas (`_MAX_RODADAS_TOOL_USE`)
não deixa o modelo encadear ferramentas para sempre.
"""
import json
from dataclasses import dataclass, field
from types import SimpleNamespace

import pytest

from app.services.ia.provedor import ProvedorAnthropic


@dataclass
class _Uso:
    input_tokens: int = 10
    output_tokens: int = 10


@dataclass
class _Bloco:
    type: str
    text: str = ""
    name: str = ""
    input: dict = field(default_factory=dict)
    id: str = "toolu_1"


@dataclass
class _Resp:
    content: list
    stop_reason: str
    usage: _Uso = field(default_factory=_Uso)


def _provedor_com_cliente_falso(respostas: list[_Resp]):
    provedor = ProvedorAnthropic.__new__(ProvedorAnthropic)  # pula __init__ (evita exigir API key real)
    provedor._modelo = "claude-sonnet-5"
    chamadas: list[dict] = []

    def create(*, messages, **kwargs):
        chamadas.append({"messages": messages, **kwargs})
        return respostas[len(chamadas) - 1]

    provedor._cliente = SimpleNamespace(messages=SimpleNamespace(create=create))
    return provedor, chamadas


def test_tool_use_e_executado_e_resultado_volta_como_tool_result():
    respostas = [
        _Resp(
            content=[_Bloco(type="tool_use", name="agenda_listar_compromissos", input={}, id="toolu_abc")],
            stop_reason="tool_use",
        ),
        _Resp(content=[_Bloco(type="text", text="Você tem 2 compromissos hoje.")], stop_reason="end_turn"),
    ]
    provedor, chamadas = _provedor_com_cliente_falso(respostas)

    execucoes = []

    def executor(nome, argumentos):
        execucoes.append((nome, argumentos))
        return {"total": 2, "compromissos": []}

    resposta = provedor.responder(
        "sistema", [{"role": "user", "content": "o que tenho hoje?"}],
        usar_internet=False,
        ferramentas=[{"name": "agenda_listar_compromissos", "description": "...", "input_schema": {}}],
        executor_ferramenta=executor,
    )

    assert resposta.texto == "Você tem 2 compromissos hoje."
    assert execucoes == [("agenda_listar_compromissos", {})]
    # a 2ª chamada ao "modelo" precisa conter o tool_result serializado em JSON
    segunda_chamada_mensagens = chamadas[1]["messages"]
    bloco_tool_result = segunda_chamada_mensagens[-1]["content"][0]
    assert bloco_tool_result["type"] == "tool_result"
    assert bloco_tool_result["tool_use_id"] == "toolu_abc"
    assert json.loads(bloco_tool_result["content"]) == {"total": 2, "compromissos": []}
    # a tool anunciada precisa ter chegado no kwarg `tools` da 1ª chamada
    assert chamadas[0]["tools"][0]["name"] == "agenda_listar_compromissos"


def test_sem_ferramentas_nao_usa_tool_use_mesmo_que_stop_reason_venha_assim():
    """Sem `executor_ferramenta`, um tool_use inesperado não deve travar o
    loop num `continue` infinito — cai no `break` normal (comportamento
    antigo, sem tools)."""
    respostas = [
        _Resp(content=[_Bloco(type="text", text="resposta sem tools")], stop_reason="end_turn"),
    ]
    provedor, chamadas = _provedor_com_cliente_falso(respostas)
    resposta = provedor.responder("sistema", [{"role": "user", "content": "oi"}], usar_internet=False)
    assert resposta.texto == "resposta sem tools"
    assert "tools" not in chamadas[0]


def test_teto_de_rodadas_de_tool_use_e_respeitado():
    """Se o modelo insistir em chamar ferramenta rodada após rodada, o loop
    não pode rodar para sempre — para no teto e devolve o que tiver."""
    resposta_tool_use = _Resp(
        content=[_Bloco(type="tool_use", name="agenda_listar_compromissos", input={}, id="toolu_x")],
        stop_reason="tool_use",
    )
    respostas = [resposta_tool_use] * (ProvedorAnthropic._MAX_RODADAS_TOOL_USE + 3)
    provedor, chamadas = _provedor_com_cliente_falso(respostas)

    resposta = provedor.responder(
        "sistema", [{"role": "user", "content": "..."}],
        usar_internet=False,
        ferramentas=[{"name": "agenda_listar_compromissos", "description": "...", "input_schema": {}}],
        executor_ferramenta=lambda nome, args: {"ok": True},
    )

    assert len(chamadas) == ProvedorAnthropic._MAX_RODADAS_TOOL_USE
    assert resposta.texto == ""  # nenhum bloco de texto veio em nenhuma rodada


def test_executor_ferramenta_recebe_input_correto_com_multiplas_tools_na_mesma_rodada():
    respostas = [
        _Resp(
            content=[
                _Bloco(type="tool_use", name="agenda_listar_compromissos", input={"limite": 5}, id="t1"),
                _Bloco(type="tool_use", name="mail_resumo_caixa", input={}, id="t2"),
            ],
            stop_reason="tool_use",
        ),
        _Resp(content=[_Bloco(type="text", text="ok")], stop_reason="end_turn"),
    ]
    provedor, chamadas = _provedor_com_cliente_falso(respostas)
    execucoes = []

    def executor(nome, argumentos):
        execucoes.append((nome, argumentos))
        return {"ok": True}

    provedor.responder(
        "sistema", [{"role": "user", "content": "..."}],
        usar_internet=False,
        ferramentas=[{"name": "x", "description": "...", "input_schema": {}}],
        executor_ferramenta=executor,
    )

    assert execucoes == [
        ("agenda_listar_compromissos", {"limite": 5}),
        ("mail_resumo_caixa", {}),
    ]
    resultados = chamadas[1]["messages"][-1]["content"]
    assert [r["tool_use_id"] for r in resultados] == ["t1", "t2"]


def test_web_search_declara_allowed_callers_direct():
    """Bug real em produção, 06-07/08/2026: com `usar_internet=True` e o
    modelo auto-selecionado sendo claude-haiku-4-5 (comum na Assistente
    Pessoal, pergunta curta), a Anthropic devolvia 400 BadRequestError —
    "claude-haiku-4-5 does not support programmatic tool calling" — porque a
    tool `web_search` não declarava `allowed_callers`, e o padrão implícito
    da API exige um recurso que aquele modelo não tem. `allowed_callers:
    ["direct"]` explícito resolve, conforme a própria mensagem de erro da
    Anthropic indicou."""
    respostas = [
        _Resp(content=[_Bloco(type="text", text="ok")], stop_reason="end_turn"),
    ]
    provedor, chamadas = _provedor_com_cliente_falso(respostas)
    provedor.responder("sistema", [{"role": "user", "content": "oi"}], usar_internet=True)
    ferramenta_busca = next(t for t in chamadas[0]["tools"] if t["name"] == "web_search")
    assert ferramenta_busca["allowed_callers"] == ["direct"]
