from dataclasses import dataclass
from datetime import timedelta
from app.models.whatsapp import WhatsAppOutboundOutbox
from app.services.cofre import cifrar_campo
from app.services.whatsapp_security import canonical_json,utcnow
from app.services.whatsapp_adapter import WhatsAppProviderError
@dataclass(frozen=True)
class OutboxDelivery: status:str; result:object|None; outbox_id:int
def deliver_once(db,*,adapter,idempotency_key,owner_id,link_id,phone,text,mode="text",template_name="",template_language="pt_BR",template_parameters=None,button_id="",button_title="Desfazer",job_id=None,retention_days=30,estimated_cost_microunits=0):
    row=db.query(WhatsAppOutboundOutbox).filter(WhatsAppOutboundOutbox.idempotency_key==idempotency_key).first()
    if row: return OutboxDelivery(row.status,None,row.id)
    row=WhatsAppOutboundOutbox(idempotency_key=idempotency_key,owner_id=owner_id,link_id=link_id,job_id=job_id,mode=mode,payload_cipher=cifrar_campo(canonical_json({"phone":phone,"text":text,"template":template_name,"parameters":template_parameters or [],"button_id":button_id}),owner_id),status="sending",attempts=1,estimated_cost_microunits=max(0,estimated_cost_microunits),expires_at=utcnow()+timedelta(days=retention_days))
    db.add(row); db.commit()
    try:
        if mode=="template": sent=adapter.send_template(phone,template_name,template_language,template_parameters or [],idempotency_key=idempotency_key)
        elif mode=="interactive": sent=adapter.send_interactive(phone,text,button_id,button_title,idempotency_key=idempotency_key)
        else: sent=adapter.send_text(phone,text,idempotency_key=idempotency_key)
    except WhatsAppProviderError as exc:
        row.status="uncertain"; row.last_error_code=type(exc).__name__; db.commit(); return OutboxDelivery("uncertain",None,row.id)
    row.status="sent"; row.provider_message_id=sent.message_id; row.sent_at=utcnow(); db.commit(); return OutboxDelivery("sent",sent,row.id)
