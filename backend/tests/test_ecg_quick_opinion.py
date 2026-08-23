"""Contrato do modo rápido: análise sem paciente e sem persistir o traçado."""
import io

from PIL import Image

from app.core.config import settings
from app.models.audit import AuditLog
from app.models.patient_profile import PatientProfile
from app.models.prontuario import PatientClinicalAISuggestion, PatientECGRecord
from app.models.subscription import Subscription
from app.services.ia import ecg_assist


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _subscribe(db, user) -> None:
    db.add(Subscription(user_id=user.id, kind="meucardio", plano="basico", status="ativo"))
    db.commit()


def _png() -> bytes:
    image = io.BytesIO()
    Image.new("RGB", (1200, 800), "white").save(image, format="PNG")
    return image.getvalue()


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
