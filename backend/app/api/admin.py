"""Curadoria editorial: o que a equipe assistencial pode ver."""

from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Response
from pydantic import BaseModel, field_validator
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import require_admin
from app.models.agenda import GoogleTestUserRequest
from app.models.audit import AuditLog
from app.models.content import Document
from app.models.kyc import KycVerification
from app.models.user import User
from app.services import emails
from app.services.knowledge_graph import backfill_mesmo_tema
from app.services.kyc import verificacao as kyc_verificacao
from app.services.professional_profile import normalize_council, normalize_professional_title

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
    # Publicar não é revisar. Esta rota mexia no `review_status` junto, e como o
    # importador se recusava a rebaixar um documento já "revisado", publicar
    # carimbava a revisão de forma permanente e irreversível — 249/249
    # documentos constavam revisados sem que ninguém os tivesse conferido.
    # Quem decide o status de revisão é o front matter do arquivo, que é onde
    # a conferência de fato acontece.
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


# ------------------------------------------------- galeria, exames, etc. --
# As quatro frentes abaixo têm o conteúdo versionado em JSON no repositório e
# carregadores em app/services/carregar_*.py — mas os carregadores nasceram
# como scripts avulsos (`python -m ...`), sem nenhuma rota que os acionasse.
# Resultado: o conteúdo existia no disco e nunca chegava ao banco, e as quatro
# seções apareciam vazias na interface. Estas rotas fecham esse buraco, no
# mesmo formato do /import que já existe para os documentos de content/.

FRENTES = {
    "galeria": ("/galeria/metadados.json", "carregar_galeria", "GalleryImage"),
    "exames": ("/exames/metadados.json", "carregar_exames", "LabTest"),
    "evidencias": ("/evidencias/metadados.json", "carregar_evidencias", "EvidenceRecord"),
    "estudos": ("/estudos/metadados.json", "carregar_estudos", "ScientificStudy"),
    "medicamentos": ("/medicamentos/metadados.json", "carregar_drugs", "Drug"),
    "checklists": ("/checklists/metadados.json", "carregar_checklists", "DischargeChecklist"),
    "trilhas": ("/trilhas/metadados.json", "carregar_trilhas", "StudyTrack"),
    "material_paciente": ("/material-paciente/metadados.json",
                          "carregar_material_paciente", "PatientMaterial"),
    "emergencia": ("/emergencia/metadados.json", "carregar_emergencia", "EmergencyProtocol"),
    "casos_clinicos": ("/casos-clinicos/metadados.json", "carregar_casos_clinicos", "ClinicalCase"),
}


def _modelo(nome: str):
    from app.models.drug import Drug
    from app.models.evidence import EvidenceRecord
    from app.models.gallery import GalleryImage
    from app.models.lab_test import LabTest
    from app.models.checklist import DischargeChecklist
    from app.models.study_track import StudyTrack
    from app.models.study import ScientificStudy
    from app.models.patient_material import PatientMaterial
    from app.models.emergency import EmergencyProtocol
    from app.models.clinical_case import ClinicalCase

    return {"GalleryImage": GalleryImage, "LabTest": LabTest,
            "EvidenceRecord": EvidenceRecord, "ScientificStudy": ScientificStudy,
            "Drug": Drug, "DischargeChecklist": DischargeChecklist,
            "StudyTrack": StudyTrack, "PatientMaterial": PatientMaterial,
            "EmergencyProtocol": EmergencyProtocol, "ClinicalCase": ClinicalCase}[nome]


@router.post("/conteudo/carregar")
def carregar_conteudo(
    frente: str | None = Query(None, description="galeria|exames|evidencias|estudos; vazio = todas"),
    db: Session = Depends(get_db),
    user=Depends(require_admin),
):
    """Lê os JSON versionados e faz upsert por slug. Não publica nada: os itens
    entram com published=false e só aparecem na interface depois da rota de
    publicação abaixo — o checkpoint de revisão exigido para conteúdo clínico."""
    import importlib

    alvos = [frente] if frente else list(FRENTES)
    desconhecidas = [f for f in alvos if f not in FRENTES]
    if desconhecidas:
        raise HTTPException(status_code=422, detail=f"Frente desconhecida: {desconhecidas[0]}")

    resultado = {}
    for nome in alvos:
        caminho, modulo, _ = FRENTES[nome]
        try:
            mod = importlib.import_module(f"app.services.{modulo}")
            resultado[nome] = mod.carregar(caminho)
        except FileNotFoundError:
            resultado[nome] = {"erro": f"{caminho} não encontrado no container"}
        except Exception as e:  # noqa: BLE001 — uma frente com problema não derruba as outras
            resultado[nome] = {"erro": f"{type(e).__name__}: {e}"}

    db.add(AuditLog(user_id=user.id, action="carregar_conteudo", entity="conteudo",
                    detail=resultado))
    db.commit()
    return resultado


