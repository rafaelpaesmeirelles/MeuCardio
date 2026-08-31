from datetime import timedelta
import asyncio,json
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from fastapi import HTTPException

from app.api import whatsapp as api
from app.core.config import settings
from app.models.user import User
from app.models.whatsapp import (
    WhatsAppCommand, WhatsAppHeartTeamJob, WhatsAppLink, WhatsAppMessage,
    WhatsAppOutboundOutbox, WhatsAppPairing, WhatsAppSummaryCache, WhatsAppUsageMetric, WhatsAppWebhookEvent,
)
from app.schemas.whatsapp import MediaReview,PIIReview, TranscriptReview
from app.services import whatsapp_assistant as svc
from app.services import whatsapp_inbound as inbound
from app.services import whatsapp_jobs
from app.services import whatsapp_security
from app.services.whatsapp_adapter import MediaResult
from app.services.ia.clinical_file_sanitizer import UnsafeClinicalFile
from app.services.whatsapp_security import token_hash, utcnow


class Query:
    def __init__(self, values=None):
        self.values = list(values or [])
    def filter(self, *args, **kwargs): return self
    def filter_by(self, **kwargs): return self
    def with_for_update(self): return self
    def order_by(self, *args): return self
    def limit(self, *args): return self
    def first(self): return self.values.pop(0) if self.values else None
    def all(self): return list(self.values)
    def scalar(self): return self.values.pop(0) if self.values else 0
    def delete(self, **kwargs): count=len(self.values);self.values=[];return count


class DB:
    def __init__(self, scripted=None):
        self.scripted = {key:list(value) for key,value in (scripted or {}).items()}
        self.added=[];self.deleted=[];self.commits=0;self.rollbacks=0
    def query(self, model): return Query(self.scripted.get(model, []))
    def add(self, value):
        if getattr(value, "id", None) is None: value.id=1000+len(self.added)
        self.added.append(value)
    def flush(self): pass
    def commit(self): self.commits+=1
    def rollback(self): self.rollbacks+=1
    def delete(self,value):self.deleted.append(value)
    def close(self):pass


def link_user():
    link=WhatsAppLink(id=9,user_id=7,phone_hash="h",phone_cipher=b"x",status="active",permissions={"read_agenda":True},retention_days=30)
    user=SimpleNamespace(id=7,email="doctor@example.com",investidor=False)
    return link,user


def test_duplicate_webhook_is_idempotent_and_has_no_side_effect():
    db=DB({WhatsAppWebhookEvent:[WhatsAppWebhookEvent(id=1,provider_event_id="wamid.1",payload_hash="x")]})
    adapter=Mock()
    result=inbound.process_meta_message(db,{"id":"wamid.1","from":"5511999999999","type":"text","text":{"body":"agenda"}},adapter=adapter)
    assert result=={"status":"duplicate"};adapter.send_text.assert_not_called();assert not db.added


def test_old_provider_timestamp_is_rejected_before_execution(monkeypatch):
    monkeypatch.setattr(inbound,"allow_rate",lambda *a,**k:True)
    db=DB({WhatsAppWebhookEvent:[]});adapter=Mock()
    result=inbound.process_meta_message(db,{"id":"old","from":"5511999999999","timestamp":"1","type":"text","text":{"body":"agenda"}},adapter=adapter)
    assert result["status"]=="rejected_replay"
    assert next(x for x in db.added if isinstance(x,WhatsAppWebhookEvent)).status=="rejected_replay"
    adapter.send_text.assert_not_called()


def test_pii_inbound_waits_for_in_app_review_and_does_not_create_command(monkeypatch):
    link,user=link_user();db=DB({WhatsAppWebhookEvent:[],WhatsAppLink:[link],User:[user]})
    monkeypatch.setattr(inbound,"allow_rate",lambda *a,**k:True);monkeypatch.setattr(inbound,"cifrar_campo",lambda *a:b"encrypted");monkeypatch.setattr(inbound,"_deliver_reply",lambda *a,**k:"sent")
    result=inbound.process_meta_message(db,{"id":"pii-1","from":"5511999999999","type":"text","text":{"body":"CPF 123.456.789-00"}},adapter=Mock())
    message=next(x for x in db.added if isinstance(x,WhatsAppMessage))
    assert message.status=="awaiting_anonymization_confirmation" and message.pii_kinds==["cpf"]
    assert not any(isinstance(x,WhatsAppCommand) for x in db.added) and "Identificadores" in result["message"]


def test_whatsapp_n3_nonce_never_leaves_ingestion_result(monkeypatch):
    link,user=link_user();db=DB({WhatsAppWebhookEvent:[],WhatsAppLink:[link],User:[user]});delivered=[]
    command=SimpleNamespace(id=88,status="awaiting_confirmation",kind="email_send",level=3,requires_in_app=True)
    monkeypatch.setattr(inbound,"allow_rate",lambda *a,**k:True);monkeypatch.setattr(inbound,"cifrar_campo",lambda *a:b"encrypted");monkeypatch.setattr(inbound,"detect_pii",lambda *a:[]);monkeypatch.setattr(inbound,"create_command",lambda *a,**k:(command,{"mensagem":"Confirmação necessária"},"super-secret-confirmation-nonce",None));monkeypatch.setattr(inbound,"_deliver_reply",lambda *a,**k:delivered.append(k["result"]) or "sent")
    result=inbound.process_meta_message(db,{"id":"n3-wa","from":"5511999999999","type":"text","text":{"body":"enviar e-mail administrativo"}},adapter=Mock())
    assert "super-secret-confirmation-nonce" not in repr(result) and "confirmation_token" not in result
    assert delivered[0]["requires_confirmation"] is True and "confirmation_token" not in delivered[0]


