from __future__ import annotations

import json
import os
import subprocess
from collections import OrderedDict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
BASE_REF = os.environ.get("BASE_REF", "origin/main")
PR_NUMBERS = [
    166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178, 179,
    180, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194,
    195, 196, 197, 199, 200, 201, 202, 203,
]
TARGET_FILES = (
    "checklists/metadados.json",
    "material-paciente/metadados.json",
    "medicamentos/metadados.json",
)
MISSING = object()


def run(*args: str) -> str:
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def load_worktree(path: str) -> list[dict[str, Any]]:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def load_at(ref: str, path: str) -> list[dict[str, Any]]:
    raw = subprocess.check_output(["git", "show", f"{ref}:{path}"], cwd=ROOT, text=True)
    return json.loads(raw)


def by_slug(items: list[dict[str, Any]], path: str) -> OrderedDict[str, dict[str, Any]]:
    out: OrderedDict[str, dict[str, Any]] = OrderedDict()
    for item in items:
        slug = item.get("slug")
        if not isinstance(slug, str) or not slug:
            raise RuntimeError(f"{path}: registro sem slug válido")
        if slug in out:
            raise RuntimeError(f"{path}: slug duplicado {slug}")
        out[slug] = item
    return out


def additive_string_list_merge(base: list[Any], ours: list[Any], theirs: list[Any], ctx: str) -> list[Any]:
    if not all(isinstance(x, str) for x in base + ours + theirs):
        raise RuntimeError(f"Conflito não automaticamente mesclável em {ctx}")
    if any(x not in ours for x in base) or any(x not in theirs for x in base):
        raise RuntimeError(f"Remoção concorrente em lista em {ctx}")
    merged: list[Any] = []
    for x in base + ours + theirs:
        if x not in merged:
            merged.append(x)
    return merged


def merge3(base: Any, ours: Any, theirs: Any, ctx: str) -> Any:
    if ours == theirs:
        return ours
    if ours == base:
        return theirs
    if theirs == base:
        return ours

    if isinstance(base, dict) and isinstance(ours, dict) and isinstance(theirs, dict):
        result: dict[str, Any] = {}
        keys = list(dict.fromkeys([*base.keys(), *ours.keys(), *theirs.keys()]))
        for key in keys:
            b = base.get(key, MISSING)
            o = ours.get(key, MISSING)
            t = theirs.get(key, MISSING)
            if o is MISSING and t is MISSING:
                continue
            if b is MISSING:
                if o is MISSING:
                    result[key] = t
                elif t is MISSING or o == t:
                    result[key] = o
                else:
                    raise RuntimeError(f"Conflito de chave nova em {ctx}.{key}")
                continue
            if o is MISSING:
                if t == b:
                    continue
                raise RuntimeError(f"Remoção concorrente em {ctx}.{key}")
            if t is MISSING:
                if o == b:
                    continue
                raise RuntimeError(f"Remoção concorrente em {ctx}.{key}")
            result[key] = merge3(b, o, t, f"{ctx}.{key}")
        return result

    if isinstance(base, list) and isinstance(ours, list) and isinstance(theirs, list):
        return additive_string_list_merge(base, ours, theirs, ctx)

    raise RuntimeError(
        f"Conflito em {ctx}: base={base!r} ours={ours!r} theirs={theirs!r}"
    )


