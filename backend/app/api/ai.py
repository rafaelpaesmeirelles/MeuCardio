import json
import logging
from datetime import datetime, timezone
from queue import Empty, Queue
from threading import Thread

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.core.security import current_user, require_admin
from app.models.audit import AuditLog
from app.models.rag import AIConversation, AIMessage
from app.services import rag

log = logging.getLogger("corvia.ai")

router = APIRouter(prefix="/api/ai", tags=["ia"])

# IDs corretos dos modelos Claude, sem sufixo de data — mesma allowlist usada
# para validar `modelo` e para popular o seletor no frontend.
MODELOS_ANTHROPIC_PERMITIDOS = ["claude-opus-5", "claude-sonnet-5", "claude-haiku-4-5", "claude-fable-5"]

# Versão do texto de consentimento para o assistente usar ferramentas de
# agenda/e-mail — mesmo padrão de MOBILITY_CONSENT_VERSION em
# agenda_integrada.py. Mudar o texto do consentimento (app/api/ai.py, tela
# correspondente) exige subir esta versão; quem já aceitou a antiga volta a
# ver o pedido de consentimento.
FERRAMENTAS_CONSENT_VERSION = "assistente-ferramentas-v1-2026-08-06"

# Trabalho 15 (07/08/2026): os dois modos do assistente. Conversa nova grava
# o modo escolhido; conversa existente usa sempre o modo com que nasceu
# (ver `_preparar_pergunta`) — o cliente não pode trocar o modo de um fio
# no meio da conversa.
MODOS_VALIDOS = {"clinica", "pessoal"}
_SSE_HEARTBEAT_SECONDS = 12.0


def _eventos_sse_da_fila(fila: Queue, fim: object, heartbeat_seconds: float = _SSE_HEARTBEAT_SECONDS):
    while True:
        try:
            evento = fila.get(timeout=heartbeat_seconds)
        except Empty:
            yield ": keep-alive\n\n"
            continue
        if evento is fim:
            break
        yield f"data: {json.dumps(evento, ensure_ascii=False)}\n\n"


class Pergunta(BaseModel):
    pergunta: str = Field(min_length=3, max_length=4000)
    conversation_id: int | None = None
    temas: list[str] | None = None
    modelo: str | None = None
    usar_internet: bool = False
    modo: str = "clinica"


class ConsentimentoFerramentas(BaseModel):
    ativar: bool


@router.get("/status")
def status(db: Session = Depends(get_db), user=Depends(current_user)):
    usado = rag.contar_uso_diario(db, user.id)
    return {
        "ativo": settings.ai_enabled and bool(settings.openai_api_key or settings.anthropic_api_key),
        "provedor": settings.ai_provider,
        "modelo": settings.openai_model if settings.ai_provider == "openai" else settings.anthropic_model,
        "modelos_disponiveis": MODELOS_ANTHROPIC_PERMITIDOS if settings.ai_provider == "anthropic" else [],
        "limite_diario": settings.ai_daily_limit,
        "usado_hoje": usado,
        "restante_hoje": max(settings.ai_daily_limit - usado, 0),
        "aviso": "Não envie identificadores de paciente. As respostas exigem validação clínica.",
        # Duas condições independentes — as duas precisam ser verdadeiras
        # para o assistente de fato usar as ferramentas nesta pergunta
        # (ver app/services/rag.py::_ferramentas_para). O frontend usa isto
        # para decidir se mostra o convite ao consentimento.
        "ferramentas_disponiveis_instalacao": settings.ai_assistant_tools_enabled,
        "ferramentas_consentidas": user.ia_ferramentas_consent_em is not None,
    }


@router.put("/ferramentas/consentimento")
def consentimento_ferramentas(dados: ConsentimentoFerramentas, db: Session = Depends(get_db), user=Depends(current_user)):
    """Liga/desliga o acesso do assistente às tools de agenda e CorvIA Mail
    do próprio médico. Revogável a qualquer momento — desligar aqui vale
    imediatamente na próxima pergunta, sem esperar a conversa atual acabar."""
    if dados.ativar:
        user.ia_ferramentas_consent_em = datetime.now(timezone.utc)
        user.ia_ferramentas_consent_versao = FERRAMENTAS_CONSENT_VERSION
    else:
        user.ia_ferramentas_consent_em = None
        user.ia_ferramentas_consent_versao = None
    db.add(AuditLog(
        user_id=user.id,
        action="ia_ferramentas_consent_concedido" if dados.ativar else "ia_ferramentas_consent_revogado",
        entity="user", entity_id=str(user.id),
        detail={"versao": FERRAMENTAS_CONSENT_VERSION},
    ))
    db.commit()
    return {
        "ferramentas_consentidas": user.ia_ferramentas_consent_em is not None,
        "consent_em": user.ia_ferramentas_consent_em,
    }