def test_public_webhook_response_is_status_only_and_redacts_all_tokens(monkeypatch):
    body=json.dumps({"entry":[{"changes":[{"value":{"messages":[{"id":"n3"}]}}]}]}).encode()
    class Request:
        async def body(self):return body
    db=DB();secret="super-secret-confirmation-nonce"
    monkeypatch.setattr(settings,"whatsapp_assistant_enabled",True);monkeypatch.setattr(api,"verify_meta_signature",lambda *a:True);monkeypatch.setattr(api,"get_adapter",Mock);monkeypatch.setattr(api,"process_meta_message",lambda *a,**k:{"status":"processed","confirmation_token":secret,"undo_token":"undo-secret","result":{"secret":secret}})
    response=asyncio.run(api.webhook(Request(),x_hub_signature_256="signed",db=db))
    assert response=={"ok":True,"processed":1,"results":[{"status":"processed"}]}
    assert secret not in repr(response) and "undo-secret" not in repr(response)


def test_audio_is_downloaded_encrypted_transcribed_then_waits_for_review(monkeypatch):
    link,user=link_user();db=DB({WhatsAppWebhookEvent:[],WhatsAppLink:[link],User:[user]})
    class Adapter:
        def download_media(self,_):return MediaResult(b"OggS-audio","audio/ogg","media")
        def transcribe_audio(self,*a,**k):return "criar lembrete amanhã 8h"
    monkeypatch.setattr(inbound,"allow_rate",lambda *a,**k:True);monkeypatch.setattr(inbound,"cifrar_campo",lambda *a:b"encrypted");monkeypatch.setattr(inbound,"guardar",lambda *a,**k:"cipher.bin");monkeypatch.setattr(inbound,"require_positive_tariff",lambda *a:12);monkeypatch.setattr(inbound,"enforce_cost_headroom",lambda *a:None);monkeypatch.setattr(inbound,"_deliver_reply",lambda *a,**k:"sent")
    result=inbound.process_meta_message(db,{"id":"audio-1","from":"5511999999999","type":"audio","audio":{"id":"m1"}},adapter=Adapter())
    message=next(x for x in db.added if isinstance(x,WhatsAppMessage));metric=next(x for x in db.added if isinstance(x,WhatsAppUsageMetric))
    assert message.status=="awaiting_transcript_review" and metric.operation=="audio_transcription" and result["status"]==message.status
    assert not any(isinstance(x,WhatsAppCommand) for x in db.added)


def test_media_with_visible_identifiers_is_rejected_before_storage(monkeypatch):
    link,user=link_user();db=DB({WhatsAppWebhookEvent:[],WhatsAppLink:[link],User:[user]});store=Mock()
    class Adapter:
        def download_media(self,_):return MediaResult(b"raw-patient-image","image/png","patient.png")
    monkeypatch.setattr(inbound,"allow_rate",lambda *a,**k:True);monkeypatch.setattr(inbound,"cifrar_campo",lambda *a:b"encrypted");monkeypatch.setattr(inbound,"_validate_media",lambda *a:("image/png","patient.png"));monkeypatch.setattr(inbound,"sanitize_clinical_file",lambda *a:(_ for _ in ()).throw(UnsafeClinicalFile("identifier")));monkeypatch.setattr(inbound,"guardar",store);monkeypatch.setattr(inbound,"_deliver_reply",lambda *a,**k:"sent")
    result=inbound.process_meta_message(db,{"id":"image-pii","from":"5511999999999","type":"image","image":{"id":"m-image"}},adapter=Adapter())
    message=next(x for x in db.added if isinstance(x,WhatsAppMessage))
    assert result["status"]=="media_rejected_identifiers" and message.status=="media_rejected_identifiers"
    store.assert_not_called()


def test_only_locally_sanitized_media_is_encrypted_and_stored(monkeypatch):
    link,user=link_user();db=DB({WhatsAppWebhookEvent:[],WhatsAppLink:[link],User:[user]});stored=[]
    class Adapter:
        def download_media(self,_):return MediaResult(b"raw-with-metadata","image/png","safe.png")
    def store(data,*a,**k):stored.append(data);return "encrypted/safe.bin"
    monkeypatch.setattr(inbound,"allow_rate",lambda *a,**k:True);monkeypatch.setattr(inbound,"cifrar_campo",lambda *a:b"encrypted");monkeypatch.setattr(inbound,"_validate_media",lambda *a:("image/png","safe.png"));monkeypatch.setattr(inbound,"sanitize_clinical_file",lambda *a:(b"sanitized-without-metadata","image/png"));monkeypatch.setattr(inbound,"guardar",store);monkeypatch.setattr(inbound,"_deliver_reply",lambda *a,**k:"sent")
    result=inbound.process_meta_message(db,{"id":"image-safe","from":"5511999999999","type":"image","image":{"id":"m-image"}},adapter=Adapter())
    assert result["status"]=="awaiting_media_review" and stored==[b"sanitized-without-metadata"]


