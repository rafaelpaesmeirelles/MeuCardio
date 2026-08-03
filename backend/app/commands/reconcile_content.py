"""Reconcilia todo o corpus versionado com o banco de dados.

Uso operacional:

    python -m app.commands.reconcile_content --publish-reviewed

A carga é idempotente. Registros já publicados não são despublicados pelos
carregadores; a opção ``--publish-reviewed`` promove somente itens cujo
``review_status`` está explicitamente marcado como ``revisado``.
"""

from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import SessionLocal
from app.models.checklist import DischargeChecklist
from app.models.clinical_case import ClinicalCase
from app.models.content import Document
from app.models.drug import Drug
from app.models.emergency import EmergencyProtocol
from app.models.evidence import EvidenceRecord
from app.models.gallery import GalleryImage
from app.models.lab_test import LabTest
from app.models.patient_material import PatientMaterial
from app.models.study import ScientificStudy
from app.models.study_track import StudyTrack
from app.services.importer import import_directory


FRONTS: dict[str, dict[str, Any]] = {
    "documentos": {
        "path": settings.content_dir,
        "model": Document,
        "minimum": 1077,
        "loader": None,
    },
    "galeria": {
        "path": "/galeria/metadados.json",
        "model": GalleryImage,
        "minimum": 236,
        "loader": "carregar_galeria",
    },
    "exames": {
        "path": "/exames/metadados.json",
        "model": LabTest,
        "minimum": 244,
        "loader": "carregar_exames",
    },
    "evidencias": {
        "path": "/evidencias/metadados.json",
        "model": EvidenceRecord,
        "minimum": 1776,
        "loader": "carregar_evidencias",
    },
    "estudos": {
        "path": "/estudos/metadados.json",
        "model": ScientificStudy,
        "minimum": 383,
        "loader": "carregar_estudos",
    },
    "medicamentos": {
        "path": "/medicamentos/metadados.json",
        "model": Drug,
        "minimum": 114,
        "loader": "carregar_drugs",
    },
    "checklists": {
        "path": "/checklists/metadados.json",
        "model": DischargeChecklist,
        "minimum": 23,
        "loader": "carregar_checklists",
    },
    "trilhas": {
        "path": "/trilhas/metadados.json",
        "model": StudyTrack,
        "minimum": 469,
        "loader": "carregar_trilhas",
    },
    "material_paciente": {
        "path": "/material-paciente/metadados.json",
        "model": PatientMaterial,
        "minimum": 27,
        "loader": "carregar_material_paciente",
    },
    "emergencia": {
        "path": "/emergencia/metadados.json",
        "model": EmergencyProtocol,
        "minimum": 31,
        "loader": "carregar_emergencia",
    },
    "casos_clinicos": {
        "path": "/casos-clinicos/metadados.json",
        "model": ClinicalCase,
        "minimum": 556,
        "loader": "carregar_casos_clinicos",
    },
}

SCIENTIFIC_MINIMUM = sum(front["minimum"] for front in FRONTS.values())


def _ensure_source(front: str, path: str) -> None:
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(f"Fonte da frente {front} não encontrada: {path}")


def _load_front(front: str, config: dict[str, Any]) -> dict:
    path = str(config["path"])
    _ensure_source(front, path)
    if config["loader"] is None:
        return import_directory(path)
    module = importlib.import_module(f"app.services.{config['loader']}")
    return module.carregar(path)


def _load_controlled_substances(db: Session) -> dict:
    path = "/controlados/listas-344-98.json"
    _ensure_source("controlados", path)
    from app.services.carregar_controlados import carregar

    return carregar(db, path)


def _publish_reviewed(db: Session) -> dict[str, int]:
    result: dict[str, int] = {}
    for front, config in FRONTS.items():
        model = config["model"]
        changed = (
            db.query(model)
            .filter(model.published.is_(False), model.review_status == "revisado")
            .update({model.published: True}, synchronize_session=False)
        )
        result[front] = int(changed)
    db.commit()
    return result


def _database_inventory(db: Session) -> dict[str, Any]:
    fronts: dict[str, Any] = {}
    total = 0
    below_minimum: dict[str, dict[str, int]] = {}
    for front, config in FRONTS.items():
        model = config["model"]
        count = db.query(model).count()
        published = db.query(model).filter(model.published.is_(True)).count()
        minimum = int(config["minimum"])
        fronts[front] = {
            "database": count,
            "published": published,
            "minimum": minimum,
        }
        total += count
        if count < minimum:
            below_minimum[front] = {"database": count, "minimum": minimum}
    return {
        "total": total,
        "minimum": SCIENTIFIC_MINIMUM,
        "fronts": fronts,
        "below_minimum": below_minimum,
    }


def reconcile(*, publish_reviewed: bool = False, allow_partial: bool = False) -> dict[str, Any]:
    loads: dict[str, Any] = {}
    for front, config in FRONTS.items():
        loads[front] = _load_front(front, config)

    db = SessionLocal()
    try:
        loads["controlados"] = _load_controlled_substances(db)
        published = _publish_reviewed(db) if publish_reviewed else {}
        database = _database_inventory(db)
    finally:
        db.close()

    result = {
        "loads": loads,
        "published_reviewed": published,
        "database": database,
    }
    if database["below_minimum"] and not allow_partial:
        raise RuntimeError(
            "Reconciliação incompleta: "
            + json.dumps(database["below_minimum"], ensure_ascii=False, sort_keys=True)
        )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--publish-reviewed",
        action="store_true",
        help="Publica somente registros com review_status=revisado.",
    )
    parser.add_argument(
        "--allow-partial",
        action="store_true",
        help="Não falha quando o banco fica abaixo do baseline versionado.",
    )
    args = parser.parse_args()

    try:
        result = reconcile(
            publish_reviewed=args.publish_reviewed,
            allow_partial=args.allow_partial,
        )
    except Exception as exc:  # noqa: BLE001 - comando precisa sair não-zero com diagnóstico
        print(json.dumps({"status": "error", "type": type(exc).__name__, "detail": str(exc)},
                         ensure_ascii=False, indent=2))
        return 1

    print(json.dumps({"status": "ok", **result}, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
