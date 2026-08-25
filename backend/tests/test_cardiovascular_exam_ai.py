"""Contrato da central transitória de IA para exames cardiovasculares."""
from __future__ import annotations

import io
import json

import pytest
from PIL import Image
from PIL.PngImagePlugin import PngInfo

from app.api import cardiovascular_exam_ai
from app.core.config import settings
from app.models.audit import AuditLog
from app.models.patient_profile import PatientProfile
from app.models.prontuario import PatientClinicalAISuggestion, PatientECGRecord
from app.models.subscription import Subscription
from app.services.ia import cardiovascular_exam_assist, ecg_assist
from app.services.ia import clinical_file_sanitizer
from app.services.ia.cardiovascular_exam_assist import (
    ClinicalFile,
    EvidenceSynthesis,
    ManagementOption,
)


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _subscribe(db, user) -> None:
    db.add(Subscription(user_id=user.id, kind="meucardio", plano="basico", status="ativo"))
    db.commit()


def _png(color: tuple[int, int, int] = (255, 255, 255)) -> bytes:
    output = io.BytesIO()
    Image.new("RGB", (80, 60), color=color).save(output, format="PNG")
    return output.getvalue()


def test_sanitizador_remove_metadados_da_imagem(monkeypatch):
    output = io.BytesIO()
    metadata = PngInfo()
    metadata.add_text("Description", "Nome: Paciente Exemplo")
    Image.new("RGB", (80, 60), "white").save(output, format="PNG", pnginfo=metadata)
    monkeypatch.setattr(clinical_file_sanitizer, "_ocr", lambda _content: "")

    sanitized, media_type = clinical_file_sanitizer.sanitize_clinical_file(output.getvalue(), "image/png")

    assert media_type == "image/png"
    assert b"Paciente Exemplo" not in sanitized
    with Image.open(io.BytesIO(sanitized)) as image:
        assert image.info == {}


def test_sanitizador_rejeita_identificador_visivel(monkeypatch):
    monkeypatch.setattr(clinical_file_sanitizer, "_ocr", lambda _content: "Nome: Paciente Exemplo")
    with pytest.raises(clinical_file_sanitizer.UnsafeClinicalFile):
        clinical_file_sanitizer.sanitize_clinical_file(_png(), "image/png")


@pytest.mark.parametrize("ocr_text", [
    "Paciente Joao Silva", "PATIENT JOHN DOE", "MRN 12345678", "CNS 123456789012345",
    "JOAO DA SILVA",
])
def test_sanitizador_rejeita_cabecalhos_sem_delimitador(monkeypatch, ocr_text):
    monkeypatch.setattr(clinical_file_sanitizer, "_ocr", lambda _content: ocr_text)
    with pytest.raises(clinical_file_sanitizer.UnsafeClinicalFile):
        clinical_file_sanitizer.sanitize_clinical_file(_png(), "image/png")


def test_sanitizador_textual_rejeita_identificador_e_normaliza_utf8():
    with pytest.raises(clinical_file_sanitizer.UnsafeClinicalFile):
        clinical_file_sanitizer.sanitize_clinical_file(
            b"Nome: Paciente Exemplo\nTroponina: 20 ng/L",
            "text/plain",
        )

    sanitized, media_type = clinical_file_sanitizer.sanitize_clinical_file(
        b"\xef\xbb\xbfTroponina: 20 ng/L",
        "text/plain",
    )
    assert sanitized == b"Troponina: 20 ng/L"
    assert media_type == "text/plain"


def test_conduta_acionavel_ou_com_dose_e_rejeitada():
    common = {
        "rationale": "Possibilidade respaldada pela fonte.", "urgency": "condicional",
        "evidence_level": None, "prerequisites": [], "contraindications": [],
        "source_urls": ["https://www.escardio.org/guideline"],
    }
    with pytest.raises(ValueError):
        ManagementOption.model_validate({"action": "Administrar medicamento", **common})
    with pytest.raises(ValueError):
        ManagementOption.model_validate({"action": "Considerar medicamento 5 mg", **common})


def _payload() -> dict:
    return {
        "exam_type": "Ecocardiograma",
        "quality": "adequada",
        "executive_summary": "Achados de teste sem dado identificável.",
        "report_interpretation": None,
        "image_analysis": [{"file_id": "arquivo-1", "observation": "Imagem recebida.", "confidence": "moderada"}],
        "measurements": [],
        "integrated_impression": ["Impressão integrada de teste."],
        "differential_diagnoses": [],
        "red_flags": [],
        "suggested_additional_tests": [],
        "possible_management": [],
        "guidelines": [],
        "limitations": ["Exige revisão médica do exame original."],
        "urgency_assessment": "absent",
        "urgent_review_recommended": False,
        "disclaimer": "Análise assistiva; requer revisão médica.",
    }


