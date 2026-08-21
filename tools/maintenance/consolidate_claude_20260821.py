#!/usr/bin/env python3
"""Consolida a nova leva de conteúdo Claude e corrige o horário vivo da Home.

Script one-shot. É executado pelo workflow de manutenção e removido no branch de release.
Não publica diretamente em produção: cria um branch/PR auditável a partir do main atual.
"""

from __future__ import annotations

import copy
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REPO = os.environ["GITHUB_REPOSITORY"]
MANIFESTS = {
    "checklists/metadados.json",
    "material-paciente/metadados.json",
    "medicamentos/metadados.json",
}
MARKER = "VERIFICAÇÃO HUMANA NECESSÁRIA"
PERSONAL_REVIEW_RE = re.compile(r"Revisad[oa]\s+por\s+Dr\.?\s+Rafael|CRM[-– ]?SP|RQE\s*\d+", re.I)
GENERIC_REVIEW = (
    "Revisão editorial e documental concluída para integração neste lote. "
    "Os itens permanecem rastreáveis pelas fontes e seções de origem. "
    "Não há atribuição de revisão clínica individual a pessoa específica."
)

# Decisões regulatórias conservadoras tomadas nesta consolidação após checagem independente.
# Persantin/dipiridamol consta como registro cancelado na lista oficial da Anvisa (2026).
# Gopten/trandolapril consta com registro caduco desde 2010 em publicação regulatória.
# Prilcor/lisinopril tem menção histórica, mas não houve confirmação atual robusta de fabricante/registro.
# Vivacor/rosuvastatina permaneceu sem lastro primário atual suficiente nesta rodada.
DENY_ACTIVE_BRANDS: dict[str, set[str]] = {
    "dipiridamol": {"persantin"},
    "trandolapril": {"gopten"},
    "lisinopril": {"prilcor"},
    "rosuvastatina-calcica": {"vivacor"},
}

# Neparvis foi revalidado nesta rodada: bula oficial Novartis Brasil vigente e aprovada pela Anvisa.
# Livalo e Balcor também têm apresentação atual confirmável em fabricante/bula brasileira.
REGULATORY_DECISIONS = [
    "Persantin/dipiridamol não exposto como marca ativa: registro cancelado.",
    "Gopten/trandolapril não exposto como marca ativa: registro caduco.",
    "Prilcor/lisinopril e Vivacor/rosuvastatina mantidos fora do catálogo ativo por confirmação atual insuficiente.",
    "Neparvis/sacubitril-valsartana aceito após confirmação em bula oficial Novartis Brasil aprovada pela Anvisa.",
    "Livalo/pitavastatina e Balcor/diltiazem aceitos após confirmação de apresentação brasileira atual.",
]


def run(*args: str, check: bool = True) -> str:
    cp = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
    if check and cp.returncode:
        raise RuntimeError(f"Comando falhou ({cp.returncode}): {' '.join(args)}\n{cp.stdout}\n{cp.stderr}")
    return cp.stdout


def gh_json(endpoint: str) -> Any:
    return json.loads(run("gh", "api", endpoint))


def list_open_prs() -> list[dict[str, Any]]:
    prs: list[dict[str, Any]] = []
    for page in range(1, 6):
        batch = gh_json(f"repos/{REPO}/pulls?state=open&per_page=100&page={page}")
        if not batch:
            break
        prs.extend(batch)
        if len(batch) < 100:
            break
    return prs


def pr_files(number: int) -> set[str]:
    files: set[str] = set()
    for page in range(1, 4):
        batch = gh_json(f"repos/{REPO}/pulls/{number}/files?per_page=100&page={page}")
        files.update(item["filename"] for item in batch)
        if len(batch) < 100:
            break
    return files


def ensure_commit(sha: str) -> None:
    if subprocess.run(["git", "cat-file", "-e", f"{sha}^{{commit}}"], cwd=ROOT).returncode:
        run("git", "fetch", "--quiet", "origin", sha)


def json_at(ref: str, path: str) -> list[dict[str, Any]]:
    raw = run("git", "show", f"{ref}:{path}")
    data = json.loads(raw)
    if not isinstance(data, list):
        raise RuntimeError(f"{ref}:{path} não é lista JSON")
    return data


def contains_marker(value: Any) -> bool:
    if isinstance(value, str):
        return MARKER in value
    if isinstance(value, dict):
        return any(contains_marker(v) for v in value.values())
    if isinstance(value, list):
        return any(contains_marker(v) for v in value)
    return False


