import logging
import secrets
from datetime import date, datetime, timezone
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, field_validator, model_validator
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.core.security import create_access_token, current_user, hash_password, verify_password
from app.core.uploads import UploadRejected, atomic_write_bytes, validate_file
from app.core.validators import UFS, cpf_valido, limpar_cpf
from app.models.audit import AuditLog
from app.models.user import User
from app.services import emails, instagram_profile
from app.services.assinatura import catalogo
from app.services.professional_profile import (
    council_display, normalize_council, normalize_professional_title, profile_payload,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])
log = logging.getLogger("meucardio.auth")


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


def _kyc_required(db: Session, user: User) -> bool:
    """Gate de KYC obrigatório (Trabalho 12, 06/08/2026) — só se aplica a
    quem já paga a assinatura principal (`kind='meucardio'`, status em
    `ACESSO_LIBERADO`). Calculado toda vez, nunca persistido: diferente de
    `profile_completion_required`, o KYC pode mudar por ação de OUTRA
    pessoa (o Rafael aprovando pela fila do admin), então um valor
    guardado ficaria velho até o próximo `PATCH /me` do próprio médico."""
    from app.core.security import ACESSO_LIBERADO
    from app.models.subscription import Subscription
    from app.services.kyc import verificacao as kyc_verificacao

    if user.role == "admin":
        return False
    sub = (
        db.query(Subscription)
        .filter(Subscription.user_id == user.id, Subscription.kind == "meucardio")
        .order_by(Subscription.id)
        .first()
    )
    if sub is None or sub.status not in ACESSO_LIBERADO:
        return False
    return not kyc_verificacao.liberado_para_uso(kyc_verificacao.obter(db, user))


def _onboarding_pendente(db: Session, user: User) -> bool:
    """Tour guiado do primeiro acesso (Trabalho 13, 06/08/2026) — só depois
    do KYC estar resolvido, para as duas telas nunca disputarem o mesmo
    momento (o App.tsx checa perfil → KYC → tour, nessa ordem, mas calcular
    já considerando isso aqui evita depender só da ordem do frontend)."""
    if _kyc_required(db, user):
        return False
    if user.role == "admin":
        return False
    from app.core.security import ACESSO_LIBERADO
    from app.models.subscription import Subscription

    sub = (
        db.query(Subscription)
        .filter(Subscription.user_id == user.id, Subscription.kind == "meucardio")
        .order_by(Subscription.id)
        .first()
    )
    if sub is None or sub.status not in ACESSO_LIBERADO:
        return False
    return not user.onboarding_visto


def _perfil(db: Session, user: User) -> dict:
    nome_conselho_exibicao, estado_conselho_exibicao = council_display(user)
    return {
        "id": user.id, "email": user.email, "full_name": user.full_name,
        "role": user.role, "specialty": user.specialty,
        "council": f"{nome_conselho_exibicao} {user.council_number}/{estado_conselho_exibicao}"
                   if user.council_name else None,
        "crm": user.crm,
        "rqe": user.rqe,
        "photo_url": user.photo_url,
        "profession": user.profession,
        "council_name": user.council_name,
        "council_number": user.council_number,
        "council_state": user.council_state,
        "council_name_other": user.council_name_other,
        "council_state_other": user.council_state_other,
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
        "instagram_handle": user.instagram_handle,
        "instagram_photo_url": user.instagram_photo_url,
        **profile_payload(user),
        "boas_vindas_pendente": user.boas_vindas_pendente,
        "assinatura_metodo_preferido": user.assinatura_metodo_preferido,
        "kyc_required": _kyc_required(db, user),
        "onboarding_pendente": _onboarding_pendente(db, user),
    }


@router.get("/me")
def me(db: Session = Depends(get_db), user: User = Depends(current_user)):
    return _perfil(db, user)