def _analysis() -> dict:
    return {
        "payload": _payload(),
        "web_sources": [{"url": "https://example.org/guideline", "title": "Diretriz", "cited": False}],
        "provider": "openai",
        "model": "modelo-multimodal-teste",
        "prompt_version": "cardiovascular-test-v1",
        "tokens_input": 120,
        "tokens_output": 80,
    }


def _enable(monkeypatch) -> None:
    monkeypatch.setattr(settings, "ai_enabled", True)
    monkeypatch.setattr(settings, "ai_clinical_multimodal_enabled", True)
    monkeypatch.setattr(settings, "ai_clinical_data_controls_approved", True)
    monkeypatch.setattr(settings, "ai_provider", "openai")
    monkeypatch.setattr(settings, "openai_api_key", "test-key")


def test_status_expoe_capacidade_multiarquivo_sem_promessa_de_persistencia(
    client, db, criar_usuario, monkeypatch,
):
    doctor, token = criar_usuario(email="status-exames@teste.local")
    _subscribe(db, doctor)
    _enable(monkeypatch)

    response = client.get("/api/exames-ia/status", headers=_headers(token))

    assert response.status_code == 200
    body = response.json()
    assert body["enabled"] is True
    assert body["unavailable_reason"] is None
    assert body["max_files"] == 5
    assert body["max_file_bytes"] == 20 * 1024 * 1024
    assert body["max_total_bytes"] == 40 * 1024 * 1024
    assert body["persists_files_in_corvia"] is False
    assert body["provider_response_storage_requested"] is False
    assert body["external_processor"] == "openai"
    assert body["consent_version"] == cardiovascular_exam_ai.CONSENT_VERSION
    assert body["searches_current_guidelines"] is True
    assert body["raw_dicom_supported"] is False
    assert body["video_supported"] is False
    assert {"image/jpeg", "image/png", "application/pdf"}.issubset(body["supported_media_types"])
    assert "echocardiogram" in body["exam_types"]


def test_status_falha_fechado_sem_aprovacao_dos_controles_de_dados(
    client, db, criar_usuario, monkeypatch,
):
    doctor, token = criar_usuario(email="controles-dados-exames@teste.local")
    _subscribe(db, doctor)
    _enable(monkeypatch)
    monkeypatch.setattr(settings, "ai_clinical_data_controls_approved", False)

    response = client.get("/api/exames-ia/status", headers=_headers(token))
    analysis = client.post(
        "/api/exames-ia/analisar",
        headers=_headers(token),
        data={
            "exam_type": "laboratory",
            "clinical_context": "Dispneia aos esforços, sem dados identificadores.",
            "confirm_external_processing": "true",
            "confirm_deidentified": "true",
            "consent_version": cardiovascular_exam_ai.CONSENT_VERSION,
        },
    )

    assert response.status_code == 200
    assert response.json()["enabled"] is False
    assert response.json()["unavailable_reason"] == "data_controls_not_approved"
    assert analysis.status_code == 503
    assert db.query(AuditLog).filter_by(action="ai_clinical_exam_transfer_attempt").count() == 0


def test_analise_exige_os_dois_consentimentos(
    client, db, criar_usuario, monkeypatch,
):
    doctor, token = criar_usuario(email="consentimento-exames@teste.local")
    _subscribe(db, doctor)
    _enable(monkeypatch)

    common = {
        "exam_type": "laboratory",
        "clinical_context": "Dispneia aos esforços, sem dados identificadores.",
        "consent_version": cardiovascular_exam_ai.CONSENT_VERSION,
    }
    missing = client.post(
        "/api/exames-ia/analisar",
        headers=_headers(token),
        data=common,
    )
    external_refused = client.post(
        "/api/exames-ia/analisar",
        headers=_headers(token),
        data={
            **common,
            "confirm_external_processing": "false",
            "confirm_deidentified": "true",
        },
    )
    deidentification_refused = client.post(
        "/api/exames-ia/analisar",
        headers=_headers(token),
        data={
            **common,
            "confirm_external_processing": "true",
            "confirm_deidentified": "false",
        },
    )

    assert missing.status_code == 422
    assert external_refused.status_code == 422
    assert deidentification_refused.status_code == 422
    assert db.query(AuditLog).filter_by(action="ai_clinical_exam_transfer_attempt").count() == 0