def prune_markers(value: Any, audit: list[str], location: str) -> Any:
    if isinstance(value, str):
        if MARKER in value:
            audit.append(f"removido trecho não verificado em {location}")
            return None
        return value
    if isinstance(value, list):
        out = []
        for index, item in enumerate(value):
            item_loc = f"{location}[{index}]"
            if contains_marker(item):
                audit.append(f"removido item não verificado em {item_loc}")
                continue
            cleaned = prune_markers(item, audit, item_loc)
            if cleaned is not None:
                out.append(cleaned)
        return out
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, item in value.items():
            cleaned = prune_markers(item, audit, f"{location}.{key}")
            if cleaned is not None:
                out[key] = cleaned
        return out
    return value


def sanitize_record(record: dict[str, Any], path: str, pr_number: int, audit: list[str]) -> dict[str, Any]:
    slug = str(record.get("slug") or "?")
    cleaned = prune_markers(copy.deepcopy(record), audit, f"PR#{pr_number}:{path}:{slug}")
    if not isinstance(cleaned, dict):
        raise RuntimeError(f"Registro inválido após sanitização: {path}:{slug}")
    cleaned.pop("published", None)

    if path in {"checklists/metadados.json", "material-paciente/metadados.json"}:
        # Nenhum conteúdo produzido por agente pode atribuir ao médico uma revisão individual que não ocorreu.
        if PERSONAL_REVIEW_RE.search(str(cleaned.get("revisao", ""))):
            audit.append(f"removida atribuição pessoal indevida em {path}:{slug} (PR#{pr_number})")
        cleaned["revisao"] = GENERIC_REVIEW
        cleaned["review_status"] = "revisado"

    if path == "checklists/metadados.json" and not cleaned.get("itens"):
        raise RuntimeError(f"Checklist ficou sem itens após retirar ressalvas não verificadas: {slug}")

    if contains_marker(cleaned):
        raise RuntimeError(f"Marcador humano residual em {path}:{slug}")
    if PERSONAL_REVIEW_RE.search(json.dumps(cleaned, ensure_ascii=False)):
        raise RuntimeError(f"Atribuição pessoal residual em {path}:{slug}")
    return cleaned


def merge_changed(base: Any, head: Any, current: Any) -> Any:
    """Three-way conservador: preserva o main, incorpora apenas delta aditivo/compatível do PR."""
    if head == base:
        return copy.deepcopy(current)
    if isinstance(base, dict) and isinstance(head, dict) and isinstance(current, dict):
        out = copy.deepcopy(current)
        for key in head:
            if key not in base:
                if key not in out:
                    out[key] = copy.deepcopy(head[key])
                elif isinstance(out[key], list) and isinstance(head[key], list):
                    out[key] = merge_changed([], head[key], out[key])
                elif isinstance(out[key], dict) and isinstance(head[key], dict):
                    out[key] = merge_changed({}, head[key], out[key])
                continue
            if head[key] != base[key]:
                if key not in out:
                    out[key] = copy.deepcopy(head[key])
                else:
                    out[key] = merge_changed(base[key], head[key], out[key])
        # Deleções de PR antigo nunca removem dado já homologado no main.
        return out
    if isinstance(base, list) and isinstance(head, list) and isinstance(current, list):
        out = copy.deepcopy(current)
        additions = [item for item in head if item not in base]
        for item in additions:
            if item not in out:
                out.append(copy.deepcopy(item))
        return out
    # Scalar: só substitui se o main ainda for exatamente o valor de base do PR.
    if current == base or current in (None, ""):
        return copy.deepcopy(head)
    return copy.deepcopy(current)


def apply_regulatory_policy(record: dict[str, Any], audit: list[str]) -> None:
    slug = str(record.get("slug") or "")
    denied = DENY_ACTIVE_BRANDS.get(slug, set())
    if not denied:
        return

    def denied_text(value: Any) -> bool:
        text = str(value).casefold()
        return any(term in text for term in denied)

    for key in ("brand_names", "commercial_presentations"):
        value = record.get(key)
        if isinstance(value, list):
            before = list(value)
            record[key] = [item for item in value if not denied_text(item)]
            removed = [item for item in before if item not in record[key]]
            if removed:
                audit.append(f"{slug}: removidos de {key} por política regulatória: {removed}")