def test_transcript_review_creates_command_only_after_confirmation(monkeypatch):
    link,user=link_user();message=WhatsAppMessage(id=4,link_id=link.id,owner_id=user.id,direction="inbound",message_type="audio",payload_cipher=b"x",status="awaiting_transcript_review",expires_at=utcnow()+timedelta(days=1))
    db=DB({WhatsAppMessage:[message]});command=SimpleNamespace(id=8,status="completed",kind="reminder_create",level=2,requires_in_app=False)
    monkeypatch.setattr(api,"decrypt_payload",lambda *a:{"transcript":"original"});monkeypatch.setattr(api,"cifrar_campo",lambda *a:b"new");monkeypatch.setattr(api,"_active",lambda *a:link);monkeypatch.setattr(api,"_audit",lambda *a,**k:None);monkeypatch.setattr(api,"create_command",lambda *a,**k:(command,{"mensagem":"ok"},None,"undo-token-long-enough"));monkeypatch.setattr(settings,"whatsapp_assistant_enabled",True)
    out=api.transcript(4,TranscriptReview(text="criar lembrete amanhã 8h",confirmed=True),db=db,user=user)
    assert message.status=="processed" and out["command"]["kind"]=="reminder_create"


def test_granular_permission_denies_write_when_only_read_is_allowed(monkeypatch):
    user=SimpleNamespace(id=7);cmd=SimpleNamespace(kind="reminder_create",level=2,link_id=9,id=1);tool=Mock()
    monkeypatch.setattr(svc,"_permission",lambda *a:False);monkeypatch.setattr(svc,"executar_tool_assistente",tool)
    result=svc._execute(DB(),user,cmd,{"text":"lembrete","arguments":{"inicio":"2026-09-01T08:00:00-03:00"}})
    assert result["erro"]=="permission_required";tool.assert_not_called()


def test_confirm_rechecks_nested_n4_and_never_calls_tool(monkeypatch):
    user=SimpleNamespace(id=7);link=SimpleNamespace(pin_hash="hash");cmd=SimpleNamespace(id=3,owner_id=7,status="awaiting_confirmation",confirmation_expires_at=utcnow()+timedelta(minutes=1),confirmation_token_hash=token_hash("token-long-enough","confirm"),kind="email_send",level=3,idempotency_key="key",payload_cipher=b"x",result_cipher=None)
    metric=SimpleNamespace(success=True,blocked_reason=None);db=DB({WhatsAppUsageMetric:[metric]});tool=Mock()
    monkeypatch.setattr(svc,"_link",lambda *a:link);monkeypatch.setattr(svc,"verify_password",lambda *a:True);monkeypatch.setattr(svc,"decrypt_payload",lambda *a:{"text":"administrativo","arguments":{"corpo":{"nested":"T.O.M.E 10mg"}}});monkeypatch.setattr(svc,"_execute",tool);monkeypatch.setattr(settings,"whatsapp_assistant_enabled",True)
    result=svc.confirm_command(db,user,cmd,token="token-long-enough",pin="123456")
    assert result["erro"]=="blocked_level_4" and cmd.status=="blocked_security" and metric.success is False;tool.assert_not_called()


def test_confirm_rechecks_semantic_clinical_payload_and_never_calls_tool(monkeypatch):
    user=SimpleNamespace(id=7);link=SimpleNamespace(pin_hash="hash");cmd=SimpleNamespace(id=3,owner_id=7,status="awaiting_confirmation",confirmation_expires_at=utcnow()+timedelta(minutes=1),confirmation_token_hash=token_hash("token-long-enough","confirm"),kind="email_send",level=3,idempotency_key="semantic",payload_cipher=b"x",result_cipher=None)
    metric=SimpleNamespace(success=True,blocked_reason=None);db=DB({WhatsAppUsageMetric:[metric]});tool=Mock()
    payload={"text":"administrativo","arguments":{"assunto":"Retorno","corpo":"O paciente tem infarto e precisa de AAS"}}
    monkeypatch.setattr(svc,"_link",lambda *a:link);monkeypatch.setattr(svc,"verify_password",lambda *a:True);monkeypatch.setattr(svc,"decrypt_payload",lambda *a:payload);monkeypatch.setattr(svc,"_execute",tool);monkeypatch.setattr(settings,"whatsapp_assistant_enabled",True)
    result=svc.confirm_command(db,user,cmd,token="token-long-enough",pin="123456")
    assert result["erro"]=="blocked_level_4" and cmd.status=="blocked_security" and metric.success is False;tool.assert_not_called()


