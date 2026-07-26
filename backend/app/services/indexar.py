"""Indexa a base científica para a busca semântica.

    docker compose exec backend python -m app.services.indexar          # só o que falta
    docker compose exec backend python -m app.services.indexar --tudo   # reindexa geral
"""

import argparse

from app.core.db import SessionLocal
from app.services import rag


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--tudo", action="store_true", help="reindexa também o que já tem embedding")
    args = p.parse_args()

    db = SessionLocal()
    try:
        r = rag.indexar_tudo(db, apenas_pendentes=not args.tudo)
        print(f"Documentos indexados: {r['documentos']}")
        print(f"Trechos gerados:      {r['trechos']}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
