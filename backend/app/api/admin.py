"""Curadoria editorial: o que a equipe assistencial pode ver."""

from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Response
from pydantic import BaseModel, field_validator
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import require_admin
from app.core.validators import cpf_mascarado, limpar_cpf
from app.models.agenda import GoogleTestUserRequest
from app.models.audit import AuditLog
from app.models.content import Document
from app.models.kyc import KycVerification
from app.models.subscription import Subscription
from app.models.user import User
from app.services import emails
from app.services.entitlement import acesso_administrativo_sem_pagamento, tem_acesso_ao_produto
from app.services.knowledge_graph import BackfillEmAndamento, backfill_mesmo_tema
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


class KycWaiversPayload(BaseModel):
    """Dispensas KYC por requisito, aplicáveis exclusivamente a Convidado."""
    professional_front: bool = False
    professional_back: bool = False
    personal_front: bool = False
    personal_back: bool = False
    personal_digital: bool = False
    selfie: bool = False

    def as_dict(self) -> dict[str, bool]:
        return {campo: bool(getattr(self, campo)) for campo in kyc_verificacao.WAIVER_FIELDS}


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
    # "normal" (fluxo de cobrança/KYC normal) | "convidado" (isento de
    # pagamento, KYC completo automático) | "investidor" (demonstração global
    # somente leitura, sem perfil/KYC). Um único campo de três valores garante
    # por construção que nunca existe convidado=true + investidor=true.
    tipo_acesso: str = "normal"
    kyc_waivers: KycWaiversPayload | None = None

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

    @field_validator("tipo_acesso")
    @classmethod
    def _tipo_acesso(cls, value: str) -> str:
        value = (value or "normal").strip().lower()
        if value not in ("normal", "convidado", "investidor"):
            raise ValueError('Tipo de acesso inválido — use "normal", "convidado" ou "investidor".')
        return value


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

    # ACCOUNT_ERASURE_HIDE_TOMBSTONES_V1
    q = db.query(User).filter(User.status != "excluido")
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
    from app.api.auth import _perfil_completo
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

    convidado = dados.tipo_acesso == "convidado"
    investidor = dados.tipo_acesso == "investidor"

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
        convidado=convidado, investidor=investidor,
        role=dados.role, password_hash=hash_password(dados.password), is_active=True,
    )
    # Fonte de verdade do primeiro acesso:
    # - Investidor nunca coleta/completa perfil e vai direto ao tour.
    # - Convidado criado pelo admin precisa completar dados pessoais +
    #   profissionais conforme `_perfil_completo`.
    # - Normal preserva o valor explícito do fluxo histórico.
    if investidor:
        novo.profile_completion_required = False
    elif convidado:
        novo.profile_completion_required = not _perfil_completo(novo)
    db.add(novo)
    db.flush()
    if dados.kyc_waivers is not None:
        if not convidado:
            raise HTTPException(status_code=422, detail="Dispensas KYC só podem ser configuradas para Convidado.")
        from app.models.kyc_waiver import KycRequirementWaiver
        linha = KycRequirementWaiver(owner_id=novo.id, **dados.kyc_waivers.as_dict())
        db.add(linha)
        db.flush()
        kyc_verificacao.reavaliar_convidado_com_dispensas(db, novo, admin_id=admin.id)
    db.add(AuditLog(
        user_id=admin.id, action="criar_usuario", entity="user",
        entity_id=str(novo.id),
        detail={
            "email": email, "role": dados.role, "tipo_acesso": dados.tipo_acesso,
            "kyc_waivers": dados.kyc_waivers.as_dict() if dados.kyc_waivers is not None else None,
        },
    ))
    db.commit()
    return {
        "id": novo.id, "email": novo.email, "full_name": novo.full_name, "role": novo.role,
        "tipo_acesso": dados.tipo_acesso, "convidado": novo.convidado, "investidor": novo.investidor,
    }


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
    if convidado and alvo.investidor:
        raise HTTPException(status_code=409, detail="Investidor e Convidado são tipos de acesso mutuamente exclusivos.")
    alvo.convidado = convidado
    db.flush()
    if convidado:
        kyc_verificacao.reavaliar_convidado_com_dispensas(db, alvo, admin_id=admin.id)
    db.add(AuditLog(
        user_id=admin.id, action="guest_access_granted" if convidado else "guest_access_revoked",
        entity="user", entity_id=str(alvo.id), detail={"email": alvo.email},
    ))
    db.commit()
    return {"id": alvo.id, "convidado": alvo.convidado}


