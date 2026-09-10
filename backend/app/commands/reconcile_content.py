"""Reconcilia todo o corpus versionado com o banco de dados.

Uso operacional:

    python -m app.commands.reconcile_content --publish-reviewed

A carga é idempotente. Registros removidos ou renomeados permanecem armazenados
para auditoria, mas são despublicados e deixam de contar para a certificação do
corpus canônico do commit atual.

O manifesto padrão schema 2 exige --publish-reviewed: a carga congela a
publicação canônica, importa uma cópia imutável validada e promove somente
as identidades explicitamente aprovadas. Sem a opção, falha antes de abrir
uma sessão de banco. --authorization-manifest (alias --full-authorization)
permite selecionar explicitamente um manifesto schema 1, cujo contrato
integral permanece inalterado. publish_preserved_content não publica schema 2.
"""

from __future__ import annotations

import argparse
import importlib
import json
from hashlib import sha256
from collections import Counter
from contextlib import contextmanager
import shutil
from tempfile import TemporaryDirectory
from pathlib import Path
from typing import Any

import frontmatter
from sqlalchemy import or_, select
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
from app.models.guideline import GuidelineLink
from app.models.patient_material import PatientMaterial
from app.models.scientific_user_document import ScientificUserDocument
from app.models.specialty_guide import SpecialtyDisease, SymptomTriageGuide
from app.models.study import ScientificStudy
from app.models.study_track import StudyTrack
from app.models.study_track import StudyTrackProgress
from app.services.editorial_kind_overrides import (
    REGISTRY_PATH as EDITORIAL_KIND_REGISTRY_PATH, load_editorial_registry,
    validate_editorial_sources, editorial_registry_scope, validate_materialized_editorial_values,
)
from app.services.carregar_triagem_sintomas import load_triage_records
from app.services.corpus_release_authorization import (
    build_front_fingerprint,
    resolve_publication_policy,
    validate_full_corpus_publication as _validate_full_corpus_publication,
    validate_full_corpus_authorization,
    validate_snapshot_authorization,
    validate_snapshot_publication,
)
from app.services.disease_manifest import load_disease_records
from app.services.importer import _resolve_markdown_slug, import_directory
from app.services.knowledge_graph import (
    arquivar_entidades_de_conteudo_despublicado,
    backfill_mesmo_tema,
)
from app.services.study_track_progress import canonicalize_progress_tokens
from app.services.scientific_loader_safety import publication_quarantine

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
EDITORIAL_APPROVALS_DIR = REPOSITORY_ROOT / "editorial-approvals"
FULL_CORPUS_AUTHORIZATION_PATH = (
    EDITORIAL_APPROVALS_DIR / "scoped-corpus-release-20260910.json"
)
BLOCKING_DIAGNOSTIC_KEYS = frozenset({
    "avisos", "duplicados_ignorados", "erros", "falhas", "ignoradas",
    "ignorados", "puladas", "pulados", "recusadas", "recusados",
    "sem_arquivo", "vazios",
})