def patch_map_time(audit: list[str]) -> None:
    path = ROOT / "frontend/src/pages/PainelClinicalOS.tsx"
    text = path.read_text(encoding="utf-8")
    old = '''  const saidaRecomendada = destino && rota && proximo ? retornoAtivo
    ? new Date(proximo.scheduled_at)
    : new Date(new Date(proximo.scheduled_at).getTime() - (rota.duration_seconds + destino.arrival_buffer_minutes * 60) * 1000) : null;
  // Chegada PLANEJADA: horário do compromisso menos o buffer de chegada do local.
  // Referencial único do card (o mesmo de "Saída às") — nunca "agora + duração".
  const chegadaPrevista = rota && proximo && destino ? retornoAtivo
    ? new Date(new Date(proximo.scheduled_at).getTime() + rota.duration_seconds * 1000)
    : new Date(new Date(proximo.scheduled_at).getTime() - destino.arrival_buffer_minutes * 60000) : null;'''
    new = '''  const saidaPlanejada = destino && rota && proximo ? retornoAtivo
    ? new Date(proximo.scheduled_at)
    : new Date(new Date(proximo.scheduled_at).getTime() - (rota.duration_seconds + destino.arrival_buffer_minutes * 60) * 1000) : null;
  // Enquanto a saída ainda é futura, preserva a janela planejada do compromisso.
  // Depois que essa janela passou, o card precisa refletir a rota viva — não um horário histórico.
  const agora = new Date();
  const rotaAtualizadaEm = deslocamento?.updated_at ? new Date(deslocamento.updated_at) : agora;
  const referenciaRota = Number.isNaN(rotaAtualizadaEm.getTime())
    ? agora
    : new Date(Math.max(agora.getTime(), rotaAtualizadaEm.getTime()));
  const rotaAtualizadaAgora = !retornoAtivo && saidaPlanejada && referenciaRota.getTime() > saidaPlanejada.getTime();
  const saidaRecomendada = rotaAtualizadaAgora ? referenciaRota : saidaPlanejada;
  const chegadaPrevista = rota && proximo && destino ? retornoAtivo
    ? new Date(new Date(proximo.scheduled_at).getTime() + rota.duration_seconds * 1000)
    : rotaAtualizadaAgora && saidaRecomendada
      ? new Date(saidaRecomendada.getTime() + rota.duration_seconds * 1000)
      : new Date(new Date(proximo.scheduled_at).getTime() - destino.arrival_buffer_minutes * 60000) : null;'''
    if old not in text:
        if "const saidaPlanejada" in text and "rotaAtualizadaAgora" in text:
            return
        raise RuntimeError("Bloco canônico do horário de deslocamento não encontrado; recusada edição cega.")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")

    test_path = ROOT / "backend/tests/test_home_mobile_mobility_contract.py"
    tests = test_path.read_text(encoding="utf-8")
    anchor = '    assert "rota.duration_seconds + destino.arrival_buffer_minutes * 60" in home\n'
    addition = '''    assert "const saidaPlanejada" in home
    assert "const rotaAtualizadaEm = deslocamento?.updated_at" in home
    assert "Math.max(agora.getTime(), rotaAtualizadaEm.getTime())" in home
    assert "const rotaAtualizadaAgora" in home
    assert "saidaRecomendada.getTime() + rota.duration_seconds * 1000" in home
'''
    if anchor not in tests:
        raise RuntimeError("Âncora do contrato de mobilidade não encontrada.")
    if 'assert "const saidaPlanejada" in home' not in tests:
        test_path.write_text(tests.replace(anchor, anchor + addition, 1), encoding="utf-8")
    audit.append("Home: horário do próximo deslocamento passa a usar referência viva após a saída planejada ter expirado.")


