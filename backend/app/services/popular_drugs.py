#!/usr/bin/env python3
"""Popula a tabela `drugs` (comparador lado a lado) a partir dos mesmos JSONs
de origem usados para a Biblioteca — sem passar pela conversão para Markdown,
que achata a estrutura (dose, contraindicações etc.) em texto corrido.

Por que existe separado do importador da Biblioteca: a Biblioteca guarda
prosa (`Document.body_md`), boa para leitura e para a IA. O comparador
precisa de campos estruturados (`dosing` como dict, `contraindications`
como lista) para renderizar a tabela lado a lado — por isso lê o JSON
original de novo, em vez de tentar re-extrair de Markdown já convertido.

Fontes aceitas, na mesma pasta:
  - knowledge/medicamentos/*.md   (formato do ZIP original, um arquivo por módulo)
  - um .md único com vários "## Módulo — Nome" + bloco ```json``` (Perplexity)

Uso:
    python tools/popular_drugs.py <knowledge_dir_ou_arquivo_perplexity> [outro...]
    # roda de dentro do container: python -m app.services.popular_drugs
"""

from __future__ import annotations

import glob
import json
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # tools/ -> repo root
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # backend/


def sem_acento(t: str) -> str:
    return unicodedata.normalize("NFKD", t.lower()).encode("ascii", "ignore").decode()


def slugify(v: str) -> str:
    v = re.sub(r"[^\w\s-]", "", sem_acento(v)).strip()
    return re.sub(r"[\s_-]+", "-", v)[:120].strip("-")


def limpar(t) -> str:
    if not isinstance(t, str):
        t = str(t)
    t = re.sub(r'<span style="display:none">.*?</span>', "", t, flags=re.S)
    t = re.sub(r"\[web:\d+\]", "", t)
    t = re.sub(r"\[\^[^\]]+\]", "", t)
    return re.sub(r"\s+", " ", t).strip()


def lista(v) -> list[str]:
    if not v:
        return []
    if isinstance(v, str):
        return [limpar(v)]
    if isinstance(v, list):
        saida = []
        for item in v:
            if isinstance(item, dict):
                saida.append("; ".join(f"{k}: {limpar(val)}" for k, val in item.items()))
            else:
                saida.append(limpar(item))
        return [s for s in saida if s]
    return [limpar(v)]


def texto(v) -> str | None:
    if not v:
        return None
    if isinstance(v, str):
        return limpar(v)
    if isinstance(v, dict):
        return "; ".join(f"{k}: {limpar(val)}" for k, val in v.items())
    if isinstance(v, list):
        return " | ".join(lista(v))
    return limpar(v)


def montar_dosing(d: dict) -> dict:
    """Junta todas as variações de campo de dose que os dois lotes usam num
    único dict, preservando a chave original como rótulo."""
    saida = {}
    for chave in ("dose", "dose_especifica", "dose_apresentacoes_especificas", "administracao"):
        if d.get(chave):
            saida[chave] = texto(d[chave])
    return saida


def referencias_de(d: dict) -> list[str]:
    refs = d.get("referencias") or d.get("references") or []
    saida = []
    if isinstance(refs, str):
        refs = [refs]
    for r in refs:
        if isinstance(r, dict):
            partes = [str(r.get(k)) for k in
                     ("titulo", "title", "organizacao", "ano", "year", "doi", "pmid", "url")
                     if r.get(k)]
            if partes:
                saida.append(limpar(" · ".join(partes)))
        elif isinstance(r, str):
            saida.append(limpar(r))
    return [s for s in saida if s]


def extrair_de_zip(knowledge_dir: Path) -> list[dict]:
    itens = []
    pasta = knowledge_dir / "medicamentos"
    if not pasta.is_dir():
        return itens
    for f in sorted(pasta.glob("*.md")):
        t = f.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"```json\s*(\{.*?\})\s*```", t, re.S)
        if not m:
            continue
        try:
            itens.append(json.loads(m.group(1)))
        except (ValueError, TypeError):
            pass
    return itens


