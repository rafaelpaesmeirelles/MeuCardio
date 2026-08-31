import json,re
from datetime import timedelta
from pathlib import Path
from fastapi import APIRouter,BackgroundTasks,Depends,Header,HTTPException,Query,Request,Response
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.db import get_db
from app.core.security import current_user,hash_password,require_admin
from app.models.user import User
from app.models.whatsapp import *
from app.schemas.whatsapp import *
from app.services.cofre import cifrar_campo,decifrar_campo
from app.services.whatsapp_security import *
from app.services.whatsapp_assistant import *
from app.services.whatsapp_assistant import _audit,_extract_document,_media_for_command
from app.services.whatsapp_outbox import deliver_once
from app.services.whatsapp_adapter import get_adapter
from app.services.whatsapp_jobs import process_pending_heart_team_jobs
from app.services.whatsapp_inbound import iter_meta_messages,process_meta_message
from app.services.whatsapp_intents import parse_intent

router=APIRouter(prefix="/api/whatsapp-assistant",tags=["whatsapp-assistant"]);public_router=APIRouter(prefix="/api/whatsapp-assistant/meta",tags=["whatsapp-meta"]);admin_router=APIRouter(prefix="/api/admin/whatsapp",tags=["admin-whatsapp"])
def _raw_pii_allowed(text,kinds):
 parsed=parse_intent(text,now=utcnow(),timezone_name=settings.whatsapp_default_timezone);allowed={"email_send":{"email"},"message_send":{"telefone"}}
 return bool(parsed.kind in allowed and set(kinds or {}).issubset(allowed[parsed.kind]))
def _link(db,u):return db.query(WhatsAppLink).filter(WhatsAppLink.user_id==u.id).first()
def _active(db,u):
 l=_link(db,u)
 if not l or l.status!="active":raise HTTPException(404,"WhatsApp não vinculado")
 return l
def _out(c,result=None,confirmation=None,undo=None):return {"id":c.id,"status":c.status,"kind":c.kind,"level":c.level,"requires_confirmation":c.status=="awaiting_confirmation","requires_in_app":c.requires_in_app,"confirmation_token":confirmation,"undo_token":undo,"message":(result or {}).get("mensagem","Comando recebido."),"result":result}
@router.get("")
def link_status(db:Session=Depends(get_db),user:User=Depends(current_user)):
 l=_link(db,user);return {"connected":bool(l and l.status=="active"),"status":l.status if l else "not_connected","phone_masked":mask_phone(json.loads(decifrar_campo(l.phone_cipher,user.id))["phone"]) if l else None,"paired_at":l.paired_at if l else None,"retention_days":l.retention_days if l else None,"permissions":l.permissions if l else {},"provider":settings.whatsapp_provider,"feature_enabled":settings.whatsapp_assistant_enabled}
@router.post("/pairings",status_code=201)
def pairing(data:PairingCreate,db:Session=Depends(get_db),user:User=Depends(current_user)):
 if not data.consent:raise HTTPException(422,"Consentimento obrigatório")
 p,code=create_pairing(db,user,retention_days=data.retention_days,permissions=data.permissions,pin=data.pin);db.commit();return {"code":code,"expires_at":p.expires_at,"whatsapp_number":settings.whatsapp_business_phone_number or None}
@router.post("/pairings/complete")
def pairing_complete(data:PairingComplete,request:Request,db:Session=Depends(get_db),user:User=Depends(current_user)):
 feature_guard()
 if settings.whatsapp_provider!="sandbox":raise HTTPException(404,"Pareamento manual indisponível")
 client=request.client.host if request.client else "unknown";keys=(f"pairing-api:user:{user.id}",f"pairing-api:code:{token_hash(data.code,'pairing-attempt')}",f"pairing-api:ip:{client}")
 if not all(allow_rate(key,limit=settings.whatsapp_pairing_max_attempts,window_seconds=settings.whatsapp_pairing_ttl_seconds) for key in keys):raise HTTPException(429,"Muitas tentativas de pareamento")
 l=complete_pairing(db,code=data.code,phone=data.phone,expected_user_id=user.id);db.commit();return {"ok":True,"link_id":l.id}
