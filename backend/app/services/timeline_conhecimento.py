"""Timeline de evolução do conhecimento por tema, dentro de Trilhas de estudo.

A timeline é DERIVADA de itens científicos já publicados/revisados na CorVIA:
`EvidenceRecord` (recomendações/diretrizes) e `ScientificStudy` (estudos,
ensaios, coortes, revisões e metanálises). Ela nunca cria um fato clínico nem
inventa um ano, DOI ou PMID. O que esta camada acrescenta é organização:
canonicaliza aliases históricos de tema, ordena cronologicamente e classifica
cada marco em um eixo editorial transparente (fundamentos, investigação,
estratificação, tratamento, procedimentos, prevenção, segurança ou diretrizes)
para que a tela mostre COMO o conhecimento daquele assunto evoluiu.

A classificação do eixo não muda o conteúdo científico nem cria relação entre
temas: usa apenas tags e texto do próprio item já revisado. Quando não há pista
suficiente, cai em um rótulo neutro (`Evidência clínica` ou
`Diretrizes e recomendações`) em vez de adivinhar.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.content import Document
from app.models.evidence import EvidenceRecord
from app.models.study import ScientificStudy
from app.services.topic_relevance import canonical_theme, normalize_text, theme_variants

EIXOS_ORDEM = (
    "Fundamentos e fisiopatologia",
    "Investigação e diagnóstico",
    "Estratificação e prognóstico",
    "Tratamento farmacológico",
    "Procedimentos e dispositivos",
    "Prevenção",
    "Segurança",
    "Diretrizes e recomendações",
    "Evidência clínica",
)

EIXO_KEYWORDS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Fundamentos e fisiopatologia", (
        "fisiopat", "mecanismo", "genetic", "genetica", "historia natural", "etiologia",
        "patogen", "remodelamento", "biologia", "fenotipo",
    )),
    ("Investigação e diagnóstico", (
        "diagnost", "investig", "ecocardi", "ressonancia", "tomografia", "angiograf",
        "cateterismo", "ffr", "ifr", "biomarc", "troponin", "natriuret", "teste ",
        "screening", "rastreio", "monitorizacao", "monitoramento", "imagem",
    )),
    ("Estratificação e prognóstico", (
        "estratific", "prognost", "preditor", "escore de risco", "risk score",
        "classificacao de risco", "predicao", "prognostic",
    )),
    ("Procedimentos e dispositivos", (
        "ablacao", "tavi", "transcateter", "angioplast", "pci", "cabg", "stent",
        "revascular", "cirurgia", "marcapasso", "desfibrilador", " cdi ", " crt ",
        "ressincron", "dispositivo", "intervencao", "procedimento",
    )),
    ("Prevenção", (
        "prevencao", "profilax", "cessacao", "vacina", "atividade fisica", "exercicio",
        "estilo de vida", "rastreio populacional",
    )),
    ("Segurança", (
        "seguranca", "safety", "sangramento", "hemorrag", "evento advers", "efeito advers",
        "toxicidade", "contraindic", "interacao", "iatrogen",
    )),
    ("Tratamento farmacológico", (
        "farmacolog", "medicamento", "terapia medicamentosa", "tratamento medicamentoso",
        "anticoagul", "antiagreg", "estatina", "pcsk9", "sglt2", "sacubitril",
        "enalapril", "betabloque", "diuret", "espironolactona", "antagonista mineralocorticoide",
        "antiarritm", "vasodilat", "trombol", "fibrinolit",
    )),
)


@dataclass
class Marco:
    ano: int
    tipo: str  # diretriz | estudo
    eixo: str
    subtipo: str
    slug: str
    titulo: str
    descricao: str
    fonte: str
    referencia: str | None
    rota: str
    documento: dict | None
    tags: list[str]
    doi: str | None
    pmid: str | None
    source_url: str | None


def _texto_classificacao(*partes: object) -> str:
    valores: list[str] = []
    for parte in partes:
        if parte is None:
            continue
        if isinstance(parte, (list, tuple, set)):
            valores.extend(str(item) for item in parte if item)
        else:
            valores.append(str(parte))
    return f" {normalize_text(' | '.join(valores))} "


def classificar_eixo(*, tipo: str, titulo: str, descricao: str, tags: list[str] | None = None) -> str:
    """Editorial axis only; never interpreted as a new clinical claim."""
    texto = _texto_classificacao(tags or [], titulo, descricao)
    for eixo, keywords in EIXO_KEYWORDS:
        if any(normalize_text(keyword) in texto for keyword in keywords):
            return eixo
    return "Diretrizes e recomendações" if tipo == "diretriz" else "Evidência clínica"


def temas_disponiveis(db: Session) -> list[dict]:
    """Canonical topics with >=1 published evidence/study, merged across aliases."""
    contagem: Counter[str] = Counter()
    for theme in db.execute(
        select(EvidenceRecord.theme).where(EvidenceRecord.published.is_(True))
    ).scalars():
        canonical = canonical_theme(theme)
        if canonical:
            contagem[canonical] += 1
    for theme in db.execute(
        select(ScientificStudy.theme).where(ScientificStudy.published.is_(True))
    ).scalars():
        canonical = canonical_theme(theme)
        if canonical:
            contagem[canonical] += 1

    return [
        {"tema": theme, "total_marcos": total}
        for theme, total in sorted(contagem.items(), key=lambda item: item[0].casefold())
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
    """Chronological scientific evolution for a canonical clinical topic."""
    canonical = canonical_theme(tema)
    if not canonical:
        return {
            "tema": "", "total": 0, "marcos": [], "eixos": [],
            "primeiro_ano": None, "ultimo_ano": None,
        }

    variants = theme_variants(canonical)
    marcos: list[Marco] = []

    evidencias = db.execute(
        select(EvidenceRecord)
        .where(EvidenceRecord.theme.in_(variants), EvidenceRecord.published.is_(True))
        .order_by(EvidenceRecord.year, EvidenceRecord.statement)
    ).scalars().all()
    for evidence in evidencias:
        title = (
            evidence.statement[:160] + "…"
            if evidence.statement and len(evidence.statement) > 160
            else (evidence.statement or "")
        )
        description = (
            f"Classe {evidence.recommendation_class} · Nível {evidence.evidence_level} · "
            f"{evidence.guideline_title}"
        )
        marcos.append(Marco(
            ano=evidence.year,
            tipo="diretriz",
            eixo=classificar_eixo(
                tipo="diretriz", titulo=evidence.statement,
                descricao=" | ".join(filter(None, [evidence.summary, evidence.guideline_title])),
                tags=evidence.tags or [],
            ),
            subtipo="recomendacao_de_diretriz",
            slug=evidence.slug,
            titulo=title,
            descricao=description,
            fonte=f"{evidence.society} {evidence.year}",
            referencia=evidence.reference,
            rota=f"/evidencias/{evidence.slug}",
            documento=_documento_relacionado(db, evidence.document_slug),
            tags=evidence.tags or [],
            doi=evidence.doi,
            pmid=None,
            source_url=evidence.source_url,
        ))

    estudos = db.execute(
        select(ScientificStudy)
        .where(ScientificStudy.theme.in_(variants), ScientificStudy.published.is_(True))
        .order_by(ScientificStudy.year, ScientificStudy.title)
    ).scalars().all()
    for study in estudos:
        marcos.append(Marco(
            ano=study.year,
            tipo="estudo",
            eixo=classificar_eixo(
                tipo="estudo", titulo=study.title,
                descricao=" | ".join(filter(None, [study.summary, study.key_findings, study.clinical_implications])),
                tags=study.tags or [],
            ),
            subtipo=study.study_type,
            slug=study.slug,
            titulo=study.title,
            descricao=study.clinical_implications,
            fonte=f"{study.journal} · {study.year}",
            referencia=study.authors,
            rota=f"/estudos/{study.slug}",
            documento=None,
            tags=study.tags or [],
            doi=study.doi,
            pmid=study.pmid,
            source_url=study.url,
        ))

    marcos.sort(key=lambda item: (item.ano, EIXOS_ORDEM.index(item.eixo), item.tipo, item.titulo))
    counts = Counter(item.eixo for item in marcos)
    eixos = [
        {"eixo": eixo, "total": counts[eixo]}
        for eixo in EIXOS_ORDEM if counts[eixo]
    ]

    return {
        "tema": canonical,
        "total": len(marcos),
        "primeiro_ano": marcos[0].ano if marcos else None,
        "ultimo_ano": marcos[-1].ano if marcos else None,
        "eixos": eixos,
        "marcos": [
            {
                "ano": item.ano,
                "tipo": item.tipo,
                "eixo": item.eixo,
                "subtipo": item.subtipo,
                "slug": item.slug,
                "titulo": item.titulo,
                "descricao": item.descricao,
                "fonte": item.fonte,
                "referencia": item.referencia,
                "rota": item.rota,
                "documento": item.documento,
                "tags": item.tags,
                "doi": item.doi,
                "pmid": item.pmid,
                "source_url": item.source_url,
            }
            for item in marcos
        ],
    }