def test_analise_rejeita_versao_de_consentimento_desatualizada(
    client, db, criar_usuario, monkeypatch,
):
    doctor, token = criar_usuario(email="consentimento-antigo-exames@teste.local")
    _subscribe(db, doctor)
    _enable(monkeypatch)

    response = client.post(
        "/api/exames-ia/analisar",
        headers=_headers(token),
        data={
            "exam_type": "laboratory",
            "clinical_context": "Dispneia aos esforços, sem dados identificadores.",
            "confirm_external_processing": "true",
            "confirm_deidentified": "true",
            "consent_version": "clinical-ai-external-processing-v1-antiga",
        },
    )

    assert response.status_code == 422
    assert "termo atual" in response.json()["detail"]
    assert db.query(AuditLog).filter_by(action="ai_clinical_exam_transfer_attempt").count() == 0


def test_identificador_direto_e_bloqueado_antes_de_auditoria_ou_provedor(
    client, db, criar_usuario, monkeypatch,
):
    doctor, token = criar_usuario(email="desidentificacao-exames@teste.local")
    _subscribe(db, doctor)
    _enable(monkeypatch)
    called = False

    def _must_not_run(*_args, **_kwargs):
        nonlocal called
        called = True
        raise AssertionError("O provedor não pode receber PHI detectável.")

    monkeypatch.setattr(cardiovascular_exam_assist, "analyze_exam", _must_not_run)
    response = client.post(
        "/api/exames-ia/analisar",
        headers=_headers(token),
        data={
            "exam_type": "laboratory",
            "clinical_context": "Nome: Paciente Exemplo; troponina elevada.",
            "confirm_external_processing": "true",
            "confirm_deidentified": "true",
            "consent_version": cardiovascular_exam_ai.CONSENT_VERSION,
        },
    )

    assert response.status_code == 422
    assert "Remova identificadores diretos" in response.json()["detail"]
    assert called is False
    assert db.query(AuditLog).filter_by(action="ai_clinical_exam_transfer_attempt").count() == 0


def test_multiplos_arquivos_exigem_confirmacao_de_mesmo_caso(
    client, db, criar_usuario, monkeypatch,
):
    doctor, token = criar_usuario(email="mesmo-caso-exames@teste.local")
    _subscribe(db, doctor)
    _enable(monkeypatch)
    response = client.post(
        "/api/exames-ia/analisar", headers=_headers(token),
        files=[
            ("arquivos", ("um.png", _png(), "image/png")),
            ("arquivos", ("dois.png", _png((230, 230, 230)), "image/png")),
        ],
        data={
            "exam_type": "ecg", "confirm_external_processing": "true",
            "confirm_deidentified": "true", "confirm_same_case": "false",
            "consent_version": cardiovascular_exam_ai.CONSENT_VERSION,
        },
    )
    assert response.status_code == 422
    assert "mesmo caso" in response.json()["detail"]
    assert db.query(AuditLog).filter_by(action="ai_clinical_exam_transfer_attempt").count() == 0


