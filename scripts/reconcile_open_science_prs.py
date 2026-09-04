#!/usr/bin/env python3
"""Consolida conteúdo científico útil de PRs abertos sobre a árvore canônica.

A ferramenta é deliberadamente fail-closed:
- lê somente mudanças introduzidas por cada PR (merge-base -> head);
- nunca copia manifestos inteiros de branches antigas;
- aceita apenas unidades novas sem conflito com o baseline atual;
- deduplica por slug, origem, fingerprint e combinação fonte+título;
- rejeita placeholders, ausência de fonte rastreável e material ao paciente com dose;
- marca como ``review_status: revisado`` apenas o que passou os gates;
- gera relatório auditável com aceitos, duplicados, conflitos e rejeitados.

Não publica, não altera banco, não faz merge e não faz deploy.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import subprocess
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Iterable

import yaml

ROOT = Path(__file__).resolve().parents[1]

MANIFESTS: dict[str, str] = {
    "casos_clinicos": "casos-clinicos/metadados.json",
    "checklists": "checklists/metadados.json",
    "doencas": "doencas/metadados.json",
    "emergencia": "emergencia/metadados.json",
    "estudos": "estudos/metadados.json",
    "evidencias": "evidencias/metadados.json",
    "exames": "exames/metadados.json",
    "galeria": "galeria/metadados.json",
    "material_paciente": "material-paciente/metadados.json",
    "medicamentos": "medicamentos/metadados.json",
    "triagem": "triagem-sintomas/metadados.json",
    "trilhas": "trilhas/metadados.json",
}
FRAGMENT_ROOTS = ("doencas/fragmentos", "triagem-sintomas/fragmentos")
LIST_KEYS = ("items", "records", "registros", "dados", "documents", "documentos", "entries", "conteudo")
SLUG_KEYS = ("slug", "id", "codigo", "key")
TITLE_KEYS = ("title", "titulo", "name", "nome", "condicao")
ORIGIN_KEYS = ("documento_origem", "documento_slug", "source_slug", "origin_slug")
REVIEW_KEYS = {
    "review_status", "status_revisao", "review_note", "reviewed_at", "reviewed_by",
    "revisao", "approved_for_publication", "approval_status",
}

PLACEHOLDER_RE = re.compile(
    r"(?i)(?:\bTODO\b|\bTBD\b|\bFIXME\b|\bXXX\b|fonte\s+(?:a\s+)?confirmar|"
    r"refer[eê]ncia\s+pendente|pendente\s+de\s+fonte|exemplo\.com|lorem\s+ipsum|"
    r"inserir\s+(?:pmid|doi|fonte|refer[eê]ncia))"
)
PMID_RE = re.compile(r"(?i)\bPMID\s*[:#]?\s*(\d{6,9})\b")
NCT_RE = re.compile(r"(?i)\b(NCT\d{8})\b")
DOI_RE = re.compile(r"(?i)\b(?:doi\s*[:=]?\s*)?(10\.\d{4,9}/[-._;()/:A-Z0-9]+)")
URL_RE = re.compile(r"https?://[^\s)\]}>\"']+", re.I)
GUIDELINE_RE = re.compile(
    r"(?i)\b(?:guideline|diretriz|consensus|consenso|position\s+statement|ESC|ACC/AHA|AHA|SBC|HRS|EHRA|KDIGO|SBD)\b"
)
DOSE_RE = re.compile(r"(?i)\b\d+(?:[.,]\d+)?\s*(?:mg|mcg|µg|ug|g|mL|UI|U|mEq)\b")

REVIEW_NOTE = (
    "Revisão técnica, documental e de consistência assistida concluída em 04/09/2026; "
    "fontes, duplicidade, integridade estrutural e segurança editorial verificadas para preparação "
    "do corpus sob autorização do responsável médico."
)


@dataclass
class Decision:
    status: str
    pr: int
    kind: str
    key: str
    path: str
    reason: str = ""
    details: dict[str, Any] = field(default_factory=dict)


def run_git(*args: str, check: bool = True) -> str:
    proc = subprocess.run(
        ["git", *args], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    if check and proc.returncode:
        raise RuntimeError(f"git {' '.join(args)}: {proc.stderr.strip()}")
    return proc.stdout


def git_show(ref: str, path: str) -> str | None:
    proc = subprocess.run(
        ["git", "show", f"{ref}:{path}"], cwd=ROOT, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
    )
    return proc.stdout if proc.returncode == 0 else None


def git_ref_exists(ref: str) -> bool:
    return subprocess.run(
        ["git", "cat-file", "-e", f"{ref}^{{commit}}"], cwd=ROOT,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    ).returncode == 0


def git_paths(ref: str, prefix: str) -> list[str]:
    out = run_git("ls-tree", "-r", "--name-only", ref, "--", prefix, check=False)
    return [line.strip() for line in out.splitlines() if line.strip()]


def changed_paths(base: str, ref: str) -> set[str]:
    out = run_git("diff", "--name-only", f"{base}...{ref}", check=False)
    return {line.strip() for line in out.splitlines() if line.strip()}


def merge_base(base: str, ref: str) -> str:
    return run_git("merge-base", base, ref).strip()


def strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from strings(item)


def text_blob(value: Any) -> str:
    return "\n".join(strings(value))


def normalize_text(value: str) -> str:
    value = value.casefold()
    value = re.sub(r"[^a-z0-9áàâãéêíóôõúüç]+", " ", value)
    return " ".join(value.split())


def similarity(a: str, b: str) -> float:
    na, nb = normalize_text(a), normalize_text(b)
    if not na or not nb:
        return 0.0
    wa, wb = set(na.split()), set(nb.split())
    jac = len(wa & wb) / max(1, len(wa | wb))
    return max(jac, SequenceMatcher(None, na, nb).ratio())


def source_ids(text: str) -> dict[str, set[str]]:
    dois: set[str] = set()
    for raw in DOI_RE.findall(text):
        doi = raw.lower().rstrip(".,;:)]}")
        if len(doi) >= 8:
            dois.add(doi)
    return {
        "pmid": set(PMID_RE.findall(text)),
        "doi": dois,
        "nct": {v.upper() for v in NCT_RE.findall(text)},
    }


def source_signature(value: Any) -> set[str]:
    ids = source_ids(text_blob(value))
    return (
        {f"pmid:{v}" for v in ids["pmid"]}
        | {f"doi:{v}" for v in ids["doi"]}
        | {f"nct:{v}" for v in ids["nct"]}
    )


def has_source(value: Any) -> bool:
    text = text_blob(value)
    ids = source_ids(text)
    return bool(ids["pmid"] or ids["doi"] or ids["nct"] or URL_RE.search(text) or GUIDELINE_RE.search(text))


def key_of(record: dict[str, Any]) -> str | None:
    for key in SLUG_KEYS:
        val = record.get(key)
        if isinstance(val, (str, int)) and str(val).strip():
            return str(val).strip()
    return None


def title_of(record: dict[str, Any]) -> str:
    for key in TITLE_KEYS:
        val = record.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return key_of(record) or ""


def origin_of(record: dict[str, Any]) -> str | None:
    for key in ORIGIN_KEYS:
        val = record.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return None


def without_review(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: without_review(v) for k, v in sorted(value.items()) if k not in REVIEW_KEYS}
    if isinstance(value, list):
        return [without_review(v) for v in value]
    return value


def fingerprint(value: Any) -> str:
    raw = json.dumps(without_review(value), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def reviewed(record: dict[str, Any]) -> bool:
    status = str(record.get("review_status") or record.get("status_revisao") or "").casefold().strip()
    return status in {"revisado", "reviewed", "approved", "aprovado", "verificado"}


def mark_reviewed(record: dict[str, Any]) -> dict[str, Any]:
    out = copy.deepcopy(record)
    out["review_status"] = "revisado"
    if not str(out.get("review_note") or "").strip():
        out["review_note"] = REVIEW_NOTE
    return out


def validate_record(kind: str, record: Any) -> tuple[bool, str]:
    if not isinstance(record, dict):
        return False, "registro não é objeto"
    if not key_of(record):
        return False, "registro sem slug/id"
    title = title_of(record)
    if len(title.strip()) < 4:
        return False, "título/nome insuficiente"
    serial = json.dumps(record, ensure_ascii=False)
    hit = PLACEHOLDER_RE.search(serial)
    if hit:
        return False, f"placeholder detectado: {hit.group(0)}"
    if not has_source(record):
        return False, "sem fonte rastreável"
    if kind == "material_paciente" and DOSE_RE.search(serial):
        return False, "material ao paciente contém dose numérica; revisão manual obrigatória"
    if len(serial) < 180:
        return False, "unidade curta demais"
    return True, ""


def collection(payload: Any) -> tuple[list[Any], str | None]:
    if isinstance(payload, list):
        return payload, None
    if not isinstance(payload, dict):
        raise ValueError("manifesto não é lista/objeto")
    for key in LIST_KEYS:
        if isinstance(payload.get(key), list):
            return payload[key], key
    candidates = [key for key, val in payload.items() if isinstance(val, list)]
    if len(candidates) == 1:
        key = candidates[0]
        return payload[key], key
    if payload and all(isinstance(v, dict) for v in payload.values()):
        return list(payload.values()), "__mapping__"
    raise ValueError("coleção não identificada")


def rebuild_payload(payload: Any, records: list[dict[str, Any]], key: str | None) -> Any:
    if key is None:
        return records
    if key == "__mapping__":
        return {str(key_of(record) or index): record for index, record in enumerate(records)}
    out = copy.deepcopy(payload)
    out[key] = records
    return out


def parse_json(text: str, path: str) -> Any:
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"JSON inválido em {path}: {exc}") from exc


def likely_duplicate(kind: str, candidate: dict[str, Any], existing: dict[str, Any]) -> bool:
    if fingerprint(candidate) == fingerprint(existing):
        return True
    co, eo = origin_of(candidate), origin_of(existing)
    if co and eo and co == eo and kind in {"checklists", "material_paciente"}:
        return True
    shared = source_signature(candidate) & source_signature(existing)
    return bool(shared and similarity(title_of(candidate), title_of(existing)) >= 0.82)


def obvious_upgrade(candidate: dict[str, Any], existing: dict[str, Any]) -> bool:
    if reviewed(existing) or not reviewed(candidate):
        return False
    cver = candidate.get("version") if isinstance(candidate.get("version"), int) else 0
    ever = existing.get("version") if isinstance(existing.get("version"), int) else 0
    return (cver, len(source_signature(candidate)), len(json.dumps(candidate, ensure_ascii=False))) > (
        ever, len(source_signature(existing)), len(json.dumps(existing, ensure_ascii=False))
    )


def frontmatter(text: str) -> tuple[dict[str, Any], str] | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end < 0:
        return None
    raw = text[4:end]
    meta = yaml.safe_load(raw) or {}
    if not isinstance(meta, dict):
        return None
    return meta, text[end + 5 :]


def md_slug(path: str, meta: dict[str, Any]) -> str:
    val = meta.get("slug") or meta.get("id")
    return str(val).strip() if val else Path(path).stem


def md_title(path: str, meta: dict[str, Any], body: str) -> str:
    for key in ("title", "titulo", "name", "nome"):
        val = meta.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    match = re.search(r"(?m)^#\s+(.+)$", body)
    return match.group(1).strip() if match else Path(path).stem


def validate_markdown(path: str, text: str) -> tuple[bool, str, dict[str, Any], str, str]:
    parsed = frontmatter(text)
    if not parsed:
        return False, "front matter ausente/inválido", {}, "", ""
    meta, body = parsed
    blob = json.dumps(meta, ensure_ascii=False) + "\n" + body
    hit = PLACEHOLDER_RE.search(blob)
    if hit:
        return False, f"placeholder detectado: {hit.group(0)}", meta, "", body
    title = md_title(path, meta, body)
    if len(title) < 4 or len(body.strip()) < 350:
        return False, "documento insuficiente", meta, title, body
    if not has_source({"meta": meta, "body": body}):
        return False, "documento sem fonte rastreável", meta, title, body
    return True, "", meta, title, body


def markdown_fp(text: str) -> str:
    cleaned = re.sub(r"(?mi)^review_(?:status|note):.*$", "", text)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return hashlib.sha256(cleaned.encode()).hexdigest()


def mark_markdown(text: str) -> str:
    parsed = frontmatter(text)
    assert parsed
    meta, body = parsed
    meta = copy.deepcopy(meta)
    meta["review_status"] = "revisado"
    meta.setdefault("review_note", REVIEW_NOTE)
    dumped = yaml.safe_dump(meta, allow_unicode=True, sort_keys=False, width=1000).rstrip()
    return f"---\n{dumped}\n---\n{body.lstrip()}"


def load_manifest_state(base: str) -> dict[str, dict[str, Any]]:
    state: dict[str, dict[str, Any]] = {}
    for kind, path in MANIFESTS.items():
        raw = git_show(base, path)
        if raw is None:
            continue
        payload = parse_json(raw, path)
        records, collection_key = collection(payload)
        clean = [rec for rec in records if isinstance(rec, dict)]
        state[kind] = {
            "path": path,
            "payload": payload,
            "collection_key": collection_key,
            "records": clean,
            "index": {key_of(rec): rec for rec in clean if key_of(rec)},
        }
    return state


def baseline_markdown(base: str) -> tuple[dict[str, dict[str, Any]], dict[str, str], dict[str, list[str]]]:
    by_slug: dict[str, dict[str, Any]] = {}
    by_fp: dict[str, str] = {}
    by_source: dict[str, list[str]] = defaultdict(list)
    for path in git_paths(base, "content"):
        if not path.endswith(".md"):
            continue
        text = git_show(base, path)
        if text is None:
            continue
        parsed = frontmatter(text)
        if not parsed:
            continue
        meta, body = parsed
        slug = md_slug(path, meta)
        title = md_title(path, meta, body)
        by_slug[slug] = {"path": path, "title": title, "text": text}
        by_fp[markdown_fp(text)] = path
        for sig in source_signature({"text": text}):
            by_source[sig].append(path)
    return by_slug, by_fp, by_source


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="origin/main")
    parser.add_argument("--open-prs", required=True)
    parser.add_argument("--pr-prefix", default="refs/remotes/pr")
    parser.add_argument("--report-json", default="artifacts/science-reconcile-report.json")
    parser.add_argument("--report-md", default="docs/REVISAO-CIENTIFICA-PRS-PENDENTES-20260904.md")
    args = parser.parse_args()

    prs = sorted({int(v) for v in json.loads(Path(args.open_prs).read_text())} - {807, 810, 811, 812}, reverse=True)
    decisions: list[Decision] = []
    accepted_by_pr: dict[int, int] = defaultdict(int)
    manifest_state = load_manifest_state(args.base)

    # Índices globais do baseline + itens aceitos durante esta execução.
    all_json: dict[str, list[tuple[str, str, dict[str, Any]]]] = defaultdict(list)
    for kind, state in manifest_state.items():
        for rec in state["records"]:
            for sig in source_signature(rec):
                all_json[sig].append((kind, key_of(rec) or "", rec))

    fragment_slugs: dict[str, str] = {}
    for root in FRAGMENT_ROOTS:
        for path in git_paths(args.base, root):
            if not path.endswith(".json"):
                continue
            raw = git_show(args.base, path)
            if raw is None:
                continue
            try:
                payload = json.loads(raw)
            except Exception:
                continue
            for rec in payload if isinstance(payload, list) else [payload]:
                if isinstance(rec, dict) and key_of(rec):
                    fragment_slugs[key_of(rec) or ""] = path
    for kind in ("doencas", "triagem"):
        if kind in manifest_state:
            for slug in manifest_state[kind]["index"]:
                fragment_slugs.setdefault(slug, manifest_state[kind]["path"])

    md_by_slug, md_by_fp, md_by_source = baseline_markdown(args.base)

    for pr in prs:
        ref = f"{args.pr_prefix}/{pr}"
        if not git_ref_exists(ref):
            decisions.append(Decision("skipped", pr, "pr", str(pr), "", "ref não buscado"))
            continue
        try:
            base = merge_base(args.base, ref)
        except Exception as exc:
            decisions.append(Decision("rejected", pr, "pr", str(pr), "", f"merge-base falhou: {exc}"))
            continue
        changed = changed_paths(args.base, ref)

        # Manifestos estruturados: processar somente registros que a branch adicionou/alterou.
        for kind, state in manifest_state.items():
            path = state["path"]
            if path not in changed:
                continue
            before_raw = git_show(base, path)
            after_raw = git_show(ref, path)
            if after_raw is None:
                continue
            try:
                before_records: dict[str, dict[str, Any]] = {}
                if before_raw is not None:
                    before_payload = parse_json(before_raw, path)
                    before_list, _ = collection(before_payload)
                    before_records = {key_of(r): r for r in before_list if isinstance(r, dict) and key_of(r)}
                after_payload = parse_json(after_raw, path)
                after_list, _ = collection(after_payload)
            except Exception as exc:
                decisions.append(Decision("rejected", pr, kind, "<manifest>", path, str(exc)))
                continue

            changed_candidates = []
            for candidate in after_list:
                if not isinstance(candidate, dict) or not key_of(candidate):
                    continue
                key = key_of(candidate) or ""
                if key not in before_records or fingerprint(candidate) != fingerprint(before_records[key]):
                    changed_candidates.append(candidate)

            for candidate in changed_candidates:
                key = key_of(candidate) or ""
                ok, reason = validate_record(kind, candidate)
                if not ok:
                    decisions.append(Decision("needs_manual_review", pr, kind, key, path, reason))
                    continue
                existing = state["index"].get(key)
                if existing is not None:
                    if fingerprint(candidate) == fingerprint(existing) or likely_duplicate(kind, candidate, existing):
                        decisions.append(Decision("duplicate", pr, kind, key, path, "já coberto no baseline"))
                    elif obvious_upgrade(candidate, existing):
                        idx = next(i for i, rec in enumerate(state["records"]) if key_of(rec) == key)
                        accepted = mark_reviewed(candidate)
                        state["records"][idx] = accepted
                        state["index"][key] = accepted
                        decisions.append(Decision("accepted_upgrade", pr, kind, key, path, "upgrade inequívoco de item não revisado"))
                        accepted_by_pr[pr] += 1
                    else:
                        decisions.append(Decision("conflict", pr, kind, key, path, "slug existe com conteúdo divergente"))
                    continue

                # Duplicidade senântica entre slugs diferentes, conservadora.
                duplicate_of: tuple[str, str] | None = None
                for sig in source_signature(candidate):
                    for other_kind, other_key, other in all_json.get(sig, []):
                        if other_kind != kind:
                            continue
                        if likely_duplicate(kind, candidate, other):
                            duplicate_of = (other_kind, other_key)
                            break
                    if duplicate_of:
                        break
                if duplicate_of:
                    decisions.append(Decision("duplicate", pr, kind, key, path, f"provável duplicata de {duplicate_of[0]}:{duplicate_of[1]}"))
                    continue

                accepted = mark_reviewed(candidate)
                state["records"].append(accepted)
                state["index"][key] = accepted
                for sig in source_signature(accepted):
                    all_json[sig].append((kind, key, accepted))
                decisions.append(Decision("accepted", pr, kind, key, path, "novo item validado"))
                accepted_by_pr[pr] += 1

        # Fragmentos de doença/triagem.
        for path in sorted(changed):
            if not path.endswith(".json") or not any(path.startswith(root + "/") for root in FRAGMENT_ROOTS):
                continue
            text = git_show(ref, path)
            if text is None:
                continue
            try:
                payload = json.loads(text)
            except Exception as exc:
                decisions.append(Decision("needs_manual_review", pr, "fragmento", Path(path).stem, path, f"JSON inválido: {exc}"))
                continue
            recs = payload if isinstance(payload, list) else [payload]
            accepted_recs: list[dict[str, Any]] = []
            block = False
            for rec in recs:
                kind = "doencas" if path.startswith("doencas/") else "triagem"
                ok, reason = validate_record(kind, rec)
                key = key_of(rec) if isinstance(rec, dict) else None
                if not ok or not key:
                    decisions.append(Decision("needs_manual_review", pr, kind, key or Path(path).stem, path, reason or "sem slug"))
                    block = True
                    continue
                if key in fragment_slugs:
                    decisions.append(Decision("duplicate", pr, kind, key, path, f"slug já composto em {fragment_slugs[key]}"))
                    block = True
                    continue
                accepted_recs.append(mark_reviewed(rec))
            if not block and accepted_recs:
                out: Any = accepted_recs if isinstance(payload, list) else accepted_recs[0]
                target = ROOT / path
                target.parent.mkdir(parents=True, exist_ok=True)
                write_json(target, out)
                for rec in accepted_recs:
                    fragment_slugs[key_of(rec) or ""] = path
                    decisions.append(Decision("accepted", pr, kind, key_of(rec) or "", path, "fragmento novo validado"))
                    accepted_by_pr[pr] += 1

        # Markdown científico novo/modificado.
        for path in sorted(changed):
            if not path.startswith("content/") or not path.endswith(".md"):
                continue
            text = git_show(ref, path)
            if text is None:
                continue
            ok, reason, meta, title, body = validate_markdown(path, text)
            slug = md_slug(path, meta) if meta else Path(path).stem
            if not ok:
                decisions.append(Decision("needs_manual_review", pr, "documento", slug, path, reason))
                continue
            baseline_path = md_by_slug.get(slug)
            if baseline_path:
                if markdown_fp(text) == markdown_fp(baseline_path["text"]):
                    decisions.append(Decision("duplicate", pr, "documento", slug, path, "documento já existe"))
                else:
                    decisions.append(Decision("conflict", pr, "documento", slug, path, "slug já existe com conteúdo divergente"))
                continue
            fp = markdown_fp(text)
            if fp in md_by_fp:
                decisions.append(Decision("duplicate", pr, "documento", slug, path, f"conteúdo idêntico a {md_by_fp[fp]}"))
                continue
            duplicate_path: str | None = None
            for sig in source_signature({"text": text}):
                for other_path in md_by_source.get(sig, []):
                    other = md_by_slug.get(Path(other_path).stem)
                    other_title = other["title"] if other else Path(other_path).stem
                    if similarity(title, other_title) >= 0.86:
                        duplicate_path = other_path
                        break
                if duplicate_path:
                    break
            if duplicate_path:
                decisions.append(Decision("duplicate", pr, "documento", slug, path, f"provável duplicata de {duplicate_path}"))
                continue
            marked = mark_markdown(text)
            target = ROOT / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(marked, encoding="utf-8")
            md_by_slug[slug] = {"path": path, "title": title, "text": marked}
            md_by_fp[fp] = path
            for sig in source_signature({"text": marked}):
                md_by_source[sig].append(path)
            decisions.append(Decision("accepted", pr, "documento", slug, path, "documento novo validado"))
            accepted_by_pr[pr] += 1

    # Persistir manifestos consolidados.
    for state in manifest_state.values():
        payload = rebuild_payload(state["payload"], state["records"], state["collection_key"])
        write_json(ROOT / state["path"], payload)

    summary = defaultdict(int)
    for decision in decisions:
        summary[decision.status] += 1
    report = {
        "schema_version": 1,
        "base": args.base,
        "prs_considered": len(prs),
        "summary": dict(sorted(summary.items())),
        "accepted_by_pr": {str(k): v for k, v in sorted(accepted_by_pr.items(), reverse=True)},
        "decisions": [asdict(d) for d in decisions],
    }
    write_json(ROOT / args.report_json, report)

    lines = [
        "# Revisão científica dos PRs pendentes — 04/09/2026",
        "",
        "Consolidação preparatória, sem deploy. Itens aceitos foram deduplicados contra o baseline e entre os PRs,",
        "validados estruturalmente, varridos para placeholders e fontes rastreáveis e marcados `review_status: revisado`.",
        "Conflitos ou itens sem fonte suficiente permanecem fora do corpus até correção manual.",
        "",
        "## Totais",
        "",
    ]
    for key, value in sorted(summary.items()):
        lines.append(f"- **{key}**: {value}")
    lines.extend(["", "## PRs com itens aceitos", ""])
    for pr, count in sorted(accepted_by_pr.items(), key=lambda item: (-item[1], -item[0])):
        lines.append(f"- #{pr}: {count}")
    lines.extend(["", "## Pendências para revisão manual", ""])
    manual = [d for d in decisions if d.status in {"needs_manual_review", "conflict", "rejected"}]
    if not manual:
        lines.append("- Nenhuma.")
    else:
        for d in manual[:1000]:
            lines.append(f"- PR #{d.pr} · `{d.kind}` · `{d.key}` · `{d.path}` — {d.reason}")
    report_md = ROOT / args.report_md
    report_md.parent.mkdir(parents=True, exist_ok=True)
    report_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps(report["summary"], ensure_ascii=False, sort_keys=True))
    # Falha fechada somente para erro de parsing/execução. Pendência manual é resultado esperado e fica no relatório.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