def extrair_de_perplexity(arquivo: Path) -> list[dict]:
    t = arquivo.read_text(encoding="utf-8", errors="replace")
    partes = re.split(r"(^## Módulo(?: NOVO| ATUALIZADO)? ?—.*$)", t, flags=re.M)
    itens = []
    for i in range(1, len(partes), 2):
        body = partes[i + 1] if i + 1 < len(partes) else ""
        m = re.search(r"```json\s*(\{.*?\})\s*```", body, re.S)
        if not m:
            continue
        try:
            d = json.loads(m.group(1))
        except (ValueError, TypeError):
            continue
        for item in (d if isinstance(d, list) else [d]):
            if isinstance(item, dict):
                itens.append(item)
    return itens


def eh_medicamento(d: dict) -> bool:
    return bool({"nome_generico", "classe", "mecanismo_acao"} & d.keys())


def montar_drug(d: dict) -> dict | None:
    nome = d.get("nome_generico") or d.get("titulo") or d.get("title")
    if not nome:
        return None
    return {
        "slug": slugify(nome),
        "generic_name": limpar(nome),
        "brand_names": lista(d.get("nomes_comerciais") or d.get("nome_comercial")),
        "drug_class": limpar(d.get("classe") or "não classificado"),
        "mechanism": texto(d.get("mecanismo_acao")),
        "presentations": lista(d.get("apresentacoes") or d.get("apresentacao")),
        "dosing": montar_dosing(d),
        "renal_adjustment": texto(d.get("ajuste_renal") or d.get("ajuste_renal_hepatico")),
        "hepatic_adjustment": texto(d.get("ajuste_hepatico")),
        "contraindications": lista(d.get("contraindicacoes")),
        "interactions": lista(d.get("interacoes") or d.get("interacoes_criticas")),
        "monitoring": lista(d.get("monitorizacao") or d.get("monitorizacao_critica")),
        "pregnancy": texto(d.get("gravidez_lactacao") or d.get("gravidez_classificacao")),
        "lactation": texto(d.get("lactacao")),
        "outcomes": {},  # nenhuma fonte trouxe desfecho estruturado — não inventar
        "references": referencias_de(d),
        "review_status": "pendente_revisao",
    }


def coletar(fontes: list[str]) -> list[dict]:
    brutos = []
    for f in fontes:
        p = Path(f)
        if p.is_dir():
            brutos += extrair_de_zip(p)
        elif p.is_file():
            brutos += extrair_de_perplexity(p)
    candidatos = [montar_drug(d) for d in brutos if eh_medicamento(d)]
    candidatos = [c for c in candidatos if c]

    melhores: dict[str, dict] = {}
    for c in candidatos:
        atual = melhores.get(c["slug"])
        peso = lambda x: sum(len(str(v)) for v in x.values())  # noqa: E731
        if atual is None or peso(c) > peso(atual):
            melhores[c["slug"]] = c
    return list(melhores.values())


def popular(fontes: list[str]) -> dict:
    from app.core.db import SessionLocal
    from app.models.drug import Drug

    drogas = coletar(fontes)
    db = SessionLocal()
    novos = atualizados = 0
    # Mesmo filtro de `carregar_drugs.py` (issue #52): campo de documentação
    # como `review_note`, sem coluna própria em `Drug`, não pode chegar ao
    # construtor sem filtro — `Drug(**d)` levanta TypeError para kwarg
    # desconhecido, ao contrário do ramo de atualização (`setattr`, silencioso).
    colunas_drug = {c.key for c in Drug.__table__.columns}
    try:
        for d in drogas:
            existente = db.query(Drug).filter(Drug.slug == d["slug"]).first()
            if existente:
                for k, v in d.items():
                    if k not in ("slug", "review_status") and k in colunas_drug:
                        setattr(existente, k, v)
                atualizados += 1
            else:
                campos = {k: v for k, v in d.items() if k in colunas_drug}
                db.add(Drug(**campos))
                novos += 1
        db.commit()
    finally:
        db.close()
    return {"encontrados": len(drogas), "novos": novos, "atualizados": atualizados}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(1)
    print(json.dumps(popular(sys.argv[1:]), ensure_ascii=False, indent=2))