@router.get("/conteudo/pendentes")
def conteudo_pendente(db: Session = Depends(get_db), _=Depends(require_admin)):
    """Quantos itens de cada frente estão carregados e ainda não publicados,
    separados por review_status — é o que o Rafael olha antes de aprovar."""
    resumo = {}
    for nome, (_, _, modelo_nome) in FRENTES.items():
        Modelo = _modelo(modelo_nome)
        total = db.query(Modelo).count()
        publicados = db.query(Modelo).filter(Modelo.published.is_(True)).count()
        revisados_pendentes = (
            db.query(Modelo)
            .filter(Modelo.published.is_(False), Modelo.review_status == "revisado")
            .count()
        )
        resumo[nome] = {
            "total": total,
            "publicados": publicados,
            "nao_publicados": total - publicados,
            "nao_publicados_com_review_revisado": revisados_pendentes,
        }
    return resumo


class PublicacaoConteudo(BaseModel):
    frente: str
    slugs: list[str] | None = None       # vazio = todos os elegíveis da frente
    somente_revisados: bool = True       # não publica o que ainda está pendente_revisao
    publicar: bool = True                # false = tira do ar


@router.post("/conteudo/publicar")
def publicar_conteudo(
    dados: PublicacaoConteudo,
    db: Session = Depends(get_db),
    user=Depends(require_admin),
):
    """Publica ou despublica itens de uma frente.

    Despublicar existe porque a verificação de conteúdo já publicado encontra
    erro: um item que afirma a parede errada num ECG precisa sair do ar no
    mesmo momento em que o erro é identificado, sem esperar deploy nem SQL
    manual. Sem `slugs`, despublicar atingiria a frente inteira — por isso a
    lista é obrigatória nesse sentido."""
    if dados.frente not in FRENTES:
        raise HTTPException(status_code=422, detail=f"Frente desconhecida: {dados.frente}")
    if not dados.publicar and not dados.slugs:
        raise HTTPException(
            status_code=422,
            detail="Para despublicar, informe os slugs — despublicar a frente inteira "
                   "por engano tiraria todo o conteúdo do ar.",
        )

    Modelo = _modelo(FRENTES[dados.frente][2])
    query = db.query(Modelo).filter(Modelo.published.is_(not dados.publicar))
    if dados.slugs:
        query = query.filter(Modelo.slug.in_(dados.slugs))
    if dados.publicar and dados.somente_revisados:
        query = query.filter(Modelo.review_status == "revisado")

    itens = query.all()
    for item in itens:
        item.published = dados.publicar

    db.add(AuditLog(
        user_id=user.id, action="publicar" if dados.publicar else "despublicar",
        entity=dados.frente,
        detail={"quantidade": len(itens), "slugs": [i.slug for i in itens]},
    ))
    db.commit()
    chave = "publicados" if dados.publicar else "despublicados"
    return {"frente": dados.frente, chave: len(itens), "slugs": [i.slug for i in itens]}


# --------------------------------------------------------------- usuários --
# Duas portas de entrada: o admin cria uma conta já aprovada (rota abaixo), ou
# a pessoa se cadastra sozinha em /api/auth/solicitar-acesso e cai numa fila
# pendente — inativa, sem acesso a nada — até um admin conferir os dados
# profissionais (conselho de classe, número de registro) e aprovar.

