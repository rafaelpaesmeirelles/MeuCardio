"""Carrega um JSON com registros de medicamento já processados diretamente
na tabela `drugs`. Complementa `popular_drugs.py`: aquele lê e converte os
arquivos-fonte originais; este só faz o upsert do resultado já pronto,
sem precisar dos arquivos-fonte no servidor.

Uso:
    python -m app.services.carregar_drugs /caminho/drugs_data.json
"""

import json
import sys

from app.core.db import SessionLocal
from app.models.drug import Drug


def carregar(caminho_json: str) -> dict:
    drogas = json.load(open(caminho_json, encoding="utf-8"))
    db = SessionLocal()
    novos = atualizados = 0
    try:
        for d in drogas:
            existente = db.query(Drug).filter(Drug.slug == d["slug"]).first()
            if existente:
                for k, v in d.items():
                    if k not in ("slug", "review_status"):
                        setattr(existente, k, v)
                atualizados += 1
            else:
                db.add(Drug(**d))
                novos += 1
        db.commit()
    finally:
        db.close()
    return {"total": len(drogas), "novos": novos, "atualizados": atualizados}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        raise SystemExit(1)
    print(json.dumps(carregar(sys.argv[1]), ensure_ascii=False, indent=2))
