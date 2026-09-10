"""Canonical favorite targets. Resolves metadata in batches without copying content.

Unknown, deleted, unpublished, private or gated targets do not expose metadata.
Saving a reference does not grant access or generate scientific/AI artifacts.
"""
from dataclasses import dataclass, field
import json
from pathlib import Path
from urllib.parse import quote
from sqlalchemy import or_
from sqlalchemy.orm import load_only
from app.core.config import settings
from app.models.content import Document
from app.models.study import ScientificStudy
from app.models.guideline import Guideline
from app.models.study_track import StudyTrack
from app.models.scientific_user_document import ScientificUserDocument
from app.models.scientific_publication_asset import ScientificPublicationAsset
from app.services.scientific_reading import MODELS, VISIBLE_GUIDELINES
from app.services.study_slug_aliases import STUDY_SLUG_ALIASES, canonical_study_slug
from app.services.guideline_source_trust import is_trusted_official_guideline
from app.services.commercial_plans import resolve_entitlements

ALIASES = {'fluxograma': 'documento', 'fluxo': 'documento', 'protocolo': 'documento'}
TARGET_MODELS = {**MODELS, 'descoberta': Guideline, 'documento_cientifico_privado': ScientificUserDocument, 'publicacao_original': ScientificPublicationAsset}
TARGET_MODELS.pop('fluxograma', None)
FUNCTIONS = {entry['slug']: entry for entry in json.loads((Path(__file__).parents[1] / 'data/favorite_functions.json').read_text())['entries']}
VALID_TYPES = frozenset(TARGET_MODELS) | {'calculadora', 'funcao'} | set(ALIASES)
AI_FUNCTIONS = frozenset({'assistente', 'heart-team', 'whatsapp-assistant', 'exames-ia', 'documentos-cientificos-ia'})

SPEC = {
    'documento': ('title', 'theme', '/biblioteca/'),
    'medicamento': ('generic_name', 'drug_class', '/medicamentos?slug='),
    'imagem': ('title', 'modality', '/galeria/'),
    'exame': ('name', 'category', '/exames/'),
    'evidencia': ('statement', 'recommendation_class', '/evidencias/'),
    'estudo': ('title', 'year', '/estudos/'),
    'doenca': ('name', 'area', '/doencas/'),
    'triagem': ('name', None, '/triagem-sintomas?slug='),
    'caso_clinico': ('titulo', 'tema', '/casos-clinicos/'),
    'trilha': ('titulo', 'tema', '/trilhas/'),
    'emergencia': ('titulo', None, '/emergencia?slug='),
    'material_paciente': ('titulo', 'tema', '/material-paciente/'),
    'checklist': ('condicao', 'theme', '/checklists/'),
    'diretriz': ('titulo', 'org', '/diretrizes?publicacao='),
    'descoberta': ('titulo', 'org', '/intelligence?publicacao='),
}

@dataclass
class Target:
    item_type: str
    item_id: int | None
    item_slug: str
    title: str
    url: str
    meta: str = ''
    reading: dict | None = None
    private_reading: dict | None = None
    equivalent_ids: set = field(default_factory=set)
    equivalent_slugs: set = field(default_factory=set)

    def public_metadata(self):
        return {'title': self.title, 'url': self.url, 'meta': self.meta, 'slug': self.item_slug,
                'reading': self.reading, 'private_reading': self.private_reading, 'available': True,
                'unavailable_reason': None}

def canonical_type(kind):
    return ALIASES.get(kind, kind)

