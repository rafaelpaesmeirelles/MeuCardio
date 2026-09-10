from types import SimpleNamespace
import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import event
from app.api import favorites as api
from app.models.favorite import Favorite
from app.models.content import Document
from app.models.study import ScientificStudy
from app.models.study_track import StudyTrack
from app.models.scientific_user_document import ScientificUserDocument
from app.services.favorite_catalog import Resolver, FUNCTIONS, SPEC, TARGET_MODELS
from app.services.scientific_reading import published_query
from app.services.study_slug_aliases import STUDY_SLUG_ALIASES

def document(db,slug='favorite-test',published=True):
    row=Document(slug=slug,title='Título científico '+slug,kind='estudo',theme='Geral',summary='Resumo',body_md='Conteúdo',published=published)
    db.add(row);db.commit();return row

def test_new_payload_rejects_arbitrary_targets():
    for payload in [{}, {'item_type':'paciente','item_id':1}, {'item_type':'documento','item_id':True}, {'item_type':'documento','item_slug':' '}, {'item_type':'funcao','item_slug':'agenda','url':'https://evil.test'}]:
        with pytest.raises(ValidationError):api.NovoFavorito(**payload)
    assert 'cursos' not in FUNCTIONS and all(not e['path'].startswith('/admin') for e in FUNCTIONS.values())
    assert set(SPEC) <= set(TARGET_MODELS)

def test_existing_numeric_favorite_and_alias_slug_are_one_reference(db,criar_usuario):
    user,_=criar_usuario(role='admin');doc=document(db)
    old=Favorite(user_id=user.id,item_type='documento',item_id=doc.id);db.add(old);db.commit()
    result=api.adicionar(api.NovoFavorito(item_type='fluxograma',item_slug=doc.slug),db,user)
    assert result['id']==old.id and result['ja_existia']
    assert db.query(Favorite).filter_by(user_id=user.id).count()==1
    status=api.status('documento',item_id=doc.id,item_slug=None,db=db,user=user)
    assert status['favorited'] and status['favorite_id']==old.id
    row=api.listar(db,user)[0]
    assert row['reading']=={'entity_type':'documento','slug':doc.slug}

def test_conflicting_identifiers_and_unpublished_items_do_not_leak(db,criar_usuario):
    user,_=criar_usuario(role='admin');one=document(db,'favorite-one');two=document(db,'favorite-two')
    with pytest.raises(HTTPException):api.adicionar(api.NovoFavorito(item_type='documento',item_id=one.id,item_slug=two.slug),db,user)
    result=api.adicionar(api.NovoFavorito(item_type='documento',item_id=one.id),db,user)
    one.published=False;db.commit()
    with pytest.raises(HTTPException) as error:api.adicionar(api.NovoFavorito(item_type='documento',item_slug=one.slug),db,user)
    assert error.value.status_code==404
    row=api.listar(db,user)[0]
    assert row['title']=='Conteúdo indisponível' and row['url'] is None and row['reading'] is None
    assert 'favorite-one' not in str(row.get('title'))
    api.remover_por_id(result['id'],db,user)
    assert api.listar(db,user)==[]

def test_deleted_study_alias_resolves_published_canonical_without_duplicates(db,criar_usuario):
    user,_=criar_usuario(role='admin');alias,slug=next(iter(STUDY_SLUG_ALIASES.items()))
    study=ScientificStudy(slug=slug,title='Estudo canônico',study_type='ensaio_clinico',journal='Journal',year=2026,summary='Resumo',key_findings='Resultado',clinical_implications='Implicação',theme='Geral',published=True)
    db.add(study);db.commit()
    first=api.adicionar(api.NovoFavorito(item_type='estudo',item_slug=alias),db,user)
    second=api.adicionar(api.NovoFavorito(item_type='estudo',item_id=study.id),db,user)
    assert first['id']==second['id'] and second['ja_existia']
    assert api.listar(db,user)[0]['item_slug']==slug

