"""Trabalho 16 (07/08/2026) — preferência de sincronização por conta
conectada: `PATCH /api/agenda/integrations/{id}/preferencias`, e como ela
afeta a leitura em `GET /api/agenda/appointments` (sync_calendar) e
`GET /api/email/mensagens/todas` (sync_mail, com o parâmetro `contas`).
"""
from datetime import datetime, timedelta, timezone

import pytest

from app.models.agenda import CalendarIntegration
from app.models.clinical_docs import Appointment
from app.models.subscription import Subscription


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _subscribe(db, user_id: int) -> None:
    db.add(Subscription(user_id=user_id, kind="meucardio", plano="basico", status="ativo"))
    db.commit()


def _integracao(db, owner_id: int, *, provider="google_calendar", capabilities=None, **extra) -> CalendarIntegration:
    item = CalendarIntegration(
        owner_id=owner_id, provider=provider, display_name=f"{provider}-teste",
        status="connected", enabled=True, sync_strategy="external_authoritative",
        capabilities=capabilities or {"read_appointments": True, "read_mail": True, "read_contacts": True},
        **extra,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


class TestPatchPreferencias:
    def test_liga_e_desliga_o_que_a_conta_realmente_tem(self, client, criar_usuario, db):
        user, token = criar_usuario(email="pref.sync.basico@teste.local")
        _subscribe(db, user.id)
        integracao = _integracao(db, user.id)

        r = client.patch(
            f"/api/agenda/integrations/{integracao.id}/preferencias",
            headers=_headers(token), json={"sync_calendar": False},
        )
        assert r.status_code == 200, r.text
        assert r.json()["sync_calendar"] is False

        db.refresh(integracao)
        assert integracao.sync_calendar is False
        assert integracao.sync_mail is True  # não mexeu, continua no default

    def test_nao_liga_o_que_a_conta_nao_tem_capacidade(self, client, criar_usuario, db):
        user, token = criar_usuario(email="pref.sync.semmail@teste.local")
        _subscribe(db, user.id)
        integracao = _integracao(db, user.id, provider="yahoo_mail", capabilities={"read_mail": True})

        r = client.patch(
            f"/api/agenda/integrations/{integracao.id}/preferencias",
            headers=_headers(token), json={"sync_calendar": True},
        )
        assert r.status_code == 422, r.text

    def test_isolado_por_usuario(self, client, criar_usuario, db):
        dono, _ = criar_usuario(email="pref.sync.dono@teste.local")
        intruso, token_intruso = criar_usuario(email="pref.sync.intruso@teste.local")
        _subscribe(db, dono.id)
        _subscribe(db, intruso.id)
        integracao = _integracao(db, dono.id)

        r = client.patch(
            f"/api/agenda/integrations/{integracao.id}/preferencias",
            headers=_headers(token_intruso), json={"sync_calendar": False},
        )
        assert r.status_code == 404


class TestListAppointmentsRespeitaSyncCalendar:
    def test_agendamento_de_conta_com_sync_desligado_nao_aparece(self, client, criar_usuario, db):
        user, token = criar_usuario(email="pref.agenda.desligado@teste.local")
        _subscribe(db, user.id)
        integracao = _integracao(db, user.id, sync_calendar=False)

        inicio = datetime.now(timezone.utc) + timedelta(days=1)
        db.add(Appointment(
            owner_id=user.id, integration_id=integracao.id, source="google_calendar",
            scheduled_at=inicio, ends_at=inicio + timedelta(minutes=30),
            patient_name_temp="Paciente externo",
        ))
        # Compromisso nativo — nunca deve sumir, integration_id nulo.
        db.add(Appointment(
            owner_id=user.id, integration_id=None, source="corvia",
            scheduled_at=inicio, ends_at=inicio + timedelta(minutes=30),
            patient_name_temp="Paciente Corvia",
        ))
        db.commit()

        r = client.get("/api/agenda/appointments", headers=_headers(token))
        assert r.status_code == 200, r.text
        nomes = {a["patient_name"] for a in r.json()}
        assert "Paciente externo" not in nomes
        assert "Paciente Corvia" in nomes

    def test_agendamento_volta_a_aparecer_ao_religar_a_preferencia(self, client, criar_usuario, db):
        user, token = criar_usuario(email="pref.agenda.religar@teste.local")
        _subscribe(db, user.id)
        integracao = _integracao(db, user.id, sync_calendar=False)
        inicio = datetime.now(timezone.utc) + timedelta(days=1)
        db.add(Appointment(
            owner_id=user.id, integration_id=integracao.id, source="google_calendar",
            scheduled_at=inicio, ends_at=inicio + timedelta(minutes=30),
            patient_name_temp="Paciente religado",
        ))
        db.commit()

        antes = client.get("/api/agenda/appointments", headers=_headers(token))
        assert "Paciente religado" not in {a["patient_name"] for a in antes.json()}

        client.patch(
            f"/api/agenda/integrations/{integracao.id}/preferencias",
            headers=_headers(token), json={"sync_calendar": True},
        )
        depois = client.get("/api/agenda/appointments", headers=_headers(token))
        assert "Paciente religado" in {a["patient_name"] for a in depois.json()}
