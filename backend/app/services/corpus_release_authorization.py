"""Valida autorizações versionadas para publicar um corpus canônico inteiro.

Uma autorização integral é deliberadamente mais restrita que os manifestos
editoriais incrementais. Ela só é aceita quando contagens, slugs, arquivos de
origem e status de revisão continuam idênticos ao inventário autorizado. Assim,
qualquer alteração posterior fecha a publicação em vez de herdar uma aprovação
destinada a outra versão do corpus.
"""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Any, Mapping


SCHEMA_VERSION = 1
FULL_CORPUS_DECISION = "approved_for_full_corpus_publication"
FULL_CORPUS_SCOPE = "entire_canonical_reviewed_corpus"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

_TOP_LEVEL_FIELDS = frozenset({
    "schema_version",
    "release",
    "decision",
    "scope",
    "approval_basis",
    "expected_total",
    "inventory_sha256",
    "fronts",
})
_FRONT_FIELDS = frozenset({
    "count",
    "reviewed_count",
    "slug_sha256",
    "source_sha256",
})


def _sha256_json(value: Any) -> str:
    payload = json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return sha256(payload).hexdigest()


def slug_inventory_sha256(slugs: set[str]) -> str:
    """Identifica exatamente um conjunto de slugs, independentemente da ordem."""
    return _sha256_json(sorted(slugs))


def source_sha256(source: Path) -> str:
    """Identifica o arquivo canônico ou a árvore Markdown que o representa."""
    if source.is_file():
        return sha256(source.read_bytes()).hexdigest()
    if not source.is_dir():
        raise RuntimeError(f"Fonte canônica inexistente: {source}")

    files = sorted(
        (path for path in source.rglob("*") if path.is_file()),
        key=lambda path: path.relative_to(source).as_posix(),
    )
    digest = sha256()
    for path in files:
        relative = path.relative_to(source).as_posix().encode("utf-8")
        content = path.read_bytes()
        # Comprimentos tornam a serialização inequívoca mesmo se nomes ou
        # conteúdos contiverem separadores usuais.
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(len(content).to_bytes(8, "big"))
        digest.update(content)
    return digest.hexdigest()


def build_front_fingerprint(
    source: Path,
    slugs: set[str],
    review_statuses: Mapping[str, str | None],
) -> dict[str, int | str]:
    """Monta a impressão auditável de uma frente canônica."""
    if set(review_statuses) != slugs:
        raise RuntimeError("Inventário de revisão diverge dos slugs canônicos.")
    statuses = Counter(review_statuses.values())
    return {
        "count": len(slugs),
        "reviewed_count": int(statuses.get("revisado", 0)),
        "slug_sha256": slug_inventory_sha256(slugs),
        "source_sha256": source_sha256(source),
    }


def corpus_inventory_sha256(
    fingerprints: Mapping[str, Mapping[str, int | str]],
) -> str:
    """Vincula o release às impressões de todas as frentes."""
    return _sha256_json({front: dict(value) for front, value in fingerprints.items()})


def _require_exact_fields(value: Mapping[str, Any], expected: frozenset[str], where: str) -> None:
    missing = sorted(expected - set(value))
    unknown = sorted(set(value) - expected)
    if missing or unknown:
        raise RuntimeError(
            f"Autorização integral inválida em {where}: "
            f"campos ausentes={missing}, desconhecidos={unknown}."
        )


