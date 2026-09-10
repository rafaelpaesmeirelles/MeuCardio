"""Account-scoped, fail-closed accounting at every paid provider boundary.

Prices: provider public pricing, cache tariffs and image limits, verified 2026-09-10.
All monetary values passed to the wallet are integer BRL micro-units. Payloads
and patient data are never persisted here. Network SDK retries must be disabled.
"""
from __future__ import annotations

import base64
import inspect
import json
import logging
import math
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_CEILING
from functools import wraps
from io import BytesIO
from threading import RLock
from uuid import uuid4

from fastapi import HTTPException
from app.core.config import settings

log = logging.getLogger("corvia.ai.accounting")
PRICING_VERSION = "2026-09-10-cache-v2"
PRICES = {
    "gpt-4o-mini": ("0.15", "0.60"), "gpt-4o": ("2.50", "10"),
    "gpt-5.6-sol": ("4", "20"), "gpt-5.6": ("4", "20"),
    "claude-haiku-4-5": ("1", "5"), "claude-sonnet-4-6": ("3", "15"),
    "claude-sonnet-5": ("2", "10"), "claude-opus-5": ("5", "25"),
    "text-embedding-3-small": ("0.02", "0"),
    "gpt-4o-mini-transcribe": ("1.25", "5"), "gpt-4o-transcribe": ("2.50", "10"),
}
BUDGETS = {
    "clinical_ai": 10_000_000, "personal_ai": 40_000_000,
    "ecg_ai": 3_000_000, "exam_ai": 10_000_000, "round_ai": 3_000_000,
    "heart_team": 100_000_000, "whatsapp_ai": 1_000_000,
    "scientific_document_ai": 10_000_000, "translation_ai": 10_000_000,
    "retrieval": 100_000, "catalog_index": 1_000_000, "editorial": 10_000_000,
}
SERVICE_CENTERS = frozenset({"retrieval", "catalog_index", "editorial"})


class AIUsageError(HTTPException):
    def __init__(self, detail="Não foi possível autorizar o orçamento desta operação de IA.", status_code=402):
        super().__init__(status_code=status_code, detail=detail)


def _config_json(name):
    try:
        value = json.loads(getattr(settings, name, "{}") or "{}")
        if not isinstance(value, dict):
            raise ValueError()
        return value
    except (TypeError, ValueError) as exc:
        raise AIUsageError("Configuração de custos de IA inválida.", 503) from exc


def model_prices(model):
    configured = _config_json("ai_model_prices_json")
    raw = configured.get(model, PRICES.get(model))
    if raw is None:
        raise AIUsageError(f"Modelo sem tarifa homologada: {model}.", 503)
    if isinstance(raw, dict):
        raw = (raw.get("input"), raw.get("output"))
    try:
        rates = tuple(Decimal(str(x)) for x in raw)
        if len(rates) != 2 or any(not x.is_finite() or x < 0 for x in rates):
            raise ValueError()
        return rates
    except Exception as exc:
        raise AIUsageError("Tarifa de IA inválida.", 503) from exc


def _count(value):
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise AIUsageError("Medição de IA inválida; reserva retida para reconciliação.", 503)
    return value


def _cache_factors(model):
    if model in {"gpt-5.6", "gpt-5.6-sol"}:
        return Decimal("0.1"), Decimal("1.25"), None
    if model in {"gpt-4o", "gpt-4o-mini"}:
        return Decimal("0.5"), None, None
    if model in {"claude-haiku-4-5", "claude-sonnet-4-6", "claude-sonnet-5", "claude-opus-5"}:
        return Decimal("0.1"), Decimal("1.25"), Decimal("2")
    return None, None, None


