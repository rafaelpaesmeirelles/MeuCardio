"""Contrato do modo rápido: análise sem paciente e sem persistir o traçado."""
import io
from types import SimpleNamespace

import httpx
import pytest
from app.services import ai_wallet
from app.services.ia.usage_control import MeteredSDK, ai_usage_scope
from PIL import Image

from app.core.config import settings
from app.models.audit import AuditLog
from app.models.patient_profile import PatientProfile
from app.models.prontuario import PatientClinicalAISuggestion, PatientECGRecord
from app.models.subscription import Subscription
from app.services.ia import ecg_assist
from app.services.ia.provedor import ProvedorAnthropic, ProvedorOpenAI, Resposta


@pytest.fixture
def metered_ecg_owner(monkeypatch):
    receipts = {"reserves": [], "settles": []}
    def reserve(**kwargs):
        receipts["reserves"].append(kwargs)
        return {"created": True}
    monkeypatch.setattr(ai_wallet, "reserve", reserve)
    monkeypatch.setattr(ai_wallet, "settle", lambda **kw: receipts["settles"].append(kw))
    monkeypatch.setattr(ai_wallet, "mark_unknown", lambda **kw: pytest.fail("unexpected unknown usage"))
    with ai_usage_scope(owner_id=1, feature="ecg_ai"):
        yield receipts


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _subscribe(db, user) -> None:
    db.add(Subscription(user_id=user.id, kind="meucardio", plano="basico", status="ativo"))
    db.commit()


def _png() -> bytes:
    image = io.BytesIO()
    Image.new("RGB", (1200, 800), "white").save(image, format="PNG")
    return image.getvalue()


def test_ecg_assist_passes_the_configured_model_to_the_provider(monkeypatch):
    class Provider:
        def analisar_arquivo_clinico(
            self, sistema, instrucao, conteudo, media_type, modelo=None,
        ):
            assert sistema == ecg_assist.SYSTEM_PROMPT
            assert instrucao == ecg_assist.INSTRUCTION
            assert conteudo == b"ecg"
            assert media_type == "image/jpeg"
            assert modelo == "vision-test"
            return Resposta(
                texto='{"quality":"limitada","summary":"Teste","rhythm":null,'
                '"heart_rate_bpm":null,"intervals":{"pr_ms":null,"qrs_ms":null,'
                '"qtc_ms":null},"axis":null,"conduction":null,"st_t":null,'
                '"other_findings":[],"red_flags":[],"limitations":["Teste"],'
                '"urgent_review_recommended":false}',
                tokens_entrada=10,
                tokens_saida=20,
                modelo="vision-test",
            )

    monkeypatch.setattr(ecg_assist, "obter_provedor", lambda: Provider())
    monkeypatch.setattr(settings, "ai_ecg_model", "vision-test")

    result = ecg_assist.analyze_ecg(b"ecg", "image/jpeg")

    assert result["model"] == "vision-test"
    assert result["payload"]["quality"] == "limitada"


def test_openai_ecg_uses_frontier_visual_default_and_retries_without_json_mode(monkeypatch, metered_ecg_owner):
    from openai import BadRequestError

    calls = []

    def create(**kwargs):
        calls.append(kwargs)
        if len(calls) == 1:
            request = httpx.Request("POST", "https://api.openai.com/v1/chat/completions")
            response = httpx.Response(400, request=request)
            raise BadRequestError("JSON mode indisponível", response=response, body={})
        return SimpleNamespace(
            usage=SimpleNamespace(prompt_tokens=10, completion_tokens=20),
            choices=[SimpleNamespace(
                message=SimpleNamespace(content='{"quality":"limitada"}'),
                finish_reason="stop",
            )],
        )

    provider = ProvedorOpenAI.__new__(ProvedorOpenAI)
    provider._modelo = "modelo-textual-do-chat"
    provider._cliente = MeteredSDK(SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=create)),
    ), "openai")
    monkeypatch.setattr(settings, "ai_max_output_tokens", 4096)

    response = provider.analisar_arquivo_clinico(
        "sistema", "instrucao", _png(), "image/png",
    )

    assert response.modelo == "gpt-5.6-sol"
    assert calls[0]["model"] == calls[1]["model"] == "gpt-5.6-sol"
    assert calls[0]["reasoning_effort"] == "high"
    assert calls[0]["max_completion_tokens"] == 4096
    assert calls[0]["messages"][1]["content"][1]["image_url"]["detail"] == "original"
    assert calls[0]["response_format"] == {"type": "json_object"}
    assert "response_format" not in calls[1]


