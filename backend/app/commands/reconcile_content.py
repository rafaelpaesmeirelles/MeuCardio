"""Reconcilia todo o corpus versionado com o banco de dados.

Uso operacional:

    python -m app.commands.reconcile_content --publish-reviewed

A carga é idempotente. Registros removidos ou renomeados permanecem armazenados
para auditoria, mas são despublicados e deixam de contar para a certificação do
corpus canônico do commit atual.
"""

from __future__ import annotations

import argparse
import importlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import frontmatter
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
from app.services.importer import _slugify, import_directory

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
BLOCKING_DIAGNOSTIC_KEYS = frozenset({
    "avisos", "duplicados_ignorados", "erros", "falhas", "ignoradas",
    "ignorados", "puladas", "pulados", "recusadas", "recusados",
    "sem_arquivo", "vazios",
})

FRONTS: dict[str, dict[str, Any]] = {
    "documentos": {"path": settings.content_dir, "model": Document, "minimum": 1077, "loader": None},
    "galeria": {"path": "/galeria/metadados.json", "model": GalleryImage, "minimum": 236, "loader": "carregar_galeria"},
    "exames": {"path": "/exames/metadados.json", "model": LabTest, "minimum": 244, "loader": "carregar_exames"},
    "evidencias": {"path": "/evidencias/metadados.json", "model": EvidenceRecord, "minimum": 1776, "loader": "carregar_evidencias"},
    "estudos": {"path": "/estudos/metadados.json", "model": ScientificStudy, "minimum": 383, "loader": "carregar_estudos"},
    "medicamentos": {"path": "/medicamentos/metadados.json", "model": Drug, "minimum": 114, "loader": "carregar_drugs"},
    "checklists": {"path": "/checklists/metadados.json", "model": DischargeChecklist, "minimum": 23, "loader": "carregar_checklists"},
    "trilhas": {"path": "/trilhas/metadados.json", "model": StudyTrack, "minimum": 469, "loader": "carregar_trilhas"},
    "material_paciente": {"path": "/material-paciente/metadados.json", "model": PatientMaterial, "minimum": 27, "loader": "carregar_material_paciente"},
    "emergencia": {"path": "/emergencia/metadados.json", "model": EmergencyProtocol, "minimum": 31, "loader": "carregar_emergencia"},
    "casos_clinicos": {"path": "/casos-clinicos/metadados.json", "model": ClinicalCase, "minimum": 556, "loader": "carregar_casos_clinicos"},
}

SCIENTIFIC_MINIMUM = sum(front["minimum"] for front in FRONTS.values())


def _source_path(path: str) -> Path:
    configured = Path(path)
    if configured.exists():
        return configured
    fallback = REPOSITORY_ROOT / path.lstrip("/")
    if fallback.exists():
        return fallback
    return configured


def _ensure_source(front: str, path: str) -> Path:
    source = _source_path(path)
    if not source.exists():
        raise FileNotFoundError(f"Fonte da frente {front} não encontrada: {path}")
    return source


def _validate_unique_slugs(front: str, slugs: list[str]) -> set[str]:
    duplicados = sorted(slug for slug, count in Counter(slugs).items() if count > 1)
    if duplicados:
        raise RuntimeError(
            f"Frente {front} contém slugs duplicados: "
            + json.dumps(duplicados, ensure_ascii=False)
        )
    return set(slugs)


def _manifest_slugs(front: str, source: Path) -> set[str] | None:
    """Valida manifestos JSON e devolve o conjunto canônico de slugs."""
    if source.suffix.lower() != ".json":
        return None

    data = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise RuntimeError(f"Manifesto da frente {front} deve ser uma lista JSON.")

    slugs: list[str] = []
    invalidos: list[int] = []
    com_espacos: list[int] = []
    for index, item in enumerate(data):
        if not isinstance(item, dict):
            invalidos.append(index)
            continue
        slug = item.get("slug")
        if not isinstance(slug, str) or not slug.strip():
            invalidos.append(index)
            continue
        if slug != slug.strip():
            com_espacos.append(index)
            continue
        slugs.append(slug)

    if invalidos:
        raise RuntimeError(
            f"Frente {front} contém itens sem slug válido nos índices: {invalidos}"
        )
    if com_espacos:
        raise RuntimeError(
            f"Frente {front} contém slugs com espaços nas extremidades nos índices: "
            f"{com_espacos}"
        )
    return _validate_unique_slugs(front, slugs)


def _markdown_slugs(front: str, source: Path) -> set[str]:
    """Obtém os mesmos slugs que o importador gera para os Markdown."""
    slugs: list[str] = []
    for md in sorted(source.rglob("*.md")):
        post = frontmatter.load(md)
        meta = post.metadata
        title = meta.get("title") or md.stem

        if "slug" in meta:
            explicit_slug = meta["slug"]
            if not isinstance(explicit_slug, str) or not explicit_slug.strip():
                raise RuntimeError(
                    f"Frente {front} contém Markdown com slug explicitamente inválido: {md}"
                )
            if explicit_slug != explicit_slug.strip():
                raise RuntimeError(
                    f"Frente {front} contém Markdown com slug com espaços nas extremidades: {md}"
                )
            slug = explicit_slug
        else:
            slug = _slugify(title)
            if not isinstance(slug, str) or not slug.strip():
                raise RuntimeError(f"Frente {front} contém Markdown sem slug válido: {md}")

        slugs.append(slug)
    return _validate_unique_slugs(front, slugs)


def _canonical_source_slugs(front: str, source: Path) -> set[str]:
    manifest = _manifest_slugs(front, source)
    if manifest is not None:
        return manifest
    if source.is_dir():
        return _markdown_slugs(front, source)
    raise RuntimeError(f"Fonte da frente {front} não permite inventariar slugs: {source}")


