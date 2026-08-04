import secrets
from datetime import date
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.core.security import create_access_token, current_user, hash_password, verify_password
from app.core.validators import UFS, cpf_valido, limpar_cpf
from app.models.user import User
from app.services import emails
from app.services.assinatura import catalogo
from app.services.professional_profile import (
    normalize_council, normalize_professional_title, profile_payload,
)

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
        "home_street": user.home_street, "home_number": user.home_number,
        "home_complement": user.home_complement, "home_neighborhood": user.home_neighborhood,
        "home_city": user.home_city, "home_state": user.home_state, "home_zip": user.home_zip,
        "practice_street": user.practice_street, "practice_number": user.practice_number,
        "practice_complement": user.practice_complement, "practice_neighborhood": user.practice_neighborhood,
        "practice_city": user.practice_city, "practice_state": user.practice_state,
        "practice_zip": user.practice_zip, "practice_phone": user.practice_phone,
        "document_logo_url": user.document_logo_url,
        **profile_payload(user),
        "boas_vindas_pendente": user.boas_vindas_pendente,
        "assinatura_metodo_preferido": user.assinatura_metodo_preferido,
    }


@router.get("/me")
def me(user: User = Depends(current_user)):
    return _perfil(user)


class DadosPessoais(BaseModel):
    """Dados que o próprio titular pode corrigir sem alterar sua identidade de acesso."""

    full_name: str
    profession: str | None = None
    council_name: str | None = None
    council_number: str | None = None
    council_state: str | None = None
    specialty: str | None = None
    rqe: str | None = None
    professional_title: str | None = None
    workplace_name: str | None = None
    workplace_department: str | None = None
    workplace_role: str | None = None
    workplace_notes: str | None = None
    include_workplace_on_documents: bool = False

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

    @field_validator("professional_title")
    @classmethod
    def _titulo(cls, v: str | None) -> str | None:
        return normalize_professional_title(v)

    @field_validator("council_name")
    @classmethod
    def _conselho(cls, v: str | None) -> str | None:
        return normalize_council(v)

    @field_validator("council_state", "home_state", "practice_state")
    @classmethod
    def _uf(cls, v: str | None) -> str | None:
        if v is None or not v.strip():
            return None
        v = v.strip().upper()
        if v not in UFS:
            raise ValueError("Estado inválido — use a sigla (ex.: SP).")
        return v


_ROTULOS_CADASTRO = {
    "full_name": "Nome completo",
    "profession": "Profissão",
    "council_name": "Conselho de classe",
    "council_number": "Número no conselho",
    "council_state": "UF do conselho",
    "specialty": "Especialidade",
    "rqe": "RQE",
    "professional_title": "Forma de tratamento",
    "workplace_name": "Local de trabalho",
    "workplace_department": "Setor/unidade",
    "workplace_role": "Cargo/função",
    "workplace_notes": "Informações profissionais",
    "include_workplace_on_documents": "Exibir local de trabalho nos documentos",
}
_CAMPOS_ENDERECO_RESIDENCIAL = (
    "home_street", "home_number", "home_complement", "home_neighborhood", "home_city", "home_state", "home_zip",
)
_CAMPOS_ENDERECO_PROFISSIONAL = (
    "practice_street", "practice_number", "practice_complement", "practice_neighborhood",
    "practice_city", "practice_state", "practice_zip", "practice_phone",
)


def _perfil_profissional_completo(user: User) -> bool:
    """Só libera o primeiro acesso quando a identificação profissional é utilizável."""
    nome = (user.full_name or "").strip()
    nome_normalizado = nome.casefold()
    nome_real = len(nome.split()) >= 2 and nome_normalizado not in {
        "novo usuário", "nova usuária", "usuário provisório", "usuária provisória",
    }
    return bool(
        nome_real
        and (user.profession or "").strip()
        and (user.council_name or "").strip()
        and (user.council_number or "").strip()
        and (user.council_state or "").strip()
    )


@router.patch("/me")
def atualizar_me(dados: DadosPessoais, background_tasks: BackgroundTasks,
                 db: Session = Depends(get_db), user: User = Depends(current_user)):
    antes = {campo: getattr(user, campo) for campo in _ROTULOS_CADASTRO}
    endereco_residencial_antes = tuple(getattr(user, c) for c in _CAMPOS_ENDERECO_RESIDENCIAL)
    endereco_profissional_antes = tuple(getattr(user, c) for c in _CAMPOS_ENDERECO_PROFISSIONAL)

    user.full_name = dados.full_name
    user.profession = (dados.profession or "").strip() or None
    user.council_name = (dados.council_name or "").strip().upper() or None
    user.council_number = (dados.council_number or "").strip() or None
    user.council_state = dados.council_state
    user.specialty = (dados.specialty or "").strip() or None
    user.rqe = (dados.rqe or "").strip() or None
    user.professional_title = dados.professional_title
    user.workplace_name = (dados.workplace_name or "").strip() or None
    user.workplace_department = (dados.workplace_department or "").strip() or None
    user.workplace_role = (dados.workplace_role or "").strip() or None
    user.workplace_notes = (dados.workplace_notes or "").strip() or None
    user.include_workplace_on_documents = dados.include_workplace_on_documents

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

    user.profile_completion_required = not _perfil_profissional_completo(user)

    mudancas = [
        {"campo": rotulo, "antigo": antes[campo], "novo": getattr(user, campo)}
        for campo, rotulo in _ROTULOS_CADASTRO.items()
        if antes[campo] != getattr(user, campo)
    ]
    if endereco_residencial_antes != tuple(getattr(user, c) for c in _CAMPOS_ENDERECO_RESIDENCIAL):
        mudancas.append({"campo": "Endereço residencial", "antigo": None, "novo": "atualizado"})
    if endereco_profissional_antes != tuple(getattr(user, c) for c in _CAMPOS_ENDERECO_PROFISSIONAL):
        mudancas.append({"campo": "Endereço profissional", "antigo": None, "novo": "atualizado"})

    db.commit()
    db.refresh(user)
    if mudancas:
        background_tasks.add_task(emails.enviar_alteracao_cadastro, user.id, mudancas)
    return _perfil(user)


@router.post("/me/boas-vindas-vista")
def marcar_boas_vindas_vista(db: Session = Depends(get_db), user: User = Depends(current_user)):
    """Fecha o popup de boas-vindas pessoal de vez."""
    user.boas_vindas_pendente = False
    db.commit()
    return {"boas_vindas_pendente": False}


class PreferenciaAssinatura(BaseModel):
    metodo: str | None = None


@router.patch("/me/assinatura")
def atualizar_preferencia_assinatura(dados: PreferenciaAssinatura, db: Session = Depends(get_db),
                                     user: User = Depends(current_user)):
    if dados.metodo is not None and catalogo.info(dados.metodo) is None:
        raise HTTPException(status_code=422, detail=f"Método de assinatura desconhecido: {dados.metodo}")
    user.assinatura_metodo_preferido = dados.metodo
    db.commit()
    db.refresh(user)
    return _perfil(user)


ASSINATURAS = {
    b"\xff\xd8\xff": ".jpg",
    b"\x89PNG\r\n\x1a\n": ".png",
}
TAMANHO_MAXIMO = 3 * 1024 * 1024


def _extensao_valida(conteudo: bytes) -> str | None:
    for assinatura, ext in ASSINATURAS.items():
        if conteudo.startswith(assinatura):
            return ext
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
