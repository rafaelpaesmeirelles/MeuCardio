"""Trilhas de estudo: o título de cada etapa é o do item real, não o slug.

Achado em 07/08/2026 (varredura geral pedida pelo Rafael): a tela de detalhe da
trilha mostrava, para cada etapa, `item_slug.replace("-", " ")` — string sem
acento e com toda palavra maiúscula, tipo "Aneurisma De Aorta Toracica Cortes
Por Etiologia E Seguimento Esc 2024". O backend nunca calculava título nenhum;
`_titulo()` em `app/api/study_tracks.py` fecha essa lacuna buscando o campo
certo na tabela do item (`Document.title`, `ScientificStudy.title`, etc.).
"""

from app.models.content import Document
from app.models.study import ScientificStudy
from app.models.study_track import StudyTrack
from app.models.subscription import Subscription


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _subscribe(db, user_id: int) -> None:
    db.add(Subscription(user_id=user_id, kind="meucardio", plano="basico", status="ativo"))
    db.commit()


def _limpar(db, *slugs: str) -> None:
    db.query(StudyTrack).filter(StudyTrack.slug.in_(slugs)).delete(synchronize_session=False)
    db.query(Document).filter(Document.slug.in_(slugs)).delete(synchronize_session=False)
    db.query(ScientificStudy).filter(ScientificStudy.slug.in_(slugs)).delete(synchronize_session=False)
    db.commit()


def test_etapa_mostra_titulo_real_do_documento_e_do_estudo(client, db, criar_usuario):
    track_slug = "trilha-teste-titulo-de-etapa"
    doc_slug = "documento-teste-titulo-de-etapa"
    estudo_slug = "estudo-teste-titulo-de-etapa"
    _limpar(db, track_slug, doc_slug, estudo_slug)

    db.add(Document(
        slug=doc_slug, title="Aneurisma de aorta torácica: cortes por etiologia e seguimento (ESC 2024)",
        kind="protocolo", theme="Aorta e doença arterial periférica", body_md="Corpo de teste.",
        review_status="revisado", published=True,
    ))
    db.add(ScientificStudy(
        slug=estudo_slug, title="EVAR-1: quinze anos, endovascular versus aberto no aneurisma de aorta abdominal",
        study_type="ensaio_clinico", journal="Lancet", year=2016, theme="Aorta e doença arterial periférica",
        summary="Resumo de teste.", key_findings="Achados de teste.", clinical_implications="Implicação de teste.",
        review_status="revisado", published=True,
    ))
    db.add(StudyTrack(
        slug=track_slug, titulo="Trilha de teste — título de etapa", tema="Aorta e doença arterial periférica",
        objetivo="Confirmar que a etapa mostra o título real do item.", nivel="intermediario",
        review_status="revisado", revisao="Teste automatizado", published=True,
        etapas=[
            {"ordem": 1, "item_type": "documento", "item_slug": doc_slug,
             "por_que": "Etapa de teste."},
            {"ordem": 2, "item_type": "estudo", "item_slug": estudo_slug,
             "por_que": "Etapa de teste."},
        ],
    ))
    db.commit()

    user, token = criar_usuario()
    _subscribe(db, user.id)

    resposta = client.get(f"/api/trilhas/{track_slug}", headers=_headers(token))
    assert resposta.status_code == 200
    etapas = resposta.json()["etapas"]

    assert etapas[0]["titulo"] == "Aneurisma de aorta torácica: cortes por etiologia e seguimento (ESC 2024)"
    assert etapas[1]["titulo"] == "EVAR-1: quinze anos, endovascular versus aberto no aneurisma de aorta abdominal"
    # A garantia que importa ao assinante: nada de slug cru vazando como título.
    assert doc_slug not in etapas[0]["titulo"]
    assert estudo_slug not in etapas[1]["titulo"]

    _limpar(db, track_slug, doc_slug, estudo_slug)


def test_etapa_indisponivel_sem_titulo_cai_no_slug_como_ultimo_recurso(client, db, criar_usuario):
    """Etapa cujo item não existe (slug digitado errado, por exemplo) não tem
    título nenhum para buscar — `titulo` vem `None`, e é o frontend que decide
    a exibição de fallback. Aqui confirmamos só o contrato do backend."""
    track_slug = "trilha-teste-etapa-sem-item"
    _limpar(db, track_slug)

    db.add(StudyTrack(
        slug=track_slug, titulo="Trilha de teste — etapa sem item", tema="Geral",
        objetivo="Confirmar o contrato quando o item não existe.", nivel="intermediario",
        review_status="revisado", revisao="Teste automatizado", published=True,
        etapas=[{"ordem": 1, "item_type": "documento", "item_slug": "slug-que-nao-existe-no-banco",
                 "por_que": "Etapa de teste."}],
    ))
    db.commit()

    user, token = criar_usuario()
    _subscribe(db, user.id)

    resposta = client.get(f"/api/trilhas/{track_slug}", headers=_headers(token))
    assert resposta.status_code == 200
    etapa = resposta.json()["etapas"][0]
    assert etapa["titulo"] is None
    assert etapa["disponivel"] is False

    _limpar(db, track_slug)