def apply_delta(
    path: str,
    base_items: list[dict[str, Any]],
    current_items: list[dict[str, Any]],
    pr_items: list[dict[str, Any]],
    pr_number: int,
) -> list[dict[str, Any]]:
    base = by_slug(base_items, path)
    current = by_slug(current_items, path)
    theirs = by_slug(pr_items, path)

    changed = [slug for slug in dict.fromkeys([*base.keys(), *theirs.keys()]) if base.get(slug) != theirs.get(slug)]
    if not changed:
        return current_items

    print(f"PR #{pr_number} -> {path}: {len(changed)} registro(s) alterado(s)")
    for slug in changed:
        b = base.get(slug, MISSING)
        t = theirs.get(slug, MISSING)
        o = current.get(slug, MISSING)

        if b is MISSING:
            if t is MISSING:
                continue
            if o is MISSING:
                current[slug] = t
            elif o != t:
                raise RuntimeError(f"PR #{pr_number}: slug novo divergente já existe: {path}:{slug}")
            continue

        if t is MISSING:
            raise RuntimeError(f"PR #{pr_number}: remoção de registro não autorizada: {path}:{slug}")

        if o is MISSING:
            raise RuntimeError(f"PR #{pr_number}: registro base desapareceu do acumulado: {path}:{slug}")

        current[slug] = merge3(b, o, t, f"PR#{pr_number}:{path}:{slug}")

    return list(current.values())


def changed_files(base: str, pr_ref: str) -> list[str]:
    raw = run("git", "diff", "--name-only", base, pr_ref, "--", *TARGET_FILES)
    return [line for line in raw.splitlines() if line]


def validate(path: str, items: list[dict[str, Any]]) -> None:
    by_slug(items, path)
    if path == "checklists/metadados.json":
        ids: dict[str, str] = {}
        for record in items:
            for entry in record.get("itens", []):
                item_id = entry.get("id")
                if not item_id:
                    continue
                if item_id in ids:
                    raise RuntimeError(f"ID de checklist duplicado: {item_id} ({ids[item_id]} e {record['slug']})")
                ids[item_id] = record["slug"]


def marker_report(base_items: list[dict[str, Any]], final_items: list[dict[str, Any]], path: str) -> list[str]:
    base = by_slug(base_items, path)
    final = by_slug(final_items, path)
    hits: list[str] = []
    for slug, item in final.items():
        if base.get(slug) == item:
            continue
        raw = json.dumps(item, ensure_ascii=False)
        if "VERIFICAÇÃO HUMANA NECESSÁRIA" in raw:
            hits.append(f"{path}:{slug}")
    return hits


def main() -> None:
    base_snapshot = {path: load_at(BASE_REF, path) for path in TARGET_FILES}
    accumulated = {path: load_worktree(path) for path in TARGET_FILES}

    for pr_number in PR_NUMBERS:
        pr_ref = f"refs/remotes/pr/{pr_number}"
        merge_base = run("git", "merge-base", BASE_REF, pr_ref)
        touched = changed_files(merge_base, pr_ref)
        if not touched:
            raise RuntimeError(f"PR #{pr_number}: nenhum dos arquivos-alvo foi alterado")
        unexpected = [p for p in touched if p not in TARGET_FILES]
        if unexpected:
            raise RuntimeError(f"PR #{pr_number}: arquivo inesperado: {unexpected}")
        for path in touched:
            accumulated[path] = apply_delta(
                path,
                load_at(merge_base, path),
                accumulated[path],
                load_at(pr_ref, path),
                pr_number,
            )

    for path, items in accumulated.items():
        validate(path, items)
        (ROOT / path).write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("\n=== RESUMO SEMÂNTICO ===")
    for path in TARGET_FILES:
        before = by_slug(base_snapshot[path], path)
        after = by_slug(accumulated[path], path)
        added = [slug for slug in after if slug not in before]
        modified = [slug for slug in after if slug in before and after[slug] != before[slug]]
        removed = [slug for slug in before if slug not in after]
        print(f"{path}: {len(before)} -> {len(after)} | +{len(added)} novos | {len(modified)} modificados | -{len(removed)}")
        if removed:
            raise RuntimeError(f"{path}: remoções não autorizadas: {removed}")

    hits: list[str] = []
    for path in TARGET_FILES:
        hits.extend(marker_report(base_snapshot[path], accumulated[path], path))
    print(f"Marcadores VERIFICAÇÃO HUMANA NECESSÁRIA em registros tocados: {len(hits)}")
    for hit in hits:
        print(f"  - {hit}")

    print(f"PRs consolidados: {len(PR_NUMBERS)}")


if __name__ == "__main__":
    main()
