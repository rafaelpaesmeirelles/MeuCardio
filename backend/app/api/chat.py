"""Chat entre assinantes.

As rotas HTTP persistem e consultam mensagens. A autenticação e o ciclo de vida
do WebSocket ficam em ``app.api.chat_session``, que usa a sessão HttpOnly do
navegador e mantém Bearer legado apenas como fallback para clientes externos.
"""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import ACESSO_LIBERADO, current_user
from app.models.chat import ChatMessage
from app.models.subscription import TIPO_MEUCARDIO, Subscription
from app.models.user import User
from app.services.professional_profile import council_display

router = APIRouter(prefix="/api/chat", tags=["chat"])


class NovaMensagem(BaseModel):
    body: str


def _e_assinante(db: Session, user_id: int, role: str) -> bool:
    if role == "admin":
        return True
    sub = (
        db.query(Subscription)
        .filter(Subscription.user_id == user_id, Subscription.kind == TIPO_MEUCARDIO)
        .order_by(Subscription.id)
        .first()
    )
    return sub is not None and sub.status in ACESSO_LIBERADO


def _dump_usuario_busca(u: User) -> dict:
    nome_conselho, estado_conselho = council_display(u)
    return {
        "id": u.id,
        "full_name": u.full_name,
        "email": u.email,
        "council_name": nome_conselho,
        "council_number": u.council_number,
        "council_state": estado_conselho,
        "specialty": u.specialty,
        "photo_url": u.photo_url,
    }


