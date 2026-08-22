"""Arquivos originais de exames do `PatientProfile` identificável.

Os bytes ficam cifrados no mesmo cofre AES-256-GCM já usado pelo
telediagnóstico. Não existe URL pública nem endpoint de exclusão: leitura é
autenticada, auditada e entregue com `Cache-Control: no-store`.
"""
from __future__ import annotations

from urllib.parse import quote

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user
from app.models.audit import AuditLog
from app.models.prontuario import PatientExamAttachment, PatientExamResult
from app.services import cofre
from app.services.clinical_ownership import patient_profile_for_user

router = APIRouter(prefix="/api/pacientes", tags=["prontuario"])

TAMANHO_MAXIMO = 20 * 1024 * 1024
_ASSINATURAS = (
    (b"%PDF-", "application/pdf", "exame.pdf"),
    (b"\xff\xd8\xff", "image/jpeg", "exame.jpg"),
    (b"\x89PNG\r\n\x1a\n", "image/png", "exame.png"),
)


def _tipo(conteudo: bytes) -> tuple[str, str] | None:
    for assinatura, mime, fallback in _ASSINATURAS:
        if conteudo.startswith(assinatura):
            return mime, fallback
    return None


def _resultado(pid: int, result_id: int, db: Session, user) -> PatientExamResult:
    patient_profile_for_user(pid, db, user)
    row = db.get(PatientExamResult, result_id)
    if not row or row.owner_id != user.id or row.patient_profile_id != pid:
        raise HTTPException(status_code=404, detail="Resultado de exame não encontrado.")
    return row


def _anexo(pid: int, result_id: int, attachment_id: int, db: Session, user) -> PatientExamAttachment:
    _resultado(pid, result_id, db, user)
    row = db.get(PatientExamAttachment, attachment_id)
    if not row or row.owner_id != user.id or row.exam_result_id != result_id:
        raise HTTPException(status_code=404, detail="Arquivo de exame não encontrado.")
    return row


def _dump(row: PatientExamAttachment) -> dict:
    return {
        "id": row.id,
        "exam_result_id": row.exam_result_id,
        "original_name": cofre.decifrar_campo(row.original_name_cifrado, row.id),
        "mime_type": row.mime_type,
        "size_bytes": row.size_bytes,
        "created_at": row.created_at,
    }


@router.get("/{pid}/arquivos-exames")
def listar_arquivos_exames(
    pid: int,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    patient_profile_for_user(pid, db, user)
    rows = (
        db.query(PatientExamAttachment)
        .join(PatientExamResult, PatientExamResult.id == PatientExamAttachment.exam_result_id)
        .filter(
            PatientExamAttachment.owner_id == user.id,
            PatientExamResult.owner_id == user.id,
            PatientExamResult.patient_profile_id == pid,
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


@router.post("/{pid}/resultados/{result_id}/arquivos", status_code=201)
async def anexar_arquivo_exame(
    pid: int,
    result_id: int,
    arquivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    _resultado(pid, result_id, db, user)
    conteudo = await arquivo.read(TAMANHO_MAXIMO + 1)
    if len(conteudo) > TAMANHO_MAXIMO:
        raise HTTPException(status_code=413, detail="O arquivo precisa ter no máximo 20 MB.")
    if not conteudo:
        raise HTTPException(status_code=422, detail="Arquivo vazio.")
    detectado = _tipo(conteudo)
    if detectado is None:
        raise HTTPException(status_code=422, detail="Envie o arquivo original em PDF, JPEG ou PNG.")
    mime_type, _fallback = detectado
    original = (arquivo.filename or "exame").strip()[:255] or "exame"

    row = PatientExamAttachment(
        owner_id=user.id,
        exam_result_id=result_id,
        uploaded_by=user.id,
        storage_name="",
        mime_type=mime_type,
        size_bytes=len(conteudo),
        original_name_cifrado=b"",
    )
    storage_name: str | None = None
    try:
        db.add(row)
        db.flush()
        storage_name = cofre.guardar(conteudo, row.id)
        row.storage_name = storage_name
        row.original_name_cifrado = cofre.cifrar_campo(original, row.id)
        db.add(AuditLog(
            user_id=user.id,
            action="attach_patient_exam_file",
            entity="patient_exam_result",
            entity_id=str(result_id),
            detail={"attachment_id": row.id, "mime_type": mime_type, "bytes": len(conteudo)},
        ))
        db.commit()
        db.refresh(row)
    except cofre.CofreIndisponivel as exc:
        db.rollback()
        if storage_name:
            cofre.apagar(storage_name)
        raise HTTPException(status_code=503, detail=f"Armazenamento seguro indisponível: {exc}") from exc
    except Exception:
        db.rollback()
        if storage_name:
            cofre.apagar(storage_name)
        raise
    return _dump(row)


@router.get("/{pid}/resultados/{result_id}/arquivos/{attachment_id}")
def abrir_arquivo_exame(
    pid: int,
    result_id: int,
    attachment_id: int,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    row = _anexo(pid, result_id, attachment_id, db, user)
    try:
        conteudo = cofre.ler(row.storage_name, row.id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado no armazenamento.") from exc
    except cofre.CofreIndisponivel as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    original = cofre.decifrar_campo(row.original_name_cifrado, row.id)
    fallback = next((f for _s, mime, f in _ASSINATURAS if mime == row.mime_type), "exame")
    db.add(AuditLog(
        user_id=user.id,
        action="read_patient_exam_file",
        entity="patient_exam_attachment",
        entity_id=str(row.id),
        detail={"exam_result_id": result_id, "mime_type": row.mime_type, "bytes": row.size_bytes},
    ))
    db.commit()

    return Response(
        content=conteudo,
        media_type=row.mime_type,
        headers={
            "Content-Disposition": f"inline; filename=\"{fallback}\"; filename*=UTF-8''{quote(original)}",
            "Cache-Control": "no-store, private",
            "X-Content-Type-Options": "nosniff",
        },
    )
