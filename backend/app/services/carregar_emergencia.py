"""Carrega `emergencia/metadados.json` para `emergency_protocols`.

Duas checagens que só existem nesta frente, e as duas por causa do que a tela é:

1. **`documento_slug`/`fluxograma_slug` precisam existir como `Document`.** Um
   protocolo revisado só pode apontar para documento publicado/revisado. Um
   protocolo ainda pendente pode apontar para documento igualmente pendente,
   porque ambos continuam fora da publicação até a mesma decisão humana. Uma
   seleção apontando para slug inexistente continua sendo recusada.
2. **`relacionados` aceita as DUAS naturezas de referência que o arquivo-fonte
   usa** — achado em 07/08/2026 ao investigar 19 protocolos que travavam entre
   si: a maioria dos itens usa `relacionados` para apontar outro DOCUMENTO
   correlato (o desenho original), mas um lote mais recente passou a usá-lo
   para apontar outro PROTOCOLO de emergência ("ver também: síndrome X"). A
   checagem original só validava contra `Document.slug`, então todo protocolo
   que citasse outro protocolo (não um documento) era recusado — inclusive
   quando os dois lados da referência já estavam prontos, só porque a busca
   olhava a tabela errada. Agora `relacionados` é aceito se o slug existir em
   QUALQUER uma das duas tabelas (Document disponível, ou EmergencyProtocol já
   presente no arquivo sendo carregado) — `documento_slug`/`fluxograma_slug`
   continuam exigindo `Document` especificamente, sem essa folga, porque são o
   texto/fluxograma que a tela realmente renderiza.
3. **`published` nunca vem do arquivo**, como nas demais frentes. Repetido aqui
   porque uma recarga não pode despublicar conteúdo em silêncio.
"""

from __future__ import annotations

import json
from pathlib import Path

from app.core.db import SessionLocal
from app.models.content import Document
from app.models.emergency import EmergencyProtocol


def _documento_pode_ser_referenciado(
    *, published: bool, document_status: str, protocol_status: str,
) -> bool:
    """Evita publicar protocolo apoiado em documento ainda não revisado."""
    return (
        published
        or document_status == "revisado"
        or (
            protocol_status == "pendente_revisao"
            and document_status == "pendente_revisao"
        )
    )


def carregar(caminho: str = "/emergencia/metadados.json") -> dict:
    dados = json.loads(Path(caminho).read_text(encoding="utf-8"))
    db = SessionLocal()
    novos = atualizados = 0
    recusados: list[dict] = []
    try:
        documentos = {
            slug: (bool(published), review_status)
            for slug, published, review_status in db.query(
                Document.slug, Document.published, Document.review_status,
            ).all()
        }
        # Todo slug de protocolo que já existe no arquivo sendo carregado —
        # cobre tanto os já persistidos quanto os que este mesmo `carregar()`
        # vai criar (o próprio arquivo é a lista completa de protocolos).
        protocolos_do_arquivo = {item["slug"] for item in dados}

        for item in dados:
            status_protocolo = item.get("review_status", "pendente_revisao")
            documentos_disponiveis = {
                slug
                for slug, (published, status_documento) in documentos.items()
                if _documento_pode_ser_referenciado(
                    published=published,
                    document_status=status_documento,
                    protocol_status=status_protocolo,
                )
            }
            faltando_documento = [
                s for s in (item["documento_slug"], item.get("fluxograma_slug"))
                if s and s not in documentos_disponiveis
            ]
            faltando_relacionado = [
                s for s in (item.get("relacionados") or [])
                if s not in documentos_disponiveis and s not in protocolos_do_arquivo
            ]
            faltando = faltando_documento + faltando_relacionado
            if faltando:
                recusados.append({"slug": item["slug"],
                                  "motivo": "documento inexistente ou ainda não revisado",
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
            reg.review_status = status_protocolo
            # `published` fica de fora de propósito — ver docstring do módulo.

        db.commit()
    finally:
        db.close()
    return {"total": len(dados), "novos": novos, "atualizados": atualizados,
            "recusados": recusados}


if __name__ == "__main__":
    print(json.dumps(carregar(), ensure_ascii=False, indent=2))