def cost_micros(model, input_tokens, output_tokens, web_searches=0, *,
                cache_read_tokens=0, cache_write_tokens=0, cache_write_1h_tokens=0):
    """Input is the unweighted total, including all cache categories."""
    rates = model_prices(model)
    fx = Decimal(str(getattr(settings, "ai_billing_usd_brl", 6)))
    if not fx.is_finite() or fx <= 0:
        raise AIUsageError("Câmbio de contabilização inválido.", 503)
    for count in (input_tokens, output_tokens, web_searches, cache_read_tokens,
                  cache_write_tokens, cache_write_1h_tokens):
        _count(count)
    ordinary = input_tokens - cache_read_tokens - cache_write_tokens - cache_write_1h_tokens
    if ordinary < 0:
        raise AIUsageError("Categorias de cache excedem o consumo informado.", 503)
    weighted = Decimal(ordinary)
    for count, factor in zip((cache_read_tokens, cache_write_tokens, cache_write_1h_tokens), _cache_factors(model)):
        if count:
            if factor is None:
                raise AIUsageError("Categoria de cache sem tarifa homologada.", 503)
            weighted += count * factor
    # The long-context threshold uses actual input, never price-weighted tokens.
    multiplier = (Decimal(2), Decimal("1.5")) if model in {"gpt-5.6", "gpt-5.6-sol"} and input_tokens > 272_000 else (1, 1)
    amount = (weighted * rates[0] * multiplier[0]
              + Decimal(output_tokens) * rates[1] * multiplier[1]
              + Decimal(web_searches) * Decimal("10000")) * fx
    return int(amount.to_integral_value(rounding=ROUND_CEILING))


def _reserve_cost(model, input_tokens, output_tokens, searches=0):
    # Assume no cache discount; cover the highest supported write tariff.
    # Claude server tools can also create cache entries without explicit markers.
    if model in {"gpt-5.6", "gpt-5.6-sol"}:
        return cost_micros(model, input_tokens, output_tokens, searches, cache_write_tokens=input_tokens)
    if _cache_factors(model)[2] is not None:
        return cost_micros(model, input_tokens, output_tokens, searches, cache_write_1h_tokens=input_tokens)
    return cost_micros(model, input_tokens, output_tokens, searches)


def _cache_ttls(value):
    ttls = set()
    if isinstance(value, dict):
        if isinstance(value.get("cache_control"), dict):
            ttl = value["cache_control"].get("ttl", "5m")
            if ttl not in {"5m", "1h"}:
                raise AIUsageError("Duração de cache não homologada.", 503)
            ttls.add(ttl)
        for child in value.values():
            ttls.update(_cache_ttls(child))
    elif isinstance(value, (tuple, list)):
        for child in value:
            ttls.update(_cache_ttls(child))
    return ttls


def image_tokens(content, model, detail="auto"):
    """Conservative image-input bound; unknown formats/models fail closed."""
    from PIL import Image
    with Image.open(BytesIO(content)) as image:
        width, height = image.size
    if min(width, height) <= 0:
        raise AIUsageError("Dimensões de imagem inválidas.", 422)
    if model in {"gpt-5.6", "gpt-5.6-sol"}:
        bound = 512 if detail == "low" else 2048 if detail == "high" else 65535
        scale = min(1, bound / max(width, height))
        width, height = math.ceil(width * scale), math.ceil(height * scale)
        patches = math.ceil(width / 32) * math.ceil(height / 32)
        if detail == "high":
            patches = min(patches, 2500)
        if patches > 30_000:
            raise AIUsageError("Imagem excede o limite de processamento visual do modelo.", 422)
        return math.ceil(patches * 1.2) + 2
    if model in {"gpt-4o", "gpt-4o-mini"}:
        base, tile = (85, 170) if model == "gpt-4o" else (2833, 5667)
        if detail == "low":
            return base
        scale = min(1, 2048 / max(width, height))
        width, height = width * scale, height * scale
        scale = min(1, 768 / min(width, height))
        return base + tile * math.ceil(width * scale / 512) * math.ceil(height * scale / 512)
    if model.startswith("claude-"):
        # Claude documents ~width*height/750 after resizing. Original pixels
        # overestimate the resized input; include fixed envelope headroom.
        return math.ceil(width * height / 750) + 1024
    raise AIUsageError("Estimativa visual não homologada para este modelo.", 503)