def test_level2_uses_canonical_agenda_tool_and_undo_compensates(monkeypatch):
    user=SimpleNamespace(id=7);cmd=SimpleNamespace(kind="reminder_create",level=2,link_id=9,id=3,owner_id=7,status="completed",undo_token_hash=token_hash("undo-token-long-enough","undo"),result_cipher=b"x")
    calls=[]
    def tool(name,args,db,user):calls.append((name,args));return {"criado":True,"compromisso":{"id":55}} if "criar" in name else {"cancelado":True}
    monkeypatch.setattr(svc,"_permission",lambda *a:True);monkeypatch.setattr(svc,"executar_tool_assistente",tool);monkeypatch.setattr(svc,"decrypt_payload",lambda *a:{"compromisso":{"id":55}});monkeypatch.setattr(svc,"_audit",lambda *a,**k:None)
    created=svc._execute(DB(),user,cmd,{"text":"lembrete","arguments":{"inicio":"2026-09-01T08:00:00-03:00"}})
    undone=svc.undo_command(DB(),user,cmd,token="undo-token-long-enough")
    assert created["compromisso"]["id"]==55 and undone["status"]=="undone"
    assert calls[0][0]=="agenda_criar_compromisso_inteligente" and calls[1][0]=="agenda_cancelar_compromisso"


def test_zero_tariff_fails_closed_before_provider_call():
    with pytest.raises(HTTPException) as exc:svc.require_positive_tariff(0,"Meta")
    assert exc.value.status_code==503


def test_heart_worker_dual_kill_switch_does_not_open_db(monkeypatch):
    factory=Mock();monkeypatch.setattr(whatsapp_jobs,"SessionLocal",factory);monkeypatch.setattr(settings,"whatsapp_assistant_enabled",True);monkeypatch.setattr(settings,"heart_team_enabled",False)
    assert whatsapp_jobs.process_heart_team_job(1)=={"status":"feature_disabled"};factory.assert_not_called()


def test_pairing_is_one_time_and_revocation_is_audited(monkeypatch):
    user=SimpleNamespace(id=7);pair=WhatsAppPairing(id=2,user_id=7,code_hash=token_hash("12345678","pairing"),expires_at=utcnow()+timedelta(minutes=5),attempts=0,retention_days=20,permissions={"read_agenda":True},pin_hash="pin")
    db=DB({WhatsAppPairing:[pair],WhatsAppLink:[]});monkeypatch.setattr(svc,"_encrypt",lambda *a:b"phone");monkeypatch.setattr(svc,"_audit",lambda *a,**k:None);monkeypatch.setattr(settings,"whatsapp_assistant_enabled",True)
    linked=svc.complete_pairing(db,code="12345678",phone="5511999999999")
    assert pair.used_at is not None and linked.status=="active" and linked.permissions=={"read_agenda":True}
    svc.revoke_link(db,user,linked)
    assert linked.status=="revoked" and linked.revoked_at is not None


def test_manual_pairing_is_sandbox_only_and_owner_bound(monkeypatch):
    user=SimpleNamespace(id=7);request=SimpleNamespace(client=SimpleNamespace(host="127.0.0.1"));captured=[]
    monkeypatch.setattr(settings,"whatsapp_assistant_enabled",True);monkeypatch.setattr(settings,"whatsapp_provider","sandbox");monkeypatch.setattr(api,"allow_rate",lambda key,**k:captured.append(key) or True)
    monkeypatch.setattr(api,"complete_pairing",lambda db,**kwargs:captured.append(kwargs) or SimpleNamespace(id=55))
    data=SimpleNamespace(code="12345678",phone="5511999999999")
    result=api.pairing_complete(data,request,db=DB(),user=user)
    assert result["link_id"]==55 and captured[-1]["expected_user_id"]==user.id
    assert all("5511999999999" not in str(item) for item in captured[:-1])


def test_manual_pairing_is_unreachable_with_meta_provider(monkeypatch):
    monkeypatch.setattr(settings,"whatsapp_assistant_enabled",True);monkeypatch.setattr(settings,"whatsapp_provider","meta");complete=Mock();monkeypatch.setattr(api,"complete_pairing",complete)
    with pytest.raises(HTTPException) as exc:api.pairing_complete(SimpleNamespace(code="12345678",phone="5511999999999"),SimpleNamespace(client=None),db=DB(),user=SimpleNamespace(id=7))
    assert exc.value.status_code==404;complete.assert_not_called()


def test_bad_pin_blocks_n3_before_any_side_effect(monkeypatch):
    user=SimpleNamespace(id=7);link=SimpleNamespace(pin_hash="hash");cmd=SimpleNamespace(owner_id=7,status="awaiting_confirmation",confirmation_expires_at=utcnow()+timedelta(minutes=1),confirmation_token_hash=token_hash("token-long-enough","confirm"),kind="message_send",level=3,idempotency_key="key",payload_cipher=b"x")
    tool=Mock();monkeypatch.setattr(svc,"_link",lambda *a:link);monkeypatch.setattr(svc,"verify_password",lambda *a:False);monkeypatch.setattr(svc,"_execute",tool);monkeypatch.setattr(settings,"whatsapp_assistant_enabled",True)
    with pytest.raises(HTTPException) as exc:svc.confirm_command(DB(),user,cmd,token="token-long-enough",pin="bad-pin")
    assert exc.value.status_code==403;tool.assert_not_called()