def test_openai_ecg_falls_back_to_gpt4o_when_frontier_is_unavailable(monkeypatch, metered_ecg_owner):
    from openai import NotFoundError

    calls = []

    def create(**kwargs):
        calls.append(kwargs)
        if kwargs["model"] == "gpt-5.6-sol":
            request = httpx.Request("POST", "https://api.openai.com/v1/chat/completions")
            response = httpx.Response(404, request=request)
            raise NotFoundError("model_not_found", response=response, body={})
        return SimpleNamespace(
            usage=SimpleNamespace(prompt_tokens=12, completion_tokens=24),
            choices=[SimpleNamespace(
                message=SimpleNamespace(content='{"quality":"limitada"}'),
                finish_reason="stop",
            )],
        )

    provider = ProvedorOpenAI.__new__(ProvedorOpenAI)
    provider._modelo = "modelo-textual-do-chat"
    provider._cliente = MeteredSDK(SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=create)),
    ), "openai")
    monkeypatch.setattr(settings, "ai_max_output_tokens", 4096)

    response = provider.analisar_arquivo_clinico(
        "sistema", "instrucao", _png(), "image/png",
    )

    assert response.modelo == "gpt-4o"
    assert [call["model"] for call in calls] == ["gpt-5.6-sol", "gpt-4o"]
    assert calls[1]["messages"][1]["content"][1]["image_url"]["detail"] == "high"
    assert calls[1]["max_tokens"] == 4096
    assert calls[1]["temperature"] == 0


def test_openai_ecg_falls_back_to_gpt4o_after_frontier_bad_request(monkeypatch, metered_ecg_owner):
    from openai import BadRequestError

    calls = []

    def create(**kwargs):
        calls.append(kwargs)
        if kwargs["model"] == "gpt-5.6-sol":
            request = httpx.Request("POST", "https://api.openai.com/v1/chat/completions")
            response = httpx.Response(400, request=request)
            raise BadRequestError(
                "parâmetro ou acesso incompatível com o modelo",
                response=response,
                body={"error": {"type": "invalid_request_error"}},
            )
        return SimpleNamespace(
            usage=SimpleNamespace(prompt_tokens=12, completion_tokens=24),
            choices=[SimpleNamespace(
                message=SimpleNamespace(content='{"quality":"limitada"}'),
                finish_reason="stop",
            )],
        )

    provider = ProvedorOpenAI.__new__(ProvedorOpenAI)
    provider._modelo = "modelo-textual-do-chat"
    provider._cliente = MeteredSDK(SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=create)),
    ), "openai")
    monkeypatch.setattr(settings, "ai_max_output_tokens", 4096)

    response = provider.analisar_arquivo_clinico(
        "sistema", "instrucao", _png(), "image/png",
    )

    assert response.modelo == "gpt-4o"
    assert [call["model"] for call in calls] == [
        "gpt-5.6-sol",
        "gpt-5.6-sol",
        "gpt-4o",
    ]
    assert "response_format" in calls[0]
    assert "response_format" not in calls[1]
    assert calls[2]["messages"][1]["content"][1]["image_url"]["detail"] == "high"


def test_openai_ecg_ignores_anthropic_model_name(monkeypatch, metered_ecg_owner):
    calls = []

    def create(**kwargs):
        calls.append(kwargs)
        return SimpleNamespace(
            usage=SimpleNamespace(prompt_tokens=10, completion_tokens=20),
            choices=[SimpleNamespace(
                message=SimpleNamespace(content='{"quality":"limitada"}'),
                finish_reason="stop",
            )],
        )

    provider = ProvedorOpenAI.__new__(ProvedorOpenAI)
    provider._modelo = "gpt-4o-mini"
    provider._cliente = MeteredSDK(SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=create)),
    ), "openai")
    monkeypatch.setattr(settings, "ai_max_output_tokens", 4096)

    response = provider.analisar_arquivo_clinico(
        "sistema", "instrucao", _png(), "image/png", modelo="claude-sonnet-4-6",
    )

    assert response.modelo == "gpt-5.6-sol"
    assert calls[0]["model"] == "gpt-5.6-sol"