class Resolver:
    """One metadata query per model plus a bounded canonical-study lookup."""
    def __init__(self, db, user, requests):
        self.db, self.user = db, user
        self.rows_by_id, self.rows_by_slug = {}, {}
        self._entitlements = None
        wanted = {}
        for request in requests:
            kind = canonical_type(request.item_type)
            model = TARGET_MODELS.get(kind)
            if model is None: continue
            ids, slugs = wanted.setdefault(model, (set(), set()))
            if request.item_id is not None: ids.add(request.item_id)
            slug = getattr(request, 'item_slug', None)
            if slug:
                if model is ScientificUserDocument:
                    if slug.isdigit(): ids.add(int(slug))
                else: slugs.add(slug)
        for model, (ids, slugs) in wanted.items():
            if model is ScientificStudy:
                slugs.update(canonical_study_slug(value) for value in tuple(slugs))
                slugs.update(STUDY_SLUG_ALIASES)
            selectors = [model.id.in_(ids)]
            if model is ScientificPublicationAsset: selectors.append(model.source_key.in_(slugs))
            elif hasattr(model, 'slug'): selectors.append(model.slug.in_(slugs))
            if model is ScientificPublicationAsset:
                from app.services.scientific_publication_catalog import public_asset_query
                query = public_asset_query(db).filter(or_(*selectors))
            else: query = db.query(model).filter(or_(*selectors))
            if model is ScientificUserDocument: query = query.filter(model.owner_id == user.id)
            names = {'id','slug','published','review_status','detection_status','doi','url','org','titulo','name','title','theme','tema','generic_name','drug_class','modality','category','statement','recommendation_class','year','area','condicao','owner_id','display_title_cifrado','original_name_cifrado','source_key','source_url','progress'}
            columns = [getattr(model,n) for n in names if hasattr(model,n)]
            for row in query.options(load_only(*columns)).all(): self._cache(model,row)
        # Restore published canonical destinations for favorites that predate
        # removal of duplicate scientific studies; never return a withdrawn title.
        if ScientificStudy in wanted:
            missing = {canonical_study_slug(row.slug) for (model,_),row in self.rows_by_id.items()
                       if model is ScientificStudy and canonical_study_slug(row.slug) != row.slug}
            if missing:
                for row in db.query(ScientificStudy).filter(ScientificStudy.slug.in_(missing)).options(load_only(ScientificStudy.id,ScientificStudy.slug,ScientificStudy.published,ScientificStudy.title,ScientificStudy.year)).all(): self._cache(ScientificStudy,row)

    def _cache(self,model,row):
        self.rows_by_id[(model,row.id)] = row
        if model is ScientificPublicationAsset: self.rows_by_slug[(model,row.source_key)] = row
        elif hasattr(row,'slug'): self.rows_by_slug[(model,row.slug)] = row

    def entitlements(self):
        if self._entitlements is None: self._entitlements = resolve_entitlements(self.db,self.user)
        return self._entitlements

    def _canonical_row(self,model,row):
        if row is not None and model is ScientificStudy:
            canonical = canonical_study_slug(row.slug)
            if canonical != row.slug: return self.rows_by_slug.get((model,canonical))
        return row

    def resolve(self, request):
        kind = canonical_type(request.item_type)
        slug = getattr(request,'item_slug',None)
        item_id = request.item_id
        if kind == 'funcao':
            entry = FUNCTIONS.get(slug or '')
            if entry is None or item_id is not None: return None
            features = self.entitlements()
            if kind == 'funcao' and slug in AI_FUNCTIONS and not features.get('ai'): return None
            if slug == 'corvia-mail' and not features.get('mail'): return None
            if entry.get('gate') == 'heart-team' and not settings.heart_team_enabled: return None
            if entry.get('gate') == 'whatsapp' and not settings.whatsapp_assistant_enabled: return None
            if entry.get('gate') in ('admin','admin-ai'): return None
            return Target(kind,None,slug,entry['title'],entry['path'],entry['group'],equivalent_slugs={slug})
        if kind == 'calculadora':
            from app.services.calculators import REGISTRY
            row = REGISTRY.get(slug or '')
            if row is None or item_id is not None: return None
            return Target(kind,None,row.slug,row.name,'/calculadoras/'+quote(row.slug,safe=''),row.theme,
                          reading={'entity_type':kind,'slug':row.slug},equivalent_slugs={row.slug})
        model = TARGET_MODELS.get(kind)
        if model is None: return None
        by_id = self._canonical_row(model,self.rows_by_id.get((model,item_id))) if item_id is not None else None
        if model is ScientificUserDocument:
            by_slug = self.rows_by_id.get((model,int(slug))) if slug and slug.isdigit() else None
        else: by_slug = self._canonical_row(model,self.rows_by_slug.get((model,canonical_study_slug(slug) if model is ScientificStudy and slug else slug))) if slug else None
        if item_id is not None and by_id is None: return None
        if slug and by_slug is None: return None
        if by_id is not None and by_slug is not None and by_id.id != by_slug.id: return None
        row = by_id if by_id is not None else by_slug
        if row is None: return None
        if model is ScientificPublicationAsset:
            return Target(kind,row.id,row.source_key,str((row.progress or {}).get('title') or row.doi),
                          '/intelligence?fonte='+quote(row.source_key,safe=''),str(row.doi),
                          reading={'entity_type':kind,'slug':row.source_key},equivalent_ids={row.id},equivalent_slugs={row.source_key})
        if model is ScientificUserDocument:
            if row.owner_id != self.user.id or not self.entitlements().get('ai'): return None
            from app.services import cofre
            try: title = cofre.decifrar_campo(row.display_title_cifrado or row.original_name_cifrado,row.id)
            except (cofre.CofreIndisponivel,ValueError): return None
            return Target(kind,row.id,str(row.id),title,'/documentos-cientificos-ia?document='+str(row.id),'Biblioteca privada',
                          private_reading={'document_id':row.id},equivalent_ids={row.id},equivalent_slugs={str(row.id)})
        if model is Guideline:
            if kind == 'descoberta':
                if not row.doi or not is_trusted_official_guideline(row): return None
            elif row.detection_status not in VISIBLE_GUIDELINES: return None
        elif not row.published: return None
        if model is StudyTrack and row.review_status != 'revisado': return None
        title_attr,meta_attr,path = SPEC[kind]
        title = str(getattr(row,title_attr))
        meta = str(getattr(row,meta_attr) or '') if meta_attr else ''
        if kind == 'evidencia':
            meta = ('Classe ' if row.recommendation_class in ('I','IIa','IIb','III') else 'Força ') + row.recommendation_class
        ids, slugs = {row.id}, {row.slug}
        if model is ScientificStudy:
            slugs.update(alias for alias,canonical in STUDY_SLUG_ALIASES.items() if canonical == row.slug)
            ids.update(alias.id for (m,_),alias in self.rows_by_id.items() if m is ScientificStudy and alias.slug in slugs)
        return Target(kind,row.id,row.slug,title,path+quote(row.slug,safe=''),meta,
                      reading={'entity_type':kind,'slug':row.slug},equivalent_ids=ids,equivalent_slugs=slugs)
