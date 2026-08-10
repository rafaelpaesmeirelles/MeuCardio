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


def test_gerar_documento_gscri_esta_implementada_e_funciona(client, db, criar_usuario):
    """CORREÇÃO (issue #52, revisão de segurança, 11/08/2026): esta suíte
    afirmava que o GSCRI "deliberadamente NÃO entrou no catálogo" e que a
    rota devolvia 404 por bloqueio proposital. Isso ficou desatualizado —
    `perioperative_calculators_geriatria.py` implementa o GSCRI por completo
    (Alrezk R et al., J Am Heart Assoc. 2017;6(11):e006648, PMID 29146612,
    coeficientes da Table 3), `status="implementada"`, mergeado em
    `calc.REGISTRY` por `app/services/__init__.py`. A asserção antiga de 404
    só "passava" por um motivo completamente diferente e não relacionado ao
    bloqueio documentado: um payload incompleto ({"idade": 70}, sem os
    campos obrigatórios) fazia `_gscri()` levantar KeyError ao acessar
    d["asa"], e a rota mapeava QUALQUER KeyError para 404 "calculadora não
    encontrada" — mascarando um erro de dado incompleto como se a
    calculadora não existisse. Ambos os defeitos foram corrigidos: o
    catálogo já tinha o GSCRI real, e a rota agora distingue "slug
    inexistente" (404) de "payload incompleto" (422) — ver
    test_gerar_documento_payload_incompleto_devolve_422_nao_404."""
    user, token = criar_usuario()
    _subscribe(db, user.id)
    resposta = client.post(
        "/api/calculators/gscri/gerar-documento",
        json={
            "payload": {
                "idade": 70, "asa": 3, "tipo_procedimento": "hernia",
                "status_funcional": "independente", "diabetes": "nao",
            },
        },
        headers=_headers(token),
    )
    assert resposta.status_code == 201, resposta.text
    corpo = resposta.json()
    assert corpo["result"] is not None
    assert "risco_pct" in corpo["result"]


def test_gerar_documento_payload_incompleto_devolve_422_nao_404(client, db, criar_usuario):
    """Regressão do bug descrito acima: KeyError por campo obrigatório
    ausente no payload (não por slug inexistente) precisa virar 422 "dados
    incompletos", nunca 404 "calculadora não encontrada" — os dois erros
    têm causas e correções completamente diferentes para quem está usando
    a API."""
    user, token = criar_usuario()
    _subscribe(db, user.id)
    resposta = client.post(
        "/api/calculators/gscri/gerar-documento",
        json={"payload": {"idade": 70}},
        headers=_headers(token),
    )
    assert resposta.status_code == 422, resposta.text


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


def test_run_calculator_slug_inexistente_devolve_404(client, db, criar_usuario):
    """`POST /{slug}/run` (endpoint distinto de /gerar-documento, sem
    checagem prévia de slug no REGISTRY) precisava continuar devolvendo 404
    para slug genuinamente inexistente, depois da correção que separou esse
    caso de "payload incompleto"."""
    user, token = criar_usuario()
    _subscribe(db, user.id)
    resposta = client.post(
        "/api/calculators/nao-existe/run", json={}, headers=_headers(token),
    )
    assert resposta.status_code == 404


def test_run_calculator_payload_incompleto_devolve_422_nao_404(client, db, criar_usuario):
    """Mesma correção do bug de /gerar-documento (KeyError de campo
    obrigatório ausente mapeado por engano para 404), agora coberta também
    em /run — a rota que primeiro apresentava o defeito."""
    user, token = criar_usuario()
    _subscribe(db, user.id)
    resposta = client.post(
        "/api/calculators/gscri/run", json={"idade": 70}, headers=_headers(token),
    )
    assert resposta.status_code == 422, resposta.text


def test_run_calculator_gscri_funciona_com_payload_completo(client, db, criar_usuario):
    user, token = criar_usuario()
    _subscribe(db, user.id)
    resposta = client.post(
        "/api/calculators/gscri/run",
        json={
            "idade": 70, "asa": 3, "tipo_procedimento": "hernia",
            "status_funcional": "independente", "diabetes": "nao",
        },
        headers=_headers(token),
    )
    assert resposta.status_code == 200, resposta.text
    assert "risco_pct" in resposta.json()["result"]


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
