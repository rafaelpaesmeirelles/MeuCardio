"""Scientific shared reading. Subscriber access; no AI plan, private files or writes."""
import hashlib
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.security import current_user
from app.models.scientific_publication_asset import ScientificPublicationAsset
from app.services import cofre
from app.services.scientific_reading import reading_manifest, get_entity, entity_sources
from app.services.scientific_publication_library import library_root
from app.services.scientific_original_reading import parse_original_fulltext, OriginalReadError
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
    if variant in ('original', 'original-text'):
        source_format = (asset.coverage or {}).get('source_format', 'jats_xml')
        if source_format not in ('jats_xml', 'pdf'):
            raise HTTPException(404, 'Formato do original ainda não disponível para leitura.')
        key = asset.original_storage_key
        media, suffix = ('application/pdf', 'pdf') if source_format == 'pdf' else ('application/xml', 'xml')
    elif variant == 'translation' and asset.status == 'ready' and asset.coverage.get('complete_text'):
        key, media, suffix = asset.translated_storage_key, 'text/plain; charset=utf-8', 'txt'
    else: raise HTTPException(404, 'Tradução integral ainda não disponível.')
    if not key: raise HTTPException(404, 'Arquivo científico ainda não disponível.')
    try: content = cofre.ler(key, asset.id, raiz=library_root())
    except (FileNotFoundError, cofre.CofreIndisponivel): raise HTTPException(503, 'Arquivo temporariamente indisponível.')
    if variant in ('original', 'original-text') and hashlib.sha256(content).hexdigest() != asset.source_sha256:
        raise HTTPException(503, 'A integridade do arquivo original não pôde ser confirmada.')
    if variant in ('original', 'original-text') and source_format == 'pdf' and not content.startswith(b'%PDF-'):
        raise HTTPException(503, 'O formato do arquivo original não pôde ser confirmado.')
    if variant == 'original-text':
        if source_format == 'pdf':
            text_proof = (asset.progress or {}).get('original_text') or {}
            if not isinstance(text_proof, dict) or text_proof.get('source_format') != 'pdf' or text_proof.get('source_sha256') != asset.source_sha256 or not text_proof.get('storage_key') or not text_proof.get('sha256'):
                raise HTTPException(404, 'Consulte o original em PDF; extração textual não disponibilizada.')
            try:
                extracted = cofre.ler(text_proof['storage_key'], asset.id, raiz=library_root())
            except (FileNotFoundError, cofre.CofreIndisponivel):
                raise HTTPException(503, 'Texto do original temporariamente indisponível.')
            if hashlib.sha256(extracted).hexdigest() != text_proof['sha256'] or len(extracted) > 8 * 1024 * 1024:
                raise HTTPException(503, 'A integridade do texto extraído não pôde ser confirmada.')
            try:
                original_text = extracted.decode('utf-8')
            except UnicodeDecodeError:
                raise HTTPException(503, 'A codificação do texto extraído não pôde ser confirmada.')
            if not original_text.strip() or len(original_text) > 2_000_000:
                raise HTTPException(503, 'O texto integral extraído não pôde ser confirmado.')
            content = ('Original em PDF — texto extraído; diagramação no arquivo original. Nenhuma tradução por IA foi realizada.\n\n' + original_text).encode('utf-8')
        else:
            provenance = (asset.progress or {}).get('import_provenance') or {}
            proof = {}
            if isinstance(provenance, dict) and provenance.get('source_sha256') == asset.source_sha256 and provenance.get('license_url') == asset.license_url:
                proof = {'verified_license_url': asset.license_url, 'verified_source_sha256': asset.source_sha256}
            try: parsed = parse_original_fulltext(content, asset.doi, **proof)
            except OriginalReadError:
                raise HTTPException(503, 'A leitura integral do arquivo original não pôde ser confirmada.')
            content = (parsed['attribution'] + '\n\nTexto do artigo no idioma original. Traduções em outros idiomas não são concatenadas nesta leitura. Tabelas e fórmulas têm representação textual; consulte o original e a fonte para sua apresentação gráfica, figuras e suplementos.\n\n' + parsed['text']).encode('utf-8')
        media, suffix = 'text/plain; charset=utf-8', 'txt'
    return Response(content=content, media_type=media, headers={'Content-Disposition': f'attachment; filename="{variant}-{source_key[:12]}.{suffix}"', 'Cache-Control': 'private, no-store', 'X-Content-Type-Options': 'nosniff'})
