"""Arquivos originais de exames do PatientProfile.

O binário nunca é público: fica cifrado no volume de exames e só é lido por
rota autenticada e escopada ao mesmo profissional/paciente/resultado.
"""
from __future__ import annotations

import re
from urllib.parse import quote

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user
from app.models.audit import AuditLog
from app.models.patient_exam_attachment import PatientExamAttachment
from app.models.prontuario import PatientExamResult
from app.services import cofre
from app.services.clinical_ownership import patient_profile_for_user

router = APIRouter(prefix="/api/pacientes", tags=["prontuario"])

ASSINATURAS = {
    b"\xff\xd8\xff": "image/jpeg",
    b"\x89PNG\r\n\x1a\n": "image/png",
    b"%PDF-": "application/pdf",
}
TAMANHO_MAXIMO = 20 * 1024 * 1024
MAX_ARQUIVOS_POR_RESULTADO = 5


def _tipo(conteudo: bytes) -> str | None:
    for assinatura, mime in ASSINATURAS.items():
        if conteudo.startswith(assinatura):
            return mime
    return None


def _resultado(pid: int, rid: int, db: Session, user) -> PatientExamResult:
    patient_profile_for_user(pid, db, user)
    row = db.get(PatientExamResult, rid)
    if not row or row.owner_id != user.id or row.patient_profile_id != pid:
        raise HTTPException(status_code=404, detail="Resultado de exame não encontrado.")
    return row


def _anexo(pid: int, rid: int, aid: int, db: Session, user) -> PatientExamAttachment:
    _resultado(pid, rid, db, user)
    row = db.get(PatientExamAttachment, aid)
    if not row or row.owner_id != user.id or row.patient_exam_result_id != rid:
        raise HTTPException(status_code=404, detail="Arquivo de exame não encontrado.")
    return row


def _dump(row: PatientExamAttachment) -> dict:
    return {
        "id": row.id,
        "patient_exam_result_id": row.patient_exam_result_id,
        "original_name": cofre.decifrar_campo(row.original_name_cifrado, row.id),
        "mime_type": row.mime_type,
        "size_bytes": row.size_bytes,
        "created_at": row.created_at,
    }


@router.get("/{pid}/resultados-arquivos")
def listar_arquivos(pid: int, db: Session = Depends(get_db), user=Depends(current_user)):
    patient_profile_for_user(pid, db, user)
    result_ids = [
        rid for (rid,) in db.query(PatientExamResult.id).filter(
            PatientExamResult.owner_id == user.id,
            PatientExamResult.patient_profile_id == pid,
        ).all()
    ]
    if not result_ids:
        return []
    rows = (
        db.query(PatientExamAttachment)
        .filter(
            PatientExamAttachment.owner_id == user.id,
            PatientExamAttachment.patient_exam_result_id.in_(result_ids),
        )
        .order_by(PatientExamAttachment.created_at.desc(), PatientExamAttachment.id.desc())
        .all()
    )
    db.add(AuditLog(
        user_id=user.id,
        action="list_patient_exam_attachments",
        entity="patient_profile",
        entity_id=str(pid),
        detail={"count": len(rows)},
    ))
    db.commit()
    return [_dump(row) for row in rows]


@router.post("/{pid}/resultados/{rid}/arquivos", status_code=201)
async def anexar_arquivo(
    pid: int,
    rid: int,
    arquivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    _resultado(pid, rid, db, user)
    quantidade = db.query(PatientExamAttachment.id).filter(
        PatientExamAttachment.owner_id == user.id,
        PatientExamAttachment.patient_exam_result_id == rid,
    ).count()
    if quantidade >= MAX_ARQUIVOS_POR_RESULTADO:
        raise HTTPException(status_code=409, detail="Este resultado já possui o limite de 5 arquivos.")

    conteudo = await arquivo.read(TAMANHO_MAXIMO + 1)
    if len(conteudo) > TAMANHO_MAXIMO:
        raise HTTPException(status_code=413, detail="O arquivo precisa ter no máximo 20 MB.")
    if not conteudo:
        raise HTTPException(status_code=422, detail="Arquivo vazio.")
    mime = _tipo(conteudo)
    if mime is None:
        raise HTTPException(status_code=422, detail="Envie o arquivo em JPEG, PNG ou PDF.")

    row = PatientExamAttachment(
        owner_id=user.id,
        patient_exam_result_id=rid,
        uploaded_by=user.id,
        storage_name="",
        original_name_cifrado=b"",
        mime_type=mime,
        size_bytes=len(conteudo),
    )
    db.add(row)
    db.flush()
    nome_original = (arquivo.filename or "exame")[:255]
    nome_storage: str | None = None
    try:
        nome_storage = cofre.guardar(conteudo, row.id)
        row.storage_name = nome_storage
        row.original_name_cifrado = cofre.cifrar_campo(nome_original, row.id)
        db.add(AuditLog(
            user_id=user.id,
            action="attach_patient_exam_file",
            entity="patient_exam_result",
            entity_id=str(rid),
            detail={
                "patient_profile_id": pid,
                "attachment_id": row.id,
                "mime_type": mime,
                "bytes": len(conteudo),
            },
        ))
        db.commit()
    except cofre.CofreIndisponivel as e:
        db.rollback()
        if nome_storage:
            cofre.apagar(nome_storage)
        raise HTTPException(status_code=503, detail=f"Armazenamento seguro indisponível: {e}")
    except Exception:
        db.rollback()
        if nome_storage:
            cofre.apagar(nome_storage)
        raise
    db.refresh(row)
    return _dump(row)


@router.get("/{pid}/resultados/{rid}/arquivos/{aid}")
def abrir_arquivo(
    pid: int,
    rid: int,
    aid: int,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    row = _anexo(pid, rid, aid, db, user)
    try:
        conteudo = cofre.ler(row.storage_name, row.id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado no armazenamento.")
    except cofre.CofreIndisponivel as e:
        raise HTTPException(status_code=503, detail=str(e))

    nome = cofre.decifrar_campo(row.original_name_cifrado, row.id)
    fallback = re.sub(r"[^A-Za-z0-9._-]", "_", nome)[:120] or "exame"
    db.add(AuditLog(
        user_id=user.id,
        action="read_patient_exam_file",
        entity="patient_exam_result",
        entity_id=str(rid),
        detail={"patient_profile_id": pid, "attachment_id": row.id},
    ))
    db.commit()
    return Response(
        content=conteudo,
        media_type=row.mime_type,
        headers={
            "Content-Disposition": f"inline; filename=\"{fallback}\"; filename*=UTF-8''{quote(nome)}",
            "Cache-Control": "no-store, private",
            "X-Content-Type-Options": "nosniff",
        },
    )
