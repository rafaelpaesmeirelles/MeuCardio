#!/usr/bin/env python3
"""Consolida duplicatas entre temas.

As duas migrações anteriores usavam uma lista de palavras-chave para decidir
o tema de protocolos e estudos, e a ordem dessa lista tinha um defeito: temas
amplos ("Doença coronariana", "Prevenção e lipídios") vinham antes de temas
estreitos ("Pericárdio", "Cardio-oncologia"), então qualquer texto que citasse
de passagem "coronariana" ou "lipídeos" caía no tema errado. O resultado:
47 documentos existem hoje em dois temas ao mesmo tempo.

Este script agrupa por título normalizado, decide o tema correto (usando
`kind` quando o documento é medicamento/calculadora/estudo, ou o classificador
corrigido quando é protocolo), mantém a versão de maior corpo e apaga a outra.

Uso:
    python tools/consolidar_temas.py content
"""

from __future__ import annotations

import argparse
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import frontmatter  # noqa: E402
from migrar_perplexity_md import TEMA_POR_CATEGORIA, tema_clinico  # noqa: E402

KIND_PARA_TEMA = {"farmacologia": "Farmacologia", "calculadora": "Calculadoras"}
# "estudo" fica de fora: título de estudo/registro pode coincidir com o nome
# curto de um protocolo (ex.: "AF-CARE") sem ser o mesmo tipo de documento —
# forçar o tema por kind nesse caso já causou uma reclassificação errada.


def sem_acento(t: str) -> str:
    return unicodedata.normalize("NFKD", t.lower()).encode("ascii", "ignore").decode()


def pasta_de(tema: str) -> str:
    return tema.replace(" ", "_")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("content_dir", type=Path)
    p.add_argument("--aplicar", action="store_true", help="sem esta flag, só mostra o plano")
    args = p.parse_args()

    grupos: dict[str, list[dict]] = {}
    for f in args.content_dir.glob("*/*.md"):
        post = frontmatter.load(f)
        chave = sem_acento(post.get("title", f.stem))
        grupos.setdefault(chave, []).append({
            "path": f, "tema": post.get("theme", ""), "kind": post.get("kind", ""),
            "corpo_len": len(post.content), "post": post,
        })

    duplicados = {k: v for k, v in grupos.items() if len(v) > 1}
    print(f"Grupos com mais de uma versão: {len(duplicados)}")

    movidos = removidos = 0
    for titulo, versoes in duplicados.items():
        # tema canônico: se alguma versão é medicamento/calculadora/estudo, o
        # `kind` decide; senão usa o classificador corrigido no maior corpo.
        kind_forte = next((v["kind"] for v in versoes if v["kind"] in KIND_PARA_TEMA), None)

        if kind_forte:
            # Não basta o corpo maior: um "Protocolo" e um "Medicamento" podem
            # colidir no mesmo título limpo sem serem o mesmo conteúdo. Só
            # comparamos tamanho entre versões da mesma estrutura (mesmo kind).
            mesmo_kind = [v for v in versoes if v["kind"] == kind_forte]
            maior = max(mesmo_kind, key=lambda v: v["corpo_len"])
            tema_certo = KIND_PARA_TEMA[kind_forte]
        else:
            maior = max(versoes, key=lambda v: v["corpo_len"])
            tema_certo = tema_clinico(titulo, maior["tema"], maior["post"].content[:800])

        destino = args.content_dir / pasta_de(tema_certo) / maior["path"].name

        print(f"\n{titulo}")
        for v in versoes:
            marca = "MANTÉM" if v is maior else "remove"
            print(f"  [{marca}] {v['tema']:32s} {v['corpo_len']:5d}  {v['path']}")
        if tema_certo != maior["tema"]:
            print(f"  -> tema corrigido para: {tema_certo}")

        if args.aplicar:
            for v in versoes:
                if v is maior:
                    continue
                v["path"].unlink()
                removidos += 1
            if maior["tema"] != tema_certo:
                maior["post"]["theme"] = tema_certo
                destino.parent.mkdir(parents=True, exist_ok=True)
                destino.write_text(frontmatter.dumps(maior["post"]) + "\n", encoding="utf-8")
                if maior["path"] != destino:
                    maior["path"].unlink(missing_ok=True)
                movidos += 1

    print(f"\n{'Aplicado' if args.aplicar else 'Simulação'}: "
          f"{removidos} removidos, {movidos} recolocados no tema correto.")
    if not args.aplicar:
        print("Rode de novo com --aplicar para efetivar.")


if __name__ == "__main__":
    main()