def validate_full_corpus_authorization(
    path: Path,
    *,
    canonical_slugs: Mapping[str, set[str]],
    fingerprints: Mapping[str, Mapping[str, int | str]],
) -> tuple[dict[str, set[str]], dict[str, Any]]:
    """Valida o manifesto integral e devolve somente os slugs vinculados.

    A função falha fechada em qualquer divergência. Ela não interpreta uma
    autorização antiga como permissão para um corpus que mudou.
    """
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(
            f"Não foi possível ler a autorização integral {path}: {exc}"
        ) from exc
    if not isinstance(payload, dict):
        raise RuntimeError("Autorização integral deve ser um objeto JSON.")
    _require_exact_fields(payload, _TOP_LEVEL_FIELDS, path.name)

    if type(payload["schema_version"]) is not int or payload["schema_version"] != SCHEMA_VERSION:
        raise RuntimeError("Autorização integral usa schema_version não suportado.")
    if payload["decision"] != FULL_CORPUS_DECISION:
        raise RuntimeError("Autorização integral não contém a decisão esperada.")
    if payload["scope"] != FULL_CORPUS_SCOPE:
        raise RuntimeError("Autorização integral não cobre o corpus canônico revisado.")
    if not isinstance(payload["release"], str) or not payload["release"].strip():
        raise RuntimeError("Autorização integral deve identificar o release.")
    if not isinstance(payload["approval_basis"], str) or not payload["approval_basis"].strip():
        raise RuntimeError("Autorização integral deve registrar a base da aprovação.")

    expected_fronts = set(canonical_slugs)
    if set(fingerprints) != expected_fronts:
        raise RuntimeError("Impressões do corpus não cobrem todas as frentes canônicas.")
    manifest_fronts = payload["fronts"]
    if not isinstance(manifest_fronts, dict) or set(manifest_fronts) != expected_fronts:
        missing = sorted(expected_fronts - set(manifest_fronts or {}))
        unknown = sorted(set(manifest_fronts or {}) - expected_fronts)
        raise RuntimeError(
            "Autorização integral diverge das frentes canônicas: "
            f"ausentes={missing}, desconhecidas={unknown}."
        )

    current_total = sum(len(slugs) for slugs in canonical_slugs.values())
    if type(payload["expected_total"]) is not int or payload["expected_total"] != current_total:
        raise RuntimeError(
            "Autorização integral diverge do total canônico: "
            f"manifesto={payload['expected_total']!r}, atual={current_total}."
        )

    for front in sorted(expected_fronts):
        expected = manifest_fronts[front]
        if not isinstance(expected, dict):
            raise RuntimeError(f"Autorização integral/{front} deve ser um objeto.")
        _require_exact_fields(expected, _FRONT_FIELDS, front)
        current = dict(fingerprints[front])
        if (
            type(current.get("count")) is not int
            or current["count"] != len(canonical_slugs[front])
        ):
            raise RuntimeError(f"Impressão atual inconsistente para {front}.")
        if current.get("reviewed_count") != current["count"]:
            raise RuntimeError(
                f"Autorização integral recusada: {front} contém item não revisado."
            )
        for digest_field in ("slug_sha256", "source_sha256"):
            if not isinstance(expected[digest_field], str) or not SHA256_RE.fullmatch(
                expected[digest_field]
            ):
                raise RuntimeError(
                    f"Autorização integral/{front}/{digest_field} não é SHA-256 válido."
                )
        if expected != current:
            raise RuntimeError(
                f"Autorização integral não corresponde à frente canônica {front}."
            )

    current_inventory_sha256 = corpus_inventory_sha256(fingerprints)
    if not isinstance(payload["inventory_sha256"], str) or not SHA256_RE.fullmatch(
        payload["inventory_sha256"]
    ):
        raise RuntimeError("inventory_sha256 da autorização integral é inválido.")
    if payload["inventory_sha256"] != current_inventory_sha256:
        raise RuntimeError("Autorização integral diverge da impressão global do corpus.")

    authorized = {front: set(canonical_slugs[front]) for front in expected_fronts}
    metadata = {
        "release": payload["release"],
        "authorized_total": current_total,
        "inventory_sha256": current_inventory_sha256,
        "fronts": {front: len(authorized[front]) for front in sorted(authorized)},
    }
    return authorized, metadata


def resolve_publication_policy(
    canonical_slugs: set[str],
    publication_intents: Mapping[str, bool | None],
    approved_slugs: set[str],
    release_authorized_slugs: set[str],
    *, quarantined_slugs: set[str] | None = None,
) -> tuple[set[str], set[str]]:
    """Resolve promoção e bloqueio sem permitir alvos não canônicos."""
    if set(publication_intents) != canonical_slugs:
        raise RuntimeError("Intenção de publicação não cobre o corpus canônico.")
    if release_authorized_slugs - canonical_slugs:
        raise RuntimeError("Autorização integral aponta slug não canônico.")

    quarantine = set(quarantined_slugs or ())
    if quarantine - canonical_slugs:
        raise RuntimeError("Quarentena aponta slug não canônico.")

    explicit_true = {
        slug for slug, value in publication_intents.items() if value is True
    }
    explicit_false = {
        slug for slug, value in publication_intents.items() if value is False
    }
    effective_true = explicit_true | release_authorized_slugs
    eligible = (effective_true & approved_slugs) - quarantine
    # A autorização integral validada é uma intenção positiva mais nova
    # e ligada ao corpus exato. Fora dela, ``False`` permanece quarentena.
    ineligible = (
        (explicit_false - release_authorized_slugs)
        | (effective_true - approved_slugs)
    )
    return eligible, ineligible | quarantine


