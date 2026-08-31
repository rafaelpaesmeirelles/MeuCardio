import io,json,re,time,unicodedata,hashlib
from datetime import timedelta
from pathlib import Path
from typing import Any
from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy import func,text as sql_text
from app.core.config import settings
from app.core.security import hash_password,verify_password
from app.models.audit import AuditLog
from app.models.user import User
from app.models.whatsapp import *
from app.services.cofre import cifrar_campo,decifrar_campo,apagar,guardar,ler
from app.services.ia.assistant_tools import executar_tool_assistente
from app.services.whatsapp_security import *
from app.services.whatsapp_intents import parse_intent
from app.services.whatsapp_adapter import get_adapter,WhatsAppProviderError
from app.services.whatsapp_outbox import deliver_once

LEVELS={"agenda_list":1,"task_list":1,"scientific_search":1,"document_summary":1,"status_read":1,"daily_summary":1,"pending_items":1,"reminder_create":2,"task_create":2,"appointment_create":2,"appointment_update":2,"routine_create":2,"draft_save":2,"list_create":2,"patient_material_draft":2,"email_send":3,"message_send":3,"document_share":3,"third_party_appointment_cancel":3,"heart_team_start":3,"blocked_critical":4}
PERMISSIONS={"agenda_list":"read_agenda","task_list":"read_tasks","scientific_search":"search_science","document_summary":"search_science","status_read":"read_tasks","daily_summary":"read_agenda","pending_items":"read_tasks","reminder_create":"create_reminder","task_create":"create_reminder","appointment_create":"create_appointment","appointment_update":"create_appointment","routine_create":"create_appointment","draft_save":"create_draft","list_create":"create_draft","patient_material_draft":"create_draft","email_send":"external_communication","message_send":"external_communication","document_share":"external_communication","third_party_appointment_cancel":"external_communication","heart_team_start":"heart_team_draft"}
SUMMARY_PIPELINE_VERSION="whatsapp-summary-v1"
SUMMARY_SYSTEM_PROMPT="Resuma objetivamente o documento fornecido. Não invente dados, doses, classes ou evidências. Identifique limitações. O resultado é rascunho para revisão humana."
def feature_guard():
 if not settings.whatsapp_assistant_enabled: raise HTTPException(503,"Assistente WhatsApp desativado.")
def _encrypt(v,owner): return cifrar_campo(canonical_json(jsonable_encoder(v)),owner)
def decrypt_payload(v,owner): return json.loads(decifrar_campo(v,owner)) if v else None
def _audit(db,uid,action,entity,eid=None,detail=None): db.add(AuditLog(user_id=uid,action=action,entity=entity,entity_id=str(eid) if eid else None,detail=detail or {}))
def _strings(v):
 if isinstance(v,str):return [v]
 if isinstance(v,dict):return sum((_strings(k)+_strings(x) for k,x in v.items()),[])
 if isinstance(v,(list,tuple)):return sum((_strings(x) for x in v),[])
 return []
def _normalized_words(value):
 """Normalize adversarial punctuation/case without discarding word boundaries."""
 folded="".join(c for c in unicodedata.normalize("NFKD",value.casefold()) if not unicodedata.combining(c))
 return re.sub(r"[^a-z0-9]+"," ",folded).strip()
def _external_clinical_decision(value):
 """Fail closed for patient diagnosis/treatment assertions sent outside CorVIA.

 This is intentionally narrower than generic medical vocabulary: educational or
 administrative messages remain N3, while an asserted diagnosis or medication
 direction remains an in-app N4 action regardless of client supplied labels.
 """
 words=_normalized_words(value)
 patient_context=re.search(r"\b(?:paciente|doente|patient|voce|seu quadro|seu exame)\b",words)
 diagnosis_object=re.search(
  r"\b(?:infarto|arritmia|fibrilacao|insuficiencia cardiaca|cardiomiopatia|isquemia|"
  r"trombose|embolia|hipertensao|hipotensao|endocardite|miocardite|pericardite|"
  r"taquicardia|bradicardia|valvopatia|estenose|sindrome|doenca)\b",words)
 therapy_object=re.search(
  r"\b(?:aas|aspirina|anticoagul\w*|antiagreg\w*|betabloq\w*|diuretic\w*|estatina|"
  r"amiodarona|digoxina|sacubitril|valsartana|losartana|enalapril|dapagliflozina|"
  r"medicamento|remedio|tratamento|terapia)\b",words)
 diagnosis_assertion=re.search(
  r"\b(?:tem|apresenta|esta com|sofre de|quadro de|compativel com|sugere|confirma|"
  r"diagnosticad[oa])\b",words)
 therapy_assertion=re.search(
  r"\b(?:precisa de|necessita de|deve|deveria|indicad[oa]|recomendad[oa]|usar|receber|"
  r"manter|retirar|parar|aumentar|reduzir)\b",words)
 return bool(
  patient_context and ((diagnosis_object and diagnosis_assertion) or (therapy_object and therapy_assertion))
  or diagnosis_object and diagnosis_assertion and therapy_object and therapy_assertion
 )
