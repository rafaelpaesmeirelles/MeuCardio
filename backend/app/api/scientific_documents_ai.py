from __future__ import annotations

import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from app.core.db import get_db
from app.core.security import current_user
from app.core.uploads import UploadRejected, safe_filename, validate_file
from app.models.audit import AuditLog
from app.models.scientific_user_document import ScientificUserDocument
from app.services import cofre
from app.services import scientific_document_ai as engine

router = APIRouter(prefix="/api/documentos-cientificos-ia", tags=["documentos-cientificos-ia"])
MAX_FILE_BYTES = 25 * 1024 * 1024


def _row_for_user(document_id: int, db: Session, user) -> ScientificUserDocument:
    row = db.get(ScientificUserDocument, document_id)
    if not row or row.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Documento científico não encontrado.")
    return row


def _title(row: ScientificUserDocument) -> str:
    if row.display_title_cifrado:
        return cofre.decifrar_campo(row.display_title_cifrado, row.id)
    return cofre.decifrar_campo(row.original_name_cifrado, row.id)


def _analysis(row: ScientificUserDocument) -> dict:
    if not row.analysis_cifrado:
        return {}
    try:
        value = json.loads(cofre.decifrar_campo(row.analysis_cifrado, row.id))
    except (json.JSONDecodeError, ValueError):
        return {}
    return value if isinstance(value, dict) else {}


def _dump(row: ScientificUserDocument, *, detail: bool = False) -> dict:
    analysis = _analysis(row)
    payload = {
        "id": row.id,
        "title": _title(row),
        "document_type": row.document_type,
        "language": row.language,
        "doi": row.doi,
        "source_url": row.source_url,
        "media_type": row.media_type,
        "size_bytes": row.size_bytes,
        "sha256": row.sha256,
        "analysis_status": row.analysis_status,
        "analysis_error": row.analysis_error,
        "incorporation_recommended": row.incorporation_recommended,
        "incorporation_status": row.incorporation_status,
        "incorporated_document_id": row.incorporated_document_id,
        "created_at": row.created_at,
        "updated_at": row.updated_at,
        "summary_pt": analysis.get("summary_pt"),
        "incorporation_reason_pt": analysis.get("incorporation_reason_pt"),
    }
    if detail:
        extracted, translated, _ = engine.decrypt_payload(row)
        payload.update({
            "analysis": analysis,
            "extracted_text": extracted,
            "translated_text": translated or extracted,
            "translation_available": bool(translated),
        })
    return payload


