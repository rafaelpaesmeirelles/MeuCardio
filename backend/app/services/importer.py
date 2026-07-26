"""Importa o conteúdo científico em Markdown para a biblioteca.

Front matter esperado (gerado por `app.services.ingest`):

    ---
    title: "Digoxina"
    slug: "digoxina"
    theme: "Farmacologia"
    kind: "farmacologia"
    summary: "…"
    source_tier: "C"
    review_status: "fonte_terciaria_revisar"
    published: false
    gaps: ["dose.manutencao_adulto"]
    source_refs: ["[A] ESC · 2023 · … — 10.1093/…"]
    ---

Regra de segurança: o importador nunca promove um módulo a `published`.
Só um administrador publica, pela rota de revisão. Reimportar preserva a decisão
de publicação já tomada por um humano.
"""

from pathlib import Path

import frontmatter

from app.core.config import settings
from app.core.db import SessionLocal
from app.models.content import Document, DocumentRevision


def _slugify(value: str) -> str:
    import re
    import unicodedata

    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    value = re.sub(r"[^\w\s-]", "", value).strip().lower()
    return re.sub(r"[\s_-]+", "-", value)[:200]


def import_directory(path: str | None = None) -> dict:
    root = Path(path or settings.content_dir)
    if not root.exists():
        return {"erro": f"{root} não existe"}

    db = SessionLocal()
    novos = atualizados = inalterados = 0
    duplicados: list[str] = []
    falhas: list[str] = []
    vistos_neste_lote: dict[str, str] = {}  # slug -> caminho do arquivo já processado

    try:
        for md in sorted(root.rglob("*.md")):
            try:
                post = frontmatter.load(md)
                meta, body = post.metadata, post.content.strip()
                if not body:
                    continue

                title = meta.get("title") or md.stem
                slug = meta.get("slug") or _slugify(title)

                # Duplicata DENTRO deste lote: dois arquivos com o mesmo slug.
                # Checar só o banco não pega isso, porque nenhum dos dois foi
                # commitado ainda quando o segundo é processado — foi exatamente
                # o que derrubou a importação inteira antes desta correção.
                if slug in vistos_neste_lote:
                    duplicados.append(
                        f"{md.relative_to(root)}  (mesmo slug '{slug}' de "
                        f"{vistos_neste_lote[slug]} — este arquivo foi ignorado)"
                    )
                    continue
                vistos_neste_lote[slug] = str(md.relative_to(root))

                doc = db.query(Document).filter(Document.slug == slug).first()
                if doc:
                    if doc.body_md == body:
                        inalterados += 1
                        continue
                    db.add(DocumentRevision(document_id=doc.id, version=doc.version,
                                            body_md=doc.body_md))
                    doc.body_md = body
                    doc.version += 1
                    atualizados += 1
                else:
                    doc = Document(slug=slug, body_md=body, published=False)
                    db.add(doc)
                    novos += 1

                doc.title = title
                doc.theme = meta.get("theme") or md.parent.name
                doc.kind = meta.get("kind", "modulo")
                doc.summary = meta.get("summary")
                doc.tags = list(meta.get("tags") or [])
                doc.source_refs = list(meta.get("source_refs") or [])
                doc.source_tier = meta.get("source_tier", "sem_fonte")
                doc.gaps = list(meta.get("gaps") or [])
                doc.evidence_level = meta.get("evidence_level")

                # A revisão humana manda: se já foi revisado, o importador não rebaixa.
                if doc.review_status != "revisado":
                    doc.review_status = meta.get("review_status", "pendente_revisao")

                # Commit por arquivo: um documento com problema não pode derrubar
                # os outros 153 que estão corretos.
                db.commit()
            except Exception as e:  # noqa: BLE001 — precisa continuar para os próximos arquivos
                db.rollback()
                falhas.append(f"{md.relative_to(root)}: {type(e).__name__}: {e}")
    finally:
        db.close()

    resultado = {
        "novos": novos, "atualizados": atualizados, "inalterados": inalterados,
        "origem": str(root),
        "nota": "Nada foi publicado automaticamente. Publique pela rota /api/admin/documents.",
    }
    if duplicados:
        resultado["duplicados_ignorados"] = duplicados
    if falhas:
        resultado["falhas"] = falhas
    return resultado


if __name__ == "__main__":
    import json

    print(json.dumps(import_directory(), ensure_ascii=False, indent=2))
