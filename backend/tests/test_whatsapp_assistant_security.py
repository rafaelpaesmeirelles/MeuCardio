from datetime import datetime,timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
import json,pytest
from pydantic import ValidationError
from app.schemas.whatsapp import PairingCreate,PERMISSION_KEYS
from app.services.whatsapp_intents import parse_intent
from app.services.whatsapp_security import utcnow
from app.services import whatsapp_assistant as svc
from app.services import whatsapp_outbox
from app.services.whatsapp_adapter import MetaCloudAdapter
from app.services.whatsapp_adapter import MediaResult,WhatsAppProviderError
from app.services.whatsapp_inbound import _interactive_action,_validate_media,iter_meta_messages
from app.services.whatsapp_security import trusted_interactive
from app.api import whatsapp as api
from app.core.config import settings

class Q:
 def __init__(self,v=None):self.v=v
 def filter(self,*a):return self
 def first(self):return self.v
 def scalar(self):return self.v
 def all(self):return self.v or []
 def with_for_update(self):return self
 def delete(self,**k):return 0
class DB:
 def __init__(self,m=None):self.m=m or {};self.added=[];self.commits=0
 def query(self,x):return Q(self.m.get(x))
 def add(self,x):self.added.append(x)
 def flush(self):
  for i,x in enumerate(self.added):
   if getattr(x,"id",None) is None:x.id=100+i
 def commit(self):self.commits+=1;self.flush()
 def rollback(self):pass
 def close(self):pass

def test_flag_defaults_off(): assert settings.whatsapp_assistant_enabled is False
def test_permissions_contract_exact():
 payload={k:True for k in PERMISSION_KEYS};assert PairingCreate(permissions=payload,consent=True).permissions==payload
 with pytest.raises(ValidationError):PairingCreate(permissions={"agenda":True},consent=True)
@pytest.mark.parametrize("body",["Você tem diagnóstico de FA","T.O.M.E 10mg","orientação terapêutica: suspenda"])
def test_nested_n4_blocks_external(body):assert svc.payload_requires_level4("email_send","administrativo",{"body":{"nested":body}})
@pytest.mark.parametrize("body",[
 "O paciente tem infarto e precisa de AAS",
 "PACIENTE APRESENTA ARRITMIA; DEVE USAR AMIODARONA",
 "A paciente está com insuficiência cardíaca e necessita de diurético",
])
def test_semantic_clinical_decisions_are_n4_without_literal_labels(body):
 assert svc.payload_requires_level4("email_send","mensagem administrativa",{"corpo":body})
def test_administrative_patient_message_remains_n3():
 assert not svc.payload_requires_level4("email_send","administrativo",{"corpo":"O paciente confirmou a agenda de terça-feira"})
def test_nl_message_parser_requires_explicit_fields():
 p=parse_intent("Enviar mensagem",now=utcnow(),timezone_name="America/Sao_Paulo");assert p.kind=="message_send" and p.clarification
def test_nl_message_parser_extracts_template_optin():
 p=parse_intent("Enviar mensagem\nTelefone: +55 11 99999-9999\nTemplate: aviso\nOpt-in ID: 81\nParâmetros: Olá",now=utcnow(),timezone_name="America/Sao_Paulo");assert p.clarification is None and p.arguments["recipient_opt_in_id"]==81
def test_undo_button_is_allowlisted_and_has_text_fallback():
 r=api._safe_reply_payload({"command_id":3,"undo_token":"abcdefghijklmnop_1234"});assert r["button_id"].startswith("corvia:undo:3:") and "DESFAZER" in r["text"]
def test_meta_template_payload(monkeypatch):
 monkeypatch.setattr(settings,"whatsapp_phone_number_id","p");monkeypatch.setattr(settings,"whatsapp_meta_access_token","t");monkeypatch.setattr(settings,"whatsapp_meta_app_secret","s");monkeypatch.setattr(settings,"whatsapp_meta_verify_token","v")
 response=Mock(status_code=200);response.json.return_value={"messages":[{"id":"wamid.1"}]};client=Mock();client.post.return_value=response
 out=MetaCloudAdapter(client=client).send_template("5511","approved","pt_BR",["x"],idempotency_key="k");assert out.message_id=="wamid.1" and client.post.call_args.kwargs["json"]["type"]=="template"