def payload_requires_level4(kind,text,args):
 s=" ".join([text or ""]+_strings(args or {})); f="".join(c for c in unicodedata.normalize("NFKD",s.casefold()) if not unicodedata.combining(c)); compact=re.sub(r"[^a-z0-9]","",f)
 operational=("assinar","prescrever","prescricaoassinada","pagamento","fazerpagamento","merge","deploy","publicar","excluirdados","apagardados","alterarpermissao","alterarpermissoes")
 clinical=("diagnostico","prognostico","orientacaoterapeutica","tome","inicie","suspenda","dosagem")
 external=kind in {"email_send","message_send","document_share"}
 return any(x in compact for x in operational) or (external and (any(x in compact for x in clinical) or _external_clinical_decision(s)))
def create_pairing(db,user,*,retention_days,permissions,pin):
 feature_guard(); code=random_pairing_code(); p=WhatsAppPairing(user_id=user.id,code_hash=token_hash(code,"pairing"),expires_at=utcnow()+timedelta(seconds=settings.whatsapp_pairing_ttl_seconds),retention_days=retention_days,permissions=permissions,pin_hash=hash_password(pin) if pin else None); db.add(p);db.flush();_audit(db,user.id,"whatsapp_pairing_created","whatsapp_pairing",p.id);return p,code
def complete_pairing(db,*,code,phone,expected_user_id=None):
 query=db.query(WhatsAppPairing).filter(WhatsAppPairing.code_hash==token_hash(code,"pairing"))
 if expected_user_id is not None:query=query.filter(WhatsAppPairing.user_id==expected_user_id)
 p=query.with_for_update().first()
 if not p or p.used_at or p.revoked_at or p.expires_at<=utcnow() or p.attempts>=settings.whatsapp_pairing_max_attempts: raise HTTPException(400,"Código inválido/expirado.")
 p.attempts+=1; link=db.query(WhatsAppLink).filter(WhatsAppLink.user_id==p.user_id).first()
 if not link: link=WhatsAppLink(user_id=p.user_id,phone_hash=phone_hash(phone),phone_cipher=_encrypt({"phone":phone},p.user_id));db.add(link)
 link.phone_hash=phone_hash(phone);link.phone_cipher=_encrypt({"phone":phone},p.user_id);link.permissions=p.permissions;link.retention_days=p.retention_days;link.pin_hash=p.pin_hash;link.status="active";link.paired_at=utcnow();p.used_at=utcnow();db.flush();db.add(WhatsAppOptEvent(link_id=link.id,owner_id=p.user_id,event="opt_in",purpose="assistente_pessoal_corvia"));return link
def revoke_link(db,user,link):
 link.status="revoked";link.revoked_at=utcnow();db.add(WhatsAppOptEvent(link_id=link.id,owner_id=user.id,event="opt_out",purpose=link.consent_purpose));_audit(db,user.id,"whatsapp_link_revoked","whatsapp_link",link.id)
def enforce_limits(db,owner):
 d=db.query(func.count(WhatsAppUsageMetric.id)).filter(WhatsAppUsageMetric.owner_id==owner,WhatsAppUsageMetric.created_at>=utcnow()-timedelta(days=1)).scalar() or 0;m=db.query(func.count(WhatsAppUsageMetric.id)).filter(WhatsAppUsageMetric.owner_id==owner,WhatsAppUsageMetric.created_at>=utcnow()-timedelta(days=30)).scalar() or 0
 if d>=settings.whatsapp_daily_command_limit or m>=settings.whatsapp_monthly_command_limit: raise HTTPException(429,"Limite atingido.")
