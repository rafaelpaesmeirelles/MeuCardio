"""Contagem transversal do acervo por área clínica especializada.

O catálogo canônico soma 13 frentes distintas. A página inicial, porém,
historicamente usava apenas ``documents.theme`` nos cartões de áreas em
destaque. Isso escondia guias de doenças, evidências, estudos, casos, trilhas,
imagens e materiais que pertencem à mesma área.

As contagens abaixo são facetas: um conteúdo neonatal também pode pertencer à
Cardiologia Pediátrica. Cada registro é contado no máximo uma vez dentro de
cada área e de cada frente, mas os totais das áreas não devem ser somados entre
si. O total global continua vindo de ``/api/library/catalog``.
"""

from __future__ import annotations

from collections.abc import Iterable
import unicodedata

from sqlalchemy.orm import Session

from app.models.checklist import DischargeChecklist
from app.models.clinical_case import ClinicalCase
from app.models.content import Document
from app.models.emergency import EmergencyProtocol
from app.models.evidence import EvidenceRecord
from app.models.gallery import GalleryImage
from app.models.lab_test import LabTest
from app.models.patient_material import PatientMaterial
from app.models.specialty_guide import SpecialtyDisease, SymptomTriageGuide
from app.models.study import ScientificStudy
from app.models.study_track import StudyTrack


AREA_DEFINITIONS = (
    {
        "id": "pediatrica",
        "label": "Cardiologia Pediátrica",
        "terms": (
            "cardiologia pediatrica", "cardiopediatria", "pediatr", "infancia",
            "crianca", "adolescen", "kawasaki",
        ),
    },
    {
        "id": "neonatal",
        "label": "Cardiologia Neonatal",
        "terms": (
            "neonat", "recem nascid", "prematur", "primeiros dias de vida",
        ),
    },
    {
        "id": "congenita",
        "label": "Cardiopatias Congênitas",
        "terms": (
            "cardiopatia congenita", "cardiopatias congenitas", "congenit",
            "grown-up congenital", "guch",
        ),
    },
    {
        "id": "geriatria",
        "label": "Cardio-Geriatria",
        "terms": (
            "cardiologia geriatrica", "cardiogeriatria", "geriatr", "idoso",
            "fragilidade", "longevidade", "centenario", "nonagenar",
        ),
    },
    {
        "id": "gestacao",
        "label": "Cardiologia na Gestação e Puerpério",
        "terms": (
            "gravidez", "gestacao", "gestante", "puerper", "amament", "lacta",
            "materna", "planejamento reprodutivo",
        ),
    },
    {
        "id": "cardiooncologia",
        "label": "Cardio-Oncologia",
        "terms": (
            "cardio-oncologia", "cardiooncologia", "oncolog", "cardiotox",
            "quimioter", "antracic", "imunoterapia", "cancer",
        ),
    },
    {
        "id": "fetal",
        "label": "Cardiologia Fetal",
        "terms": (
            "cardiologia fetal", "cardiologia_fetal", "fetal", "pre-natal",
            "prenatal", "perinatal",
        ),
    },
)


# Somente campos de classificação/identificação são carregados. Textos clínicos
# completos e JSONs pesados não entram na consulta.
AREA_SOURCES = (
    ("documentos", Document, ("slug", "title", "theme", "tags")),
    ("evidencias", EvidenceRecord, ("slug", "guideline_title", "theme", "tags")),
    ("estudos", ScientificStudy, ("slug", "title", "theme", "tags")),
    ("casos_clinicos", ClinicalCase, ("slug", "titulo", "tema")),
    ("trilhas", StudyTrack, ("slug", "titulo", "tema")),
    ("galeria", GalleryImage, ("slug", "title", "theme", "tags")),
    ("exames", LabTest, ("slug", "name", "category", "theme", "tags")),
    ("checklists", DischargeChecklist, ("slug", "condicao", "theme")),
    ("material_paciente", PatientMaterial, ("slug", "titulo", "tema")),
    ("emergencia", EmergencyProtocol, ("slug", "titulo")),
    (
        "doencas_especializadas",
        SpecialtyDisease,
        ("slug", "name", "area", "category", "subtype", "tags"),
    ),
    ("triagem_sintomas", SymptomTriageGuide, ("slug", "name", "areas", "tags")),
)


def _normalizar(value: object) -> str:
    text = str(value or "")
    return "".join(
        character for character in unicodedata.normalize("NFD", text)
        if unicodedata.category(character) != "Mn"
    ).casefold().replace("_", " ")


def _flatten(value: object) -> Iterable[str]:
    if value is None:
        return ()
    if isinstance(value, dict):
        return (str(item) for pair in value.items() for item in pair)
    if isinstance(value, (list, tuple, set)):
        return (str(item) for item in value)
    return (str(value),)


def matching_area_ids(*values: object) -> set[str]:
    """Classifica metadados sem usar corpo clínico ou conteúdo não publicado."""
    text = _normalizar(" ".join(
        flattened
        for value in values
        for flattened in _flatten(value)
    ))
    return {
        definition["id"]
        for definition in AREA_DEFINITIONS
        if any(term in text for term in definition["terms"])
    }


def content_area_counts(db: Session) -> list[dict]:
    counters: dict[str, dict[str, int]] = {
        definition["id"]: {} for definition in AREA_DEFINITIONS
    }

    for source_key, model, field_names in AREA_SOURCES:
        fields = [getattr(model, name) for name in field_names]
        rows = db.query(model.id, *fields).filter(model.published.is_(True)).all()
        matched_ids: dict[str, set[int]] = {
            definition["id"]: set() for definition in AREA_DEFINITIONS
        }
        for row in rows:
            record_id = int(row[0])
            for area_id in matching_area_ids(*row[1:]):
                matched_ids[area_id].add(record_id)
        for area_id, record_ids in matched_ids.items():
            if record_ids:
                counters[area_id][source_key] = len(record_ids)

    return [
        {
            "id": definition["id"],
            "label": definition["label"],
            "count": sum(counters[definition["id"]].values()),
            "collections": len(counters[definition["id"]]),
            "breakdown": counters[definition["id"]],
        }
        for definition in AREA_DEFINITIONS
    ]
