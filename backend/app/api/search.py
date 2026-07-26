from fastapi import APIRouter, Depends, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import current_user

router = APIRouter(prefix="/api/search", tags=["busca"])

SQL = text("""
SELECT slug, title, kind, theme, source_tier,
       ts_headline('portuguese', coalesce(summary, left(body_md, 800)),
                   plainto_tsquery('portuguese', :q),
                   'StartSel=<mark>,StopSel=</mark>,MaxFragments=2,FragmentDelimiter= … ') AS snippet,
       ts_rank(search_vector, plainto_tsquery('portuguese', :q)) AS rank
FROM documents
WHERE published = true
  AND search_vector @@ plainto_tsquery('portuguese', :q)
ORDER BY rank DESC
LIMIT :limit
""")


@router.get("")
def search(
    q: str = Query(..., min_length=2),
    limit: int = Query(25, le=100),
    db: Session = Depends(get_db),
    _=Depends(current_user),
):
    rows = db.execute(SQL, {"q": q, "limit": limit}).mappings().all()
    return {"query": q, "count": len(rows), "results": [dict(r) for r in rows]}