def enforce_cost_headroom(db,owner,cost):
 if getattr(getattr(getattr(db,"bind",None),"dialect",None),"name",None)=="postgresql":db.execute(sql_text("SELECT pg_advisory_xact_lock(hashtextextended(:k,0))"),{"k":f"wa-cost:{owner}"})
 since=utcnow()-timedelta(days=30); total=0
 for model in (WhatsAppUsageMetric,WhatsAppMessage,WhatsAppOutboundOutbox): total+=db.query(func.coalesce(func.sum(model.estimated_cost_microunits),0)).filter(model.owner_id==owner,model.created_at>=since).scalar() or 0
 if total+max(0,int(cost))>settings.whatsapp_monthly_cost_ceiling_microunits: raise HTTPException(429,"Teto de custo atingido.")
def require_positive_tariff(v,op):
 if int(v or 0)<=0: raise HTTPException(503,f"Tarifa de {op} não homologada.")
 return int(v)
def _link(db,user,cmd): return db.query(WhatsAppLink).filter(WhatsAppLink.id==cmd.link_id,WhatsAppLink.user_id==user.id,WhatsAppLink.status=="active").first()
def _permission(db,user,cmd,key):
 l=_link(db,user,cmd);return bool(l and (l.permissions or {}).get(key))
def _recipient_opted_in(db,user,phone,event_id):
 e=db.query(WhatsAppOptEvent).filter(WhatsAppOptEvent.id==event_id,WhatsAppOptEvent.owner_id==user.id,WhatsAppOptEvent.event=="opt_in",WhatsAppOptEvent.purpose=="external_message_recipient").first()
 if not e:return False
 try:
  if json.loads(e.detail or "{}").get("recipient_phone_hash")!=phone_hash(phone):return False
 except ValueError:return False
 outs=db.query(WhatsAppOptEvent).filter(WhatsAppOptEvent.owner_id==user.id,WhatsAppOptEvent.event=="opt_out",WhatsAppOptEvent.created_at>=e.created_at).all()
 for item in outs:
  try:
   if json.loads(item.detail or "{}").get("recipient_phone_hash")==phone_hash(phone):return False
  except (TypeError,ValueError):continue
 return True
def _media_for_command(db,user,message_id,*,require_reviewed=True):
 m=db.query(WhatsAppMessage).filter(WhatsAppMessage.id==message_id,WhatsAppMessage.owner_id==user.id).first()
 if not m:raise HTTPException(404,"Arquivo não encontrado")
 payload=decrypt_payload(m.payload_cipher,user.id) or {};key=payload.get("media_storage_key")
 if require_reviewed and (m.status!="processed" or payload.get("sanitized") is not True):raise HTTPException(409,"Arquivo ainda não foi confirmado pelo assinante")
 if not key:raise HTTPException(409,"Arquivo não está disponível")
 return m,payload,ler(key,user.id,raiz=Path(settings.whatsapp_media_dir))
def _extract_document(data,mime_type):
 if mime_type in {"text/plain","text/csv"}:return data.decode("utf-8-sig")[:30000]
 if mime_type=="application/pdf":
  import fitz
  with fitz.open(stream=data,filetype="pdf") as document:return "\n".join(page.get_text("text") for page in document)[:30000]
 return ""
def _summary_model():
 return settings.anthropic_model if settings.ai_provider=="anthropic" else settings.openai_model
def _summary_cache_key(media,text_value):
 media_sha=media.get("sha256") or hashlib.sha256(text_value.encode("utf-8")).hexdigest()
 material=canonical_json({"media_sha256":media_sha,"model":_summary_model(),"prompt":SUMMARY_SYSTEM_PROMPT,"pipeline":SUMMARY_PIPELINE_VERSION})
 return media_sha,hashlib.sha256(material.encode("utf-8")).hexdigest()
def _summary_cache_get(db,owner_id,key):
 return db.query(WhatsAppSummaryCache).filter(WhatsAppSummaryCache.owner_id==owner_id,WhatsAppSummaryCache.cache_key==key,WhatsAppSummaryCache.expires_at>utcnow()).first()