@router.patch("")
def update_link(data:LinkUpdate,db:Session=Depends(get_db),user:User=Depends(current_user)):
 feature_guard();l=_active(db,user)
 if data.retention_days is not None:l.retention_days=data.retention_days
 if data.permissions is not None:l.permissions=data.permissions
 if data.pin is not None:l.pin_hash=hash_password(data.pin)
 db.commit();return {"ok":True}
@router.delete("/link")
def disconnect(db:Session=Depends(get_db),user:User=Depends(current_user)):
 l=_active(db,user);revoke_link(db,user,l);db.commit();return {"ok":True,"status":"revoked"}
@router.post("/recipient-opt-ins",status_code=201)
def optin(data:RecipientOptInCreate,db:Session=Depends(get_db),user:User=Depends(current_user)):
 feature_guard();l=_active(db,user)
 if not data.confirm:raise HTTPException(422,"Confirmação obrigatória")
 e=WhatsAppOptEvent(link_id=l.id,owner_id=user.id,event="opt_in",purpose="external_message_recipient",detail=canonical_json({"recipient_phone_hash":phone_hash(data.phone),"source":data.source,"purpose":data.purpose}));db.add(e);db.flush();db.commit();return {"ok":True,"opt_in_id":e.id,"phone_masked":mask_phone(data.phone)}
@router.post("/recipient-opt-outs")
def optout(data:RecipientOptOutCreate,db:Session=Depends(get_db),user:User=Depends(current_user)):
 feature_guard();l=_active(db,user);e=WhatsAppOptEvent(link_id=l.id,owner_id=user.id,event="opt_out",purpose="external_message_recipient",detail=canonical_json({"recipient_phone_hash":phone_hash(data.phone)}));db.add(e);db.flush();db.commit();return {"ok":True,"opt_out_id":e.id}
@router.post("/commands",response_model=CommandOut,status_code=202)
def command(data:CommandCreate,db:Session=Depends(get_db),user:User=Depends(current_user)):
 c,r,t,u=create_command(db,user,_active(db,user),text=data.text,idempotency_key=data.idempotency_key,explicit_kind=data.kind,arguments=data.arguments);db.commit();return _out(c,r,t,u)
@router.post("/commands/{cid}/confirm",response_model=CommandOut)
def confirm(cid:int,data:CommandConfirm,bg:BackgroundTasks,db:Session=Depends(get_db),user:User=Depends(current_user)):
 c=db.query(WhatsAppCommand).filter(WhatsAppCommand.id==cid,WhatsAppCommand.owner_id==user.id).first()
 if not c:raise HTTPException(404,"Comando ausente")
 r=confirm_command(db,user,c,token=data.token,pin=data.pin);db.commit()
 if c.kind=="heart_team_start" and c.status=="completed":bg.add_task(process_pending_heart_team_jobs,1)
 return _out(c,r)
@router.post("/commands/{cid}/confirmation-token")
def reissue_confirmation(cid:int,db:Session=Depends(get_db),user:User=Depends(current_user)):
 feature_guard();c=db.query(WhatsAppCommand).filter(WhatsAppCommand.id==cid,WhatsAppCommand.owner_id==user.id).with_for_update().first()
 if not c:raise HTTPException(404,"Comando ausente")
 if c.status!="awaiting_confirmation" or c.level!=3:raise HTTPException(409,"Comando não aguarda confirmação")
 token=random_token();c.confirmation_token_hash=token_hash(token,"confirm");c.confirmation_expires_at=utcnow()+timedelta(seconds=settings.whatsapp_confirmation_ttl_seconds);_audit(db,user.id,"whatsapp_confirmation_reissued","whatsapp_command",c.id,detail={"expires_in_seconds":settings.whatsapp_confirmation_ttl_seconds});db.commit();return {"command_id":c.id,"confirmation_token":token,"expires_at":c.confirmation_expires_at}
