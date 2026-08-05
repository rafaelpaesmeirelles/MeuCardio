from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.commands.reconcile_content import FRONTS as RECONCILIATION_FRONTS
from app.commands.reconcile_content import SCIENTIFIC_MINIMUM
from app.core.db import get_db
from app.core.security import current_user, require_admin
from app.models.checklist import DischargeChecklist
from app.models.clinical_case import ClinicalCase
from app.models.content import Document, DocumentRevision
from app.models.drug import Drug
from app.models.emergency import EmergencyProtocol
from app.models.evidence import EvidenceRecord
from app.models.gallery import GalleryImage
from app.models.lab_test import LabTest
from app.models.patient_material import PatientMaterial
from app.models.specialty_guide import SpecialtyDisease, SymptomTriageGuide
from app.models.study import ScientificStudy
from app.models.study_track import StudyTrack
from app.services.content_areas import content_area_counts

router = APIRouter(prefix="/api/library", tags=["biblioteca"])

# Os mínimos vêm da mesma fonte usada pelo reconciliador operacional. O número
# de arquivos físicos é certificado pelo inventário versionado e não é inferido
# das tabelas, que representam registros científicos, não arquivos do filesystem.
SCIENTIFIC_CORPUS_MINIMUM = SCIENTIFIC_MINIMUM
SCIENTIFIC_FILES_EXPECTED = 1_327

CATALOG_FRONTS = (
    ("documentos", "Documentos científicos", "/biblioteca", Document),
    ("evidencias", "Evidências e recomendações", "/evidencias", EvidenceRecord),
    ("estudos", "Estudos clínicos", "/estudos", ScientificStudy),
    ("casos_clinicos", "Casos clínicos", "/casos-clinicos", ClinicalCase),
    ("trilhas", "Trilhas de estudo", "/trilhas", StudyTrack),
    ("galeria", "Galeria de imagens", "/galeria", GalleryImage),
    ("exames", "Exames e interpretação", "/exames", LabTest),
    ("medicamentos", "Medicamentos", "/medicamentos", Drug),
    ("checklists", "Checklists", "/checklists", DischargeChecklist),
    ("material_paciente", "Material para pacientes", "/material-paciente", PatientMaterial),
    ("emergencia", "Protocolos de emergência", "/emergencia", EmergencyProtocol),
    ("doencas_especializadas", "Guias por doença", "/guias-doencas", SpecialtyDisease),
    ("triagem_sintomas", "Triagem por sintomas", "/triagem-sintomas", SymptomTriageGuide),
)


def _card(d: Document) -> dict:
    return {
        "id": d.id,
        "slug": d.slug,
        "title": d.title,
        "kind": d.kind,
        "theme": d.theme,
        "summary": d.summary,
        "tags": d.tags,
        "evidence_level": d.evidence_level,
        "review_status": d.review_status,
        "source_tier": d.source_tier,
        "gaps": d.gaps,
        "updated_at": d.updated_at,
    }


@router.get("/catalog")
def catalog(db: Session = Depends(get_db), _=Depends(current_user)):
    """Resumo canônico das 13 frentes científicas.

    ``total`` e ``inventory_total`` representam todos os registros preservados
    no PostgreSQL. ``published_total`` informa separadamente o conteúdo já
    liberado aos assinantes. A integridade é verificada frente a frente, como no
    reconciliador, para que excedente numa coleção nunca esconda déficit noutra.
    """
    fronts = []
    published_total = 0
    inventory_total = 0
    below_minimum: dict[str, dict[str, int]] = {}

    for key, label, route, model in CATALOG_FRONTS:
        inventory_count = db.query(model).count()
        published_count = db.query(model).filter(model.published.is_(True)).count()
        minimum = int(RECONCILIATION_FRONTS[key]["minimum"])
        missing = max(minimum - inventory_count, 0)

        inventory_total += inventory_count
        published_total += published_count
        if missing:
            below_minimum[key] = {
                "inventory_count": inventory_count,
                "minimum": minimum,
                "missing": missing,
            }

        fronts.append({
            "key": key,
            "label": label,
            "route": route,
            "count": published_count,
            "inventory_count": inventory_count,
            "minimum": minimum,
            "missing": missing,
            "integrity_ok": missing == 0,
        })

    missing_total = sum(item["missing"] for item in below_minimum.values())
    return {
        "total": inventory_total,
        "inventory_total": inventory_total,
        "published_total": published_total,
        "unpublished": max(inventory_total - published_total, 0),
        "fronts": fronts,
        "expected_minimum": SCIENTIFIC_CORPUS_MINIMUM,
        "physical_files_expected": SCIENTIFIC_FILES_EXPECTED,
        "integrity_ok": not below_minimum,
        "missing": missing_total,
        "below_minimum": below_minimum,
    }


