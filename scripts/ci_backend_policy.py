#!/usr/bin/env python3
"""Classifica o risco de uma mudanca e escolhe a menor suite backend segura.

A politica e deliberadamente conservadora:

* mudancas somente de frontend/documentacao nao iniciam a suite backend;
* codigo backend sem superficies de alto risco executa testes relacionados;
* migrations, autenticacao, dados clinicos, dependencias, CI e infraestrutura
  sempre exigem a suite backend completa;
* qualquer caminho desconhecido ou modulo sem teste relacionado cai para a
  suite completa (fail closed).

O script nao consulta a rede. A deduplicacao por SHA e certificado de suite e
feita pelo workflow depois que esta classificacao deterministica e produzida.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath
from typing import Iterable


POLICY_VERSION = "backend-risk-v1"

SAFE_WITHOUT_BACKEND_PREFIXES = (
    "frontend/",
    "docs/",
)
SAFE_WITHOUT_BACKEND_FILES = {
    "README.md",
    "COBERTURA.md",
    "CLAUDE.md",
    "CLAUDE_HISTORICO.md",
    "LICENSE",
}

CLINICAL_CORPUS_PREFIXES = (
    "content/",
    "galeria/",
    "exames/",
    "evidencias/",
    "estudos/",
    "medicamentos/",
    "checklists/",
    "trilhas/",
    "material-paciente/",
    "emergencia/",
    "casos-clinicos/",
    "doencas/",
    "triagem-sintomas/",
    "controlados/",
    "editorial-approvals/",
)

INFRASTRUCTURE_PREFIXES = (
    ".github/",
    "infra/",
    "ops/",
    "scripts/",
    "backend/migrations/",
    "backend/app/models/",
    "backend/alembic/",
)
INFRASTRUCTURE_FILES = {
    "deploy.sh",
    "atualizar.sh",
    "docker-compose.yml",
    "docker-compose.prod.yml",
    "backend/alembic.ini",
    "backend/Dockerfile",
    "backend/Dockerfile.prod",
    "backend/requirements.txt",
    "backend/requirements-dev.txt",
}

# Superficies cuja alteracao pode mudar autenticacao/autorizacao, persistencia
# de dados clinicos identificaveis, assinatura, auditoria ou publicacao do
# corpus. O teste e por componente normalizado, evitando falsos positivos como
# ``author`` conter ``auth``.
HIGH_RISK_BACKEND_COMPONENTS = {
    "auth",
    "authentication",
    "authorization",
    "admin",
    "access",
    "permission",
    "permissions",
    "role",
    "roles",
    "oauth",
    "cookie",
    "cookies",
    "security",
    "session",
    "sessions",
    "token",
    "tokens",
    "password",
    "passwords",
    "user",
    "users",
    "user_access",
    "account_access",
    "kyc",
    "cofre",
    "audit",
    "auditoria",
    "patient",
    "patients",
    "patient_profiles",
    "patient_timeline",
    "paciente",
    "pacientes",
    "prontuario",
    "prescription",
    "prescriptions",
    "prescricao",
    "receituario",
    "clinical_case",
    "clinical_cases",
    "clinical",
    "clinico",
    "clinica",
    "medical",
    "agenda",
    "agenda_integrada",
    "exam",
    "exams",
    "exame",
    "exames",
    "lab_test",
    "lab_tests",
    "drug",
    "drugs",
    "medication",
    "medications",
    "medicamento",
    "medicamentos",
    "evidence",
    "evidencia",
    "study",
    "studies",
    "estudo",
    "emergency",
    "emergencia",
    "disease",
    "diseases",
    "doenca",
    "triage",
    "triagem",
    "guideline",
    "guidelines",
    "specialty",
    "specialty_guides",
    "search",
    "connected_content",
    "heart_team",
    "whatsapp",
    "document",
    "documents",
    "documentos",
    "signature",
    "assinatura",
    "certificado",
    "upload",
    "storage",
    "reconcile_content",
    "publish_preserved_content",
    "importer",
    "disease_manifest",
    "triage_manifest",
    "knowledge_graph",
    "rag",
    "billing",
    "payment",
    "payments",
    "stripe",
}

BACKEND_ENTRYPOINTS = {
    "backend/app/main.py",
    "backend/app/core/config.py",
    "backend/app/core/db.py",
}

SAFE_TEST_PATH = re.compile(r"^tests/test_[A-Za-z0-9_]+\.py$")
TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_]+")


@dataclass(frozen=True)
class PolicyDecision:
    backend_mode: str
    suite_key: str
    focused_tests: tuple[str, ...]
    reasons: tuple[str, ...]
    policy_version: str = POLICY_VERSION

    def github_outputs(self) -> dict[str, str]:
        return {
            "backend_mode": self.backend_mode,
            "suite_key": self.suite_key,
            "focused_tests": " ".join(self.focused_tests),
            "policy_version": self.policy_version,
            "policy_reasons": json.dumps(self.reasons, ensure_ascii=True),
        }


def _normalize_path(raw: str) -> str:
    value = raw.strip().replace("\\", "/")
    while value.startswith("./"):
        value = value[2:]
    if not value or value.startswith("/"):
        raise ValueError(f"caminho invalido: {raw!r}")
    path = PurePosixPath(value)
    if ".." in path.parts:
        raise ValueError(f"caminho fora do repositorio: {raw!r}")
    return path.as_posix()


def _component_tokens(path: str) -> set[str]:
    tokens: set[str] = set()
    for part in PurePosixPath(path).parts:
        stem = part.rsplit(".", 1)[0]
        tokens.update(token.casefold() for token in TOKEN_PATTERN.findall(stem))
        tokens.update(token.casefold() for token in stem.split("_") if token)
        tokens.add(stem.casefold())
    return tokens


def _full_risk_reason(path: str) -> str | None:
    if path in INFRASTRUCTURE_FILES:
        return f"infra:{path}"
    if path in BACKEND_ENTRYPOINTS:
        return f"backend-entrypoint:{path}"
    if path.startswith(CLINICAL_CORPUS_PREFIXES):
        return f"clinical-corpus:{path}"
    if path.startswith(INFRASTRUCTURE_PREFIXES):
        return f"infra:{path}"
    if path.startswith("backend/"):
        name = PurePosixPath(path).name
        if name.startswith("requirements") or name.startswith("Dockerfile"):
            return f"backend-dependency:{path}"
        risky = sorted(_component_tokens(path) & HIGH_RISK_BACKEND_COMPONENTS)
        if risky:
            return f"high-risk-backend:{risky[0]}:{path}"
    return None


def _safe_without_backend(path: str) -> bool:
    if path in SAFE_WITHOUT_BACKEND_FILES:
        return True
    if path.startswith(SAFE_WITHOUT_BACKEND_PREFIXES):
        return True
    # Markdown solto na raiz e apenas documentacao, nao codigo operacional.
    return "/" not in path and path.casefold().endswith(".md")


def _candidate_test_tokens(source_path: str) -> tuple[str, ...]:
    relative = PurePosixPath(source_path).relative_to("backend")
    stem = relative.stem.casefold()
    if stem in {"__init__", "main", "config", "db"}:
        return ()
    dotted = ".".join(relative.with_suffix("").parts).casefold()
    return tuple(dict.fromkeys((dotted, stem)))


def _related_tests(
    backend_paths: Iterable[str],
    *,
    repo_root: Path,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    tests_root = repo_root / "backend" / "tests"
    all_tests = sorted(tests_root.glob("test_*.py"))
    selected: set[str] = set()
    unmapped: list[str] = []

    readiness = tests_root / "test_readiness.py"
    if readiness.is_file():
        selected.add("tests/test_readiness.py")

    test_text: dict[Path, str] = {}
    for test in all_tests:
        if not SAFE_TEST_PATH.fullmatch(f"tests/{test.name}"):
            continue
        try:
            test_text[test] = test.read_text(encoding="utf-8").casefold()
        except UnicodeDecodeError:
            # Um teste Python nao UTF-8 e por si so uma superficie desconhecida.
            test_text[test] = ""

    for path in backend_paths:
        relative = PurePosixPath(path).relative_to("backend").as_posix()
        if relative.startswith("tests/test_") and relative.endswith(".py"):
            if not SAFE_TEST_PATH.fullmatch(relative):
                unmapped.append(path)
                continue
            if not (repo_root / "backend" / relative).is_file():
                # Teste removido/renomeado: a suite completa precisa provar que
                # nenhuma cobertura ou importacao residual foi quebrada.
                unmapped.append(path)
                continue
            selected.add(relative)
            continue

        if not relative.startswith("app/") or not relative.endswith(".py"):
            unmapped.append(path)
            continue

        if not (repo_root / "backend" / relative).is_file():
            # ``git diff --no-renames`` transforma rename em delete+add. Uma
            # origem backend ausente e, portanto, delete/rename e exige full.
            unmapped.append(path)
            continue

        tokens = _candidate_test_tokens(path)
        if not tokens:
            unmapped.append(path)
            continue

        matches: set[str] = set()
        dotted, stem = tokens
        stem_pattern = re.compile(rf"(?<![A-Za-z0-9_]){re.escape(stem)}(?![A-Za-z0-9_])")
        for test, content in test_text.items():
            if dotted in content or stem_pattern.search(content) or stem in test.stem.casefold():
                matches.add(f"tests/{test.name}")
        if not matches:
            unmapped.append(path)
            continue
        selected.update(matches)

    return tuple(sorted(selected)), tuple(sorted(unmapped))


def classify_paths(paths: Iterable[str], *, repo_root: Path) -> PolicyDecision:
    normalized: list[str] = []
    invalid: list[str] = []
    for raw in paths:
        if not raw.strip():
            continue
        try:
            normalized.append(_normalize_path(raw))
        except ValueError:
            invalid.append(raw)

    normalized = sorted(set(normalized))
    if invalid:
        return PolicyDecision(
            backend_mode="full",
            suite_key=f"{POLICY_VERSION}-full",
            focused_tests=(),
            reasons=tuple(f"invalid-path:{item!r}" for item in invalid),
        )
    if not normalized:
        return PolicyDecision(
            backend_mode="full",
            suite_key=f"{POLICY_VERSION}-full",
            focused_tests=(),
            reasons=("empty-change-set:fail-closed",),
        )

    full_reasons = [reason for path in normalized if (reason := _full_risk_reason(path))]
    if full_reasons:
        return PolicyDecision(
            backend_mode="full",
            suite_key=f"{POLICY_VERSION}-full",
            focused_tests=(),
            reasons=tuple(sorted(set(full_reasons))),
        )

    backend_paths = [path for path in normalized if path.startswith("backend/")]
    unknown = [
        path
        for path in normalized
        if not path.startswith("backend/") and not _safe_without_backend(path)
    ]
    if unknown:
        return PolicyDecision(
            backend_mode="full",
            suite_key=f"{POLICY_VERSION}-full",
            focused_tests=(),
            reasons=tuple(f"unknown-path:{path}" for path in unknown),
        )

    if not backend_paths:
        return PolicyDecision(
            backend_mode="skip",
            suite_key=f"{POLICY_VERSION}-skip",
            focused_tests=(),
            reasons=("frontend-or-docs-only",),
        )

    tests, unmapped = _related_tests(backend_paths, repo_root=repo_root)
    if unmapped or not tests:
        reasons = [f"unmapped-backend:{path}" for path in unmapped]
        if not tests:
            reasons.append("no-focused-tests:fail-closed")
        return PolicyDecision(
            backend_mode="full",
            suite_key=f"{POLICY_VERSION}-full",
            focused_tests=(),
            reasons=tuple(sorted(set(reasons))),
        )

    digest = hashlib.sha256(
        (POLICY_VERSION + "\n" + "\n".join(tests)).encode("utf-8")
    ).hexdigest()[:16]
    return PolicyDecision(
        backend_mode="focused",
        suite_key=f"{POLICY_VERSION}-focused-{digest}",
        focused_tests=tests,
        reasons=tuple(f"focused-backend:{path}" for path in backend_paths),
    )


def _write_github_outputs(path: Path, decision: PolicyDecision) -> None:
    with path.open("a", encoding="utf-8") as stream:
        for key, value in decision.github_outputs().items():
            if "\n" in value or "\r" in value:
                raise ValueError(f"output multilinha nao permitido: {key}")
            stream.write(f"{key}={value}\n")


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paths-file", type=Path, required=True)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--github-output", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    paths = args.paths_file.read_text(encoding="utf-8").splitlines()
    decision = classify_paths(paths, repo_root=args.repo_root.resolve())
    if args.github_output is not None:
        _write_github_outputs(args.github_output, decision)
    print(json.dumps(asdict(decision), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
