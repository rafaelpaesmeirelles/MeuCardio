"""CLI de `cmed_precos.atualizar()` — mesmo caminho de código chamado pela
rota `POST /api/admin/cmed/atualizar` e pelo cron diário
(`infra/cmed_cron.sh`). Uso: `python -m app.services.cmed_precos_cli`."""
import logging
import sys

from app.core.db import SessionLocal
from app.services import cmed_precos

logging.basicConfig(level=logging.INFO)


def main() -> int:
    forcar = "--forcar" in sys.argv
    db = SessionLocal()
    try:
        resultado = cmed_precos.atualizar(db, forcar=forcar)
        print(resultado)
        return 0
    except Exception as e:  # noqa: BLE001 — cron precisa do código de saída != 0
        print(f"ERRO: {e}", file=sys.stderr)
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
