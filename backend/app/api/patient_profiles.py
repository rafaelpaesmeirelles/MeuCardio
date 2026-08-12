"""Cadastro de paciente reutilizável entre documentos (12/08/2026, pedido
do Rafael) — ver `app.models.patient_profile.PatientProfile` para a
justificativa de ser uma entidade separada do `Patient` do round.

Todo endpoint aqui é escopado por `owner_id == user.id`: um médico só
enxerga, busca, edita ou apaga o PRÓPRIO cadastro de paciente — nunca o de
outro (mesma disciplina de posse do resto do produto, centralizada em
`app.services.clinical_ownership.patient_profile_for_user`).
"""
from __future__ import annotations

import json
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user
from app.models.patient_profile import PatientProfile
from app.services import cofre
from app.services.clinical_ownership import patient_profile_for_user
from app.services.patient_profile_service import snapshot_de
from app.services.professional_profile import normalize_search_text

router = APIRouter(prefix="/api/pacientes", tags=["pacientes"])


class EnderecoIn(BaseModel):
    logradouro: str | None = None
    numero: str | None = None
    complemento: str | None = None
    bairro: str | None = None
    cidade: str | None = None
    uf: str | None = None
    cep: str | None = None

    def esta_vazio(self) -> bool:
        return not any((
            self.logradouro, self.numero, self.complemento,
            self.bairro, self.cidade, self.uf, self.cep,
        ))


class PatientProfileIn(BaseModel):
    full_name: str
    cpf: str | None = None
    birth_date: date | None = None
    sex: str | None = None
    phone: str | None = None
    email: str | None = None
    endereco: EnderecoIn | None = None


def _dump(perfil: PatientProfile) -> dict:
    snap = snapshot_de(perfil)
    return {
        "id": perfil.id,
        "full_name": snap["full_name"],
        "cpf": snap["cpf"],
        "birth_date": snap["birth_date"],
        "sex": snap["sex"],
        "phone": snap["phone"],
        "email": snap["email"],
        "endereco": snap["endereco"],
        "created_at": perfil.created_at,
        "updated_at": perfil.updated_at,
    }


def _gravar_campos(perfil: PatientProfile, dados: PatientProfileIn) -> None:
    """`perfil.id` precisa existir antes de cifrar (é o AAD do cofre) —
    chamar sempre depois de `db.add(perfil); db.flush()`."""
    perfil.full_name_cifrado = cofre.cifrar_campo(dados.full_name.strip(), perfil.id)
    perfil.cpf_cifrado = cofre.cifrar_campo(dados.cpf.strip(), perfil.id) if dados.cpf and dados.cpf.strip() else None
    perfil.birth_date = dados.birth_date
    perfil.sex = (dados.sex or "").strip()[:1] or None
    perfil.phone_cifrado = cofre.cifrar_campo(dados.phone.strip(), perfil.id) if dados.phone and dados.phone.strip() else None
    perfil.email_cifrado = cofre.cifrar_campo(dados.email.strip(), perfil.id) if dados.email and dados.email.strip() else None
    if dados.endereco and not dados.endereco.esta_vazio():
        perfil.endereco_cifrado = cofre.cifrar_campo(
            json.dumps(dados.endereco.model_dump(), ensure_ascii=False), perfil.id,
        )
    else:
        perfil.endereco_cifrado = None


@router.get("")
def listar_pacientes(
    busca: str | None = Query(None, max_length=120),
    db: Session = Depends(get_db), user=Depends(current_user),
):
    """Lista só o cadastro do próprio médico (`owner_id == user.id`) — o
    mesmo filtro de posse que `patient_profile_for_user` aplica em cada
    endpoint individual, aqui aplicado à listagem inteira. Decifra em
    memória e filtra por nome em Python (mesmo padrão já usado em
    `GET /document-templates/gerados?nome=`), porque o nome está cifrado
    e não dá para filtrar por `LIKE` no banco."""
    rows = (
        db.query(PatientProfile)
        .filter(PatientProfile.owner_id == user.id)
        .order_by(PatientProfile.created_at.desc())
        .all()
    )
    alvo = normalize_search_text(busca)
    resultado = []
    for perfil in rows:
        dump = _dump(perfil)
        if alvo and alvo not in normalize_search_text(dump["full_name"]):
            continue
        resultado.append(dump)
    return resultado


@router.post("", status_code=201)
def criar_paciente(dados: PatientProfileIn, db: Session = Depends(get_db), user=Depends(current_user)):
    if not dados.full_name.strip():
        raise HTTPException(status_code=422, detail="Informe o nome do paciente.")
    perfil = PatientProfile(owner_id=user.id, full_name_cifrado=b"")
    db.add(perfil)
    db.flush()
    _gravar_campos(perfil, dados)
    db.commit()
    db.refresh(perfil)
    return _dump(perfil)


@router.get("/{pid}")
def obter_paciente(pid: int, db: Session = Depends(get_db), user=Depends(current_user)):
    perfil = patient_profile_for_user(pid, db, user)
    return _dump(perfil)


@router.put("/{pid}")
def editar_paciente(pid: int, dados: PatientProfileIn, db: Session = Depends(get_db), user=Depends(current_user)):
    if not dados.full_name.strip():
        raise HTTPException(status_code=422, detail="Informe o nome do paciente.")
    perfil = patient_profile_for_user(pid, db, user)
    _gravar_campos(perfil, dados)
    db.commit()
    db.refresh(perfil)
    return _dump(perfil)


@router.delete("/{pid}", status_code=204)
def apagar_paciente(pid: int, db: Session = Depends(get_db), user=Depends(current_user)):
    perfil = patient_profile_for_user(pid, db, user)
    # `generated_documents.patient_profile_id` é `ON DELETE SET NULL` — o
    # documento já emitido continua existindo, com o snapshot cifrado
    # intacto; só perde o atalho de navegação até este cadastro.
    db.delete(perfil)
    db.commit()
