from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import create_access_token, current_user, hash_password, verify_password
from app.core.validators import UFS, cpf_valido, limpar_cpf
from app.models.user import User

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form.username.lower().strip()).first()
    if not user or not verify_password(form.password, user.password_hash):
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos.")
    if user.status == "pendente":
        raise HTTPException(
            status_code=403,
            detail="Seu cadastro ainda está em análise. Você recebe acesso assim que um "
                   "administrador confirmar seu registro no conselho de classe.",
        )
    if user.status == "rejeitado":
        raise HTTPException(
            status_code=403,
            detail="Sua solicitação de acesso não foi aprovada. Fale com a administração "
                   "do serviço para mais informações.",
        )
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Esta conta está desativada.")
    return {"access_token": create_access_token(user.email), "token_type": "bearer"}


def _cpf_mascarado(cpf: str | None) -> str | None:
    """Só os quatro últimos dígitos ficam legíveis — o suficiente pro titular
    reconhecer o próprio cadastro sem expor o documento inteiro na tela."""
    if not cpf:
        return None
    digitos = limpar_cpf(cpf)
    if len(digitos) != 11:
        return None
    return f"***.***.{digitos[6:9]}-{digitos[9:]}"


def _perfil(user: User) -> dict:
    return {
        "id": user.id, "email": user.email, "full_name": user.full_name,
        "role": user.role, "specialty": user.specialty,
        "council": f"{user.council_name} {user.council_number}/{user.council_state}"
                   if user.council_name else None,
        "crm": user.crm,
        "profession": user.profession,
        "council_name": user.council_name,
        "council_number": user.council_number,
        "council_state": user.council_state,
        "cpf_mascarado": _cpf_mascarado(user.cpf),
        "birth_date": user.birth_date,
        "created_at": user.created_at,
    }


@router.get("/me")
def me(user: User = Depends(current_user)):
    return _perfil(user)


class DadosPessoais(BaseModel):
    """Só o que o próprio titular pode corrigir sozinho. E-mail fica de fora
    porque é a identidade do token JWT, e CPF/data de nascimento porque são os
    dados conferidos na aprovação do cadastro — mudança neles passa pelo admin."""

    full_name: str
    profession: str | None = None
    council_name: str | None = None
    council_number: str | None = None
    council_state: str | None = None
    specialty: str | None = None

    @field_validator("full_name")
    @classmethod
    def _nome(cls, v: str) -> str:
        if len(v.strip().split()) < 2:
            raise ValueError("Informe nome completo.")
        return v.strip()

    @field_validator("council_state")
    @classmethod
    def _uf(cls, v: str | None) -> str | None:
        if v is None or not v.strip():
            return None
        v = v.strip().upper()
        if v not in UFS:
            raise ValueError("Estado do conselho inválido — use a sigla (ex.: SP).")
        return v


@router.patch("/me")
def atualizar_me(dados: DadosPessoais, db: Session = Depends(get_db),
                 user: User = Depends(current_user)):
    user.full_name = dados.full_name
    user.profession = (dados.profession or "").strip() or None
    user.council_name = (dados.council_name or "").strip().upper() or None
    user.council_number = (dados.council_number or "").strip() or None
    user.council_state = dados.council_state
    user.specialty = (dados.specialty or "").strip() or None
    db.commit()
    db.refresh(user)
    return _perfil(user)


class TrocaDeSenha(BaseModel):
    senha_atual: str
    nova_senha: str


@router.post("/alterar-senha")
def alterar_senha(dados: TrocaDeSenha, db: Session = Depends(get_db),
                  user: User = Depends(current_user)):
    if not verify_password(dados.senha_atual, user.password_hash):
        raise HTTPException(status_code=400, detail="Senha atual incorreta.")
    if len(dados.nova_senha) < 8:
        raise HTTPException(status_code=422, detail="A nova senha precisa ter ao menos 8 caracteres.")
    if dados.nova_senha == dados.senha_atual:
        raise HTTPException(status_code=422, detail="A nova senha precisa ser diferente da atual.")
    user.password_hash = hash_password(dados.nova_senha)
    db.commit()
    return {"nota": "Senha alterada."}


class SolicitacaoAcesso(BaseModel):
    full_name: str
    birth_date: date
    cpf: str
    profession: str
    council_name: str
    council_number: str
    council_state: str
    specialty: str | None = None
    email: str
    password: str

    @field_validator("full_name")
    @classmethod
    def _nome(cls, v: str) -> str:
        if len(v.strip().split()) < 2:
            raise ValueError("Informe nome completo.")
        return v.strip()

    @field_validator("council_state")
    @classmethod
    def _uf(cls, v: str) -> str:
        v = v.strip().upper()
        if v not in UFS:
            raise ValueError("Estado do conselho inválido — use a sigla (ex.: SP).")
        return v

    @field_validator("email")
    @classmethod
    def _email(cls, v: str) -> str:
        v = v.strip().lower()
        if "@" not in v:
            raise ValueError("E-mail inválido.")
        return v


@router.post("/solicitar-acesso", status_code=201)
def solicitar_acesso(dados: SolicitacaoAcesso, db: Session = Depends(get_db)):
    """Acesso público. Cria conta PENDENTE e INATIVA — só um admin aprovando ela
    passa a valer. Nenhum dado de paciente é visível antes disso."""
    if dados.birth_date >= date.today():
        raise HTTPException(status_code=422, detail="Data de nascimento inválida.")
    if not cpf_valido(dados.cpf):
        raise HTTPException(status_code=422, detail="CPF inválido — confira os números digitados.")
    if len(dados.password) < 8:
        raise HTTPException(status_code=422, detail="A senha precisa ter ao menos 8 caracteres.")

    cpf_limpo = limpar_cpf(dados.cpf)
    if db.query(User).filter(User.email == dados.email).first():
        raise HTTPException(status_code=409, detail="Já existe uma solicitação ou conta com este e-mail.")
    if db.query(User).filter(User.cpf == cpf_limpo).first():
        raise HTTPException(status_code=409, detail="Já existe uma solicitação ou conta com este CPF.")

    novo = User(
        email=dados.email, full_name=dados.full_name, birth_date=dados.birth_date,
        cpf=cpf_limpo, profession=dados.profession.strip(),
        council_name=dados.council_name.strip().upper(), council_number=dados.council_number.strip(),
        council_state=dados.council_state, specialty=(dados.specialty or "").strip() or None,
        password_hash=hash_password(dados.password),
        role="leitor",  # perfil mínimo até o admin decidir o perfil definitivo na aprovação
        status="pendente", is_active=False,
    )
    db.add(novo)
    db.commit()

    from app.services.notificar import notificar_admins_nova_solicitacao
    notificar_admins_nova_solicitacao(db, novo.full_name, novo.email)

    return {
        "nota": "Solicitação registrada. Você recebe acesso assim que um administrador "
                "conferir seus dados profissionais."
    }