def test_multiplas_fotos_sao_transitorias_e_auditoria_nao_contem_phi(
    client, db, criar_usuario, monkeypatch,
):
    doctor, token = criar_usuario(email="multifoto-exames@teste.local")
    _subscribe(db, doctor)
    _enable(monkeypatch)
    # Este é um teste do contrato HTTP/auditoria. A integração do sanitizador
    # com o OCR tem testes próprios e não deve depender do Tesseract do runner.
    monkeypatch.setattr(clinical_file_sanitizer, "_ocr", lambda _content: "")
    first = _png((255, 255, 255))
    second = _png((220, 230, 240))
    received: dict[str, object] = {}

    def _analyze(files, exam_type, clinical_question, report_text, clinical_context):
        received.update({
            "files": files,
            "exam_type": exam_type,
            "clinical_question": clinical_question,
            "report_text": report_text,
            "clinical_context": clinical_context,
        })
        return _analysis()

    monkeypatch.setattr(cardiovascular_exam_assist, "analyze_exam", _analyze)
    response = client.post(
        "/api/exames-ia/analisar",
        headers=_headers(token),
        files=[
            ("arquivos", ("eco-apical-paciente.png", first, "image/png")),
            ("arquivos", ("eco-paraesternal-paciente.png", second, "image/png")),
        ],
        data={
            "exam_type": "echocardiogram",
            "clinical_question": "Avaliar função ventricular e valvopatias.",
            "report_text": "FEVE estimada em 45%, sem identificação.",
            "clinical_context": "Dispneia NYHA II, sem identificação.",
            "confirm_external_processing": "true",
            "confirm_deidentified": "true",
            "confirm_same_case": "true",
            "consent_version": cardiovascular_exam_ai.CONSENT_VERSION,
            "file_notes": '["apical", "paraesternal"]',
        },
    )

    assert response.status_code == 200, response.text
    assert response.json()["persisted_in_corvia"] is False
    assert response.json()["provider_response_storage_requested"] is False
    assert "stored" not in response.json()
    assert response.json()["payload"]["exam_type"] == "Ecocardiograma"
    files = received["files"]
    assert all(item.content.startswith(b"\x89PNG\r\n\x1a\n") for item in files)
    assert [item.media_type for item in files] == ["image/png", "image/png"]
    assert [item.file_id for item in files] == ["arquivo-1", "arquivo-2"]
    assert [item.label for item in files] == ["apical", "paraesternal"]

    db.expire_all()
    assert db.query(PatientProfile).count() == 0
    assert db.query(PatientECGRecord).count() == 0
    assert db.query(PatientClinicalAISuggestion).count() == 0
    attempt = db.query(AuditLog).filter_by(action="ai_clinical_exam_transfer_attempt").one()
    outcome = db.query(AuditLog).filter_by(action="ai_clinical_exam_transfer_outcome").one()
    assert attempt.detail["file_count"] == 2
    assert attempt.detail["media_types"] == ["image/png", "image/png"]
    assert attempt.detail["total_size_bytes"] == len(first) + len(second)
    assert attempt.detail["persists_files_in_corvia"] is False
    assert attempt.detail["provider_response_storage_requested"] is False
    assert attempt.detail["consent_version"] == cardiovascular_exam_ai.CONSENT_VERSION
    assert len(attempt.detail["consent_payload_sha256"]) == 64
    assert outcome.detail["status"] == "success"
    audit_text = json.dumps([attempt.detail, outcome.detail], ensure_ascii=False)
    for forbidden in (
        "eco-apical-paciente.png",
        "eco-paraesternal-paciente.png",
        "FEVE estimada",
        "Dispneia NYHA",
        "Avaliar função ventricular",
        "Achados de teste",
    ):
        assert forbidden not in audit_text


def test_cota_diaria_e_compartilhada_com_ecg_legado(
    client, db, criar_usuario, monkeypatch,
):
    doctor, token = criar_usuario(email="cota-exames@teste.local")
    _subscribe(db, doctor)
    _enable(monkeypatch)
    monkeypatch.setattr(settings, "ai_daily_limit", 1)
    db.add(AuditLog(
        user_id=doctor.id,
        action="ai_ecg_transfer_attempt",
        entity="ecg_quick_opinion",
        entity_id=str(doctor.id),
        detail={"status": "reserved"},
    ))
    db.commit()

    response = client.post(
        "/api/exames-ia/analisar",
        headers=_headers(token),
        data={
            "exam_type": "laboratory",
            "clinical_context": "Dor torácica sem dados identificadores.",
            "confirm_external_processing": "true",
            "confirm_deidentified": "true",
            "consent_version": cardiovascular_exam_ai.CONSENT_VERSION,
        },
    )

    assert response.status_code == 429
    assert "Limite diário" in response.json()["detail"]
    assert db.query(AuditLog).filter_by(action="ai_clinical_exam_transfer_attempt").count() == 0


