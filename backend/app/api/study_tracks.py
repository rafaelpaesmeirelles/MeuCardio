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


def _progresso(db: Session, user_id: int, track: StudyTrack) -> StudyTrackProgress | None:
    return db.query(StudyTrackProgress).filter(
        StudyTrackProgress.user_id == user_id, StudyTrackProgress.track_id == track.id
    ).first()


def _dump(t: StudyTrack, prog: StudyTrackProgress | None, com_etapas: bool = True) -> dict:
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
             "concluida": e.get("item_slug") in feitas}
            for e in etapas
        ]
    return d


@router.get("")
def listar(db: Session = Depends(get_db), user: User = Depends(current_user)):
    ts = db.query(StudyTrack).filter(StudyTrack.published.is_(True)).order_by(StudyTrack.titulo).all()
    return [_dump(t, _progresso(db, user.id, t), com_etapas=False) for t in ts]


@router.get("/{slug}")
def detalhe(slug: str, db: Session = Depends(get_db), user: User = Depends(current_user)):
    t = db.query(StudyTrack).filter(
        StudyTrack.slug == slug, StudyTrack.published.is_(True)
    ).first()
    if t is None:
        raise HTTPException(status_code=404, detail="Trilha não encontrada.")
    return _dump(t, _progresso(db, user.id, t))


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
    return _dump(t, prog)
