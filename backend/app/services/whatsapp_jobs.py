import json
from datetime import timedelta
from fastapi import HTTPException
from app.core.config import settings
from app.core.db import SessionLocal
from app.models.audit import AuditLog
from app.models.whatsapp import *
from app.services.cofre import cifrar_campo,decifrar_campo
from app.services.whatsapp_adapter import get_adapter
from app.services.whatsapp_assistant import enforce_cost_headroom,require_positive_tariff
from app.services.whatsapp_outbox import deliver_once
from app.services.whatsapp_security import canonical_json,phone_hash,utcnow
def process_heart_team_job(job_id,*,adapter=None):
 if not settings.whatsapp_assistant_enabled or not settings.heart_team_enabled:return {"status":"feature_disabled"}
 db=SessionLocal()
 try:
  job=db.query(WhatsAppHeartTeamJob).filter(WhatsAppHeartTeamJob.id==job_id).with_for_update().first()
  if not job:return {"status":"not_found"}
  if job.status not in {"queued","retry"}:return {"status":job.status}
  job.status="running";job.attempts+=1;db.commit()
  from app.models.heart_team import HeartTeamCase
  from app.services.heart_team import analyze_case_by_id
  case=db.query(HeartTeamCase).filter(HeartTeamCase.id==job.case_id,HeartTeamCase.owner_id==job.owner_id).first()
  if case.status not in {"awaiting_review","completed"}:case=analyze_case_by_id(db,case_id=case.id,owner_id=job.owner_id,actor_id=job.owner_id,confirm_deidentified=True,confirm_medical_review=True,origin="whatsapp_worker")
  link=db.query(WhatsAppLink).filter(WhatsAppLink.id==job.link_id,WhatsAppLink.status=="active").first()
  if not link:
   job.status="cancelled";job.last_error_code="link_revoked";job.completed_at=utcnow();db.add(AuditLog(user_id=job.owner_id,action="whatsapp_heart_notification_cancelled",entity="whatsapp_heart_team_job",entity_id=str(job.id),detail={"reason":"link_revoked"}));db.commit();return {"status":"cancelled"}
  phone=json.loads(decifrar_campo(link.phone_cipher,link.user_id))["phone"];recent=db.query(WhatsAppMessage.id).filter(WhatsAppMessage.link_id==link.id,WhatsAppMessage.direction=="inbound",WhatsAppMessage.created_at>=utcnow()-timedelta(hours=24)).first();text=f"O parecer do Heart Team está pronto para revisão médica. {settings.public_url}/heart-team/{case.id}";cost=0
  if settings.whatsapp_provider=="meta":
   try:cost=require_positive_tariff(settings.whatsapp_meta_message_cost_microunits,"Meta");enforce_cost_headroom(db,job.owner_id,cost)
   except HTTPException:
    job.status="retry";job.last_error_code="cost_configuration_blocked";db.add(AuditLog(user_id=job.owner_id,action="whatsapp_heart_notification_blocked",entity="whatsapp_heart_team_job",entity_id=str(job.id),detail={"reason":"cost_configuration"}));db.commit();return {"status":"retry"}
  if settings.whatsapp_provider=="meta" and not recent:
   if not settings.whatsapp_heart_team_ready_template_name:job.status="retry";job.last_error_code="outside_window_no_template";db.commit();return {"status":"retry"}
   d=deliver_once(db,adapter=adapter or get_adapter(),idempotency_key=f"heart-ready:{job.id}",owner_id=job.owner_id,link_id=link.id,job_id=job.id,phone=phone,text=text,mode="template",template_name=settings.whatsapp_heart_team_ready_template_name,template_parameters=[f"{settings.public_url}/heart-team/{case.id}"],retention_days=link.retention_days,estimated_cost_microunits=cost)
  else:d=deliver_once(db,adapter=adapter or get_adapter(),idempotency_key=f"heart-ready:{job.id}",owner_id=job.owner_id,link_id=link.id,job_id=job.id,phone=phone,text=text,retention_days=link.retention_days,estimated_cost_microunits=cost)
  job.status="notified" if d.status=="sent" else "failed";job.completed_at=utcnow()
  if d.status=="sent":
   out=db.query(WhatsAppOutboundOutbox).filter(WhatsAppOutboundOutbox.id==d.outbox_id).first();provider_id=d.result.message_id if d.result else (out.provider_message_id if out else None);job.provider_message_id=provider_id
   if provider_id and not db.query(WhatsAppMessage).filter(WhatsAppMessage.provider_message_id==provider_id).first():db.add(WhatsAppMessage(link_id=link.id,owner_id=job.owner_id,provider_message_id=provider_id,direction="outbound",message_type="template" if not recent else "text",payload_cipher=cifrar_campo(canonical_json({"event":"heart_team_ready","case_id":case.id,"recipient_phone_hash":phone_hash(phone)}),job.owner_id),pii_kinds=[],status="accepted",authorization_level=1,meta_billable=settings.whatsapp_provider=="meta",estimated_cost_microunits=cost,expires_at=utcnow()+timedelta(days=link.retention_days)))
   if out:out.estimated_cost_microunits=0
  db.add(AuditLog(user_id=job.owner_id,action="whatsapp_heart_notification_finished",entity="whatsapp_heart_team_job",entity_id=str(job.id),detail={"status":job.status,"billable":settings.whatsapp_provider=="meta"}));db.commit();return {"status":job.status,"case_id":case.id}
 finally:db.close()
def process_pending_heart_team_jobs(limit=3):
 db=SessionLocal()
 try:
  cutoff=utcnow()-timedelta(seconds=max(60,settings.whatsapp_heart_team_job_lease_seconds));db.query(WhatsAppOutboundOutbox).filter(WhatsAppOutboundOutbox.status=="sending",WhatsAppOutboundOutbox.updated_at<=cutoff).update({"status":"uncertain"},synchronize_session=False);db.query(WhatsAppHeartTeamJob).filter(WhatsAppHeartTeamJob.status=="running",WhatsAppHeartTeamJob.updated_at<=cutoff).update({"status":"retry","next_attempt_at":utcnow()},synchronize_session=False);db.commit();ids=[x[0] for x in db.query(WhatsAppHeartTeamJob.id).filter(WhatsAppHeartTeamJob.status.in_({"queued","retry"}),WhatsAppHeartTeamJob.next_attempt_at<=utcnow()).limit(limit).all()]
 finally:db.close()
 results=[]
 for job_id in ids:
  try:results.append(process_heart_team_job(job_id))
  except Exception as exc:results.append({"status":"worker_error","job_id":job_id,"error":type(exc).__name__})
 return {"processed":results}
