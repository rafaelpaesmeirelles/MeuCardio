import json

from app.models.clinical_case import ClinicalCase
from app.models.evidence import EvidenceRecord
from app.models.study_track import StudyTrack
from app.models.subscription import Subscription
from app.services.carregar_trilhas import _existe, carregar


def _subscribe(db, user_id: int) -> None:
    db.add(Subscription(user_id=user_id, kind="meucardio", plano="basico", status="ativo"))
    db.commit()


def _limpar_registros(db, track_slug: str, evidence_slug: str) -> None:
    db.query(StudyTrack).filter(StudyTrack.slug == track_slug).delete(
        synchronize_session=False
    )
    db.query(EvidenceRecord).filter(EvidenceRecord.slug == evidence_slug).delete(
        synchronize_session=False
    )
    db.commit()


def test_carregador_valida_slug_real_de_calculadora(db):
    from app.services.calculators import REGISTRY

    slug_real = next(iter(REGISTRY))
    assert _existe(db, "calculadora", slug_real) is True
    assert _existe(db, "calculadora", "calculadora-que-nao-existe") is False


def test_carregador_aceita_evidencia_existente_na_trilha(db, tmp_path):
    track_slug = "trilha-teste-referencia-evidencia"
    evidence_slug = "evidencia-teste-referencia-trilha"
    _limpar_registros(db, track_slug, evidence_slug)

    evidencia = EvidenceRecord(
        slug=evidence_slug,
        statement="Recomendação de teste para validar o vínculo da trilha.",
        recommendation_class="I",
        evidence_level="A",
        society="SBC",
        year=2026,
        guideline_title="Diretriz de teste",
        reference="Referência de teste",
        theme="Testes automatizados",
        tags=["teste"],
        review_status="revisado",
        published=True,
    )
    db.add(evidencia)
    db.commit()

    manifesto = [{
        "slug": track_slug,
        "titulo": "Trilha de teste",
        "tema": "Testes automatizados",
        "objetivo": "Confirmar que evidências válidas não são recusadas.",
        "nivel": "intermediario",
        "review_status": "revisado",
        "revisao": "Teste automatizado",
        "etapas": [{
            "ordem": 1,
            "item_type": "evidencia",
            "item_slug": evidence_slug,
            "por_que": "A recomendação fundamenta a etapa clínica.",
        }],
    }]
    caminho = tmp_path / "trilhas.json"
    caminho.write_text(json.dumps(manifesto, ensure_ascii=False), encoding="utf-8")

    try:
        assert _existe(db, "evidencia", evidence_slug) is True
        assert _existe(db, "evidencia", "evidencia-que-nao-existe") is False

        resultado = carregar(str(caminho))
        assert resultado == {"novos": 1, "atualizados": 0}

        db.expire_all()
        trilha = db.query(StudyTrack).filter(StudyTrack.slug == track_slug).one()
        assert trilha.etapas[0]["item_type"] == "evidencia"
        assert trilha.etapas[0]["item_slug"] == evidence_slug
    finally:
        _limpar_registros(db, track_slug, evidence_slug)


def test_carregador_aceita_caso_clinico_existente_na_trilha(db, tmp_path):
    """Regressão: `_existe()` nunca reconheceu `item_type == "caso_clinico"`
    e recusava a trilha inteira (achado em 07/08/2026, publicando 3 trilhas
    novas que tinham etapa de caso clínico — todas rejeitadas em silêncio
    até este fix)."""
    track_slug = "trilha-teste-referencia-caso-clinico"
    caso_slug = "caso-clinico-teste-referencia-trilha"
    db.query(StudyTrack).filter(StudyTrack.slug == track_slug).delete(synchronize_session=False)
    db.query(ClinicalCase).filter(ClinicalCase.slug == caso_slug).delete(synchronize_session=False)
    db.commit()

    caso = ClinicalCase(
        slug=caso_slug, tema="Testes automatizados", titulo="Caso de teste",
        enunciado="Vinheta de teste.", pergunta="Pergunta de teste?",
        opcoes=["A", "B"], resposta_correta=0, explicacao="Explicação de teste.",
        source_refs=["Referência de teste"], review_status="revisado", published=True,
    )
    db.add(caso)
    db.commit()

    manifesto = [{
        "slug": track_slug,
        "titulo": "Trilha de teste",
        "tema": "Testes automatizados",
        "objetivo": "Confirmar que caso clínico válido não é recusado.",
        "nivel": "intermediario",
        "review_status": "revisado",
        "revisao": "Teste automatizado",
        "etapas": [{
            "ordem": 1,
            "item_type": "caso_clinico",
            "item_slug": caso_slug,
            "por_que": "O caso aplica a decisão clínica da etapa.",
        }],
    }]
    caminho = tmp_path / "trilhas.json"
    caminho.write_text(json.dumps(manifesto, ensure_ascii=False), encoding="utf-8")

    try:
        assert _existe(db, "caso_clinico", caso_slug) is True
        assert _existe(db, "caso_clinico", "caso-que-nao-existe") is False

        resultado = carregar(str(caminho))
        assert resultado == {"novos": 1, "atualizados": 0}

        db.expire_all()
        trilha = db.query(StudyTrack).filter(StudyTrack.slug == track_slug).one()
        assert trilha.etapas[0]["item_type"] == "caso_clinico"
        assert trilha.etapas[0]["item_slug"] == caso_slug
    finally:
        db.query(StudyTrack).filter(StudyTrack.slug == track_slug).delete(synchronize_session=False)
        db.query(ClinicalCase).filter(ClinicalCase.slug == caso_slug).delete(synchronize_session=False)
        db.commit()


