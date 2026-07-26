from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user
from app.models.clinical_docs import Appointment, GeneratedDocument, Prescription
from app.models.round import Patient, PatientAISuggestion, PatientNote

router = APIRouter(prefix="/api/timeline", tags=["timeline"])


@router.get("/patient/{patient_id}")
def timeline_paciente(patient_id: int, db: Session = Depends(get_db), user=Depends(current_user)):
    p = db.get(Patient, patient_id)
    if not p or (p.created_by != user.id and user.role != "admin"):
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")

    eventos = []

    for n in db.query(PatientNote).filter(PatientNote.patient_id == patient_id):
        eventos.append({
            "tipo": "evolucao", "data": n.created_at,
            "titulo": "Evolução registrada",
            "resumo": n.body[:160],
        })

    for s in db.query(PatientAISuggestion).filter(PatientAISuggestion.patient_id == patient_id):
        eventos.append({
            "tipo": "auxilio_ia", "data": s.created_at,
            "titulo": "Auxílio de IA gerado",
            "resumo": s.differential_diagnosis[:160],
        })

    for pr in db.query(Prescription).filter(Prescription.patient_id == patient_id):
        nomes = ", ".join(i.get("drug_name", "") for i in pr.items[:3])
        eventos.append({
            "tipo": "prescricao", "data": pr.created_at,
            "titulo": "Prescrição emitida",
            "resumo": nomes or "—",
        })

    for gd in db.query(GeneratedDocument).filter(GeneratedDocument.patient_id == patient_id):
        eventos.append({
            "tipo": "documento", "data": gd.created_at,
            "titulo": f"{gd.doc_type.capitalize()} gerado — {gd.title}",
            "resumo": gd.rendered_body[:160],
        })

    for ap in db.query(Appointment).filter(Appointment.patient_id == patient_id):
        eventos.append({
            "tipo": "consulta", "data": ap.scheduled_at,
            "titulo": f"Consulta ({ap.appointment_type}) — {ap.status}",
            "resumo": ap.notes[:160] if ap.notes else "—",
        })

    eventos.sort(key=lambda e: e["data"], reverse=True)
    return eventos