@router.get("/themes")
def themes(db: Session = Depends(get_db), _=Depends(current_user)):
    rows = db.execute(
        select(Document.theme, func.count(Document.id))
        .where(Document.published.is_(True))
        .group_by(Document.theme).order_by(Document.theme)
    ).all()
    return [{"theme": t, "count": c} for t, c in rows]


@router.get("/area-counts")
def area_counts(db: Session = Depends(get_db), _=Depends(current_user)):
    """Totais publicados das áreas especializadas em todas as coleções.

    São contagens por faceta e podem se sobrepor: um guia fetal, por exemplo,
    também pode ser parte da Cardiologia Pediátrica. O ``breakdown`` permite à
    interface explicar de quais coleções veio o total sem contar um registro
    duas vezes dentro da mesma área/frente.
    """
    return {
        "areas": content_area_counts(db),
        "counting_rule": "published_unique_per_area_and_collection",
        "overlapping_facets": True,
    }


@router.get("/documents")
def list_documents(
    theme: str | None = None,
    kind: str | None = None,
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    _=Depends(current_user),
):
    q = db.query(Document).filter(Document.published.is_(True))
    if theme:
        q = q.filter(Document.theme == theme)
    if kind:
        q = q.filter(Document.kind == kind)
    total = q.count()
    items = q.order_by(Document.title, Document.id).offset(offset).limit(limit).all()
    next_offset = offset + len(items)
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "next_offset": next_offset if next_offset < total else None,
        "has_more": next_offset < total,
        "items": [_card(d) for d in items],
    }


@router.get("/presentation-options")
def presentation_options(db: Session = Depends(get_db), _=Depends(current_user)):
    """Catálogo leve e completo usado pelo Modo Apresentação.

    Evita baixar seis páginas do objeto científico completo (tags, lacunas,
    metadados de revisão) para uma tela que precisa apenas identificar e
    selecionar o documento. Uma única resposta também elimina a falha parcial
    em que cinco páginas carregavam e a sexta derrubava todo o catálogo.
    """
    documents = (
        db.query(Document)
        .filter(Document.published.is_(True))
        .order_by(Document.theme, Document.title, Document.id)
        .all()
    )
    return [{
        "slug": document.slug,
        "title": document.title,
        "theme": document.theme,
        "kind": document.kind,
        "summary": document.summary,
        "review_status": document.review_status,
    } for document in documents]


@router.get("/documents/{slug}")
def get_document(slug: str, db: Session = Depends(get_db), _=Depends(current_user)):
    d = db.query(Document).filter(Document.slug == slug, Document.published.is_(True)).first()
    if not d:
        raise HTTPException(status_code=404, detail="Documento não encontrado ou ainda em revisão.")
    return {**_card(d), "body_md": d.body_md, "source_refs": d.source_refs,
            "source_tier": d.source_tier, "gaps": d.gaps, "version": d.version}


@router.put("/documents/{slug}")
def update_document(
    slug: str, payload: dict, db: Session = Depends(get_db), user=Depends(require_admin)
):
    d = db.query(Document).filter(Document.slug == slug).first()
    if not d:
        raise HTTPException(status_code=404, detail="Documento não encontrado.")
    db.add(DocumentRevision(
        document_id=d.id, version=d.version, body_md=d.body_md, author_id=user.id
    ))
    for f in ("title", "summary", "body_md", "theme", "kind", "review_status", "evidence_level"):
        if f in payload:
            setattr(d, f, payload[f])
    d.version += 1
    db.commit()
    return {"slug": d.slug, "version": d.version}
