"""Diretrizes de origem e alerta de atualização (Tarefa 9).

Separação que o briefing faz e o código respeita: **a diretriz ter sido
revisada não significa que o conteúdo do MeuCardio esteja errado.** O alerta
avisa que existe revisão publicada a considerar; quem decide se o texto daqui
mudou é a revisão humana, com o mesmo checkpoint de sempre. Por isso nada aqui
altera `review_status` nem despublica documento.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user, require_admin
from app.models.audit import AuditLog
from app.models.content import Document
from app.models.favorite import Favorite
from app.models.guideline import Guideline, GuidelineLink
from app.models.user import User

router = APIRouter(prefix="/api/diretrizes", tags=["diretrizes"])


def _dump(g: Guideline, vinculos: int = 0, confirmados: int = 0) -> dict:
    return {
        "slug": g.slug, "org": g.org, "titulo": g.titulo, "ano": g.ano,
        "doi": g.doi, "url": g.url,
        "vinculos": vinculos, "vinculos_confirmados": confirmados,
        "substituida": g.superseded_by_id is not None,
        "substituida_em": g.substituida_em,
        "alerta_enviado_em": g.alerta_enviado_em,
    }


@router.get("")
def listar(
    org: str | None = None,
    substituidas: bool | None = Query(None, description="filtra só as revisadas"),
    db: Session = Depends(get_db),
    _=Depends(current_user),
):
    q = db.query(Guideline)
    if org:
        q = q.filter(Guideline.org == org.upper())
    if substituidas is True:
        q = q.filter(Guideline.superseded_by_id.isnot(None))
    elif substituidas is False:
        q = q.filter(Guideline.superseded_by_id.is_(None))

    contagens = dict(
        db.query(GuidelineLink.guideline_id, func.count(GuidelineLink.id))
        .group_by(GuidelineLink.guideline_id).all()
    )
    confirmadas = dict(
        db.query(GuidelineLink.guideline_id, func.count(GuidelineLink.id))
        .filter(GuidelineLink.confirmado.is_(True))
        .group_by(GuidelineLink.guideline_id).all()
    )
    return [
        _dump(g, contagens.get(g.id, 0), confirmadas.get(g.id, 0))
        for g in q.order_by(Guideline.org, Guideline.ano.desc(), Guideline.titulo).all()
    ]


@router.get("/{slug}/impacto")
def impacto(slug: str, db: Session = Depends(get_db), _=Depends(require_admin)):
    """Que conteúdo depende desta diretriz e quantos assinantes o favoritaram.

    É a pergunta que a Tarefa 9 precisa responder antes de qualquer alerta:
    notificar todo mundo sobre toda diretriz revisada vira ruído, e ruído faz o
    assinante desligar o aviso que importa.
    """
    g = db.query(Guideline).filter(Guideline.slug == slug).first()
    if g is None:
        raise HTTPException(status_code=404, detail="Diretriz não encontrada.")

    vinculos = db.query(GuidelineLink).filter(GuidelineLink.guideline_id == g.id).all()
    ids_ligados = [v.item_id for v in vinculos if v.item_type == "documento"]
    # Só conteúdo publicado conta como impacto. Documento retido — por estar
    # em revisão ou por ter sido absorvido numa fusão — continua com vínculo
    # no banco, mas ninguém o lê, e contá-lo inflaria o alcance do alerta.
    docs = (db.query(Document)
              .filter(Document.id.in_(ids_ligados), Document.published.is_(True))
              .all()) if ids_ligados else []
    ids_doc = [d.id for d in docs]

    favoritos = dict(
        db.query(Favorite.item_id, func.count(func.distinct(Favorite.user_id)))
        .filter(Favorite.item_type == "documento", Favorite.item_id.in_(ids_doc))
        .group_by(Favorite.item_id).all()
    ) if ids_doc else {}

    usuarios = db.query(func.count(func.distinct(Favorite.user_id))).filter(
        Favorite.item_type == "documento", Favorite.item_id.in_(ids_doc or [0])
    ).scalar() or 0

    return {
        "diretriz": _dump(g, len(vinculos)),
        "conteudo": [
            {"slug": d.slug, "titulo": d.title, "tema": d.theme,
             "publicado": d.published, "review_status": d.review_status,
             "assinantes_que_favoritaram": favoritos.get(d.id, 0)}
            for d in sorted(docs, key=lambda x: x.title)
        ],
        "assinantes_impactados": usuarios,
        "vinculos_em_conteudo_retido": len(ids_ligados) - len(ids_doc),
        "nota": "Favoritar é o sinal de uso disponível hoje. Assinante que leu sem "
                "favoritar não é contado — o número é piso, não total.",
    }


class Substituicao(BaseModel):
    substituida_por_slug: str
    nota: str | None = None


@router.post("/admin/{slug}/substituida")
def marcar_substituida(
    slug: str, dados: Substituicao,
    db: Session = Depends(get_db), admin=Depends(require_admin),
):
    antiga = db.query(Guideline).filter(Guideline.slug == slug).first()
    nova = db.query(Guideline).filter(Guideline.slug == dados.substituida_por_slug).first()
    if antiga is None or nova is None:
        raise HTTPException(status_code=404, detail="Diretriz não encontrada.")
    if antiga.id == nova.id:
        raise HTTPException(status_code=422, detail="Uma diretriz não substitui a si mesma.")
    if nova.ano < antiga.ano:
        # Não é impossível (uma diretriz pode ser substituída por outra de ano
        # anterior em republicação), mas é raro o bastante para merecer recusa
        # explícita em vez de virar dado silenciosamente errado.
        raise HTTPException(
            status_code=422,
            detail=f"A diretriz substituta ({nova.ano}) é anterior à substituída ({antiga.ano}). "
                   "Se isso está correto, ajuste os anos antes.",
        )

    antiga.superseded_by_id = nova.id
    antiga.substituida_em = datetime.now(timezone.utc)
    antiga.alerta_enviado_em = None  # há novidade a comunicar
    db.add(AuditLog(user_id=admin.id, action="marcar_diretriz_substituida",
                    entity="guideline", entity_id=antiga.slug,
                    detail={"por": nova.slug, "nota": dados.nota}))
    db.commit()
    return {"substituida": antiga.slug, "por": nova.slug,
            "conteudo_afetado": db.query(GuidelineLink)
                                  .filter(GuidelineLink.guideline_id == antiga.id).count()}


@router.get("/admin/pendentes-de-alerta")
def pendentes_de_alerta(db: Session = Depends(get_db), _=Depends(require_admin)):
    """Diretrizes marcadas como substituídas cujo alerta ainda não foi enviado."""
    q = db.query(Guideline).filter(
        Guideline.superseded_by_id.isnot(None),
        Guideline.alerta_enviado_em.is_(None),
    ).order_by(Guideline.substituida_em)
    saida = []
    for g in q.all():
        nova = db.query(Guideline).filter(Guideline.id == g.superseded_by_id).first()
        saida.append({
            "slug": g.slug, "titulo": g.titulo, "ano": g.ano,
            "substituida_por": nova.slug if nova else None,
            "ano_nova": nova.ano if nova else None,
            "conteudo_afetado": db.query(GuidelineLink)
                                  .filter(GuidelineLink.guideline_id == g.id).count(),
        })
    return saida


@router.post("/admin/extrair")
def extrair_vinculos(db: Session = Depends(get_db), admin=Depends(require_admin)):
    """Cria diretrizes e vínculos a partir das `source_refs` dos documentos.

    Idempotente: rodar de novo não duplica nem sobrescreve confirmação humana.
    Vínculo novo nasce **não confirmado** — a extração é palpite bem-informado,
    e carimbá-la como verdade repetiria o erro do `review_status` automático que
    este projeto já corrigiu uma vez.
    """
    from app.services.extrair_diretrizes import extrair

    criadas = vinculos_novos = 0
    for doc in db.query(Document).all():
        for d in extrair(list(doc.source_refs or [])):
            g = db.query(Guideline).filter(Guideline.slug == d["slug"]).first()
            if g is None:
                g = Guideline(slug=d["slug"], org=d["org"], titulo=d["titulo"],
                              ano=d["ano"], doi=d["doi"], url=d["url"], tema=doc.theme)
                db.add(g); db.flush(); criadas += 1
            elif g.doi is None and d["doi"]:
                g.doi = d["doi"]  # completa o que faltava, sem sobrescrever

            existe = db.query(GuidelineLink).filter(
                GuidelineLink.guideline_id == g.id,
                GuidelineLink.item_type == "documento",
                GuidelineLink.item_id == doc.id,
            ).first()
            if existe is None:
                db.add(GuidelineLink(guideline_id=g.id, item_type="documento",
                                     item_id=doc.id, trecho=d["trecho"]))
                vinculos_novos += 1
    db.commit()
    db.add(AuditLog(user_id=admin.id, action="extrair_diretrizes", entity="guideline",
                    detail={"criadas": criadas, "vinculos": vinculos_novos}))
    db.commit()
    return {
        "diretrizes_criadas": criadas,
        "vinculos_criados": vinculos_novos,
        "nota": "Vínculos entram como não confirmados. Confirme antes de usá-los "
                "como base de alerta — a extração acerta muito e erra alguma coisa.",
    }

@router.post("/admin/consolidar")
def consolidar_duplicatas(db: Session = Depends(get_db), admin=Depends(require_admin)):
    """Funde diretrizes que o extrator criou em duplicidade.

    A geração de slug foi corrigida depois que as primeiras entradas já estavam
    no banco: variantes de título — citação da revista colada no fim, ou o
    subtítulo "developed in collaboration with…" estourando o corte — produziam
    duas entradas para a mesma diretriz. Isso é pior do que parece: o alerta
    avisaria só metade dos documentos que dependem dela.

    Recalcula o slug de cada diretriz com a regra atual e funde as que colidem,
    mantendo a mais antiga (menor id), transferindo os vínculos e preservando
    qualquer confirmação humana já feita.
    """
    from app.services.extrair_diretrizes import _slug

    por_slug: dict[str, Guideline] = {}
    fundidas, vinculos_movidos = 0, 0
    for g in db.query(Guideline).order_by(Guideline.id).all():
        canonico = _slug(g.org, g.ano, g.titulo)
        principal = por_slug.get(canonico)
        if principal is None:
            por_slug[canonico] = g
            if g.slug != canonico and not db.query(Guideline).filter(
                Guideline.slug == canonico, Guideline.id != g.id
            ).first():
                g.slug = canonico
            continue

        for v in db.query(GuidelineLink).filter(GuidelineLink.guideline_id == g.id).all():
            ja = db.query(GuidelineLink).filter(
                GuidelineLink.guideline_id == principal.id,
                GuidelineLink.item_type == v.item_type,
                GuidelineLink.item_id == v.item_id,
            ).first()
            if ja is None:
                v.guideline_id = principal.id
                vinculos_movidos += 1
            else:
                # Confirmação humana nunca se perde numa fusão.
                if v.confirmado and not ja.confirmado:
                    ja.confirmado = True
                    ja.origem = v.origem
                db.delete(v)
        if principal.doi is None and g.doi:
            principal.doi = g.doi
        db.delete(g)
        fundidas += 1

    db.commit()
    db.add(AuditLog(user_id=admin.id, action="consolidar_diretrizes", entity="guideline",
                    detail={"fundidas": fundidas, "vinculos_movidos": vinculos_movidos}))
    db.commit()
    return {"diretrizes_fundidas": fundidas, "vinculos_movidos": vinculos_movidos,
            "restantes": db.query(Guideline).count()}
