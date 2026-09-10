"""Published scientific objects -> shared source identity; read-only, no paid calls."""
import hashlib
import re
from urllib.parse import urlsplit, urlunsplit, quote
from fastapi import HTTPException
from app.models.content import Document
from app.models.study import ScientificStudy
from app.models.evidence import EvidenceRecord
from app.models.guideline import Guideline
from app.models.specialty_guide import SpecialtyDisease, SymptomTriageGuide
from app.models.drug import Drug
from app.models.lab_test import LabTest
from app.models.clinical_case import ClinicalCase
from app.models.study_track import StudyTrack
from app.models.emergency import EmergencyProtocol
from app.models.patient_material import PatientMaterial
from app.models.gallery import GalleryImage
from app.models.checklist import DischargeChecklist
from app.models.scientific_publication_asset import ScientificPublicationAsset

MODELS = {'documento': Document, 'fluxograma': Document, 'estudo': ScientificStudy,
          'evidencia': EvidenceRecord, 'diretriz': Guideline, 'doenca': SpecialtyDisease,
          'triagem': SymptomTriageGuide, 'medicamento': Drug, 'exame': LabTest,
          'caso_clinico': ClinicalCase, 'trilha': StudyTrack, 'emergencia': EmergencyProtocol,
          'material_paciente': PatientMaterial, 'imagem': GalleryImage, 'checklist': DischargeChecklist}
VISIBLE_GUIDELINES = ('revisada', 'analisada', 'revisao_necessaria', 'aplicada_auto')
DOI = re.compile(r'10\.\d{4,9}/[-._;()/:A-Z0-9]+', re.I)

def normalize_doi(value):
    match = DOI.search(str(value or ''))
    if not match: return None
    value = match.group(0).rstrip('.,;').lower()
    while value.endswith(')') and value.count(')') > value.count('('): value = value[:-1]
    return value

def source_identity(value):
    value = str(value or '').strip()
    doi = normalize_doi(value)
    if doi:
        identity, url = 'doi:' + doi, 'https://doi.org/' + doi
    else:
        match = re.search(r'https?://[^\s<>\]"}]+', value, re.I)
        if not match:
            return None
        url = match.group(0).rstrip('.,;)')
        try:
            parsed = urlsplit(url)
            if parsed.scheme not in ('http', 'https') or not parsed.hostname or parsed.username or parsed.password:
                return None
            url = urlunsplit((parsed.scheme, parsed.netloc.lower(), parsed.path, parsed.query, ''))
        except ValueError:
            return None
        identity = 'url:' + url
    return {'key': hashlib.sha256(identity.encode()).hexdigest(), 'doi': doi, 'url': url}

def published_query(db, model):
    query = db.query(model)
    if model is Guideline: return query.filter(model.detection_status.in_(VISIBLE_GUIDELINES))
    query = query.filter(model.published.is_(True))
    if model is StudyTrack: query = query.filter(model.review_status == 'revisado')
    return query

def get_entity(db, entity_type, slug):
    if entity_type == 'publicacao_original':
        from app.services.scientific_publication_catalog import public_asset_query, public_asset_entity
        row = public_asset_query(db).filter(ScientificPublicationAsset.source_key == slug).first()
        if row is None: raise HTTPException(404, 'Publicação original não disponível no acervo público.')
        return public_asset_entity(row)
    if entity_type == 'descoberta':
        from app.services.guideline_source_trust import is_trusted_official_guideline
        row = db.query(Guideline).filter(Guideline.slug == slug).first()
        if row is None or not row.doi or not is_trusted_official_guideline(row):
            raise HTTPException(404, 'Publicação científica não confirmada pelo radar.')
        return row
    if entity_type == 'calculadora':
        from app.services.calculators import REGISTRY
        row = REGISTRY.get(slug)
        if row is None: raise HTTPException(404, 'Calculadora não encontrada.')
        return row
    model = MODELS.get(entity_type)
    if model is None:
        raise HTTPException(404, 'Tipo de conteúdo científico não encontrado.')
    if entity_type == 'estudo':
        from app.services.study_slug_aliases import canonical_study_slug
        slug = canonical_study_slug(slug)
    row = published_query(db, model).filter(model.slug == slug).first()
    if row is None:
        raise HTTPException(404, 'Conteúdo científico publicado não encontrado.')
    return row

def references(row):
    values = []
    for name in ('doi', 'url', 'source_url', 'source_refs', 'source_urls', 'reference', 'references', 'fontes'):
        value = getattr(row, name, None)
        if isinstance(value, str):
            values.append(value)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, str): values.append(item)
                elif isinstance(item, dict):
                    values.extend(str(item.get(k) or '') for k in ('doi', 'url', 'source_url', 'reference'))
    result = {}
    for value in values:
        # A reference may contain several explicitly identified publications.
        matches = list(DOI.finditer(value))
        candidates = [m.group(0) for m in matches] if matches else [value]
        for candidate in candidates:
            source = source_identity(candidate)
            if source: result[source['key']] = source
    return list(result.values())