def _execute(db,user,cmd,payload):
 kind=cmd.kind;a=payload.get("arguments") or {}
 if cmd.level==4 or payload_requires_level4(kind,payload.get("text",""),a):return {"erro":"blocked_level_4","mensagem":"Ação crítica bloqueada."}
 key=PERMISSIONS.get(kind)
 if key and not _permission(db,user,cmd,key):return {"erro":"permission_required","mensagem":"Permissão ausente."}
 if kind in {"agenda_list","task_list"}:
  result=executar_tool_assistente("agenda_listar_compromissos",{},db,user)
  if kind=="task_list" and isinstance(result,dict) and isinstance(result.get("compromissos"),list):
   tasks=[item for item in jsonable_encoder(result["compromissos"]) if (item.get("appointment_type") or item.get("tipo")) in {"tarefa","lembrete"}];return {"total":len(tasks),"tarefas":tasks}
  return result
 if kind in {"reminder_create","task_create","appointment_create"}:
  if not a.get("inicio"):return {"erro":"data_required"}
  return executar_tool_assistente("agenda_criar_compromisso_inteligente",{"inicio":a["inicio"],"duracao_minutos":a.get("duracao_minutos",15),"tipo":"lembrete" if kind=="reminder_create" else "tarefa" if kind=="task_create" else "consulta","observacoes":a.get("descricao") or payload.get("text")},db,user)
 if kind=="appointment_update":
  if not a.get("appointment_id") or not a.get("novo_inicio"):return {"erro":"data_required","mensagem":"Informe compromisso e novo horário."}
  from app.models.clinical_docs import Appointment
  current=db.query(Appointment).filter(Appointment.id==int(a["appointment_id"]),Appointment.owner_id==user.id).first()
  if not current:return {"erro":"appointment_not_found"}
  previous={"appointment_id":current.id,"inicio":current.scheduled_at.isoformat(),"duracao_minutos":current.duration_minutes}
  result=executar_tool_assistente("agenda_reagendar_compromisso",{"appointment_id":a["appointment_id"],"novo_inicio":a["novo_inicio"],"duracao_minutos":a.get("duracao_minutos")},db,user)
  if "erro" not in result:result["_undo"]=previous
  return result
 if kind=="routine_create":
  required=("dias_semana","hora_inicio","hora_fim","titulo")
  if not all(a.get(x) for x in required):return {"erro":"routine_data_required","mensagem":"Informe dias, início, fim e título."}
  return executar_tool_assistente("agenda_criar_rotina_semanal",a,db,user)
 if kind=="third_party_appointment_cancel":
  if not a.get("appointment_id"):return {"erro":"appointment_required","mensagem":"Informe o compromisso."}
  return executar_tool_assistente("agenda_cancelar_compromisso",{"appointment_id":a["appointment_id"],"motivo":a.get("motivo") or "Cancelado após confirmação explícita no CorVIA"},db,user)
 if kind=="scientific_search":
  from app.api import search
  return search.search(q=a.get("q") or payload.get("text"),_=user,db=db)
 if kind=="document_summary":
  _,media,data=_media_for_command(db,user,a.get("media_message_id") or a.get("document_id"));text_value=media.get("sanitized_extract") or _extract_document(data,media.get("mime_type"))
  if not text_value.strip():return {"erro":"text_extraction_unavailable","mensagem":"Não foi possível extrair texto seguro deste documento."}
  media_sha,cache_key=_summary_cache_key(media,text_value);cached=_summary_cache_get(db,user.id,cache_key)
  if cached:
   cached.last_accessed_at=utcnow();result=decrypt_payload(cached.result_cipher,user.id) or {}
   db.add(WhatsAppUsageMetric(owner_id=user.id,link_id=cmd.link_id,idempotency_key=f"summary-cache:{cmd.id}",operation="document_summary_cache_hit",provider="cache",model=cached.model,estimated_cost_microunits=0,success=True))
   return result|{"cache_hit":True}
  cost=require_positive_tariff(settings.whatsapp_scientific_summary_cost_microunits,"resumo científico");enforce_cost_headroom(db,user.id,cost)
  from app.services.ia.provedor import obter_provedor
  try:response=obter_provedor().responder(sistema=SUMMARY_SYSTEM_PROMPT,mensagens=[{"role":"user","content":text_value}],modelo=_summary_model(),usar_internet=False,max_output_tokens=900)
  except Exception:return {"erro":"summary_provider_unavailable","mensagem":"Resumo indisponível; nenhuma conclusão foi gerada."}
  db.add(WhatsAppUsageMetric(owner_id=user.id,link_id=cmd.link_id,idempotency_key=f"summary:{cmd.id}",operation="document_summary_ai",provider=settings.ai_provider,model=response.modelo,input_units=response.tokens_entrada,output_units=response.tokens_saida,estimated_cost_microunits=cost,success=True))
  result={"mensagem":"Resumo em rascunho pronto para revisão.","summary":response.texto,"draft":True,"limitations":["Revisão humana obrigatória."]};link=_link(db,user,cmd)
  db.add(WhatsAppSummaryCache(owner_id=user.id,cache_key=cache_key,media_sha256=media_sha,model=response.modelo or _summary_model(),pipeline_version=SUMMARY_PIPELINE_VERSION,result_cipher=_encrypt(result,user.id),expires_at=utcnow()+timedelta(days=link.retention_days)))
  return result|{"cache_hit":False}
 if kind in {"status_read","daily_summary","pending_items"}:
  from app.models.assinatura import DocumentoEmitido
  from app.models.scientific_user_document import ScientificUserDocument
  agenda=executar_tool_assistente("agenda_listar_compromissos",{"limite":20},db,user)
  drafts=db.query(func.count(WhatsAppDraft.id)).filter(WhatsAppDraft.owner_id==user.id,WhatsAppDraft.status=="active").scalar() or 0
  unsigned=db.query(func.count(DocumentoEmitido.id)).filter(DocumentoEmitido.criado_por==user.id,DocumentoEmitido.assinado_em.is_(None)).scalar() or 0
  scientific=db.query(func.count(ScientificUserDocument.id)).filter(ScientificUserDocument.owner_id==user.id,ScientificUserDocument.analysis_status.in_({"pendente","processando"})).scalar() or 0
  return {"status":"ok","mensagem":"Resumo diário autorizado." if kind=="daily_summary" else "Pendências autorizadas consultadas." if kind=="pending_items" else "Status autorizado consultado.","agenda":agenda,"drafts":drafts,"documents_awaiting_signature":unsigned,"scientific_processes_pending":scientific,"full_result_url":f"{settings.public_url}/conta/integracoes"}
 if kind in {"draft_save","list_create","patient_material_draft"}:
  if not a.get("corpo"):return {"erro":"content_required","mensagem":"Informe o conteúdo."}
  draft=WhatsAppDraft(owner_id=user.id,link_id=cmd.link_id,kind="list" if kind=="list_create" else "patient_material" if kind=="patient_material_draft" else "draft",title_cipher=_encrypt(a.get("titulo"),user.id) if a.get("titulo") else None,body_cipher=_encrypt(a.get("corpo"),user.id),status="active",expires_at=utcnow()+timedelta(days=(_link(db,user,cmd).retention_days)))
  db.add(draft);db.flush();return {"mensagem":"Rascunho salvo.","draft":{"id":draft.id,"kind":draft.kind}}
 if kind=="email_send":
  args=dict(a);args["confirmacao_usuario"]=True;return executar_tool_assistente("mail_enviar_mensagem",args,db,user)
 if kind=="message_send":
  if settings.whatsapp_provider!="meta" or not settings.whatsapp_meta_configured:return {"erro":"provider_unavailable"}
  phone="".join(c for c in str(a.get("recipient_phone") or "") if c.isdigit());template=str(a.get("template_name") or "");allowed={x.strip() for x in settings.whatsapp_approved_template_names.split(",") if x.strip()}
  if template not in allowed:return {"erro":"approved_template_required"}
  if not _recipient_opted_in(db,user,phone,a.get("recipient_opt_in_id")):return {"erro":"recipient_opt_in_required"}
  cost=require_positive_tariff(settings.whatsapp_meta_message_cost_microunits,"Meta");enforce_cost_headroom(db,user.id,cost);l=_link(db,user,cmd)
  delivery=deliver_once(db,adapter=get_adapter(),idempotency_key=f"command-message:{cmd.id}",owner_id=user.id,link_id=l.id,phone=phone,text="",mode="template",template_name=template,template_language=a.get("template_language","pt_BR"),template_parameters=a.get("template_parameters",[])[:10],retention_days=l.retention_days,estimated_cost_microunits=cost)
  if delivery.status!="sent":return {"erro":"delivery_uncertain"}
  out=db.query(WhatsAppOutboundOutbox).filter(WhatsAppOutboundOutbox.id==delivery.outbox_id).first();mid=delivery.result.message_id if delivery.result else out.provider_message_id
  db.add(WhatsAppMessage(link_id=l.id,owner_id=user.id,provider_message_id=mid,direction="outbound",message_type="template",payload_cipher=_encrypt({"template":template,"recipient_phone_hash":phone_hash(phone)},user.id),pii_kinds=["telefone"],status="accepted",authorization_level=3,meta_billable=True,estimated_cost_microunits=cost,expires_at=utcnow()+timedelta(days=l.retention_days)));out.estimated_cost_microunits=0;return {"mensagem":"Template enviado.","provider_message_id":mid}
 if kind=="document_share":
  from app.models.assinatura import DocumentoEmitido
  from app.models.compartilhamento import DocumentShareLink
  doc_type=a.get("document_type");reference_id=a.get("document_id");hours=min(max(int(a.get("expires_hours") or 24),1),168)
  if doc_type not in {"generated_document","prescription_document"} or not reference_id:return {"erro":"document_reference_required","mensagem":"Informe tipo e ID do documento emitido."}
  emitted=db.query(DocumentoEmitido).filter(DocumentoEmitido.tipo==doc_type,DocumentoEmitido.referencia_id==int(reference_id),DocumentoEmitido.criado_por==user.id).first()
  if not emitted:return {"erro":"document_not_owned_or_not_issued","mensagem":"Documento emitido não encontrado para este assinante."}
  share=DocumentShareLink(tipo=doc_type,referencia_id=int(reference_id),criado_por=user.id,expires_at=utcnow()+timedelta(hours=hours));db.add(share);db.flush();return {"mensagem":"Link seguro criado após confirmação.","share_url":f"{settings.public_url}/documentos/{share.token}","expires_at":share.expires_at}
 if kind=="heart_team_start":
  if not settings.heart_team_enabled:return {"erro":"feature_disabled"}
  from app.services.heart_team import create_case_draft
  case_payload={"case_text":payload.get("text"),"question":a.get("question"),"selected_agents":a.get("selected_agents")}
  media_row=media_payload=media_data=None
  if a.get("media_message_id"):
   media_row,media_payload,media_data=_media_for_command(db,user,a["media_message_id"]);extracted=media_payload.get("sanitized_extract") or _extract_document(media_data,media_payload.get("mime_type"));case_payload["case_text"]=(payload.get("text") or "")+("\n\nConteúdo objetivo do anexo:\n"+extracted if extracted else "")
  case=create_case_draft(db,owner_id=user.id,created_by_id=user.id,payload=case_payload,origin="whatsapp")
  if media_data is not None:
   from app.models.heart_team import HeartTeamAttachment
   key=guardar(media_data,user.id,raiz=Path(settings.heart_team_files_dir));db.add(HeartTeamAttachment(case_id=case.id,owner_id=user.id,kind="upload",storage_key=key,media_type=media_payload.get("mime_type") or "application/octet-stream",size_bytes=len(media_data),sha256=hashlib.sha256(media_data).hexdigest(),objective_extract={"type":"whatsapp_sanitized_reviewed","text":extracted[:24000]}))
  job=WhatsAppHeartTeamJob(command_id=cmd.id,case_id=case.id,owner_id=user.id,link_id=cmd.link_id,status="queued",next_attempt_at=utcnow());db.add(job);return {"mensagem":"Análise enfileirada.","case_id":case.id,"full_result_url":f"{settings.public_url}/heart-team/{case.id}"}
 return {"erro":"unsupported"}