class NovoUsuario(BaseModel):
    email: str
    full_name: str
    crm: str | None = None
    profession: str | None = None
    council_name: str | None = None
    council_number: str | None = None
    council_state: str | None = None
    specialty: str | None = None
    professional_title: str | None = None
    workplace_name: str | None = None
    workplace_department: str | None = None
    workplace_role: str | None = None
    workplace_notes: str | None = None
    include_workplace_on_documents: bool = False
    profile_completion_required: bool = False
    role: str = "medico"  # admin | medico | residente | leitor
    password: str

    @field_validator("professional_title")
    @classmethod
    def _title(cls, value: str | None) -> str | None:
        return normalize_professional_title(value)

    @field_validator("council_name")
    @classmethod
    def _council(cls, value: str | None) -> str | None:
        return normalize_council(value)

    @field_validator("council_state")
    @classmethod
    def _state(cls, value: str | None) -> str | None:
        value = (value or "").strip().upper()
        if value and (len(value) != 2 or not value.isalpha()):
            raise ValueError("UF inválida.")
        return value or None


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
        "council_state": u.council_state,
        "council_name_other": u.council_name_other, "council_state_other": u.council_state_other,
        "specialty": u.specialty,
        "professional_title": u.professional_title,
        "workplace_name": u.workplace_name,
        "workplace_department": u.workplace_department,
        "workplace_role": u.workplace_role,
        "workplace_notes": u.workplace_notes,
        "include_workplace_on_documents": u.include_workplace_on_documents,
        "profile_completion_required": u.profile_completion_required,
        "role": u.role, "status": u.status, "is_active": u.is_active,
        "rejection_note": u.rejection_note, "created_at": u.created_at,
        "convidado": u.convidado,
        "investidor": u.investidor,
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
        profession=(dados.profession or "").strip() or None,
        council_name=dados.council_name,
        council_number=(dados.council_number or "").strip() or None,
        council_state=dados.council_state,
        specialty=(dados.specialty or "").strip() or None,
        professional_title=dados.professional_title,
        workplace_name=(dados.workplace_name or "").strip() or None,
        workplace_department=(dados.workplace_department or "").strip() or None,
        workplace_role=(dados.workplace_role or "").strip() or None,
        workplace_notes=(dados.workplace_notes or "").strip() or None,
        include_workplace_on_documents=dados.include_workplace_on_documents,
        profile_completion_required=dados.profile_completion_required,
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


@router.patch("/users/{user_id}/convidado")
def alternar_convidado(
    user_id: int, convidado: bool, db: Session = Depends(get_db), admin=Depends(require_admin)
):
    """Marca/desmarca uma conta como médico convidado (08/08/2026, issue #52
    — entitlement reconhecido de imediato via `tem_acesso_ao_produto()`,
    sem depender de checkout). A submissão de KYC continua sendo aprovada
    automaticamente em vez de cair na fila de revisão manual. Reversível a
    qualquer momento; desmarcar não cancela retroativamente um KYC já
    liberado — só remove o acesso administrativo (a menos que o usuário
    também tenha assinatura paga em dia, caso em que continua com acesso
    por essa outra fonte, sem relação com este flag)."""
    from app.models.user import User

    alvo = db.get(User, user_id)
    if not alvo:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    alvo.convidado = convidado
    db.add(AuditLog(
        user_id=admin.id, action="guest_access_granted" if convidado else "guest_access_revoked",
        entity="user", entity_id=str(alvo.id), detail={"email": alvo.email},
    ))
    db.commit()
    return {"id": alvo.id, "convidado": alvo.convidado}


@router.patch("/users/{user_id}/investidor")
def alternar_investidor(
    user_id: int, investidor: bool, db: Session = Depends(get_db), admin=Depends(require_admin)
):
    """Marca/desmarca uma conta como investidor (issue #52) — acesso
    cortesia de demonstração via `tem_acesso_ao_produto()`, sem checkout,
    sem cobrança. Nunca eleva `role` (não vira admin), nunca exige KYC
    (`_kyc_required` trata investidor como isento — ver app/api/auth.py).
    Reversível a qualquer momento; desmarcar remove o acesso administrativo
    a menos que o usuário também tenha assinatura paga em dia."""
    from app.models.user import User

    alvo = db.get(User, user_id)
    if not alvo:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    alvo.investidor = investidor
    db.add(AuditLog(
        user_id=admin.id,
        action="investor_access_granted" if investidor else "investor_access_revoked",
        entity="user", entity_id=str(alvo.id), detail={"email": alvo.email},
    ))
    db.commit()
    return {"id": alvo.id, "investidor": alvo.investidor}