def test_cota_compartilhada_tambem_bloqueia_ecg_apos_uso_da_central(
    client, db, criar_usuario, monkeypatch,
):
    """Evita contornar a cota no sentido central ampla -> ECG legado."""
    doctor, token = criar_usuario(email="cota-reversa-exames@teste.local")
    _subscribe(db, doctor)
    _enable(monkeypatch)
    monkeypatch.setattr(settings, "ai_daily_limit", 1)
    db.add(AuditLog(
        user_id=doctor.id,
        action="ai_clinical_exam_transfer_attempt",
        entity="cardiovascular_exam_quick_analysis",
        entity_id=str(doctor.id),
        detail={"status": "reserved"},
    ))
    db.commit()

    monkeypatch.setattr(ecg_assist, "analyze_ecg", lambda *_args: {
        "payload": {
            "quality": "limitada",
            "summary": "Resultado que não deve ser solicitado ao provedor.",
            "rhythm": None,
            "heart_rate_bpm": None,
            "intervals": {"pr_ms": None, "qrs_ms": None, "qtc_ms": None},
            "axis": None,
            "conduction": None,
            "st_t": None,
            "other_findings": [],
            "red_flags": [],
            "limitations": ["Teste"],
            "urgent_review_recommended": False,
        },
        "provider": "openai",
        "model": "modelo-teste",
        "prompt_version": "ecg-test-v1",
        "tokens_input": 1,
        "tokens_output": 1,
    })
    response = client.post(
        "/api/ecg-ia/analisar",
        headers=_headers(token),
        files={"arquivo": ("ecg.png", _png(), "image/png")},
        data={"confirm_external_processing": "true"},
    )

    assert response.status_code == 429
    assert "Limite diário" in response.json()["detail"]


def test_parser_da_responses_reune_fontes_e_remove_duplicatas():
    text, sources, searches = cardiovascular_exam_assist._response_text_and_sources({
        "output": [
            {
                "type": "web_search_call",
                "action": {
                    "sources": [
                        {"url": "https://www.escardio.org/guideline", "title": "Diretriz oficial"},
                    ],
                },
            },
            {
                "type": "message",
                "content": [{
                    "type": "output_text",
                    "text": '{"exam_type":"teste"}',
                    "annotations": [
                        {
                            "type": "url_citation",
                            "url": "https://www.escardio.org/guideline",
                            "title": "Diretriz duplicada",
                        },
                        {
                            "type": "url_citation",
                            "url": "https://pubmed.ncbi.nlm.nih.gov/12345/",
                            "title": "Estudo primário",
                        },
                    ],
                }],
            },
        ],
    })

    assert text == '{"exam_type":"teste"}'
    assert searches == 1
    assert sources == [
        {"url": "https://www.escardio.org/guideline", "title": "Diretriz oficial", "cited": True},
        {"url": "https://pubmed.ncbi.nlm.nih.gov/12345/", "title": "Estudo primário", "cited": True},
    ]


def test_parser_descarta_fontes_fora_dos_dominios_oficiais():
    text, sources, searches = cardiovascular_exam_assist._response_text_and_sources({
        "output": [
            {
                "type": "web_search_call",
                "status": "completed",
                "action": {"sources": [
                    {"url": "https://blog.example/guideline", "title": "Blog"},
                    {"url": "http://www.escardio.org/inseguro", "title": "Sem TLS"},
                    {"url": "https://evil-escardio.org/falso", "title": "Domínio parecido"},
                    {"url": "https://www.escardio.org/oficial#secao", "title": "Oficial"},
                ]},
            },
            {"type": "message", "content": [{
                "type": "output_text", "text": "{}", "annotations": [],
            }]},
        ],
    })

    assert text == "{}"
    assert searches == 1
    assert sources == [{"url": "https://www.escardio.org/oficial", "title": "Oficial", "cited": False}]


def test_evidencia_exige_url_oficial_efetivamente_retornada_pela_busca():
    evidence = EvidenceSynthesis.model_validate({
        "possible_management": [{
            "action": "Considerar avaliação adicional",
            "rationale": "Possibilidade condicionada à confirmação clínica.",
            "urgency": "condicional",
            "evidence_level": None,
            "prerequisites": ["Confirmar os dados do exame"],
            "contraindications": [],
            "source_urls": ["https://www.escardio.org/outra-diretriz"],
        }],
        "guidelines": [],
        "evidence_limitations": [],
    })

    with pytest.raises(ValueError, match="Conduta sem vínculo"):
        cardiovascular_exam_assist._validate_evidence(evidence, [{
            "url": "https://www.escardio.org/diretriz-consultada",
            "title": "Diretriz consultada",
            "cited": True,
        }])


def test_evidencia_rejeita_fonte_recuperada_mas_nao_citada():
    evidence = EvidenceSynthesis.model_validate({
        "possible_management": [{
            "action": "Considerar avaliação adicional",
            "rationale": "Possibilidade condicionada à confirmação clínica.",
            "urgency": "condicional", "evidence_level": None,
            "prerequisites": [], "contraindications": [],
            "source_urls": ["https://www.escardio.org/guideline"],
        }],
        "guidelines": [], "evidence_limitations": [],
    })
    with pytest.raises(ValueError, match="Conduta sem vínculo"):
        cardiovascular_exam_assist._validate_evidence(evidence, [{
            "url": "https://www.escardio.org/guideline", "title": "Recuperada", "cited": False,
        }])