def test_outbox_crash_never_resends(monkeypatch):
 from app.models.whatsapp import WhatsAppOutboundOutbox
 class ODB(DB):
  row=None
  def query(self,x):return Q(self.row if x is WhatsAppOutboundOutbox else None)
  def add(self,x):self.row=x;super().add(x)
 db=ODB();monkeypatch.setattr(whatsapp_outbox,"cifrar_campo",lambda *a:b"x");calls=[]
 class A:
  def send_text(self,*a,**k):calls.append(1);raise SystemExit
 with pytest.raises(SystemExit):whatsapp_outbox.deliver_once(db,adapter=A(),idempotency_key="key",owner_id=1,link_id=1,phone="5511",text="x")
 assert whatsapp_outbox.deliver_once(db,adapter=A(),idempotency_key="key",owner_id=1,link_id=1,phone="5511",text="x").status=="sending" and calls==[1]
def test_retention_runner_without_http(monkeypatch):
 from app.commands import purge_expired_whatsapp_data as runner
 db=DB();monkeypatch.setattr(runner,"purge_expired_data",lambda d:4);assert runner.purge_once(session_factory=lambda:db,origin="test")==4 and db.commits==1
def test_migration_chained_after_heart():
 text=Path("backend/migrations/versions/f88w20260831_whatsapp_assistant.py").read_text();assert 'down_revision="f87h20260831"' in text

def test_meta_button_and_list_only_accept_server_allowlist():
 button={"type":"interactive","interactive":{"button_reply":{"id":"corvia:menu:agenda","title":"payload livre ignorado"}}}
 listed={"type":"interactive","interactive":{"list_reply":{"id":"corvia:menu:tarefas","title":"qualquer"}}}
 assert _interactive_action(button)=={"action":"text","text":"consultar agenda"}
 assert _interactive_action(listed)=={"action":"text","text":"consultar tarefas"}
 assert _interactive_action({"type":"interactive","interactive":{"button_reply":{"id":"ataque:deploy"}}}) is None

def test_meta_dynamic_undo_is_strictly_validated():
 valid=trusted_interactive("corvia:undo:42:abcdefghijklmnop_1234")
 assert valid["action"]=="undo" and valid["command_id"]==42
 assert trusted_interactive("corvia:undo:42:curto") is None
 assert trusted_interactive("corvia:undo:42:x;deploy") is None

def test_iter_meta_messages_handles_multi_entry_batch():
 payload={"entry":[{"changes":[{"value":{"messages":[{"id":"a"},{"id":"b"}]}}]},{"changes":[{"value":{"messages":[{"id":"c"}]}}]}]}
 assert [x["id"] for x in iter_meta_messages(payload)]==["a","b","c"]

def test_media_validation_rejects_type_spoofing(monkeypatch):
 monkeypatch.setattr(settings,"whatsapp_max_media_bytes",1024)
 with pytest.raises(Exception):_validate_media("image",MediaResult(b"%PDF-1.4\n%%EOF","image/jpeg","x"))
 assert _validate_media("audio",MediaResult(b"OggSdata","audio/ogg","a"))[0]=="audio/ogg"
 with pytest.raises(Exception):_validate_media("audio",MediaResult(b"x","application/octet-stream","a"))

def test_meta_media_download_enforces_provider_size(monkeypatch):
 monkeypatch.setattr(settings,"whatsapp_phone_number_id","p");monkeypatch.setattr(settings,"whatsapp_meta_access_token","t");monkeypatch.setattr(settings,"whatsapp_meta_app_secret","s");monkeypatch.setattr(settings,"whatsapp_meta_verify_token","v");monkeypatch.setattr(settings,"whatsapp_max_media_bytes",5)
 metadata=Mock(status_code=200);metadata.json.return_value={"url":"https://media","file_size":6}
 client=Mock();client.get.return_value=metadata
 with pytest.raises(WhatsAppProviderError):MetaCloudAdapter(client=client).download_media("media_1")
 assert client.get.call_count==1

def test_audio_transcription_returns_reviewable_text(monkeypatch):
 monkeypatch.setattr(settings,"whatsapp_phone_number_id","p");monkeypatch.setattr(settings,"whatsapp_meta_access_token","t");monkeypatch.setattr(settings,"whatsapp_meta_app_secret","s");monkeypatch.setattr(settings,"whatsapp_meta_verify_token","v");monkeypatch.setattr(settings,"openai_api_key","key")
 import openai
 client=Mock();client.audio.transcriptions.create.return_value=SimpleNamespace(text="  revisar antes de executar  ")
 monkeypatch.setattr(openai,"OpenAI",lambda **_:client)
 assert MetaCloudAdapter(client=Mock()).transcribe_audio(b"audio",filename="a.ogg",mime_type="audio/ogg")=="revisar antes de executar"
