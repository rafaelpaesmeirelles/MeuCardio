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

    if payload["schema_version"] != SCHEMA_VERSION:
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
) -> tuple[set[str], set[str]]:
    """Resolve promoção e bloqueio sem permitir alvos não canônicos."""
    if set(publication_intents) != canonical_slugs:
        raise RuntimeError("Intenção de publicação não cobre o corpus canônico.")
    if release_authorized_slugs - canonical_slugs:
        raise RuntimeError("Autorização integral aponta slug não canônico.")

    explicit_true = {
        slug for slug, value in publication_intents.items() if value is True
    }
    explicit_false = {
        slug for slug, value in publication_intents.items() if value is False
    }
    effective_true = explicit_true | release_authorized_slugs
    eligible = effective_true & approved_slugs
    # A autorização integral validada é uma intenção positiva mais nova
    # e ligada ao corpus exato. Fora dela, ``False`` permanece quarentena.
    ineligible = (
        (explicit_false - release_authorized_slugs)
        | (effective_true - approved_slugs)
    )
    return eligible, ineligible


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
