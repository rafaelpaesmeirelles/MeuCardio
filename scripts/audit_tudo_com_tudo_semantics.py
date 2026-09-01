#!/usr/bin/env python3
"""Auditoria semântica sentinela do mecanismo Tudo com Tudo.

Compara duas decisões determinísticas sobre um conjunto pequeno e forte e
separa os dois caminhos que produziam falsos nexos:

* grafo: expansão em segundo salto de um mesmo tema amplo;
* contexto: aceitação lexical por um único token fora da stoplist antiga.

``Depois`` valida o matcher contextual e a política tipada do grafo reais
quando seus invariantes estão presentes. Referências equivalentes existem
apenas para tornar explícita a comparação com uma base anterior à correção.

O script não acessa banco, rede, embeddings nem dados de paciente. A
canonicalização de temas vem do mecanismo real para impedir que a sentinela
divirja silenciosamente dos aliases usados pela aplicação.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
from types import SimpleNamespace
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIXTURES = ROOT / "scripts/fixtures/tudo_com_tudo_semantic_cases.json"
sys.path.insert(0, str(ROOT / "backend"))

from app.services.topic_relevance import canonical_theme, normalize_text  # noqa: E402


EXPECTED_COHORTS = {
    "correta_obvia": True,
    "correta_dificil": True,
    "semelhante_errada": False,
    "absurda": False,
}
EXPECTED_PATHS = frozenset({"knowledge_graph", "contextual_lexical"})

# A direção é parte da semântica. Um verbo correto no par invertido não
# recebe passe automático. O catálogo é propositalmente menor que o allowlist
# de persistência: aqui constam apenas pares exercitados pelas sentinelas.
ALLOWED_PAIRS: dict[str, frozenset[tuple[str, str]]] = {
    "indicated_for": frozenset({("medicamento", "doenca")}),
    "diagnosed_by": frozenset({("doenca", "exame")}),
    "monitor_with": frozenset({
        ("medicamento", "exame"),
        ("doenca", "exame"),
    }),
    "associated_with": frozenset({
        ("doenca", "calculadora"),
        ("calculadora", "doenca"),
    }),
    "used_in_case": frozenset({
        ("caso_clinico", "documento"),
        ("caso_clinico", "evidencia"),
        ("caso_clinico", "exame"),
    }),
}

MINIMUM_SCORES = {
    "indicated_for": 0.85,
    "diagnosed_by": 0.85,
    "monitor_with": 0.85,
    "associated_with": 0.90,
    "used_in_case": 0.85,
}

REQUIRED_GENERIC_TOKENS = frozenset({
    "agudo", "cronico", "diagnostico", "dor", "frequencia", "imagem",
    "insuficiencia", "pressao", "prevencao", "risco", "tratamento",
})

# Stoplist exatamente anterior à correção. Os seis termos destacados nas
# sentinelas lexicais não estavam nela e, portanto, um único overlap bastava.
LEGACY_CONTEXT_STOPLIST = frozenset({
    "cardiologia", "cardiovascular", "cardiaco", "cardiaca", "doenca", "sindrome",
    "manejo", "tratamento", "terapia", "avaliacao", "diagnostico", "risco", "estudo",
    "evidencia", "diretriz", "clinico", "clinica", "paciente", "adulto", "adultos",
    "crianca", "criancas", "adolescente", "agudo", "aguda", "cronico", "cronica",
    "grave", "arterial", "atrial", "ventricular", "atleta", "esporte", "exercicio",
    "cardiomiopatia", "cardiomiopatias", "para", "pela", "pelo", "pelos", "pelas",
    "com", "sem", "entre", "versus", "apos", "antes", "durante", "como", "quando",
    "qual", "quais", "uma", "umas", "uns", "sobre", "este", "esta", "esse", "essa",
    "dos", "das", "nas", "nos",
})


def _load_fixtures(path: Path) -> tuple[list[dict[str, Any]], str]:
    raw = path.read_bytes()
    payload = json.loads(raw)
    if payload.get("schema_version") != 1 or not isinstance(payload.get("cases"), list):
        raise ValueError("Fixture sem schema_version=1 ou sem lista cases.")
    cases = payload["cases"]
    seen: set[str] = set()
    counts = Counter()
    for index, case in enumerate(cases):
        case_id = case.get("id")
        cohort = case.get("cohort")
        if not isinstance(case_id, str) or not case_id or case_id in seen:
            raise ValueError(f"Caso #{index}: id ausente ou duplicado: {case_id!r}")
        seen.add(case_id)
        if cohort not in EXPECTED_COHORTS:
            raise ValueError(f"{case_id}: coorte inválida: {cohort!r}")
        if case.get("path") not in EXPECTED_PATHS:
            raise ValueError(f"{case_id}: caminho inválido: {case.get('path')!r}")
        if case.get("expected") is not EXPECTED_COHORTS[cohort]:
            raise ValueError(f"{case_id}: expected contradiz a coorte {cohort}.")
        counts[cohort] += 1
        for side in ("source", "target"):
            entity = case.get(side)
            if not isinstance(entity, dict):
                raise ValueError(f"{case_id}: {side} ausente.")
            for field in ("type", "title", "theme"):
                if not isinstance(entity.get(field), str) or not entity[field].strip():
                    raise ValueError(f"{case_id}: {side}.{field} inválido.")
            anchors = entity.get("anchors")
            if not isinstance(anchors, list) or not anchors or not all(
                isinstance(anchor, str) and anchor.strip() for anchor in anchors
            ):
                raise ValueError(f"{case_id}: {side}.anchors inválido.")
        candidate = case.get("candidate")
        required = (
            "relation_type", "provenance_type", "confidence", "review_status",
            "relevance_score", "evidence_source",
        )
        if not isinstance(candidate, dict) or any(field not in candidate for field in required):
            raise ValueError(f"{case_id}: candidate incompleto.")
        score = candidate["relevance_score"]
        if not isinstance(score, (int, float)) or isinstance(score, bool) or not 0 <= score <= 1:
            raise ValueError(f"{case_id}: relevance_score fora de [0, 1].")
    missing = set(EXPECTED_COHORTS) - set(counts)
    if missing:
        raise ValueError(f"Coortes sem casos: {sorted(missing)}")
    return cases, hashlib.sha256(raw).hexdigest()


def _same_canonical_theme(case: dict[str, Any]) -> bool:
    source_theme = canonical_theme(case["source"]["theme"])
    target_theme = canonical_theme(case["target"]["theme"])
    return bool(source_theme and source_theme == target_theme)


def _explicit_reviewed(case: dict[str, Any]) -> bool:
    candidate = case["candidate"]
    return (
        candidate["confidence"] == "explicit"
        and candidate["review_status"] == "revisado"
        and candidate["provenance_type"] in {"editorial", "imported"}
    )


def _legacy_context_tokens(value: object) -> set[str]:
    if isinstance(value, (list, tuple, set, frozenset)):
        text = " ".join(str(item) for item in value if item)
    else:
        text = str(value or "")
    return {
        token for token in normalize_text(text).split()
        if len(token) >= 3 and not token.isdigit() and token not in LEGACY_CONTEXT_STOPLIST
    }


def _reference_relevance_tokens(value: object) -> set[str]:
    if isinstance(value, (list, tuple, set, frozenset)):
        text = " ".join(str(item) for item in value if item)
    else:
        text = str(value or "")
    normalized = re.sub(r"[^a-z0-9]+", " ", normalize_text(text))
    return {
        token for token in normalized.split()
        if len(token) >= 3
        and not token.isdigit()
        and token not in (LEGACY_CONTEXT_STOPLIST | REQUIRED_GENERIC_TOKENS)
    }


def _reference_score_contextual_relevance(
    origin_terms: set[str], *, title_or_slug: object, tags: object = None,
) -> SimpleNamespace:
    title_overlap = origin_terms & _reference_relevance_tokens(title_or_slug)
    tag_overlap = origin_terms & _reference_relevance_tokens(tags)
    score = sum(5 if term in tag_overlap else 3 for term in title_overlap | tag_overlap)
    return SimpleNamespace(score=score, accepted=score >= 3)


def _load_contextual_policy(mechanism_root: Path) -> tuple[object, str]:
    """Carrega o matcher real; usa referência apenas em bases pré-correção."""
    path = mechanism_root / "backend/app/services/topic_relevance.py"
    module_name = f"corvia_semantic_audit_{hashlib.sha256(str(path).encode()).hexdigest()[:12]}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Não foi possível carregar {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    required = (
        "GENERIC_RELATION_TOKENS", "CONTEXT_MIN_RELEVANCE_SCORE",
        "relevance_tokens", "score_contextual_relevance",
    )
    if all(hasattr(module, name) for name in required):
        return module, "implementation"
    fallback = SimpleNamespace(
        GENERIC_RELATION_TOKENS=REQUIRED_GENERIC_TOKENS | LEGACY_CONTEXT_STOPLIST,
        CONTEXT_MIN_RELEVANCE_SCORE=3,
        CONTEXT_TITLE_TOKEN_WEIGHT=3,
        CONTEXT_TAG_TOKEN_WEIGHT=5,
        relevance_tokens=_reference_relevance_tokens,
        score_contextual_relevance=_reference_score_contextual_relevance,
    )
    return fallback, "reference_fallback"


def _load_graph_policy(mechanism_root: Path) -> tuple[object | None, str]:
    """Load the real typed graph policy when auditing a corrected tree."""
    path = mechanism_root / "backend/app/services/knowledge_relation_policy.py"
    if not path.is_file():
        return None, "reference_fallback"
    module_name = f"corvia_graph_policy_{hashlib.sha256(str(path).encode()).hexdigest()[:12]}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Não foi possível carregar {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    required = ("RelacaoClinicaInvalida", "RELATION_TYPE_MATRIX", "validar_relacao_clinica")
    if not all(hasattr(module, name) for name in required):
        return None, "reference_fallback"
    return module, "implementation"


def _legacy_contextual_decision(case: dict[str, Any]) -> bool:
    if not _same_canonical_theme(case):
        return False
    origin_terms = _legacy_context_tokens(case["source"]["title"])
    origin_terms -= _legacy_context_tokens(case["source"]["theme"])
    candidate_terms = _legacy_context_tokens((
        case["target"]["title"], case["target"].get("tags", []),
    ))
    return bool(origin_terms & candidate_terms)


def legacy_decision(case: dict[str, Any]) -> bool:
    """Baseline fiel a cada caminho: tema amplo ou overlap lexical unitário."""
    if case["path"] == "contextual_lexical":
        return _legacy_contextual_decision(case)
    return _explicit_reviewed(case) or _same_canonical_theme(case)


def _guarded_graph_decision(case: dict[str, Any]) -> bool:
    """Política sentinela com tipo, direção, proveniência e âncora clínica."""
    candidate = case["candidate"]
    if candidate["review_status"] == "rejeitado":
        return False
    if candidate["provenance_type"] == "ai_suggested" or candidate["confidence"] == "ai_suggested":
        return False

    relation_type = candidate["relation_type"]
    pair = (case["source"]["type"], case["target"]["type"])
    if pair not in ALLOWED_PAIRS.get(relation_type, frozenset()):
        return False
    if float(candidate["relevance_score"]) < MINIMUM_SCORES[relation_type]:
        return False

    evidence_source = str(candidate.get("evidence_source") or "").strip()
    if not evidence_source:
        return False
    if _explicit_reviewed(case):
        return True

    # Relações derivadas não ganham semântica a partir do tema ou de uma
    # palavra repetida. Exigem a mesma entidade/decisão clínica estruturada.
    source_anchors = set(case["source"]["anchors"])
    target_anchors = set(case["target"]["anchors"])
    return bool(source_anchors & target_anchors) and (
        candidate["provenance_type"] == "structured_metadata"
        and candidate["confidence"] == "derived"
    )


def _corrected_contextual_decision(case: dict[str, Any], policy: object) -> bool:
    if not _same_canonical_theme(case):
        return False
    origin_terms = policy.relevance_tokens(case["source"]["title"])
    origin_terms -= policy.relevance_tokens(case["source"]["theme"])
    match = policy.score_contextual_relevance(
        origin_terms,
        title_or_slug=case["target"]["title"],
        tags=case["target"].get("tags"),
    )
    return bool(match.accepted)


def _corrected_graph_decision_actual(case: dict[str, Any], policy: object | None) -> bool:
    candidate = case["candidate"]
    if candidate["relation_type"] in {"same_theme", "belongs_to_topic"}:
        return False
    if policy is None:
        return _guarded_graph_decision(case)
    try:
        policy.validar_relacao_clinica(
            source_type=case["source"]["type"],
            relation_type=candidate["relation_type"],
            target_type=case["target"]["type"],
            relevance_score=candidate["relevance_score"],
            provenance_type=candidate["provenance_type"],
            confidence=candidate["confidence"],
            review_status=candidate["review_status"],
            evidence_source=candidate["evidence_source"],
            extra=candidate.get("extra"),
        )
    except policy.RelacaoClinicaInvalida:
        return False
    return True


def corrected_decision(
    case: dict[str, Any], contextual_policy: object, graph_policy: object | None,
) -> bool:
    if case["path"] == "contextual_lexical":
        return _corrected_contextual_decision(case, contextual_policy)
    return _corrected_graph_decision_actual(case, graph_policy)


def _metrics(cases: list[dict[str, Any]], decide: Callable[[dict[str, Any]], bool]) -> dict[str, Any]:
    tp = fp = tn = fn = 0
    decisions: dict[str, bool] = {}
    for case in cases:
        predicted = bool(decide(case))
        expected = bool(case["expected"])
        decisions[case["id"]] = predicted
        if predicted and expected:
            tp += 1
        elif predicted and not expected:
            fp += 1
        elif not predicted and not expected:
            tn += 1
        else:
            fn += 1

    def ratio(numerator: int, denominator: int) -> float:
        return round(numerator / denominator, 4) if denominator else 0.0

    precision = ratio(tp, tp + fp)
    recall = ratio(tp, tp + fn)
    return {
        "true_positive": tp,
        "false_positive": fp,
        "true_negative": tn,
        "false_negative": fn,
        "accuracy": ratio(tp + tn, len(cases)),
        "precision": precision,
        "recall": recall,
        "f1": ratio(2 * precision * recall, precision + recall),
        "decisions": decisions,
    }


def _shared_generic_tokens(case: dict[str, Any]) -> list[str]:
    source = set(normalize_text(case["source"]["title"]).split())
    target = set(normalize_text(case["target"]["title"]).split())
    return sorted(source & target & REQUIRED_GENERIC_TOKENS)


def _mechanism_facts(
    mechanism_root: Path,
    contextual_policy: object,
    contextual_policy_source: str,
    graph_policy_source: str,
) -> dict[str, Any]:
    graph = (
        mechanism_root / "backend/app/services/knowledge_graph.py"
    ).read_text(encoding="utf-8")
    graph_api = (
        mechanism_root / "backend/app/api/knowledge_graph.py"
    ).read_text(encoding="utf-8")
    relation_policy = (
        mechanism_root / "backend/app/services/knowledge_relation_policy.py"
    )
    relation_policy_text = (
        relation_policy.read_text(encoding="utf-8") if relation_policy.is_file() else ""
    )
    connected_after = (
        mechanism_root / "backend/app/services/connected_content.py"
    ).read_text(encoding="utf-8")
    search_api = (mechanism_root / "backend/app/api/search.py").read_text(encoding="utf-8")
    rag = (mechanism_root / "backend/app/services/rag.py").read_text(encoding="utf-8")
    generic_tokens = set(contextual_policy.GENERIC_RELATION_TOKENS)
    generic_rejections = {
        token: not bool(contextual_policy.relevance_tokens(token))
        for token in sorted(REQUIRED_GENERIC_TOKENS)
    }
    discriminative_terms = contextual_policy.relevance_tokens("brugada")
    discriminative_match = contextual_policy.score_contextual_relevance(
        discriminative_terms, title_or_slug="protocolo de brugada",
    )
    return {
        "knowledge_graph_before": {
            "baseline_commit": "e16c73c0",
            "two_hop_topic_expansion_was_public": True,
            "same_theme_was_treated_as_direct_relation": True,
            "taxonomic_score_was_treated_as_clinical_relevance": 0.35,
        },
        "knowledge_graph_after": {
            "policy_source": graph_policy_source,
            "typed_policy_enforced": (
                "validar_relacao_clinica(" in graph
                and "RELATION_TYPE_MATRIX" in relation_policy_text
                and "def validar_relacao_clinica(" in relation_policy_text
            ),
            "default_theme_expansion_disabled": bool(re.search(
                r"def relacionados_de\([^)]*incluir_contexto_tematico:\s*bool\s*=\s*False",
                graph,
                re.DOTALL,
            )),
            "same_theme_filtered_from_direct_results": bool(re.search(
                r"if\s+relacao\.relation_type\s*==\s*[\"']same_theme[\"']:\s*continue",
                graph,
            )),
            "public_api_blocks_theme_expansion": (
                "if incluir_contexto_tematico:" in graph_api
                and "incluir_contexto_tematico=False" in graph_api
            ),
            "theme_navigation_remains_internal_opt_in": (
                "vizinhos_de_tema" in graph
                and "if topicos and incluir_contexto_tematico:" in graph
            ),
        },
        "contextual_lexical_before": {
            "baseline_commit": "e16c73c0",
            "one_token_overlap_was_sufficient": True,
            "missing_required_stoplist_tokens": sorted(
                REQUIRED_GENERIC_TOKENS - LEGACY_CONTEXT_STOPLIST
            ),
        },
        "contextual_lexical_after": {
            "policy_source": contextual_policy_source,
            "threshold": contextual_policy.CONTEXT_MIN_RELEVANCE_SCORE,
            "title_token_weight": getattr(
                contextual_policy, "CONTEXT_TITLE_TOKEN_WEIGHT", None,
            ),
            "tag_token_weight": getattr(
                contextual_policy, "CONTEXT_TAG_TOKEN_WEIGHT", None,
            ),
            "missing_required_stoplist_tokens": sorted(
                REQUIRED_GENERIC_TOKENS - generic_tokens
            ),
            "generic_single_token_rejections": generic_rejections,
            "one_discriminative_title_token_is_explainably_accepted": bool(
                discriminative_match.accepted
                and discriminative_match.score
                >= contextual_policy.CONTEXT_MIN_RELEVANCE_SCORE
            ),
            "connected_content_uses_real_scorer": (
                "score_contextual_relevance" in connected_after
                and "CONTEXT_MIN_RELEVANCE_SCORE" in connected_after
            ),
        },
        "retrieval_not_relations": {
            "api_search_uses_full_text": bool(re.search(
                r"plainto_tsquery|tsvector|tsquery", search_api, re.IGNORECASE,
            )),
            "relation_modules_use_full_text": bool(re.search(
                r"plainto_tsquery|tsvector|tsquery", graph + connected_after, re.IGNORECASE,
            )),
            "rag_uses_embeddings_for_retrieval": (
                "cosine_distance" in rag and "obter_provedor_embeddings" in rag
            ),
            "relation_modules_use_embedding_distance": bool(re.search(
                r"cosine_distance|vector_distance|DocumentChunk", graph + connected_after,
            )),
        },
    }


def audit(
    fixtures: Path = DEFAULT_FIXTURES,
    mechanism_root: Path = ROOT,
) -> dict[str, Any]:
    cases, fixture_sha256 = _load_fixtures(fixtures)
    contextual_policy, contextual_policy_source = _load_contextual_policy(mechanism_root)
    graph_policy, graph_policy_source = _load_graph_policy(mechanism_root)
    before = _metrics(cases, legacy_decision)
    after_decide = lambda case: corrected_decision(
        case, contextual_policy, graph_policy,
    )
    after = _metrics(cases, after_decide)
    path_metrics = {
        path: {
            "cases": len(path_cases),
            "before": _metrics(path_cases, legacy_decision),
            "after": _metrics(path_cases, after_decide),
        }
        for path in sorted(EXPECTED_PATHS)
        if (path_cases := [case for case in cases if case["path"] == path])
    }
    preserved = sorted(
        case["id"] for case in cases
        if before["decisions"][case["id"]] and after["decisions"][case["id"]]
    )
    eliminated = sorted(
        case["id"] for case in cases
        if before["decisions"][case["id"]] and not after["decisions"][case["id"]]
    )
    added = sorted(
        case["id"] for case in cases
        if not before["decisions"][case["id"]] and after["decisions"][case["id"]]
    )
    residual_errors = sorted(
        case["id"] for case in cases
        if after["decisions"][case["id"]] != case["expected"]
    )
    generic_false_positives = {
        case["id"]: _shared_generic_tokens(case)
        for case in cases
        if not case["expected"]
        and case["path"] == "contextual_lexical"
        and before["decisions"][case["id"]]
        and _shared_generic_tokens(case)
    }
    same_theme_false_positives = sorted(
        case["id"] for case in cases
        if not case["expected"]
        and case["path"] == "knowledge_graph"
        and before["decisions"][case["id"]]
        and _same_canonical_theme(case)
    )
    facts = _mechanism_facts(
        mechanism_root,
        contextual_policy,
        contextual_policy_source,
        graph_policy_source,
    )
    matcher_after = facts["contextual_lexical_after"]
    graph_after = facts["knowledge_graph_after"]
    invariant_errors = []
    if matcher_after["missing_required_stoplist_tokens"]:
        invariant_errors.append("matcher_stoplist_incompleta")
    if not all(matcher_after["generic_single_token_rejections"].values()):
        invariant_errors.append("token_generico_ainda_pontua")
    if matcher_after["threshold"] < matcher_after["title_token_weight"]:
        invariant_errors.append("threshold_abaixo_de_um_token_de_titulo")
    if (
        contextual_policy_source == "implementation"
        and not matcher_after["connected_content_uses_real_scorer"]
    ):
        invariant_errors.append("connected_content_nao_usa_scorer_real")
    if graph_policy_source != "implementation":
        invariant_errors.append("politica_tipificada_do_grafo_ausente")
    for invariant in (
        "typed_policy_enforced",
        "default_theme_expansion_disabled",
        "same_theme_filtered_from_direct_results",
        "public_api_blocks_theme_expansion",
    ):
        if not graph_after[invariant]:
            invariant_errors.append(f"grafo_{invariant}")
    counts = Counter(case["cohort"] for case in cases)
    try:
        fixture_label = str(fixtures.relative_to(ROOT))
    except ValueError:
        fixture_label = fixtures.name
    return {
        "audit_version": 3,
        "fixture": fixture_label,
        "fixture_sha256": fixture_sha256,
        "cases": len(cases),
        "cohorts": dict(sorted(counts.items())),
        "paths": {path: data["cases"] for path, data in path_metrics.items()},
        "before": before,
        "after": after,
        "path_metrics": path_metrics,
        "preserved": preserved,
        "eliminated": eliminated,
        "added": added,
        "residual_errors": residual_errors,
        "invariant_errors": invariant_errors,
        "diagnostics": {
            "theme_expansion_false_positives": same_theme_false_positives,
            "one_token_lexical_false_positives": generic_false_positives,
            "mechanism_facts": facts,
        },
        "root_cause": (
            "Duas causas independentes: (1) tema canônico amplo expandido em "
            "segundo salto como se fosse nexo clínico; (2) matcher contextual "
            "aceitava um único token não bloqueado, enquanto pressão, frequência, "
            "insuficiência, prevenção, dor e imagem faltavam na stoplist."
        ),
        "corrected_rule": (
            "Grafo preserva curadoria e exige relação tipada/âncora estruturada; "
            "matcher contextual remove termos genéricos e aplica o scorer/threshold "
            "auditável real. Full text de /api/search e embeddings do RAG são "
            "recuperação de informação e não criam arestas."
        ),
    }


def _print_summary(result: dict[str, Any]) -> None:
    before = result["before"]
    after = result["after"]
    print(f"Sentinelas: {result['cases']} | coortes: {result['cohorts']}")
    print(
        "Antes: "
        f"precisão={before['precision']:.2%}, recall={before['recall']:.2%}, "
        f"acurácia={before['accuracy']:.2%}, FP={before['false_positive']}, FN={before['false_negative']}"
    )
    print(
        "Depois: "
        f"precisão={after['precision']:.2%}, recall={after['recall']:.2%}, "
        f"acurácia={after['accuracy']:.2%}, FP={after['false_positive']}, FN={after['false_negative']}"
    )
    print(
        f"Preservadas={len(result['preserved'])} | eliminadas={len(result['eliminated'])} | "
        f"adicionadas={len(result['added'])} | erros residuais={len(result['residual_errors'])}"
    )
    matcher = result["diagnostics"]["mechanism_facts"]["contextual_lexical_after"]
    graph = result["diagnostics"]["mechanism_facts"]["knowledge_graph_after"]
    print(
        f"Matcher={matcher['policy_source']} | threshold={matcher['threshold']} | "
        f"grafo={graph['policy_source']} | erros de invariante={len(result['invariant_errors'])}"
    )
    print(f"Causa-raiz: {result['root_cause']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixtures", type=Path, default=DEFAULT_FIXTURES)
    parser.add_argument(
        "--mechanism-root", type=Path, default=ROOT,
        help="Raiz que contém o matcher corrigido a validar.",
    )
    parser.add_argument(
        "--require-actual-matcher", action="store_true",
        help="Falha se a raiz ainda não contiver o scorer/stoplist corrigidos.",
    )
    parser.add_argument(
        "--require-actual-mechanisms", action="store_true",
        help="Falha se o matcher ou a política tipada do grafo não forem reais.",
    )
    parser.add_argument("--json", action="store_true", help="Emite o relatório completo em JSON.")
    args = parser.parse_args()
    fixtures = args.fixtures.resolve()
    result = audit(fixtures, args.mechanism_root.resolve())
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        _print_summary(result)
    matcher_source = result["diagnostics"]["mechanism_facts"][
        "contextual_lexical_after"
    ]["policy_source"]
    graph_source = result["diagnostics"]["mechanism_facts"][
        "knowledge_graph_after"
    ]["policy_source"]
    if args.require_actual_matcher and matcher_source != "implementation":
        return 2
    if args.require_actual_mechanisms and (
        matcher_source != "implementation" or graph_source != "implementation"
    ):
        return 2
    return 1 if result["residual_errors"] or result["invariant_errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
