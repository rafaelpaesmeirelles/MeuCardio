"""Timeline de evolução do conhecimento por doença (tarefa #53, dentro de
"Trilhas de estudo").

Pedido do Rafael: um item novo em Trilhas de estudo que lista as principais
doenças/temas da cardiologia e mostra a evolução do conhecimento/tratamento de
cada uma ao longo do tempo, com link para tudo que já existe no site sobre
cada marco.

**Decisão de arquitetura (opção "b" das duas descritas na tarefa): a timeline
é DERIVADA dos dados que já existem, sem tabela nova.** `evidence_records.year`
(recomendação de sociedade/diretriz, com classe e nível) e
`scientific_studies.year` (ensaio/estudo original, com periódico) já são datas
reais e verificadas — cada uma foi conferida contra fonte primária no momento
em que aquele item foi revisado e publicado, seguindo a mesma régua de todo o
conteúdo do projeto (nunca fabricar PMID/DOI/ano). Esta camada só agrupa por
tema e ordena cronologicamente o que já existe; não inventa nenhum "marco" novo
nem exige curadoria manual por tema — foi o critério que a tarefa pediu para
preferir esta abordagem à de uma tabela `TimelineMarco` com narrativa própria.

Cada marco aponta para a página real do item (evidência ou estudo). Como essas
duas páginas já têm o painel "Tudo sobre este tema" instalado (tarefa #54), o
médico chega a qualquer marco e, de lá, alcança tudo mais do mesmo tema com um
clique — não é preciso duplicar esse cruzamento aqui. Quando a evidência
carrega `document_slug`, o marco também aponta para o documento de origem, se
publicado, para não perder essa referência que já existe no dado.

Só item `published = True` entra — mesma regra do resto do produto.
"""

from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.content import Document
from app.models.evidence import EvidenceRecord
from app.models.study import ScientificStudy


@dataclass
class Marco:
    ano: int
    tipo: str  # "diretriz" (evidência/recomendação) | "estudo"
    slug: str
    titulo: str
    descricao: str
    fonte: str
    rota: str
    documento: dict | None


def temas_disponiveis(db: Session) -> list[dict]:
    """Temas com pelo menos um marco (evidência ou estudo publicado, com ano),
    ordenados alfabeticamente. Nunca lista tema sem nenhum conteúdo — mesma
    régua do resto do produto de não mostrar entrada vazia."""

    ev_rows = db.execute(
        select(EvidenceRecord.theme, func.count(EvidenceRecord.id))
        .where(EvidenceRecord.published.is_(True))
        .group_by(EvidenceRecord.theme)
    ).all()
    est_rows = db.execute(
        select(ScientificStudy.theme, func.count(ScientificStudy.id))
        .where(ScientificStudy.published.is_(True))
        .group_by(ScientificStudy.theme)
    ).all()

    contagem: dict[str, int] = {}
    for tema, n in ev_rows:
        contagem[tema] = contagem.get(tema, 0) + n
    for tema, n in est_rows:
        contagem[tema] = contagem.get(tema, 0) + n

    return [
        {"tema": tema, "total_marcos": total}
        for tema, total in sorted(contagem.items(), key=lambda kv: kv[0].lower())
    ]


def _documento_relacionado(db: Session, slug: str | None) -> dict | None:
    if not slug:
        return None
    doc = db.execute(
        select(Document).where(Document.slug == slug, Document.published.is_(True))
    ).scalar_one_or_none()
    if doc is None:
        return None
    return {"slug": doc.slug, "titulo": doc.title, "rota": f"/biblioteca/{doc.slug}"}


def montar_timeline(db: Session, tema: str) -> dict:
    """Marcos publicados do tema (evidências + estudos), em ordem cronológica.

    Nunca lança exceção por tema sem correspondência — devolve `marcos: []`,
    mesmo comportamento de `related_content.buscar_relacionados`.
    """

    tema = (tema or "").strip()
    if not tema:
        return {"tema": tema, "marcos": [], "total": 0}

    marcos: list[Marco] = []

    evidencias = db.execute(
        select(EvidenceRecord)
        .where(EvidenceRecord.theme == tema, EvidenceRecord.published.is_(True))
        .order_by(EvidenceRecord.year, EvidenceRecord.statement)
    ).scalars().all()
    for e in evidencias:
        titulo = (e.statement[:160] + "…") if len(e.statement) > 160 else e.statement
        marcos.append(Marco(
            ano=e.year,
            tipo="diretriz",
            slug=e.slug,
            titulo=titulo,
            descricao=f"Classe {e.recommendation_class} · Nível {e.evidence_level} · {e.guideline_title}",
            fonte=f"{e.society} {e.year}",
            rota=f"/evidencias/{e.slug}",
            documento=_documento_relacionado(db, e.document_slug),
        ))

    estudos = db.execute(
        select(ScientificStudy)
        .where(ScientificStudy.theme == tema, ScientificStudy.published.is_(True))
        .order_by(ScientificStudy.year, ScientificStudy.title)
    ).scalars().all()
    for s in estudos:
        marcos.append(Marco(
            ano=s.year,
            tipo="estudo",
            slug=s.slug,
            titulo=s.title,
            descricao=s.clinical_implications,
            fonte=f"{s.journal} · {s.year}",
            rota=f"/estudos/{s.slug}",
            documento=None,
        ))

    marcos.sort(key=lambda m: (m.ano, m.tipo, m.titulo))

    return {
        "tema": tema,
        "total": len(marcos),
        "marcos": [
            {
                "ano": m.ano, "tipo": m.tipo, "slug": m.slug, "titulo": m.titulo,
                "descricao": m.descricao, "fonte": m.fonte, "rota": m.rota,
                "documento": m.documento,
            }
            for m in marcos
        ],
    }
