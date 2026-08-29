"""Indexa a base científica para a busca semântica.

    docker compose exec backend python -m app.services.indexar          # só o que falta
    docker compose exec backend python -m app.services.indexar --tudo   # reindexa geral
"""

import argparse

from openai import RateLimitError

from app.core.db import SessionLocal
from app.services import rag


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--tudo", action="store_true", help="reindexa também o que já tem embedding")
    args = p.parse_args()

    db = SessionLocal()
    try:
        try:
            r = rag.indexar_tudo(db, apenas_pendentes=not args.tudo)
        except RateLimitError as exc:
            # A indexação semântica é derivada e pode ser retomada depois. Falta de
            # crédito no provedor não deve derrubar nem reverter um deploy cujo
            # corpus, banco e aplicação já foram validados com sucesso.
            if getattr(exc, "code", None) == "insufficient_quota" or "insufficient_quota" in str(exc):
                print("AVISO: indexação RAG adiada por falta de créditos no provedor; conteúdo permanece pendente para reindexação posterior.")
                return
            raise
        print(f"Documentos indexados: {r['documentos']}")
        print(f"Trechos gerados:      {r['trechos']}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
