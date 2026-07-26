"""Carrega estudos científicos a partir de um JSON de metadados.

Uso:
    python -m app.services.carregar_estudos /caminho/estudos.json
"""

import json
import sys

from app.core.db import SessionLocal
from app.models.study import ScientificStudy


def carregar(caminho_json: str) -> dict:
    itens = json.load(open(caminho_json, encoding="utf-8"))
    db = SessionLocal()
    novos, atualizados = 0, 0
    try:
        for item in itens:
            existente = db.query(ScientificStudy).filter(ScientificStudy.slug == item["slug"]).first()
            if existente:
                for campo, valor in item.items():
                    setattr(existente, campo, valor)
                atualizados += 1
            else:
                db.add(ScientificStudy(**item))
                novos += 1
        db.commit()
    finally:
        db.close()
    return {"novos": novos, "atualizados": atualizados}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        raise SystemExit(1)
    print(json.dumps(carregar(sys.argv[1]), ensure_ascii=False, indent=2))
