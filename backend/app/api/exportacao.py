"""Tarefas 12 e 16 — exportação em PDF: material do paciente e modo apresentação.

As duas moram no mesmo router porque compartilham o mesmo motor de PDF e a
mesma regra de fundo: **exportar não cria conteúdo**. O que sai daqui é o que já
está publicado e verificado na plataforma, em outro formato.

O que muda entre elas é o destinatário, e isso muda tudo no desenho da página:
o material do paciente é retrato, corpo de leitura, linguagem leiga; a
apresentação é paisagem, corpo de projeção, um assunto por página.
"""

from __future__ import annotations

import re
import unicodedata

from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user
from app.models.audit import AuditLog
from app.models.content import Document
from app.models.patient_material import PatientMaterial
from app.services import apresentacao as svc_apres
from app.services import material_paciente as svc_material

router = APIRouter(tags=["exportação"])

LIMITE_ANOTACAO = 2000


def _dados_do_medico(user) -> dict:
    return {
        "full_name": getattr(user, "full_name", "") or "",
        "council_name": getattr(user, "council_name", None),
        "council_number": getattr(user, "council_number", None),
        "council_state": getattr(user, "council_state", None),
        "rqe": getattr(user, "rqe", None),
    }


def _nome_arquivo(base: str, sufixo: str) -> str:
    """Nome de arquivo sem acento e sem espaço.

    O cabeçalho `Content-Disposition` é latin-1 por padrão: acento cru nele faz o
    navegador baixar com nome corrompido, ou o servidor recusar o header.
    """
    limpo = unicodedata.normalize("NFKD", base).encode("ascii", "ignore").decode()
    limpo = re.sub(r"[^A-Za-z0-9]+", "-", limpo).strip("-").lower()[:80]
    return f"{limpo or 'corvia'}-{sufixo}.pdf"


def _pdf(conteudo: bytes, nome: str) -> Response:
    return Response(
        content=conteudo,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{nome}"'},
    )


# ---------------------------------------------------------------------------
# Tarefa 16 — modo apresentação
# ---------------------------------------------------------------------------

class PedidoApresentacao(BaseModel):
    anotacao: str = Field(default="", max_length=LIMITE_ANOTACAO)


@router.post("/api/biblioteca/{slug}/apresentacao")
def exportar_apresentacao(
    slug: str,
    dados: PedidoApresentacao | None = None,
    db: Session = Depends(get_db),
    user=Depends(current_user),
):
    """Exporta um documento publicado como apresentação para aula ou round.

    A anotação chega por POST e **não é gravada em lugar nenhum**: ela existe
    durante a geração do arquivo e some. É deliberado — a observação de um round
    específico não é conteúdo da plataforma, e persistir seria o primeiro passo
    para ela reaparecer como se fosse.
    """
    doc = (db.query(Document)
             .filter(Document.slug == slug, Document.published.is_(True))
             .first())
    if doc is None:
        raise HTTPException(status_code=404, detail="Documento não encontrado ou não publicado.")

    anotacao = (dados.anotacao if dados else "") or ""
    pdf = svc_apres.gerar(doc, _dados_do_medico(user), anotacao=anotacao.strip())

    db.add(AuditLog(user_id=user.id, action="exportar_apresentacao", entity="documents",
                    entity_id=slug[:255],
                    detail={"com_anotacao": bool(anotacao.strip()), "bytes": len(pdf)}))
    db.commit()
    return _pdf(pdf, _nome_arquivo(doc.title, "apresentacao"))


# ---------------------------------------------------------------------------
# Tarefa 12 — material educativo do paciente
# ---------------------------------------------------------------------------

def _dump(m: PatientMaterial) -> dict:
    return {
        "slug": m.slug, "titulo": m.titulo, "subtitulo": m.subtitulo,
        "tema": m.tema, "resumo": m.resumo, "documento_slug": m.documento_slug,
        "secoes": m.secoes or [], "sinais_de_alerta": list(m.sinais_de_alerta or []),
        "perguntas": list(m.perguntas or []), "fontes": list(m.fontes or []),
    }


@router.get("/api/material-paciente")
def listar_materiais(db: Session = Depends(get_db), _=Depends(current_user)):
    itens = (db.query(PatientMaterial)
               .filter(PatientMaterial.published.is_(True))
               .order_by(PatientMaterial.titulo)
               .all())
    return [{"slug": m.slug, "titulo": m.titulo, "subtitulo": m.subtitulo,
             "tema": m.tema, "resumo": m.resumo} for m in itens]


@router.get("/api/material-paciente/{slug}")
def obter_material(slug: str, db: Session = Depends(get_db), _=Depends(current_user)):
    m = (db.query(PatientMaterial)
           .filter(PatientMaterial.slug == slug, PatientMaterial.published.is_(True))
           .first())
    if m is None:
        raise HTTPException(status_code=404, detail="Material não encontrado.")
    return _dump(m)


@router.get("/api/material-paciente/{slug}/pdf")
def baixar_material(slug: str, db: Session = Depends(get_db), user=Depends(current_user)):
    """Gera o PDF que o médico imprime e entrega ao paciente.

    A identificação do prescritor vem do perfil de quem pede — o papel sai com o
    nome de quem entrega, e não genérico, porque é a essa pessoa que o paciente
    volta com dúvida.
    """
    m = (db.query(PatientMaterial)
           .filter(PatientMaterial.slug == slug, PatientMaterial.published.is_(True))
           .first())
    if m is None:
        raise HTTPException(status_code=404, detail="Material não encontrado.")

    pdf = svc_material.gerar(m, _dados_do_medico(user))
    db.add(AuditLog(user_id=user.id, action="gerar_material_paciente",
                    entity="patient_materials", entity_id=slug[:255],
                    detail={"bytes": len(pdf)}))
    db.commit()
    return _pdf(pdf, _nome_arquivo(m.titulo, "material-do-paciente"))