def _dump_kyc_waivers(db: Session, user_id: int) -> dict[str, bool]:
    from app.models.kyc_waiver import KycRequirementWaiver
    linha = db.get(KycRequirementWaiver, user_id)
    if linha is None:
        return {campo: False for campo in kyc_verificacao.WAIVER_FIELDS}
    return {campo: bool(getattr(linha, campo)) for campo in kyc_verificacao.WAIVER_FIELDS}


@router.get("/users/{user_id}/kyc-waivers")
def obter_kyc_waivers(
    user_id: int, db: Session = Depends(get_db), _=Depends(require_admin),
):
    alvo = db.get(User, user_id)
    if alvo is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    return {"user_id": alvo.id, "convidado": alvo.convidado, "waivers": _dump_kyc_waivers(db, alvo.id)}


@router.put("/users/{user_id}/kyc-waivers")
def configurar_kyc_waivers(
    user_id: int, dados: KycWaiversPayload,
    db: Session = Depends(get_db), admin=Depends(require_admin),
):
    """Configura dispensas individuais de KYC para um Convidado.

    A alteração é reavaliada imediatamente no backend: se todos os requisitos
    remanescentes já estiverem satisfeitos, o KYC termina em ``aprovado``;
    retirar uma dispensa que torne um documento ausente obrigatório reabre o
    gate com ``reenvio_solicitado``.
    """
    from app.models.kyc_waiver import KycRequirementWaiver

    alvo = db.get(User, user_id)
    if alvo is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    if alvo.investidor:
        raise HTTPException(status_code=409, detail="Investidor não participa do fluxo de KYC.")
    if not alvo.convidado:
        raise HTTPException(status_code=409, detail="Dispensas KYC individuais são exclusivas de contas Convidado.")

    valores = dados.as_dict()
    linha = db.get(KycRequirementWaiver, alvo.id)
    if linha is None:
        linha = KycRequirementWaiver(owner_id=alvo.id, **valores)
        db.add(linha)
    else:
        for campo, valor in valores.items():
            setattr(linha, campo, valor)
    db.flush()
    registro = kyc_verificacao.reavaliar_convidado_com_dispensas(db, alvo, admin_id=admin.id)
    db.add(AuditLog(
        user_id=admin.id, action="kyc_waivers_updated", entity="user",
        entity_id=str(alvo.id), detail={"waivers": valores, "kyc_status": registro.status if registro else None},
    ))
    db.commit()
    return {
        "user_id": alvo.id,
        "convidado": True,
        "waivers": _dump_kyc_waivers(db, alvo.id),
        "kyc_status": registro.status if registro else None,
    }


@router.patch("/users/{user_id}/investidor")
def alternar_investidor(
    user_id: int, investidor: bool, db: Session = Depends(get_db), admin=Depends(require_admin)
):
    """Marca/desmarca uma conta como Investidor.

    É acesso de demonstração global somente leitura, sem checkout, cobrança,
    perfil ou KYC. Nunca eleva `role`; ao conceder, as invariantes do modelo
    fixam senha CorVIAOS, status aprovado, convidado=False e tour pendente.
    """
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