def _binary_tokens(encoded, media_type, model, detail="auto"):
    try:
        data = base64.b64decode(encoded, validate=True)
        if media_type == "application/pdf":
            import fitz
            with fitz.open(stream=data, filetype="pdf") as document:
                if document.page_count > 12:
                    raise AIUsageError("PDF excede 12 páginas para esta análise.", 422)
                # PDFs include page images and extracted text. Use the maximum
                # supported visual patch envelope for each page plus text bytes.
                return sum(36_002 + len(page.get_text().encode("utf-8")) for page in document)
        return image_tokens(data, model, detail)
    except AIUsageError:
        raise
    except Exception as exc:
        raise AIUsageError("Não foi possível estimar o custo do arquivo clínico.", 422) from exc


def input_token_bound(value, model):
    if hasattr(value, "model_dump"):
        value = value.model_dump()
    if isinstance(value, str):
        if value.startswith("data:"):
            header, encoded = value.split(",", 1)
            return _binary_tokens(encoded, header[5:].split(";")[0], model)
        return len(value.encode("utf-8"))
    if isinstance(value, (list, tuple)):
        return sum(input_token_bound(v, model) + 16 for v in value)
    if isinstance(value, dict):
        if isinstance(value.get("type"), str) and value.get("type") in {"image", "document"} and isinstance(value.get("source"), dict):
            src = value["source"]
            if src.get("type") != "base64":
                raise AIUsageError("Arquivo remoto sem orçamento verificável.", 422)
            return _binary_tokens(src.get("data", ""), src.get("media_type"), model)
        if isinstance(value.get("type"), str) and value.get("type") in {"image_url", "input_image"}:
            image = value.get("image_url")
            url = image.get("url") if isinstance(image, dict) else image
            detail = image.get("detail", "auto") if isinstance(image, dict) else value.get("detail", "auto")
            if not isinstance(url, str) or not url.startswith("data:"):
                raise AIUsageError("Imagem remota sem orçamento verificável.", 422)
            header, encoded = url.split(",", 1)
            return _binary_tokens(encoded, header[5:].split(";")[0], model, detail)
        return sum(input_token_bound(v, model) + len(str(k)) + 16 for k, v in value.items())
    return len(str(value)) + 16


def estimate_request(provider, request):
    model = request.get("model")
    model_prices(model)
    _cache_ttls(request)
    output = int(request.get("max_completion_tokens", request.get("max_output_tokens", request.get("max_tokens", 0))) or 0)
    if output <= 0 and not str(model).startswith("text-embedding-"):
        raise AIUsageError("Chamada de IA sem limite de saída.", 503)
    searches = sum(int(t.get("max_uses", 3)) for t in request.get("tools", []) if str(t.get("type", "")).startswith("web_search"))
    if searches > 3:
        raise AIUsageError("Orçamento de buscas externas excedido.", 422)
    inputs = input_token_bound(request, model) + 256
    # Search result content is additional provider-side model input.
    inputs += searches * 25_000
    return _reserve_cost(model, inputs, output, searches)


@dataclass
class UsageScope:
    owner_id: int | None
    feature: str
    cost_center: str | None = None
    operation_key: str = field(default_factory=lambda: "ai:" + uuid4().hex)
    planned_cost: int = 0
    reserved_cost: int = 0
    spent: int = 0
    pending: int = 0
    tokens_input: int = 0
    tokens_output: int = 0
    unknown: bool = False
    quote_only: bool = False
    approved_credit_centavos: int | None = None
    models: set = field(default_factory=set)
    lock: object = field(default_factory=RLock)

    @property
    def ceiling(self):
        raw = _config_json("ai_journey_budgets_json").get(self.feature, BUDGETS.get(self.feature))
        if not isinstance(raw, int) or isinstance(raw, bool) or raw <= 0:
            raise AIUsageError("Operação sem teto de custo homologado.", 503)
        return raw

    def reserve(self, estimate, model):
        from app.services import ai_wallet
        if self.quote_only:
            raise AIUsageError("Uma cotação não pode executar chamadas pagas.", 403)
        with self.lock:
            if self.unknown:
                raise AIUsageError("Uma chamada anterior aguarda reconciliação de custo.", 409)
            if self.reserved_cost:
                if estimate + self.spent + self.pending > self.reserved_cost:
                    raise AIUsageError("A operação atingiu o orçamento previamente autorizado.")
                self.pending += estimate
                return
            amount = max(estimate, self.planned_cost)
            if amount > self.ceiling:
                raise AIUsageError("O orçamento estimado excede o teto desta operação. Reduza o conteúdo ou ajuste o limite.")
            receipt = ai_wallet.reserve(owner_id=self.owner_id, operation_key=self.operation_key,
                feature=self.feature, model=model, max_cost_micros=amount,
                pricing_version=PRICING_VERSION, cost_center=self.cost_center)
            if not receipt.get("created"):
                raise AIUsageError("Esta operação já possui uma reserva; não será enviada novamente.", 409)
            self.reserved_cost = amount
            if self.approved_credit_centavos is not None:
                quoted_credit = receipt.get("reserved_credit_micros")
                if not isinstance(quoted_credit, int) or quoted_credit > self.approved_credit_centavos * 10_000:
                    raise AIUsageError("O orçamento mudou desde a confirmação. Solicite uma nova cotação.", 409)
            self.pending += estimate


