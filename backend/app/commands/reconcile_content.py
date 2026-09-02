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
from sqlalchemy import or_
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
from app.models.specialty_guide import SpecialtyDisease, SymptomTriageGuide
from app.models.study import ScientificStudy
from app.models.study_track import StudyTrack
from app.models.study_track import StudyTrackProgress
from app.services.carregar_triagem_sintomas import load_triage_records
from app.services.corpus_release_authorization import (
    build_front_fingerprint,
    resolve_publication_policy,
    validate_full_corpus_publication as _validate_full_corpus_publication,
    validate_full_corpus_authorization,
)
from app.services.disease_manifest import load_disease_records
from app.services.importer import _resolve_markdown_slug, import_directory
from app.services.knowledge_graph import (
    arquivar_entidades_de_conteudo_despublicado,
    backfill_mesmo_tema,
)
from app.services import rag as rag_service
from app.services import rag_multi
from app.services.study_track_progress import canonicalize_progress_tokens

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
EDITORIAL_APPROVALS_DIR = REPOSITORY_ROOT / "editorial-approvals"
FULL_CORPUS_AUTHORIZATION_PATH = (
    EDITORIAL_APPROVALS_DIR / "full-corpus-release-20260901.json"
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
        result = module.carregar(str(source))
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


def _load_full_corpus_authorization(
    canonical_slugs: dict[str, set[str]],
    sources: dict[str, Path],
) -> tuple[dict[str, set[str]], dict[str, Any] | None]:
    """Valida a autorização integral ligada ao corpus exato do checkout.

    O manifesto é opcional para compatibilidade com releases anteriores. Quando
    presente, qualquer divergência de arquivo, slug, contagem ou revisão aborta a
    reconciliação antes da primeira mutação no banco.
    """
    empty = {front: set() for front in FRONTS}
    if not FULL_CORPUS_AUTHORIZATION_PATH.exists():
        return empty, None
    if set(sources) != set(FRONTS) or set(canonical_slugs) != set(FRONTS):
        raise RuntimeError("Inventário incompleto para validar autorização integral.")

    fingerprints = {}
    for front in FRONTS:
        statuses = _canonical_review_statuses(front, sources[front])
        fingerprint_source = (
            sources[front].parent
            if front in {"doencas_especializadas", "triagem_sintomas"}
            else sources[front]
        )
        fingerprints[front] = build_front_fingerprint(
            fingerprint_source,
            canonical_slugs[front],
            statuses,
        )
    return validate_full_corpus_authorization(
        FULL_CORPUS_AUTHORIZATION_PATH,
        canonical_slugs=canonical_slugs,
        fingerprints=fingerprints,
    )


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
    approved_slugs: dict[str, set[str]],
    publication_intents: dict[str, dict[str, bool | None]],
    full_corpus_authorized_slugs: dict[str, set[str]] | None = None,
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

            removed = (
                db.query(model)
                .filter(model.published.is_(True), model.slug.notin_(slugs))
                .update({model.published: False}, synchronize_session=False)
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


def _reindexar_rag_pendente(db: Session) -> dict[str, Any]:
    """Parte 3 da correção coordenada de 02/09/2026 — fecha o gap de
    idempotência do pipeline: até aqui, `reconcile()` publicava e
    reconciliava o grafo (`backfill_mesmo_tema`), mas nunca colocava o
    conteúdo novo na fila de RAG/embedding — isso ficava só num comando
    manual avulso (`reindex_rag_completo_20260902`). Chamado sempre que o
    corpus é reconciliado (`--publish-reviewed`), com `apenas_pendentes=True`
    (idempotente: só processa quem ainda não tem chunk).

    `indexar_tudo()`/`indexar_tudo_multi()` já são resilientes a falha do
    provedor de embeddings item a item (Part 3) — uma falha de crédito/rede
    aqui nunca derruba a reconciliação nem faz o conteúdo desaparecer da
    busca léxica, que não depende de embedding nenhum."""
    return {
        "documentos": rag_service.indexar_tudo(db, apenas_pendentes=True),
        "multi_frente": rag_multi.indexar_tudo_multi(db, apenas_pendentes=True),
    }


def reconcile(*, publish_reviewed: bool = False, allow_partial: bool = False) -> dict[str, Any]:
    loads: dict[str, Any] = {}
    prepared = {
        front: _prepare_front(front, config)
        for front, config in FRONTS.items()
    }
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
    ) = _load_full_corpus_authorization(canonical_slugs, sources)
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
            commit=False,
        )
        arquivar_entidades_de_conteudo_despublicado(preflight_db, commit=False)
        preflight_db.commit()
    except Exception:
        preflight_db.rollback()
        raise
    finally:
        preflight_db.close()

    for front, config in FRONTS.items():
        (
            loads[front],
            loaded_slugs,
            loaded_intents,
        ) = _load_front(front, config, prepared=prepared[front])
        if loaded_slugs != canonical_slugs[front] or loaded_intents != publication_intents[front]:
            raise RuntimeError(f"Frente {front}: estado preparado divergiu durante a carga.")

    db = SessionLocal()
    try:
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
            commit=False,
        )
        database = _database_inventory(db, canonical_slugs)
        if database["below_minimum"] and not allow_partial:
            raise RuntimeError(
                "Reconciliação incompleta: "
                + json.dumps(database["below_minimum"], ensure_ascii=False, sort_keys=True)
            )
        _validate_full_corpus_publication(database, full_corpus_authorization)
        db.commit()
        knowledge_graph = backfill_mesmo_tema(db)
        rag = _reindexar_rag_pendente(db)
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
        "published_reviewed": published,
        "unpublished_absent": unpublished_absent,
        "unpublished_unreviewed": unpublished_unreviewed,
        "unpublished_ineligible": unpublished_ineligible,
        "migrated_study_track_progress": migrated_study_track_progress,
        "database": database,
        "knowledge_graph": knowledge_graph,
        "rag": rag,
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--publish-reviewed", action="store_true",
                        help="Publica somente registros revisados com aprovação versionada.")
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
