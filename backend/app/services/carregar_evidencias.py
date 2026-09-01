"""Carrega registros de evidência a partir de um JSON de metadados.

Uso:
    python -m app.services.carregar_evidencias /caminho/evidencias.json
"""

import json
import sys

from app.core.db import SessionLocal
from app.models.evidence import EvidenceRecord
from app.services.scientific_loader_safety import combined_review_note, enforce_safe_publication


# O manifesto só pode reduzir publicação: `false` põe em quarentena, `true`
# nunca promove. A decisão positiva continua fora do carregador.

# Filtro pelas colunas reais do modelo — sem ele, um campo de documentação
# novo no JSON (ex.: `review_note`) derruba a carga inteira com TypeError ao
# criar um registro novo. Foi exatamente o que aconteceu com `drugs` no
# incidente de deploy de 11/08/2026 (issue #52); aplicado aqui de forma
# preventiva, mesmo sem mismatch hoje.
_COLUNAS = {c.key for c in EvidenceRecord.__table__.columns}


def carregar(caminho_json: str) -> dict:
    itens = json.load(open(caminho_json, encoding="utf-8"))
    db = SessionLocal()
    novos, atualizados = 0, 0
    try:
        for bruto in itens:
            item = {
                k: v
                for k, v in bruto.items()
                if k not in {"published", "review_note"} and k in _COLUNAS
            }
            existente = db.query(EvidenceRecord).filter(EvidenceRecord.slug == item["slug"]).first()
            note = combined_review_note(
                bruto,
                existing=getattr(existente, "review_note", None),
            )
            if note is not None:
                item["review_note"] = note
            if existente:
                for campo, valor in item.items():
                    setattr(existente, campo, valor)
                enforce_safe_publication(existente, bruto, is_new=False)
                atualizados += 1
            else:
                registro = EvidenceRecord(**item)
                enforce_safe_publication(registro, bruto, is_new=True)
                db.add(registro)
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