def create_command(db,user,link,*,text,idempotency_key,explicit_kind,arguments,pii_reviewed=False,message_id=None):
 feature_guard(); existing=db.query(WhatsAppCommand).filter(WhatsAppCommand.owner_id==user.id,WhatsAppCommand.idempotency_key==idempotency_key).first()
 if existing:return existing,decrypt_payload(existing.result_cipher,user.id) or {},None,None
 enforce_limits(db,user.id);p=parse_intent(text,explicit_kind=explicit_kind,explicit_arguments=arguments,now=utcnow(),timezone_name=settings.whatsapp_default_timezone);kind="blocked_critical" if payload_requires_level4(p.kind,text,p.arguments) else p.kind
 if kind not in LEVELS:raise HTTPException(422,"Comando inválido")
 level=LEVELS[kind];pii=detect_pii(text);status="blocked_security" if level==4 else "blocked_pii" if pii and not pii_reviewed else "needs_clarification" if p.clarification else "awaiting_confirmation" if level==3 else "pending";payload={"text":text,"arguments":p.arguments,"pii":pii};cmd=WhatsAppCommand(link_id=link.id,owner_id=user.id,message_id=message_id,kind=kind,idempotency_key=idempotency_key,level=level,status=status,payload_cipher=_encrypt(payload,user.id),requires_in_app=level==4,expires_at=utcnow()+timedelta(days=link.retention_days));db.add(cmd);db.flush();confirm=undo=None
 _audit(db,user.id,"whatsapp_command_created","whatsapp_command",cmd.id,detail={"kind":kind,"level":level,"status":status})
 if status=="awaiting_confirmation":confirm=random_token();cmd.confirmation_token_hash=token_hash(confirm,"confirm");cmd.confirmation_expires_at=utcnow()+timedelta(seconds=settings.whatsapp_confirmation_ttl_seconds)
 if level==2 and status=="pending":undo=random_token();cmd.undo_token_hash=token_hash(undo,"undo");cmd.undo_expires_at=utcnow()+timedelta(seconds=settings.whatsapp_confirmation_ttl_seconds)
 if status=="pending":result=_execute(db,user,cmd,payload);cmd.status="failed" if "erro" in result else "completed"
 elif status=="awaiting_confirmation":result={"mensagem":"Confirmação explícita necessária."}
 else:result={"erro":status,"mensagem":p.clarification or "Bloqueado."}
 cmd.result_cipher=_encrypt(result,user.id);db.add(WhatsAppUsageMetric(owner_id=user.id,link_id=link.id,idempotency_key=idempotency_key,operation=kind,provider=settings.whatsapp_provider,success="erro" not in result,blocked_reason=result.get("erro")));return cmd,result,confirm,undo
