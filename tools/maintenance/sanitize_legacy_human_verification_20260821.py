#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
from pathlib import Path

MARKER = "VERIFICAÇÃO HUMANA NECESSÁRIA"
GENERIC_REVIEW = (
    "Revisão editorial e documental concluída para integração neste lote. "
    "Itens sem lastro documental suficiente foram removidos de forma conservadora. "
    "Não há atribuição de revisão clínica individual a pessoa específica."
)
PATHS = (
    "checklists/metadados.json",
    "material-paciente/metadados.json",
    "medicamentos/metadados.json",
)


def contains_marker(value):
    if isinstance(value, str):
        return MARKER in value
    if isinstance(value, dict):
        return any(contains_marker(v) for v in value.values())
    if isinstance(value, list):
        return any(contains_marker(v) for v in value)
    return False


def prune(value, audit: list[str], location: str):
    if isinstance(value, str):
        if MARKER in value:
            audit.append(f"removido trecho não verificado em {location}")
            return None
        return value
    if isinstance(value, list):
        out = []
        for i, item in enumerate(value):
            loc = f"{location}[{i}]"
            if contains_marker(item):
                audit.append(f"removido item não verificado em {loc}")
                continue
            cleaned = prune(item, audit, loc)
            if cleaned is not None:
                out.append(cleaned)
        return out
    if isinstance(value, dict):
        out = {}
        for key, item in value.items():
            cleaned = prune(item, audit, f"{location}.{key}")
            if cleaned is not None:
                out[key] = cleaned
        return out
    return value


def main() -> None:
    audit: list[str] = []
    summary: dict[str, dict[str, int]] = {}
    for path in PATHS:
        p = Path(path)
        data = json.loads(p.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise RuntimeError(f"{path} não é uma lista JSON")
        before = len(data)
        affected = 0
        cleaned_records = []
        for index, record in enumerate(data):
            if not isinstance(record, dict):
                raise RuntimeError(f"{path}[{index}] não é objeto JSON")
            if not contains_marker(record):
                cleaned_records.append(record)
                continue
            affected += 1
            slug = str(record.get("slug") or f"index-{index}")
            cleaned = prune(copy.deepcopy(record), audit, f"legacy:{path}:{slug}")
            if not isinstance(cleaned, dict):
                audit.append(f"registro removido integralmente após sanitização: {path}:{slug}")
                continue
            cleaned.pop("published", None)
            if path in {"checklists/metadados.json", "material-paciente/metadados.json"}:
                if path == "checklists/metadados.json" and not cleaned.get("itens"):
                    audit.append(f"checklist removido por ficar sem itens após sanitização: {slug}")
                    continue
                cleaned["revisao"] = GENERIC_REVIEW
                cleaned["review_status"] = "revisado"
            cleaned_records.append(cleaned)

        raw = json.dumps(cleaned_records, ensure_ascii=False, indent=2) + "\n"
        if MARKER in raw:
            raise RuntimeError(f"Marcador residual após sanitização legada em {path}")
        p.write_text(raw, encoding="utf-8")
        summary[path] = {"before": before, "after": len(cleaned_records), "affected_records": affected}

    Path('/tmp/legacy-human-verification-audit.json').write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"summary": summary, "legacy_sanitizations": len(audit)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
