import asyncio
import io

import pytest
from fastapi import HTTPException, UploadFile

from app.api import prescricao_especial
from app.models.assinatura import DocumentoEmitido
from app.models.clinical_docs import GeneratedDocument


def _doc(db, owner_id: int, *, status: str, mode: str = "propria") -> GeneratedDocument:
    g = GeneratedDocument(
        created_by=owner_id,
        doc_type=prescricao_especial.DOC_TYPE,
        title=prescricao_especial.TITULO,
        rendered_body="Texto",
        variables={
            "special_prescription": True,
            "originator_id": owner_id,
            "signer_id": owner_id,
            "mode": mode,
            "status": status,
        },
    )
    db.add(g)
    db.commit()
    db.refresh(g)
    return g


def test_pdf_manual_emitido_fica_disponivel_sem_fingir_assinatura(db, criar_usuario, monkeypatch):
    user, _ = criar_usuario(email="manual@teste.local")
    g = _doc(db, user.id, status="emitida_manual")
    registro = DocumentoEmitido(
        tipo="generated_document",
        referencia_id=g.id,
        metodo="MANUAL",
        nivel="nenhuma",
        arquivo_nome="fake",
        sha256="0" * 64,
        bytes_tam=8,
        assinado_em=None,
        criado_por=user.id,
    )
    db.add(registro)
    db.commit()
    monkeypatch.setattr(prescricao_especial.assinatura_emissao, "ler_bytes", lambda _registro: b"%PDF-ok")

    response = prescricao_especial.pdf(g.id, db=db, user=user)
    assert response.body == b"%PDF-ok"
    serializado = prescricao_especial._serializar(db, g)
    assert serializado["signed"] is False
    assert serializado["pdf_available"] is True


def test_upload_externo_rejeita_pdf_assinado_de_outro_documento(db, criar_usuario, monkeypatch):
    user, _ = criar_usuario(email="externo@teste.local")
    g = _doc(db, user.id, status="aguardando_assinatura_externa")
    registro = DocumentoEmitido(
        tipo="generated_document",
        referencia_id=g.id,
        metodo="VIDAAS",
        nivel="qualificada",
        arquivo_nome="fake-original",
        sha256="1" * 64,
        bytes_tam=17,
        assinado_em=None,
        criado_por=user.id,
    )
    db.add(registro)
    db.commit()
    monkeypatch.setattr(
        prescricao_especial.assinatura_emissao,
        "ler_bytes",
        lambda _registro: b"%PDF-original-corvia",
    )
    monkeypatch.setattr(prescricao_especial, "validate_file", lambda *_args, **_kwargs: None)

    upload = UploadFile(filename="assinado.pdf", file=io.BytesIO(b"%PDF-outro-documento-assinado"))
    with pytest.raises(HTTPException) as exc:
        asyncio.run(prescricao_especial.assinatura_externa(g.id, upload, db=db, user=user))
    assert exc.value.status_code == 422
    assert "não corresponde" in str(exc.value.detail)
