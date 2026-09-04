"""DEPRECADO desde a correção coordenada de 03/09/2026 — mantido só como
atalho de compatibilidade para quem ainda chame `python -m
app.services.indexar` de fora deste repositório (scripts antigos, hábito de
operador). Cobria só `documents`, nunca as outras 12 frentes de
`rag_sources`/calculadoras — usar em vez disso:

    python -m app.commands.reindex_rag_completo_20260902 [--dry-run] [--forcar] [--only-types ...] [--limit N]

`deploy.sh` já não chama este módulo — o responsável único pela indexação
incremental do RAG é `app.commands.reindex_rag_completo_20260902` (ver seção
"Indexação RAG incremental" em deploy.sh).
"""

import argparse
import json
import sys

from app.commands.reindex_rag_completo_20260902 import rodar


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--tudo", action="store_true", help="reindexa também o que já tem embedding (equivale a --forcar)")
    args = p.parse_args()

    print(
        "AVISO: app.services.indexar está deprecado — delegando para "
        "app.commands.reindex_rag_completo_20260902 (cobre documents + as 12 "
        "frentes de rag_sources + calculadoras, não só documents).",
        file=sys.stderr,
    )
    resultado, exit_code = rodar(forcar=args.tudo)
    print(json.dumps(resultado, ensure_ascii=False, indent=2, default=str))
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