def test_heart_ready_outside_meta_window_without_template_is_retained(monkeypatch):
    from app.models.heart_team import HeartTeamCase
    job=SimpleNamespace(id=1,case_id=11,owner_id=7,link_id=9,status="queued",attempts=0,last_error_code=None)
    case=SimpleNamespace(id=11,owner_id=7,status="awaiting_review")
    link=SimpleNamespace(id=9,user_id=7,status="active",phone_cipher=b"x",retention_days=30)
    db=DB({WhatsAppHeartTeamJob:[job],HeartTeamCase:[case],WhatsAppLink:[link],WhatsAppMessage:[]})
    monkeypatch.setattr(whatsapp_jobs,"SessionLocal",lambda:db);monkeypatch.setattr(whatsapp_jobs,"decifrar_campo",lambda *a:'{"phone":"5511999999999"}');monkeypatch.setattr(whatsapp_jobs,"require_positive_tariff",lambda *a:10);monkeypatch.setattr(whatsapp_jobs,"enforce_cost_headroom",lambda *a:None);monkeypatch.setattr(settings,"whatsapp_assistant_enabled",True);monkeypatch.setattr(settings,"heart_team_enabled",True);monkeypatch.setattr(settings,"whatsapp_provider","meta");monkeypatch.setattr(settings,"whatsapp_heart_team_ready_template_name","")
    result=whatsapp_jobs.process_heart_team_job(1,adapter=Mock())
    assert result["status"]=="retry" and job.last_error_code=="outside_window_no_template"


def test_heart_notification_revoked_link_cancels_without_provider(monkeypatch):
    from app.models.heart_team import HeartTeamCase
    job=SimpleNamespace(id=1,case_id=11,owner_id=7,link_id=9,status="queued",attempts=0,last_error_code=None,completed_at=None);case=SimpleNamespace(id=11,owner_id=7,status="awaiting_review");db=DB({WhatsAppHeartTeamJob:[job],HeartTeamCase:[case],WhatsAppLink:[]});adapter=Mock()
    monkeypatch.setattr(whatsapp_jobs,"SessionLocal",lambda:db);monkeypatch.setattr(settings,"whatsapp_assistant_enabled",True);monkeypatch.setattr(settings,"heart_team_enabled",True)
    result=whatsapp_jobs.process_heart_team_job(1,adapter=adapter)
    assert result["status"]=="cancelled" and job.last_error_code=="link_revoked";adapter.send_text.assert_not_called()


def test_heart_notification_meta_cost_is_counted_once(monkeypatch):
    from app.models.heart_team import HeartTeamCase
    from app.services.whatsapp_outbox import OutboxDelivery
    job=SimpleNamespace(id=1,case_id=11,owner_id=7,link_id=9,status="queued",attempts=0,last_error_code=None,completed_at=None,provider_message_id=None);case=SimpleNamespace(id=11,owner_id=7,status="awaiting_review");link=SimpleNamespace(id=9,user_id=7,status="active",phone_cipher=b"x",retention_days=30);outbox=SimpleNamespace(id=20,provider_message_id="wamid.ready",estimated_cost_microunits=10)
    class SeqDB(DB):
        def __init__(self):super().__init__({WhatsAppHeartTeamJob:[job],HeartTeamCase:[case],WhatsAppLink:[link],WhatsAppOutboundOutbox:[outbox]});self.message_queries=0
        def query(self,model):
            if model is WhatsAppMessage or getattr(model,"class_",None) is WhatsAppMessage:
                self.message_queries+=1;return Query([SimpleNamespace(id=2)] if self.message_queries==1 else [])
            return super().query(model)
    db=SeqDB();sent=SimpleNamespace(message_id="wamid.ready")
    monkeypatch.setattr(whatsapp_jobs,"SessionLocal",lambda:db);monkeypatch.setattr(whatsapp_jobs,"decifrar_campo",lambda *a:'{"phone":"5511999999999"}');monkeypatch.setattr(whatsapp_jobs,"require_positive_tariff",lambda *a:10);monkeypatch.setattr(whatsapp_jobs,"enforce_cost_headroom",lambda *a:None);monkeypatch.setattr(whatsapp_jobs,"deliver_once",lambda *a,**k:OutboxDelivery("sent",sent,20));monkeypatch.setattr(whatsapp_jobs,"cifrar_campo",lambda *a:b"encrypted");monkeypatch.setattr(settings,"whatsapp_assistant_enabled",True);monkeypatch.setattr(settings,"heart_team_enabled",True);monkeypatch.setattr(settings,"whatsapp_provider","meta")
    result=whatsapp_jobs.process_heart_team_job(1,adapter=Mock())
    message=next(x for x in db.added if isinstance(x,WhatsAppMessage))
    assert result["status"]=="notified" and message.meta_billable is True and message.estimated_cost_microunits==10 and outbox.estimated_cost_microunits==0