_scope: ContextVar[UsageScope | None] = ContextVar("corvia_ai_usage_scope", default=None)


@contextmanager
def ai_usage_scope(owner_id=None, feature="clinical_ai", *, cost_center=None, inherit=False):
    parent = _scope.get()
    if parent is not None and (inherit or (parent.owner_id == owner_id and parent.cost_center == cost_center)):
        yield parent
        return
    if owner_id is None and cost_center not in SERVICE_CENTERS:
        raise AIUsageError("Operação de IA sem conta responsável.", 403)
    if owner_id is not None and (isinstance(owner_id, bool) or not isinstance(owner_id, int) or owner_id <= 0 or cost_center is not None):
        raise AIUsageError("Conta de IA inválida.", 403)
    current = UsageScope(owner_id, feature, cost_center, quote_only=bool(parent and parent.quote_only))
    token = _scope.set(current)
    try:
        yield current
    finally:
        try:
            if current.reserved_cost:
                from app.services import ai_wallet
                kw = dict(owner_id=current.owner_id, operation_key=current.operation_key, cost_center=current.cost_center)
                if current.unknown or current.pending:
                    ai_wallet.mark_unknown(**kw, known_cost_micros=current.spent,
                        known_tokens_input=current.tokens_input, known_tokens_output=current.tokens_output,
                        model=next(iter(current.models)) if len(current.models) == 1 else "mixed")
                else:
                    ai_wallet.settle(**kw, actual_cost_micros=current.spent,
                        tokens_input=current.tokens_input, tokens_output=current.tokens_output,
                        model=next(iter(current.models)) if len(current.models) == 1 else "mixed")
        finally:
            _scope.reset(token)


def ai_operation(feature, *, owner="user.id", cost_center=None, inherit=False):
    """Service decorator; generators keep the context inside their worker."""
    def decorate(fn):
        signature = inspect.signature(fn)
        def scope_for(args, kwargs):
            bound = signature.bind(*args, **kwargs); bound.apply_defaults()
            selected = feature(bound.arguments) if callable(feature) else feature
            value = None
            if owner:
                path = owner.split("."); value = bound.arguments.get(path[0])
                for part in path[1:]:
                    value = getattr(value, part, None)
            return ai_usage_scope(value, selected, cost_center=cost_center, inherit=inherit)
        if inspect.isgeneratorfunction(fn):
            @wraps(fn)
            def wrapped(*args, **kwargs):
                with scope_for(args, kwargs):
                    yield from fn(*args, **kwargs)
        elif inspect.iscoroutinefunction(fn):
            @wraps(fn)
            async def wrapped(*args, **kwargs):
                with scope_for(args, kwargs):
                    return await fn(*args, **kwargs)
        else:
            @wraps(fn)
            def wrapped(*args, **kwargs):
                with scope_for(args, kwargs):
                    return fn(*args, **kwargs)
        return wrapped
    return decorate


