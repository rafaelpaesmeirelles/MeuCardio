import re,unicodedata
from dataclasses import dataclass
from datetime import datetime,timedelta
from typing import Any
from zoneinfo import ZoneInfo
EMAIL=re.compile(r"[\w.+-]+@[\w.-]+",re.I); ID=re.compile(r"(?:#|\bid\s*)(\d+)",re.I); PHONE=re.compile(r"(?<!\d)(\+?\d[\d ()-]{7,20}\d)(?!\d)")
@dataclass(frozen=True)
class ParsedIntent: kind:str; arguments:dict[str,Any]; clarification:str|None=None
def _field(t,l):
 m=re.search(rf"(?:^|\n)\s*{l}\s*:\s*(.+?)(?=\n\s*\w[\w -]*\s*:|$)",t,re.I|re.S); return m.group(1).strip() if m else None
def _dt(t,now,tz):
 n=t.casefold(); off=1 if "amanh" in n else 0 if "hoje" in n else None; m=re.search(r"(\d{1,2})(?::|h)(\d{2})?",t)
 if off is None or not m:return None
 local=now.astimezone(ZoneInfo(tz))+timedelta(days=off); return local.replace(hour=int(m.group(1)),minute=int(m.group(2) or 0),second=0,microsecond=0).isoformat()
def parse_intent(text,*,explicit_kind=None,explicit_arguments=None,now,timezone_name):
 raw=(text or "").strip(); n=raw.casefold(); a=dict(explicit_arguments or {})
 if explicit_kind:k=explicit_kind
 elif "heart team" in n:k="heart_team_start"
 elif "enviar e-mail" in n:k="email_send"
 elif any(x in n for x in ("enviar mensagem","mande uma mensagem","mandar mensagem")):k="message_send"
 elif "compartilhar documento" in n or "gerar link do documento" in n:k="document_share"
 elif "reagendar" in n or "remarcar" in n:k="appointment_update"
 elif "cancelar compromisso" in n:k="third_party_appointment_cancel"
 elif any(x in n for x in ("criar compromisso","agendar compromisso","marcar compromisso")):k="appointment_create"
 elif "criar rotina" in n or "rotina semanal" in n:k="routine_create"
 elif "resumo diário" in n or "resumo do dia" in n:k="daily_summary"
 elif any(x in n for x in ("pendências","pendencias","retornos pendentes","exames pendentes","assinaturas pendentes")):k="pending_items"
 elif "material ao paciente" in n or "material para o paciente" in n:k="patient_material_draft"
 elif any(x in n for x in ("lembrete","lembrar","lembre-me","lembre me")):k="reminder_create"
 elif "criar tarefa" in n:k="task_create"
 elif "tarefas" in n:k="task_list"
 elif "agenda" in n:k="agenda_list"
 elif "resum" in n and ("pdf" in n or "document" in n):k="document_summary"
 elif any(x in n for x in ("pesquisar","artigo","evidência","diretriz")):k="scientific_search"
 elif "criar lista" in n:k="list_create"
 elif "preparar" in n or "rascunho" in n:k="draft_save"
 else:k="status_read"
 ref=ID.search(raw); ref=int(ref.group(1)) if ref else None
 if k in {"reminder_create","task_create","appointment_create"}:
  a.setdefault("inicio",_dt(raw,now,timezone_name))
  if not a.get("inicio"):return ParsedIntent(k,a,"Informe data e hora.")
 if k=="appointment_update":
  a.setdefault("appointment_id",ref);a.setdefault("novo_inicio",_dt(raw,now,timezone_name))
  if not a.get("appointment_id") or not a.get("novo_inicio"):return ParsedIntent(k,a,"Informe ID do compromisso e novo horário.")
 if k=="third_party_appointment_cancel":
  a.setdefault("appointment_id",ref);a.setdefault("motivo",_field(raw,"motivo"))
  if not a.get("appointment_id"):return ParsedIntent(k,a,"Informe o ID do compromisso.")
 if k=="routine_create":
  dias=_field(raw,"dias");normalize=lambda v:"".join(c for c in unicodedata.normalize("NFKD",v.casefold()) if not unicodedata.combining(c))
  a.setdefault("dias_semana",[normalize(x.strip()) for x in re.split(r"[,;|]",dias) if x.strip()] if dias else None);a.setdefault("hora_inicio",_field(raw,"início") or _field(raw,"inicio"));a.setdefault("hora_fim",_field(raw,"fim"));a.setdefault("titulo",_field(raw,"título") or _field(raw,"titulo"));a.setdefault("local_nome",_field(raw,"local"));a.setdefault("endereco",_field(raw,"endereço") or _field(raw,"endereco"))
  if not all(a.get(x) for x in ("dias_semana","hora_inicio","hora_fim","titulo")):return ParsedIntent(k,a,"Informe Dias, Início, Fim e Título. Informe Local quando a rotina não tiver um local cadastrado.")
 if k=="email_send":
  em=EMAIL.findall(raw); a.setdefault("para",em[0] if em else None); a.setdefault("assunto",_field(raw,"assunto")); a.setdefault("corpo",_field(raw,"corpo") or _field(raw,"mensagem"))
  if not all(a.get(x) for x in ("para","assunto","corpo")):return ParsedIntent(k,a,"Informe destinatário, assunto e corpo.")
 if k=="message_send":
  p=PHONE.search(raw); a.setdefault("recipient_phone","".join(c for c in p.group(1) if c.isdigit()) if p else None); a.setdefault("template_name",_field(raw,"template")); a.setdefault("template_language",_field(raw,"idioma") or "pt_BR")
  oi=re.search(r"opt[- ]?in\s+id\s*:\s*(\d+)",raw,re.I); a.setdefault("recipient_opt_in_id",int(oi.group(1)) if oi else None); ps=_field(raw,"parâmetros") or _field(raw,"parametros"); a.setdefault("template_parameters",[x.strip() for x in re.split(r"[|;\n]",ps) if x.strip()] if ps else [])
  if not all(a.get(x) for x in ("recipient_phone","recipient_opt_in_id","template_name")):return ParsedIntent(k,a,"Informe Telefone, Template e Opt-in ID registrados.")
 if k=="document_share":
  a.setdefault("document_id",ref);a.setdefault("document_type","prescription_document" if "receita" in n else "generated_document" if "documento" in n else None)
  hours=re.search(r"(?:validade|expira[^\d]*)\s*(\d{1,3})\s*h",raw,re.I);a.setdefault("expires_hours",int(hours.group(1)) if hours else 24)
  if not a.get("document_id") or not a.get("document_type"):return ParsedIntent(k,a,"Informe o tipo (documento gerado ou receita) e o ID emitido.")
 if k=="scientific_search":a.setdefault("q",raw)
 if k=="document_summary" and not any(a.get(x) for x in ("text","document_id","media_message_id")):
  if ref:a["document_id"]=ref
  else:return ParsedIntent(k,a,"Informe documento.")
 if k in {"draft_save","list_create","patient_material_draft"}:
  a.setdefault("titulo",_field(raw,"titulo") or _field(raw,"título")); a.setdefault("corpo",_field(raw,"corpo") or _field(raw,"mensagem") or _field(raw,"itens"))
  if not a.get("corpo"):return ParsedIntent(k,a,"Informe conteúdo.")
 return ParsedIntent(k,{x:y for x,y in a.items() if y is not None})