def entity_sources(db, row):
    result = {s['key']: s for s in references(row)}
    linked = [getattr(row, name, None) for name in ('documento_slug', 'document_slug', 'documento_origem')]
    linked.extend(getattr(row, 'related_document_slugs', None) or [])
    for slug in linked:
        if not slug: continue
        doc = published_query(db, Document).filter(Document.slug == slug).first()
        if doc:
            result.update((s['key'], s) for s in references(doc))
    study_slug = getattr(row, 'study_slug', None)
    if study_slug:
        study = published_query(db, ScientificStudy).filter(ScientificStudy.slug == study_slug).first()
        if study: result.update((s['key'], s) for s in references(study))
    # Track steps reference public source-bearing content, not private progress.
    if isinstance(row, StudyTrack):
        for step in row.etapas or []:
            if not isinstance(step, dict): continue
            kind = step.get('item_type') or step.get('tipo')
            slug = step.get('item_slug') or step.get('slug')
            model = MODELS.get(kind)
            if model in (Document, ScientificStudy, EvidenceRecord) and slug:
                item = published_query(db, model).filter(model.slug == slug).first()
                if item: result.update((s['key'], s) for s in references(item))
    return list(result.values())

def editorial_summary(row):
    for name in ('summary', 'resumo', 'objetivo', 'what_it_measures', 'mechanism', 'findings', 'gatilho', 'purpose'):
        value = getattr(row, name, None)
        if isinstance(value, str) and value.strip(): return value.strip()
    return None

def reading_manifest(db, entity_type, slug):
    row = get_entity(db, entity_type, slug)
    sources = entity_sources(db, row)
    keys = [s['key'] for s in sources]
    assets = {a.source_key: a for a in db.query(ScientificPublicationAsset).filter(ScientificPublicationAsset.source_key.in_(keys)).all()} if keys else {}
    for source in sources:
        asset = assets.get(source['key'])
        base = f'/api/scientific-reading/{quote(entity_type, safe="")}/{quote(row.slug, safe="")}/sources/{source["key"]}'
        has_original = bool(asset and asset.original_storage_key and asset.license_url and asset.source_sha256)
        source_format = (asset.coverage or {}).get('source_format', 'jats_xml') if asset else None
        extracted_original = (asset.progress or {}).get('original_text') if asset else None
        readable_pdf = bool(isinstance(extracted_original, dict) and extracted_original.get('storage_key') and
                            extracted_original.get('source_sha256') == asset.source_sha256 and
                            re.fullmatch(r'[0-9a-f]{64}', str(extracted_original.get('sha256', ''))))
        native_pt = bool(has_original and (asset.coverage or {}).get('native_pt'))
        original_suffix = 'pdf' if source_format == 'pdf' else 'xml'
        original_media = 'application/pdf' if source_format == 'pdf' else 'application/xml'
        complete = bool(asset and asset.status == 'ready' and asset.translated_storage_key and asset.coverage.get('complete_text'))
        status = 'original_pt' if native_pt else 'available' if complete else ('blocked_license' if asset and asset.status == 'blocked_license' else 'pending' if asset and asset.status in ('pending', 'downloaded', 'translating', 'budget_wait') else 'unavailable')
        source.update({
            'original': {'read_url': base + '/original-text' if has_original and (source_format != 'pdf' or readable_pdf) else None, 'coverage': {**asset.coverage, 'complete_text': True} if has_original else {}, 'status': 'available' if has_original else 'source_only', 'url': base + '/original' if has_original else source['url'], 'media_type': original_media if has_original else None, 'filename': 'original-' + source['key'][:12] + '.' + original_suffix if has_original else None},
            'translation_pt': {'coverage': asset.coverage if asset else {}, 'status': status, 'url': base + '/translation' if complete else None, 'reason': 'O original já está em português; não é necessária tradução por IA.' if native_pt else asset.reason if asset else 'Tradução integral ainda não preparada para esta fonte.', 'media_type': 'text/plain; charset=utf-8', 'filename': 'traducao-' + source['key'][:12] + '.txt'},
            'summary_pt': {'status': 'available' if asset and asset.summary_pt else 'unavailable', 'text': asset.summary_pt if asset else None, 'origin': (asset.progress or {}).get('summary_origin', 'fulltext_ai') if asset else None},
            'license_url': asset.license_url if asset else None, 'coverage': asset.coverage if asset else {},
            'title': (asset.progress or {}).get('title') if asset else None, 'authors': (asset.progress or {}).get('authors', []) if asset else [], 'attribution': (asset.progress or {}).get('attribution') if asset else None,
            'provenance': {'source_sha256': asset.source_sha256 if asset else None, 'pmcid': asset.pmcid if asset else None, 'model': (asset.progress or {}).get('model') if asset else None},
        })
    summary = None if entity_type == 'descoberta' else editorial_summary(row)
    return {'entity_type': entity_type, 'slug': row.slug, 'summary_pt': {'status': 'available' if summary else 'unavailable', 'text': summary, 'origin': 'corvia_editorial'}, 'sources': sources}
