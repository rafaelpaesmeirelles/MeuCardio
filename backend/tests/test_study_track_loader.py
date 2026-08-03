import json

from app.models.evidence import EvidenceRecord
from app.models.study_track import StudyTrack
from app.services.carregar_trilhas import _existe, carregar


def _limpar_registros(db, track_slug: str, evidence_slug: str) -> None:
    db.query(StudyTrack).filter(StudyTrack.slug == track_slug).delete(
        synchronize_session=False
    )
    db.query(EvidenceRecord).filter(EvidenceRecord.slug == evidence_slug).delete(
        synchronize_session=False
    )
    db.commit()


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