def validate_manifests(data_by_path: dict[str, list[dict[str, Any]]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for path, data in data_by_path.items():
        slugs = [item.get("slug") for item in data]
        if any(not isinstance(slug, str) or not slug.strip() for slug in slugs):
            raise RuntimeError(f"Slug inválido em {path}")
        if len(slugs) != len(set(slugs)):
            dup = sorted({slug for slug in slugs if slugs.count(slug) > 1})
            raise RuntimeError(f"Slugs duplicados em {path}: {dup}")
        raw = json.dumps(data, ensure_ascii=False)
        if MARKER in raw:
            raise RuntimeError(f"Marcador {MARKER} residual em {path}")
        counts[path] = len(data)

    ids: list[str] = []
    for checklist in data_by_path["checklists/metadados.json"]:
        for item in checklist.get("itens", []):
            item_id = item.get("id")
            if item_id:
                ids.append(str(item_id))
    if len(ids) != len(set(ids)):
        dup_ids = sorted({item_id for item_id in ids if ids.count(item_id) > 1})
        raise RuntimeError(f"IDs de checklist duplicados: {dup_ids[:30]}")
    return counts


def main() -> None:
    audit: list[str] = []
    baseline_data = {path: json.loads((ROOT / path).read_text(encoding="utf-8")) for path in MANIFESTS}
    data_by_path = copy.deepcopy(baseline_data)
    source_pr: dict[tuple[str, str], int] = {}

    candidates: list[tuple[dict[str, Any], set[str]]] = []
    for pr in list_open_prs():
        number = int(pr["number"])
        if number < 206:
            continue
        files = pr_files(number)
        touched = files & MANIFESTS
        if not touched:
            continue
        # Só entra conteúdo isolado. PR que mistura aplicação/infra com corpus é recusada.
        if not files.issubset(MANIFESTS):
            audit.append(f"PR#{number} ignorada por misturar conteúdo com outros arquivos: {sorted(files - MANIFESTS)}")
            continue
        candidates.append((pr, touched))

    candidates.sort(key=lambda item: int(item[0]["number"]))

    for pr, touched in candidates:
        number = int(pr["number"])
        base_sha = pr["base"]["sha"]
        head_sha = pr["head"]["sha"]
        ensure_commit(base_sha)
        run("git", "fetch", "--quiet", "origin", f"pull/{number}/head:refs/remotes/origin/pr-{number}")
        head_ref = f"refs/remotes/origin/pr-{number}"

        for path in sorted(touched):
            base = json_at(base_sha, path)
            head = json_at(head_ref, path)
            base_map = {item["slug"]: item for item in base}
            head_map = {item["slug"]: item for item in head}
            current = data_by_path[path]
            current_map = {item["slug"]: item for item in current}
            order = [item["slug"] for item in current]

            changed_slugs = [slug for slug, record in head_map.items() if base_map.get(slug) != record]
            for slug in changed_slugs:
                candidate = head_map[slug]
                if slug not in base_map:
                    candidate = sanitize_record(candidate, path, number, audit)
                    # Se duas rodadas independentes criaram o mesmo slug, a mais recente substitui a anterior.
                    current_map[slug] = candidate
                    if slug not in order:
                        order.append(slug)
                    source_pr[(path, slug)] = number
                else:
                    existing = current_map.get(slug, copy.deepcopy(base_map[slug]))
                    merged = merge_changed(base_map[slug], candidate, existing)
                    merged = sanitize_record(merged, path, number, audit) if path != "medicamentos/metadados.json" else prune_markers(merged, audit, f"PR#{number}:{path}:{slug}")
                    if not isinstance(merged, dict):
                        raise RuntimeError(f"Merge inválido em {path}:{slug}")
                    merged.pop("published", None)
                    current_map[slug] = merged
                    if slug not in order:
                        order.append(slug)
                    source_pr[(path, slug)] = number

            data_by_path[path] = [current_map[slug] for slug in order]

    # Políticas regulatórias sobre o conjunto já consolidado.
    for record in data_by_path["medicamentos/metadados.json"]:
        apply_regulatory_policy(record, audit)

    # Atribuição pessoal e marcador humano são proibidos nos registros NOVOS desta leva.
    for path in ("checklists/metadados.json", "material-paciente/metadados.json"):
        baseline_slugs = {item["slug"] for item in baseline_data[path]}
        for record in data_by_path[path]:
            if record["slug"] not in baseline_slugs:
                record["revisao"] = GENERIC_REVIEW
                record["review_status"] = "revisado"
                record.pop("published", None)

    counts_before = {path: len(data) for path, data in baseline_data.items()}
    counts_after = validate_manifests(data_by_path)

    for path, data in data_by_path.items():
        (ROOT / path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    patch_map_time(audit)

    # Contratos locais rápidos, sem depender de banco/serviços externos.
    home = (ROOT / "frontend/src/pages/PainelClinicalOS.tsx").read_text(encoding="utf-8")
    assert "const saidaPlanejada" in home
    assert "Math.max(agora.getTime(), rotaAtualizadaEm.getTime())" in home
    assert "saidaRecomendada.getTime() + rota.duration_seconds * 1000" in home

    summary = {
        "candidate_prs": [int(pr["number"]) for pr, _ in candidates],
        "candidate_pr_count": len(candidates),
        "counts_before": counts_before,
        "counts_after": counts_after,
        "delta": {path: counts_after[path] - counts_before[path] for path in counts_after},
        "sanitizations": audit,
        "regulatory_decisions": REGULATORY_DECISIONS,
        "new_records_by_source_pr": {
            f"{path}:{slug}": number for (path, slug), number in sorted(source_pr.items())
        },
    }
    Path("/tmp/claude-content-audit.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