@router.post("/commands/{cid}/undo",response_model=CommandOut)
def undo(cid:int,data:CommandUndo,db:Session=Depends(get_db),user:User=Depends(current_user)):
 c=db.query(WhatsAppCommand).filter(WhatsAppCommand.id==cid,WhatsAppCommand.owner_id==user.id).first();r=undo_command(db,user,c,token=data.token);db.commit();return _out(c,r)
@router.get("/history")
def history(db:Session=Depends(get_db),user:User=Depends(current_user)):return [{"id":c.id,"kind":c.kind,"level":c.level,"status":c.status,"can_confirm":c.status=="awaiting_confirmation" and c.level==3,"result":decrypt_payload(c.result_cipher,user.id),"created_at":c.created_at} for c in db.query(WhatsAppCommand).filter(WhatsAppCommand.owner_id==user.id).order_by(WhatsAppCommand.created_at.desc()).limit(100).all()]
@router.get("/messages/pending")
def pending(db:Session=Depends(get_db),user:User=Depends(current_user)):
 rows=db.query(WhatsAppMessage).filter(WhatsAppMessage.owner_id==user.id,WhatsAppMessage.status.in_({"awaiting_transcript_review","awaiting_anonymization_confirmation","awaiting_media_review","transcription_unavailable"})).all();result=[]
 for m in rows:
  payload=decrypt_payload(m.payload_cipher,user.id) or {};review_text=payload.get("transcript_reviewed") or payload.get("transcript") or payload.get("text")
  result.append({"id":m.id,"type":m.message_type,"status":m.status,"pii_kinds":m.pii_kinds,"review_text":review_text,"transcript":review_text,"pii_use_allowed":m.status=="awaiting_anonymization_confirmation" and _raw_pii_allowed(review_text or "",m.pii_kinds),"mime_type":payload.get("mime_type"),"filename":payload.get("filename"),"created_at":m.created_at})
 return result
@router.post("/messages/{mid}/transcript")
def transcript(mid:int,data:TranscriptReview,db:Session=Depends(get_db),user:User=Depends(current_user)):
 feature_guard();m=db.query(WhatsAppMessage).filter(WhatsAppMessage.id==mid,WhatsAppMessage.owner_id==user.id).first()
 if not m or m.status not in {"awaiting_transcript_review","transcription_unavailable"}:raise HTTPException(409,"Mensagem não aguarda revisão de transcrição")
 if not data.confirmed:m.status="transcript_rejected";db.commit();return {"ok":True,"status":m.status}
 payload=decrypt_payload(m.payload_cipher,user.id) or {};payload["transcript_reviewed"]=data.text;m.payload_cipher=cifrar_campo(canonical_json(payload),user.id)
 if detect_pii(data.text):m.pii_kinds=detect_pii(data.text);m.status="awaiting_anonymization_confirmation";db.commit();return {"ok":True,"status":m.status}
 c,r,t,u=create_command(db,user,_active(db,user),text=data.text,idempotency_key=f"review:transcript:{m.id}",explicit_kind=None,arguments={},pii_reviewed=True,message_id=m.id);m.status="processed";_audit(db,user.id,"whatsapp_transcript_reviewed","whatsapp_message",m.id);db.commit();return {"ok":True,"status":m.status,"command":_out(c,r,t,u)}
