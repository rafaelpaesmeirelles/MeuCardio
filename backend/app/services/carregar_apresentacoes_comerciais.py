"""Carrega apresentações comerciais (marca, laboratório, dosagem, tamanhos
de caixa) num JSON, aplicando só no campo commercial_presentations — não
mexe em nenhum outro dado do medicamento.

Uso:
    python -m app.services.carregar_apresentacoes_comerciais /caminho/arquivo.json
"""

import json
import sys

from app.core.db import SessionLocal
from app.models.drug import Drug


def carregar(caminho_json: str) -> dict:
    itens = json.load(open(caminho_json, encoding="utf-8"))
    db = SessionLocal()
    atualizados, nao_encontrados = 0, []
    try:
        for item in itens:
            d = db.query(Drug).filter(Drug.slug == item["slug"]).first()
            if not d:
                nao_encontrados.append(item["slug"])
                continue
            d.commercial_presentations = item["commercial_presentations"]
            atualizados += 1
        db.commit()
    finally:
        db.close()
    return {"atualizados": atualizados, "nao_encontrados": nao_encontrados}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        raise SystemExit(1)
    print(json.dumps(carregar(sys.argv[1]), ensure_ascii=False, indent=2))
