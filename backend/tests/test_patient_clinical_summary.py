"""Um cenário integrado cobre resumo, resultados e timeline longitudinal."""
import io
from datetime import datetime, timezone

import pytest
from PIL import Image
from pydantic import ValidationError

from app.api.patient_profiles import _operational_day_utc_bounds
from app.core.config import settings
from app.models.audit import AuditLog
from app.models.lab_test import LabTest
from app.models.prontuario import (
    PatientClinicalAISuggestion, PatientClinicalItem, PatientECGRecord, PatientExamResult,
)
from app.models.subscription import Subscription
from app.services import cofre
from app.services.ia import ecg_assist


def _h(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _assinar(db, *users) -> None:
    db.add_all([Subscription(user_id=u.id, kind="meucardio", plano="basico", status="ativo") for u in users])
    db.commit()


def test_resumo_clinico_cifra_preserva_historico_e_isola_medicos(
    client, db, criar_usuario, monkeypatch, tmp_path,
):
    medico, token = criar_usuario(email="resumo-a@teste.local")
    intruso, token_intruso = criar_usuario(email="resumo-b@teste.local")
    _assinar(db, medico, intruso)

    perfil = client.post("/api/pacientes", headers=_h(token), json={"full_name": "Paciente Resumo"})
    assert perfil.status_code == 201
    pid = perfil.json()["id"]
    atendimento = client.post(
        f"/api/pacientes/{pid}/atendimentos", headers=_h(token),
        json={"encounter_type": "consulta", "chief_complaint": "Retorno"},
    )
    assert atendimento.status_code == 201
    eid = atendimento.json()["id"]

    base = f"/api/pacientes/{pid}/resumo-clinico"
    problema = client.post(base, headers=_h(token), json={"kind": "problema", "name": "Hipertensão arterial"})
    alergia = client.post(base, headers=_h(token), json={"kind": "alergia", "name": "Penicilina", "details": "Urticária"})
    medicacao = client.post(
        base, headers=_h(token),
        json={"kind": "medicacao", "name": "Losartana", "details": "Uso contínuo", "source_encounter_id": eid},
    )
    assert problema.status_code == alergia.status_code == medicacao.status_code == 201

    db.expire_all()
    row = db.get(PatientClinicalItem, problema.json()["id"])
    assert row is not None and row.payload_cifrado
    assert b"Hipertens" not in row.payload_cifrado

    ativos = client.get(base, headers=_h(token))
    assert ativos.status_code == 200
    assert {x["kind"] for x in ativos.json()} == {"problema", "alergia", "medicacao"}
    assert client.get(base, headers=_h(token_intruso)).status_code == 404

    inativado = client.post(f"{base}/{medicacao.json()['id']}/inativar", headers=_h(token))
    assert inativado.status_code == 200
    assert inativado.json()["is_active"] is False and inativado.json()["ended_at"]
    assert len(client.get(base, headers=_h(token)).json()) == 2
    historico = client.get(f"{base}?incluir_inativos=true", headers=_h(token))
    assert historico.status_code == 200 and len(historico.json()) == 3

    resultados = f"/api/pacientes/{pid}/resultados"
    catalogo = db.query(LabTest).filter_by(slug="troponina-i-teste-longitudinal").one_or_none()
    if catalogo is None:
        catalogo = LabTest(
            slug="troponina-i-teste-longitudinal", name="Troponina I", category="laboratorial",
            what_it_measures="Lesão miocárdica", indications="Suspeita de SCA",
            interpretation="Interpretar no contexto clínico", theme="biomarcadores",
            tags=[], source_refs=[], published=True,
        )
        db.add(catalogo)
    catalogo.published = True
    db.commit()
    db.refresh(catalogo)
    troponina = client.post(
        resultados, headers=_h(token),
        json={
            "exam_kind": "laboratorial", "exam_name": "Troponina I", "structured_result": "12",
            "unit": "ng/L", "reference_range": "< 19", "notes": "Amostra sem hemólise",
            "source": "Laboratório externo", "lab_test_id": catalogo.id,
            "source_encounter_id": eid, "performed_at": "2026-08-22T10:00:00-03:00",
        },
    )
    assert troponina.status_code == 201
    rid = troponina.json()["id"]
    db.expire_all()
    resultado_row = db.get(PatientExamResult, rid)
    assert resultado_row is not None and resultado_row.payload_cifrado
    assert resultado_row.patient_profile_id == pid and resultado_row.author_id == medico.id
    assert resultado_row.source_encounter_id == eid and resultado_row.lab_test_id == catalogo.id
    assert all(term not in resultado_row.payload_cifrado for term in (b"Troponina", b"Amostra", b"Laborat"))

    lista_resultados = client.get(resultados, headers=_h(token))
    assert lista_resultados.status_code == 200 and lista_resultados.json()[0]["exam_name"] == "Troponina I"
    assert lista_resultados.json()[0]["structured_result"] == "12"
    assert lista_resultados.json()[0]["lab_test_slug"] == catalogo.slug
    assert lista_resultados.json()[0]["source"] == "Laboratório externo"
    detalhe = client.get(f"{resultados}/{rid}", headers=_h(token))
    assert detalhe.status_code == 200 and detalhe.json()["result"]["notes"] == "Amostra sem hemólise"
    assert client.get(resultados, headers=_h(token_intruso)).status_code == 404
    assert client.get(f"{resultados}/{rid}", headers=_h(token_intruso)).status_code == 404

    ecg = client.post(
        resultados, headers=_h(token),
        json={
            "exam_kind": "metodo_grafico", "exam_name": "ECG",
            "report_text": "Ritmo sinusal. Sem alterações isquêmicas agudas.",
            "source": "Clínica", "performed_at": "2026-08-21T09:00:00-03:00",
        },
    )
    assert ecg.status_code == 201
    assert ecg.json()["structured_result"] is None
    assert ecg.json()["report_text"].startswith("Ritmo sinusal")

    correcao = client.post(
        f"{resultados}/{rid}/correcoes", headers=_h(token),
        json={
            "exam_kind": "laboratorial", "exam_name": "Troponina I", "structured_result": "13", "unit": "ng/L",
            "reference_range": "< 19", "source": "Laboratório externo", "lab_test_id": catalogo.id,
            "correction_reason": "Correção do valor transcrito", "source_encounter_id": eid,
            "performed_at": "2026-08-22T10:00:00-03:00",
        },
    )
    assert correcao.status_code == 201
    assert correcao.json()["correction_of_id"] == rid
    atualizados = client.get(resultados, headers=_h(token)).json()
    assert len(atualizados) == 3
    original = next(item for item in atualizados if item["id"] == rid)
    assert original["is_superseded"] is True and original["corrected_by_id"] == correcao.json()["id"]
    historico_correcao = client.get(f"{resultados}/{correcao.json()['id']}", headers=_h(token))
    assert [item["id"] for item in historico_correcao.json()["history"]] == [rid, correcao.json()["id"]]
    assert historico_correcao.json()["history"][1]["correction_reason"] == "Correção do valor transcrito"
    assert client.post(
        f"{resultados}/{rid}/correcoes", headers=_h(token),
        json={"exam_name": "Troponina I", "structured_result": "14", "correction_reason": "Nova tentativa"},
    ).status_code == 409
    assert client.post(
        f"{resultados}/{rid}/correcoes", headers=_h(token_intruso),
        json={"exam_name": "Troponina I", "structured_result": "99", "correction_reason": "Acesso indevido"},
    ).status_code == 404

    timeline = client.get(f"/api/pacientes/{pid}/linha-do-tempo", headers=_h(token))
    assert timeline.status_code == 200
    tipos = {evento["tipo"] for evento in timeline.json()}
    assert {"atendimento", "problema", "alergia", "medicacao", "resultado_exame"}.issubset(tipos)
    assert any(evento["titulo"] == "Medicação inativada" for evento in timeline.json())
    assert any(evento["titulo"] == "Correção de resultado" for evento in timeline.json())
    eventos_exame = [evento for evento in timeline.json() if evento["tipo"] == "resultado_exame"]
    assert any(evento["source"] == "Laboratório externo" and evento["lab_test_id"] == catalogo.id for evento in eventos_exame)
    original_timeline = next(evento for evento in eventos_exame if evento["exam_result_id"] == rid)
    assert original_timeline["status"] == "substituido"
    assert original_timeline["is_superseded"] is True
    assert original_timeline["corrected_by_id"] == correcao.json()["id"]
    datas = [datetime.fromisoformat(evento["data"]) for evento in timeline.json()]
    assert datas == sorted(datas, reverse=True)
    assert client.get(f"/api/pacientes/{pid}/linha-do-tempo", headers=_h(token_intruso)).status_code == 404

    # ECG patient-specific: arquivo cifrado, sugestão separada e somente a
    # interpretação explicitamente aceita pelo médico vira resultado clínico.
    monkeypatch.setattr(settings, "exames_dir", str(tmp_path / "ecgs"))
    monkeypatch.setattr(settings, "ai_enabled", True)
    monkeypatch.setattr(settings, "ai_clinical_multimodal_enabled", True)
    monkeypatch.setattr(settings, "openai_api_key", "test-key")
    image = io.BytesIO()
    Image.new("RGB", (1200, 800), "white").save(image, format="PNG")
    ecg_bytes = image.getvalue()
    ecg_upload = client.post(
        f"/api/pacientes/{pid}/ecgs",
        headers=_h(token),
        files={"arquivo": ("ecg-paciente.png", ecg_bytes, "image/png")},
        data={"performed_at": "2026-08-23T08:00:00-03:00", "source_encounter_id": str(eid)},
    )
    assert ecg_upload.status_code == 201, ecg_upload.text
    ecg_id = ecg_upload.json()["id"]
    db.expire_all()
    ecg_row = db.get(PatientECGRecord, ecg_id)
    assert ecg_row is not None and ecg_row.patient_profile_id == pid
    assert ecg_row.owner_id == medico.id and ecg_row.author_id == medico.id
    assert ecg_row.source_encounter_id == eid
    assert cofre.ler(ecg_row.storage_key, ecg_row.id) == ecg_bytes
    assert ecg_bytes != (tmp_path / "ecgs" / ecg_row.storage_key).read_bytes()
    status_ia = client.get(f"/api/pacientes/{pid}/ecgs/ia-status", headers=_h(token))
    assert status_ia.status_code == 200 and status_ia.json() == {
        "enabled": True,
        "supported_media_types": ["image/jpeg", "image/png", "image/webp"],
    }
    monkeypatch.setattr(settings, "openai_api_key", "")
    assert client.get(f"/api/pacientes/{pid}/ecgs/ia-status", headers=_h(token)).json()["enabled"] is False
    attempts_without_key = db.query(AuditLog.id).filter(
        AuditLog.action == "ai_ecg_transfer_attempt",
    ).count()
    assert client.post(
        f"/api/pacientes/{pid}/ecgs/{ecg_id}/sugestoes", headers=_h(token),
        json={"confirm_external_processing": True},
    ).status_code == 503
    assert db.query(AuditLog.id).filter(
        AuditLog.action == "ai_ecg_transfer_attempt",
    ).count() == attempts_without_key
    monkeypatch.setattr(settings, "openai_api_key", "test-key")
    monkeypatch.setattr(settings, "ai_clinical_multimodal_enabled", False)
    assert client.get(
        f"/api/pacientes/{pid}/ecgs/ia-status", headers=_h(token),
    ).json() == {
        "enabled": False,
        "supported_media_types": ["image/jpeg", "image/png", "image/webp"],
    }
    monkeypatch.setattr(settings, "ai_clinical_multimodal_enabled", True)
    assert client.get(
        f"/api/pacientes/{pid}/ecgs/ia-status", headers=_h(token_intruso),
    ).status_code == 404
    primeira_pagina = client.get(
        f"/api/pacientes/{pid}/ecgs?limite=1&offset=0", headers=_h(token),
    )
    assert primeira_pagina.status_code == 200 and [row["id"] for row in primeira_pagina.json()] == [ecg_id]
    assert client.get(
        f"/api/pacientes/{pid}/ecgs?limite=1&offset=1", headers=_h(token),
    ).json() == []
    assert client.get(f"/api/pacientes/{pid}/ecgs", headers=_h(token_intruso)).status_code == 404
    assert client.get(
        f"/api/pacientes/{pid}/ecgs/{ecg_id}/arquivo", headers=_h(token_intruso),
    ).status_code == 404
    download = client.get(f"/api/pacientes/{pid}/ecgs/{ecg_id}/arquivo", headers=_h(token))
    assert download.status_code == 200 and download.content == ecg_bytes
    assert download.headers["cache-control"] == "no-store, private"

    attempts_before_pdf = db.query(AuditLog.id).filter(
        AuditLog.action == "ai_ecg_transfer_attempt",
    ).count()
    ecg_row.media_type = "application/pdf"
    db.commit()
    unsupported_pdf = client.post(
        f"/api/pacientes/{pid}/ecgs/{ecg_id}/sugestoes", headers=_h(token),
        json={"confirm_external_processing": True},
    )
    assert unsupported_pdf.status_code == 422
    assert db.query(AuditLog.id).filter(
        AuditLog.action == "ai_ecg_transfer_attempt",
    ).count() == attempts_before_pdf
    ecg_row.media_type = "image/png"
    db.commit()

    def _analysis(_content: bytes, _media_type: str) -> dict:
        assert _content == ecg_bytes and _media_type == "image/png"
        return {
            "payload": {
                "quality": "adequada", "summary": "Ritmo sinusal, FC aproximada de 72 bpm.",
                "rhythm": "Ritmo sinusal", "heart_rate_bpm": 72,
                "intervals": {"pr_ms": 160, "qrs_ms": 90, "qtc_ms": 420},
                "axis": "Normal", "conduction": "Sem bloqueio evidente",
                "st_t": "Sem supradesnivelamento evidente", "other_findings": [],
                "red_flags": [], "limitations": ["Confirmar calibração no original"],
                "urgent_review_recommended": False,
                "disclaimer": "Sugestão gerada por IA; requer revisão médica.",
            },
            "provider": "test", "model": "vision-test", "prompt_version": "ecg-test-v1",
            "tokens_input": 100, "tokens_output": 50,
        }

    def _provider_failure(_content: bytes, _media_type: str) -> dict:
        raise RuntimeError("falha simulada sem PHI")

    monkeypatch.setattr(ecg_assist, "analyze_ecg", _provider_failure)
    results_before_ai = len(client.get(resultados, headers=_h(token)).json())
    assert client.post(
        f"/api/pacientes/{pid}/ecgs/{ecg_id}/sugestoes", headers=_h(token), json={},
    ).status_code == 422
    assert client.post(
        f"/api/pacientes/{pid}/ecgs/{ecg_id}/sugestoes", headers=_h(token),
        json={"confirm_external_processing": False},
    ).status_code == 422
    failed_transfer = client.post(
        f"/api/pacientes/{pid}/ecgs/{ecg_id}/sugestoes", headers=_h(token),
        json={"confirm_external_processing": True},
    )
    assert failed_transfer.status_code == 502
    db.expire_all()
    failed_attempt = db.query(AuditLog).filter(
        AuditLog.action == "ai_ecg_transfer_attempt",
    ).order_by(AuditLog.id.desc()).first()
    failed_outcome = db.query(AuditLog).filter(
        AuditLog.action == "ai_ecg_transfer_outcome",
    ).order_by(AuditLog.id.desc()).first()
    assert failed_attempt is not None and failed_attempt.detail["status"] == "reserved"
    assert failed_outcome is not None and failed_outcome.detail["status"] == "provider_error"
    assert failed_outcome.detail["transfer_attempt_id"] == failed_attempt.id
    assert "falha simulada" not in str(failed_attempt.detail) + str(failed_outcome.detail)

    original_limit = settings.ai_daily_limit
    monkeypatch.setattr(settings, "ai_daily_limit", 1)
    assert client.post(
        f"/api/pacientes/{pid}/ecgs/{ecg_id}/sugestoes", headers=_h(token),
        json={"confirm_external_processing": True},
    ).status_code == 429
    monkeypatch.setattr(settings, "ai_daily_limit", original_limit)
    monkeypatch.setattr(ecg_assist, "analyze_ecg", _analysis)
    suggestion_response = client.post(
        f"/api/pacientes/{pid}/ecgs/{ecg_id}/sugestoes", headers=_h(token),
        json={"confirm_external_processing": True},
    )
    assert suggestion_response.status_code == 201, suggestion_response.text
    suggestion = suggestion_response.json()
    suggestion_id = suggestion["id"]
    assert suggestion["status"] == "generated" and suggestion["accepted_result_id"] is None
    assert suggestion["payload"]["rhythm"] == "Ritmo sinusal"
    assert len(client.get(resultados, headers=_h(token)).json()) == results_before_ai
    db.expire_all()
    suggestion_row = db.get(PatientClinicalAISuggestion, suggestion_id)
    assert suggestion_row is not None and b"Ritmo sinusal" not in suggestion_row.payload_cifrado
    log = db.query(AuditLog).filter(AuditLog.action == "ai_ecg_suggest").order_by(AuditLog.id.desc()).first()
    assert log is not None and "Ritmo" not in str(log.detail)
    successful_outcome = db.query(AuditLog).filter(
        AuditLog.action == "ai_ecg_transfer_outcome",
    ).order_by(AuditLog.id.desc()).first()
    assert successful_outcome is not None and successful_outcome.detail["status"] == "success"
    assert successful_outcome.detail["transfer_attempt_id"] == log.detail["transfer_attempt_id"]
    assert client.post(
        f"/api/pacientes/{pid}/ecgs/{ecg_id}/sugestoes/{suggestion_id}/revisao",
        headers=_h(token_intruso),
        json={"decision": "accept", "final_interpretation": "Acesso indevido"},
    ).status_code == 404

    pending_timeline = client.get(f"/api/pacientes/{pid}/linha-do-tempo", headers=_h(token)).json()
    assert any(
        item["tipo"] == "ecg_anexado" and item["ecg_record_id"] == ecg_id
        and item["status"] == "awaiting_review"
        for item in pending_timeline
    )
    reviewed_text = "Ritmo sinusal. FC 72 bpm. Sem alterações agudas de ST-T."
    accepted = client.post(
        f"/api/pacientes/{pid}/ecgs/{ecg_id}/sugestoes/{suggestion_id}/revisao",
        headers=_h(token),
        json={
            "decision": "accept", "final_interpretation": reviewed_text,
            "review_note": "Traçado e calibração conferidos pelo médico.",
        },
    )
    assert accepted.status_code == 200, accepted.text
    assert accepted.json()["suggestion"]["status"] == "accepted"
    accepted_result_id = accepted.json()["result"]["id"]
    assert accepted.json()["result"]["report_text"] == reviewed_text
    assert accepted.json()["result"]["ai_suggestion_id"] == suggestion_id
    db.expire_all()
    suggestion_row = db.get(PatientClinicalAISuggestion, suggestion_id)
    assert suggestion_row.accepted_result_id == accepted_result_id
    assert "Traçado".encode() not in (suggestion_row.review_note_cifrado or b"")

    final_timeline = client.get(f"/api/pacientes/{pid}/linha-do-tempo", headers=_h(token)).json()
    assert not any(item["tipo"] == "ecg_anexado" and item["ecg_record_id"] == ecg_id for item in final_timeline)
    accepted_event = next(item for item in final_timeline if item.get("exam_result_id") == accepted_result_id)
    assert accepted_event["ecg_record_id"] == ecg_id
    assert accepted_event["ai_suggestion_id"] == suggestion_id
    assert accepted_event["ai_review_status"] == "accepted"

    second_suggestion = client.post(
        f"/api/pacientes/{pid}/ecgs/{ecg_id}/sugestoes", headers=_h(token),
        json={"confirm_external_processing": True},
    )
    assert second_suggestion.status_code == 201
    second_id = second_suggestion.json()["id"]
    suggestion_history = f"/api/pacientes/{pid}/ecgs/{ecg_id}/sugestoes"
    assert [row["id"] for row in client.get(
        f"{suggestion_history}?limite=1&offset=0", headers=_h(token),
    ).json()] == [second_id]
    assert [row["id"] for row in client.get(
        f"{suggestion_history}?limite=1&offset=1", headers=_h(token),
    ).json()] == [suggestion_id]
    assert client.get(suggestion_history, headers=_h(token_intruso)).status_code == 404
    assert client.post(
        f"/api/pacientes/{pid}/ecgs/{ecg_id}/sugestoes/{second_id}/revisao",
        headers=_h(token),
        json={"decision": "accept", "final_interpretation": "Outra interpretação"},
    ).status_code == 409
    rejected = client.post(
        f"/api/pacientes/{pid}/ecgs/{ecg_id}/sugestoes/{second_id}/revisao",
        headers=_h(token),
        json={"decision": "reject", "review_note": "Sugestão não compatível com o traçado."},
    )
    assert rejected.status_code == 200 and rejected.json()["suggestion"]["status"] == "rejected"
    assert rejected.json()["result"] is None

    # Qualquer dado longitudinal torna o cadastro parte do prontuário e impede deleção física.
    assert client.delete(f"/api/pacientes/{pid}", headers=_h(token)).status_code == 409
    so_exame = client.post("/api/pacientes", headers=_h(token), json={"full_name": "Paciente Só Exame"})
    pid_so_exame = so_exame.json()["id"]
    assert client.post(
        f"/api/pacientes/{pid_so_exame}/resultados", headers=_h(token),
        json={"exam_kind": "metodo_grafico", "exam_name": "ECG", "report_text": "Ritmo sinusal"},
    ).status_code == 201
    assert client.delete(f"/api/pacientes/{pid_so_exame}", headers=_h(token)).status_code == 409


def test_ecg_ai_contract_rejects_blank_summary_and_uses_operational_day(monkeypatch):
    with pytest.raises(ValidationError):
        ecg_assist.ECGSuggestionPayload.model_validate({
            "quality": "adequada",
            "summary": "   ",
            "intervals": {"pr_ms": None, "qrs_ms": None, "qtc_ms": None},
        })

    monkeypatch.setattr(settings, "fuso_operacao", "America/Sao_Paulo")
    start, end = _operational_day_utc_bounds(
        datetime(2026, 8, 23, 0, 30, tzinfo=timezone.utc),
    )
    assert start == datetime(2026, 8, 22, 3, 0, tzinfo=timezone.utc)
    assert end == datetime(2026, 8, 23, 3, 0, tzinfo=timezone.utc)
