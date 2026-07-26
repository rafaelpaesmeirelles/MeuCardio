import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.core.security import current_user, require_admin
from app.models.audit import AuditLog
from app.models.rag import AIConversation, AIMessage
from app.services import rag

router = APIRouter(prefix="/api/ai", tags=["ia"])


class Pergunta(BaseModel):
    pergunta: str = Field(min_length=3, max_length=4000)
    conversation_id: int | None = None
    temas: list[str] | None = None


@router.get("/status")
def status(db: Session = Depends(get_db), user=Depends(current_user)):
    usado = rag.contar_uso_diario(db, user.id)
    return {
        "ativo": settings.ai_enabled and bool(settings.openai_api_key or settings.anthropic_api_key),
        "provedor": settings.ai_provider,
        "modelo": settings.openai_model if settings.ai_provider == "openai" else settings.anthropic_model,
        "limite_diario": settings.ai_daily_limit,
        "usado_hoje": usado,
        "restante_hoje": max(settings.ai_daily_limit - usado, 0),
        "aviso": "Não envie identificadores de paciente. As respostas exigem validação clínica.",
    }


@router.get("/conversas")
def listar_conversas(db: Session = Depends(get_db), user=Depends(current_user)):
    itens = db.execute(
        select(AIConversation)
        .where(AIConversation.user_id == user.id)
        .order_by(AIConversation.updated_at.desc())
        .limit(50)
    ).scalars().all()
    return [{"id": c.id, "titulo": c.titulo, "updated_at": c.updated_at} for c in itens]


@router.get("/conversas/{cid}")
def ler_conversa(cid: int, db: Session = Depends(get_db), user=Depends(current_user)):
    conv = db.get(AIConversation, cid)
    if not conv or conv.user_id != user.id:
        raise HTTPException(status_code=404, detail="Conversa não encontrada.")
    msgs = db.execute(
        select(AIMessage).where(AIMessage.conversation_id == cid).order_by(AIMessage.created_at)
    ).scalars().all()
    return {
        "id": conv.id,
        "titulo": conv.titulo,
        "mensagens": [{
            "papel": m.papel,
            "conteudo": m.conteudo,
            "fontes": json.loads(m.fontes) if m.fontes else [],
            "fontes_pubmed": json.loads(m.fontes_pubmed) if m.fontes_pubmed else [],
            "created_at": m.created_at,
        } for m in msgs],
    }


@router.delete("/conversas/{cid}", status_code=204)
def apagar_conversa(cid: int, db: Session = Depends(get_db), user=Depends(current_user)):
    conv = db.get(AIConversation, cid)
    if not conv or conv.user_id != user.id:
        raise HTTPException(status_code=404, detail="Conversa não encontrada.")
    db.delete(conv)
    db.commit()


@router.post("/perguntar")
def perguntar(dados: Pergunta, db: Session = Depends(get_db), user=Depends(current_user)):
    if not settings.ai_enabled:
        raise HTTPException(status_code=503, detail="A IA clínica está desligada nesta instalação.")

    achados = rag.identificadores_encontrados(dados.pergunta)
    if achados:
        raise HTTPException(
            status_code=422,
            detail=f"Remova estes identificadores antes de enviar: {', '.join(achados)}.",
        )

    usado = rag.contar_uso_diario(db, user.id)
    if usado >= settings.ai_daily_limit:
        raise HTTPException(
            status_code=429,
            detail=f"Limite diário de {settings.ai_daily_limit} consultas atingido. Recomeça amanhã.",
        )

    if dados.conversation_id:
        conv = db.get(AIConversation, dados.conversation_id)
        if not conv or conv.user_id != user.id:
            raise HTTPException(status_code=404, detail="Conversa não encontrada.")
    else:
        conv = AIConversation(user_id=user.id, titulo=dados.pergunta[:120].strip())
        db.add(conv)
        db.flush()

    anteriores = db.execute(
        select(AIMessage).where(AIMessage.conversation_id == conv.id).order_by(AIMessage.created_at)
    ).scalars().all()
    historico = [{"role": m.papel, "content": m.conteudo} for m in anteriores]

    try:
        r = rag.perguntar(db, dados.pergunta, historico, dados.temas)
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))
    except Exception as e:  # falha do provedor externo
        raise HTTPException(
            status_code=502,
            detail=f"O provedor de IA não respondeu ({type(e).__name__}). Tente novamente.",
        )

    db.add(AIMessage(conversation_id=conv.id, papel="user", conteudo=dados.pergunta))
    db.add(AIMessage(
        conversation_id=conv.id, papel="assistant", conteudo=r["texto"],
        fontes=r["fontes_json"],
        fontes_pubmed=json.dumps(r["fontes_pubmed"], ensure_ascii=False) if r["fontes_pubmed"] else None,
        modelo=r["modelo"],
        tokens_entrada=r["tokens_entrada"], tokens_saida=r["tokens_saida"],
    ))
    db.add(AuditLog(
        user_id=user.id, action="perguntar", entity="ia", entity_id=str(conv.id),
        detail={"modelo": r["modelo"], "fontes": [f["slug"] for f in r["fontes"]],
                "fontes_pubmed": [f["pmid"] for f in r["fontes_pubmed"]],
                "tokens": r["tokens_entrada"] + r["tokens_saida"]},
    ))
    db.commit()

    return {
        "conversation_id": conv.id,
        "resposta": r["texto"],
        "fontes": r["fontes"],
        "fontes_pubmed": r["fontes_pubmed"],
        "modelo": r["modelo"],
    }


@router.post("/reindexar")
def reindexar(
    tudo: bool = False, db: Session = Depends(get_db), user=Depends(require_admin)
):
    """Gera embeddings dos documentos. Consome créditos do provedor."""
    if not settings.ai_enabled:
        raise HTTPException(status_code=503, detail="A IA clínica está desligada nesta instalação.")
    resultado = rag.indexar_tudo(db, apenas_pendentes=not tudo)
    db.add(AuditLog(user_id=user.id, action="reindexar", entity="ia", detail=resultado))
    db.commit()
    return resultado