class NovaPreAutorizacaoConvidado(BaseModel):
    """Pedido do Rafael (08/08/2026): cadastrar a pré-autorização ANTES do
    convidado se registrar, por e-mail e/ou nome completo, escolhendo se
    esse convidado específico terá CorvIA Mail ou não. Ver
    `app/models/convidado_pre_autorizado.py` para o mecanismo completo."""

    email: str | None = None
    nome_completo: str | None = None
    incluir_corvia_mail: bool = True
    observacao: str | None = None

    @field_validator("email")
    @classmethod
    def _email(cls, v: str | None) -> str | None:
        v = (v or "").strip().lower()
        if not v:
            return None
        if "@" not in v:
            raise ValueError("E-mail inválido.")
        return v

    @field_validator("nome_completo")
    @classmethod
    def _nome(cls, v: str | None) -> str | None:
        v = (v or "").strip()
        return v or None


@router.post("/convidados-pre-autorizados", status_code=201)
def criar_pre_autorizacao_convidado(
    dados: NovaPreAutorizacaoConvidado, db: Session = Depends(get_db), admin=Depends(require_admin)
):
    """Cadastra a pré-autorização de um convidado por e-mail e/ou nome
    completo — quando ele se cadastrar em `POST /auth/solicitar-acesso`
    casando com esta linha, o acesso já libera automaticamente, sem
    precisar de nenhum clique manual depois. Só admin."""
    from app.models.convidado_pre_autorizado import ConvidadoPreAutorizado

    if not dados.email and not dados.nome_completo:
        raise HTTPException(
            status_code=422, detail="Informe pelo menos o e-mail ou o nome completo do convidado."
        )
    if dados.email and (
        db.query(ConvidadoPreAutorizado)
        .filter(ConvidadoPreAutorizado.email == dados.email, ConvidadoPreAutorizado.usado_em.is_(None))
        .first()
    ):
        raise HTTPException(status_code=409, detail="Já existe uma pré-autorização pendente com este e-mail.")

    linha = ConvidadoPreAutorizado(
        email=dados.email, nome_completo=dados.nome_completo,
        incluir_corvia_mail=dados.incluir_corvia_mail, observacao=dados.observacao,
        criado_por=admin.id,
    )
    db.add(linha)
    db.commit()
    db.refresh(linha)
    db.add(AuditLog(
        user_id=admin.id, action="criar_pre_autorizacao_convidado",
        entity="convidado_pre_autorizado", entity_id=str(linha.id),
        detail={"email": linha.email, "nome_completo": linha.nome_completo,
                "incluir_corvia_mail": linha.incluir_corvia_mail},
    ))
    db.commit()
    return _dump_pre_autorizacao(linha)


def _dump_pre_autorizacao(linha) -> dict:
    return {
        "id": linha.id, "email": linha.email, "nome_completo": linha.nome_completo,
        "incluir_corvia_mail": linha.incluir_corvia_mail, "observacao": linha.observacao,
        "criado_em": linha.criado_em, "usado_em": linha.usado_em,
        "usado_por_user_id": linha.usado_por_user_id,
    }


@router.get("/convidados-pre-autorizados")
def listar_pre_autorizacoes_convidado(db: Session = Depends(get_db), _=Depends(require_admin)):
    from app.models.convidado_pre_autorizado import ConvidadoPreAutorizado

    linhas = (
        db.query(ConvidadoPreAutorizado)
        .order_by(ConvidadoPreAutorizado.usado_em.is_(None).desc(), ConvidadoPreAutorizado.criado_em.desc())
        .all()
    )
    return [_dump_pre_autorizacao(l) for l in linhas]


@router.delete("/convidados-pre-autorizados/{pre_autorizacao_id}", status_code=204)
def revogar_pre_autorizacao_convidado(
    pre_autorizacao_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)
):
    """Só revoga pré-autorização ainda não usada — uma já consumida virou
    histórico de uma conta real, apagar aqui não desfaria o convite."""
    from app.models.convidado_pre_autorizado import ConvidadoPreAutorizado

    linha = db.get(ConvidadoPreAutorizado, pre_autorizacao_id)
    if not linha:
        raise HTTPException(status_code=404, detail="Pré-autorização não encontrada.")
    if linha.usado_em is not None:
        raise HTTPException(status_code=409, detail="Esta pré-autorização já foi usada — não é mais possível revogar.")
    db.add(AuditLog(
        user_id=admin.id, action="revogar_pre_autorizacao_convidado",
        entity="convidado_pre_autorizado", entity_id=str(linha.id),
        detail={"email": linha.email, "nome_completo": linha.nome_completo},
    ))
    db.delete(linha)
    db.commit()


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


