from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user

router = APIRouter(prefix="/api/search", tags=["busca"])

# Até 29/07/2026 esta busca consultava só `documents`, e os itens de galeria,
# exames, evidências e estudos eram invisíveis para quem pesquisava — 103
# publicados que ninguém encontrava. Prioridade definida pelo Rafael naquela
# data: conteúdo publicado e invisível é mais urgente que conteúdo novo.
#
# São cinco consultas em UNION, e não uma tabela genérica, porque as frentes não
# têm esquema comum. Duas armadilhas que o desenho evita:
#
# 1. **Evidências não tem título.** O que identifica o registro é o `statement`,
#    texto longo. Aqui ele é truncado para servir de título, e o texto inteiro
#    segue no snippet — inventar um título curto exibiria dado que não existe.
# 2. **Exames usa `name`, não `title`.** Quem generaliza sem olhar quebra aqui.
#
# Os nomes de campo da resposta (`title`, `kind`, `theme`, `slug`, `snippet`)
# são mantidos de propósito, mesmo onde a semântica mudou: `Busca.tsx` consome
# exatamente esses cinco, e trocá-los quebraria a tela sem necessidade. O que é
# novo entra como campo adicional (`frente`), que é aditivo e não quebra nada.
#
# `published = true` em todas as cinco: sem isso a busca exporia o que está
# retido esperando o aval do Rafael.

SQL = text("""
WITH achados AS (
  SELECT 'documento' AS frente, slug, title, kind, theme, source_tier,
         coalesce(summary, left(body_md, 800)) AS corpo, search_vector AS v
  FROM documents WHERE published = true
  UNION ALL
  SELECT 'galeria', slug, title, modality, theme, NULL,
         coalesce(findings, ''), search_vector
  FROM gallery_images WHERE published = true
  UNION ALL
  SELECT 'exame', slug, name, category, theme, NULL,
         coalesce(what_it_measures, '') || ' ' || coalesce(interpretation, ''),
         search_vector
  FROM lab_tests WHERE published = true
  UNION ALL
  -- `statement` vira título truncado E corpo: é o mesmo campo, por falta de
  -- título nesta frente. Está declarado aqui para não parecer descuido.
  SELECT 'evidencia', slug, left(statement, 120),
         'Classe ' || recommendation_class || ' · nível ' || evidence_level,
         theme, NULL, statement, search_vector
  FROM evidence_records WHERE published = true
  UNION ALL
  SELECT 'estudo', slug, title, study_type, theme, NULL,
         coalesce(summary, '') || ' ' || coalesce(key_findings, ''), search_vector
  FROM scientific_studies WHERE published = true
)
SELECT frente, slug, title, kind, theme, source_tier,
       ts_headline('portuguese', corpo, plainto_tsquery('portuguese', :q),
                   'StartSel=<mark>,StopSel=</mark>,MaxFragments=2,FragmentDelimiter= … ') AS snippet,
       ts_rank(v, plainto_tsquery('portuguese', :q)) AS rank
FROM achados
WHERE v @@ plainto_tsquery('portuguese', :q)
ORDER BY rank DESC
LIMIT :limit
""")


@router.get("")
def search(
    q: str = Query(..., min_length=2),
    frente: str | None = Query(
        None, description="documento|galeria|exame|evidencia|estudo — vazio traz todas"),
    limit: int = Query(25, le=100),
    db: Session = Depends(get_db),
    _=Depends(current_user),
):
    rows = [dict(r) for r in db.execute(SQL, {"q": q, "limit": limit}).mappings().all()]
    if frente:
        rows = [r for r in rows if r["frente"] == frente]
    # Contagem por frente serve à interface: dizer "3 evidências, 1 estudo"
    # antes de o usuário rolar a lista é o que torna a busca ampliada útil, em
    # vez de apenas mais longa.
    por_frente: dict[str, int] = {}
    for r in rows:
        por_frente[r["frente"]] = por_frente.get(r["frente"], 0) + 1
    return {"query": q, "count": len(rows), "por_frente": por_frente, "results": rows}