def plan_requests(provider, requests):
    current = _scope.get()
    if current is None:
        raise AIUsageError("Chamada de IA sem contexto de contabilização.", 403)
    planned = sum(estimate_request(provider, request) for request in requests)
    if current.reserved_cost:
        if planned + current.spent > current.reserved_cost:
            raise AIUsageError("As próximas etapas excedem a reserva desta operação.")
    else:
        current.planned_cost = max(current.planned_cost, planned)
        if planned > current.ceiling:
            raise AIUsageError("O orçamento total estimado excede o teto desta operação.")
    return planned


def _mapping(value):
    if isinstance(value, dict):
        return value
    if hasattr(value, "model_dump"):
        return value.model_dump()
    return vars(value) if value is not None and hasattr(value, "__dict__") else {}


def _usage_details(value):
    if value is not None and not (isinstance(value, dict) or hasattr(value, "model_dump") or hasattr(value, "__dict__")):
        raise AIUsageError("Detalhamento de consumo inválido; reserva retida.", 503)
    return _mapping(value)


class RequestMeter:
    def __init__(self, scope, model, estimate, *, provider=None, request=None):
        self.provider = provider or ("anthropic" if model.startswith("claude-") else "openai")
        self.cache_ttls = _cache_ttls(request or {})
        self.scope, self.model, self.finished = scope, model, False
        self.estimate = estimate

    def finish(self, usage, *, output=None):
        u = _mapping(usage)
        input_count = u.get("input_tokens", u.get("prompt_tokens", u.get("total_tokens") if self.model.startswith("text-embedding-") else None))
        output_count = u.get("output_tokens", u.get("completion_tokens", 0 if self.model.startswith("text-embedding-") else None))
        if input_count is None or output_count is None:
            raise AIUsageError("O provedor não informou consumo verificável; reserva retida para reconciliação.", 503)
        input_count, output_count = _count(input_count), _count(output_count)
        cache_read = cache_write = cache_1h = 0
        if self.provider == "anthropic":
            cache_read = _count(u.get("cache_read_input_tokens", 0) or 0)
            creation = _count(u.get("cache_creation_input_tokens", 0) or 0)
            breakdown = _usage_details(u.get("cache_creation"))
            if breakdown:
                cache_write = _count(breakdown.get("ephemeral_5m_input_tokens", 0) or 0)
                cache_1h = _count(breakdown.get("ephemeral_1h_input_tokens", 0) or 0)
                if cache_write + cache_1h != creation:
                    raise AIUsageError("Medição de escrita de cache inconsistente.", 503)
            elif creation:
                if self.cache_ttls == {"5m"}:
                    cache_write = creation
                elif self.cache_ttls == {"1h"}:
                    cache_1h = creation
                else:
                    raise AIUsageError("Duração da escrita de cache não verificável; reserva retida.", 503)
            # Anthropic excludes cache reads and writes from input_tokens.
            input_count += creation + cache_read
        else:
            details = _usage_details(u.get("input_tokens_details") if u.get("input_tokens_details") is not None else u.get("prompt_tokens_details"))
            cache_read = _count(details.get("cached_tokens", 0) or 0)
            cache_write = _count(details.get("cache_write_tokens", 0) or 0)
        server = _mapping(u.get("server_tool_use"))
        searches = _count(server.get("web_search_requests", 0) or 0)
        if output:
            searches = max(searches, sum(_mapping(row).get("type") == "web_search_call" for row in output))
        cost = cost_micros(self.model, input_count, output_count, searches,
            cache_read_tokens=cache_read, cache_write_tokens=cache_write, cache_write_1h_tokens=cache_1h)
        with self.scope.lock:
            self.scope.pending -= self.estimate
            self.scope.spent += cost
            self.scope.tokens_input += input_count
            self.scope.tokens_output += output_count
            self.scope.models.add(self.model)
            self.finished = True
            if self.scope.spent > self.scope.reserved_cost:
                # Wallet records the complete provider liability, caps user
                # debit at the reservation and blocks further account spending.
                raise AIUsageError("Consumo excedeu a estimativa e exige reconciliação.", 503)
        log.info("ai_request_usage operation=%s feature=%s model=%s input=%d output=%d searches=%d cost_micros=%d",
                 self.scope.operation_key, self.scope.feature, self.model, input_count, output_count, searches, cost)