def _collect_blocking_diagnostics(value: Any, path: str = "") -> dict[str, Any]:
    diagnostics: dict[str, Any] = {}
    if isinstance(value, dict):
        for key, item in value.items():
            current = f"{path}.{key}" if path else str(key)
            if key in BLOCKING_DIAGNOSTIC_KEYS:
                if item:
                    diagnostics[current] = item
                continue
            if isinstance(item, (dict, list, tuple)):
                diagnostics.update(_collect_blocking_diagnostics(item, current))
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            if isinstance(item, (dict, list, tuple)):
                current = f"{path}[{index}]" if path else f"[{index}]"
                diagnostics.update(_collect_blocking_diagnostics(item, current))
    return diagnostics


def _assert_no_rejections(front: str, result: dict[str, Any]) -> None:
    diagnostics = _collect_blocking_diagnostics(result)
    if diagnostics:
        raise RuntimeError(
            f"Frente {front} recusou conteúdo: "
            + json.dumps(diagnostics, ensure_ascii=False, sort_keys=True)
        )


def _load_front(front: str, config: dict[str, Any]) -> tuple[dict, set[str]]:
    source = _ensure_source(front, str(config["path"]))
    canonical_slugs = _canonical_source_slugs(front, source)
    if config["loader"] is None:
        result = import_directory(str(source))
    else:
        module = importlib.import_module(f"app.services.{config['loader']}")
        result = module.carregar(str(source))
    result = {**result, "itens_fonte": len(canonical_slugs)}
    _assert_no_rejections(front, result)
    return result, canonical_slugs


def _load_controlled_substances(db: Session) -> dict:
    source = _ensure_source("controlados", "/controlados/listas-344-98.json")
    from app.services.carregar_controlados import carregar

    result = carregar(db, str(source))
    _assert_no_rejections("controlados", result)
    return result


def _synchronize_publication(
    db: Session,
    canonical_slugs: dict[str, set[str]],
    *,
    publish_reviewed: bool,
) -> tuple[dict[str, int], dict[str, int]]:
    """Publica somente o corpus atual e despublica slugs ausentes do commit."""
    published: dict[str, int] = {}
    unpublished_absent: dict[str, int] = {}
    try:
        for front, config in FRONTS.items():
            model = config["model"]
            slugs = canonical_slugs[front]
            if publish_reviewed:
                changed = (
                    db.query(model)
                    .filter(
                        model.slug.in_(slugs),
                        model.published.is_(False),
                        model.review_status == "revisado",
                    )
                    .update({model.published: True}, synchronize_session=False)
                )
                published[front] = int(changed)
            else:
                published[front] = 0

            removed = (
                db.query(model)
                .filter(model.published.is_(True), model.slug.notin_(slugs))
                .update({model.published: False}, synchronize_session=False)
            )
            unpublished_absent[front] = int(removed)
        db.commit()
    except Exception:
        db.rollback()
        raise
    return published, unpublished_absent


def _database_inventory(
    db: Session,
    canonical_slugs: dict[str, set[str]],
) -> dict[str, Any]:
    fronts: dict[str, Any] = {}
    total = 0
    published_total = 0
    stored_total = 0
    below_minimum: dict[str, dict[str, int]] = {}
    for front, config in FRONTS.items():
        model = config["model"]
        slugs = canonical_slugs[front]
        canonical = db.query(model).filter(model.slug.in_(slugs)).count()
        published = db.query(model).filter(
            model.slug.in_(slugs), model.published.is_(True)
        ).count()
        stored = db.query(model).count()
        minimum = int(config["minimum"])
        fronts[front] = {
            "database": canonical,
            "published": published,
            "stored": stored,
            "archived_absent": max(stored - canonical, 0),
            "minimum": minimum,
        }
        total += canonical
        published_total += published
        stored_total += stored
        if canonical < minimum:
            below_minimum[front] = {"database": canonical, "minimum": minimum}
    return {
        "total": total,
        "published_total": published_total,
        "stored_total": stored_total,
        "archived_absent_total": max(stored_total - total, 0),
        "minimum": SCIENTIFIC_MINIMUM,
        "fronts": fronts,
        "below_minimum": below_minimum,
    }


def reconcile(*, publish_reviewed: bool = False, allow_partial: bool = False) -> dict[str, Any]:
    loads: dict[str, Any] = {}
    canonical_slugs: dict[str, set[str]] = {}
    for front, config in FRONTS.items():
        loads[front], canonical_slugs[front] = _load_front(front, config)

    db = SessionLocal()
    try:
        loads["controlados"] = _load_controlled_substances(db)
        published, unpublished_absent = _synchronize_publication(
            db, canonical_slugs, publish_reviewed=publish_reviewed
        )
        database = _database_inventory(db, canonical_slugs)
    finally:
        db.close()

    result = {
        "loads": loads,
        "published_reviewed": published,
        "unpublished_absent": unpublished_absent,
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
    parser.add_argument("--publish-reviewed", action="store_true",
                        help="Publica somente registros com review_status=revisado.")
    parser.add_argument("--allow-partial", action="store_true",
                        help="Não falha quando o banco fica abaixo do baseline versionado.")
    args = parser.parse_args()

    try:
        result = reconcile(publish_reviewed=args.publish_reviewed,
                           allow_partial=args.allow_partial)
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"status": "error", "type": type(exc).__name__, "detail": str(exc)},
                         ensure_ascii=False, indent=2))
        return 1

    print(json.dumps({"status": "ok", **result}, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
