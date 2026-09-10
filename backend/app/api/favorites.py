from datetime import datetime, timezone
import hashlib
from types import SimpleNamespace
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import or_, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.security import current_user
from app.models.favorite import Favorite
from app.models.user import User
from app.services.favorite_catalog import ALIASES, FUNCTIONS, Resolver, VALID_TYPES, canonical_type

router = APIRouter(prefix='/api/favorites', tags=['favoritos'])
TIPOS_VALIDOS = VALID_TYPES

class NovoFavorito(BaseModel):
    model_config = ConfigDict(extra='forbid')
    item_type: str = Field(min_length=1,max_length=30)
    item_id: int | None = Field(default=None,gt=0,strict=True)
    item_slug: str | None = Field(default=None,min_length=1,max_length=500)

    @model_validator(mode='after')
    def validate_identity(self):
        if self.item_type not in VALID_TYPES: raise ValueError('Tipo de item inválido.')
        if self.item_slug is not None:
            self.item_slug = self.item_slug.strip()
            if not self.item_slug: raise ValueError('Slug inválido.')
        if self.item_id is None and self.item_slug is None: raise ValueError('Informe ID ou slug do conteúdo.')
        return self

def _existing(db,user,target):
    types = [target.item_type] + [alias for alias,canonical in ALIASES.items() if canonical == target.item_type]
    identity = []
    if target.equivalent_ids: identity.append(Favorite.item_id.in_(target.equivalent_ids))
    if target.equivalent_slugs: identity.append(Favorite.item_slug.in_(target.equivalent_slugs))
    if not identity: return None
    return db.query(Favorite).filter(Favorite.user_id==user.id,Favorite.item_type.in_(types),or_(*identity)).order_by(Favorite.id).first()

def _target(db,user,request):
    target = Resolver(db,user,[request]).resolve(request)
    if target is None: raise HTTPException(404,'Conteúdo indisponível ou sem permissão de acesso.')
    return target

@router.get('/types')
def supported_types(user:User=Depends(current_user)):
    return {'item_types':sorted(VALID_TYPES),'functions':[{'item_type':'funcao','item_slug':e['slug'],'title':e['title'],'url':e['path']} for e in FUNCTIONS.values()]}

@router.get('/status')
def status(item_type:str,item_id:int|None=Query(default=None,gt=0),item_slug:str|None=Query(default=None,min_length=1,max_length=500),db:Session=Depends(get_db),user:User=Depends(current_user)):
    try: request = NovoFavorito(item_type=item_type,item_id=item_id,item_slug=item_slug)
    except ValueError: raise HTTPException(422,'Identidade de favorito inválida.')
    target = Resolver(db,user,[request]).resolve(request)
    if target is None:
        return {'favorited':False,'favorite_id':None,'available':False,'item_type':canonical_type(item_type),'item_id':item_id,'item_slug':item_slug}
    existing = _existing(db,user,target)
    return {'favorited':bool(existing),'favorite_id':existing.id if existing else None,'available':True,
            'item_type':target.item_type,'item_id':target.item_id,'item_slug':target.item_slug}

@router.get('')
def listar(db:Session=Depends(get_db),user:User=Depends(current_user)):
    rows=db.query(Favorite).filter(Favorite.user_id==user.id).order_by(Favorite.created_at.desc(),Favorite.id.desc()).all()
    resolver=Resolver(db,user,rows)
    result=[]
    for favorite in rows:
        target=resolver.resolve(favorite)
        base={'id':favorite.id,'item_type':canonical_type(favorite.item_type),'item_id':favorite.item_id,'item_slug':favorite.item_slug}
        if target:
            base.update(target.public_metadata())
            base['item_slug']=target.item_slug
        else:
            base.update(title='Conteúdo indisponível',url=None,meta='',slug=None,reading=None,private_reading=None,
                        available=False,unavailable_reason='Este conteúdo foi removido, deixou de estar publicado ou requer acesso vigente.')
        result.append(base)
    return result

@router.post('',status_code=201)
def adicionar(dados:NovoFavorito,db:Session=Depends(get_db),user:User=Depends(current_user)):
    target=_target(db,user,dados)
    # Serialize all representations (ID, slug, aliases) of the same owned target.
    # Unique constraints remain the final boundary for old clients/concurrent inserts.
    identity=f'{user.id}:{target.item_type}:{target.item_slug}'
    key=int.from_bytes(hashlib.sha256(identity.encode()).digest()[:8],'big',signed=True)
    db.execute(text('SELECT pg_advisory_xact_lock(:key)'),{'key':key})
    existing=_existing(db,user,target)
    if existing:
        return {'id':existing.id,'ja_existia':True,'item_type':target.item_type,'item_id':target.item_id,'item_slug':target.item_slug}
    inserted=db.execute(insert(Favorite).values(user_id=user.id,item_type=target.item_type,item_id=target.item_id,
            item_slug=target.item_slug,created_at=datetime.now(timezone.utc)).on_conflict_do_nothing().returning(Favorite.id)).scalar()
    if inserted is None:
        existing=_existing(db,user,target)
        if existing is None:
            db.rollback();raise HTTPException(409,'Não foi possível concluir o favorito. Atualize e tente novamente.')
        inserted=existing.id
    db.commit()
    return {'id':inserted,'ja_existia':False,'item_type':target.item_type,'item_id':target.item_id,'item_slug':target.item_slug}

@router.delete('/by-id/{favorite_id}',status_code=204)
def remover_por_id(favorite_id:int,db:Session=Depends(get_db),user:User=Depends(current_user)):
    db.query(Favorite).filter(Favorite.id==favorite_id,Favorite.user_id==user.id).delete()
    db.commit()

@router.delete('/by-slug/{item_type}/{item_slug}',status_code=204)
def remover_por_slug(item_type:str,item_slug:str,db:Session=Depends(get_db),user:User=Depends(current_user)):
    request=SimpleNamespace(item_type=item_type,item_id=None,item_slug=item_slug)
    target=Resolver(db,user,[request]).resolve(request)
    types=[canonical_type(item_type)] + [alias for alias,canonical in ALIASES.items() if canonical==canonical_type(item_type)]
    filters=[Favorite.item_slug==item_slug]
    if target:
        if target.equivalent_ids: filters.append(Favorite.item_id.in_(target.equivalent_ids))
        if target.equivalent_slugs: filters.append(Favorite.item_slug.in_(target.equivalent_slugs))
    db.query(Favorite).filter(Favorite.user_id==user.id,Favorite.item_type.in_(types),or_(*filters)).delete(synchronize_session=False)
    db.commit()

@router.delete('/{item_type}/{item_id}',status_code=204)
def remover(item_type:str,item_id:int,db:Session=Depends(get_db),user:User=Depends(current_user)):
    # Legacy clients remove the exact owned numeric favorite, even after withdrawal.
    types=[canonical_type(item_type)] + [alias for alias,canonical in ALIASES.items() if canonical==canonical_type(item_type)]
    db.query(Favorite).filter(Favorite.user_id==user.id,Favorite.item_type.in_(types),Favorite.item_id==item_id).delete(synchronize_session=False)
    db.commit()
