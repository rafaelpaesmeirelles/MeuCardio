"""Confirmações de agenda por e-mail, enviadas somente após confirmação real."""

from __future__ import annotations

import html
import smtplib
from datetime import datetime, timezone
from email.message import EmailMessage
from zoneinfo import ZoneInfo

from app.core.config import settings
from app.core.db import SessionLocal
from app.models.agenda import AppointmentCommunication, CalendarLocation, SchedulingService
from app.models.clinical_docs import Appointment
from app.services.cofre import decifrar_campo


def _send(message: EmailMessage) -> None:
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as server:
        server.starttls()
        server.login(settings.smtp_user, settings.smtp_password)
        server.send_message(message)


def send_appointment_communication(communication_id: int) -> bool:
    """Abre sessão própria para funcionar com BackgroundTasks ou job externo."""
    db = SessionLocal()
    try:
        communication = db.get(AppointmentCommunication, communication_id)
        if not communication or communication.status not in {"pending", "retry"}:
            return False
        appointment = db.get(Appointment, communication.appointment_id)
        if not appointment or appointment.status != "confirmado" or appointment.confirmation_status != "confirmed":
            communication.status = "blocked_unconfirmed"
            communication.error_message = "Agendamento ainda não confirmado na fonte autoritativa."
            db.commit()
            return False
        if not settings.smtp_configurado:
            communication.status = "retry"
            communication.error_message = "SMTP não configurado."
            db.commit()
            return False
        if not communication.recipient_cipher:
            communication.status = "failed"
            communication.error_message = "Destinatário ausente."
            db.commit()
            return False

        recipient = decifrar_campo(communication.recipient_cipher, appointment.id)
        zone = ZoneInfo(appointment.timezone or settings.fuso_operacao)
        local_start = appointment.scheduled_at.astimezone(zone)
        service = db.get(SchedulingService, appointment.service_id) if appointment.service_id else None
        location = db.get(CalendarLocation, appointment.location_id) if appointment.location_id else None
        service_name = service.name if service else appointment.appointment_type.capitalize()
        location_name = location.name if location else "Local a confirmar"
        when = local_start.strftime("%d/%m/%Y às %H:%M")

        subject = "Confirmação de agendamento — Corvia"
        text = (
            "Seu agendamento foi confirmado.\n\n"
            f"Data e horário: {when}\n"
            f"Atendimento: {service_name}\n"
            f"Local: {location_name}\n\n"
            "Em caso de dúvida ou necessidade de reagendamento, entre em contato com o consultório.\n\n"
            "Corvia — O caminho do coração"
        )
        body = (
            "<div style='font-family:Arial,sans-serif;color:#12303d;line-height:1.55'>"
            "<h1 style='font-size:22px'>Agendamento confirmado</h1>"
            f"<p><strong>Data e horário:</strong> {html.escape(when)}<br>"
            f"<strong>Atendimento:</strong> {html.escape(service_name)}<br>"
            f"<strong>Local:</strong> {html.escape(location_name)}</p>"
            "<p>Em caso de dúvida ou necessidade de reagendamento, entre em contato com o consultório.</p>"
            "<p style='color:#617984'>Corvia — O caminho do coração</p></div>"
        )
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = settings.smtp_from
        message["To"] = recipient
        message.set_content(text)
        message.add_alternative(body, subtype="html")
        try:
            _send(message)
        except Exception as exc:  # SMTP precisa falhar sem desfazer o agendamento.
            communication.status = "retry"
            communication.error_message = str(exc)[:500]
            db.commit()
            return False
        communication.status = "sent"
        communication.sent_at = datetime.now(timezone.utc)
        communication.error_message = None
        db.commit()
        return True
    finally:
        db.close()


def send_pending_communications(owner_id: int, limit: int = 50) -> dict:
    db = SessionLocal()
    try:
        ids = [row[0] for row in db.query(AppointmentCommunication.id).filter(
            AppointmentCommunication.owner_id == owner_id,
            AppointmentCommunication.status.in_(("pending", "retry")),
        ).order_by(AppointmentCommunication.created_at).limit(limit).all()]
    finally:
        db.close()
    sent = sum(1 for item_id in ids if send_appointment_communication(item_id))
    return {"processed": len(ids), "sent": sent, "not_sent": len(ids) - sent}