@router.post("/messages/{mid}/pii-review")
def pii_review(mid:int,data:PIIReview,db:Session=Depends(get_db),user:User=Depends(current_user)):
 feature_guard();m=db.query(WhatsAppMessage).filter(WhatsAppMessage.id==mid,WhatsAppMessage.owner_id==user.id).first()
 if not m or m.status!="awaiting_anonymization_confirmation":raise HTTPException(409,"Mensagem não aguarda revisão de identificadores")
 if not data.confirmed:m.status="pii_rejected";db.commit();return {"ok":True,"status":m.status}
 payload=decrypt_payload(m.payload_cipher,user.id) or {};source=payload.get("transcript_reviewed") or payload.get("transcript") or payload.get("text") or ""
 kinds=detect_pii(source)
 if not data.anonymize and not _raw_pii_allowed(source,kinds):raise HTTPException(422,"Dados identificáveis só podem permanecer quando estritamente necessários ao destinatário de e-mail ou mensagem; anonimize o restante")
 reviewed,kinds=anonymize_text(source) if data.anonymize else (source,kinds)
 if data.anonymize and detect_pii(reviewed):raise HTTPException(422,"Não foi possível anonimizar todos os identificadores com segurança")
 payload["reviewed_text"]=reviewed;payload["identifiers_removed"]=bool(data.anonymize);m.payload_cipher=cifrar_campo(canonical_json(payload),user.id)
 c,r,t,u=create_command(db,user,_active(db,user),text=reviewed,idempotency_key=f"review:pii:{m.id}:{int(data.anonymize)}",explicit_kind=None,arguments={},pii_reviewed=True,message_id=m.id);m.status="processed";_audit(db,user.id,"whatsapp_pii_reviewed","whatsapp_message",m.id,detail={"anonymized":data.anonymize,"kinds":kinds});db.commit();return {"ok":True,"status":m.status,"command":_out(c,r,t,u)}
@router.post("/messages/{mid}/media-review")
def media_review(mid:int,data:MediaReview,db:Session=Depends(get_db),user:User=Depends(current_user)):
 feature_guard();m=db.query(WhatsAppMessage).filter(WhatsAppMessage.id==mid,WhatsAppMessage.owner_id==user.id).first()
 if not m or m.status!="awaiting_media_review":raise HTTPException(409,"Mensagem não aguarda revisão de arquivo")
 if not data.confirmed or data.action=="reject":m.status="media_rejected";db.commit();return {"ok":True,"status":m.status,"action":"reject"}
 if data.action=="store_only":m.status="reviewed_stored";_audit(db,user.id,"whatsapp_media_stored","whatsapp_message",m.id);db.commit();return {"ok":True,"status":m.status,"action":data.action}
 if not data.contains_no_identifiers:raise HTTPException(422,"Confirme que o arquivo não contém identificadores ou envie uma versão anonimizada")
 _,media_payload,media_data=_media_for_command(db,user,m.id,require_reviewed=False);extracted=_extract_document(media_data,media_payload.get("mime_type"))
 if extracted and detect_pii(extracted):raise HTTPException(422,"Identificadores detectados no documento. Envie uma versão anonimizada antes de resumir ou encaminhar ao Heart Team")
 kind="document_summary" if data.action=="summarize" else "heart_team_start";text=data.question or ("Resumir documento revisado" if kind=="document_summary" else "CorVIA, monte um Heart Team para este caso")
 c,r,t,u=create_command(db,user,_active(db,user),text=text,idempotency_key=f"review:media:{m.id}:{kind}",explicit_kind=kind,arguments={"media_message_id":m.id,"question":data.question},pii_reviewed=True,message_id=m.id);m.status="processed";_audit(db,user.id,"whatsapp_media_reviewed","whatsapp_message",m.id,detail={"action":data.action});db.commit();return {"ok":True,"status":m.status,"action":data.action,"command":_out(c,r,t,u)}
@router.get("/metrics")
def metrics(db:Session=Depends(get_db),user:User=Depends(current_user)):
 since=utcnow()-timedelta(days=30);rows=db.query(WhatsAppUsageMetric).filter(WhatsAppUsageMetric.owner_id==user.id,WhatsAppUsageMetric.created_at>=since).all();msgs=db.query(WhatsAppMessage).filter(WhatsAppMessage.owner_id==user.id,WhatsAppMessage.created_at>=since).all();return {"commands":len(rows),"messages_received":sum(m.direction=="inbound" for m in msgs),"messages_sent":sum(m.direction=="outbound" for m in msgs),"meta_billable_messages":sum(m.meta_billable for m in msgs),"ai_commands":len(rows),"blocked_commands":sum(bool(r.blocked_reason) for r in rows),"success_rate":sum(r.success for r in rows)/len(rows) if rows else 1,"average_latency_ms":sum(r.latency_ms for r in rows)/len(rows) if rows else 0,"daily_used":sum(r.created_at>=utcnow()-timedelta(days=1) for r in rows),"monthly_used":len(rows),"estimated_cost_microunits":sum(r.estimated_cost_microunits for r in rows)+sum(m.estimated_cost_microunits for m in msgs),"daily_limit":settings.whatsapp_daily_command_limit,"monthly_limit":settings.whatsapp_monthly_command_limit}
