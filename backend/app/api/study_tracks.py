"""Trilhas de estudo (Tarefa 11b).

Curadoria do que já existe: a trilha não cria conteúdo, ela propõe ordem e diz
por que cada etapa vem naquele ponto. O progresso é por médico e por trilha, e
guardado pelo slug da etapa — reordenar a trilha depois não reescreve o que a
pessoa já leu.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user
from app.models.study_track import StudyTrack, StudyTrackProgress
from app.models.user import User

router = APIRouter(prefix="/api/trilhas", tags=["trilhas de estudo"])

# Onde cada tipo de etapa vive na interface. Fica aqui, e não no frontend, para
# uma trilha nova não exigir mudança de código na tela.
ROTA = {
    "documento": "/biblioteca/{slug}",
    "medicamento": "/medicamentos?slug={slug}",
    "estudo": "/estudos/{slug}",
    "calculadora": "/calculadoras/{slug}",
    "checklist": "/checklists",
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
    from app.models.content import Document
    from app.models.drug import Drug
    from app.models.study import ScientificStudy

    modelos = {"documento": Document, "medicamento": Drug,
               "estudo": ScientificStudy, "checklist": DischargeChecklist}
    Modelo = modelos.get(item_type)
    if Modelo is None:
        return True  # calculadora vive em código, não em tabela
    item = db.query(Modelo).filter(Modelo.slug == slug).first()
    return bool(item and getattr(item, "published", False))


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