def test_anthropic_ecg_ignores_openai_model_name(monkeypatch, metered_ecg_owner):
    calls = []

    def create(**kwargs):
        calls.append(kwargs)
        return SimpleNamespace(
            usage=SimpleNamespace(input_tokens=11, output_tokens=22),
            content=[SimpleNamespace(type="text", text='{"quality":"limitada"}')],
            stop_reason="end_turn",
        )

    provider = ProvedorAnthropic.__new__(ProvedorAnthropic)
    provider._modelo = "claude-sonnet-4-6"
    provider._cliente = MeteredSDK(SimpleNamespace(messages=SimpleNamespace(create=create)), "anthropic")
    monkeypatch.setattr(settings, "ai_max_output_tokens", 4096)

    response = provider.analisar_arquivo_clinico(
        "sistema", "instrucao", _png(), "image/png", modelo="gpt-5.6-sol",
    )

    assert response.modelo == "claude-sonnet-4-6"
    assert calls[0]["model"] == "claude-sonnet-4-6"
    assert calls[0]["messages"][0]["content"][0]["type"] == "image"


def test_anthropic_ecg_falls_back_from_rejected_claude_model(monkeypatch, metered_ecg_owner):
    from anthropic import BadRequestError

    calls = []

    def create(**kwargs):
        calls.append(kwargs)
        if kwargs["model"] == "claude-sonnet-5":
            request = httpx.Request("POST", "https://api.anthropic.com/v1/messages")
            response = httpx.Response(400, request=request)
            raise BadRequestError("model not available", response=response, body={})
        return SimpleNamespace(
            usage=SimpleNamespace(input_tokens=11, output_tokens=22),
            content=[SimpleNamespace(type="text", text='{"quality":"limitada"}')],
            stop_reason="end_turn",
        )

    provider = ProvedorAnthropic.__new__(ProvedorAnthropic)
    provider._modelo = "claude-sonnet-4-6"
    provider._cliente = MeteredSDK(SimpleNamespace(messages=SimpleNamespace(create=create)), "anthropic")
    monkeypatch.setattr(settings, "ai_max_output_tokens", 4096)

    response = provider.analisar_arquivo_clinico(
        "sistema",
        "instrucao",
        _png(),
        "image/png",
        modelo="claude-sonnet-5",
    )

    assert response.modelo == "claude-sonnet-4-6"
    assert [call["model"] for call in calls] == [
        "claude-sonnet-5",
        "claude-sonnet-4-6",
    ]


def test_quick_ecg_returns_transient_opinion_without_patient_record(
    client, db, criar_usuario, monkeypatch,
):
    doctor, token = criar_usuario(email="ecg-rapido@teste.local")
    _subscribe(db, doctor)
    monkeypatch.setattr(settings, "ai_enabled", True)
    monkeypatch.setattr(settings, "ai_clinical_multimodal_enabled", True)
    monkeypatch.setattr(settings, "openai_api_key", "test-key")
    ecg_bytes = _png()

    def _analysis(content: bytes, media_type: str) -> dict:
        assert content == ecg_bytes
        assert media_type == "image/png"
        return {
            "payload": {
                "quality": "adequada",
                "summary": "Ritmo sinusal, FC aproximada de 72 bpm.",
                "rhythm": "Ritmo sinusal",
                "heart_rate_bpm": 72,
                "intervals": {"pr_ms": 160, "qrs_ms": 90, "qtc_ms": 420},
                "axis": "Normal",
                "conduction": "Sem bloqueio evidente",
                "st_t": "Sem supradesnivelamento evidente",
                "other_findings": [],
                "red_flags": [],
                "limitations": ["Confirmar calibração no original"],
                "urgent_review_recommended": False,
                "disclaimer": "Sugestão gerada por IA; requer revisão médica.",
            },
            "provider": "test",
            "model": "vision-test",
            "prompt_version": "ecg-test-v1",
            "tokens_input": 100,
            "tokens_output": 50,
        }

    monkeypatch.setattr(ecg_assist, "analyze_ecg", _analysis)
    status = client.get("/api/ecg-ia/status", headers=_headers(token))
    assert status.status_code == 200
    assert status.json() == {
        "enabled": True,
        "unavailable_reason": None,
        "supported_media_types": ["image/jpeg", "image/png", "image/webp"],
        "max_size_bytes": 20 * 1024 * 1024,
        "stores_file": False,
    }

    missing_consent = client.post(
        "/api/ecg-ia/analisar",
        headers=_headers(token),
        files={"arquivo": ("ecg.png", ecg_bytes, "image/png")},
    )
    assert missing_consent.status_code == 422

    refused_consent = client.post(
        "/api/ecg-ia/analisar",
        headers=_headers(token),
        files={"arquivo": ("ecg.png", ecg_bytes, "image/png")},
        data={"confirm_external_processing": "false"},
    )
    assert refused_consent.status_code == 422

    response = client.post(
        "/api/ecg-ia/analisar",
        headers=_headers(token),
        files={"arquivo": ("ecg.png", ecg_bytes, "image/png")},
        data={"confirm_external_processing": "true"},
    )
    assert response.status_code == 200, response.text
    assert response.json()["stored"] is False
    assert response.json()["payload"]["rhythm"] == "Ritmo sinusal"

    db.expire_all()
    assert db.query(PatientProfile).count() == 0
    assert db.query(PatientECGRecord).count() == 0
    assert db.query(PatientClinicalAISuggestion).count() == 0
    attempt = db.query(AuditLog).filter_by(action="ai_ecg_transfer_attempt").one()
    outcome = db.query(AuditLog).filter_by(action="ai_ecg_transfer_outcome").one()
    assert attempt.entity == outcome.entity == "ecg_quick_opinion"
    assert attempt.detail["stores_file"] is False
    assert outcome.detail["status"] == "success"
    audit_text = str(attempt.detail) + str(outcome.detail)
    assert "ecg.png" not in audit_text
    assert "Ritmo sinusal" not in audit_text