@router.delete("/data")
def delete_data(data:RetentionDeleteIn,db:Session=Depends(get_db),user:User=Depends(current_user)):
 if not data.confirm:raise HTTPException(422,"Confirmação obrigatória")
 rows=db.query(WhatsAppMessage).filter(WhatsAppMessage.owner_id==user.id).all()
 for row in rows:
  try:
   key=(decrypt_payload(row.payload_cipher,user.id) or {}).get("media_storage_key")
   if key:apagar(key,raiz=Path(settings.whatsapp_media_dir))
  except Exception:pass
 l=_link(db,user);link_id=l.id if l else None
 db.query(WhatsAppOutboundOutbox).filter(WhatsAppOutboundOutbox.owner_id==user.id).delete(synchronize_session=False);db.query(WhatsAppHeartTeamJob).filter(WhatsAppHeartTeamJob.owner_id==user.id).delete(synchronize_session=False);db.query(WhatsAppMessage).filter(WhatsAppMessage.owner_id==user.id).delete(synchronize_session=False);db.query(WhatsAppCommand).filter(WhatsAppCommand.owner_id==user.id).delete(synchronize_session=False);db.query(WhatsAppDraft).filter(WhatsAppDraft.owner_id==user.id).delete(synchronize_session=False);db.query(WhatsAppSummaryCache).filter(WhatsAppSummaryCache.owner_id==user.id).delete(synchronize_session=False);db.query(WhatsAppUsageMetric).filter(WhatsAppUsageMetric.owner_id==user.id).delete(synchronize_session=False);db.query(WhatsAppPairing).filter(WhatsAppPairing.user_id==user.id).delete(synchronize_session=False);db.query(WhatsAppOptEvent).filter(WhatsAppOptEvent.owner_id==user.id).delete(synchronize_session=False)
 if link_id:db.query(WhatsAppWebhookEvent).filter(WhatsAppWebhookEvent.link_id==link_id).delete(synchronize_session=False)
 if l:db.delete(l)
 db.add(AuditLog(user_id=user.id,action="whatsapp_data_deleted",entity="whatsapp_transport_data",entity_id=str(user.id),detail={"media_files":len(rows)}));db.commit();return {"ok":True,"deleted":True}
def _safe_reply_payload(r):
 if r.get("undo_token") and r.get("command_id"):
  t=r["undo_token"];i=r["command_id"];return {"text":f"Ação concluída. Use o botão ou responda DESFAZER {i} {t}","button_id":f"corvia:undo:{i}:{t}","button_title":"Desfazer"}
 if r.get("requires_confirmation") or r.get("confirmation_token"):return {"text":"Confirme esta ação somente na área autenticada do CorVIA.","button_id":None,"button_title":None}
 return {"text":"Comando recebido. Confira no CorVIA.","button_id":None,"button_title":None}
@public_router.get("/webhook")
def verify(hub_mode:str|None=Query(None,alias="hub.mode"),hub_verify_token:str|None=Query(None,alias="hub.verify_token"),hub_challenge:str|None=Query(None,alias="hub.challenge")):
 if hub_mode=="subscribe" and hub_verify_token==settings.whatsapp_meta_verify_token:return Response(hub_challenge or "")
 raise HTTPException(403,"Inválido")
