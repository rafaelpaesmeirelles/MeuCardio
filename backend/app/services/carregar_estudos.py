"""Carrega estudos científicos a partir de um JSON de metadados.

Uso:
    python -m app.services.carregar_estudos /caminho/estudos.json
"""

import json
import sys

from app.core.db import SessionLocal
from app.models.study import ScientificStudy


# `published` NUNCA vem do JSON. Publicar e decisao humana, registrada no banco
# pela rota /api/admin/conteudo/publicar — e o checkpoint de revisao clinica
# exigido para conteudo que vai a producao. Antes desta guarda, qualquer
# recarga copiava `published: false` do arquivo por cima do banco e tirava do
# ar tudo que ja estava publicado. Foi o que aconteceu com evidencias e
# estudos ao recarregar uma correcao de texto. Mesmo principio que o
# importer.py ja aplica aos documentos de content/.

# Filtro pelas colunas reais do modelo — sem ele, um campo de documentação
# novo no JSON (ex.: `review_note`) derruba a carga inteira com TypeError ao
# criar um registro novo. Foi exatamente o que aconteceu com `drugs` no
# incidente de deploy de 11/08/2026 (issue #52); aplicado aqui de forma
# preventiva, mesmo sem mismatch hoje.
_COLUNAS = {c.key for c in ScientificStudy.__table__.columns}


def carregar(caminho_json: str) -> dict:
    itens = json.load(open(caminho_json, encoding="utf-8"))
    db = SessionLocal()
    novos, atualizados = 0, 0
    try:
        for item in itens:
            item = {k: v for k, v in item.items() if k != "published" and k in _COLUNAS}
            existente = db.query(ScientificStudy).filter(ScientificStudy.slug == item["slug"]).first()
            if existente:
                for campo, valor in item.items():
                    setattr(existente, campo, valor)
                atualizados += 1
            else:
                db.add(ScientificStudy(**item))
                novos += 1
        db.commit()
    finally:
        db.close()
    return {"novos": novos, "atualizados": atualizados}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        raise SystemExit(1)
    print(json.dumps(carregar(sys.argv[1]), ensure_ascii=False, indent=2))
