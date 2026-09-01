"""Carrega `material-paciente/metadados.json` para a tabela `patient_materials`.

Segue o padrão das outras frentes, com duas diferenças que são deste conteúdo:

1. **`published` nunca promove pela carga.** `false` é respeitado como
   quarentena; `true` depende da decisão editorial explícita fora do loader.
2. **Recusa material que contenha posologia.** A Tarefa 12 é explícita: o
   material é educativo, não prescritivo. A checagem é mecânica e propositalmente
   grosseira — prefere recusar um texto legítimo a deixar passar uma dose para
   um leigo que não tem como julgar se aquilo se aplica a ele.

Correções editoriais pequenas e auditáveis podem ser versionadas em
`material-paciente/correcoes/*.json`. Elas são aplicadas antes da barreira de
posologia e, portanto, não enfraquecem a proteção: o texto resultante ainda
precisa passar integralmente pelo mesmo detector.
"""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any

from app.core.db import SessionLocal
from app.models.patient_material import PatientMaterial
from app.services.scientific_loader_safety import (
    enforce_safe_publication,
    production_provenance,
    source_references,
    source_review_note,
)

# "500 mg", "12,5mg", "5 mg/kg", "2 comprimidos ao dia", "80 UI"
POSOLOGIA = re.compile(
    r"\b\d+(?:[.,]\d+)?\s*(?:mg|g|mcg|µg|ml|mL|UI|mEq)\b"
    r"|\b\d+\s*(?:comprimido|cápsula|gota|ampola)s?\b"
    r"|\b\d+\s*x\s*/?\s*dia\b",
    re.I,
)


def _texto_do_registro(item: dict) -> str:
    partes = [item.get("titulo", ""), item.get("subtitulo") or "", item.get("resumo") or ""]
    for s in item.get("secoes", []):
        partes.append(s.get("titulo", ""))
        partes.extend(s.get("paragrafos", []))
        partes.extend(s.get("itens", []))
    partes.extend(item.get("sinais_de_alerta", []))
    partes.extend(item.get("perguntas", []))
    return "\n".join(partes)


def _regex_replace_recursive(value: Any, pattern: re.Pattern[str], replacement: str) -> tuple[Any, int]:
    if isinstance(value, str):
        updated, count = pattern.subn(replacement, value)
        return updated, count
    if isinstance(value, list):
        total = 0
        result = []
        for item in value:
            updated, count = _regex_replace_recursive(item, pattern, replacement)
            result.append(updated)
            total += count
        return result, total
    if isinstance(value, dict):
        total = 0
        result: dict[str, Any] = {}
        for key, item in value.items():
            updated, count = _regex_replace_recursive(item, pattern, replacement)
            result[key] = updated
            total += count
        return result, total
    return value, 0


def _aplicar_correcoes(dados: list[dict], caminho: Path) -> list[dict]:
    """Aplica overlays por slug sem alterar o manifesto-fonte.

    Cada `replace_patterns` precisa encontrar ao menos uma ocorrência. Isso
    impede que uma correção envelhecida passe silenciosamente a não fazer nada.
    """
    result = [copy.deepcopy(item) for item in dados]
    by_slug = {str(item.get("slug") or ""): index for index, item in enumerate(result)}
    corrections_dir = caminho.parent / "correcoes"
    if not corrections_dir.exists():
        return result

    for path in sorted(corrections_dir.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            raise ValueError(f"{path}: correções devem ser uma lista")
        for correction in payload:
            if not isinstance(correction, dict):
                raise ValueError(f"{path}: correção deve ser objeto")
            slug = str(correction.get("slug") or "").strip()
            if not slug or slug not in by_slug:
                raise ValueError(f"{path}: slug inexistente: {slug or '?'}")
            index = by_slug[slug]
            record: Any = result[index]
            operations = correction.get("replace_patterns") or []
            if not isinstance(operations, list) or not operations:
                raise ValueError(f"{path}:{slug}: replace_patterns deve ser lista não vazia")
            for operation in operations:
                if not isinstance(operation, dict):
                    raise ValueError(f"{path}:{slug}: operação inválida")
                pattern_text = operation.get("pattern")
                replacement = operation.get("replacement")
                if not isinstance(pattern_text, str) or not pattern_text or not isinstance(replacement, str):
                    raise ValueError(f"{path}:{slug}: pattern/replacement inválidos")
                pattern = re.compile(pattern_text, re.I)
                record, count = _regex_replace_recursive(record, pattern, replacement)
                if count == 0:
                    raise ValueError(f"{path}:{slug}: padrão não encontrado: {pattern_text}")
            result[index] = record
    return result


def carregar(caminho: str = "/material-paciente/metadados.json") -> dict:
    source = Path(caminho)
    dados_raw = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(dados_raw, list):
        raise ValueError(f"{source}: manifesto deve ser uma lista")
    dados = _aplicar_correcoes(dados_raw, source)
    db = SessionLocal()
    novos = atualizados = 0
    recusados: list[dict] = []
    try:
        for item in dados:
            achado = POSOLOGIA.search(_texto_do_registro(item))
            if achado:
                recusados.append({"slug": item.get("slug"),
                                  "motivo": f"contém posologia: {achado.group(0)!r}"})
                continue

            reg = (db.query(PatientMaterial)
                     .filter(PatientMaterial.slug == item["slug"]).first())
            is_new = reg is None
            if is_new:
                reg = PatientMaterial(slug=item["slug"])
                db.add(reg)
                novos += 1
            else:
                atualizados += 1
                reg.version = (reg.version or 1) + 1

            reg.titulo = item["titulo"]
            reg.subtitulo = item.get("subtitulo")
            reg.tema = item.get("tema", "Cardiologia")
            reg.documento_slug = item.get("documento_slug")
            reg.secoes = item.get("secoes", [])
            reg.sinais_de_alerta = item.get("sinais_de_alerta", [])
            reg.perguntas = item.get("perguntas", [])
            references = source_references(item, primary="fontes")
            if references is not None:
                reg.fontes = references
            elif is_new:
                reg.fontes = []
            reg.resumo = item.get("resumo")
            note = source_review_note(item)
            if note is not None:
                reg.review_note = note
            provenance = production_provenance(item)
            if provenance is not None:
                reg.fonte_producao = provenance
            if "review_status" in item:
                reg.review_status = item["review_status"]
            elif is_new:
                reg.review_status = "pendente_revisao"
            enforce_safe_publication(reg, item, is_new=is_new)

        db.commit()
    finally:
        db.close()
    return {"total": len(dados), "novos": novos, "atualizados": atualizados,
            "recusados": recusados}


if __name__ == "__main__":
    print(json.dumps(carregar(), ensure_ascii=False, indent=2))