class DadosPessoais(BaseModel):
    """Dados que o próprio titular pode corrigir sem alterar sua identidade de acesso."""

    full_name: str
    profession: str | None = None
    council_name: str | None = None
    council_number: str | None = None
    council_state: str | None = None
    # Preenchidos só quando council_name == "OUTRO" (08/08/2026, pedido do
    # Rafael) — ver o mesmo campo em SolicitacaoAcesso, mais abaixo.
    council_name_other: str | None = None
    council_state_other: str | None = None
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

    @field_validator("council_name_other", "council_state_other")
    @classmethod
    def _texto_livre_outro(cls, v: str | None) -> str | None:
        v = (v or "").strip()
        return v or None

    @model_validator(mode="after")
    def _campos_outro_coerentes(self) -> "DadosPessoais":
        if (self.council_name or "").strip().upper() == "OUTRO":
            if not self.council_name_other or not self.council_state_other:
                raise ValueError(
                    'Para conselho "Outro", informe qual é o conselho e o estado/região.'
                )
        return self


_ROTULOS_CADASTRO = {
    "full_name": "Nome completo",
    "profession": "Profissão",
    "council_name": "Conselho de classe",
    "council_number": "Número no conselho",
    "council_state": "UF do conselho",
    "council_name_other": "Nome do conselho (Outro)",
    "council_state_other": "Estado/região do conselho (Outro)",
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
    # "OUTRO" não tem UF de 2 letras que sirva — o par de campos livres
    # (conselho + estado/região) é quem completa a identificação aqui
    # (08/08/2026, pedido do Rafael). Qualquer outro conselho continua
    # exigindo a UF de sempre, sem mudança de comportamento.
    eh_outro = (user.council_name or "").strip().upper() == "OUTRO"
    estado_ok = (
        bool((user.council_name_other or "").strip()) and bool((user.council_state_other or "").strip())
        if eh_outro
        else bool((user.council_state or "").strip())
    )
    return bool(
        nome_real
        and (user.profession or "").strip()
        and (user.council_name or "").strip()
        and (user.council_number or "").strip()
        and estado_ok
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
    user.council_name_other = dados.council_name_other
    user.council_state_other = dados.council_state_other
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
    return _perfil(db, user)


@router.post("/me/boas-vindas-vista")
def marcar_boas_vindas_vista(db: Session = Depends(get_db), user: User = Depends(current_user)):
    """Fecha o popup de boas-vindas pessoal de vez."""
    user.boas_vindas_pendente = False
    db.commit()
    return {"boas_vindas_pendente": False}


@router.post("/me/onboarding-concluido")
def marcar_onboarding_concluido(db: Session = Depends(get_db), user: User = Depends(current_user)):
    """Fecha o tour guiado do primeiro acesso (Trabalho 13) de vez — tanto
    quem termina o tour quanto quem escolhe pular chegam aqui."""
    user.onboarding_visto = True
    db.commit()
    return {"onboarding_pendente": False}


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
    return _perfil(db, user)


TAMANHO_MAXIMO = 3 * 1024 * 1024

EXTENSAO_POR_MIME = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


def _validar_imagem_perfil(conteudo: bytes, nome_original: str | None) -> str:
    """Valida o arquivo também fora de produção e devolve extensão canônica.

    A camada ASGI faz a validação antecipada em produção. Repeti-la no router
    evita que execução local/testes aceitem apenas magic bytes e mantém uma
    única regra para JPEG, PNG e WEBP.
    """
    try:
        mime = validate_file(conteudo, nome_original or "imagem", "image")
    except UploadRejected as erro:
        raise HTTPException(status_code=erro.status_code, detail=erro.detail) from None
    return EXTENSAO_POR_MIME[mime]


def _remover_arquivos_antigos(diretorio: Path, user_id: int, *, preservar: Path | None = None) -> None:
    for antigo in diretorio.glob(f"{user_id}-*"):
        if preservar is not None and antigo == preservar:
            continue
        try:
            antigo.unlink(missing_ok=True)
        except OSError:
            # O banco já aponta apenas para o arquivo atual. Um órfão eventual
            # não pode transformar um upload bem-sucedido em erro ao usuário.
            log.warning("Não foi possível remover imagem de perfil obsoleta: %s", antigo)


def _publicar_imagem_perfil(
    *, conteudo: bytes, nome_original: str | None, subdiretorio: str,
    prefixo_publico: str, atributo: str, db: Session, user: User,
) -> dict:
    extensao = _validar_imagem_perfil(conteudo, nome_original)
    diretorio = Path(settings.uploads_dir) / subdiretorio
    nome = f"{user.id}-{secrets.token_hex(8)}{extensao}"

    try:
        # A imagem é lida por outro contêiner (Caddy) no volume compartilhado.
        arquivo_novo = atomic_write_bytes(diretorio, nome, conteudo, mode=0o644)
    except OSError:
        log.exception("Falha ao gravar imagem de perfil em %s", diretorio)
        raise HTTPException(
            status_code=503,
            detail="O armazenamento de imagens está temporariamente indisponível. Tente novamente.",
        ) from None

    setattr(user, atributo, f"/{prefixo_publico}/{nome}")
    try:
        db.commit()
        db.refresh(user)
    except SQLAlchemyError:
        db.rollback()
        arquivo_novo.unlink(missing_ok=True)
        log.exception("Falha ao salvar referência da imagem de perfil no banco")
        raise HTTPException(
            status_code=503,
            detail="Não foi possível concluir o upload agora. O arquivo anterior foi preservado.",
        ) from None

    # O arquivo anterior só é apagado depois da nova imagem e do banco estarem
    # confirmados. Assim uma falha no meio da troca nunca deixa o perfil vazio.
    _remover_arquivos_antigos(diretorio, user.id, preservar=arquivo_novo)
    return _perfil(db, user)


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

    return _publicar_imagem_perfil(
        conteudo=conteudo, nome_original=arquivo.filename,
        subdiretorio="fotos", prefixo_publico="fotos", atributo="photo_url",
        db=db, user=user,
    )


@router.delete("/me/foto")
def remover_foto(db: Session = Depends(get_db), user: User = Depends(current_user)):
    destino = Path(settings.uploads_dir) / "fotos"
    user.photo_url = None
    db.commit()
    db.refresh(user)
    _remover_arquivos_antigos(destino, user.id)
    return _perfil(db, user)


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

    return _publicar_imagem_perfil(
        conteudo=conteudo, nome_original=arquivo.filename,
        subdiretorio="logos", prefixo_publico="logos", atributo="document_logo_url",
        db=db, user=user,
    )


@router.delete("/me/logo")
def remover_logo(db: Session = Depends(get_db), user: User = Depends(current_user)):
    destino = Path(settings.uploads_dir) / "logos"
    user.document_logo_url = None
    db.commit()
    db.refresh(user)
    _remover_arquivos_antigos(destino, user.id)
    return _perfil(db, user)


class TrocaDeSenha(BaseModel):
    senha_atual: str
    nova_senha: str


@router.post("/alterar-senha")
def alterar_senha(dados: TrocaDeSenha, background_tasks: BackgroundTasks,
                  db: Session = Depends(get_db), user: User = Depends(current_user)):
    if not verify_password(dados.senha_atual, user.password_hash):
        raise HTTPException(status_code=400, detail="Senha atual incorreta.")
    if len(dados.nova_senha) < 8:
        raise HTTPException(status_code=422, detail="A nova senha precisa ter ao menos 8 caracteres.")
    if dados.nova_senha == dados.senha_atual:
        raise HTTPException(status_code=422, detail="A nova senha precisa ser diferente da atual.")
    user.password_hash = hash_password(dados.nova_senha)
    db.commit()
    background_tasks.add_task(emails.enviar_senha_alterada, user.id)
    return {"nota": "Senha alterada."}


class TrocaDeEmail(BaseModel):
    senha_atual: str
    novo_email: str

    @field_validator("novo_email")
    @classmethod
    def _email(cls, v: str) -> str:
        v = v.strip().lower()
        if "@" not in v:
            raise ValueError("E-mail inválido.")
        return v


@router.post("/trocar-email")
def trocar_email(dados: TrocaDeEmail, background_tasks: BackgroundTasks,
                 db: Session = Depends(get_db), user: User = Depends(current_user)):
    if not verify_password(dados.senha_atual, user.password_hash):
        raise HTTPException(status_code=400, detail="Senha atual incorreta.")
    if dados.novo_email == user.email:
        raise HTTPException(status_code=422, detail="Este já é o seu e-mail atual.")
    if db.query(User).filter(User.email == dados.novo_email).first():
        raise HTTPException(status_code=409, detail="Já existe uma conta com este e-mail.")

    email_antigo = user.email
    user.email = dados.novo_email
    db.commit()
    background_tasks.add_task(emails.enviar_troca_email, user.id, email_antigo, dados.novo_email)
    return {"nota": "E-mail alterado. Use o novo endereço para entrar a partir de agora."}


class SolicitacaoAcesso(BaseModel):
    full_name: str
    birth_date: date
    cpf: str
    profession: str
    council_name: str
    council_number: str
    # Opcional aqui de propósito: obrigatório só quando o conselho NÃO é
    # "Outro" (checado no model_validator abaixo, depois que council_name já
    # foi normalizado) — pra "Outro" quem manda é council_state_other, texto
    # livre, porque a UF de 2 letras não serve pra região não-brasileira.
    council_state: str | None = None
    # Preenchidos só quando council_name == "OUTRO" (08/08/2026, pedido do
    # Rafael): o nome real do conselho e o estado/região em texto livre.
    council_name_other: str | None = None
    council_state_other: str | None = None
    specialty: str | None = None
    professional_title: str | None = None
    workplace_name: str | None = None
    workplace_department: str | None = None
    workplace_role: str | None = None
    workplace_notes: str | None = None
    include_workplace_on_documents: bool = False
    # Opcional (tarefa #43, 08/08/2026) — o médico digita se quiser; nunca
    # buscado/adivinhado pelo sistema. Ver instagram_profile.py para a
    # busca best-effort da foto pública a partir DESTE handle específico.
    instagram_handle: str | None = None
    email: str
    password: str

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
    def _conselho(cls, v: str) -> str:
        return normalize_council(v) or "OUTRO"

    @field_validator("council_state")
    @classmethod
    def _uf(cls, v: str | None) -> str | None:
        if v is None or not v.strip():
            return None
        v = v.strip().upper()
        if v not in UFS:
            raise ValueError("Estado do conselho inválido — use a sigla (ex.: SP).")
        return v

    @field_validator("council_name_other", "council_state_other")
    @classmethod
    def _texto_livre_outro(cls, v: str | None) -> str | None:
        v = (v or "").strip()
        return v or None

    @field_validator("instagram_handle")
    @classmethod
    def _instagram(cls, v: str | None) -> str | None:
        v = (v or "").strip().lstrip("@")
        if not v:
            return None
        if len(v) > 30 or not all(c.isalnum() or c in "._" for c in v):
            raise ValueError(
                "Instagram inválido — use só letras, números, ponto e sublinhado, sem o @."
            )
        return v

    @field_validator("email")
    @classmethod
    def _email(cls, v: str) -> str:
        v = v.strip().lower()
        if "@" not in v:
            raise ValueError("E-mail inválido.")
        return v

    @model_validator(mode="after")
    def _conselho_outro_ou_uf(self) -> "SolicitacaoAcesso":
        # "OUTRO" pede o texto livre (conselho não identificável por sigla
        # fixa, estado/região pode nem ser brasileiro); qualquer outro
        # conselho continua exigindo a UF de sempre, sem mudança de
        # comportamento (08/08/2026, pedido do Rafael).
        if self.council_name == "OUTRO":
            if not self.council_name_other or not self.council_state_other:
                raise ValueError(
                    'Para conselho "Outro", informe qual é o conselho e o estado/região.'
                )
        elif self.council_state is None:
            raise ValueError("Estado do conselho inválido — use a sigla (ex.: SP).")
        return self


@router.post("/solicitar-acesso", status_code=201)
def solicitar_acesso(dados: SolicitacaoAcesso, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
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

    # Pré-autorização de convidado por e-mail (08/08/2026, pedido do Rafael):
    # um admin já cadastrou este e-mail em ConvidadoPreAutorizado ANTES do
    # cadastro acontecer — quando ele bate aqui, o usuário nasce já aprovado
    # e marcado como convidado, sem precisar de nenhum clique manual depois.
    # Consumo é único: `usado_em` trava a linha contra reaproveitamento.
    from app.models.convidado_pre_autorizado import ConvidadoPreAutorizado

    pre_autorizacao = (
        db.query(ConvidadoPreAutorizado)
        .filter(ConvidadoPreAutorizado.email == dados.email, ConvidadoPreAutorizado.usado_em.is_(None))
        .first()
    )
    convidado_via_pre_autorizacao = pre_autorizacao is not None

    novo = User(
        email=dados.email, full_name=dados.full_name, birth_date=dados.birth_date,
        cpf=cpf_limpo, profession=dados.profession.strip(),
        council_name=dados.council_name.strip().upper(), council_number=dados.council_number.strip(),
        council_state=dados.council_state,
        council_name_other=dados.council_name_other, council_state_other=dados.council_state_other,
        specialty=(dados.specialty or "").strip() or None,
        professional_title=dados.professional_title,
        workplace_name=(dados.workplace_name or "").strip() or None,
        workplace_department=(dados.workplace_department or "").strip() or None,
        workplace_role=(dados.workplace_role or "").strip() or None,
        workplace_notes=(dados.workplace_notes or "").strip() or None,
        include_workplace_on_documents=dados.include_workplace_on_documents,
        instagram_handle=dados.instagram_handle,
        password_hash=hash_password(dados.password),
        role="leitor" if not convidado_via_pre_autorizacao else "medico",
        status="pendente" if not convidado_via_pre_autorizacao else "aprovado",
        is_active=convidado_via_pre_autorizacao,
        convidado=convidado_via_pre_autorizacao,
    )
    if convidado_via_pre_autorizacao:
        novo.reviewed_at = datetime.now(timezone.utc)
    db.add(novo)
    db.commit()
    db.refresh(novo)

    if dados.instagram_handle:
        # Best-effort, nunca bloqueia a resposta do cadastro nem depende de
        # aprovação — é só uma foto pública, independente do fluxo de KYC.
        # Ver a limitação real documentada em app/services/instagram_profile.py.
        background_tasks.add_task(instagram_profile.buscar_e_salvar_foto, novo.id, dados.instagram_handle)

    if convidado_via_pre_autorizacao:
        pre_autorizacao.usado_em = datetime.now(timezone.utc)
        pre_autorizacao.usado_por_user_id = novo.id
        db.add(AuditLog(
            user_id=novo.id, action="convidado_via_pre_autorizacao", entity="user",
            entity_id=str(novo.id),
            detail={
                "email": novo.email,
                "pre_autorizacao_id": pre_autorizacao.id,
                "observacao": pre_autorizacao.observacao,
                "nota": "Cadastro aprovado e marcado convidado automaticamente — e-mail já "
                        "pré-autorizado por um admin antes do cadastro acontecer.",
            },
        ))
        db.commit()
        return {
            "nota": "Cadastro concluído! Seu acesso já está liberado — você pode entrar agora.",
            "acesso_imediato": True,
        }

    from app.services.notificar import notificar_admins_nova_solicitacao
    notificar_admins_nova_solicitacao(db, novo.full_name, novo.email)
    background_tasks.add_task(emails.enviar_solicitacao_recebida, novo.id)

    return {
        "nota": "Solicitação registrada. Você recebe acesso assim que um administrador "
                "conferir seus dados profissionais."
    }
