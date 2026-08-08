"""Trilhas de estudo (Tarefa 11b).

Curadoria do que já existe: a trilha não cria conteúdo, ela propõe ordem e diz
por que cada etapa vem naquele ponto. O progresso é por médico e por trilha, e
guardado pelo slug da etapa — reordenar a trilha depois não reescreve o que a
pessoa já leu.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user
from app.models.study_track import StudyTrack, StudyTrackProgress
from app.models.user import User
from app.services.timeline_conhecimento import montar_timeline, temas_disponiveis

router = APIRouter(prefix="/api/trilhas", tags=["trilhas de estudo"])

# Onde cada tipo de etapa vive na interface. Fica aqui, e não no frontend, para
# uma trilha nova não exigir mudança de código na tela.
ROTA = {
    "documento": "/biblioteca/{slug}",
    "medicamento": "/medicamentos?slug={slug}",
    "estudo": "/estudos/{slug}",
    "calculadora": "/calculadoras/{slug}",
    "checklist": "/checklists",
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

    modelos = {"documento": Document, "medicamento": Drug,
               "estudo": ScientificStudy, "checklist": DischargeChecklist,
               "evidencia": EvidenceRecord, "caso_clinico": ClinicalCase}
    Modelo = modelos.get(item_type)
    if Modelo is None:
        return True  # calculadora vive em código, não em tabela
    item = db.query(Modelo).filter(Modelo.slug == slug).first()
    return bool(item and getattr(item, "published", False))


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


def _progresso(db: Session, user_id: int, track: StudyTrack) -> StudyTrackProgress | None:
    return db.query(StudyTrackProgress).filter(
        StudyTrackProgress.user_id == user_id, StudyTrackProgress.track_id == track.id
    ).first()


def _dump(db: Session, t: StudyTrack, prog: StudyTrackProgress | None, com_etapas: bool = True) -> dict:
    feitas = set((prog.concluidas if prog else []) or [])
    etapas = t.etapas or []
    d = {
        "slug": t.slug, "titulo": t.titulo, "tema": t.tema, "objetivo": t.objetivo,
        "nivel": t.nivel, "total_etapas": len(etapas),
        "concluidas": len([e for e in etapas if e.get("item_slug") in feitas]),
        "finalizada_em": prog.concluida_em if prog else None,
    }
    if com_etapas:
        d["etapas"] = [
            {**e,
             "titulo": _titulo(db, e.get("item_type"), e.get("item_slug")),
             "link": ROTA.get(e.get("item_type"), "").format(slug=e.get("item_slug")),
             "concluida": e.get("item_slug") in feitas,
             "disponivel": _disponivel(db, e.get("item_type"), e.get("item_slug"))}
            for e in etapas
        ]
        d["etapas_indisponiveis"] = len([e for e in d["etapas"] if not e["disponivel"]])
    return d


@router.get("")
def listar(db: Session = Depends(get_db), user: User = Depends(current_user)):
    ts = db.query(StudyTrack).filter(StudyTrack.published.is_(True)).order_by(StudyTrack.titulo).all()
    progressos = {
        progresso.track_id: progresso
        for progresso in db.query(StudyTrackProgress).filter(
            StudyTrackProgress.user_id == user.id,
            StudyTrackProgress.track_id.in_([track.id for track in ts]),
        ).all()
    } if ts else {}
    return [_dump(db, t, progressos.get(t.id), com_etapas=False) for t in ts]


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
        StudyTrack.slug == slug, StudyTrack.published.is_(True)
    ).first()
    if t is None:
        raise HTTPException(status_code=404, detail="Trilha não encontrada.")
    return _dump(db, t, _progresso(db, user.id, t))


class MarcarEtapa(BaseModel):
    item_slug: str
    concluida: bool = True


@router.post("/{slug}/progresso")
def marcar(slug: str, dados: MarcarEtapa,
           db: Session = Depends(get_db), user: User = Depends(current_user)):
    t = db.query(StudyTrack).filter(
        StudyTrack.slug == slug, StudyTrack.published.is_(True)
    ).first()
    if t is None:
        raise HTTPException(status_code=404, detail="Trilha não encontrada.")
    validos = {e.get("item_slug") for e in (t.etapas or [])}
    if dados.item_slug not in validos:
        raise HTTPException(status_code=422, detail="Esta etapa não pertence à trilha.")

    prog = _progresso(db, user.id, t)
    if prog is None:
        prog = StudyTrackProgress(user_id=user.id, track_id=t.id, concluidas=[])
        db.add(prog)

    feitas = set(prog.concluidas or [])
    feitas.add(dados.item_slug) if dados.concluida else feitas.discard(dados.item_slug)
    prog.concluidas = sorted(feitas)
    # A trilha se conclui sozinha quando a última etapa é marcada — não há botão
    # de "finalizar", porque a conclusão é consequência e não decisão.
    prog.concluida_em = datetime.now(timezone.utc) if feitas >= validos else None
    db.commit()
    return _dump(db, t, prog)
