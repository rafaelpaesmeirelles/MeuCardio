"""Carrega redução de PAS/PAD por medicamento a partir de um JSON com dado
real e fonte citada (não gerado por IA, extraído de revisão sistemática de
acesso aberto). Complementa carregar_drugs.py com os dois campos novos.

Uso:
    python -m app.services.carregar_eficacia_pa /caminho/eficacia_pa.json
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
            d.sbp_reduction_mmhg = item["sbp_reduction_mmhg"]
            d.dbp_reduction_mmhg = item["dbp_reduction_mmhg"]
            d.bp_evidence_source = item["bp_evidence_source"]
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
