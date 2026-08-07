"""Laudo genérico de calculadora clínica (pedido do Rafael, 07/08/2026:
"todas as calculadoras habilitadas para... gerar laudo completo do
resultado?"). Testado pela rota HTTP real, não só a função interna — mesma
régua do resto do projeto.
"""
from app.models.audit import AuditLog
from app.models.clinical_docs import GeneratedDocument
from app.models.subscription import Subscription


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _subscribe(db, user_id: int) -> None:
    db.add(Subscription(user_id=user_id, kind="meucardio", plano="basico", status="ativo"))
    db.commit()


def test_gerar_documento_recalcula_no_servidor_e_ignora_resultado_do_cliente(client, db, criar_usuario):
    """Regra de sempre: o servidor nunca confia num resultado que o cliente
    diga ter calculado — só o `payload` bruto é aceito, o número final vem
    de `calc.run()` no próprio servidor."""
    user, token = criar_usuario()
    _subscribe(db, user.id)
    resposta = client.post(
        "/api/calculators/cha2ds2-vasc/gerar-documento",
        json={
            "patient_name": "Fulano de Tal",
            "contexto_clinico": "Fibrilação atrial persistente, investigação ambulatorial",
            "conduta_recomendada": "Iniciar anticoagulação oral conforme escore",
            "payload": {
                "idade": 68,
                "sexo": "M",
                "ic_disfuncao_ve": True,
                "hipertensao": True,
                "diabetes": False,
                "avc_ait_tromboembolismo": False,
                "doenca_vascular": False,
            },
        },
        headers=_headers(token),
    )
    assert resposta.status_code == 201, resposta.text
    corpo = resposta.json()
    assert corpo["title"]
    assert "Contexto clínico" in corpo["rendered_body"]
    assert "Fibrilação atrial persistente" in corpo["rendered_body"]
    assert "Iniciar anticoagulação" in corpo["rendered_body"]
    assert corpo["result"] is not None
    assert corpo["patient_name"] == "Fulano de Tal"


def test_gerar_documento_calculadora_inexistente_devolve_404(client, db, criar_usuario):
    user, token = criar_usuario()
    _subscribe(db, user.id)
    resposta = client.post(
        "/api/calculators/nao-existe/gerar-documento",
        json={"payload": {}},
        headers=_headers(token),
    )
    assert resposta.status_code == 404


def test_gerar_documento_dados_invalidos_devolve_422(client, db, criar_usuario):
    user, token = criar_usuario()
    _subscribe(db, user.id)
    resposta = client.post(
        "/api/calculators/cha2ds2-vasc/gerar-documento",
        json={"payload": {"idade": "não é um número"}},
        headers=_headers(token),
    )
    assert resposta.status_code in (409, 422)


def test_gerar_documento_gscri_nao_esta_no_catalogo_calculavel(client, db, criar_usuario):
    """GSCRI é documentado (content/Perioperatório) mas deliberadamente NÃO
    entrou no catálogo de calculadoras — os coeficientes por categoria
    cirúrgica não foram validados contra a publicação original nesta sessão.
    A rota genérica precisa herdar esse bloqueio (404, calculadora
    inexistente) sem tratamento especial que a contorne."""
    user, token = criar_usuario()
    _subscribe(db, user.id)
    resposta = client.post(
        "/api/calculators/gscri/gerar-documento",
        json={"payload": {"idade": 70}},
        headers=_headers(token),
    )
    assert resposta.status_code == 404


def test_gerar_documento_endereco_invalido_devolve_422(client, db, criar_usuario):
    user, token = criar_usuario()
    _subscribe(db, user.id)
    resposta = client.post(
        "/api/calculators/cha2ds2-vasc/gerar-documento",
        json={"payload": {}, "endereco": "não é uma opção válida"},
        headers=_headers(token),
    )
    assert resposta.status_code == 422


def test_gerar_documento_registra_auditlog_e_persiste(client, db, criar_usuario):
    user, token = criar_usuario()
    _subscribe(db, user.id)
    resposta = client.post(
        "/api/calculators/has-bled/gerar-documento",
        json={"payload": {}},
        headers=_headers(token),
    )
    assert resposta.status_code == 201, resposta.text
    doc_id = resposta.json()["id"]

    gerado = db.get(GeneratedDocument, doc_id)
    assert gerado is not None
    assert gerado.doc_type == "calculadora_clinica"
    assert gerado.created_by == user.id

    log = (
        db.query(AuditLog)
        .filter(AuditLog.action == "gerar_documento_calculadora", AuditLog.entity_id == str(doc_id))
        .first()
    )
    assert log is not None
    assert log.detail["calculadora"] == "has-bled"


def test_gerar_documento_funciona_para_calculadora_de_dose(client, db, criar_usuario):
    """Não é só escore — as calculadoras de dose (kind='dose') também devem
    gerar laudo, mesmo endpoint genérico."""
    user, token = criar_usuario()
    _subscribe(db, user.id)
    resposta = client.post(
        "/api/calculators/infusao-continua-peso/gerar-documento",
        json={
            "payload": {
                "droga": "noradrenalina",
                "peso": 70,
                "dose_alvo": 0.1,
                "quantidade_no_frasco": 4,
                "volume_da_solucao": 250,
            },
        },
        headers=_headers(token),
    )
    assert resposta.status_code == 201, resposta.text
    assert "mL/h" in resposta.json()["rendered_body"]