def confirm_command(db,user,cmd,*,token,pin):
 feature_guard()
 if cmd.owner_id!=user.id or cmd.status!="awaiting_confirmation":raise HTTPException(409,"Estado inválido")
 if cmd.confirmation_expires_at<=utcnow() or token_hash(token,"confirm")!=cmd.confirmation_token_hash:raise HTTPException(403,"Confirmação inválida")
 l=_link(db,user,cmd)
 if not l or not l.pin_hash or not pin or not verify_password(pin,l.pin_hash):raise HTTPException(403,"PIN inválido")
 payload=decrypt_payload(cmd.payload_cipher,user.id)
 metric=db.query(WhatsAppUsageMetric).filter(WhatsAppUsageMetric.owner_id==user.id,WhatsAppUsageMetric.idempotency_key==cmd.idempotency_key).first()
 if payload_requires_level4(cmd.kind,payload.get("text",""),payload.get("arguments")):
  cmd.level=4;cmd.status="blocked_security"
  if metric:metric.success=False;metric.blocked_reason="blocked_level_4"
  _audit(db,user.id,"whatsapp_command_blocked_level4","whatsapp_command",cmd.id,detail={"kind":cmd.kind})
  return {"erro":"blocked_level_4"}
 result=_execute(db,user,cmd,payload);cmd.status="failed" if "erro" in result else "completed";cmd.result_cipher=_encrypt(result,user.id);cmd.confirmation_token_hash=None;cmd.executed_at=utcnow()
 if metric:metric.success="erro" not in result;metric.blocked_reason=result.get("erro")
 _audit(db,user.id,"whatsapp_command_confirmed","whatsapp_command",cmd.id,detail={"kind":cmd.kind,"success":"erro" not in result})
 return result
