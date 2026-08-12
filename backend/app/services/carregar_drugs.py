"""Carrega um JSON com registros de medicamento já processados diretamente
na tabela `drugs`. Complementa `popular_drugs.py`: aquele lê e converte os
arquivos-fonte originais; este só faz o upsert do resultado já pronto,
sem precisar dos arquivos-fonte no servidor.

Uso:
    python -m app.services.carregar_drugs /caminho/drugs_data.json
"""

import json
import sys

from app.core.db import SessionLocal
from app.models.drug import Drug

# `review_note` (e qualquer outro campo de front matter que documente a
# verificação de fonte, sem virar dado clínico) é convenção já em uso em
# `documents`/`evidencias` deste projeto — documentação para quem lê o
# arquivo, nunca persistida no banco (`Document` não tem coluna própria e
# ignora o campo em silêncio). `Drug` também não tem essa coluna, mas ao
# contrário do importador de `Document`, este construía o registro NOVO via
# `Drug(**d)` sem filtrar — SQLAlchemy declarative rejeita kwarg desconhecido
# na criação (`TypeError: 'review_note' is an invalid keyword argument for
# Drug`), diferente do caminho de atualização (que usa `setattr`, silencioso
# para atributo não mapeado). Filtrar pelas colunas reais de `Drug` alinha os
# dois caminhos ao mesmo comportamento — nunca falha por causa de um campo de
# documentação, em nenhum dos dois ramos (issue #52).
_COLUNAS_DRUG = {c.key for c in Drug.__table__.columns}


def carregar(caminho_json: str) -> dict:
    drogas = json.load(open(caminho_json, encoding="utf-8"))
    db = SessionLocal()
    novos = atualizados = 0
    try:
        for d in drogas:
            existente = db.query(Drug).filter(Drug.slug == d["slug"]).first()
            if existente:
                # O manifesto versionado é a fonte canônica também para o
                # review_status. Se um verbete voltar a `pendente_revisao`,
                # esse estado precisa chegar ao banco para que a reconciliação
                # o despublique. Preservar o status antigo poderia manter
                # conteúdo não revisado visível depois de uma regressão.
                for k, v in d.items():
                    if k != "slug" and k in _COLUNAS_DRUG:
                        setattr(existente, k, v)
                atualizados += 1
            else:
                campos = {k: v for k, v in d.items() if k in _COLUNAS_DRUG}
                db.add(Drug(**campos))
                novos += 1
        db.commit()
    finally:
        db.close()
    return {"total": len(drogas), "novos": novos, "atualizados": atualizados}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        raise SystemExit(1)
    print(json.dumps(carregar(sys.argv[1]), ensure_ascii=False, indent=2))