def test_anthropic_ecg_reserves_more_expensive_fallback_before_call(monkeypatch, metered_ecg_owner):
    from anthropic import BadRequestError
    from app.services.ia.usage_control import cost_micros
    calls = []
    def create(**kwargs):
        calls.append(kwargs)
        if len(calls) == 1:
            response = httpx.Response(400, request=httpx.Request("POST", "https://api.anthropic.com/v1/messages"))
            raise BadRequestError("model unavailable", response=response, body={})
        return SimpleNamespace(
            usage=SimpleNamespace(input_tokens=11, output_tokens=22),
            content=[SimpleNamespace(type="text", text='{"quality":"limitada"}')],
            stop_reason="end_turn")
    provider = ProvedorAnthropic.__new__(ProvedorAnthropic)
    provider._modelo = "claude-sonnet-5"
    provider._cliente = MeteredSDK(SimpleNamespace(messages=SimpleNamespace(create=create)), "anthropic")
    with ai_usage_scope(owner_id=2, feature="ecg_ai"):
        result = provider.analisar_arquivo_clinico("sistema", "instrucao", _png(), "image/png")
    assert [call["model"] for call in calls] == ["claude-sonnet-5", "claude-sonnet-4-6"]
    assert result.modelo == "claude-sonnet-4-6"
    assert len(metered_ecg_owner["reserves"]) == 1
    assert metered_ecg_owner["settles"][0]["actual_cost_micros"] == cost_micros("claude-sonnet-4-6", 11, 22)


@pytest.mark.parametrize("provider_type,model", [(ProvedorOpenAI,"gpt-5.6-sol"), (ProvedorAnthropic,"claude-sonnet-5")])
def test_ecg_insufficient_allowance_blocks_all_attempts(monkeypatch, metered_ecg_owner, provider_type, model):
    from app.services.ia.usage_control import AIUsageError
    calls = []
    def create(**kwargs):
        calls.append(kwargs)
        raise AssertionError("Provider must not run without a reservation")
    def refuse(**kwargs):
        raise AIUsageError("Saldo insuficiente")
    monkeypatch.setattr(ai_wallet, "reserve", refuse)
    provider = provider_type.__new__(provider_type)
    provider._modelo = model
    provider_name = "anthropic" if provider_type is ProvedorAnthropic else "openai"
    raw = SimpleNamespace(messages=SimpleNamespace(create=create),
                          chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
    provider._cliente = MeteredSDK(raw, provider_name)
    with pytest.raises(AIUsageError) as caught:
        provider.analisar_arquivo_clinico("sistema", "instrucao", _png(), "image/png")
    assert caught.value.status_code == 402
    assert calls == []