@router.post("/cursos/semear-exemplo")
def semear_curso_exemplo(_=Depends(require_admin)):
    """Cadastra o curso de demonstração `Corvia Curso`.

    Idempotente e sem conta conectada no Stripe, de modo que a rota de
    assinatura recusa a venda: curso de demonstração que aceitasse cartão
    cobraria de verdade em nome de um parceiro que não existe.
    """
    from app.services.seed_curso_exemplo import semear

    return semear()


# ------------------------------------------------------- receituário (T27) --
# Não entra no dicionário FRENTES de propósito: aquelas rotas assumem que o
# modelo tem `published`, e dado regulatório não se publica — ele vale ou não
# vale. `/conteudo/pendentes` quebraria ao consultar Modelo.published.


@router.post("/receituario/carregar-listas")
def carregar_listas_controladas(db: Session = Depends(get_db), user=Depends(require_admin)):
    """Carrega as listas da Portaria 344/98 e semeia os tipos de receituário.

    Não liga nenhum tipo: `ativo` de registro existente é preservado, porque
    ligar o controle especial depende do SNCR e da assinatura digital, e é
    decisão humana — não efeito colateral de uma recarga."""
    from app.services.carregar_controlados import carregar

    resultado = carregar(db)
    db.add(AuditLog(user_id=user.id, action="carregar_listas_344",
                    entity="receituario", detail=resultado))
    db.commit()
    return resultado


# ------------------------------------------------- usuários online (31/07) --
# "Online" não é um campo gravado — é derivado no momento da consulta a
# partir de `last_seen_at` (atualizado com throttle em `current_user`, ver
# core/security.py). Uma janela de 5 minutos: maior que o throttle de 60s
# (senão todo mundo apareceria offline entre uma requisição e outra), curta o
# bastante para não mostrar como "online" quem fechou a aba há 20 minutos.
JANELA_ONLINE_SEGUNDOS = 300


@router.get("/usuarios-online")
def usuarios_online(db: Session = Depends(get_db), _=Depends(require_admin)):
    from app.models.user import User

    agora = datetime.now(timezone.utc)
    usuarios = (
        db.query(User)
        .filter(User.is_active.is_(True))
        .order_by(User.last_seen_at.is_(None), User.last_seen_at.desc())
        .all()
    )
    return [
        {
            "id": u.id,
            "full_name": u.full_name,
            "email": u.email,
            "role": u.role,
            "last_seen_at": u.last_seen_at,
            "online": bool(
                u.last_seen_at and (agora - u.last_seen_at).total_seconds() <= JANELA_ONLINE_SEGUNDOS
            ),
        }
        for u in usuarios
    ]


# ---------------------------------------------------------------------------
# Reclamação de spam contra a caixa do CorvIA Mail — trava de reputação de
# domínio (material-paciente-por-email-spec.md, "risco operacional", 02/08/2026)
# ---------------------------------------------------------------------------

LIMITE_RECLAMACOES_SUSPENSAO = 3


