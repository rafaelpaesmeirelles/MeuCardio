"""Carrega `material-paciente/metadados.json` para a tabela `patient_materials`.

Segue o padrão das outras frentes, com duas diferenças que são deste conteúdo:

1. **`published` NUNCA vem do arquivo.** Repetido aqui porque já aconteceu de
   verdade nas frentes de evidências e estudos: o carregador copiava o campo do
   JSON por cima do banco e qualquer recarga despublicava tudo em silêncio.
2. **Recusa material que contenha posologia.** A Tarefa 12 é explícita: o
   material é educativo, não prescritivo. A checagem é mecânica e propositalmente
   grosseira — prefere recusar um texto legítimo a deixar passar uma dose para
   um leigo que não tem como julgar se aquilo se aplica a ele.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from app.core.db import SessionLocal
from app.models.patient_material import PatientMaterial

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


def carregar(caminho: str = "/material-paciente/metadados.json") -> dict:
    dados = json.loads(Path(caminho).read_text(encoding="utf-8"))
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
            if reg is None:
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
            reg.fontes = item.get("fontes", [])
            reg.resumo = item.get("resumo")
            reg.review_status = item.get("review_status", "pendente_revisao")
            # `published` fica de fora de propósito — ver docstring do módulo.

        db.commit()
    finally:
        db.close()
    return {"total": len(dados), "novos": novos, "atualizados": atualizados,
            "recusados": recusados}


if __name__ == "__main__":
    print(json.dumps(carregar(), ensure_ascii=False, indent=2))
