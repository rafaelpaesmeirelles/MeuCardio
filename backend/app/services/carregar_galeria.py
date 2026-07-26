"""Carrega imagens da galeria a partir de um JSON de metadados. As imagens em
si (arquivo binário) precisam já estar em /galeria no servidor — este script
só cria/atualiza os registros no banco, e confere que o arquivo existe antes
de publicar (nunca publica registro apontando pra arquivo inexistente).

Uso:
    python -m app.services.carregar_galeria /caminho/galeria.json
"""

import json
import sys
from pathlib import Path

from app.core.db import SessionLocal
from app.models.gallery import GalleryImage

GALERIA_DIR = Path("/galeria")


def carregar(caminho_json: str) -> dict:
    itens = json.load(open(caminho_json, encoding="utf-8"))
    db = SessionLocal()
    novos, atualizados, sem_arquivo = 0, 0, []
    try:
        for item in itens:
            caminho_arquivo = GALERIA_DIR / item["file_path"]
            if not caminho_arquivo.exists():
                sem_arquivo.append(item["file_path"])
                continue

            existente = db.query(GalleryImage).filter(GalleryImage.slug == item["slug"]).first()
            if existente:
                for campo in ("title", "modality", "theme", "findings", "teaching_points",
                              "file_path", "thumbnail_path", "source_name", "source_url",
                              "license", "attribution", "tags", "review_status", "published"):
                    if campo in item:
                        setattr(existente, campo, item[campo])
                atualizados += 1
            else:
                db.add(GalleryImage(**{k: v for k, v in item.items()}))
                novos += 1
        db.commit()
    finally:
        db.close()
    return {"novos": novos, "atualizados": atualizados, "sem_arquivo": sem_arquivo}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        raise SystemExit(1)
    print(json.dumps(carregar(sys.argv[1]), ensure_ascii=False, indent=2))