@router.post("/email-accounts/{account_id}/registrar-reclamacao")
def registrar_reclamacao_spam(account_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    """Reativa, não automática: não há webhook de bounce/reclamação do
    Mail360 verificado nesta sessão, então o incremento é manual — o admin
    (ou um processo que leia relatório do provedor) chama esta rota quando
    uma reclamação chega. Ao atingir o limite, `envio_material_suspenso`
    liga sozinho e bloqueia só o envio de material a paciente; o resto do
    CorvIA Mail continua funcionando normalmente."""
    from app.models.email_account import EmailAccount

    conta = db.get(EmailAccount, account_id)
    if conta is None:
        raise HTTPException(status_code=404, detail="Caixa não encontrada.")

    conta.reclamacoes_spam += 1
    suspenso_agora = False
    if conta.reclamacoes_spam >= LIMITE_RECLAMACOES_SUSPENSAO and not conta.envio_material_suspenso:
        conta.envio_material_suspenso = True
        suspenso_agora = True

    db.add(AuditLog(
        user_id=admin.id, action="registrar_reclamacao_spam", entity="email_accounts",
        entity_id=str(account_id),
        detail={"reclamacoes_spam": conta.reclamacoes_spam, "suspenso_agora": suspenso_agora},
    ))
    db.commit()
    return {
        "reclamacoes_spam": conta.reclamacoes_spam,
        "envio_material_suspenso": conta.envio_material_suspenso,
    }


@router.post("/email-accounts/{account_id}/reativar-envio-material")
def reativar_envio_material(account_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    """Contraparte manual da suspensão acima — decisão do admin, depois de
    investigar a causa das reclamações."""
    from app.models.email_account import EmailAccount

    conta = db.get(EmailAccount, account_id)
    if conta is None:
        raise HTTPException(status_code=404, detail="Caixa não encontrada.")

    conta.envio_material_suspenso = False
    conta.reclamacoes_spam = 0
    db.add(AuditLog(
        user_id=admin.id, action="reativar_envio_material", entity="email_accounts",
        entity_id=str(account_id), detail={},
    ))
    db.commit()
    return {"envio_material_suspenso": False, "reclamacoes_spam": 0}


# ---------------------------------------------------------------------------
# Fila de liberação manual de testador do Google (app OAuth em modo Testing,
# teto de 100 contas, sem API pra automatizar — ver GoogleTestUserRequest em
# app/models/agenda.py e o pré-cadastro em app/api/agenda_integrada.py).
# ---------------------------------------------------------------------------


@router.get("/google-teste")
def listar_pedidos_teste_google(
    status: str = Query("pendente"), db: Session = Depends(get_db), _=Depends(require_admin),
):
    query = db.query(GoogleTestUserRequest)
    if status:
        query = query.filter(GoogleTestUserRequest.status == status)
    itens = query.order_by(GoogleTestUserRequest.created_at.asc()).all()
    return [
        {
            "id": i.id, "user_id": i.user_id, "google_email": i.google_email,
            "status": i.status, "created_at": i.created_at, "liberado_em": i.liberado_em,
        }
        for i in itens
    ]


@router.post("/google-teste/{item_id}/liberar")
def liberar_pedido_teste_google(
    item_id: int, background_tasks: BackgroundTasks,
    db: Session = Depends(get_db), admin=Depends(require_admin),
):
    """Chamada DEPOIS que o admin já adicionou o e-mail como testador no
    Google Cloud Console (passo manual, fora deste sistema — não há API do
    Google pra isso). Aqui só registra e avisa o assinante."""
    item = db.get(GoogleTestUserRequest, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Pedido não encontrado.")
    if item.status == "liberado":
        raise HTTPException(status_code=409, detail="Este pedido já foi liberado.")

    item.status = "liberado"
    item.liberado_em = datetime.now(timezone.utc)
    item.liberado_por = admin.id
    db.add(AuditLog(
        user_id=admin.id, action="google_teste_liberado", entity="google_test_user_requests",
        entity_id=str(item_id), detail={"google_email": item.google_email, "user_id": item.user_id},
    ))
    db.commit()
    background_tasks.add_task(emails.enviar_google_teste_liberado, item.user_id, item.google_email)
    item.notificado_em = datetime.now(timezone.utc)
    db.commit()
    return {"id": item.id, "status": item.status, "liberado_em": item.liberado_em}


# ---------------------------------------------------------------------------
# Verificação de identidade pós-pagamento (Trabalho 11, 06/08/2026) —
# documentos e selfie do assinante, revisão definitiva do admin. A liberação
# automática (por CRM confirmado, quando a credencial existir, ou por
# ausência de checagem possível pra qualquer outro conselho — ver
# `council_check.py`) já deixa o assinante usar a Corvia antes desta
# revisão — aqui é a aprovação DEFINITIVA, que fecha o ciclo mesmo pra quem
# já foi liberado.
# ---------------------------------------------------------------------------

_CAMPOS_DOCUMENTO = {
    "doc_profissional_frente", "doc_profissional_verso",
    "doc_pessoal_frente", "doc_pessoal_verso", "doc_pessoal_digital", "selfie",
}


def _mime_por_assinatura(dados: bytes) -> str:
    if dados.startswith(b"%PDF-"):
        return "application/pdf"
    if dados.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if dados.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if dados.startswith(b"RIFF"):
        return "image/webp"
    return "application/octet-stream"


@router.get("/kyc")
def listar_verificacoes_pendentes(db: Session = Depends(get_db), _=Depends(require_admin)):
    """Fila de revisão definitiva. Para profissão sem checagem automática
    possível (todo conselho que não seja CRM — ver `council_check.py`), o
    profissional já está liberado (`status == "liberado_sem_checagem"`) e
    esta é a única validação que o registro dele recebe — por isso os
    dados de profissão/conselho vêm aqui, não só no cadastro."""
    itens = kyc_verificacao.listar_pendentes(db)
    usuarios = {
        u.id: u for u in db.query(User).filter(User.id.in_([i.owner_id for i in itens])).all()
    } if itens else {}
    return [
        {
            "id": i.id, "user_id": i.owner_id, "status": i.status,
            "conselho_check_status": i.conselho_check_status,
            "conselho_check_detalhe": i.conselho_check_detalhe,
            "profession": (usuarios[i.owner_id].profession if i.owner_id in usuarios else None),
            "council_name": (usuarios[i.owner_id].council_name if i.owner_id in usuarios else None),
            "council_number": (usuarios[i.owner_id].council_number if i.owner_id in usuarios else None),
            "council_state": (usuarios[i.owner_id].council_state if i.owner_id in usuarios else None),
            "tem_documento_digital": i.doc_pessoal_digital is not None,
            "criado_em": i.criado_em, "liberado_em": i.liberado_em,
        }
        for i in itens
    ]


@router.get("/kyc/{item_id}/documento/{campo}")
def ver_documento_kyc(item_id: int, campo: str, db: Session = Depends(get_db), admin=Depends(require_admin)):
    if campo not in _CAMPOS_DOCUMENTO:
        raise HTTPException(status_code=422, detail="Campo de documento desconhecido.")
    item = db.get(KycVerification, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Verificação não encontrada.")
    try:
        conteudo = kyc_verificacao.ler_documento(item, campo, item.owner_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Este documento não foi enviado.") from None
    db.add(AuditLog(
        user_id=admin.id, action="kyc_documento_visualizado", entity="kyc_verifications",
        entity_id=str(item_id), detail={"campo": campo},
    ))
    db.commit()
    return Response(content=conteudo, media_type=_mime_por_assinatura(conteudo))


class DecisaoKyc(BaseModel):
    nota: str | None = None


@router.post("/kyc/{item_id}/aprovar")
def aprovar_verificacao(item_id: int, dados: DecisaoKyc, db: Session = Depends(get_db), admin=Depends(require_admin)):
    item = db.get(KycVerification, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Verificação não encontrada.")
    kyc_verificacao.aprovar(db, item, admin, dados.nota)
    db.add(AuditLog(
        user_id=admin.id, action="kyc_aprovado", entity="kyc_verifications",
        entity_id=str(item_id), detail={"user_id": item.owner_id},
    ))
    db.commit()
    return {"id": item.id, "status": item.status}


@router.post("/kyc/{item_id}/rejeitar")
def rejeitar_verificacao(item_id: int, dados: DecisaoKyc, db: Session = Depends(get_db), admin=Depends(require_admin)):
    if not dados.nota or not dados.nota.strip():
        raise HTTPException(status_code=422, detail="Explique o motivo da rejeição — o assinante precisa saber o que corrigir.")
    item = db.get(KycVerification, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Verificação não encontrada.")
    kyc_verificacao.rejeitar(db, item, admin, dados.nota.strip())
    db.add(AuditLog(
        user_id=admin.id, action="kyc_rejeitado", entity="kyc_verifications",
        entity_id=str(item_id), detail={"user_id": item.owner_id, "nota": dados.nota.strip()},
    ))
    db.commit()
    return {"id": item.id, "status": item.status}


@router.post("/grafo/backfill")
def backfill_grafo_conhecimento(db: Session = Depends(get_db), admin=Depends(require_admin)):
    """Semeia/atualiza o Grafo de Conhecimento Clínico Universal a partir do
    metadado já publicado (issue #52, nova fase) — idempotente e
    não-destrutivo, pode ser chamado quantas vezes for preciso (ex.: depois
    de publicar conteúdo novo). Nunca toca em dado de paciente — só as
    frentes de conteúdo global já cobertas pelo allowlist do modelo."""
    resultado = backfill_mesmo_tema(db)
    db.add(AuditLog(
        user_id=admin.id, action="grafo_backfill", entity="knowledge_graph",
        detail=resultado,
    ))
    db.commit()
    return resultado