def test_responses_envia_multiplos_arquivos_com_store_false(monkeypatch):
    captured: dict[str, object] = {"requests": []}
    clinical_payload = {key: value for key, value in _payload().items() if key not in {
        "possible_management", "guidelines", "disclaimer", "urgent_review_recommended",
    }}
    source_url = "https://www.escardio.org/guideline"
    evidence_payload = {
        "possible_management": [],
        "guidelines": [{
            "organization": "ESC",
            "title": "Diretriz oficial de teste",
            "year": 2024,
            "url": source_url,
            "evidence_summary": "Síntese assistiva vinculada à fonte citada.",
            "section_or_page": None,
            # Mesmo que o modelo os devolva, o serviço não os publica sem
            # conferência humana do documento integral.
            "recommendation_class": "I",
            "evidence_level": "A",
        }],
        "evidence_limitations": [],
    }

    def raw_response(payload: dict, *, with_search: bool) -> dict:
        output = []
        if with_search:
            output.append({"type": "web_search_call", "status": "completed", "action": {
                "sources": [{"url": source_url, "title": "Diretriz"}],
            }})
        output.append({"type": "message", "content": [{
            "type": "output_text",
            "text": json.dumps(payload),
            "annotations": ([{
                "type": "url_citation", "url": source_url, "title": "Diretriz",
            }] if with_search else []),
        }]})
        return {"status": "completed", "model": "modelo-retornado", "output": output,
                "usage": {"input_tokens": 10, "output_tokens": 5}}

    class FakeResponse:
        def raise_for_status(self):
            return None

        def __init__(self, payload):
            self.payload = payload

        def json(self):
            return self.payload

    class FakeClient:
        def __init__(self, **kwargs):
            captured["client_kwargs"] = kwargs

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def post(self, url, *, headers, json):
            captured.update({"url": url, "headers": headers})
            captured["requests"].append(json)
            with_search = "tools" in json
            return FakeResponse(raw_response(evidence_payload if with_search else clinical_payload, with_search=with_search))

    _enable(monkeypatch)
    monkeypatch.setattr(settings, "ai_cardiovascular_exam_model", "modelo-configurado")
    monkeypatch.setattr(cardiovascular_exam_assist.httpx, "Client", FakeClient)
    result = cardiovascular_exam_assist.analyze_exam(
        [
            ClinicalFile(content=b"imagem-1", media_type="image/jpeg", file_id="arquivo-1", label="apical"),
            ClinicalFile(content=b"%PDF-1.4\n%%EOF", media_type="application/pdf", file_id="arquivo-2", label="laudo"),
        ],
        "echocardiogram",
        "Qual a impressão integrada?",
        "Laudo desidentificado.",
        "Contexto desidentificado.",
    )

    clinical_request, evidence_request = captured["requests"]
    assert captured["url"] == cardiovascular_exam_assist.RESPONSES_URL
    assert clinical_request["model"] == "modelo-configurado"
    assert clinical_request["store"] is False
    assert "tools" not in clinical_request
    assert evidence_request["store"] is False
    assert evidence_request["tools"][0]["filters"]["allowed_domains"]
    assert evidence_request["include"] == ["web_search_call.action.sources"]
    content = clinical_request["input"][0]["content"]
    assert [item["type"] for item in content] == ["input_text", "input_image", "input_file"]
    assert content[1]["image_url"].startswith("data:image/jpeg;base64,")
    assert content[2]["filename"] == "arquivo-2.pdf"
    assert content[2]["file_data"].startswith("data:application/pdf;base64,")
    assert result["web_sources"] == [{"url": source_url, "title": "Diretriz", "cited": True}]
    assert result["tokens_input"] == 20
    assert result["tokens_output"] == 10
    assert result["payload"]["guidelines"][0]["evidence_summary"] == (
        "Síntese assistiva vinculada à fonte citada."
    )
    assert result["payload"]["guidelines"][0]["recommendation_class"] is None
    assert result["payload"]["guidelines"][0]["evidence_level"] is None
    assert result["payload"]["disclaimer"].startswith("Análise assistiva gerada por IA")
