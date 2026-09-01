"""A resposta do caso clínico só pode ser revelada depois da tentativa."""

from app.models.clinical_case import ClinicalCase, ClinicalCaseAttempt
from app.models.subscription import Subscription


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_get_nao_vaza_gabarito_e_post_revela_correcao(client, db, criar_usuario):
    slug = "caso-teste-gabarito-nao-vaza"
    db.query(ClinicalCase).filter(ClinicalCase.slug == slug).delete(synchronize_session=False)
    db.commit()
    case = ClinicalCase(
        slug=slug,
        titulo="Caso de teste sem vazamento de gabarito",
        tema="Testes automatizados",
        nivel="intermediário",
        enunciado="Vinheta clínica de teste.",
        pergunta="Qual é a alternativa correta?",
        opcoes=["Alternativa incorreta", "Alternativa correta"],
        resposta_correta=1,
        explicacao="A segunda alternativa é a correta segundo a fonte de teste.",
        source_refs=["Fonte de teste"],
        review_status="revisado",
        published=True,
    )
    db.add(case)
    db.commit()
    user, token = criar_usuario()
    db.add(Subscription(user_id=user.id, kind="meucardio", plano="basico", status="ativo"))
    db.commit()
    headers = _headers(token)

    try:
        initial = client.get(f"/api/casos-clinicos/{slug}", headers=headers)
        assert initial.status_code == 200, initial.text
        assert "resposta_correta" not in initial.json()
        assert "explicacao" not in initial.json()

        answer = client.post(
            f"/api/casos-clinicos/{slug}/responder",
            headers=headers,
            json={"opcao_escolhida": 0},
        )
        assert answer.status_code == 200, answer.text
        assert answer.json() == {
            "acertou": False,
            "resposta_correta": 1,
            "explicacao": "A segunda alternativa é a correta segundo a fonte de teste.",
        }

        # Mesmo depois de uma tentativa, um novo GET pode iniciar uma repetição
        # do caso e não deve entregar o gabarito no payload inicial.
        repeated = client.get(f"/api/casos-clinicos/{slug}", headers=headers)
        assert "resposta_correta" not in repeated.json()
        assert "explicacao" not in repeated.json()
        assert repeated.json()["tentativas"] == 1
    finally:
        db.query(ClinicalCaseAttempt).filter(ClinicalCaseAttempt.case_id == case.id).delete(
            synchronize_session=False
        )
        db.query(ClinicalCase).filter(ClinicalCase.slug == slug).delete(
            synchronize_session=False
        )
        db.commit()