@contextmanager
def paid_request(provider, request):
    current = _scope.get()
    if current is None:
        raise AIUsageError("Chamada paga sem conta ou centro de custo autorizado.", 403)
    estimate = estimate_request(provider, request)
    current.reserve(estimate, request["model"])
    meter = RequestMeter(current, request["model"], estimate, provider=provider, request=request)
    try:
        yield meter
    except BaseException as exc:
        status = getattr(exc, "status_code", None)
        if status is None:
            status = getattr(getattr(exc, "response", None), "status_code", None)
        # Only explicit provider request rejections are known not to be billed.
        if not meter.finished and status not in {400, 401, 403, 404, 422, 429}:
            current.unknown = True
        raise
    finally:
        if not meter.finished:
            with current.lock:
                current.pending -= meter.estimate
        if not meter.finished and not current.unknown:
            # Success without usable accounting is also uncertain.
            import sys
            if sys.exc_info()[0] is None:
                current.unknown = True


class MeteredSDK:
    """Transparent SDK resource proxy accounting each request and stream."""
    def __init__(self, resource, provider, path=()):
        self._resource, self._provider, self._path = resource, provider, path

    def __getattr__(self, name):
        value = getattr(self._resource, name)
        path = (*self._path, name)
        if name not in {"create", "stream"}:
            return MeteredSDK(value, self._provider, path)
        if name == "stream":
            @contextmanager
            def streaming(**kwargs):
                with paid_request(self._provider, kwargs) as meter:
                    with value(**kwargs) as stream:
                        yield stream
                        response = stream.get_final_message()
                        meter.finish(response.usage, output=getattr(response, "content", None))
            return streaming
        def invoke(**kwargs):
            if kwargs.get("stream"):
                def chunks():
                    with paid_request(self._provider, kwargs) as meter:
                        stream = value(**kwargs)
                        usage = None
                        try:
                            for chunk in stream:
                                if getattr(chunk, "usage", None) is not None:
                                    usage = chunk.usage
                                yield chunk
                            meter.finish(usage)
                        finally:
                            if hasattr(stream, "close"):
                                stream.close()
                return chunks()
            with paid_request(self._provider, kwargs) as meter:
                response = value(**kwargs)
                meter.finish(response.usage, output=getattr(response, "content", None))
                return response
        return invoke


def metered_responses_post(client, url, *, headers, json):
    request = dict(json)
    if any(str(t.get("type", "")).startswith("web_search") for t in request.get("tools", [])):
        request["max_tool_calls"] = min(int(request.get("max_tool_calls", 3)), 3)
    with paid_request("openai", request) as meter:
        response = client.post(url, headers=headers, json=request)
        response.raise_for_status()
        payload = response.json()
        meter.finish(payload.get("usage"), output=payload.get("output"))
        return response


def plan_rounds(provider, request, rounds, tool_result_bytes=20_000):
    """Reserve the bounded provider loop before its first paid request."""
    current = _scope.get()
    if current is None:
        raise AIUsageError("Chamada de IA sem conta responsável.", 403)
    estimate_request(provider, request)  # Validate the request before planning.
    if not isinstance(rounds, int) or isinstance(rounds, bool) or rounds <= 0 or tool_result_bytes < 0:
        raise AIUsageError("Limite de rodadas inválido.", 503)
    maximum_output = int(request.get("max_completion_tokens", request.get("max_output_tokens", request.get("max_tokens", 0))) or 0)
    searches = sum(int(t.get("max_uses", 3)) for t in request.get("tools", []) if str(t.get("type", "")).startswith("web_search"))
    inputs = input_token_bound(request, request["model"]) + 256 + searches * 25_000
    # Generated output is already a token bound. Tool text uses its UTF-8 byte
    # bound, with message framing headroom. Recompute each full round so that
    # crossing a long-context threshold reprices the complete input/output.
    # The actual serialized request is checked again immediately before egress.
    amount = sum(_reserve_cost(request["model"], inputs + i * (maximum_output + tool_result_bytes + 1024),
                               maximum_output, searches) for i in range(rounds))
    if current.reserved_cost:
        if amount + current.spent > current.reserved_cost:
            raise AIUsageError("As rodadas excedem o orçamento reservado.")
    else:
        current.planned_cost = max(current.planned_cost, amount)
        if amount > current.ceiling:
            raise AIUsageError("O orçamento das rodadas excede o teto da operação.")
    return amount


