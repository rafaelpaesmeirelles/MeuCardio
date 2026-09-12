"""Ensaio focal do contrato de criação; somente objetos sintéticos e banco falso."""
import json
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import patch
from fastapi import BackgroundTasks, HTTPException
from app.api import agenda_integrada as agenda
from app.services import whatsapp_assistant as wa
from app.services.ia import assistant_automation_tools as tools
from app.services.whatsapp_intents import parse_intent

class DB:
    def __init__(self): self.rows=[];self.commits=0
    def add(self,row): self.rows.append(row)
    def flush(self):
        for i,row in enumerate(self.rows,1):
            if row.id is None: row.id=i
    def commit(self): self.flush();self.commits+=1
    def rollback(self): raise AssertionError("Rollback inesperado no cenário válido")
    def refresh(self,row): pass
    def query(self,model): return NS(filter=lambda *a:NS(first=lambda:None))

user=NS(id=42,investidor=False)
start="2026-10-01T09:00:00-03:00"
checks=[]
with patch.object(agenda,"_owner_for",return_value=42), patch.object(agenda,"find_conflicts",return_value=[]), patch.object(agenda,"_commitment_conflicts",return_value=[]), patch.object(agenda,"queue_external_operation",return_value=None), patch.object(agenda,"_audit",return_value=None), patch.object(agenda,"_dump_appointment",side_effect=lambda db,item:{"id":item.id,"appointment_type":item.appointment_type,"patient_id":item.patient_id,"patient_name":item.patient_name_temp}), patch.object(tools,"_resolver_local",return_value=(None,None)), patch.object(wa,"_permission",return_value=True):
    for kind,expected_type in (("reminder_create","lembrete"),("task_create","tarefa"),("appointment_create","compromisso")):
        db=DB()
        cmd=NS(kind=kind,level=2,link_id=1,owner_id=42)
        result=wa._execute(db,user,cmd,{"arguments":{"inicio":start},"text":"Reunião de planejamento"})
        assert "erro" not in result,result
        assert result["compromisso"]["appointment_type"]==expected_type
        assert result["compromisso"]["patient_id"] is None and result["compromisso"]["patient_name"] is None
        checks.append({"cenario":kind,"resultado":"criado no contrato canônico, sem paciente fictício"})
    clinical_cmd=NS(kind="appointment_create",level=2,link_id=1,owner_id=42)
    db=DB()
    result=wa._execute(db,user,clinical_cmd,{"arguments":{"inicio":start,"tipo":"consulta"},"text":"Consulta"})
    assert result["erro"]=="patient_required" and not db.rows
    try:
        agenda.create_appointment(agenda.AppointmentIn(starts_at=start,appointment_type="consulta"),BackgroundTasks(),db=db,user=user)
    except HTTPException as exc: assert exc.status_code==422
    else: raise AssertionError("Consulta sem paciente aceita")
    checks.append({"cenario":"consulta sem paciente","resultado":"rejeitada no WhatsApp e na API canônica antes de escrever"})
    result=wa._execute(DB(),user,clinical_cmd,{"arguments":{"inicio":start,"tipo":"consulta","paciente_nome":"Pessoa demonstrativa"},"text":"Consulta"})
    assert "erro" not in result and result["compromisso"]["patient_name"]=="Pessoa demonstrativa"
    checks.append({"cenario":"consulta com paciente explicitamente informado","resultado":"contrato canônico mantém a identificação fornecida"})
    try:
        agenda.create_appointment(agenda.AppointmentIn(starts_at=start,appointment_type="consulta",patient_id=999),BackgroundTasks(),db=DB(),user=user)
    except HTTPException as exc: assert exc.status_code==404
    else: raise AssertionError("Paciente fora do escopo aceito")
    checks.append({"cenario":"paciente inexistente/fora do escopo","resultado":"checagem canônica de titularidade preservada"})

now=datetime(2026,9,12,tzinfo=timezone.utc)
for text,clarification in (("criar compromisso amanhã 09:00",False),("criar compromisso consulta amanhã 09:00",True),("criar compromisso consulta amanhã 09:00\nPaciente ID: 19",False),("criar compromisso para estudar consulta amanhã 09:00\nTipo: compromisso",False)):
    parsed=parse_intent(text,now=now,timezone_name="America/Sao_Paulo")
    assert bool(parsed.clarification)==clarification,parsed
checks.append({"cenario":"interpretação de compromisso pessoal versus consulta","resultado":"paciente solicitado somente no tipo clínico; Tipo: compromisso explícito respeitado"})
out=Path(__file__).resolve().parents[2]/"docs/correcoes-auditoria-20260912/provas-ciencia/whatsapp-criacao.json"
out.write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"aprovados":len(checks),"resultados":checks},ensure_ascii=False))