def test_lgpd_delete_erases_media_transport_rows_before_link(monkeypatch):
    link,user=link_user();message=WhatsAppMessage(id=4,link_id=9,owner_id=7,direction="inbound",message_type="document",payload_cipher=b"x",status="reviewed",expires_at=utcnow())
    db=DB({WhatsAppMessage:[message],WhatsAppHeartTeamJob:[SimpleNamespace(id=1)],WhatsAppCommand:[SimpleNamespace(id=2)],WhatsAppUsageMetric:[SimpleNamespace(id=3)],WhatsAppPairing:[SimpleNamespace(id=4)],WhatsAppLink:[link]})
    removed=[];monkeypatch.setattr(api,"decrypt_payload",lambda *a:{"media_storage_key":"cipher.bin"});monkeypatch.setattr(api,"apagar",lambda key,**k:removed.append(key))
    result=api.delete_data(SimpleNamespace(confirm=True),db=db,user=user)
    assert result["deleted"] is True and removed==["cipher.bin"] and db.deleted==[link] and db.commits==1


def test_direct_heart_team_with_pii_is_blocked_until_review(monkeypatch):
    link,user=link_user();db=DB({WhatsAppCommand:[]});monkeypatch.setattr(svc,"enforce_limits",lambda *a:None);monkeypatch.setattr(svc,"_encrypt",lambda *a:b"encrypted");monkeypatch.setattr(svc,"_audit",lambda *a,**k:None);monkeypatch.setattr(settings,"whatsapp_assistant_enabled",True)
    command,result,_,_=svc.create_command(db,user,link,text="Heart Team CPF 123.456.789-00",idempotency_key="heart-pii-1",explicit_kind="heart_team_start",arguments={})
    assert command.status=="blocked_pii" and result["erro"]=="blocked_pii"
    assert not any(isinstance(x,WhatsAppHeartTeamJob) for x in db.added)


@pytest.mark.parametrize("text",["excluir dados","apagar dados","alterar permissões","fazer deploy"])
def test_all_critical_actions_are_level4_regardless_of_explicit_kind(text):
    assert svc.payload_requires_level4("reminder_create",text,{}) is True


def test_draft_and_list_are_persisted_and_reversibly_deleted(monkeypatch):
    link,user=link_user();db=DB();cmd=SimpleNamespace(kind="draft_save",level=2,link_id=9,id=12,owner_id=7,status="completed",undo_token_hash=token_hash("undo-token-long-enough","undo"),result_cipher=b"x")
    monkeypatch.setattr(svc,"_permission",lambda *a:True);monkeypatch.setattr(svc,"_link",lambda *a:link);monkeypatch.setattr(svc,"_encrypt",lambda *a:b"encrypted");monkeypatch.setattr(svc,"_audit",lambda *a,**k:None)
    result=svc._execute(db,user,cmd,{"text":"rascunho","arguments":{"titulo":"Plantão","corpo":"Itens administrativos"}})
    draft=next(x for x in db.added if x.__class__.__name__=="WhatsAppDraft");cmd.result_cipher=b"result";monkeypatch.setattr(svc,"decrypt_payload",lambda *a:result);db.scripted[draft.__class__]=[draft]
    undone=svc.undo_command(db,user,cmd,token="undo-token-long-enough")
    assert result["draft"]["id"]==draft.id and draft.status=="deleted" and undone["status"]=="undone"


def test_pdf_extract_uses_installed_pymupdf_runtime():
    import fitz
    document=fitz.open();page=document.new_page();page.insert_text((72,72),"Documento científico revisável")
    data=document.tobytes();document.close()
    assert "Documento científico" in svc._extract_document(data,"application/pdf")


def test_production_rate_limit_fails_closed_when_redis_is_unavailable(monkeypatch):
    from redis.exceptions import ConnectionError
    monkeypatch.setattr(whatsapp_security,"_distributed_rate",lambda *a,**k:(_ for _ in ()).throw(ConnectionError("offline")));monkeypatch.setattr(whatsapp_security,"ambiente_atual",lambda:"production")
    assert whatsapp_security.allow_rate("sender") is False


def test_whatsapp_origin_n3_reissues_token_only_in_authenticated_app_then_confirms(monkeypatch):
    user=SimpleNamespace(id=7);link=SimpleNamespace(pin_hash="hash");cmd=SimpleNamespace(id=44,owner_id=7,status="awaiting_confirmation",level=3,kind="email_send",confirmation_token_hash=None,confirmation_expires_at=None,idempotency_key="wa:n3",payload_cipher=b"x",result_cipher=b"x",executed_at=None)
    db=DB({WhatsAppCommand:[cmd],WhatsAppUsageMetric:[]});monkeypatch.setattr(api,"random_token",lambda:"reissued-token-long-enough");monkeypatch.setattr(api,"_audit",lambda *a,**k:None);monkeypatch.setattr(settings,"whatsapp_assistant_enabled",True)
    issued=api.reissue_confirmation(44,db=db,user=user)
    assert issued["confirmation_token"]=="reissued-token-long-enough" and cmd.confirmation_token_hash==token_hash(issued["confirmation_token"],"confirm")
    monkeypatch.setattr(svc,"_link",lambda *a:link);monkeypatch.setattr(svc,"verify_password",lambda *a:True);monkeypatch.setattr(svc,"decrypt_payload",lambda *a:{"text":"administrativo","arguments":{"para":"x@example.com","assunto":"Agenda","corpo":"Confirme"}});monkeypatch.setattr(svc,"_execute",lambda *a,**k:{"mensagem":"enviado"});monkeypatch.setattr(svc,"_encrypt",lambda *a:b"result");monkeypatch.setattr(svc,"_audit",lambda *a,**k:None)
    result=svc.confirm_command(db,user,cmd,token=issued["confirmation_token"],pin="123456")
    assert result["mensagem"]=="enviado" and cmd.status=="completed"