def undo_command(db,user,cmd,*,token):
 if not cmd or cmd.owner_id!=user.id or cmd.level!=2 or cmd.status!="completed" or token_hash(token,"undo")!=cmd.undo_token_hash:raise HTTPException(409,"Não pode desfazer")
 result=decrypt_payload(cmd.result_cipher,user.id) or {};appointment=result.get("compromisso") if isinstance(result,dict) else None;appointment_id=(appointment or {}).get("id") if isinstance(appointment,dict) else None
 if cmd.kind in {"reminder_create","task_create","appointment_create"}:
  if not appointment_id:raise HTTPException(409,"A ação não possui compensação segura")
  compensated=executar_tool_assistente("agenda_cancelar_compromisso",{"appointment_id":appointment_id,"motivo":"Desfeito pelo assinante via CorVIA"},db,user)
  if "erro" in compensated:raise HTTPException(409,"Não foi possível desfazer com segurança")
 if cmd.kind=="routine_create":
  routines=result.get("rotina") if isinstance(result,dict) else None;routine_ids=[item.get("id") for item in jsonable_encoder(routines or []) if isinstance(item,dict) and item.get("id")]
  if not routine_ids:raise HTTPException(409,"Rotina não disponível para desfazer")
  from app.api.agenda_integrada import disable_work_routine
  for routine_id in routine_ids:disable_work_routine(int(routine_id),professional_id=None,db=db,user=user)
 if cmd.kind=="appointment_update":
  previous=result.get("_undo") if isinstance(result,dict) else None
  if not previous:raise HTTPException(409,"Horário anterior não disponível para desfazer")
  compensated=executar_tool_assistente("agenda_reagendar_compromisso",{"appointment_id":previous["appointment_id"],"novo_inicio":previous["inicio"],"duracao_minutos":previous.get("duracao_minutos")},db,user)
  if "erro" in compensated:raise HTTPException(409,"Não foi possível restaurar o compromisso")
 if cmd.kind in {"draft_save","list_create","patient_material_draft"}:
  draft_id=((result.get("draft") or {}).get("id") if isinstance(result,dict) else None);draft=db.query(WhatsAppDraft).filter(WhatsAppDraft.id==draft_id,WhatsAppDraft.owner_id==user.id,WhatsAppDraft.status=="active").first()
  if not draft:raise HTTPException(409,"Rascunho não disponível para desfazer")
  draft.status="deleted"
 cmd.status="undone";cmd.undo_token_hash=None;_audit(db,user.id,"whatsapp_command_undone","whatsapp_command",cmd.id);return {"ok":True,"status":"undone"}