def plan_token_budgets(provider, budgets, *, requests=()):
    """Plan bounded future stages without constructing synthetic clinical text."""
    current = _scope.get()
    if current is None:
        raise AIUsageError("Operação sem conta responsável.", 403)
    amount = sum(_reserve_cost(b["model"], int(b["input_tokens"]), int(b["max_output_tokens"]),
                             int(b.get("web_searches", 0))) for b in budgets)
    amount += sum(estimate_request(provider, request) for request in requests)
    if current.reserved_cost:
        if amount + current.spent > current.reserved_cost:
            raise AIUsageError("Etapas excedem a reserva da operação.")
    else:
        current.planned_cost = max(current.planned_cost, amount)
        if amount > current.ceiling:
            raise AIUsageError("O orçamento completo excede o teto da operação.")
    return amount


def audio_duration(content, media_type):
    """Probe local media only; no remote protocols, no persistent clinical file."""
    import os
    import subprocess
    import tempfile
    formats = {"audio/ogg": "ogg", "audio/opus": "ogg", "audio/mpeg": "mp3",
               "audio/mp3": "mp3", "audio/wav": "wav", "audio/x-wav": "wav",
               "audio/mp4": "mov", "audio/aac": "aac", "audio/webm": "matroska"}
    fmt = formats.get(media_type.split(";", 1)[0].strip())
    if fmt is None:
        raise AIUsageError("Formato de áudio sem orçamento homologado.", 422)
    fd, path = tempfile.mkstemp(prefix="corvia-audio-budget-")
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(content)
        result = subprocess.run(["ffprobe", "-v", "error", "-protocol_whitelist", "file,pipe",
            "-f", fmt, "-show_entries", "format=duration", "-of", "json", path],
            capture_output=True, check=True, timeout=5, text=True)
        seconds = float(json.loads(result.stdout)["format"]["duration"])
        if not math.isfinite(seconds) or not 0 < seconds <= 600:
            raise ValueError("duration")
        return seconds
    except Exception as exc:
        raise AIUsageError("Não foi possível validar a duração do áudio (máximo 10 minutos).", 422) from exc
    finally:
        os.unlink(path)


def metered_transcription(client, *, model, content, filename, media_type):
    if model not in {"gpt-4o-mini-transcribe", "gpt-4o-transcribe"}:
        raise AIUsageError("Modelo de transcrição sem medição homologada.", 503)
    seconds = audio_duration(content, media_type)
    # 100 audio tokens/second is deliberately above normal transcription use;
    # both supported transcription models document a 2,000-token output limit.
    request = {"model": model, "input": "x" * (math.ceil(seconds * 100) + 1024),
               "max_output_tokens": 2_000}
    stream = BytesIO(content); stream.name = filename
    with paid_request("openai", request) as meter:
        result = client.audio.transcriptions.create(model=model, file=stream)
        meter.finish(getattr(result, "usage", None))
        return result


@contextmanager
def quote_scope(owner_id, feature):
    """Read-only monetary planning; paid egress is forbidden in this context."""
    if not isinstance(owner_id, int) or isinstance(owner_id, bool) or owner_id <= 0:
        raise AIUsageError("Conta inválida para cotação.", 403)
    current = UsageScope(owner_id, feature, quote_only=True)
    token = _scope.set(current)
    try:
        yield current
    finally:
        _scope.reset(token)


def set_approved_credit_limit(centavos):
    """Bind a trusted, persisted user approval to the current operation."""
    current = _scope.get()
    if current is None or not isinstance(centavos, int) or isinstance(centavos, bool) or centavos < 0:
        raise AIUsageError("Confirmação de orçamento inválida.", 403)
    if current.reserved_cost:
        raise AIUsageError("O limite aprovado deve ser definido antes da primeira chamada.", 409)
    current.approved_credit_centavos = centavos