FRONTS: dict[str, dict[str, Any]] = {
    "documentos": {"path": settings.content_dir, "model": Document, "minimum": 1079, "loader": None},
    "galeria": {"path": "/galeria/metadados.json", "model": GalleryImage, "minimum": 236, "loader": "carregar_galeria"},
    "exames": {"path": "/exames/metadados.json", "model": LabTest, "minimum": 244, "loader": "carregar_exames"},
    "evidencias": {"path": "/evidencias/metadados.json", "model": EvidenceRecord, "minimum": 1779, "loader": "carregar_evidencias"},
    "estudos": {"path": "/estudos/metadados.json", "model": ScientificStudy, "minimum": 383, "loader": "carregar_estudos"},
    "medicamentos": {"path": "/medicamentos/metadados.json", "model": Drug, "minimum": 114, "loader": "carregar_drugs"},
    "checklists": {"path": "/checklists/metadados.json", "model": DischargeChecklist, "minimum": 24, "loader": "carregar_checklists"},
    # `casos_clinicos` precisa vir ANTES de `trilhas`: uma etapa de trilha
    # pode referenciar `item_type: "caso_clinico"` (`carregar_trilhas._existe`),
    # e a validação de referência consulta o banco, não o JSON de origem —
    # se `casos_clinicos` ainda não tiver sido carregado nesta mesma rodada,
    # qualquer trilha que aponte para um caso clínico real e existente é
    # rejeitada por "referência inexistente" em falso. Bug real, reproduzido
    # localmente ao rodar `reconcile_content --publish-reviewed` contra o
    # conteúdo íntegro do RC (issue #52, nova fase) — os 6 slugs citados no
    # erro sempre existiam em `casos-clinicos/metadados.json`, só ainda não
    # tinham chegado ao banco nesta ordem antiga.
    "casos_clinicos": {"path": "/casos-clinicos/metadados.json", "model": ClinicalCase, "minimum": 556, "loader": "carregar_casos_clinicos"},
    "trilhas": {"path": "/trilhas/metadados.json", "model": StudyTrack, "minimum": 470, "loader": "carregar_trilhas"},
    "material_paciente": {"path": "/material-paciente/metadados.json", "model": PatientMaterial, "minimum": 28, "loader": "carregar_material_paciente"},
    "emergencia": {"path": "/emergencia/metadados.json", "model": EmergencyProtocol, "minimum": 32, "loader": "carregar_emergencia"},
    "doencas_especializadas": {
        "path": "/doencas/metadados.json",
        "model": SpecialtyDisease,
        "minimum": 94,
        "loader": "carregar_doencas_especializadas",
    },
    "triagem_sintomas": {
        "path": "/triagem-sintomas/metadados.json",
        "model": SymptomTriageGuide,
        "minimum": 15,
        "loader": "carregar_triagem_sintomas",
    },
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

    if front == "doencas_especializadas":
        data = load_disease_records(source)
    elif front == "triagem_sintomas":
        data = load_triage_records(source)
    else:
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
    """Usa exatamente a mesma resolução de slug do importador Markdown."""
    slugs: list[str] = []
    for md in sorted(source.rglob("*.md")):
        post = frontmatter.load(md)
        title = post.metadata.get("title") or md.stem
        slug = _resolve_markdown_slug(
            post.metadata,
            title,
            source=f"Frente {front}, arquivo {md}",
        )
        slugs.append(slug)
    return _validate_unique_slugs(front, slugs)


def _canonical_source_slugs(front: str, source: Path) -> set[str]:
    manifest = _manifest_slugs(front, source)
    if manifest is not None:
        return manifest
    if source.is_dir():
        return _markdown_slugs(front, source)
    raise RuntimeError(f"Fonte da frente {front} não permite inventariar slugs: {source}")


def _canonical_source_metadata(front: str, source: Path) -> list[tuple[str, dict[str, Any]]]:
    """Carrega metadados usando os mesmos manifestos e slugs dos loaders."""
    records: list[tuple[str, dict[str, Any]]] = []
    if source.suffix.lower() == ".json":
        if front == "doencas_especializadas":
            payload = load_disease_records(source)
        elif front == "triagem_sintomas":
            payload = load_triage_records(source)
        else:
            payload = json.loads(source.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            raise RuntimeError(f"Manifesto da frente {front} deve ser uma lista JSON.")
        for index, item in enumerate(payload):
            if not isinstance(item, dict):
                raise RuntimeError(f"Frente {front} contém item inválido no índice {index}.")
            slug = item.get("slug")
            if not isinstance(slug, str) or not slug.strip() or slug != slug.strip():
                raise RuntimeError(
                    f"Frente {front} contém slug inválido no índice {index}."
                )
            records.append((slug, item))
    elif source.is_dir():
        for md in sorted(source.rglob("*.md")):
            post = frontmatter.load(md)
            title = post.metadata.get("title") or md.stem
            slug = _resolve_markdown_slug(
                post.metadata,
                title,
                source=f"Frente {front}, arquivo {md}",
            )
            records.append((slug, post.metadata))
    else:
        raise RuntimeError(
            f"Fonte da frente {front} não permite ler metadados canônicos: {source}"
        )

    duplicates = sorted(
        slug for slug, count in Counter(slug for slug, _metadata in records).items()
        if count > 1
    )
    if duplicates:
        raise RuntimeError(
            f"Frente {front} contém slugs duplicados: "
            + json.dumps(duplicates, ensure_ascii=False)
        )
    return records


def _canonical_publication_intents(front: str, source: Path) -> dict[str, bool | None]:
    """Lê intenção explícita sem transformar ausência legada em promoção.

    ``True`` autoriza a etapa de publicação somente quando há também revisão e
    aprovação versionada; ``False`` é quarentena; ausência preserva o estado
    anterior e nunca promove um registro novo ainda falso.
    """
    records = _canonical_source_metadata(front, source)

    intents: dict[str, bool | None] = {}
    for slug, metadata in records:
        if "published" not in metadata:
            intents[slug] = None
            continue
        value = metadata["published"]
        if not isinstance(value, bool):
            raise RuntimeError(
                f"Frente {front}/{slug}: published deve ser booleano quando informado."
            )
        intents[slug] = value
    return intents


def _canonical_review_statuses(front: str, source: Path) -> dict[str, str | None]:
    """Lê o status editorial de cada item da fonte canônica."""
    return {
        slug: metadata.get("review_status")
        for slug, metadata in _canonical_source_metadata(front, source)
    }


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


def _prepare_front(
    front: str, config: dict[str, Any]
) -> tuple[Path, set[str], dict[str, bool | None]]:
    source = _ensure_source(front, str(config["path"]))
    canonical_slugs = _canonical_source_slugs(front, source)
    publication_intents = _canonical_publication_intents(front, source)
    if set(publication_intents) != canonical_slugs:
        raise RuntimeError(f"Frente {front}: inventário e intenção de publicação divergiram.")
    return source, canonical_slugs, publication_intents


def _load_front(
    front: str,
    config: dict[str, Any],
    *,
    prepared: tuple[Path, set[str], dict[str, bool | None]] | None = None,
) -> tuple[dict, set[str], dict[str, bool | None]]:
    source, canonical_slugs, publication_intents = (
        prepared if prepared is not None else _prepare_front(front, config)
    )
    if config["loader"] is None:
        result = import_directory(str(source))
    else:
        module = importlib.import_module(f"app.services.{config['loader']}")
        result = module.carregar(str(source), asset_root=source.parent) if front == "galeria" else module.carregar(str(source))
    result = {**result, "itens_fonte": len(canonical_slugs)}
    _assert_no_rejections(front, result)
    return result, canonical_slugs, publication_intents


def _load_editorial_approvals() -> dict[str, set[str]]:
    """Carrega decisões editoriais versionadas por lote.

    O conteúdo produzido por agentes permanece com o status de origem no arquivo
    para preservar proveniência. A aprovação humana para publicação vive em um
    manifesto separado, auditável, e só vale para slugs que continuam canônicos
    no commit atual.
    """
    approvals: dict[str, set[str]] = {front: set() for front in FRONTS}
    if not EDITORIAL_APPROVALS_DIR.exists():
        return approvals

    for path in sorted(EDITORIAL_APPROVALS_DIR.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("decision") != "approved_for_publication":
            continue
        fronts = payload.get("fronts") or {}
        unknown = sorted(set(fronts) - set(FRONTS))
        if unknown:
            raise RuntimeError(
                f"Aprovação editorial {path.name} contém frentes desconhecidas: {unknown}"
            )
        for front, slugs in fronts.items():
            if not isinstance(slugs, list) or not all(isinstance(x, str) and x for x in slugs):
                raise RuntimeError(
                    f"Aprovação editorial {path.name}/{front} deve ser lista de slugs."
                )
            approvals[front].update(slugs)
    return approvals


def _validate_editorial_approvals(
    canonical_slugs: dict[str, set[str]],
    approvals: dict[str, set[str]] | None = None,
) -> dict[str, int]:
    """Valida aprovações sem convertê-las em revisão clínica."""
    approvals = approvals if approvals is not None else _load_editorial_approvals()
    validated: dict[str, int] = {}
    for front, slugs in approvals.items():
        absent = sorted(slugs - canonical_slugs[front])
        if absent:
            raise RuntimeError(
                f"Aprovação editorial de {front} aponta slugs ausentes do corpus: {absent}"
            )
        validated[front] = len(slugs)
    return validated


def _canonical_source_fingerprints(front: str, source: Path) -> dict[str, str]:
    if source.is_dir():
        result = {}
        for md in sorted(source.rglob("*.md")):
            post = frontmatter.load(md)
            slug = _resolve_markdown_slug(post.metadata, post.metadata.get("title") or md.stem, source=str(md))
            result[slug] = sha256(md.read_bytes()).hexdigest()
        return result
    return {slug: sha256(json.dumps(metadata, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            for slug, metadata in _canonical_source_metadata(front, source)}


def _load_full_corpus_authorization(
    canonical_slugs: dict[str, set[str]],
    sources: dict[str, Path],
    *,
    authorization_path: Path | None = None,
    evidence_root: Path | None = None,
) -> tuple[dict[str, set[str]], dict[str, Any] | None]:
    """Validate the selected exact snapshot before any database mutation.

    The scoped default is mandatory. Schema 1 stays strict when explicitly
    selected; an absent or malformed schema 2 never falls back to old approval.
    """
    path = Path(authorization_path) if authorization_path is not None else FULL_CORPUS_AUTHORIZATION_PATH
    if not path.exists():
        raise RuntimeError(f"Autorização de publicação não encontrada: {path}")
    if set(sources) != set(FRONTS) or set(canonical_slugs) != set(FRONTS):
        raise RuntimeError("Inventário incompleto para validar autorização do corpus.")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError("Autorização de publicação deve ser objeto JSON.")
    fingerprints = {}
    review_statuses = {}
    for front in FRONTS:
        statuses = _canonical_review_statuses(front, sources[front])
        review_statuses[front] = statuses
        fingerprint_source = sources[front].parent if front in {"doencas_especializadas", "triagem_sintomas"} else sources[front]
        fingerprints[front] = build_front_fingerprint(fingerprint_source, canonical_slugs[front], statuses)
    if payload.get("schema_version") == 2:
        return validate_snapshot_authorization(
            path, canonical_slugs=canonical_slugs, fingerprints=fingerprints,
            review_statuses=review_statuses,
            source_fingerprints={front: _canonical_source_fingerprints(front, sources[front]) for front in FRONTS},
            repository_root=evidence_root or REPOSITORY_ROOT,
        )
    return validate_full_corpus_authorization(path, canonical_slugs=canonical_slugs, fingerprints=fingerprints)


def _validate_release_publication(database, authorization):
    if authorization and authorization.get("schema_version") == 2:
        validate_snapshot_publication(database, authorization)
    else:
        _validate_full_corpus_publication(database, authorization)


def _authorization_quarantine(authorization) -> dict[str, set[str]]:
    if not authorization or authorization.get("schema_version") != 2:
        return {}
    return {front: set(slugs) for front, slugs in authorization["quarantined"].items()}


def _load_controlled_substances(db: Session) -> dict:
    source = _ensure_source("controlados", "/controlados/listas-344-98.json")
    from app.services.carregar_controlados import carregar

    result = carregar(db, str(source))
    _assert_no_rejections("controlados", result)
    return result


def _runtime_managed_document_filter():
    """Documentos científicos criados em runtime não pertencem ao corpus Git.

    O reconcile canônico deve arquivar documentos estáticos removidos do commit,
    mas não pode despublicar sínteses CorVIA Intelligence nem documentos
    incorporados explicitamente a partir do acervo privado do assinante.
    """
    incorporated_ids = select(ScientificUserDocument.incorporated_document_id).where(
        ScientificUserDocument.incorporated_document_id.is_not(None)
    )
    guideline_summary_ids = select(GuidelineLink.item_id).where(
        GuidelineLink.item_type == "intelligence_document"
    )
    return or_(
        Document.slug.like("corvia-intelligence-%"),
        Document.id.in_(incorporated_ids),
        Document.id.in_(guideline_summary_ids),
    )


def _synchronize_publication(
    db: Session,
    canonical_slugs: dict[str, set[str]],
    *,
    publish_reviewed: bool,
    approved_slugs: dict[str, set[str]],
    publication_intents: dict[str, dict[str, bool | None]],
    full_corpus_authorized_slugs: dict[str, set[str]] | None = None,
    quarantined_slugs: dict[str, set[str]] | None = None,
    dry_run: bool = False,
    commit: bool = True,
) -> tuple[dict[str, int], dict[str, int], dict[str, int], dict[str, int]]:
    """Aplica a única política de publicação das fontes canônicas.

    ``dry_run`` executa as mesmas operações e devolve as mesmas contagens, mas
    reverte a transação inteira ao final. Com ``commit=False``, o chamador pode
    compor a política com outras mutações fail-closed na mesma transação.
    """
    published: dict[str, int] = {}
    unpublished_absent: dict[str, int] = {}
    unpublished_unreviewed: dict[str, int] = {}
    unpublished_ineligible: dict[str, int] = {}
    full_corpus_authorized_slugs = full_corpus_authorized_slugs or {}
    quarantined_slugs = quarantined_slugs or {}
    try:
        for front, config in FRONTS.items():
            model = config["model"]
            slugs = canonical_slugs[front]
            intents = publication_intents[front]
            if set(intents) != slugs:
                raise RuntimeError(
                    f"Frente {front}: intenção de publicação não cobre o corpus canônico."
                )
            release_authorized = full_corpus_authorized_slugs.get(front, set())
            approved = approved_slugs.get(front, set())
            eligible, ineligible = resolve_publication_policy(
                slugs,
                intents,
                approved,
                release_authorized,
                quarantined_slugs=quarantined_slugs.get(front, set()),
            )
            if publish_reviewed:
                changed = (
                    db.query(model)
                    .filter(
                        model.slug.in_(eligible),
                        model.published.is_(False),
                        model.review_status == "revisado",
                    )
                    .update({model.published: True}, synchronize_session=False)
                )
                published[front] = int(changed)
            else:
                published[front] = 0

            blocked = (
                db.query(model)
                .filter(
                    model.slug.in_(ineligible),
                    model.published.is_(True),
                )
                .update({model.published: False}, synchronize_session=False)
            )
            unpublished_ineligible[front] = int(blocked)

            demoted = (
                db.query(model)
                .filter(
                    model.slug.in_(slugs),
                    model.published.is_(True),
                    or_(
                        model.review_status.is_(None),
                        model.review_status != "revisado",
                    ),
                )
                .update({model.published: False}, synchronize_session=False)
            )
            unpublished_unreviewed[front] = int(demoted)

            # Documentos CorVIA Intelligence são produzidos em runtime pelo
            # pipeline científico e não vivem na árvore Markdown canônica.
            # Ausência no Git não significa remoção editorial para esse namespace.
            removed_query = db.query(model).filter(
                model.published.is_(True),
                model.slug.notin_(slugs),
            )
            if front == "documentos":
                removed_query = removed_query.filter(
                    ~_runtime_managed_document_filter()
                )
            removed = removed_query.update(
                {model.published: False}, synchronize_session=False
            )
            unpublished_absent[front] = int(removed)
        if dry_run:
            db.rollback()
        elif commit:
            db.commit()
        else:
            db.flush()
    except Exception:
        db.rollback()
        raise
    return (
        published,
        unpublished_absent,
        unpublished_unreviewed,
        unpublished_ineligible,
    )


def _database_inventory(
    db: Session,
    canonical_slugs: dict[str, set[str]],
    *,
    include_published_slugs: bool = False,
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
        runtime_managed = 0
        if front == "documentos":
            runtime_managed = db.query(model).filter(
                _runtime_managed_document_filter(),
                model.slug.notin_(slugs),
            ).count()
        minimum = int(config["minimum"])
        fronts[front] = {
            "database": canonical,
            "published": published,
            "stored": stored,
            "runtime_managed": runtime_managed,
            "archived_absent": max(stored - canonical - runtime_managed, 0),
            "minimum": minimum,
        }
        if include_published_slugs:
            fronts[front]["published_slugs"] = sorted(slug for (slug,) in db.query(model.slug).filter(model.slug.in_(slugs), model.published.is_(True)).all())
        total += canonical
        published_total += published
        stored_total += stored
        if canonical < minimum:
            below_minimum[front] = {"database": canonical, "minimum": minimum}
    return {
        "total": total,
        "published_total": published_total,
        "stored_total": stored_total,
        "archived_absent_total": sum(
            item["archived_absent"] for item in fronts.values()
        ),
        "runtime_managed_total": sum(
            item["runtime_managed"] for item in fronts.values()
        ),
        "minimum": SCIENTIFIC_MINIMUM,
        "fronts": fronts,
        "below_minimum": below_minimum,
    }


def _migrate_study_track_progress(db: Session) -> int:
    """Troca slugs de estudos consolidados dentro do JSONB de progresso.

    A alteração participa da mesma transação da sincronização de publicação:
    se a reconciliação falhar, o progresso não fica parcialmente migrado.
    """
    updated = 0
    for progress in db.query(StudyTrackProgress).all():
        current = list(progress.concluidas or [])
        migrated = canonicalize_progress_tokens(current)
        # Compare as lists so the migration also removes pre-existing
        # duplicates and persists the deterministic ordering promised by
        # ``canonicalize_progress_tokens``. Comparing only sets would silently
        # leave ``[slug, slug]`` unchanged.
        if migrated != current:
            progress.concluidas = migrated
            updated += 1
    return updated



@contextmanager
def _immutable_release_sources(prepared, authorization_path: Path):
    """Copy approved text/metadata and its evidence before touching the DB.

    Native loaders only consume this private snapshot. Referenced gallery assets are copied as regular files; their stored
    file_path strings are left unchanged. No database field receives a snapshot path.
    """
    with TemporaryDirectory(prefix="corvia-corpus-snapshot-") as temporary:
        snapshot_root = Path(temporary)
        copied = {}
        def relative_source(source, front):
            try:
                return source.relative_to(REPOSITORY_ROOT)
            except ValueError:
                configured = Path(str(FRONTS[front]["path"]).lstrip("/"))
                if ".." in configured.parts:
                    raise RuntimeError("Caminho de fonte inválido.")
                return configured
        for front, (source, _slugs, _intents) in prepared.items():
            target = snapshot_root / relative_source(source, front)
            target.parent.mkdir(parents=True, exist_ok=True)
            if source.is_dir():
                shutil.copytree(source, target, dirs_exist_ok=True)
            elif front in {"doencas_especializadas", "triagem_sintomas"}:
                shutil.copytree(source.parent, target.parent, dirs_exist_ok=True)
            else:
                shutil.copy2(source, target)
                corrections = source.parent / "correcoes"
                if corrections.is_dir():
                    shutil.copytree(corrections, target.parent / "correcoes", dirs_exist_ok=True)
            copied[front] = target

        def copy_evidence(relative):
            path = Path(relative)
            if path.is_absolute() or ".." in path.parts:
                raise RuntimeError("Caminho de evidência inválido.")
            source = (REPOSITORY_ROOT / path).resolve()
            if not source.is_relative_to(REPOSITORY_ROOT.resolve()) or not source.is_file():
                raise RuntimeError("Fonte de evidência ausente ou fora do repositório.")
            target = snapshot_root / path
            if not target.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
            return target

        auth_target = snapshot_root / "editorial-approvals" / authorization_path.name
        auth_target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(authorization_path, auth_target)
        manifest = json.loads(auth_target.read_text())
        evidence_paths = {
            claim["evidence_path"]
            for claims in manifest.get("provenance", {}).values()
            for claim in claims.values()
        }
        for path in evidence_paths:
            evidence = json.loads(copy_evidence(path).read_text())
            for reference in evidence.get("references", []):
                copy_evidence(reference["path"])
        # Separate metadata ledger: frozen independently, never added to or
        # substituted for the existing scientific publication authorization.
        editorial_registry = load_editorial_registry()
        editorial_dir = snapshot_root / "backend/app/services"
        editorial_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(editorial_registry["registry_path"], editorial_dir / "editorial_kind_registry.json")
        shutil.copy2(editorial_registry["evidence_path"], editorial_dir / Path(editorial_registry["evidence_file"]))
        # Read-only files prevent accidental mutation by native loaders. The
        # validated snapshot, rather than later reads of live sources, is used.
        for path in snapshot_root.rglob("*"):
            if path.is_file() and not path.is_symlink():
                path.chmod(0o444)
        snapshot_prepared = {}
        for front, target in copied.items():
            slugs = _canonical_source_slugs(front, target)
            intents = _canonical_publication_intents(front, target)
            snapshot_prepared[front] = (target, slugs, intents)
        yield snapshot_prepared, auth_target, snapshot_root


def reconcile(*, publish_reviewed: bool = False, allow_partial: bool = False,
              authorization_path: Path | None = None) -> dict[str, Any]:
    selected = Path(authorization_path) if authorization_path is not None else FULL_CORPUS_AUTHORIZATION_PATH
    if not selected.is_file():
        raise RuntimeError(f"Autorização de publicação não encontrada: {selected}")
    manifest = json.loads(selected.read_text(encoding="utf-8"))
    prepared = {front: _prepare_front(front, config) for front, config in FRONTS.items()}
    if isinstance(manifest, dict) and manifest.get("schema_version") == 2:
        if not publish_reviewed:
            raise RuntimeError("Reconciliação de snapshot schema 2 exige --publish-reviewed; nenhuma carga foi iniciada.")
        with _immutable_release_sources(prepared, selected) as (snapshot, authorization, evidence_root):
            return _reconcile_prepared(snapshot, publish_reviewed=publish_reviewed,
                allow_partial=allow_partial, authorization_path=authorization, evidence_root=evidence_root)
    return _reconcile_prepared(prepared, publish_reviewed=publish_reviewed,
        allow_partial=allow_partial, authorization_path=selected, evidence_root=REPOSITORY_ROOT)


def _reconcile_prepared(prepared, *, publish_reviewed: bool, allow_partial: bool,
                        authorization_path: Path, evidence_root: Path) -> dict[str, Any]:
    frozen_registry_path = evidence_root / "backend/app/services/editorial_kind_registry.json"
    registry = load_editorial_registry(frozen_registry_path if frozen_registry_path.is_file() else EDITORIAL_KIND_REGISTRY_PATH)
    editorial_preflight = validate_editorial_sources(evidence_root, registry)
    loads: dict[str, Any] = {}
    canonical_slugs = {
        front: state[1]
        for front, state in prepared.items()
    }
    publication_intents = {
        front: state[2]
        for front, state in prepared.items()
    }
    sources = {front: state[0] for front, state in prepared.items()}
    (
        full_corpus_authorized_slugs,
        full_corpus_authorization,
    ) = _load_full_corpus_authorization(canonical_slugs, sources, authorization_path=authorization_path, evidence_root=evidence_root)
    quarantined_slugs = _authorization_quarantine(full_corpus_authorization)
    freeze_during_load = canonical_slugs if full_corpus_authorization and full_corpus_authorization.get("schema_version") == 2 else quarantined_slugs
    approved_slugs = _load_editorial_approvals()
    approved_slugs = {
        front: approved_slugs[front] | full_corpus_authorized_slugs[front]
        for front in FRONTS
    }
    editorial_approvals = _validate_editorial_approvals(
        canonical_slugs, approvals=approved_slugs
    )

    # Fecha quarentena, revogação, remoção e os respectivos nós do grafo ANTES
    # do primeiro loader. As duas mutações compartilham a mesma transação: uma
    # falha intermediária não pode deixar conteúdo despublicado ainda ativo no
    # grafo, nem arquivar o grafo sem efetivar a despublicação correspondente.
    preflight_db = SessionLocal()
    try:
        (
            _preflight_published,
            preflight_absent,
            preflight_unreviewed,
            preflight_ineligible,
        ) = _synchronize_publication(
            preflight_db,
            canonical_slugs,
            publish_reviewed=False,
            approved_slugs=approved_slugs,
            publication_intents=publication_intents,
            full_corpus_authorized_slugs=full_corpus_authorized_slugs,
            quarantined_slugs=freeze_during_load,
            commit=False,
        )
        arquivar_entidades_de_conteudo_despublicado(preflight_db, commit=False)
        preflight_db.commit()
    except Exception:
        preflight_db.rollback()
        raise
    finally:
        preflight_db.close()

    with editorial_registry_scope(registry), publication_quarantine(freeze_during_load, {front: config["model"] for front, config in FRONTS.items()}):
        for front, config in FRONTS.items():
            (
                loads[front],
                loaded_slugs,
                loaded_intents,
            ) = _load_front(front, config, prepared=prepared[front])
            if loaded_slugs != canonical_slugs[front] or loaded_intents != publication_intents[front]:
                raise RuntimeError(f"Frente {front}: estado preparado divergiu durante a carga.")

    rechecked_registry = load_editorial_registry(registry["registry_path"])
    if validate_editorial_sources(evidence_root, rechecked_registry) != editorial_preflight:
        raise RuntimeError("Editorial metadata evidence changed during import")

    # The bytes consumed by the native loaders must still match the approved
    # snapshot. Recheck before promotion rather than trusting prepared slugs.
    rechecked_slugs, rechecked_authorization = _load_full_corpus_authorization(
        canonical_slugs, sources, authorization_path=authorization_path, evidence_root=evidence_root)
    if rechecked_slugs != full_corpus_authorized_slugs or rechecked_authorization != full_corpus_authorization:
        raise RuntimeError("A autorização ou o conteúdo mudou durante a importação.")

    db = SessionLocal()
    try:
        loads["editorial_metadata"] = {**editorial_preflight, "materialized": validate_materialized_editorial_values(db, registry)}
        loads["controlados"] = _load_controlled_substances(db)
        migrated_study_track_progress = _migrate_study_track_progress(db)
        (
            published,
            final_absent,
            final_unreviewed,
            final_ineligible,
        ) = _synchronize_publication(
            db,
            canonical_slugs,
            publish_reviewed=publish_reviewed,
            approved_slugs=approved_slugs,
            publication_intents=publication_intents,
            full_corpus_authorized_slugs=full_corpus_authorized_slugs,
            quarantined_slugs=quarantined_slugs,
            commit=False,
        )
        arquivar_entidades_de_conteudo_despublicado(db, commit=False)
        database = _database_inventory(db, canonical_slugs, include_published_slugs=bool(full_corpus_authorization and full_corpus_authorization.get("schema_version") == 2))
        if database["below_minimum"] and not allow_partial:
            raise RuntimeError(
                "Reconciliação incompleta: "
                + json.dumps(database["below_minimum"], ensure_ascii=False, sort_keys=True)
            )
        _validate_release_publication(database, full_corpus_authorization)
        db.commit()
        knowledge_graph = backfill_mesmo_tema(db, source_root=evidence_root) if full_corpus_authorization and full_corpus_authorization.get("schema_version") == 2 else backfill_mesmo_tema(db)
        arquivar_entidades_de_conteudo_despublicado(db)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

    unpublished_absent = {
        front: preflight_absent[front] + final_absent[front]
        for front in FRONTS
    }
    unpublished_unreviewed = {
        front: preflight_unreviewed[front] + final_unreviewed[front]
        for front in FRONTS
    }
    unpublished_ineligible = {
        front: preflight_ineligible[front] + final_ineligible[front]
        for front in FRONTS
    }

    result = {
        "loads": loads,
        "editorial_approvals": editorial_approvals,
        "full_corpus_authorization": full_corpus_authorization,
        "quarantined_by_front": {front: len(slugs) for front, slugs in quarantined_slugs.items()},
        "immutable_source_snapshot": bool(full_corpus_authorization and full_corpus_authorization.get("schema_version") == 2),
        "published_reviewed": published,
        "unpublished_absent": unpublished_absent,
        "unpublished_unreviewed": unpublished_unreviewed,
        "unpublished_ineligible": unpublished_ineligible,
        "migrated_study_track_progress": migrated_study_track_progress,
        "database": database,
        "knowledge_graph": knowledge_graph,
        # Correção coordenada de 03/09/2026 (seção "arquitetura de deploy"):
        # `reconcile()` NUNCA mais chama o provedor de embeddings. Publicar/
        # reconciliar tem que ser rápido e determinístico — sem depender de
        # rede externa — porque roda inteiramente dentro da janela em que o
        # Caddy está fechado (`deploy.sh`, entre parar e reabrir o proxy). A
        # indexação RAG (documentos + as 12 frentes de `rag_sources`) agora é
        # responsabilidade exclusiva de
        # `app.commands.reindex_rag_completo_20260902`, disparado pelo
        # `deploy.sh` DEPOIS que o tráfego já reabriu — nunca dentro da janela
        # crítica, e uma falha ali nunca derruba o deploy nem aciona rollback.
        "rag": {
            "status": "nao_executado_aqui",
            "motivo": (
                "reconcile() não indexa RAG desde 03/09/2026 — rode "
                "'python -m app.commands.reindex_rag_completo_20260902' separadamente "
                "(o deploy.sh já faz isso, fora da janela de tráfego fechado)."
            ),
        },
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--publish-reviewed", action="store_true",
                        help="Publica somente registros revisados com aprovação versionada.")
    parser.add_argument("--allow-partial", action="store_true",
                        help="Não falha quando o banco fica abaixo do baseline versionado.")
    parser.add_argument("--authorization-manifest", "--full-authorization", dest="authorization_path", type=Path,
                        help="Manifesto exato schema 2; o alias --full-authorization também permite selecionar explicitamente schema 1.")
    args = parser.parse_args()

    try:
        result = reconcile(publish_reviewed=args.publish_reviewed,
                           allow_partial=args.allow_partial,
                           authorization_path=args.authorization_path)
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"status": "error", "type": type(exc).__name__, "detail": str(exc)},
                         ensure_ascii=False, indent=2))
        return 1

    print(json.dumps({"status": "ok", **result}, ensure_ascii=False, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