@router.get("/buscar-usuarios")
def buscar_usuarios(
    q: str = Query(..., min_length=2),
    conselho: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    """Busca por nome, e-mail ou número de registro — com filtro opcional de
    órgão de classe. Só retorna usuários que também são assinantes."""
    termo = f"%{q.strip()}%"
    consulta = db.query(User).filter(
        User.id != user.id,
        User.is_active.is_(True),
        or_(
            User.full_name.ilike(termo),
            User.email.ilike(termo),
            User.council_number.ilike(termo),
        ),
    )
    if conselho:
        consulta = consulta.filter(User.council_name == conselho)

    candidatos = consulta.order_by(User.full_name).limit(30).all()
    return [_dump_usuario_busca(u) for u in candidatos if _e_assinante(db, u.id, u.role)]


@router.get("/orgaos-de-classe")
def orgaos_de_classe(db: Session = Depends(get_db), _: User = Depends(current_user)):
    """Lista órgãos de classe distintos já cadastrados."""
    linhas = (
        db.query(User.council_name)
        .filter(User.council_name.isnot(None), User.council_name != "")
        .distinct()
        .order_by(User.council_name)
        .all()
    )
    return [linha[0] for linha in linhas]


@router.get("/suporte")
def contato_de_suporte(db: Session = Depends(get_db), user: User = Depends(current_user)):
    """Retorna o administrador principal para o atalho de suporte."""
    admin = (
        db.query(User)
        .filter(User.role == "admin", User.is_active.is_(True))
        .order_by(User.id)
        .first()
    )
    if admin is None or admin.id == user.id:
        return None
    return {
        **_dump_usuario_busca(admin),
        "online": bool(
            admin.last_seen_at
            and (datetime.now(timezone.utc) - admin.last_seen_at).total_seconds() <= 300
        ),
    }


@router.get("/conversas")
def listar_conversas(db: Session = Depends(get_db), user: User = Depends(current_user)):
    """Uma linha por interlocutor, com última mensagem e contagem de não lidas."""
    mensagens = (
        db.query(ChatMessage)
        .filter(or_(ChatMessage.sender_id == user.id, ChatMessage.recipient_id == user.id))
        .order_by(ChatMessage.created_at.desc())
        .all()
    )

    por_interlocutor: dict[int, dict] = {}
    for mensagem in mensagens:
        outro_id = mensagem.recipient_id if mensagem.sender_id == user.id else mensagem.sender_id
        if outro_id not in por_interlocutor:
            por_interlocutor[outro_id] = {
                "user_id": outro_id,
                "ultima_mensagem": mensagem.body,
                "ultima_em": mensagem.created_at,
                "de_mim": mensagem.sender_id == user.id,
                "nao_lidas": 0,
            }
        if mensagem.recipient_id == user.id and mensagem.read_at is None:
            por_interlocutor[outro_id]["nao_lidas"] += 1

    if not por_interlocutor:
        return []

    outros = db.query(User).filter(User.id.in_(por_interlocutor.keys())).all()
    nomes = {usuario.id: usuario for usuario in outros}

    resultado = []
    for outro_id, dados in por_interlocutor.items():
        usuario = nomes.get(outro_id)
        if not usuario:
            continue
        resultado.append({
            **dados,
            "full_name": usuario.full_name,
            "photo_url": usuario.photo_url,
        })
    resultado.sort(key=lambda conversa: conversa["ultima_em"], reverse=True)
    return resultado


@router.get("/nao-lidas")
def contar_nao_lidas(db: Session = Depends(get_db), user: User = Depends(current_user)):
    """Retorna o total de mensagens não lidas para o badge do chat."""
    total = (
        db.query(func.count(ChatMessage.id))
        .filter(ChatMessage.recipient_id == user.id, ChatMessage.read_at.is_(None))
        .scalar()
    )
    return {"total": total or 0}


@router.get("/mensagens/{outro_id}")
def historico(
    outro_id: int,
    antes_de: int | None = None,
    limite: int = 50,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    outro = db.get(User, outro_id)
    if not outro:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    consulta = db.query(ChatMessage).filter(
        or_(
            and_(ChatMessage.sender_id == user.id, ChatMessage.recipient_id == outro_id),
            and_(ChatMessage.sender_id == outro_id, ChatMessage.recipient_id == user.id),
        )
    )
    if antes_de:
        consulta = consulta.filter(ChatMessage.id < antes_de)
    mensagens = consulta.order_by(ChatMessage.id.desc()).limit(min(limite, 100)).all()
    mensagens.reverse()

    return [
        {
            "id": mensagem.id,
            "sender_id": mensagem.sender_id,
            "recipient_id": mensagem.recipient_id,
            "body": mensagem.body,
            "created_at": mensagem.created_at,
            "read_at": mensagem.read_at,
        }
        for mensagem in mensagens
    ]


@router.post("/mensagens/{outro_id}")
async def enviar_mensagem(
    outro_id: int,
    dados: NovaMensagem,
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    corpo = dados.body.strip()
    if not corpo:
        raise HTTPException(status_code=422, detail="Mensagem vazia.")
    if len(corpo) > 4000:
        raise HTTPException(status_code=422, detail="Mensagem muito longa (máximo 4000 caracteres).")

    outro = db.get(User, outro_id)
    if not outro or not outro.is_active:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    if not _e_assinante(db, outro_id, outro.role):
        raise HTTPException(status_code=403, detail="Este usuário não tem assinatura ativa no momento.")

    mensagem = ChatMessage(sender_id=user.id, recipient_id=outro_id, body=corpo)
    db.add(mensagem)
    db.commit()
    db.refresh(mensagem)

    payload = {
        "tipo": "mensagem",
        "id": mensagem.id,
        "sender_id": mensagem.sender_id,
        "recipient_id": mensagem.recipient_id,
        "body": mensagem.body,
        "created_at": mensagem.created_at.isoformat(),
    }
    await gerenciador.enviar_para(outro_id, payload)
    await gerenciador.enviar_para(user.id, payload)

    return payload


@router.post("/mensagens/{outro_id}/marcar-lidas")
def marcar_lidas(outro_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    agora = datetime.now(timezone.utc)
    atualizadas = (
        db.query(ChatMessage)
        .filter(
            ChatMessage.sender_id == outro_id,
            ChatMessage.recipient_id == user.id,
            ChatMessage.read_at.is_(None),
        )
        .update({"read_at": agora}, synchronize_session=False)
    )
    db.commit()
    return {"marcadas": atualizadas}


class GerenciadorDeConexoes:
    """Mantém as conexões WebSocket ativas por usuário e dispositivo."""

    def __init__(self) -> None:
        self._conexoes: dict[int, list] = {}

    async def conectar(self, user_id: int, ws) -> None:
        await ws.accept()
        self._conexoes.setdefault(user_id, []).append(ws)

    def desconectar(self, user_id: int, ws) -> None:
        conexoes = self._conexoes.get(user_id)
        if not conexoes:
            return
        if ws in conexoes:
            conexoes.remove(ws)
        if not conexoes:
            self._conexoes.pop(user_id, None)

    async def enviar_para(self, user_id: int, payload: dict) -> None:
        for ws in list(self._conexoes.get(user_id, [])):
            try:
                await ws.send_json(payload)
            except Exception:
                self.desconectar(user_id, ws)

    async def encerrar_usuario(self, user_id: int) -> None:
        """Derruba conexoes antigas quando a sessao unica e substituida."""
        conexoes = list(self._conexoes.pop(user_id, []))
        for ws in conexoes:
            try:
                await ws.close(code=4401, reason="Sessão substituída por um novo login.")
            except Exception:
                pass


gerenciador = GerenciadorDeConexoes()
