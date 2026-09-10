"""Scientific shared reading. Subscriber access; no AI plan, private files or writes."""
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.security import current_user
from app.models.scientific_publication_asset import ScientificPublicationAsset
from app.services import cofre
from app.services.scientific_reading import reading_manifest, get_entity, entity_sources
from app.services.scientific_publication_library import library_root
router = APIRouter(prefix='/api/scientific-reading', tags=['leitura-cientifica'])

@router.get('/{entity_type}/{slug}')
def manifest(entity_type: str, slug: str, db: Session = Depends(get_db), user=Depends(current_user)):
    return reading_manifest(db, entity_type, slug)

@router.get('/{entity_type}/{slug}/sources/{source_key}/{variant}')
def artifact(entity_type: str, slug: str, source_key: str, variant: str, db: Session = Depends(get_db), user=Depends(current_user)):
    row = get_entity(db, entity_type, slug)
    if source_key not in {s['key'] for s in entity_sources(db, row)}:
        raise HTTPException(404, 'Fonte não vinculada a este conteúdo publicado.')
    asset = db.query(ScientificPublicationAsset).filter_by(source_key=source_key).first()
    if not asset or not asset.license_url or not asset.source_sha256:
        raise HTTPException(404, 'Arquivo científico ainda não disponível.')
    if variant == 'original':
        key, media, suffix = asset.original_storage_key, 'application/xml', 'xml'
    elif variant == 'translation' and asset.status == 'ready' and asset.coverage.get('complete_text'):
        key, media, suffix = asset.translated_storage_key, 'text/plain; charset=utf-8', 'txt'
    else: raise HTTPException(404, 'Tradução integral ainda não disponível.')
    if not key: raise HTTPException(404, 'Arquivo científico ainda não disponível.')
    try: content = cofre.ler(key, asset.id, raiz=library_root())
    except (FileNotFoundError, cofre.CofreIndisponivel): raise HTTPException(503, 'Arquivo temporariamente indisponível.')
    return Response(content=content, media_type=media, headers={'Content-Disposition': f'attachment; filename="{variant}-{source_key[:12]}.{suffix}"', 'Cache-Control': 'private, no-store', 'X-Content-Type-Options': 'nosniff'})