def purge_expired_data(db,owner_id=None):
 now=utcnow();mq=db.query(WhatsAppMessage).filter(WhatsAppMessage.expires_at<=now);oq=db.query(WhatsAppOutboundOutbox).filter(WhatsAppOutboundOutbox.expires_at<=now);cq=db.query(WhatsAppCommand.id).filter(WhatsAppCommand.expires_at<=now)
 if owner_id is not None:mq=mq.filter(WhatsAppMessage.owner_id==owner_id);oq=oq.filter(WhatsAppOutboundOutbox.owner_id==owner_id);cq=cq.filter(WhatsAppCommand.owner_id==owner_id)
 media_rows=mq.all()
 for row in media_rows:
  try:
   key=(decrypt_payload(row.payload_cipher,row.owner_id) or {}).get("media_storage_key")
   if key:apagar(key,raiz=Path(settings.whatsapp_media_dir))
  except Exception:pass
 ids=[x[0] for x in cq.all()];deleted=mq.delete(synchronize_session=False)+oq.delete(synchronize_session=False)
 if ids:deleted+=db.query(WhatsAppHeartTeamJob).filter(WhatsAppHeartTeamJob.command_id.in_(ids)).delete(synchronize_session=False)
 drafts=db.query(WhatsAppDraft).filter(WhatsAppDraft.expires_at<=now)
 if owner_id is not None:drafts=drafts.filter(WhatsAppDraft.owner_id==owner_id)
 cache=db.query(WhatsAppSummaryCache).filter(WhatsAppSummaryCache.expires_at<=now)
 if owner_id is not None:cache=cache.filter(WhatsAppSummaryCache.owner_id==owner_id)
 deleted+=drafts.delete(synchronize_session=False)+cache.delete(synchronize_session=False);commands=db.query(WhatsAppCommand).filter(WhatsAppCommand.id.in_(ids));return deleted+(commands.delete(synchronize_session=False) if ids else 0)