def validate_full_corpus_publication(
    database: Mapping[str, Any],
    authorization: Mapping[str, Any] | None,
) -> None:
    """Impede sucesso parcial quando um release integral foi autorizado."""
    if authorization is None:
        return
    expected_fronts = authorization.get("fronts")
    expected_total = authorization.get("authorized_total")
    if not isinstance(expected_fronts, dict) or type(expected_total) is not int:
        raise RuntimeError("Metadados da autorização integral são inválidos.")

    database_fronts = database.get("fronts") or {}
    if (
        not isinstance(database_fronts, dict)
        or set(database_fronts) != set(expected_fronts)
        or any(not isinstance(value, Mapping) for value in database_fronts.values())
    ):
        raise RuntimeError("Inventário publicado não cobre as frentes autorizadas.")
    mismatches = {
        front: {
            "authorized": expected_count,
            "published": database_fronts[front].get("published"),
        }
        for front, expected_count in expected_fronts.items()
        if type(expected_count) is not int
        or database_fronts[front].get("published") != expected_count
    }
    if database.get("published_total") != expected_total or mismatches:
        raise RuntimeError(
            "Publicação integral incompleta: "
            + json.dumps(
                {
                    "authorized_total": expected_total,
                    "published_total": database.get("published_total"),
                    "front_mismatches": mismatches,
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )


SNAPSHOT_SCHEMA_VERSION = 2
SNAPSHOT_DECISION = "approved_snapshot_with_quarantine"
SNAPSHOT_SCOPE = "exact_canonical_snapshot"
_SNAPSHOT_FIELDS = _TOP_LEVEL_FIELDS | {"approved", "quarantined", "provenance"}
_PROVENANCE_FIELDS = frozenset({"basis", "evidence_path", "evidence_sha256", "source_sha256"})
_EVIDENCE_FIELDS = frozenset({"schema_version", "decision", "approval_basis", "approved_sources", "approved_bases", "references"})
_EVIDENCE_REFERENCE_FIELDS = frozenset({"path", "sha256", "basis"})
_EVIDENCE_BASES = frozenset({"baseline_unchanged", "approved_package", "authorized_tct_theme_normalization"})


def _digest(value: Any, where: str) -> str:
    if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
        raise RuntimeError(f"SHA-256 inválido: {where}.")
    return value


def _evidence_file(root: Path, relative: Any, digest: Any) -> Path:
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute() or ".." in Path(relative).parts:
        raise RuntimeError("Caminho de evidência inválido.")
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise RuntimeError("Evidência inexistente ou fora do repositório.")
    if sha256(path.read_bytes()).hexdigest() != _digest(digest, relative):
        raise RuntimeError(f"Hash da evidência divergente: {relative}.")
    return path


def _slug_set(value: Any, where: str) -> set[str]:
    if not isinstance(value, list) or any(not isinstance(s, str) or not s or s.strip() != s for s in value):
        raise RuntimeError(f"Lista de slugs inválida: {where}.")
    if len(set(value)) != len(value):
        raise RuntimeError(f"Slugs duplicados: {where}.")
    return set(value)


def validate_snapshot_authorization(
    path: Path, *, canonical_slugs: Mapping[str, set[str]],
    fingerprints: Mapping[str, Mapping[str, int | str]],
    review_statuses: Mapping[str, Mapping[str, str | None]],
    source_fingerprints: Mapping[str, Mapping[str, str]], repository_root: Path,
) -> tuple[dict[str, set[str]], dict[str, Any]]:
    """Certify an exact snapshot and an evidence-bound publishable subset.

    Quarantined sources remain in the inventory and are never promoted by an
    older or generic approval. This is publication authorization, not an
    assertion of a human medical review. Schema 1 retains its strict contract.
    """
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise RuntimeError("Não foi possível ler autorização de snapshot.") from exc
    if not isinstance(payload, dict):
        raise RuntimeError("Autorização de snapshot deve ser um objeto.")
    _require_exact_fields(payload, _SNAPSHOT_FIELDS, path.name)
    if type(payload["schema_version"]) is not int or payload["schema_version"] != SNAPSHOT_SCHEMA_VERSION:
        raise RuntimeError("Schema de snapshot inválido.")
    if payload["decision"] != SNAPSHOT_DECISION or payload["scope"] != SNAPSHOT_SCOPE:
        raise RuntimeError("Decisão ou escopo de snapshot inválido.")
    if any(not isinstance(payload[k], str) or not payload[k].strip() for k in ("release", "approval_basis")):
        raise RuntimeError("Snapshot sem identificação/base de autorização.")
    fronts = set(canonical_slugs)
    collections = [fingerprints, review_statuses, source_fingerprints,
                   payload["fronts"], payload["approved"], payload["quarantined"], payload["provenance"]]
    if any(not isinstance(c, Mapping) or set(c) != fronts for c in collections):
        raise RuntimeError("Snapshot não cobre exatamente as frentes canônicas.")
    total = sum(len(slugs) for slugs in canonical_slugs.values())
    if type(payload["expected_total"]) is not int or payload["expected_total"] != total:
        raise RuntimeError("Snapshot diverge do total canônico.")
    if _digest(payload["inventory_sha256"], "inventory") != corpus_inventory_sha256(fingerprints):
        raise RuntimeError("Snapshot diverge da impressão global do corpus.")
    approved, quarantined, evidence_cache = {}, {}, {}
    for front in sorted(fronts):
        current = dict(fingerprints[front])
        expected = payload["fronts"][front]
        if not isinstance(expected, dict):
            raise RuntimeError("Impressão de frente inválida.")
        _require_exact_fields(expected, _FRONT_FIELDS, front)
        statuses = review_statuses[front]
        sources = source_fingerprints[front]
        slugs = canonical_slugs[front]
        if not isinstance(statuses, Mapping) or not isinstance(sources, Mapping) or set(statuses) != slugs or set(sources) != slugs:
            raise RuntimeError(f"Inventário por item incompleto: {front}.")
        if any(type(expected[k]) is not int for k in ("count", "reviewed_count")):
            raise RuntimeError("Contagem de frente inválida.")
        for field in ("source_sha256", "slug_sha256"):
            _digest(expected[field], f"{front}/{field}")
        if (current != expected or current["count"] != len(slugs)
                or current["reviewed_count"] != sum(v == "revisado" for v in statuses.values())
                or current["slug_sha256"] != slug_inventory_sha256(slugs)):
            raise RuntimeError(f"Snapshot não corresponde à frente canônica {front}.")
        a = _slug_set(payload["approved"][front], f"approved/{front}")
        q = _slug_set(payload["quarantined"][front], f"quarantined/{front}")
        if a & q or a | q != slugs:
            raise RuntimeError(f"Partição aprovado/quarentena não é exata: {front}.")
        provenance = payload["provenance"][front]
        if not isinstance(provenance, dict) or set(provenance) != a:
            raise RuntimeError(f"Proveniência não cobre exatamente os aprovados: {front}.")
        for slug in a:
            if statuses[slug] != "revisado":
                raise RuntimeError(f"Item aprovado não revisado: {front}/{slug}.")
            claim = provenance[slug]
            if not isinstance(claim, dict):
                raise RuntimeError("Proveniência inválida.")
            _require_exact_fields(claim, _PROVENANCE_FIELDS, f"{front}/{slug}")
            if claim["basis"] not in _EVIDENCE_BASES:
                raise RuntimeError("Base de proveniência desconhecida.")
            if _digest(claim["source_sha256"], slug) != _digest(sources[slug], slug):
                raise RuntimeError(f"Fonte aprovada foi alterada: {front}/{slug}.")
            if not isinstance(claim["evidence_path"], str):
                raise RuntimeError("Caminho de evidência inválido.")
            _digest(claim["evidence_sha256"], "evidence")
            key = (claim["evidence_path"], claim["evidence_sha256"])
            if key not in evidence_cache:
                evidence_path = _evidence_file(repository_root, *key)
                try:
                    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
                except ValueError as exc:
                    raise RuntimeError("Índice de evidências inválido.") from exc
                if not isinstance(evidence, dict):
                    raise RuntimeError("Índice de evidências deve ser objeto.")
                _require_exact_fields(evidence, _EVIDENCE_FIELDS, key[0])
                if (type(evidence["schema_version"]) is not int or evidence["schema_version"] != 1
                        or evidence["decision"] != "reconciled_publication_evidence"
                        or not isinstance(evidence["approval_basis"], str) or not evidence["approval_basis"].strip()
                        or not isinstance(evidence["approved_sources"], dict)
                        or not isinstance(evidence["approved_bases"], dict)
                        or not isinstance(evidence["references"], list) or not evidence["references"]):
                    raise RuntimeError("Índice de evidências sem contrato de autorização.")
                bases = set()
                for reference in evidence["references"]:
                    if not isinstance(reference, dict):
                        raise RuntimeError("Referência de evidência inválida.")
                    _require_exact_fields(reference, _EVIDENCE_REFERENCE_FIELDS, key[0])
                    if reference["basis"] not in _EVIDENCE_BASES:
                        raise RuntimeError("Base da referência desconhecida.")
                    _evidence_file(repository_root, reference["path"], reference["sha256"])
                    bases.add(reference["basis"])
                evidence_cache[key] = (evidence, bases)
            evidence, bases = evidence_cache[key]
            evidence_front = evidence["approved_sources"].get(front, {})
            basis_front = evidence["approved_bases"].get(front, {})
            if (claim["basis"] not in bases or not isinstance(evidence_front, dict)
                    or not isinstance(basis_front, dict) or basis_front.get(slug) != claim["basis"]
                    or evidence_front.get(slug) != claim["source_sha256"]):
                raise RuntimeError(f"Evidência não autoriza esta identidade/fonte: {front}/{slug}.")
        approved[front], quarantined[front] = a, q
    return approved, {
        "schema_version": 2, "release": payload["release"], "canonical_total": total,
        "authorized_total": sum(map(len, approved.values())),
        "inventory_sha256": payload["inventory_sha256"],
        "fronts": {front: len(approved[front]) for front in sorted(fronts)},
        "approved": {front: sorted(approved[front]) for front in sorted(fronts)},
        "quarantined": {front: sorted(quarantined[front]) for front in sorted(fronts)},
    }


def validate_snapshot_publication(database: Mapping[str, Any], authorization: Mapping[str, Any]) -> None:
    """Check exact canonical identities, not merely equal row counts.

    Runtime-managed content must be excluded by the caller from published_slugs.
    """
    if authorization.get("schema_version") != 2:
        raise RuntimeError("Autorização final de snapshot inválida.")
    expected = authorization.get("approved")
    quarantine = authorization.get("quarantined")
    actual = database.get("fronts")
    if not isinstance(expected, dict) or not isinstance(quarantine, dict) or not isinstance(actual, dict) or set(actual) != set(expected) or set(quarantine) != set(expected):
        raise RuntimeError("Publicação não cobre exatamente as frentes do snapshot.")
    for front, slugs in expected.items():
        row = actual[front]
        if not isinstance(row, dict):
            raise RuntimeError("Inventário publicado inválido.")
        wanted = _slug_set(slugs, front)
        blocked = _slug_set(quarantine[front], front)
        published = _slug_set(row.get("published_slugs"), front)
        if wanted & blocked or published != wanted or published & blocked:
            raise RuntimeError(f"Publicação diverge das identidades autorizadas: {front}.")
        if type(row.get("published")) is not int or row["published"] != len(wanted):
            raise RuntimeError(f"Contagem publicada diverge: {front}.")
    if type(database.get("published_total")) is not int or database["published_total"] != authorization.get("authorized_total"):
        raise RuntimeError("Total publicado diverge do snapshot autorizado.")
