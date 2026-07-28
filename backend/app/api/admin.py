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

    return {"GalleryImage": GalleryImage, "LabTest": LabTest,
            "EvidenceRecord": EvidenceRecord, "ScientificStudy": ScientificStudy,
            "Drug": Drug, "DischargeChecklist": DischargeChecklist,
            "StudyTrack": StudyTrack, "PatientMaterial": PatientMaterial,
            "EmergencyProtocol": EmergencyProtocol}[nome]


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


@router.post("/cursos/semear-exemplo")
def semear_curso_exemplo(_=Depends(require_admin)):
    """Cadastra o curso de demonstração `Corvia Curso`.

    Idempotente e sem conta conectada no Stripe, de modo que a rota de
    assinatura recusa a venda: curso de demonstração que aceitasse cartão
    cobraria de verdade em nome de um parceiro que não existe.
    """
    from app.services.seed_curso_exemplo import semear

    return semear()
