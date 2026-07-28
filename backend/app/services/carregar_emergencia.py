"""Carrega `emergencia/metadados.json` para `emergency_protocols`.

Duas checagens que só existem nesta frente, e as duas por causa do que a tela é:

1. **O documento referenciado precisa existir e estar publicado.** Uma seleção
   apontando para slug inexistente produziria um cartão que abre vazio — na
   única tela do sistema em que abrir vazio custa tempo que o paciente não tem.
   O registro é recusado, com o motivo, em vez de carregado torto.
2. **`published` nunca vem do arquivo**, como nas demais frentes. Repetido aqui
   porque já aconteceu de verdade: um carregador copiava o campo do JSON por
   cima do banco e qualquer recarga despublicava tudo em silêncio.
"""

from __future__ import annotations

import json
from pathlib import Path

from app.core.db import SessionLocal
from app.models.content import Document
from app.models.emergency import EmergencyProtocol


def carregar(caminho: str = "/emergencia/metadados.json") -> dict:
    dados = json.loads(Path(caminho).read_text(encoding="utf-8"))
    db = SessionLocal()
    novos = atualizados = 0
    recusados: list[dict] = []
    try:
        publicados = {
            s for (s,) in db.query(Document.slug).filter(Document.published.is_(True)).all()
        }

        for item in dados:
            faltando = [
                s for s in ([item["documento_slug"], item.get("fluxograma_slug")]
                            + list(item.get("relacionados") or []))
                if s and s not in publicados
            ]
            if faltando:
                recusados.append({"slug": item["slug"],
                                  "motivo": "documento não publicado ou inexistente",
                                  "slugs": faltando})
                continue

            reg = (db.query(EmergencyProtocol)
                     .filter(EmergencyProtocol.slug == item["slug"]).first())
            if reg is None:
                reg = EmergencyProtocol(slug=item["slug"])
                db.add(reg)
                novos += 1
            else:
                atualizados += 1

            reg.titulo = item["titulo"]
            reg.gatilho = item.get("gatilho")
            reg.ordem = item.get("ordem", 99)
            reg.documento_slug = item["documento_slug"]
            reg.fluxograma_slug = item.get("fluxograma_slug")
            reg.relacionados = list(item.get("relacionados") or [])
            reg.review_status = item.get("review_status", "pendente_revisao")
            # `published` fica de fora de propósito — ver docstring do módulo.

        db.commit()
    finally:
        db.close()
    return {"total": len(dados), "novos": novos, "atualizados": atualizados,
            "recusados": recusados}


if __name__ == "__main__":
    print(json.dumps(carregar(), ensure_ascii=False, indent=2))
