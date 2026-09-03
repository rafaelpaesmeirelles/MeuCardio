"""Carga/sincronização da base oficial de médicos do CFM.

Exemplos:
    python -m app.commands.sync_cfm_registry --download
    python -m app.commands.sync_cfm_registry --zip /tmp/TOTAL.zip
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import os
import sys

from app.core.config import settings
from app.core.db import SessionLocal
from app.services.cfm_registry import (
    CfmRegistryError,
    baixar_totalzip,
    importar_totalzip,
    importar_totalzip_path,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sincroniza a base oficial de médicos do CFM.")
    origem = parser.add_mutually_exclusive_group(required=True)
    origem.add_argument(
        "--download",
        action="store_true",
        help="Baixa o TOTAL.ZIP oficial usando a chave configurada no backend e aplica o snapshot.",
    )
    origem.add_argument(
        "--zip",
        dest="zip_path",
        help="Aplica um TOTAL.ZIP local já obtido oficialmente do CFM.",
    )
    parser.add_argument(
        "--sha256",
        dest="expected_sha256",
        default=None,
        help="SHA-256 esperado do arquivo local/baixado; a carga aborta em divergência.",
    )
    return parser


def _chave_download() -> str:
    # Alguns convênios recebem uma credencial própria para o arquivo completo.
    # Se ela não existir, mantém compatibilidade com a chave única já prevista
    # no CorVIA. Nenhuma das duas é registrada em log.
    return (
        os.getenv("CFM_TOTALZIP_CHAVE", "").strip()
        or settings.cfm_webservice_chave.strip()
    )


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    db = SessionLocal()
    try:
        if args.download:
            chave = _chave_download()
            if not chave:
                raise CfmRegistryError(
                    "Credencial de download do CFM não está configurada no ambiente de produção."
                )
            payload = baixar_totalzip(chave)
            digest = sha256(payload).hexdigest()
            run = importar_totalzip(
                db,
                payload,
                expected_sha256=args.expected_sha256,
            )
        else:
            run = importar_totalzip_path(
                db,
                args.zip_path,
                expected_sha256=args.expected_sha256,
            )
            digest = run.dataset_sha256 or ""
        print(
            "CFM_SYNC_OK "
            f"run_id={run.id} sha256={digest} records={run.record_count} "
            f"invalid_identifiers={run.invalid_identifier_count} "
            f"deactivated={run.deactivated_count}"
        )
        return 0
    except CfmRegistryError as exc:
        # A mensagem nunca inclui a chave; o serviço também não registra corpo
        # de resposta de autenticação nem parâmetros secretos.
        print(f"CFM_SYNC_ERROR {exc}", file=sys.stderr)
        return 2
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
