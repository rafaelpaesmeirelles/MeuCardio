"""Contratos de progresso das trilhas: identidade, histórico e concorrência."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

from app.models.content import Document
from app.models.study_track import StudyTrack, StudyTrackProgress
from app.models.subscription import Subscription
from app.services.calculators import REGISTRY
from app.services.study_track_progress import (
    completed_stage_ids,
    expand_legacy_progress_tokens,
    stage_identity,
)


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _subscribe(db, user_id: int) -> None:
    db.add(Subscription(user_id=user_id, kind="meucardio", plano="basico", status="ativo"))
    db.commit()


def _calculator_slugs_without_documents(db, total: int) -> list[str]:
    slugs = [
        slug for slug in REGISTRY
        if db.query(Document.id).filter(Document.slug == slug).first() is None
    ]
    assert len(slugs) >= total
    return slugs[:total]


def _cleanup(db, track_slug: str, *document_slugs: str) -> None:
    db.query(StudyTrack).filter(StudyTrack.slug == track_slug).delete(
        synchronize_session=False
    )
    if document_slugs:
        db.query(Document).filter(Document.slug.in_(document_slugs)).delete(
            synchronize_session=False
        )
    db.commit()


def _track(track_slug: str, stages: list[dict]) -> StudyTrack:
    return StudyTrack(
        slug=track_slug,
        titulo="Trilha de teste de progresso",
        tema="Testes automatizados",
        objetivo="Validar o contrato de progresso.",
        nivel="intermediário",
        etapas=stages,
        review_status="revisado",
        published=True,
    )


def test_slug_legado_e_expandido_sem_perder_colisao_entre_tipos():
    stages = [
        {"item_type": "documento", "item_slug": "has-bled"},
        {"item_type": "calculadora", "item_slug": "has-bled"},
    ]

    expanded = expand_legacy_progress_tokens(["has-bled"], stages)

    assert expanded == ["calculadora:has-bled", "documento:has-bled"]
    assert completed_stage_ids(["has-bled"], stages) == set(expanded)


def test_documento_e_calculadora_com_mesmo_slug_progridem_separadamente(
    client, db, criar_usuario,
):
    track_slug = "trilha-teste-identidade-composta"
    calc_slug = _calculator_slugs_without_documents(db, 1)[0]
    _cleanup(db, track_slug, calc_slug)
    db.add(Document(
        slug=calc_slug,
        title="Documento com o mesmo slug da calculadora",
        kind="protocolo",
        theme="Testes automatizados",
        body_md="Conteúdo de teste.",
        review_status="revisado",
        published=True,
    ))
    db.add(_track(track_slug, [
        {"ordem": 1, "item_type": "documento", "item_slug": calc_slug, "por_que": "Ler."},
        {"ordem": 2, "item_type": "calculadora", "item_slug": calc_slug, "por_que": "Aplicar."},
    ]))
    db.commit()
    user, token = criar_usuario()
    _subscribe(db, user.id)
    headers = _headers(token)

    try:
        detail = client.get(f"/api/trilhas/{track_slug}", headers=headers)
        assert detail.status_code == 200, detail.text
        steps = detail.json()["etapas"]
        assert [step["etapa_id"] for step in steps] == [
            f"documento:{calc_slug}", f"calculadora:{calc_slug}",
        ]

        ambiguous = client.post(
            f"/api/trilhas/{track_slug}/progresso",
            headers=headers,
            json={"item_slug": calc_slug, "concluida": True},
        )
        assert ambiguous.status_code == 422
        assert "mais de uma etapa" in ambiguous.json()["detail"]

        marked = client.post(
            f"/api/trilhas/{track_slug}/progresso",
            headers=headers,
            json={
                "etapa_id": f"documento:{calc_slug}",
                "item_type": "documento",
                "item_slug": calc_slug,
                "concluida": True,
            },
        )
        assert marked.status_code == 200, marked.text
        body = marked.json()
        assert body["concluidas"] == 1
        assert body["concluida_atualmente"] is False
        by_type = {step["item_type"]: step for step in body["etapas"]}
        assert by_type["documento"]["concluida"] is True
        assert by_type["calculadora"]["concluida"] is False
    finally:
        _cleanup(db, track_slug, calc_slug)


def test_progresso_legado_e_convertido_na_primeira_escrita_e_timestamp_e_historico(
    client, db, criar_usuario,
):
    track_slug = "trilha-teste-progresso-legado"
    calc_slug = _calculator_slugs_without_documents(db, 1)[0]
    _cleanup(db, track_slug, calc_slug)
    db.add(Document(
        slug=calc_slug, title="Documento legado", kind="protocolo",
        theme="Testes automatizados", body_md="Conteúdo.",
        review_status="revisado", published=True,
    ))
    track = _track(track_slug, [
        {"ordem": 1, "item_type": "documento", "item_slug": calc_slug, "por_que": "Ler."},
        {"ordem": 2, "item_type": "calculadora", "item_slug": calc_slug, "por_que": "Aplicar."},
    ])
    db.add(track)
    db.commit()
    user, token = criar_usuario()
    _subscribe(db, user.id)
    progress = StudyTrackProgress(user_id=user.id, track_id=track.id, concluidas=[calc_slug])
    db.add(progress)
    db.commit()
    headers = _headers(token)

    try:
        legacy_detail = client.get(f"/api/trilhas/{track_slug}", headers=headers).json()
        assert legacy_detail["concluidas"] == 2
        assert all(step["concluida"] for step in legacy_detail["etapas"])

        unmarked = client.post(
            f"/api/trilhas/{track_slug}/progresso",
            headers=headers,
            json={
                "etapa_id": f"documento:{calc_slug}",
                "item_type": "documento",
                "item_slug": calc_slug,
                "concluida": False,
            },
        )
        assert unmarked.status_code == 200, unmarked.text
        assert unmarked.json()["concluidas"] == 1

        db.expire_all()
        stored = db.query(StudyTrackProgress).filter_by(user_id=user.id, track_id=track.id).one()
        assert stored.concluidas == [f"calculadora:{calc_slug}"]

        completed = client.post(
            f"/api/trilhas/{track_slug}/progresso",
            headers=headers,
            json={
                "etapa_id": f"documento:{calc_slug}",
                "item_type": "documento",
                "item_slug": calc_slug,
                "concluida": True,
            },
        )
        assert completed.status_code == 200, completed.text
        first_timestamp = completed.json()["conclusao_historica_em"]
        assert completed.json()["concluida_atualmente"] is True
        assert completed.json()["finalizada_em"] == first_timestamp
        assert first_timestamp is not None

        repeated = client.post(
            f"/api/trilhas/{track_slug}/progresso",
            headers=headers,
            json={
                "etapa_id": f"documento:{calc_slug}",
                "item_type": "documento",
                "item_slug": calc_slug,
                "concluida": True,
            },
        )
        assert repeated.status_code == 200
        assert repeated.json()["conclusao_historica_em"] == first_timestamp

        incomplete = client.post(
            f"/api/trilhas/{track_slug}/progresso",
            headers=headers,
            json={
                "etapa_id": f"documento:{calc_slug}",
                "item_type": "documento",
                "item_slug": calc_slug,
                "concluida": False,
            },
        ).json()
        assert incomplete["concluida_atualmente"] is False
        assert incomplete["finalizada_em"] is None
        assert incomplete["conclusao_historica_em"] == first_timestamp
    finally:
        _cleanup(db, track_slug, calc_slug)


def test_etapa_nao_publicada_nao_pode_ser_concluida(client, db, criar_usuario):
    track_slug = "trilha-teste-etapa-indisponivel"
    doc_slug = "documento-teste-etapa-indisponivel"
    _cleanup(db, track_slug, doc_slug)
    db.add(Document(
        slug=doc_slug, title="Documento ainda em revisão", kind="protocolo",
        theme="Testes automatizados", body_md="Conteúdo.",
        review_status="revisado", published=False,
    ))
    db.add(_track(track_slug, [
        {"ordem": 1, "item_type": "documento", "item_slug": doc_slug, "por_que": "Ler."},
    ]))
    db.commit()
    user, token = criar_usuario()
    _subscribe(db, user.id)

    try:
        response = client.post(
            f"/api/trilhas/{track_slug}/progresso",
            headers=_headers(token),
            json={"item_type": "documento", "item_slug": doc_slug, "concluida": True},
        )
        assert response.status_code == 409
        assert "não está publicada" in response.json()["detail"]
        assert db.query(StudyTrackProgress).filter_by(user_id=user.id).count() == 0
    finally:
        _cleanup(db, track_slug, doc_slug)


def test_trilha_publicada_sem_revisao_permanece_fechada(client, db, criar_usuario):
    track_slug = "trilha-teste-publicada-sem-revisao"
    _cleanup(db, track_slug)
    track = _track(track_slug, [])
    track.review_status = "pendente_revisao"
    db.add(track)
    db.commit()
    user, token = criar_usuario()
    _subscribe(db, user.id)
    headers = _headers(token)

    try:
        detail = client.get(f"/api/trilhas/{track_slug}", headers=headers)
        listing = client.get("/api/trilhas", headers=headers)

        assert detail.status_code == 404
        assert listing.status_code == 200
        assert track_slug not in {item["slug"] for item in listing.json()["items"]}
    finally:
        _cleanup(db, track_slug)


def test_edicao_editorial_muda_estado_atual_sem_apagar_primeira_conclusao(
    client, db, criar_usuario,
):
    track_slug = "trilha-teste-edicao-apos-conclusao"
    calc_a, calc_b = _calculator_slugs_without_documents(db, 2)
    _cleanup(db, track_slug)
    track = _track(track_slug, [
        {"ordem": 1, "item_type": "calculadora", "item_slug": calc_a, "por_que": "A."},
    ])
    db.add(track)
    db.commit()
    user, token = criar_usuario()
    _subscribe(db, user.id)
    headers = _headers(token)

    try:
        completed = client.post(
            f"/api/trilhas/{track_slug}/progresso",
            headers=headers,
            json={"item_type": "calculadora", "item_slug": calc_a, "concluida": True},
        )
        assert completed.status_code == 200, completed.text
        first_timestamp = completed.json()["conclusao_historica_em"]

        db.expire_all()
        stored_track = db.query(StudyTrack).filter_by(slug=track_slug).one()
        stored_track.etapas = [
            {"ordem": 1, "item_type": "calculadora", "item_slug": calc_a, "por_que": "A."},
            {"ordem": 2, "item_type": "calculadora", "item_slug": calc_b, "por_que": "B."},
        ]
        db.commit()

        reopened = client.get(f"/api/trilhas/{track_slug}", headers=headers).json()
        assert reopened["concluidas"] == 1
        assert reopened["total_etapas"] == 2
        assert reopened["concluida_atualmente"] is False
        assert reopened["finalizada_em"] is None
        assert reopened["conclusao_historica_em"] == first_timestamp

        db.expire_all()
        stored_track = db.query(StudyTrack).filter_by(slug=track_slug).one()
        stored_track.etapas = [
            {"ordem": 1, "item_type": "calculadora", "item_slug": calc_a, "por_que": "A."},
        ]
        db.commit()
        restored = client.get(f"/api/trilhas/{track_slug}", headers=headers).json()
        assert restored["concluida_atualmente"] is True
        assert restored["finalizada_em"] == first_timestamp
    finally:
        _cleanup(db, track_slug)


def test_duas_primeiras_gravacoes_concorrentes_preservam_as_duas_etapas(
    client, db, criar_usuario,
):
    track_slug = "trilha-teste-progresso-concorrente"
    calc_a, calc_b = _calculator_slugs_without_documents(db, 2)
    _cleanup(db, track_slug)
    db.add(_track(track_slug, [
        {"ordem": 1, "item_type": "calculadora", "item_slug": calc_a, "por_que": "A."},
        {"ordem": 2, "item_type": "calculadora", "item_slug": calc_b, "por_que": "B."},
    ]))
    db.commit()
    user, token = criar_usuario()
    _subscribe(db, user.id)
    headers = _headers(token)
    barrier = Barrier(2)

    def mark(calc_slug: str):
        barrier.wait(timeout=5)
        return client.post(
            f"/api/trilhas/{track_slug}/progresso",
            headers=headers,
            json={
                "etapa_id": stage_identity("calculadora", calc_slug),
                "item_type": "calculadora",
                "item_slug": calc_slug,
                "concluida": True,
            },
        )

    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            responses = list(executor.map(mark, (calc_a, calc_b)))
        assert [response.status_code for response in responses] == [200, 200]

        detail = client.get(f"/api/trilhas/{track_slug}", headers=headers)
        assert detail.status_code == 200
        assert detail.json()["concluidas"] == 2
        assert detail.json()["concluida_atualmente"] is True

        db.expire_all()
        progress = db.query(StudyTrackProgress).filter_by(
            user_id=user.id,
        ).one()
        assert progress.concluidas == sorted([
            stage_identity("calculadora", calc_a),
            stage_identity("calculadora", calc_b),
        ])
    finally:
        _cleanup(db, track_slug)