@router.get("/conversas")
def listar_conversas(modo: str | None = None, db: Session = Depends(get_db), user=Depends(current_user)):
    """`modo` filtra o histórico (Trabalho 15) — sem ele, devolve os dois
    misturados, mas o frontend sempre passa o modo da tela atual, para
    Clínica e Pessoal nunca aparecerem no mesmo histórico."""
    if modo is not None and modo not in MODOS_VALIDOS:
        raise HTTPException(status_code=422, detail=f"modo inválido. Use um de: {', '.join(sorted(MODOS_VALIDOS))}.")
    consulta = select(AIConversation).where(AIConversation.user_id == user.id)
    if modo is not None:
        consulta = consulta.where(AIConversation.modo == modo)
    itens = db.execute(consulta.order_by(AIConversation.updated_at.desc()).limit(50)).scalars().all()
    return [{"id": c.id, "titulo": c.titulo, "modo": c.modo, "updated_at": c.updated_at} for c in itens]


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
        "modo": conv.modo,
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


def _preparar_pergunta(dados: Pergunta, db: Session, user) -> tuple[AIConversation, list[dict], str | None]:
    """Validações e preparação comuns às duas rotas (normal e streaming) —
    existir em duas rotas não pode significar duas regras de validação."""
    if not settings.ai_enabled:
        raise HTTPException(status_code=503, detail="A IA clínica está desligada nesta instalação.")

    if dados.modo not in MODOS_VALIDOS:
        raise HTTPException(status_code=422, detail=f"modo inválido. Use um de: {', '.join(sorted(MODOS_VALIDOS))}.")

    achados = rag.identificadores_encontrados(dados.pergunta)
    if achados:
        raise HTTPException(
            status_code=422,
            detail=f"Remova estes identificadores antes de enviar: {', '.join(achados)}.",
        )

    if dados.modelo is not None and dados.modelo not in MODELOS_ANTHROPIC_PERMITIDOS:
        raise HTTPException(
            status_code=422,
            detail=f"Modelo inválido. Use um de: {', '.join(MODELOS_ANTHROPIC_PERMITIDOS)}.",
        )
    if dados.usar_internet and settings.ai_provider != "anthropic":
        raise HTTPException(
            status_code=422,
            detail="A busca na internet exige o provedor Claude (AI_PROVIDER=anthropic).",
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
        conv = AIConversation(user_id=user.id, titulo=dados.pergunta[:120].strip(), modo=dados.modo)
        db.add(conv)
        # commit, não flush: a conversa precisa estar DURAVELMENTE gravada
        # antes de perguntar() começar — achado em produção (IntegrityError
        # em ai_messages, FK apontando pra conversation_id inexistente): com
        # só flush(), a conversa ficava presa numa transação aberta e OCIOSA
        # durante os ~1-2 min de streaming/busca na internet, e o
        # idle_in_transaction_session_timeout do Postgres derrubava essa
        # transação no meio — a linha "existia" só na sessão do SQLAlchemy,
        # nunca foi de fato commitada, e o INSERT final em ai_messages
        # referenciava um id que não estava na tabela.
        db.commit()

    anteriores = db.execute(
        select(AIMessage).where(AIMessage.conversation_id == conv.id).order_by(AIMessage.created_at)
    ).scalars().all()
    historico = [{"role": m.papel, "content": m.conteudo} for m in anteriores]

    # Usuário não escolheu modelo manualmente no dropdown ("Automático") — decide
    # pelo conteúdo da pergunta, em vez de deixar o provider cair no modelo fixo
    # do .env.
    modelo_efetivo = dados.modelo
    if modelo_efetivo is None and settings.ai_provider == "anthropic":
        modelo_efetivo = rag.escolher_modelo_automatico(dados.pergunta)

    return conv, historico, modelo_efetivo


@router.post("/perguntar")
def perguntar(dados: Pergunta, db: Session = Depends(get_db), user=Depends(current_user)):
    conv, historico, modelo_efetivo = _preparar_pergunta(dados, db, user)

    try:
        r = rag.perguntar(
            db, dados.pergunta, historico, dados.temas,
            modelo=modelo_efetivo, usar_internet=dados.usar_internet, user=user,
            modo=conv.modo,
        )
    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))
    except Exception as e:  # falha do provedor externo
        log.exception("Falha em /ai/perguntar (conversation_id=%s)", conv.id)
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
        "modo": conv.modo,
        "resposta": r["texto"],
        "fontes": r["fontes"],
        "fontes_pubmed": r["fontes_pubmed"],
        "modelo": r["modelo"],
        "truncado": r["truncado"],
    }