@public_router.post("/webhook")
async def webhook(request:Request,x_hub_signature_256:str|None=Header(None),db:Session=Depends(get_db)):
 feature_guard();body=await request.body()
 if not verify_meta_signature(body,x_hub_signature_256):raise HTTPException(401,"Assinatura inválida")
 try:payload=json.loads(body)
 except ValueError:raise HTTPException(400,"JSON inválido")
 adapter=get_adapter();results=[]
 for message in iter_meta_messages(payload):
  try:
   result=process_meta_message(db,message,adapter=adapter);db.commit();results.append(result)
  except IntegrityError:
   db.rollback();results.append({"status":"duplicate"})
  except Exception as exc:
   db.rollback();results.append({"status":"failed","error":type(exc).__name__})
 public_results=[{"status":x.get("status") or "processed"} for x in results]
 return {"ok":True,"processed":sum(x.get("status") not in {"duplicate","invalid"} for x in results),"results":public_results}
@admin_router.post("/retention/purge")
def purge(db:Session=Depends(get_db),admin:User=Depends(require_admin)):
 n=purge_expired_data(db);db.commit();return {"ok":True,"deleted":n}
@admin_router.get("/metrics")
def admin_metrics(db:Session=Depends(get_db),admin:User=Depends(require_admin)):
 since=utcnow()-timedelta(days=30);usage=db.query(WhatsAppUsageMetric).filter(WhatsAppUsageMetric.created_at>=since).all();reservations=db.query(WhatsAppOutboundOutbox).filter(WhatsAppOutboundOutbox.created_at>=since).all();messages=db.query(WhatsAppMessage).filter(WhatsAppMessage.created_at>=since).all();events=db.query(WhatsAppWebhookEvent).filter(WhatsAppWebhookEvent.received_at>=since).all();commands=db.query(WhatsAppCommand).filter(WhatsAppCommand.created_at>=since).all();by_user={}
 operations={}
 for r in usage:
  x=by_user.setdefault(r.owner_id,{"owner_id":r.owner_id,"commands":0,"estimated_cost_microunits":0,"daily_used":0,"monthly_used":0,"operations":{}});x["commands"]+=1;x["monthly_used"]+=1;x["daily_used"]+=int(r.created_at>=utcnow()-timedelta(days=1));x["estimated_cost_microunits"]+=r.estimated_cost_microunits;x["operations"][r.operation]=x["operations"].get(r.operation,0)+1;x["daily_limit"]=settings.whatsapp_daily_command_limit;x["monthly_limit"]=settings.whatsapp_monthly_command_limit
  op=operations.setdefault(r.operation,{"commands":0,"success":0,"blocked":0,"estimated_cost_microunits":0});op["commands"]+=1;op["success"]+=int(r.success);op["blocked"]+=int(bool(r.blocked_reason));op["estimated_cost_microunits"]+=r.estimated_cost_microunits
 for o in reservations:
  x=by_user.setdefault(o.owner_id,{"owner_id":o.owner_id,"commands":0,"estimated_cost_microunits":0,"daily_used":0,"monthly_used":0,"operations":{},"daily_limit":settings.whatsapp_daily_command_limit,"monthly_limit":settings.whatsapp_monthly_command_limit});x["reserved_cost_microunits"]=x.get("reserved_cost_microunits",0)+o.estimated_cost_microunits
 models={}
 for row in usage:
  if row.model:models[row.model]=models.get(row.model,0)+1
 return {"period_days":30,"subscribers":list(by_user.values()),"operations":operations,"messages_received":sum(m.direction=="inbound" for m in messages),"messages_sent":sum(m.direction=="outbound" for m in messages),"meta_billable_messages":sum(bool(m.meta_billable) for m in messages),"webhooks_failed":sum(e.status in {"failed","rejected_replay","rate_limited"} for e in events),"commands_blocked":sum(c.status in {"blocked_security","blocked_pii","failed"} for c in commands),"success_rate":sum(bool(x.success) for x in usage)/len(usage) if usage else 1.0,"average_latency_ms":sum(int(x.latency_ms or 0) for x in usage)/len(usage) if usage else 0,"models":models,"outbox_pending":sum(o.status in {"sending","pending","uncertain"} for o in reservations),"monthly_cost_ceiling_microunits":settings.whatsapp_monthly_cost_ceiling_microunits}