@router.post("/kyc/{item_id}/solicitar-reenvio")
def solicitar_reenvio_verificacao(
    item_id: int, dados: DecisaoKyc, db: Session = Depends(get_db), admin=Depends(require_admin),
):
    """Terceira decisão possível além de aprovar/rejeitar (11/08/2026, ficha
    administrativa do assinante) — para quando a submissão está quase certa
    e só falta um documento melhor (foto ilegível, borrada, cortada), sem
    ser uma recusa definitiva. Ver `KycVerification.status ==
    "reenvio_solicitado"` e `kyc_verificacao.solicitar_reenvio` — mesmo
    efeito de acesso de `rejeitar` (o assinante sai do conjunto que
    `liberado_para_uso` aceita até reenviar), rótulo e nota diferentes.

    Nunca sobrescreve o histórico de uma decisão anterior: como `aprovar`/
    `rejeitar`, esta rota só muda o `status` atual do registro (que É
    mutável — é o mesmo registro que o assinante reenvia por cima) e grava
    MAIS uma linha de `AuditLog`, nunca apagando as anteriores. Quem quiser
    a sequência completa de decisões usa `GET /admin/usuarios/{id}` — o
    histórico ali vem inteiro do `AuditLog`, não do estado atual da linha.
    """
    if not dados.nota or not dados.nota.strip():
        raise HTTPException(
            status_code=422,
            detail="Explique o que precisa ser reenviado — o assinante precisa saber o que corrigir.",
        )
    item = db.get(KycVerification, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Verificação não encontrada.")
    kyc_verificacao.solicitar_reenvio(db, item, admin, dados.nota.strip())
    db.add(AuditLog(
        user_id=admin.id, action="kyc_reenvio_solicitado", entity="kyc_verifications",
        entity_id=str(item_id), detail={"user_id": item.owner_id, "nota": dados.nota.strip()},
    ))
    db.commit()
    return {"id": item.id, "status": item.status}


# ---------------------------------------------------------------------------
# Ficha administrativa completa do assinante (11/08/2026, issue de
# estabilização pré-lançamento) — um único lugar para validar cadastro, KYC
# e assinatura de um usuário, para análise/decisão humana. Convive com
# `GET /admin/users` (sem paginação/busca, mantida como está — é a rota que
# `Admin.tsx`/`Shell.tsx` já usam para a fila de aprovação de cadastro e o
# contador de pendentes; refazer essas duas telas em cima da rota nova é
# trabalho de frontend, fora desta frente) e com `GET /admin/kyc` (fila de
# revisão pendente — a ficha aqui é "tudo sobre ESTE usuário", não fila).
#
# Nada aqui reimplementa a decisão de acesso: `tem_acesso_ao_produto()` e
# `acesso_administrativo_sem_pagamento()` (app/services/entitlement.py) são
# chamadas diretamente, nunca reconstruídas em paralelo.
# ---------------------------------------------------------------------------

_CONTA_STATUS_VALORES = {"pendente", "aprovado", "rejeitado"}
_KYC_STATUS_VALORES = {
    "aguardando_revisao", "liberado_conselho_ok", "liberado_sem_checagem",
    "aprovado", "rejeitado", "reenvio_solicitado", "sem_kyc",
}
_ASSINATURA_STATUS_VALORES = {
    "inativo", "ativo", "teste", "pendente", "inadimplente",
    "suspenso", "cancelado", "pausado", "sem_assinatura",
}
_ACOES_DECISAO_KYC = {"kyc_aprovado", "kyc_rejeitado", "kyc_reenvio_solicitado"}


def _linha_lista_usuario(u: User, kyc: KycVerification | None, sub: Subscription | None) -> dict:
    return {
        "id": u.id,
        "full_name": u.full_name,
        "email": u.email,
        "cpf_mascarado": cpf_mascarado(u.cpf),
        "profession": u.profession,
        "council_name": u.council_name,
        "council_name_other": u.council_name_other,
        "council_number": u.council_number,
        "council_state": u.council_state,
        "council_state_other": u.council_state_other,
        "created_at": u.created_at,
        "status": u.status,
        "convidado": u.convidado,
        "investidor": u.investidor,
        "kyc_status": kyc.status if kyc else None,
        "kyc_aprovado_em": kyc.aprovado_em if kyc else None,
        "kyc_liberado_em": kyc.liberado_em if kyc else None,
        "subscription_status": sub.status if sub else None,
        "subscription_plano": sub.plano if sub else None,
        "subscription_periodicidade": sub.periodicidade if sub else None,
    }


@router.get("/usuarios")
def listar_usuarios_ficha(
    q: str | None = Query(None, max_length=160, description="Nome, e-mail, CPF ou nº do conselho"),
    status: str | None = Query(None, description="Status da conta: pendente, aprovado ou rejeitado"),
    kyc_status: str | None = Query(None, description="Status do KYC, ou 'sem_kyc'"),
    subscription_status: str | None = Query(
        None, description="Status da assinatura (kind=meucardio), ou 'sem_assinatura'"
    ),
    convidado: bool | None = Query(None),
    investidor: bool | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    """Lista pesquisável e paginada, para o admin achar rápido o cadastro
    que precisa validar. Filtros combináveis — todo `AND`, nunca `OR` entre
    filtros diferentes (só `q` casa por `OR` entre os próprios campos de
    busca)."""
    if status is not None and status not in _CONTA_STATUS_VALORES:
        raise HTTPException(status_code=422, detail=f"status inválido. Use um de: {sorted(_CONTA_STATUS_VALORES)}")
    if kyc_status is not None and kyc_status not in _KYC_STATUS_VALORES:
        raise HTTPException(status_code=422, detail=f"kyc_status inválido. Use um de: {sorted(_KYC_STATUS_VALORES)}")
    if subscription_status is not None and subscription_status not in _ASSINATURA_STATUS_VALORES:
        raise HTTPException(
            status_code=422,
            detail=f"subscription_status inválido. Use um de: {sorted(_ASSINATURA_STATUS_VALORES)}",
        )

    query = db.query(User).filter(User.status != "excluido")
    if status:
        query = query.filter(User.status == status)
    if convidado is not None:
        query = query.filter(User.convidado.is_(convidado))
    if investidor is not None:
        query = query.filter(User.investidor.is_(investidor))
    if q and q.strip():
        termo = q.strip()
        termo_ilike = f"%{termo}%"
        condicoes = [
            User.full_name.ilike(termo_ilike),
            User.email.ilike(termo_ilike),
            User.council_number.ilike(termo_ilike),
            User.crm.ilike(termo_ilike),
        ]
        digitos = limpar_cpf(termo)
        if len(digitos) >= 3:
            condicoes.append(User.cpf.ilike(f"%{digitos}%"))
        query = query.filter(or_(*condicoes))
    if kyc_status:
        if kyc_status == "sem_kyc":
            query = query.filter(User.id.notin_(select(KycVerification.owner_id)))
        else:
            query = query.filter(
                User.id.in_(select(KycVerification.owner_id).where(KycVerification.status == kyc_status))
            )
    if subscription_status:
        sub_meucardio = select(Subscription.user_id).where(Subscription.kind == "meucardio")
        if subscription_status == "sem_assinatura":
            query = query.filter(User.id.notin_(sub_meucardio))
        else:
            query = query.filter(
                User.id.in_(sub_meucardio.where(Subscription.status == subscription_status))
            )

    total = query.count()
    usuarios = (
        query.order_by(User.created_at.desc(), User.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    ids = [u.id for u in usuarios]
    kyc_por_usuario: dict[int, KycVerification] = {}
    sub_por_usuario: dict[int, Subscription] = {}
    if ids:
        kyc_por_usuario = {
            k.owner_id: k
            for k in db.query(KycVerification).filter(KycVerification.owner_id.in_(ids)).all()
        }
        # Ordenado por id desc para o `setdefault` abaixo ficar com a
        # assinatura kind=meucardio mais recente de cada usuário quando
        # houver mais de uma (ex.: uma cancelada antiga + a atual).
        for s in (
            db.query(Subscription)
            .filter(Subscription.user_id.in_(ids), Subscription.kind == "meucardio")
            .order_by(Subscription.id.desc())
            .all()
        ):
            sub_por_usuario.setdefault(s.user_id, s)

    return {
        "items": [
            _linha_lista_usuario(u, kyc_por_usuario.get(u.id), sub_por_usuario.get(u.id))
            for u in usuarios
        ],
        "page": page,
        "page_size": page_size,
        "total": total,
        "has_more": page * page_size < total,
    }


def _dump_assinatura(s: Subscription) -> dict:
    """Nunca inclui segredo, cartão ou CVV — só os IDs do Stripe (o próprio
    dado sensível de pagamento nunca passa pelo nosso banco, é o Stripe quem
    guarda)."""
    return {
        "id": s.id,
        "kind": s.kind,
        "course_id": s.course_id,
        "plano": s.plano,
        "periodicidade": s.periodicidade,
        "status": s.status,
        "current_period_end": s.current_period_end,
        "stripe_customer_id": s.stripe_customer_id,
        "stripe_subscription_id": s.stripe_subscription_id,
        "last_event_at": s.last_event_at,
        "created_at": s.created_at,
        "updated_at": s.updated_at,
    }


def _dump_documentos_kyc(kyc: KycVerification) -> list[dict]:
    documentos = []
    for campo in sorted(_CAMPOS_DOCUMENTO):
        disponivel = getattr(kyc, campo, None) is not None
        documentos.append({
            "campo": campo,
            "disponivel": disponivel,
            "url": f"/api/admin/kyc/{kyc.id}/documento/{campo}" if disponivel else None,
        })
    return documentos


def _timeline_usuario(db: Session, alvo: User, kyc: KycVerification | None, assinaturas: list[Subscription]) -> list[dict]:
    """Todo `AuditLog` relacionado a este usuário — cadastro/decisão de
    acesso (`entity="user"`), KYC (`entity="kyc_verifications"`, pelo id do
    registro DELE — é 1:1 com o usuário, `owner_id` é `unique=True`) e
    assinatura (`entity="subscription"`, por todos os ids de `Subscription`
    que já existiram para ele, não só a atual). Cronológico, mais recente
    primeiro."""
    condicoes = [and_(AuditLog.entity == "user", AuditLog.entity_id == str(alvo.id))]
    if kyc is not None:
        condicoes.append(and_(AuditLog.entity == "kyc_verifications", AuditLog.entity_id == str(kyc.id)))
    ids_assinatura = [str(s.id) for s in assinaturas]
    if ids_assinatura:
        condicoes.append(and_(AuditLog.entity == "subscription", AuditLog.entity_id.in_(ids_assinatura)))

    entradas = (
        db.query(AuditLog)
        .filter(or_(*condicoes))
        .order_by(AuditLog.created_at.desc(), AuditLog.id.desc())
        .all()
    )
    autor_ids = {e.user_id for e in entradas if e.user_id}
    autores = (
        {u.id: u.full_name for u in db.query(User).filter(User.id.in_(autor_ids)).all()}
        if autor_ids else {}
    )
    return [
        {
            "id": e.id,
            "action": e.action,
            "entity": e.entity,
            "entity_id": e.entity_id,
            "detail": e.detail,
            "created_at": e.created_at,
            "admin_id": e.user_id,
            "admin_nome": autores.get(e.user_id) if e.user_id else None,
        }
        for e in entradas
    ]


def _dump_kyc_bloco(kyc: KycVerification | None, timeline: list[dict]) -> dict:
    if kyc is None:
        return {
            "existe": False, "id": None, "status": None,
            "criado_em": None, "atualizado_em": None,
            "liberado_em": None, "aprovado_em": None, "aprovado_por": None,
            "nota_revisao": None,
            "conselho_check_status": None, "conselho_check_detalhe": None, "conselho_check_em": None,
            "ultima_decisao": None,
            "documentos": [],
        }
    ultima = next(
        (e for e in timeline if e["entity"] == "kyc_verifications" and e["action"] in _ACOES_DECISAO_KYC),
        None,
    )
    ultima_decisao = None
    if ultima:
        ultima_decisao = {
            "action": ultima["action"],
            "em": ultima["created_at"],
            "admin_id": ultima["admin_id"],
            "admin_nome": ultima["admin_nome"],
            "nota": (ultima["detail"] or {}).get("nota"),
        }
    return {
        "existe": True,
        "id": kyc.id,
        "status": kyc.status,
        "criado_em": kyc.criado_em,
        "atualizado_em": kyc.atualizado_em,
        "liberado_em": kyc.liberado_em,
        "aprovado_em": kyc.aprovado_em,
        "aprovado_por": kyc.aprovado_por,
        "nota_revisao": kyc.nota_revisao,
        "conselho_check_status": kyc.conselho_check_status,
        "conselho_check_detalhe": kyc.conselho_check_detalhe,
        "conselho_check_em": kyc.conselho_check_em,
        "ultima_decisao": ultima_decisao,
        "documentos": _dump_documentos_kyc(kyc),
    }


def _origem_acesso(user: User, sub_meucardio: Subscription | None, tem_acesso: bool) -> str:
    """Rótulo de exibição, derivado da MESMA decisão que
    `tem_acesso_ao_produto()` já tomou — nunca uma segunda regra."""
    if user.role == "admin":
        return "admin"
    if user.convidado:
        return "convidado"
    if user.investidor:
        return "investidor"
    if tem_acesso and sub_meucardio is not None:
        return "assinatura_paga"
    return "sem_acesso"


@router.get("/usuarios/{user_id}")
def ficha_usuario(user_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    """A ficha administrativa completa — dados pessoais, dados
    profissionais, assinatura/billing, KYC (com link para cada documento,
    reaproveitando `GET /admin/kyc/{id}/documento/{campo}` já existente,
    nunca um segundo caminho de servir arquivo) e o histórico integral de
    `AuditLog` relacionado a este usuário."""
    alvo = db.get(User, user_id)
    if not alvo:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    kyc = db.query(KycVerification).filter(KycVerification.owner_id == alvo.id).first()
    assinaturas = (
        db.query(Subscription)
        .filter(Subscription.user_id == alvo.id)
        .order_by(Subscription.id.desc())
        .all()
    )
    sub_meucardio = next((s for s in assinaturas if s.kind == "meucardio"), None)

    timeline = _timeline_usuario(db, alvo, kyc, assinaturas)

    tem_acesso = tem_acesso_ao_produto(db, alvo)
    origem = _origem_acesso(alvo, sub_meucardio, tem_acesso)

    reviewed_by_nome = None
    if alvo.reviewed_by:
        revisor = db.get(User, alvo.reviewed_by)
        reviewed_by_nome = revisor.full_name if revisor else None

    return {
        "id": alvo.id,
        "full_name": alvo.full_name,
        "email": alvo.email,
        "cpf_mascarado": cpf_mascarado(alvo.cpf),
        "status": alvo.status,
        "role": alvo.role,
        "created_at": alvo.created_at,
        "conta": {
            "status": alvo.status,
            "is_active": alvo.is_active,
            "role": alvo.role,
            "reviewed_by": alvo.reviewed_by,
            "reviewed_by_nome": reviewed_by_nome,
            "reviewed_at": alvo.reviewed_at,
            "rejection_note": alvo.rejection_note,
            "created_at": alvo.created_at,
            "convidado": alvo.convidado,
            "investidor": alvo.investidor,
            "convidado_plano_preferido": alvo.convidado_plano_preferido,
            "profile_completion_required": alvo.profile_completion_required,
        },
        "dados_pessoais": {
            "full_name": alvo.full_name,
            "cpf": alvo.cpf,  # sem máscara — tela administrativa, autorização explícita
            "birth_date": alvo.birth_date,
            "email": alvo.email,
            "instagram_handle": alvo.instagram_handle,
            "endereco_residencial": {
                "street": alvo.home_street, "number": alvo.home_number,
                "complement": alvo.home_complement, "neighborhood": alvo.home_neighborhood,
                "city": alvo.home_city, "state": alvo.home_state, "zip": alvo.home_zip,
            },
        },
        "dados_profissionais": {
            "profession": alvo.profession,
            "council_name": alvo.council_name,
            "council_name_other": alvo.council_name_other,
            "council_number": alvo.council_number,
            "council_state": alvo.council_state,
            "council_state_other": alvo.council_state_other,
            "crm": alvo.crm,
            "rqe": alvo.rqe,
            "specialty": alvo.specialty,
            "professional_title": alvo.professional_title,
            "workplace_name": alvo.workplace_name,
            "workplace_department": alvo.workplace_department,
            "workplace_role": alvo.workplace_role,
            "workplace_notes": alvo.workplace_notes,
            "include_workplace_on_documents": alvo.include_workplace_on_documents,
            "endereco_profissional": {
                "street": alvo.practice_street, "number": alvo.practice_number,
                "complement": alvo.practice_complement, "neighborhood": alvo.practice_neighborhood,
                "city": alvo.practice_city, "state": alvo.practice_state, "zip": alvo.practice_zip,
                "phone": alvo.practice_phone,
            },
        },
        "assinatura": {
            "tem_acesso_ao_produto": tem_acesso,
            "origem_acesso": origem,
            "acesso_administrativo_sem_pagamento": acesso_administrativo_sem_pagamento(alvo),
            "assinatura_principal": _dump_assinatura(sub_meucardio) if sub_meucardio else None,
            "todas_assinaturas": [_dump_assinatura(s) for s in assinaturas],
        },
        "kyc": _dump_kyc_bloco(kyc, timeline),
        "historico": timeline,
    }


@router.post("/grafo/backfill")
def backfill_grafo_conhecimento(db: Session = Depends(get_db), admin=Depends(require_admin)):
    """Semeia/atualiza o Grafo de Conhecimento Clínico Universal a partir do
    metadado já publicado (issue #52, nova fase) — idempotente e
    não-destrutivo, pode ser chamado quantas vezes for preciso (ex.: depois
    de publicar conteúdo novo). Nunca toca em dado de paciente — só as
    frentes de conteúdo global já cobertas pelo allowlist do modelo."""
    # O log e a reconciliação participam da mesma transação: não existe
    # backfill bem-sucedido sem sua trilha administrativa correspondente.
    try:
        resultado = backfill_mesmo_tema(db, commit=False)
    except BackfillEmAndamento as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    db.add(AuditLog(
        user_id=admin.id, action="grafo_backfill", entity="knowledge_graph",
        detail=resultado,
    ))
    db.commit()
    return resultado
