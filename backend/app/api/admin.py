"""Curadoria editorial: o que a equipe assistencial pode ver."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import require_admin
from app.models.audit import AuditLog
from app.models.content import Document

router = APIRouter(prefix="/api/admin", tags=["administração"])


class DecisaoRevisao(BaseModel):
    publicar: bool
    nota: str | None = None


@router.get("/overview")
def overview(db: Session = Depends(get_db), _=Depends(require_admin)):
    por_tier = dict(
        db.execute(select(Document.source_tier, func.count()).group_by(Document.source_tier)).all()
    )
    por_status = dict(
        db.execute(select(Document.review_status, func.count()).group_by(Document.review_status)).all()
    )
    publicados = db.query(Document).filter(Document.published.is_(True)).count()
    com_lacuna = db.query(Document).filter(func.cardinality(Document.gaps) > 0).count()
    return {
        "total": db.query(Document).count(),
        "publicados": publicados,
        "retidos": db.query(Document).filter(Document.published.is_(False)).count(),
        "por_nivel_de_fonte": por_tier,
        "por_status_de_revisao": por_status,
        "com_lacuna_declarada": com_lacuna,
    }


@router.get("/queue")
def fila_de_revisao(
    tier: str | None = Query(None, description="A, B, C ou sem_fonte"),
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    """Fila priorizada: o que sustenta melhor evidência aparece primeiro."""
    q = db.query(Document).filter(Document.published.is_(False))
    if tier:
        q = q.filter(Document.source_tier == tier)
    ordem = {"A": 0, "B": 1, "C": 2, "sem_fonte": 3}
    itens = sorted(q.limit(500).all(), key=lambda d: (ordem.get(d.source_tier, 9), d.title))[:limit]
    return [
        {
            "slug": d.slug, "title": d.title, "theme": d.theme, "kind": d.kind,
            "source_tier": d.source_tier, "review_status": d.review_status,
            "gaps": d.gaps, "source_refs": d.source_refs,
        }
        for d in itens
    ]


@router.post("/documents/{slug}/review")
def revisar(
    slug: str,
    decisao: DecisaoRevisao,
    db: Session = Depends(get_db),
    user=Depends(require_admin),
):
    doc = db.query(Document).filter(Document.slug == slug).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Documento não encontrado.")

    doc.published = decisao.publicar
    doc.review_status = "revisado" if decisao.publicar else "pendente_revisao"
    doc.reviewed_by = user.id
    doc.reviewed_at = datetime.now(timezone.utc)
    db.add(AuditLog(
        user_id=user.id,
        action="publicar" if decisao.publicar else "despublicar",
        entity="document",
        entity_id=slug,
        detail={"tier": doc.source_tier, "nota": decisao.nota, "gaps": doc.gaps},
    ))
    db.commit()
    return {"slug": doc.slug, "published": doc.published, "review_status": doc.review_status}


@router.post("/import")
def importar(db: Session = Depends(get_db), user=Depends(require_admin)):
    from app.services.importer import import_directory

    resultado = import_directory()
    db.add(AuditLog(user_id=user.id, action="importar", entity="content", detail=resultado))
    db.commit()
    return resultado


# --------------------------------------------------------------- usuários --
# Duas portas de entrada: o admin cria uma conta já aprovada (rota abaixo), ou
# a pessoa se cadastra sozinha em /api/auth/solicitar-acesso e cai numa fila
# pendente — inativa, sem acesso a nada — até um admin conferir os dados
# profissionais (conselho de classe, número de registro) e aprovar.

class NovoUsuario(BaseModel):
    email: str
    full_name: str
    crm: str | None = None
    role: str = "medico"  # admin | medico | residente | leitor
    password: str


class SenhaTemporaria(BaseModel):
    password: str


class DecisaoAcesso(BaseModel):
    aprovar: bool
    role: str = "medico"  # perfil definitivo, só usado se aprovar=true
    nota: str | None = None  # motivo, sobretudo se rejeitado


def _dump_usuario(u) -> dict:
    return {
        "id": u.id, "email": u.email, "full_name": u.full_name,
        "birth_date": u.birth_date, "cpf": u.cpf, "profession": u.profession,
        "council_name": u.council_name, "council_number": u.council_number,
        "council_state": u.council_state, "specialty": u.specialty,
        "role": u.role, "status": u.status, "is_active": u.is_active,
        "rejection_note": u.rejection_note, "created_at": u.created_at,
    }


@router.get("/users")
def listar_usuarios(
    status: str | None = None, db: Session = Depends(get_db), _=Depends(require_admin)
):
    from app.models.user import User

    q = db.query(User)
    if status:
        q = q.filter(User.status == status)
    itens = q.order_by(User.status, User.full_name).all()
    return [_dump_usuario(u) for u in itens]


@router.post("/users/{user_id}/decidir")
def decidir_solicitacao(
    user_id: int, dados: DecisaoAcesso, db: Session = Depends(get_db), admin=Depends(require_admin)
):
    """Aprova ou rejeita uma solicitação de autocadastro. Aprovar libera o
    acesso (is_active=True) com o perfil escolhido aqui, não o que a pessoa
    pediu — quem decide o nível de acesso é sempre o admin."""
    from datetime import datetime, timezone

    from app.models.user import User

    alvo = db.get(User, user_id)
    if not alvo:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    if alvo.status != "pendente":
        raise HTTPException(status_code=409, detail="Esta solicitação já foi decidida.")
    if dados.aprovar and dados.role not in ("admin", "medico", "residente", "leitor"):
        raise HTTPException(status_code=422, detail="Perfil inválido.")

    alvo.status = "aprovado" if dados.aprovar else "rejeitado"
    alvo.is_active = dados.aprovar
    alvo.role = dados.role if dados.aprovar else alvo.role
    alvo.reviewed_by = admin.id
    alvo.reviewed_at = datetime.now(timezone.utc)
    alvo.rejection_note = None if dados.aprovar else (dados.nota or "Não especificado")

    db.add(AuditLog(
        user_id=admin.id, action="aprovar_acesso" if dados.aprovar else "rejeitar_acesso",
        entity="user", entity_id=str(alvo.id),
        detail={"email": alvo.email, "role": alvo.role, "nota": dados.nota},
    ))
    db.commit()
    return _dump_usuario(alvo)


@router.post("/users", status_code=201)
def criar_usuario(dados: NovoUsuario, db: Session = Depends(get_db), admin=Depends(require_admin)):
    from app.core.security import hash_password
    from app.models.user import User

    email = dados.email.strip().lower()
    if not email or "@" not in email:
        raise HTTPException(status_code=422, detail="E-mail inválido.")
    if len(dados.password) < 8:
        raise HTTPException(status_code=422, detail="A senha precisa ter ao menos 8 caracteres.")
    if dados.role not in ("admin", "medico", "residente", "leitor"):
        raise HTTPException(status_code=422, detail="Perfil inválido.")
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=409, detail="Já existe uma conta com este e-mail.")

    novo = User(
        email=email, full_name=dados.full_name.strip(), crm=dados.crm,
        role=dados.role, password_hash=hash_password(dados.password), is_active=True,
    )
    db.add(novo)
    db.flush()
    db.add(AuditLog(user_id=admin.id, action="criar_usuario", entity="user",
                    entity_id=str(novo.id), detail={"email": email, "role": dados.role}))
    db.commit()
    return {"id": novo.id, "email": novo.email, "full_name": novo.full_name, "role": novo.role}


@router.patch("/users/{user_id}/ativo")
def alternar_usuario(
    user_id: int, ativo: bool, db: Session = Depends(get_db), admin=Depends(require_admin)
):
    from app.models.user import User

    alvo = db.get(User, user_id)
    if not alvo:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    if alvo.id == admin.id and not ativo:
        raise HTTPException(status_code=400, detail="Você não pode desativar sua própria conta.")
    alvo.is_active = ativo
    db.add(AuditLog(user_id=admin.id, action="ativar" if ativo else "desativar",
                    entity="user", entity_id=str(alvo.id)))
    db.commit()
    return {"id": alvo.id, "is_active": alvo.is_active}


@router.post("/users/{user_id}/senha")
def redefinir_senha(
    user_id: int, dados: SenhaTemporaria, db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    from app.core.security import hash_password
    from app.models.user import User

    alvo = db.get(User, user_id)
    if not alvo:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    if len(dados.password) < 8:
        raise HTTPException(status_code=422, detail="A senha precisa ter ao menos 8 caracteres.")
    alvo.password_hash = hash_password(dados.password)
    db.add(AuditLog(user_id=admin.id, action="redefinir_senha", entity="user",
                    entity_id=str(alvo.id)))
    db.commit()
    return {"id": alvo.id, "nota": "Senha redefinida. Repasse ao usuário por um canal seguro."}
