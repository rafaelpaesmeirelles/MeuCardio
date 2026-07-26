"""Carrega meia-vida de vários medicamentos de uma vez, a partir de um JSON
com dado real e fonte citada (bula da FDA, revisão farmacocinética publicada
ou registro de estudo clínico) — não gerado por IA.

Uso:
    python -m app.services.carregar_meia_vida_lote /caminho/meia_vida_lote.json
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
            d.half_life_hours = item["half_life_hours"]
            d.half_life_note = item["half_life_note"]
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
