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

import re
from pathlib import Path

import frontmatter

from app.core.config import settings
from app.core.db import SessionLocal
from app.models.content import Document, DocumentRevision


# Fontes que não sustentam conteúdo clínico neste produto: site comercial de
# bula, guia interno de outra instituição, wiki, material de estudante,
# agregador e calculadora. A Fase B já removeu sete delas do acervo à mão; esta
# lista existe para o importador reconhecer o resto sozinho.
FONTES_FRACAS = (
    "consultaremedios", "consulta remédios", "guiafarmaceutico", "hsl.org.br",
    "sírio-libanês", "sirio-libanes", "health.ucsd.edu", "medscape", "mdcalc",
    "drugs.com", "wikipedia", "wikipédia", "wikidoc", "sanarmed", "sanar",
    "pebmed", "medicinanet", "tuasaude", "youtube", "empendium", "rdocumentation",
    "doccheck", "flexikon", "slideshare", "scribd",
)

# Marcadores de fonte primária: diretriz de sociedade ou artigo com
# identificador persistente. Um DOI/PMID não prova que o artigo diz o que o
# documento afirma — prova só que a referência existe e é rastreável, que é
# exatamente o que este campo mede.
#
# O DOI vai por regex, não por substring: procurar `"10."` solto classificava
# como primária qualquer referência cuja URL tivesse um `10.` no meio, e foi o
# que aconteceu com um verbete apoiado só no NCBI Bookshelf.
IDENTIFICADOR_PERSISTENTE = re.compile(r"\b10\.\d{4,9}/\S+|\bpmid[:\s]*\d{6,9}", re.I)

MARCADORES_PRIMARIOS = (
    "diretriz", "guideline", "consensus", "consenso", "statement",
    "sociedade brasileira de cardiologia", "american college of",
    "american heart association", "european society of cardiology",
    "n engl j med", "lancet", "circulation", "jama", "eur heart j", "bmj",
)

MARCA_LACUNA = "VERIFICAÇÃO HUMANA NECESSÁRIA"


def derivar_tier(refs: list[str]) -> str:
    """Deriva `source_tier` das próprias referências.

    Existe porque o campo era lido só do front matter, com padrão `sem_fonte`, e
    **nenhum** dos arquivos o declara — então os 249 documentos entravam como
    "sem fonte", inclusive os bem referenciados. A fila de revisão ordena por
    tier, de modo que o defeito não deixava um dado errado à vista: deixava a
    priorização inteira sem efeito, que é pior porque não parece quebrado.
    """
    if not refs:
        return "sem_fonte"
    texto = [r.lower() for r in refs]
    if any(IDENTIFICADOR_PERSISTENTE.search(r) or any(m in r for m in MARCADORES_PRIMARIOS)
           for r in texto):
        return "A"
    if all(any(f in r for f in FONTES_FRACAS) for r in texto):
        return "C"
    return "B"


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
                corpo_mudou = doc is None or doc.body_md != body
                if doc:
                    # Só o corpo gera revisão e sobe a versão. O front matter é
                    # reaplicado sempre, mesmo com corpo idêntico: antes desta
                    # separação, o importador dava `continue` quando o corpo não
                    # mudava e engolia toda correção de metadado — trocar
                    # `theme`, `summary`, `tags` ou `source_refs` não tinha
                    # efeito nenhum, e o relatório ainda dizia "inalterados",
                    # o que parecia sucesso. Foi assim que um `theme` com
                    # underscore sobreviveu a várias reimportações.
                    if corpo_mudou:
                        db.add(DocumentRevision(document_id=doc.id, version=doc.version,
                                                body_md=doc.body_md))
                        doc.body_md = body
                        doc.version += 1
                        atualizados += 1
                    else:
                        inalterados += 1
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
                # Declarado no arquivo vence; sem declaração, deriva das refs.
                doc.source_tier = meta.get("source_tier") or derivar_tier(doc.source_refs)

                lacunas = list(meta.get("gaps") or [])
                # Quem escreve marca a incerteza no corpo, com o texto literal que o
                # CLAUDE.md exige. Sem esta linha a marcação ficava só na prosa e não
                # chegava a `com_lacuna_declarada`, ou seja, não entrava em fila
                # nenhuma — some da revisão exatamente o que foi sinalizado.
                if MARCA_LACUNA in body and MARCA_LACUNA not in lacunas:
                    lacunas.append(MARCA_LACUNA)
                doc.gaps = lacunas
                doc.evidence_level = meta.get("evidence_level")

                # O arquivo é a fonte da verdade do status de revisão, inclusive para
                # rebaixar. Antes, o importador se recusava a mexer em qualquer
                # documento já marcado `revisado` — e como a rota de publicação
                # carimbava `revisado` ao publicar, bastava publicar para o status
                # ficar preso em "revisado" para sempre. Resultado medido: 249/249
                # documentos constavam revisados, com 159 arquivos dizendo
                # `pendente_revisao`. O sistema afirmava ao assinante uma revisão
                # que ninguém tinha feito.
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
