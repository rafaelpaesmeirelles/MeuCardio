"""Ponto único de verificação de posse de paciente clínico.

Achado de auditoria (issue #52, gate final da estabilização de 09-10/08/2026):
`app/api/timeline.py`, `prescriptions.py` e `appointments.py` reimplementavam
cada um a própria checagem de posse, e três delas continham
`user.role != "admin"` — deixando QUALQUER administrador ler ou operar dados
clínicos de paciente de outro médico, mesmo com `app/api/round.py` (a rota de
posse direta do mesmo paciente) negando corretamente o mesmo par
paciente/intruso. Dados clínicos de paciente (evolução, prescrição,
consulta) são propriedade exclusiva do médico que os criou — diferente do
modelo de `ServiceOrder` (telediagnóstico), que é um mercado de dois lados
por desenho (o solicitante pede, o admin/especialista atende qualquer
pedido da fila) e continua fora deste ponto único de propósito.

Regra, sem exceção: só `patient.created_by == user.id`. Nenhum papel dá
acesso amplo a paciente alheio — nem `admin`. Se uma regra de negócio real
algum dia precisar de acesso administrativo a paciente de outro médico
(auditoria, suporte), ela precisa ser uma exceção EXPLÍCITA e AUDITADA aqui,
nunca reintroduzida por engano num endpoint disperso.
"""
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.patient_profile import PatientProfile
from app.models.round import Patient


def patient_for_user(
    patient_id: int,
    db: Session,
    user,
    *,
    allow_archived: bool = True,
) -> Patient:
    """Devolve o paciente só se pertencer ao usuário autenticado; 404
    (nunca 403) nos dois casos — paciente inexistente e paciente de outro
    médico devolvem exatamente a mesma resposta, para não confirmar a
    existência de um `patient_id` alheio por enumeração."""
    patient = db.get(Patient, patient_id)
    if not patient or patient.created_by != user.id:
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")
    if not allow_archived and patient.archived_at is not None:
        raise HTTPException(status_code=410, detail="Paciente removido do round.")
    return patient


def patient_profile_for_user(profile_id: int, db: Session, user) -> PatientProfile:
    """Mesma regra e mesma forma de resposta de `patient_for_user`, agora
    para o cadastro de paciente reutilizável entre documentos
    (`PatientProfile`, 12/08/2026) — só `owner_id == user.id`, 404 (nunca
    403) tanto para id inexistente quanto para paciente de outro médico.
    É este ponto único que garante, no backend, que a busca/seleção de
    paciente na geração de documento nunca alcança cadastro alheio — o
    filtro do frontend nunca é a proteção real."""
    perfil = db.get(PatientProfile, profile_id)
    if not perfil or perfil.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")
    return perfil
