"""Trilhas de estudo (Tarefa 11b).

Curadoria do que já existe: a trilha não cria conteúdo, ela propõe ordem e diz
por que cada etapa vem naquele ponto. O progresso é por médico e por trilha, e
guardado pela identidade estável ``item_type:item_slug`` — reordenar a trilha
depois não reescreve o que a pessoa já leu, e conteúdos de tipos diferentes
podem compartilhar slug sem compartilhar estado.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user
from app.models.study_track import StudyTrack, StudyTrackProgress
from app.models.user import User
from app.services.study_slug_aliases import canonical_study_slug
from app.services.study_track_progress import (
    STAGE_TYPES,
    canonical_stage_slug,
    completed_stage_ids,
    expand_legacy_progress_tokens,
    split_stage_identity,
    stage_identity,
)
from app.services.timeline_conhecimento import montar_timeline, temas_disponiveis

router = APIRouter(prefix="/api/trilhas", tags=["trilhas de estudo"])

# Onde cada tipo de etapa vive na interface. Fica aqui, e não no frontend, para
# uma trilha nova não exigir mudança de código na tela.
ROTA = {
    "documento": "/biblioteca/{slug}",
    "medicamento": "/medicamentos?slug={slug}",
    "estudo": "/estudos/{slug}",
    "calculadora": "/calculadoras/{slug}",
    "checklist": "/checklists/{slug}",
    "evidencia": "/evidencias/{slug}",
    "caso_clinico": "/casos-clinicos/{slug}",
}



def _disponivel(db: Session, item_type: str, slug: str) -> bool:
    """A etapa aponta para conteúdo que o assinante consegue abrir agora?

    Existir e estar no ar são coisas diferentes. O carregador valida existência
    — impede trilha com slug digitado errado —, mas conteúdo em revisão continua
    despublicado, e uma etapa clicável que devolve 404 quebra a confiança na
    trilha inteira. Melhor mostrar a etapa marcada como indisponível do que
    escondê-la: a curadoria continua legível, e fica claro que falta publicar,
    não que falta conteúdo.
    """
    from app.models.checklist import DischargeChecklist
    from app.models.clinical_case import ClinicalCase
    from app.models.content import Document
    from app.models.drug import Drug
    from app.models.evidence import EvidenceRecord
    from app.models.study import ScientificStudy

    if item_type == "calculadora":
        from app.services.calculators import REGISTRY

        return slug in REGISTRY

    modelos = {"documento": Document, "medicamento": Drug,
               "estudo": ScientificStudy, "checklist": DischargeChecklist,
               "evidencia": EvidenceRecord, "caso_clinico": ClinicalCase}
    Modelo = modelos.get(item_type)
    if Modelo is None:
        return False
    item = db.query(Modelo).filter(Modelo.slug == slug).first()
    return bool(
        item
        and getattr(item, "published", False)
        and getattr(item, "review_status", None) == "revisado"
    )


def _titulo(db: Session, item_type: str, slug: str) -> str | None:
    """Título de verdade do item referenciado pela etapa.

    Achado em 07/08/2026: a etapa nunca carregou título nenhum — nem no JSON de
    origem, nem em campo calculado aqui. O frontend preenchia a lacuna sozinho,
    mostrando `item_slug.replace("-", " ")` — daí títulos como "Aneurisma De
    Aorta Toracica Cortes Por Etiologia E Seguimento Esc 2024": sem acento
    (o slug nunca tem), com capitalização de toda palavra (inclusive artigo e
    preposição) e sigla espremida no meio ("Esc 2024" em vez de "ESC 2024").
    Busca o título real na tabela do item, mesmo critério de `_disponivel()`.
    """
    from app.models.checklist import DischargeChecklist
    from app.models.clinical_case import ClinicalCase
    from app.models.content import Document
    from app.models.drug import Drug
    from app.models.evidence import EvidenceRecord
    from app.models.study import ScientificStudy
    from app.services.calculators import REGISTRY

    if item_type == "calculadora":
        calc = REGISTRY.get(slug)
        return calc.name if calc else None

    # Campo que funciona como título em cada tabela — nem todas têm `title`.
    # `evidencia` não tem título próprio: o enunciado (`statement`) é o que a
    # própria tela de Evidências usa como cabeçalho do card.
    modelos_e_campo = {
        "documento": (Document, "title"),
        "medicamento": (Drug, "generic_name"),
        "estudo": (ScientificStudy, "title"),
        "checklist": (DischargeChecklist, "condicao"),
        "evidencia": (EvidenceRecord, "statement"),
        "caso_clinico": (ClinicalCase, "titulo"),
    }
    par = modelos_e_campo.get(item_type)
    if par is None:
        return None
    Modelo, campo = par
    item = db.query(Modelo).filter(Modelo.slug == slug).first()
    return getattr(item, campo) if item else None


def _progresso(
    db: Session,
    user_id: int,
    track: StudyTrack,
    *,
    lock: bool = False,
) -> StudyTrackProgress | None:
    query = db.query(StudyTrackProgress).filter(
        StudyTrackProgress.user_id == user_id, StudyTrackProgress.track_id == track.id
    )
    if lock:
        query = query.with_for_update()
    return query.first()


def _dump(db: Session, t: StudyTrack, prog: StudyTrackProgress | None, com_etapas: bool = True) -> dict:
    # Compatibilidade imediata: aliases podem ser reconciliados em lote, mas
    # slugs legados também são reconhecidos sem exigir migração destrutiva. A
    # primeira escrita dessa trilha persiste as identidades compostas.
    etapas = t.etapas or []
    feitas = completed_stage_ids(prog.concluidas if prog else [], etapas)
    identidades = [
        stage_identity(str(etapa.get("item_type") or ""), str(etapa.get("item_slug") or ""))
        for etapa in etapas
    ]
    concluida_atualmente = bool(identidades) and all(
        identidade in feitas for identidade in identidades
    )
    conclusao_historica_em = prog.concluida_em if prog else None
    d = {
        "slug": t.slug, "titulo": t.titulo, "tema": t.tema, "objetivo": t.objetivo,
        "nivel": t.nivel, "total_etapas": len(etapas),
        "concluidas": len([identidade for identidade in identidades if identidade in feitas]),
        # Compatibilidade: clientes antigos tratavam ``finalizada_em`` como o
        # estado atual. O timestamp historico so aparece aqui enquanto todas as
        # etapas vigentes continuam concluidas. Clientes novos devem usar o
        # booleano explicito e podem exibir separadamente o primeiro termino.
        "finalizada_em": conclusao_historica_em if concluida_atualmente else None,
        "concluida_atualmente": concluida_atualmente,
        "conclusao_historica_em": conclusao_historica_em,
    }
    if com_etapas:
        d["etapas"] = [
            {**e,
             "etapa_id": stage_identity(e.get("item_type"), e.get("item_slug")),
             "titulo": _titulo(db, e.get("item_type"), e.get("item_slug")),
             "link": ROTA.get(e.get("item_type"), "").format(slug=e.get("item_slug")),
             "concluida": stage_identity(e.get("item_type"), e.get("item_slug")) in feitas,
             "disponivel": _disponivel(db, e.get("item_type"), e.get("item_slug"))}
            for e in etapas
        ]
        d["etapas_indisponiveis"] = len([e for e in d["etapas"] if not e["disponivel"]])
    return d


@router.get("")
def listar(
    limit: int = Query(60, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(current_user),
):
    query = db.query(StudyTrack).filter(
        StudyTrack.published.is_(True), StudyTrack.review_status == "revisado"
    )
    total = query.count()
    ts = query.order_by(StudyTrack.titulo).offset(offset).limit(limit).all()
    progressos = {
        progresso.track_id: progresso
        for progresso in db.query(StudyTrackProgress).filter(
            StudyTrackProgress.user_id == user.id,
            StudyTrackProgress.track_id.in_([track.id for track in ts]),
        ).all()
    } if ts else {}
    items = [_dump(db, t, progressos.get(t.id), com_etapas=False) for t in ts]
    return {
        "total": total, "limit": limit, "offset": offset,
        "next_offset": offset + len(items) if offset + len(items) < total else None,
        "has_more": offset + len(items) < total,
        "items": items,
    }


# --- Timeline de evolução do conhecimento por doença (tarefa #53) ----------
# Declaradas ANTES de `/{slug}` de propósito: "/timeline" e "/timeline/temas"
# têm o mesmo formato de caminho que o `/{slug}` genérico logo abaixo
# (um ou dois segmentos depois do prefixo `/api/trilhas`), e o FastAPI
# resolve por ORDEM DE DECLARAÇÃO — se o catch-all viesse primeiro, uma
# chamada a `/api/trilhas/timeline` seria interpretada como `slug="timeline"`
# e devolveria 404 em vez de acionar esta rota.

@router.get("/timeline/temas")
def timeline_temas(db: Session = Depends(get_db), _: User = Depends(current_user)):
    """Temas com marco publicado (evidência ou estudo), para o seletor da
    tela de timeline — nunca lista tema sem nenhum conteúdo."""
    return temas_disponiveis(db)


@router.get("/timeline")
def timeline(
    tema: str = Query(..., min_length=1, max_length=120),
    db: Session = Depends(get_db),
    _: User = Depends(current_user),
):
    """Marcos (evidências + estudos publicados) do tema, em ordem
    cronológica — ver `app.services.timeline_conhecimento` para a decisão de
    arquitetura (derivada dos dados existentes, sem tabela nova)."""
    return montar_timeline(db, tema)


@router.get("/{slug}")
def detalhe(slug: str, db: Session = Depends(get_db), user: User = Depends(current_user)):
    t = db.query(StudyTrack).filter(
        StudyTrack.slug == slug,
        StudyTrack.published.is_(True),
        StudyTrack.review_status == "revisado",
    ).first()
    if t is None:
        raise HTTPException(status_code=404, detail="Trilha não encontrada.")
    return _dump(db, t, _progresso(db, user.id, t))


class MarcarEtapa(BaseModel):
    item_slug: str
    item_type: str | None = None
    etapa_id: str | None = None
    concluida: bool = True


def _resolver_etapa(t: StudyTrack, dados: MarcarEtapa) -> tuple[dict, str]:
    """Resolve payload novo ou legado sem voltar a aceitar ambiguidade."""
    etapas = t.etapas or []
    identidade_solicitada: str | None = None

    if dados.etapa_id:
        parsed = split_stage_identity(dados.etapa_id)
        if parsed is None:
            raise HTTPException(status_code=422, detail="Identidade de etapa inválida.")
        tipo_id, slug_id = parsed
        if dados.item_type and dados.item_type != tipo_id:
            raise HTTPException(status_code=422, detail="Tipo e identidade da etapa não conferem.")
        if canonical_stage_slug(tipo_id, dados.item_slug) != slug_id:
            raise HTTPException(status_code=422, detail="Slug e identidade da etapa não conferem.")
        identidade_solicitada = stage_identity(tipo_id, slug_id)
    elif dados.item_type:
        if dados.item_type not in STAGE_TYPES:
            raise HTTPException(status_code=422, detail="Tipo de etapa inválido.")
        identidade_solicitada = stage_identity(dados.item_type, dados.item_slug)

    if identidade_solicitada is None:
        slug_legado = canonical_study_slug(dados.item_slug)
        candidatas = [
            etapa for etapa in etapas
            if canonical_stage_slug(
                str(etapa.get("item_type") or ""), str(etapa.get("item_slug") or "")
            ) == slug_legado
        ]
        if len(candidatas) > 1:
            raise HTTPException(
                status_code=422,
                detail="Este slug identifica mais de uma etapa; informe item_type ou etapa_id.",
            )
    else:
        candidatas = [
            etapa for etapa in etapas
            if stage_identity(
                str(etapa.get("item_type") or ""), str(etapa.get("item_slug") or "")
            ) == identidade_solicitada
        ]

    if len(candidatas) != 1:
        raise HTTPException(status_code=422, detail="Esta etapa não pertence à trilha.")
    etapa = candidatas[0]
    return etapa, stage_identity(etapa.get("item_type"), etapa.get("item_slug"))


@router.post("/{slug}/progresso")
def marcar(slug: str, dados: MarcarEtapa,
           db: Session = Depends(get_db), user: User = Depends(current_user)):
    t = db.query(StudyTrack).filter(
        StudyTrack.slug == slug,
        StudyTrack.published.is_(True),
        StudyTrack.review_status == "revisado",
    ).first()
    if t is None:
        raise HTTPException(status_code=404, detail="Trilha não encontrada.")
    etapa, etapa_id = _resolver_etapa(t, dados)
    if dados.concluida and not _disponivel(db, etapa.get("item_type"), etapa.get("item_slug")):
        raise HTTPException(
            status_code=409,
            detail="Esta etapa ainda não está publicada e não pode ser concluída.",
        )

    # A linha de progresso pode ainda nao existir. Bloquear a propria linha nao
    # resolveria a corrida entre dois INSERTs; a linha estavel do usuario
    # serializa as escritas desse usuario antes de consultar/criar o progresso.
    db.query(User).filter(User.id == user.id).with_for_update().one()
    prog = _progresso(db, user.id, t, lock=True)
    if prog is None:
        if not dados.concluida:
            db.commit()  # libera o lock sem criar uma linha vazia de progresso
            return _dump(db, t, None)
        prog = StudyTrackProgress(user_id=user.id, track_id=t.id, concluidas=[])
        db.add(prog)

    validos = {
        stage_identity(etapa_atual.get("item_type"), etapa_atual.get("item_slug"))
        for etapa_atual in (t.etapas or [])
    }
    feitas = set(expand_legacy_progress_tokens(prog.concluidas, t.etapas or []))
    concluida_antes = bool(validos) and feitas >= validos
    feitas.add(etapa_id) if dados.concluida else feitas.discard(etapa_id)
    prog.concluidas = sorted(feitas)
    concluida_agora = bool(validos) and feitas >= validos
    # ``concluida_em`` passa a ser o primeiro termino historico. Desmarcar ou
    # editar a trilha muda o estado atual calculado por ``_dump``, sem apagar a
    # informacao de que ela ja foi concluida. Repetir o mesmo PUT semantico via
    # POST permanece idempotente e nao reescreve o instante.
    if concluida_agora and not concluida_antes and prog.concluida_em is None:
        prog.concluida_em = datetime.now(timezone.utc)
    db.commit()
    return _dump(db, t, prog)
