"""Carrega imagens da galeria a partir de um JSON de metadados. As imagens em
si precisam existir no volume /galeria em produção ou ao lado do manifesto no
checkout de CI/desenvolvimento. O script só cria/atualiza registros quando o
arquivo existe, evitando cartões quebrados.

Uso:
    python -m app.services.carregar_galeria /caminho/galeria.json
"""

import json
import sys
from pathlib import Path

from app.core.db import SessionLocal
from app.models.gallery import GalleryImage
from app.services.scientific_loader_safety import enforce_safe_publication

GALERIA_DIR = Path("/galeria")


# `published` NUNCA vem do JSON. Publicar e decisao humana, registrada no banco
# pela rota /api/admin/conteudo/publicar — e o checkpoint de revisao clinica
# exigido para conteudo que vai a producao. Antes desta guarda, qualquer
# recarga copiava `published: false` do arquivo por cima do banco e tirava do
# ar tudo que ja estava publicado.

# Campos que o modelo aceita, derivados das colunas reais de `GalleryImage`
# — mesmo padrão de `carregar_estudos.py`/`carregar_evidencias.py`/
# `carregar_exames.py`/`carregar_drugs.py`, adotado aqui (revisão adversarial
# pós-incidente) em vez de uma lista fixa mantida à mão: uma coluna nova no
# modelo já entra automaticamente, sem precisar lembrar de atualizar dois
# lugares. Sem este filtro, um campo de documentação novo no JSON (ex.:
# `review_note`, convenção já usada em outras frentes) derrubaria a carga
# inteira com TypeError ao tentar `GalleryImage(**item)` — foi exatamente o
# que aconteceu com `drugs` no incidente de deploy de 11/08/2026 (issue #52).
# `_EXCLUIDOS` são os campos que nunca devem vir do JSON: `id` é auto-gerado,
# `published` é decisão humana (nunca sobrescrita por recarga, ver guarda
# abaixo), `created_at`/`reviewed_by` são geridos pelo próprio banco/fluxo de
# revisão, não pelo conteúdo.
_EXCLUIDOS = {"id", "published", "created_at", "reviewed_by"}
CAMPOS = {c.key for c in GalleryImage.__table__.columns} - _EXCLUIDOS


def _asset_root(caminho_json: str) -> Path:
    """Prioriza o volume produtivo e usa o diretório versionado em CI/dev."""
    if GALERIA_DIR.exists():
        return GALERIA_DIR
    return Path(caminho_json).resolve().parent


def carregar(caminho_json: str) -> dict:
    itens = json.load(open(caminho_json, encoding="utf-8"))
    asset_root = _asset_root(caminho_json)
    db = SessionLocal()
    novos, atualizados, sem_arquivo = 0, 0, []
    try:
        for item in itens:
            caminho_arquivo = asset_root / item["file_path"]
            if not caminho_arquivo.is_file():
                sem_arquivo.append(item["file_path"])
                continue

            existente = db.query(GalleryImage).filter(GalleryImage.slug == item["slug"]).first()
            if existente:
                for campo in CAMPOS - {"slug"}:
                    if campo in item:
                        setattr(existente, campo, item[campo])
                enforce_safe_publication(existente, item, is_new=False)
                atualizados += 1
            else:
                registro = GalleryImage(**{k: v for k, v in item.items() if k in CAMPOS})
                enforce_safe_publication(registro, item, is_new=True)
                db.add(registro)
                novos += 1
        db.commit()
    finally:
        db.close()
    return {
        "novos": novos,
        "atualizados": atualizados,
        "sem_arquivo": sem_arquivo,
        "asset_root": str(asset_root),
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        raise SystemExit(1)
    print(json.dumps(carregar(sys.argv[1]), ensure_ascii=False, indent=2))
