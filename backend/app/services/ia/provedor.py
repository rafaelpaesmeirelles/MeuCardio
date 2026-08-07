"""Abstração de provedor de IA.

Hoje o serviço roda em OpenAI, porque o crédito já está contratado.
Trocar para Claude depois é mudar `AI_PROVIDER` no .env — nenhuma rota,
nenhum modelo de dados e nenhuma tela precisam ser tocados.

Regra: o provedor só transporta texto. Toda a política clínica (grounding,
recusa de invenção, aviso de validação) vive no prompt do serviço de RAG,
igual para qualquer provedor.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.core.config import settings


@dataclass
class Resposta:
    texto: str
    tokens_entrada: int
    tokens_saida: int
    modelo: str
    # True quando a resposta foi cortada por atingir ai_max_output_tokens —
    # sem isso o usuário recebe um texto incompleto (ex.: dose cortada no
    # meio) sem nenhum sinal de que faltou conteúdo.
    truncado: bool = False


class ProvedorIA(ABC):
    @abstractmethod
    def embeddings(self, textos: list[str]) -> list[list[float]]: ...

    @abstractmethod
    def responder(
        self,
        sistema: str,
        mensagens: list[dict],
        modelo: str | None = None,
        usar_internet: bool = True,
        ferramentas: list[dict] | None = None,
        executor_ferramenta=None,
    ) -> Resposta: ...

    @abstractmethod
    def responder_stream(
        self,
        sistema: str,
        mensagens: list[dict],
        modelo: str | None = None,
        usar_internet: bool = True,
        ferramentas: list[dict] | None = None,
        executor_ferramenta=None,
    ):
        """Gerador: produz {"delta": str} a cada pedaço de texto e termina com
        {"final": Resposta(...)}. Existe para manter a conexão HTTP viva em
        perguntas longas — ver nota em ProvedorAnthropic.responder_stream."""
        ...

    @property
    @abstractmethod
    def dimensao_embedding(self) -> int: ...


class ProvedorOpenAI(ProvedorIA):
    def __init__(self) -> None:
        from openai import OpenAI

        self._cliente = OpenAI(api_key=settings.openai_api_key)
        self._modelo = settings.openai_model
        self._modelo_embedding = settings.openai_embedding_model

    @property
    def dimensao_embedding(self) -> int:
        return settings.embedding_dim

    def embeddings(self, textos: list[str]) -> list[list[float]]:
        resp = self._cliente.embeddings.create(model=self._modelo_embedding, input=textos)
        return [d.embedding for d in resp.data]

    def responder(
        self,
        sistema: str,
        mensagens: list[dict],
        modelo: str | None = None,
        usar_internet: bool = True,
        ferramentas: list[dict] | None = None,
        executor_ferramenta=None,
    ) -> Resposta:
        # usar_internet, modelo, ferramentas e executor_ferramenta não têm
        # efeito no caminho OpenAI — aceitos na assinatura só por paridade de
        # interface com ProvedorAnthropic. A validação de que usar_internet e
        # ferramentas exigem provider="anthropic" é feita antes, na rota
        # (app/api/ai.py), não aqui.
        modelo_efetivo = self._modelo
        resp = self._cliente.chat.completions.create(
            model=modelo_efetivo,
            messages=[{"role": "system", "content": sistema}, *mensagens],
            max_tokens=settings.ai_max_output_tokens,
            temperature=0.2,
        )
        uso = resp.usage
        return Resposta(
            texto=resp.choices[0].message.content or "",
            tokens_entrada=getattr(uso, "prompt_tokens", 0) or 0,
            tokens_saida=getattr(uso, "completion_tokens", 0) or 0,
            modelo=modelo_efetivo,
            truncado=resp.choices[0].finish_reason == "length",
        )

    def responder_stream(
        self,
        sistema: str,
        mensagens: list[dict],
        modelo: str | None = None,
        usar_internet: bool = True,
        ferramentas: list[dict] | None = None,
        executor_ferramenta=None,
    ):
        modelo_efetivo = self._modelo
        stream = self._cliente.chat.completions.create(
            model=modelo_efetivo,
            messages=[{"role": "system", "content": sistema}, *mensagens],
            max_tokens=settings.ai_max_output_tokens,
            temperature=0.2,
            stream=True,
            stream_options={"include_usage": True},
        )
        textos: list[str] = []
        tokens_entrada = 0
        tokens_saida = 0
        truncado = False
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                pedaco = chunk.choices[0].delta.content
                textos.append(pedaco)
                yield {"delta": pedaco}
            if chunk.choices and chunk.choices[0].finish_reason == "length":
                truncado = True
            if chunk.usage:
                tokens_entrada = chunk.usage.prompt_tokens or 0
                tokens_saida = chunk.usage.completion_tokens or 0
        yield {"final": Resposta(
            texto="".join(textos), tokens_entrada=tokens_entrada,
            tokens_saida=tokens_saida, modelo=modelo_efetivo, truncado=truncado,
        )}


class ProvedorAnthropic(ProvedorIA):
    """Preparado para a troca futura.

    A API da Anthropic não oferece endpoint de embeddings próprio. Ao migrar,
    mantenha os embeddings em um serviço dedicado (OpenAI, Voyage ou modelo
    local) e use a Anthropic apenas para a geração — por isso a interface
    separa `embeddings` de `responder`.
    """

    def __init__(self) -> None:
        import anthropic

        self._cliente = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self._modelo = settings.anthropic_model

    @property
    def dimensao_embedding(self) -> int:
        return settings.embedding_dim

    def embeddings(self, textos: list[str]) -> list[list[float]]:
        raise NotImplementedError(
            "Configure AI_EMBEDDING_PROVIDER separadamente ao migrar a geração para Claude."
        )

    def _kwargs_base(
        self, sistema: str, modelo_efetivo: str, usar_internet: bool,
        ferramentas: list[dict] | None = None,
    ) -> dict:
        kwargs: dict = {
            "model": modelo_efetivo,
            "system": sistema,
            "max_tokens": settings.ai_max_output_tokens,
        }
        tools: list[dict] = []
        if usar_internet:
            # max_uses limita quantas vezes o modelo pode chamar a busca DENTRO
            # da mesma resposta. Sem teto, uma pergunta complexa podia disparar
            # buscas demais e estourar o tempo que uma conexão HTTP comum
            # tolera antes de cair — foi o que produziu "Failed to fetch" em
            # produção mesmo com a resposta pronta do lado do servidor
            # (medido: ~125s de principio a fim, conexão morrendo ~100s).
            # `allowed_callers: ["direct"]` explícito — bug real em produção,
            # 06-07/08/2026: a Assistente Pessoal (Trabalho 15) pode
            # auto-selecionar claude-haiku-4-5 para pergunta curta/simples, e
            # esse modelo não suporta "chamada programática" de ferramenta, o
            # modo que a API assume por padrão quando o campo não é
            # declarado. Sem isso a chamada inteira falhava com 400
            # BadRequestError, e o assinante via só "O provedor de IA não
            # respondeu" — a mensagem de erro da própria Anthropic já indica
            # esta correção. Modelos que suportam chamada programática
            # continuam funcionando normalmente com o campo explícito.
            tools.append({
                "type": "web_search_20260209", "name": "web_search", "max_uses": 3,
                "allowed_callers": ["direct"],
            })
        if ferramentas:
            # Tools "cliente" (agenda/e-mail do próprio usuário) — ao contrário
            # da web_search, que o servidor da Anthropic executa sozinho,
            # estas precisam ser executadas por nós (ver `executor_ferramenta`
            # em `responder`/`responder_stream`) e o resultado devolvido como
            # `tool_result` na mesma conversa.
            tools.extend(ferramentas)
        if tools:
            kwargs["tools"] = tools
        return kwargs

    @staticmethod
    def _blocos_tool_use(resp) -> list:
        return [bloco for bloco in resp.content if bloco.type == "tool_use"]

    # stop_reason == "pause_turn" acontece em buscas na internet mais longas
    # (ferramenta server-side): não é erro nem resposta pronta, é o sinal de
    # que o modelo ainda está no meio do raciocínio/busca e precisa que a
    # MESMA conversa continue — resposta anterior sem tratar isso chegava com
    # texto final vazio. O jeito certo, por documentação da Anthropic, é
    # reenviar o bloco de conteúdo do assistente como nova mensagem
    # "assistant" e chamar de novo, sem tool_result (quem executa a busca é o
    # servidor da Anthropic, não este código). Teto de 2 rodadas, não 5: cada
    # rodada extra soma latência de rede numa conexão que já está no limite
    # do que navegador/NAT tolera fica ociosa.
    _MAX_RODADAS_PAUSE_TURN = 2
    # Uma pergunta que aciona tool de agenda/e-mail costuma precisar de mais
    # de uma chamada por turno (ex.: "quando é minha próxima consulta com a
    # Dona Maria" pode exigir listar compromissos e SÓ DEPOIS responder) —
    # teto maior que o de pause_turn, mas ainda finito: nunca deixamos o
    # modelo encadear ferramentas indefinidamente numa única resposta.
    _MAX_RODADAS_TOOL_USE = 6

    def responder(
        self,
        sistema: str,
        mensagens: list[dict],
        modelo: str | None = None,
        usar_internet: bool = True,
        ferramentas: list[dict] | None = None,
        executor_ferramenta=None,
    ) -> Resposta:
        modelo_efetivo = modelo or self._modelo
        kwargs = self._kwargs_base(sistema, modelo_efetivo, usar_internet, ferramentas)
        max_rodadas = self._MAX_RODADAS_TOOL_USE if ferramentas else self._MAX_RODADAS_PAUSE_TURN

        mensagens_turno = list(mensagens)
        textos: list[str] = []
        tokens_entrada = 0
        tokens_saida = 0
        for _ in range(max_rodadas):
            resp = self._cliente.messages.create(messages=mensagens_turno, **kwargs)
            tokens_entrada += resp.usage.input_tokens
            tokens_saida += resp.usage.output_tokens
            # Com busca na internet ligada, resp.content mistura blocos de texto
            # com blocos de uso de ferramenta (server_tool_use/web_search_tool_result)
            # — só os blocos type == "text" compõem a resposta final ao usuário.
            textos.append("".join(b.text for b in resp.content if b.type == "text"))
            if resp.stop_reason == "tool_use" and executor_ferramenta is not None:
                blocos = self._blocos_tool_use(resp)
                resultados = [
                    {
                        "type": "tool_result",
                        "tool_use_id": bloco.id,
                        "content": json.dumps(executor_ferramenta(bloco.name, bloco.input), ensure_ascii=False),
                    }
                    for bloco in blocos
                ]
                mensagens_turno = [
                    *mensagens_turno,
                    {"role": "assistant", "content": resp.content},
                    {"role": "user", "content": resultados},
                ]
                continue
            if resp.stop_reason != "pause_turn":
                break
            mensagens_turno = [*mensagens_turno, {"role": "assistant", "content": resp.content}]

        return Resposta(
            texto="".join(textos),
            tokens_entrada=tokens_entrada,
            tokens_saida=tokens_saida,
            modelo=modelo_efetivo,
            # stop_reason da última rodada — se saiu do loop por esgotar
            # max_tokens em vez de terminar (end_turn) ou parar de pausar,
            # o texto está cortado no meio.
            truncado=resp.stop_reason == "max_tokens",
        )

    def responder_stream(
        self,
        sistema: str,
        mensagens: list[dict],
        modelo: str | None = None,
        usar_internet: bool = True,
        ferramentas: list[dict] | None = None,
        executor_ferramenta=None,
    ):
        modelo_efetivo = modelo or self._modelo
        kwargs = self._kwargs_base(sistema, modelo_efetivo, usar_internet, ferramentas)
        max_rodadas = self._MAX_RODADAS_TOOL_USE if ferramentas else self._MAX_RODADAS_PAUSE_TURN

        mensagens_turno = list(mensagens)
        textos: list[str] = []
        tokens_entrada = 0
        tokens_saida = 0
        for _ in range(max_rodadas):
            with self._cliente.messages.stream(messages=mensagens_turno, **kwargs) as stream:
                # stream.text_stream só emite pedaços de blocos type == "text",
                # ignorando automaticamente server_tool_use/web_search_tool_result
                # — mesmo filtro do caminho não-streaming, aplicado pelo SDK.
                for pedaco in stream.text_stream:
                    textos.append(pedaco)
                    yield {"delta": pedaco}
                resp = stream.get_final_message()
            tokens_entrada += resp.usage.input_tokens
            tokens_saida += resp.usage.output_tokens
            if resp.stop_reason == "tool_use" and executor_ferramenta is not None:
                blocos = self._blocos_tool_use(resp)
                for bloco in blocos:
                    yield {"status": f"Consultando {bloco.name.replace('_', ' ')}…"}
                resultados = [
                    {
                        "type": "tool_result",
                        "tool_use_id": bloco.id,
                        "content": json.dumps(executor_ferramenta(bloco.name, bloco.input), ensure_ascii=False),
                    }
                    for bloco in blocos
                ]
                mensagens_turno = [
                    *mensagens_turno,
                    {"role": "assistant", "content": resp.content},
                    {"role": "user", "content": resultados},
                ]
                continue
            if resp.stop_reason != "pause_turn":
                break
            mensagens_turno = [*mensagens_turno, {"role": "assistant", "content": resp.content}]

        yield {"final": Resposta(
            texto="".join(textos), tokens_entrada=tokens_entrada,
            tokens_saida=tokens_saida, modelo=modelo_efetivo,
            truncado=resp.stop_reason == "max_tokens",
        )}


_cache: ProvedorIA | None = None
_cache_embeddings: ProvedorIA | None = None


def obter_provedor() -> ProvedorIA:
    """Provedor usado pra GERAR RESPOSTA (chat) — pode ser OpenAI ou Anthropic."""
    global _cache
    if _cache is None:
        _cache = {"openai": ProvedorOpenAI, "anthropic": ProvedorAnthropic}[
            settings.ai_provider
        ]()
    return _cache


def obter_provedor_embeddings() -> ProvedorIA:
    """Provedor usado só pra EMBEDDING (busca semântica) — hoje só a OpenAI
    oferece isso. Mesmo com ai_provider="anthropic", a busca na biblioteca
    continua usando este provedor, não o de cima. Se os dois forem "openai",
    reaproveita a mesma instância (evita duplicar cliente HTTP à toa)."""
    global _cache_embeddings
    if _cache_embeddings is None:
        if settings.ai_embedding_provider == settings.ai_provider:
            _cache_embeddings = obter_provedor()
        else:
            _cache_embeddings = {"openai": ProvedorOpenAI, "anthropic": ProvedorAnthropic}[
                settings.ai_embedding_provider
            ]()
    return _cache_embeddings
