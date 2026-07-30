import secrets
from datetime import date
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from app.core.config import settings
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
        "rqe": user.rqe,
        "photo_url": user.photo_url,
        "profession": user.profession,
        "council_name": user.council_name,
        "council_number": user.council_number,
        "council_state": user.council_state,
        "cpf_mascarado": _cpf_mascarado(user.cpf),
        "birth_date": user.birth_date,
        "created_at": user.created_at,
        # Endereços completos (Tarefa 29) — usados no cabeçalho/rodapé de
        # receita e documento, à escolha do médico na hora de emitir.
        "home_street": user.home_street, "home_number": user.home_number,
        "home_complement": user.home_complement, "home_neighborhood": user.home_neighborhood,
        "home_city": user.home_city, "home_state": user.home_state, "home_zip": user.home_zip,
        "practice_street": user.practice_street, "practice_number": user.practice_number,
        "practice_complement": user.practice_complement, "practice_neighborhood": user.practice_neighborhood,
        "practice_city": user.practice_city, "practice_state": user.practice_state,
        "practice_zip": user.practice_zip, "practice_phone": user.practice_phone,
        "document_logo_url": user.document_logo_url,
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
    rqe: str | None = None

    # Endereços completos (Tarefa 29) — residencial e profissional, os dois
    # opcionais. `practice_phone` é exigido por lei para receita de
    # anabolizantes (Lei nº 9.965/2000); os demais servem para o
    # cabeçalho/rodapé de qualquer receita ou documento, à escolha do médico.
    home_street: str | None = None
    home_number: str | None = None
    home_complement: str | None = None
    home_neighborhood: str | None = None
    home_city: str | None = None
    home_state: str | None = None
    home_zip: str | None = None

    practice_street: str | None = None
    practice_number: str | None = None
    practice_complement: str | None = None
    practice_neighborhood: str | None = None
    practice_city: str | None = None
    practice_state: str | None = None
    practice_zip: str | None = None
    practice_phone: str | None = None

    @field_validator("full_name")
    @classmethod
    def _nome(cls, v: str) -> str:
        if len(v.strip().split()) < 2:
            raise ValueError("Informe nome completo.")
        return v.strip()

    @field_validator("council_state", "home_state", "practice_state")
    @classmethod
    def _uf(cls, v: str | None) -> str | None:
        if v is None or not v.strip():
            return None
        v = v.strip().upper()
        if v not in UFS:
            raise ValueError("Estado inválido — use a sigla (ex.: SP).")
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
    user.rqe = (dados.rqe or "").strip() or None

    user.home_street = (dados.home_street or "").strip() or None
    user.home_number = (dados.home_number or "").strip() or None
    user.home_complement = (dados.home_complement or "").strip() or None
    user.home_neighborhood = (dados.home_neighborhood or "").strip() or None
    user.home_city = (dados.home_city or "").strip() or None
    user.home_state = dados.home_state
    user.home_zip = (dados.home_zip or "").strip() or None

    user.practice_street = (dados.practice_street or "").strip() or None
    user.practice_number = (dados.practice_number or "").strip() or None
    user.practice_complement = (dados.practice_complement or "").strip() or None
    user.practice_neighborhood = (dados.practice_neighborhood or "").strip() or None
    user.practice_city = (dados.practice_city or "").strip() or None
    user.practice_state = dados.practice_state
    user.practice_zip = (dados.practice_zip or "").strip() or None
    user.practice_phone = (dados.practice_phone or "").strip() or None

    db.commit()
    db.refresh(user)
    return _perfil(user)


# --- foto de perfil --------------------------------------------------------
# Validação por assinatura de arquivo (magic bytes), não por Content-Type nem
# por extensão: os dois são informados pelo cliente e não provam nada sobre o
# conteúdo. Sem dependência de biblioteca de imagem — só os bytes iniciais.
ASSINATURAS = {
    b"\xff\xd8\xff": ".jpg",
    b"\x89PNG\r\n\x1a\n": ".png",
}
TAMANHO_MAXIMO = 3 * 1024 * 1024  # 3 MB


def _extensao_valida(conteudo: bytes) -> str | None:
    for assinatura, ext in ASSINATURAS.items():
        if conteudo.startswith(assinatura):
            return ext
    # WEBP: "RIFF" nos 4 primeiros bytes e "WEBP" nos bytes 8-12.
    if conteudo[:4] == b"RIFF" and conteudo[8:12] == b"WEBP":
        return ".webp"
    return None


@router.post("/me/foto")
async def enviar_foto(
    arquivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    conteudo = await arquivo.read(TAMANHO_MAXIMO + 1)
    if len(conteudo) > TAMANHO_MAXIMO:
        raise HTTPException(status_code=413, detail="A imagem precisa ter no máximo 3 MB.")
    if not conteudo:
        raise HTTPException(status_code=422, detail="Arquivo vazio.")

    extensao = _extensao_valida(conteudo)
    if extensao is None:
        raise HTTPException(status_code=422, detail="Envie uma imagem JPEG, PNG ou WEBP.")

    destino = Path(settings.uploads_dir) / "fotos"
    destino.mkdir(parents=True, exist_ok=True)

    # Nome derivado do id do usuário: um arquivo por pessoa, sem acumular lixo
    # a cada troca. O sufixo aleatório force o cache do navegador a recarregar.
    for antigo in destino.glob(f"{user.id}-*"):
        antigo.unlink(missing_ok=True)
    nome = f"{user.id}-{secrets.token_hex(4)}{extensao}"
    (destino / nome).write_bytes(conteudo)

    user.photo_url = f"/fotos/{nome}"
    db.commit()
    db.refresh(user)
    return _perfil(user)


@router.delete("/me/foto")
def remover_foto(db: Session = Depends(get_db), user: User = Depends(current_user)):
    destino = Path(settings.uploads_dir) / "fotos"
    for antigo in destino.glob(f"{user.id}-*"):
        antigo.unlink(missing_ok=True)
    user.photo_url = None
    db.commit()
    db.refresh(user)
    return _perfil(user)


# --- logo pessoal/do consultório, para receita e documento (Tarefa 29) -----
# Mesmo padrão de validação e armazenamento da foto de perfil acima — conceito
# diferente (vai impresso no papel timbrado, não aparece na interface).
@router.post("/me/logo")
async def enviar_logo(
    arquivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    conteudo = await arquivo.read(TAMANHO_MAXIMO + 1)
    if len(conteudo) > TAMANHO_MAXIMO:
        raise HTTPException(status_code=413, detail="A imagem precisa ter no máximo 3 MB.")
    if not conteudo:
        raise HTTPException(status_code=422, detail="Arquivo vazio.")

    extensao = _extensao_valida(conteudo)
    if extensao is None:
        raise HTTPException(status_code=422, detail="Envie uma imagem JPEG, PNG ou WEBP.")

    destino = Path(settings.uploads_dir) / "logos"
    destino.mkdir(parents=True, exist_ok=True)

    for antigo in destino.glob(f"{user.id}-*"):
        antigo.unlink(missing_ok=True)
    nome = f"{user.id}-{secrets.token_hex(4)}{extensao}"
    (destino / nome).write_bytes(conteudo)

    user.document_logo_url = f"/logos/{nome}"
    db.commit()
    db.refresh(user)
    return _perfil(user)


@router.delete("/me/logo")
def remover_logo(db: Session = Depends(get_db), user: User = Depends(current_user)):
    destino = Path(settings.uploads_dir) / "logos"
    for antigo in destino.glob(f"{user.id}-*"):
        antigo.unlink(missing_ok=True)
    user.document_logo_url = None
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