@router.post("/perguntar/stream")
def perguntar_stream(dados: Pergunta, db: Session = Depends(get_db), user=Depends(current_user)):
    """Mesma rota de `/perguntar`, em streaming (Server-Sent Events).

    Existe porque uma pergunta com busca na internet ligada podia passar de
    100s de ponta a ponta — mais do que uma conexão HTTP comum (NAT, proxy,
    navegador) tolera ociosa — e o front recebia "Failed to fetch" mesmo com
    a resposta pronta do lado do servidor. Streaming mantém bytes chegando o
    tempo todo, o que evita esse timeout por inatividade da conexão.
    """
    conv, historico, modelo_efetivo = _preparar_pergunta(dados, db, user)
    # Capturados como valores simples, não objetos ORM — ver o comentário
    # dentro de eventos() sobre por que a sessão do Depends(get_db) não pode
    # ser usada lá dentro.
    conv_id = conv.id
    conv_modo = conv.modo
    user_id = user.id

    def eventos():
        fila = Queue()
        fim = object()

        def produzir_eventos():
            # Sessão própria, independente da injetada por Depends(get_db).
            # Achado ao vivo em produção (DetachedInstanceError em conv.id): o
            # FastAPI encerra a sessão do Depends assim que esta rota RETORNA o
            # StreamingResponse — não quando o generator termina de rodar.
            # Como a geração agora roda numa thread para permitir heartbeats,
            # a sessão também precisa nascer e morrer dentro dessa thread.
            from app.core.db import SessionLocal
            from app.models.user import User

            db2 = SessionLocal()
            try:
                user2 = db2.get(User, user_id)
                for evento in rag.perguntar_stream(
                    db2, dados.pergunta, historico, dados.temas,
                    modelo=modelo_efetivo, usar_internet=dados.usar_internet, user=user2,
                    modo=conv_modo,
                ):
                    if "status" in evento:
                        fila.put({"tipo": "status", "etapa": evento["status"]})
                    elif "delta" in evento:
                        fila.put({"tipo": "delta", "texto": evento["delta"]})
                    elif "final" in evento:
                        r = evento["final"]
                        db2.add(AIMessage(conversation_id=conv_id, papel="user", conteudo=dados.pergunta))
                        db2.add(AIMessage(
                            conversation_id=conv_id, papel="assistant", conteudo=r["texto"],
                            fontes=r["fontes_json"],
                            fontes_pubmed=json.dumps(r["fontes_pubmed"], ensure_ascii=False) if r["fontes_pubmed"] else None,
                            modelo=r["modelo"],
                            tokens_entrada=r["tokens_entrada"], tokens_saida=r["tokens_saida"],
                        ))
                        db2.add(AuditLog(
                            user_id=user_id, action="perguntar", entity="ia", entity_id=str(conv_id),
                            detail={"modelo": r["modelo"], "fontes": [f["slug"] for f in r["fontes"]],
                                    "fontes_pubmed": [f["pmid"] for f in r["fontes_pubmed"]],
                                    "tokens": r["tokens_entrada"] + r["tokens_saida"], "via": "stream"},
                        ))
                        db2.commit()
                        fila.put({
                            "tipo": "final", "conversation_id": conv_id, "modo": conv_modo,
                            "fontes": r["fontes"], "fontes_pubmed": r["fontes_pubmed"],
                            "modelo": r["modelo"], "truncado": r["truncado"],
                        })
                    else:
                        raise ValueError("Evento inválido recebido do RAG.")
            except Exception as e:
                log.exception("Falha em /ai/perguntar/stream (conversation_id=%s)", conv_id)
                db2.rollback()
                fila.put({
                    "tipo": "erro",
                    "detalhe": f"O provedor de IA não respondeu ({type(e).__name__}). Tente novamente.",
                })
            finally:
                db2.close()
                fila.put(fim)

        Thread(
            target=produzir_eventos,
            name=f"corvia-ai-stream-{conv_id}",
            daemon=True,
        ).start()

        # Algumas etapas do provedor e das tools não produzem texto por vários
        # segundos. Sem bytes intermediários, navegador/proxy podiam tratar a
        # conexão como parada. Comentários SSE mantêm a conexão viva e são
        # ignorados pelo parser do cliente; não alteram o contrato dos eventos.
        yield from _eventos_sse_da_fila(fila, fim)

    return StreamingResponse(
        eventos(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache, no-transform", "X-Accel-Buffering": "no"},
    )


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