def test_api_trilha_resolve_link_e_disponibilidade_de_evidencia_e_caso_clinico(client, db, criar_usuario):
    """Regressão irmã da acima, na camada da API (achado no mesmo lote,
    07/08/2026): `ROTA` e `_disponivel()` em `app/api/study_tracks.py`
    nunca reconheciam "evidencia"/"caso_clinico" — a etapa virava um link
    vazio (`ROTA.get(tipo, "")` sem entrada) e `disponivel=True` mesmo se o
    item de baixo não existisse ou não estivesse publicado (caía no ramo
    "Modelo is None -> True", pensado só para calculadora)."""
    from app.models.clinical_case import ClinicalCase
    from app.models.evidence import EvidenceRecord
    from app.models.study_track import StudyTrack

    user, token = criar_usuario()
    _subscribe(db, user.id)
    track_slug = "trilha-teste-api-evidencia-caso-clinico"
    evidence_slug = "evidencia-teste-api-trilha"
    caso_slug = "caso-clinico-teste-api-trilha"
    for M, s in ((StudyTrack, track_slug), (EvidenceRecord, evidence_slug), (ClinicalCase, caso_slug)):
        db.query(M).filter(M.slug == s).delete(synchronize_session=False)
    db.commit()

    db.add(EvidenceRecord(
        slug=evidence_slug, statement="Recomendação de teste.",
        recommendation_class="I", evidence_level="A", society="SBC", year=2026,
        guideline_title="Diretriz de teste", reference="Referência de teste",
        theme="Testes automatizados", tags=["teste"],
        review_status="revisado", published=True,
    ))
    # Caso clínico deliberadamente NÃO publicado, para provar que
    # `_disponivel()` agora distingue "existe" de "está no ar".
    db.add(ClinicalCase(
        slug=caso_slug, tema="Testes automatizados", titulo="Caso de teste",
        enunciado="Vinheta.", pergunta="Pergunta?", opcoes=["A", "B"],
        resposta_correta=0, explicacao="Explicação.", source_refs=["Ref"],
        review_status="revisado", published=False,
    ))
    db.add(StudyTrack(
        slug=track_slug, titulo="Trilha de teste", tema="Testes automatizados",
        objetivo="Testar evidencia/caso_clinico na API.", nivel="intermediario",
        review_status="revisado", published=True,
        etapas=[
            {"ordem": 1, "item_type": "evidencia", "item_slug": evidence_slug, "por_que": "x"},
            {"ordem": 2, "item_type": "caso_clinico", "item_slug": caso_slug, "por_que": "y"},
        ],
    ))
    db.commit()

    try:
        r = client.get(f"/api/trilhas/{track_slug}", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200, r.text
        corpo = r.json()
        etapas = {e["item_type"]: e for e in corpo["etapas"]}

        assert etapas["evidencia"]["link"] == f"/evidencias/{evidence_slug}"
        assert etapas["evidencia"]["disponivel"] is True

        assert etapas["caso_clinico"]["link"] == f"/casos-clinicos/{caso_slug}"
        assert etapas["caso_clinico"]["disponivel"] is False  # não publicado

        assert corpo["etapas_indisponiveis"] == 1
    finally:
        for M, s in ((StudyTrack, track_slug), (EvidenceRecord, evidence_slug), (ClinicalCase, caso_slug)):
            db.query(M).filter(M.slug == s).delete(synchronize_session=False)
        db.commit()
