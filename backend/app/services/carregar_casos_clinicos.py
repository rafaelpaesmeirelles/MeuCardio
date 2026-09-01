"""Carrega os casos clínicos interativos a partir do JSON de metadados.

Uso:
    python -m app.services.carregar_casos_clinicos /casos-clinicos/metadados.json
"""

import json
import sys

from app.core.db import SessionLocal
from app.models.clinical_case import ClinicalCase
from app.services.scientific_loader_safety import combined_review_note, enforce_safe_publication

# `published` só é consumido como quarentena; nunca promove pela carga.
CAMPOS = {"slug", "titulo", "tema", "nivel", "enunciado", "pergunta", "opcoes",
          "resposta_correta", "explicacao", "source_refs", "review_status", "revisao"}


def carregar(caminho_json: str) -> dict:
    itens = json.load(open(caminho_json, encoding="utf-8"))
    db = SessionLocal()
    novos = atualizados = 0
    avisos: list[str] = []
    try:
        for bruto in itens:
            item = {k: v for k, v in bruto.items() if k in CAMPOS}

            opcoes = item.get("opcoes") or []
            if len(opcoes) < 2:
                avisos.append(f"{item.get('slug','?')}: menos de 2 opções, não carregado")
                continue
            indice = item.get("resposta_correta")
            if not isinstance(indice, int) or not (0 <= indice < len(opcoes)):
                avisos.append(f"{item.get('slug','?')}: resposta_correta fora do intervalo de opções, não carregado")
                continue
            if not item.get("source_refs"):
                # Não bloqueia — mas conduta correta sem fonte citada é exatamente
                # o que este produto proíbe em qualquer outra frente de conteúdo.
                avisos.append(f"{item.get('slug','?')}: sem source_refs")

            existente = db.query(ClinicalCase).filter(
                ClinicalCase.slug == item["slug"]
            ).first()
            note = combined_review_note(
                bruto,
                existing=getattr(existente, "revisao", None),
            )
            if note is not None:
                item["revisao"] = note
            if existente:
                for campo, valor in item.items():
                    setattr(existente, campo, valor)
                enforce_safe_publication(existente, bruto, is_new=False)
                atualizados += 1
            else:
                registro = ClinicalCase(**item)
                enforce_safe_publication(registro, bruto, is_new=True)
                db.add(registro)
                novos += 1
        db.commit()
    finally:
        db.close()
    resultado = {"novos": novos, "atualizados": atualizados}
    if avisos:
        resultado["avisos"] = avisos
    return resultado


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        raise SystemExit(1)
    print(json.dumps(carregar(sys.argv[1]), ensure_ascii=False, indent=2))
