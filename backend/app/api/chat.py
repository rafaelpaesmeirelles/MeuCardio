"""Chat entre assinantes (Tarefa de 31/07/2026, pedido do Rafael).

Sem tabela de "conversa": o par (sender_id, recipient_id) já identifica a
thread. Entrega em tempo real via WebSocket, com um `ConnectionManager` em
memória — este backend roda como processo único (ver docker-compose.prod.yml,
sem réplicas), então não há necessidade de pub/sub via Redis para sincronizar
conexões entre instâncias. Se isso mudar, é aqui que entra.

Autenticação do WebSocket é manual (não usa `Depends(oauth2_scheme)`): o
WebSocket nativo do browser não permite header `Authorization` customizado, só
query string ou subprotocolo — o token chega como `?token=`.
"""
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import SessionLocal, get_db
from app.core.security import ACESSO_LIBERADO, current_user
from app.models.chat import ChatMessage
from app.models.subscription import TIPO_MEUCARDIO, Subscription
from app.models.user import User

router = APIRouter(prefix="/api/chat", tags=["chat"])

# O WebSocket vive num router À PARTE, sem o `Depends(assinante_ativo)` que
# `main.py` aplica a `router` via `include_router(..., dependencies=[...])`.
# Medido na prática: esse `dependencies` do include_router SE APLICA também a
# rotas de WebSocket, e `assinante_ativo`/`current_user` dependem de
# `OAuth2PasswordBearer`, que exige um `Request` HTTP — recebendo um
# `WebSocket` no lugar, estoura `TypeError` e a conexão cai com HTTP 500 no
# handshake. Autenticação e checagem de assinatura do WS são feitas à mão,
# dentro do próprio handler (`_usuario_do_token_ws` + `_e_assinante`).
router_ws = APIRouter(prefix="/api/chat", tags=["chat"])


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
    return {
        "id": u.id,
        "full_name": u.full_name,
        "email": u.email,
        "council_name": u.council_name,
        "council_number": u.council_number,
        "council_state": u.council_state,
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
    órgão de classe (CRM, COREN, CRF...). Só retorna quem também é assinante:
    conversar com uma conta pendente/sem assinatura não faz sentido aqui."""
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
    """Lista de `council_name` distintos já cadastrados, para popular o filtro
    de busca sem hardcodar a lista de conselhos no frontend."""
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
    """Quem é o "Dr. Rafael" do atalho "Fale com o Dr. Rafael" (pedido dele em
    31/07/2026).

    O responsável é o **admin de menor id** — mesmo critério que o resto do
    sistema já usa para identificar o administrador principal (ver as gravações
    de `AuditLog`). Não há coluna "é o dono do produto" no modelo, e criar uma
    só para isto seria migração de esquema para um dado que hoje tem uma única
    resposta possível.

    Devolve `null` em vez de 404 quando o próprio usuário é o responsável: para
    ele o atalho não faz sentido (conversaria consigo mesmo) e o frontend
    simplesmente não desenha o botão.
    """
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
        # O frontend precisa saber se pode contar com resposta rápida antes de
        # prometer isso ao assinante na interface.
        "online": bool(
            admin.last_seen_at
            and (datetime.now(timezone.utc) - admin.last_seen_at).total_seconds() <= 300
        ),
    }


@router.get("/conversas")
def listar_conversas(db: Session = Depends(get_db), user: User = Depends(current_user)):
    """Uma linha por interlocutor, com a última mensagem e a contagem de não
    lidas — o que a lista de conversas de qualquer chat mostra."""
    mensagens = (
        db.query(ChatMessage)
        .filter(or_(ChatMessage.sender_id == user.id, ChatMessage.recipient_id == user.id))
        .order_by(ChatMessage.created_at.desc())
        .all()
    )

    por_interlocutor: dict[int, dict] = {}
    for m in mensagens:
        outro_id = m.recipient_id if m.sender_id == user.id else m.sender_id
        if outro_id not in por_interlocutor:
            por_interlocutor[outro_id] = {
                "user_id": outro_id,
                "ultima_mensagem": m.body,
                "ultima_em": m.created_at,
                "de_mim": m.sender_id == user.id,
                "nao_lidas": 0,
            }
        if m.recipient_id == user.id and m.read_at is None:
            por_interlocutor[outro_id]["nao_lidas"] += 1

    if not por_interlocutor:
        return []

    outros = db.query(User).filter(User.id.in_(por_interlocutor.keys())).all()
    nomes = {u.id: u for u in outros}

    resultado = []
    for outro_id, dados in por_interlocutor.items():
        u = nomes.get(outro_id)
        if not u:
            continue
        resultado.append({
            **dados,
            "full_name": u.full_name,
            "photo_url": u.photo_url,
        })
    resultado.sort(key=lambda c: c["ultima_em"], reverse=True)
    return resultado


@router.get("/nao-lidas")
def contar_nao_lidas(db: Session = Depends(get_db), user: User = Depends(current_user)):
    """Só o total — usado pelo badge do ícone flutuante, chamado com mais
    frequência que a lista de conversas inteira."""
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
            "id": m.id,
            "sender_id": m.sender_id,
            "recipient_id": m.recipient_id,
            "body": m.body,
            "created_at": m.created_at,
            "read_at": m.read_at,
        }
        for m in mensagens
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

    msg = ChatMessage(sender_id=user.id, recipient_id=outro_id, body=corpo)
    db.add(msg)
    db.commit()
    db.refresh(msg)

    payload = {
        "tipo": "mensagem",
        "id": msg.id,
        "sender_id": msg.sender_id,
        "recipient_id": msg.recipient_id,
        "body": msg.body,
        "created_at": msg.created_at.isoformat(),
    }
    await gerenciador.enviar_para(outro_id, payload)
    await gerenciador.enviar_para(user.id, payload)  # ecoa nas outras abas do remetente

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


# --------------------------------------------------------------- WebSocket --

class GerenciadorDeConexoes:
    """Um usuário pode ter mais de uma aba/dispositivo aberto — por isso a
    lista, não uma conexão única por `user_id`."""

    def __init__(self) -> None:
        self._conexoes: dict[int, list[WebSocket]] = {}

    async def conectar(self, user_id: int, ws: WebSocket) -> None:
        await ws.accept()
        self._conexoes.setdefault(user_id, []).append(ws)

    def desconectar(self, user_id: int, ws: WebSocket) -> None:
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


gerenciador = GerenciadorDeConexoes()


def _usuario_do_token_ws(token: str, db: Session) -> User | None:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError:
        return None
    if payload.get("scope", "app") != "app":
        return None
    email = payload.get("sub")
    if not email:
        return None
    return db.query(User).filter(User.email == email, User.is_active.is_(True)).first()


@router_ws.websocket("/ws")
async def chat_ws(ws: WebSocket, token: str = Query(...)):
    # Dependência própria de sessão: `Depends(get_db)` é para rotas HTTP
    # normais, um WebSocket de vida longa não pode segurar essa sessão presa
    # à requisição inteira sem risco de vazar conexão do pool.
    db = SessionLocal()
    try:
        user = _usuario_do_token_ws(token, db)
        if user is None or not _e_assinante(db, user.id, user.role):
            await ws.close(code=4401)
            return
    finally:
        db.close()

    await gerenciador.conectar(user.id, ws)
    try:
        while True:
            # O envio de mensagem em si vai por HTTP (POST /mensagens/{id}),
            # que já cuida de persistência e validação. O socket só recebe
            # pings/keepalive do cliente para detectar desconexão cedo.
            await ws.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        gerenciador.desconectar(user.id, ws)