def test_pending_contract_exposes_transcript_and_pii_branch(monkeypatch):
    _,user=link_user();message=WhatsAppMessage(id=4,link_id=9,owner_id=7,direction="inbound",message_type="audio",payload_cipher=b"x",pii_kinds=["telefone"],status="awaiting_anonymization_confirmation",expires_at=utcnow(),created_at=utcnow())
    db=DB({WhatsAppMessage:[message]});monkeypatch.setattr(api,"decrypt_payload",lambda *a:{"transcript":"Enviar mensagem\nTelefone: +55 11 99999-9999\nTemplate: aviso\nOpt-in ID: 2"})
    row=api.pending(db=db,user=user)[0]
    assert "Enviar mensagem" in row["transcript"] and row["review_text"]==row["transcript"] and row["pii_use_allowed"] is True


def test_admin_metrics_groups_cost_by_operation_and_subscriber():
    now=utcnow();usage=WhatsAppUsageMetric(owner_id=7,link_id=9,idempotency_key="x",operation="document_summary_ai",provider="openai",estimated_cost_microunits=50,success=True,created_at=now)
    reservation=WhatsAppOutboundOutbox(id=3,idempotency_key="o",owner_id=7,link_id=9,mode="template",payload_cipher=b"x",status="sending",estimated_cost_microunits=20,expires_at=now+timedelta(days=1),created_at=now)
    result=api.admin_metrics(db=DB({WhatsAppUsageMetric:[usage],WhatsAppOutboundOutbox:[reservation]}),admin=SimpleNamespace(id=1))
    assert result["operations"]["document_summary_ai"]["estimated_cost_microunits"]==50
    assert result["subscribers"][0]["reserved_cost_microunits"]==20


def test_address_anonymization_is_real_and_heart_team_can_never_use_raw_pii(monkeypatch):
    text="Heart Team para paciente na Rua das Flores, 120; CPF 123.456.789-00"
    reviewed,kinds=whatsapp_security.anonymize_text(text)
    assert "endereco" in kinds and "Rua das Flores" not in reviewed and "123.456.789-00" not in reviewed
    assert api._raw_pii_allowed(text,kinds) is False


def test_extended_identifiers_are_removed_fail_closed():
    text="Nome: Maria da Silva; CNS: 123456789012345; RG: 12.345.678-9; nascimento: 01/02/1970; CEP 01310-100"
    reviewed,kinds=whatsapp_security.anonymize_text(text)
    assert {"nome","cns","rg","data_nascimento","cep"}.issubset(set(kinds))
    for raw in ("Maria da Silva","123456789012345","12.345.678-9","01/02/1970","01310-100"):
        assert raw not in reviewed


def test_raw_pii_is_allowed_only_as_required_external_recipient():
    email="Enviar e-mail para medico@example.com\nAssunto: Agenda\nCorpo: Reunião administrativa"
    assert api._raw_pii_allowed(email,["email"]) is True
    assert api._raw_pii_allowed(email,["email","cpf"]) is False
    assert api._raw_pii_allowed("Heart Team telefone +55 11 99999-9999",["telefone"]) is False


def test_routine_uses_canonical_tool_and_missing_fields_have_no_side_effect(monkeypatch):
    link,user=link_user();cmd=SimpleNamespace(kind="routine_create",level=2,link_id=9,id=1);tool=Mock(return_value={"criado":True,"rotina":[{"id":1}]})
    monkeypatch.setattr(svc,"_permission",lambda *a:True);monkeypatch.setattr(svc,"executar_tool_assistente",tool)
    blocked=svc._execute(DB(),user,cmd,{"text":"rotina","arguments":{"dias_semana":["segunda"]}})
    assert blocked["erro"]=="routine_data_required";tool.assert_not_called()
    result=svc._execute(DB(),user,cmd,{"text":"rotina","arguments":{"dias_semana":["segunda"],"hora_inicio":"08:00","hora_fim":"12:00","titulo":"Clínica","local_nome":"Clínica"}})
    assert result["criado"] is True and tool.call_args.args[0]=="agenda_criar_rotina_semanal"