@router.get("")
def list_documents(
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    rows = (
        db.query(ScientificUserDocument)
        .filter(ScientificUserDocument.owner_id == user.id)
        .order_by(ScientificUserDocument.created_at.desc(), ScientificUserDocument.id.desc())
        .all()
    )
    return [_dump(row) for row in rows]


@router.post("", status_code=201)
async def upload_document(
    arquivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    try:
        content = await arquivo.read(MAX_FILE_BYTES + 1)
    finally:
        await arquivo.close()
    if len(content) > MAX_FILE_BYTES:
        raise HTTPException(status_code=413, detail="O documento científico precisa ter no máximo 25 MB.")
    try:
        original_name = safe_filename(arquivo.filename, "documento-cientifico")
        # A política de anexo já valida PDF/OOXML/TXT de forma fail-closed,
        # incluindo macros, objetos incorporados e scripts em PDF.
        media_type = validate_file(content, original_name, "email")
    except UploadRejected as error:
        raise HTTPException(status_code=error.status_code, detail=error.detail) from error
    if media_type not in {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "text/plain",
        "text/csv",
    }:
        raise HTTPException(status_code=422, detail="Envie PDF, DOCX, PPTX, TXT ou CSV para análise científica.")

    digest = engine.sha256_bytes(content)
    existing = db.query(ScientificUserDocument).filter(
        ScientificUserDocument.owner_id == user.id,
        ScientificUserDocument.sha256 == digest,
    ).first()
    if existing:
        return _dump(existing)

    row = ScientificUserDocument(
        owner_id=user.id,
        storage_key="",
        original_name_cifrado=b"",
        display_title_cifrado=None,
        media_type=media_type,
        size_bytes=len(content),
        sha256=digest,
        analysis_status="pendente",
        incorporation_status="nao_avaliado",
    )
    storage_key: str | None = None
    try:
        db.add(row)
        db.flush()
        storage_key = cofre.guardar(content, row.id, raiz=engine.private_root())
        row.storage_key = storage_key
        row.original_name_cifrado = cofre.cifrar_campo(original_name, row.id)
        row.display_title_cifrado = cofre.cifrar_campo(original_name, row.id)
        db.add(AuditLog(
            user_id=user.id,
            action="upload_private_scientific_document",
            entity="scientific_user_document",
            entity_id=str(row.id),
            detail={"media_type": media_type, "size_bytes": len(content), "sha256": digest},
        ))
        db.commit()
    except IntegrityError:
        db.rollback()
        if storage_key:
            cofre.apagar(storage_key, raiz=engine.private_root())
        existing = db.query(ScientificUserDocument).filter(
            ScientificUserDocument.owner_id == user.id,
            ScientificUserDocument.sha256 == digest,
        ).first()
        if existing:
            return _dump(existing)
        raise
    except cofre.CofreIndisponivel as error:
        db.rollback()
        if storage_key:
            cofre.apagar(storage_key, raiz=engine.private_root())
        raise HTTPException(status_code=503, detail="Biblioteca científica privada indisponível.") from error
    db.refresh(row)
    return _dump(row)


@router.get("/{document_id}")
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    row = _row_for_user(document_id, db, user)
    db.add(AuditLog(
        user_id=user.id,
        action="read_private_scientific_document",
        entity="scientific_user_document",
        entity_id=str(row.id),
        detail={},
    ))
    db.commit()
    return _dump(row, detail=True)


@router.get("/{document_id}/arquivo")
def get_original_file(
    document_id: int,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    row = _row_for_user(document_id, db, user)
    try:
        content = cofre.ler(row.storage_key, row.id, raiz=engine.private_root())
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail="Arquivo original não encontrado.") from error
    except cofre.CofreIndisponivel as error:
        raise HTTPException(status_code=503, detail="Arquivo privado indisponível.") from error
    db.add(AuditLog(
        user_id=user.id,
        action="read_private_scientific_original",
        entity="scientific_user_document",
        entity_id=str(row.id),
        detail={"media_type": row.media_type},
    ))
    db.commit()
    return Response(
        content=content,
        media_type=row.media_type,
        headers={"Content-Disposition": f'inline; filename="documento-cientifico-{row.id}"', "Cache-Control": "no-store, private", "X-Content-Type-Options": "nosniff"},
    )


@router.post("/{document_id}/analisar")
async def analyze_document(
    document_id: int,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    row = _row_for_user(document_id, db, user)
    if row.analysis_status == "processando":
        raise HTTPException(status_code=409, detail="Este documento já está em análise.")
    row.analysis_status = "processando"
    row.analysis_error = None
    db.commit()
    try:
        content = cofre.ler(row.storage_key, row.id, raiz=engine.private_root())
        extracted = await run_in_threadpool(engine.extract_text, content, row.media_type)
        analysis = await run_in_threadpool(engine.analyze_text, extracted)
        duplicate = engine.find_duplicate(db, analysis)
        if duplicate:
            analysis["adds_to_corvia"] = False
            analysis["incorporation_reason_pt"] = f"Documento já representado no acervo CorVIA por {duplicate.title}."
            row.incorporation_status = "duplicado"
            row.incorporated_document_id = duplicate.id
        elif analysis.get("adds_to_corvia"):
            row.incorporation_status = "aguardando_consentimento"
        else:
            row.incorporation_status = "nao_recomendado"

        translated = ""
        if analysis.get("needs_translation"):
            translated = await run_in_threadpool(engine.translate_full_text, extracted)
        row.extracted_text_cifrado = cofre.cifrar_campo(extracted, row.id)
        row.translated_text_cifrado = cofre.cifrar_campo(translated, row.id) if translated else None
        row.analysis_cifrado = cofre.cifrar_campo(json.dumps(analysis, ensure_ascii=False), row.id)
        row.display_title_cifrado = cofre.cifrar_campo(str(analysis.get("title") or _title(row)), row.id)
        row.document_type = str(analysis.get("document_type") or "outro")[:40]
        row.language = str(analysis.get("language") or "")[:20] or None
        row.doi = str(analysis.get("doi") or "").strip()[:160] or None
        row.source_url = str(analysis.get("source_url") or "").strip() or None
        row.incorporation_recommended = bool(analysis.get("adds_to_corvia")) and duplicate is None
        row.analysis_status = "concluido"
        db.add(AuditLog(
            user_id=user.id,
            action="analyze_private_scientific_document",
            entity="scientific_user_document",
            entity_id=str(row.id),
            detail={"document_type": row.document_type, "language": row.language, "incorporation_recommended": row.incorporation_recommended, "duplicate_document_id": duplicate.id if duplicate else None},
        ))
        db.commit()
    except Exception as error:
        db.rollback()
        row = _row_for_user(document_id, db, user)
        row.analysis_status = "erro"
        row.analysis_error = type(error).__name__[:160]
        db.add(AuditLog(
            user_id=user.id,
            action="analyze_private_scientific_document_failed",
            entity="scientific_user_document",
            entity_id=str(row.id),
            detail={"error_type": type(error).__name__},
        ))
        db.commit()
        if isinstance(error, ValueError):
            raise HTTPException(status_code=422, detail=str(error)) from error
        raise HTTPException(status_code=502, detail=f"A análise científica não foi concluída ({type(error).__name__}). O original privado foi preservado.") from error
    return _dump(row, detail=True)


@router.post("/{document_id}/incorporar")
def incorporate_document(
    document_id: int,
    confirm_incorporation: bool = Form(...),
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    row = _row_for_user(document_id, db, user)
    if not confirm_incorporation:
        raise HTTPException(status_code=422, detail="Confirme explicitamente a incorporação ao acervo compartilhado do CorVIA.")
    if row.analysis_status != "concluido" or not row.analysis_cifrado:
        raise HTTPException(status_code=409, detail="Analise o documento antes de decidir sobre incorporação.")
    if row.incorporation_status == "duplicado" and row.incorporated_document_id:
        return {"incorporated": False, "duplicate": True, "document_id": row.incorporated_document_id}
    if not row.incorporation_recommended:
        raise HTTPException(status_code=409, detail="A análise atual não identificou ganho de repertório que justifique incorporação automática.")

    extracted, translated, analysis = engine.decrypt_payload(row)
    row.consented_at = datetime.now(timezone.utc)
    row.incorporation_status = "consentido"
    document = engine.incorporate(db, row, analysis, translated or extracted, reviewer_id=user.id)
    db.add(AuditLog(
        user_id=user.id,
        action="consent_and_incorporate_scientific_document",
        entity="scientific_user_document",
        entity_id=str(row.id),
        detail={"document_id": document.id, "slug": document.slug, "doi": row.doi},
    ))
    db.commit()
    return {"incorporated": row.incorporation_status == "incorporado", "duplicate": row.incorporation_status == "duplicado", "document_id": document.id, "slug": document.slug}
