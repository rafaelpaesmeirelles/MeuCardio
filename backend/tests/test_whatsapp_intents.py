from datetime import datetime, timezone

import pytest

from app.services.whatsapp_intents import parse_intent


NOW = datetime(2026, 8, 31, 12, tzinfo=timezone.utc)


def parse(text, kind=None, arguments=None):
    return parse_intent(text, explicit_kind=kind, explicit_arguments=arguments, now=NOW, timezone_name="America/Sao_Paulo")


@pytest.mark.parametrize("text,kind", [
    ("consultar agenda", "agenda_list"),
    ("consultar tarefas", "task_list"),
    ("pesquisar diretriz de insuficiência cardíaca", "scientific_search"),
    ("resumir PDF id 22", "document_summary"),
    ("CorVIA, monte um Heart Team para este caso", "heart_team_start"),
])
def test_read_and_clinical_intents(text, kind):
    assert parse(text).kind == kind


def test_create_reminder_extracts_absolute_iso_time():
    parsed = parse("criar lembrete amanhã 8h")
    assert parsed.kind == "reminder_create" and parsed.clarification is None
    assert "T08:00:00" in parsed.arguments["inicio"]


def test_update_appointment_requires_and_extracts_id_and_time():
    assert parse("reagendar compromisso").clarification
    parsed = parse("reagendar compromisso #72 amanhã 14h")
    assert parsed.arguments["appointment_id"] == 72 and "T14:00:00" in parsed.arguments["novo_inicio"]


def test_cancel_third_party_appointment_is_level3_intent_with_id():
    parsed = parse("cancelar compromisso #91\nMotivo: solicitação do médico")
    assert parsed.kind == "third_party_appointment_cancel"
    assert parsed.arguments == {"appointment_id": 91, "motivo": "solicitação do médico"}


def test_message_send_never_invents_template_or_optin():
    assert parse("enviar mensagem para +55 11 99999-9999").clarification
    parsed = parse("Enviar mensagem\nTelefone: +55 11 99999-9999\nTemplate: aviso_agenda\nOpt-in ID: 81\nIdioma: pt_BR\nParâmetros: Rafael | 08:00")
    assert parsed.clarification is None
    assert parsed.arguments["recipient_phone"] == "5511999999999"
    assert parsed.arguments["template_parameters"] == ["Rafael", "08:00"]


def test_email_requires_recipient_subject_and_body():
    assert parse("enviar e-mail para medico@example.com").clarification
    parsed = parse("Enviar e-mail para medico@example.com\nAssunto: Agenda\nCorpo: Confirme o horário")
    assert parsed.clarification is None and parsed.arguments["para"] == "medico@example.com"


def test_explicit_arguments_are_preserved_but_kind_is_server_allowlisted_later():
    parsed = parse("ação administrativa", kind="message_send", arguments={"recipient_phone": "5511999999999", "template_name": "aviso", "recipient_opt_in_id": 2})
    assert parsed.kind == "message_send" and parsed.clarification is None


def test_routine_requires_structured_fields_and_extracts_them_without_guessing():
    assert parse("criar rotina semanal").clarification
    parsed=parse("Criar rotina semanal\nDias: segunda, terça\nInício: 08:00\nFim: 12:00\nTítulo: Consultório\nLocal: Clínica")
    assert parsed.clarification is None and parsed.arguments["dias_semana"]==["segunda","terca"]


@pytest.mark.parametrize("text,kind",[("resumo diário","daily_summary"),("ver pendências de exames e assinaturas","pending_items"),("preparar material ao paciente\nTítulo: FA\nCorpo: rascunho educativo","patient_material_draft")])
def test_daily_pending_and_patient_material_intents(text,kind):
    assert parse(text).kind==kind


def test_document_share_requires_owned_issued_reference_fields():
    parsed=parse("compartilhar documento gerado #44 validade 48h")
    assert parsed.clarification is None and parsed.arguments=={"document_id":44,"document_type":"generated_document","expires_hours":48}
    assert parse("compartilhar documento").clarification
