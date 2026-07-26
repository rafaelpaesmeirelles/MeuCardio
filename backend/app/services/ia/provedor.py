"""Abstração de provedor de IA.

Hoje o serviço roda em OpenAI, porque o crédito já está contratado.
Trocar para Claude depois é mudar `AI_PROVIDER` no .env — nenhuma rota,
nenhum modelo de dados e nenhuma tela precisam ser tocados.

Regra: o provedor só transporta texto. Toda a política clínica (grounding,
recusa de invenção, aviso de validação) vive no prompt do serviço de RAG,
igual para qualquer provedor.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.core.config import settings


@dataclass
class Resposta:
    texto: str
    tokens_entrada: int
    tokens_saida: int
    modelo: str


class ProvedorIA(ABC):
    @abstractmethod
    def embeddings(self, textos: list[str]) -> list[list[float]]: ...

    @abstractmethod
    def responder(self, sistema: str, mensagens: list[dict]) -> Resposta: ...

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

    def responder(self, sistema: str, mensagens: list[dict]) -> Resposta:
        resp = self._cliente.chat.completions.create(
            model=self._modelo,
            messages=[{"role": "system", "content": sistema}, *mensagens],
            max_tokens=settings.ai_max_output_tokens,
            temperature=0.2,
        )
        uso = resp.usage
        return Resposta(
            texto=resp.choices[0].message.content or "",
            tokens_entrada=getattr(uso, "prompt_tokens", 0) or 0,
            tokens_saida=getattr(uso, "completion_tokens", 0) or 0,
            modelo=self._modelo,
        )


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

    def responder(self, sistema: str, mensagens: list[dict]) -> Resposta:
        resp = self._cliente.messages.create(
            model=self._modelo,
            system=sistema,
            messages=mensagens,
            max_tokens=settings.ai_max_output_tokens,
        )
        return Resposta(
            texto="".join(b.text for b in resp.content if b.type == "text"),
            tokens_entrada=resp.usage.input_tokens,
            tokens_saida=resp.usage.output_tokens,
            modelo=self._modelo,
        )


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