def test_patient_material_is_private_draft_not_published(monkeypatch):
    link,user=link_user();db=DB();cmd=SimpleNamespace(kind="patient_material_draft",level=2,link_id=9,id=2)
    monkeypatch.setattr(svc,"_permission",lambda *a:True);monkeypatch.setattr(svc,"_link",lambda *a:link);monkeypatch.setattr(svc,"_encrypt",lambda *a:b"encrypted")
    result=svc._execute(db,user,cmd,{"text":"material","arguments":{"titulo":"Orientação","corpo":"Texto educativo para revisão"}})
    draft=next(x for x in db.added if x.__class__.__name__=="WhatsAppDraft")
    assert result["draft"]["kind"]=="patient_material" and draft.status=="active"


def test_media_review_blocks_document_with_detected_identifiers(monkeypatch):
    link,user=link_user();message=WhatsAppMessage(id=4,link_id=9,owner_id=7,direction="inbound",message_type="document",payload_cipher=b"x",status="awaiting_media_review",expires_at=utcnow());db=DB({WhatsAppMessage:[message]});create=Mock()
    monkeypatch.setattr(settings,"whatsapp_assistant_enabled",True);monkeypatch.setattr(api,"_media_for_command",lambda *a:(message,{"mime_type":"application/pdf"},b"pdf"));monkeypatch.setattr(api,"_extract_document",lambda *a:"Paciente na Rua das Flores, 120");monkeypatch.setattr(api,"create_command",create)
    with pytest.raises(HTTPException) as exc:api.media_review(4,MediaReview(confirmed=True,action="heart_team",contains_no_identifiers=True),db=db,user=user)
    assert exc.value.status_code==422;create.assert_not_called()


def test_document_summary_cache_is_encrypted_tenant_scoped_and_avoids_second_provider_call(monkeypatch):
    from app.services.ia import provedor
    class CacheQuery(Query):
        def filter(self,*conditions,**kwargs):
            for condition in conditions:
                key=getattr(getattr(condition,"left",None),"key",None);value=getattr(getattr(condition,"right",None),"value",None)
                if key in {"owner_id","cache_key"}:self.values=[row for row in self.values if getattr(row,key)==value]
            return self
    class CacheDB(DB):
        def query(self,model):
            if model is WhatsAppSummaryCache:return CacheQuery([row for row in self.added if isinstance(row,WhatsAppSummaryCache)])
            return super().query(model)
    db=CacheDB();provider=Mock();provider.responder.side_effect=[SimpleNamespace(modelo="economico-v1",tokens_entrada=10,tokens_saida=5,texto="Resumo A"),SimpleNamespace(modelo="economico-v1",tokens_entrada=10,tokens_saida=5,texto="Resumo B")]
    monkeypatch.setattr(svc,"_permission",lambda *a:True);monkeypatch.setattr(svc,"_media_for_command",lambda *a:(None,{"sha256":"abc123","mime_type":"text/plain","sanitized_extract":"Conteúdo científico"},b""));monkeypatch.setattr(svc,"_link",lambda *a:SimpleNamespace(retention_days=30));monkeypatch.setattr(svc,"_encrypt",lambda value,owner:value);monkeypatch.setattr(svc,"decrypt_payload",lambda value,owner:value);monkeypatch.setattr(svc,"require_positive_tariff",lambda *a:10);monkeypatch.setattr(svc,"enforce_cost_headroom",lambda *a:None);monkeypatch.setattr(provedor,"obter_provedor",lambda:provider)
    cmd=lambda cid:SimpleNamespace(kind="document_summary",level=1,link_id=9,id=cid)
    first=svc._execute(db,SimpleNamespace(id=7),cmd(1),{"arguments":{"media_message_id":4}})
    hit=svc._execute(db,SimpleNamespace(id=7),cmd(2),{"arguments":{"media_message_id":4}})
    other=svc._execute(db,SimpleNamespace(id=8),cmd(3),{"arguments":{"media_message_id":4}})
    assert first["cache_hit"] is False and hit["cache_hit"] is True and hit["summary"]=="Resumo A"
    assert other["cache_hit"] is False and other["summary"]=="Resumo B" and provider.responder.call_count==2
    caches=[row for row in db.added if isinstance(row,WhatsAppSummaryCache)]
    assert {row.owner_id for row in caches}=={7,8} and all(not isinstance(row.result_cipher,(str,bytes)) for row in caches)


def test_summary_cache_is_removed_by_retention_and_lgpd_delete(monkeypatch):
    expired=WhatsAppSummaryCache(owner_id=7,cache_key="k",media_sha256="m",model="model",pipeline_version="v1",result_cipher=b"cipher",expires_at=utcnow()-timedelta(seconds=1))
    db=DB({WhatsAppSummaryCache:[expired]});assert svc.purge_expired_data(db,owner_id=7)==1
    link,user=link_user();cache=WhatsAppSummaryCache(owner_id=7,cache_key="k2",media_sha256="m",model="model",pipeline_version="v1",result_cipher=b"cipher",expires_at=utcnow()+timedelta(days=1));queried=[]
    class RecordingDB(DB):
        def query(self,model):queried.append(model);return super().query(model)
    api.delete_data(SimpleNamespace(confirm=True),db=RecordingDB({WhatsAppLink:[link],WhatsAppSummaryCache:[cache]}),user=user)
    assert WhatsAppSummaryCache in queried
