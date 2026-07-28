"""Carrega os checklists de alta a partir do JSON de metadados.

Uso:
    python -m app.services.carregar_checklists /checklists/metadados.json
"""

import json
import sys

from app.core.db import SessionLocal
from app.models.checklist import DischargeChecklist

# `published` NUNCA vem do JSON, pelo mesmo motivo das outras frentes: publicar
# é decisão humana registrada pela rota de publicação, e copiar o campo do
# arquivo por cima do banco já tirou conteúdo do ar em silêncio neste projeto.

# Campos que o modelo aceita. Qualquer outro no JSON é ignorado de propósito —
# um campo novo no arquivo deve falhar em ser gravado, e não criar coluna
# fantasma ou estourar erro no meio da carga das outras condições.
CAMPOS = {"slug", "condicao", "resumo", "theme", "documento_origem",
          "itens", "source_refs", "review_status"}


def carregar(caminho_json: str) -> dict:
    itens = json.load(open(caminho_json, encoding="utf-8"))
    db = SessionLocal()
    novos = atualizados = 0
    avisos: list[str] = []
    try:
        for bruto in itens:
            item = {k: v for k, v in bruto.items() if k in CAMPOS}

            # Um checklist sem item é um cabeçalho vazio na tela de quem vai dar
            # alta. Melhor recusar e dizer qual do que carregar e deixar o
            # médico descobrir na hora.
            if not item.get("itens"):
                avisos.append(f"{item.get('slug','?')}: sem itens, não carregado")
                continue

            ids = [i.get("id") for i in item["itens"]]
            if len(ids) != len(set(ids)):
                avisos.append(f"{item['slug']}: ids de item repetidos, não carregado")
                continue
            sem_origem = [i.get("id") for i in item["itens"] if not i.get("origem_secao")]
            if sem_origem:
                # Não bloqueia, mas registra: o briefing exige que os itens venham
                # do protocolo correspondente, e item sem seção de origem é item
                # que ninguém consegue rastrear depois.
                avisos.append(f"{item['slug']}: itens sem origem_secao: {sem_origem}")

            existente = db.query(DischargeChecklist).filter(
                DischargeChecklist.slug == item["slug"]
            ).first()
            if existente:
                for campo, valor in item.items():
                    setattr(existente, campo, valor)
                atualizados += 1
            else:
                db.add(DischargeChecklist(**item))
                novos += 1
        db.commit()
    finally:
        db.close()
    resultado = {"novos": novos, "atualizados": atualizados}
    if avisos:
        resultado["avisos"] = avisos
    return resultado


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        raise SystemExit(1)
    print(json.dumps(carregar(sys.argv[1]), ensure_ascii=False, indent=2))
