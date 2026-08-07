"""Avaliação Cardiológica Pré-Operatória de Risco Cirúrgico (pedido do
Rafael, 07/08/2026) — testado pela rota HTTP real, não só a função interna:
o endpoint reaproveita `GeneratedDocument` e as rotas já existentes de
`app/api/documents.py` para PDF/assinatura/e-mail, então o único
comportamento genuinamente novo aqui é a montagem do corpo a partir das
calculadoras (RCRI/Gupta MICA) recalculadas no servidor.
"""

from app.models.subscription import Subscription


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _subscribe(db, user_id: int) -> None:
    db.add(Subscription(user_id=user_id, kind="meucardio", plano="basico", status="ativo"))
    db.commit()


def test_gerar_documento_com_rcri_e_gupta(client, db, criar_usuario):
    user, token = criar_usuario()
    _subscribe(db, user.id)

    payload = {
        "patient_name": "Paciente de Teste",
        "idade": 72,
        "procedimento_planejado": "Colecistectomia videolaparoscópica eletiva",
        "indicacao_cirurgica": "Colelitíase sintomática",
        "capacidade_funcional": "Sobe 2 lances de escada sem dispneia (>4 METs)",
        "rcri": {
            "cirurgia_alto_risco": False,
            "cardiopatia_isquemica": True,
            "insuficiencia_cardiaca_congestiva": False,
            "doenca_cerebrovascular": False,
            "diabetes_em_uso_de_insulina": False,
            "creatinina_maior_2": False,
        },
        "gupta": {
            "idade": 72, "status_funcional": "independente", "asa": 2,
            "creatinina_maior_1_5": False, "tipo_procedimento": "vesicula_apendice_adrenal_baco",
        },
        "conduta_recomendada": "Manter betabloqueador em uso crônico; sem indicação de exame adicional.",
    }
    resposta = client.post("/api/avaliacao-preoperatoria/gerar", json=payload, headers=_headers(token))
    assert resposta.status_code == 201, resposta.text
    corpo = resposta.json()
    assert corpo["doc_type"] == "avaliacao_preoperatoria"
    assert corpo["patient_name"] == "Paciente de Teste"
    assert corpo["rcri"] == {"pontos": 1, "classe": "II", "evento_pct": "0,9"}
    assert corpo["gupta"]["procedimento"] == "Vesícula biliar, apêndice, adrenal ou baço"
    assert "RCRI" in corpo["rendered_body"]
    assert "Gupta MICA" in corpo["rendered_body"]
    assert corpo["medico"]["full_name"] == user.full_name

    # O documento gerado é um GeneratedDocument comum — as rotas já
    # existentes de PDF/listagem devem enxergá-lo sem nenhum código novo.
    gid = corpo["id"]
    listagem = client.get("/api/document-templates/gerados", headers=_headers(token))
    assert listagem.status_code == 200
    assert any(item["id"] == gid and item["doc_type"] == "avaliacao_preoperatoria" for item in listagem.json()["items"])

    pdf = client.get(f"/api/document-templates/gerados/{gid}/pdf", headers=_headers(token))
    assert pdf.status_code == 200
    assert pdf.content.startswith(b"%PDF-")


def test_gerar_exige_ao_menos_um_escore(client, db, criar_usuario):
    user, token = criar_usuario()
    _subscribe(db, user.id)
    resposta = client.post("/api/avaliacao-preoperatoria/gerar", json={
        "procedimento_planejado": "Herniorrafia inguinal",
    }, headers=_headers(token))
    assert resposta.status_code == 422


def test_gerar_recalcula_no_servidor_mesmo_se_cliente_mentir(client, db, criar_usuario):
    """Não existe campo para o cliente mandar um `resultado` pronto — o
    endpoint só aceita os campos brutos de entrada de cada calculadora e
    sempre recalcula. Este teste documenta essa garantia: o RCRI devolvido
    bate com o que os 6 booleanos realmente implicam, não com nenhum valor
    que o payload pudesse tentar embutir em outro campo."""
    user, token = criar_usuario()
    _subscribe(db, user.id)
    resposta = client.post("/api/avaliacao-preoperatoria/gerar", json={
        "procedimento_planejado": "Artroplastia de quadril",
        "rcri": {
            "cirurgia_alto_risco": True,
            "cardiopatia_isquemica": True,
            "insuficiencia_cardiaca_congestiva": True,
            "doenca_cerebrovascular": True,
            "diabetes_em_uso_de_insulina": True,
            "creatinina_maior_2": True,
        },
    }, headers=_headers(token))
    assert resposta.status_code == 201
    assert resposta.json()["rcri"] == {"pontos": 6, "classe": "IV", "evento_pct": "11,0"}