def test_calculator_slug_and_functions_keep_capability_gates(db,criar_usuario,monkeypatch):
    user,_=criar_usuario(role='admin')
    from app.services.calculators import REGISTRY
    slug=next(iter(REGISTRY))
    first=api.adicionar(api.NovoFavorito(item_type='calculadora',item_slug=slug),db,user)
    second=api.adicionar(api.NovoFavorito(item_type='calculadora',item_slug=slug),db,user)
    assert first['id']==second['id'] and first['item_id'] is None
    api.adicionar(api.NovoFavorito(item_type='funcao',item_slug='agenda'),db,user)
    monkeypatch.setattr('app.services.favorite_catalog.settings.heart_team_enabled',False)
    with pytest.raises(HTTPException):api.adicionar(api.NovoFavorito(item_type='funcao',item_slug='heart-team'),db,user)
    with pytest.raises(HTTPException):api.adicionar(api.NovoFavorito(item_type='funcao',item_slug='https://evil.test'),db,user)
    api.remover_por_slug('calculadora',slug,db,user)
    assert all(row['item_type']!='calculadora' for row in api.listar(db,user))

def test_private_owner_checked_before_decryption_and_favorite_delete_is_scoped(db,criar_usuario,monkeypatch):
    owner,_=criar_usuario('owner@teste.local',role='admin');other,_=criar_usuario('other@teste.local',role='admin')
    row=ScientificUserDocument(owner_id=owner.id,storage_key='favorite-private',original_name_cifrado=b'original',display_title_cifrado=b'title',media_type='application/pdf',size_bytes=10,sha256='a'*64)
    db.add(row);db.commit()
    calls=[]
    monkeypatch.setattr('app.services.cofre.decifrar_campo',lambda value,id:calls.append(id) or 'Título privado do dono')
    with pytest.raises(HTTPException):api.adicionar(api.NovoFavorito(item_type='documento_cientifico_privado',item_id=row.id),db,other)
    assert calls==[]
    saved=api.adicionar(api.NovoFavorito(item_type='documento_cientifico_privado',item_id=row.id),db,owner)
    metadata=api.listar(db,owner)[0]
    assert metadata['private_reading']=={'document_id':row.id} and metadata['reading'] is None
    api.remover_por_id(saved['id'],db,other)
    assert db.get(Favorite,saved['id']) is not None
    malicious=Favorite(user_id=other.id,item_type='documento_cientifico_privado',item_id=row.id)
    db.add(malicious);db.commit();calls.clear()
    metadata=api.listar(db,other)[0]
    assert not metadata['available'] and calls==[]

def test_pending_track_is_not_favoritable_or_scientifically_readable(db,criar_usuario):
    user,_=criar_usuario(role='admin');track=StudyTrack(slug='favorite-pending-track',titulo='Trilha em revisão',published=True,review_status='pendente_revisao')
    db.add(track);db.commit()
    with pytest.raises(HTTPException):api.adicionar(api.NovoFavorito(item_type='trilha',item_slug=track.slug),db,user)
    assert published_query(db,StudyTrack).filter_by(id=track.id).first() is None

def test_list_uses_batched_metadata_queries_not_one_select_per_favorite(db,criar_usuario):
    user,_=criar_usuario(role='admin')
    for index in range(12):
        doc=document(db,'favorite-batch-'+str(index));db.add(Favorite(user_id=user.id,item_type='documento',item_id=doc.id))
    db.commit();user_id=user.id;statements=[]
    def record(conn,cursor,statement,parameters,context,executemany):
        if statement.lstrip().upper().startswith('SELECT'):statements.append(statement)
    event.listen(db.bind,'before_cursor_execute',record)
    try:rows=api.listar(db,user)
    finally:event.remove(db.bind,'before_cursor_execute',record)
    assert len(rows)==12 and len(statements)<=3
    assert not any('documents.body_md' in sql for sql in statements)
