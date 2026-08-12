"""Ficha administrativa completa do assinante (11/08/2026, issue de
estabilização pré-lançamento) — GET /api/admin/usuarios (lista pesquisável
e paginada), GET /api/admin/usuarios/{id} (a ficha em si) e
POST /api/admin/kyc/{id}/solicitar-reenvio (terceira decisão de KYC, além
de aprovar/rejeitar).

Cobre principalmente segurança (só admin, em toda rota nova; 401 sem
token; 404 para usuário inexistente) e a integridade do contrato de
resposta que o frontend vai consumir — não reexecuta a suíte geral.
"""
import pytest

from app.models.audit import AuditLog
from app.models.subscription import Subscription
from app.services.kyc import verificacao


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(autouse=True)
def _diretorio_kyc(tmp_path, monkeypatch):
    from app.core.config import settings

    monkeypatch.setattr(settings, "kyc_dir", str(tmp_path))


def _docs(**overrides) -> verificacao.DocumentosSubmissao:
    base = dict(
        doc_profissional_frente=b"frente-profissional",
        doc_profissional_verso=b"verso-profissional",
        selfie=b"selfie-ao-vivo",
        doc_pessoal_frente=b"frente-pessoal",
        doc_pessoal_verso=b"verso-pessoal",
    )
    base.update(overrides)
    return verificacao.DocumentosSubmissao(**base)


def _admin(criar_usuario):
    return criar_usuario(email="admin-ficha@teste.local", role="admin")


# ---------------------------------------------------------------------------
# Segurança — matriz de papéis, nas três rotas novas
# ---------------------------------------------------------------------------

ROTAS_PROTEGIDAS = [
    ("GET", "/api/admin/usuarios"),
    ("GET", "/api/admin/usuarios/1"),
    ("POST", "/api/admin/kyc/1/solicitar-reenvio"),
]


@pytest.mark.parametrize("metodo,rota", ROTAS_PROTEGIDAS)
def test_sem_token_e_401(client, db, metodo, rota):
    resposta = client.request(metodo, rota, json={"nota": "x"} if metodo == "POST" else None)
    assert resposta.status_code == 401


@pytest.mark.parametrize("papel", ["medico", "leitor", "residente"])
@pytest.mark.parametrize("metodo,rota", ROTAS_PROTEGIDAS)
def test_papel_nao_admin_e_403(client, db, criar_usuario, metodo, rota, papel):
    _, token = criar_usuario(email=f"nao-admin-{papel}-{metodo}@teste.local", role=papel)
    resposta = client.request(
        metodo, rota, headers=_headers(token), json={"nota": "x"} if metodo == "POST" else None
    )
    assert resposta.status_code == 403


def test_admin_acessa_as_tres_rotas(client, db, criar_usuario):
    """Confirma que require_admin (não current_user) protege — um admin de
    verdade, olhando a PRÓPRIA ficha ou a de outro, sempre passa."""
    admin, token_admin = _admin(criar_usuario)
    resposta_lista = client.get("/api/admin/usuarios", headers=_headers(token_admin))
    assert resposta_lista.status_code == 200

    resposta_ficha = client.get(f"/api/admin/usuarios/{admin.id}", headers=_headers(token_admin))
    assert resposta_ficha.status_code == 200

    kyc = verificacao.submeter(db, admin, _docs())
    db.commit()
    resposta_reenvio = client.post(
        f"/api/admin/kyc/{kyc.id}/solicitar-reenvio",
        json={"nota": "foto ilegível, reenvie mais nítida"},
        headers=_headers(token_admin),
    )
    assert resposta_reenvio.status_code == 200, resposta_reenvio.text
    assert resposta_reenvio.json()["status"] == "reenvio_solicitado"


def test_usuario_inexistente_e_404(client, db, criar_usuario):
    _, token_admin = _admin(criar_usuario)
    resposta = client.get("/api/admin/usuarios/999999", headers=_headers(token_admin))
    assert resposta.status_code == 404


def test_documento_com_campo_desconhecido_continua_422(client, db, criar_usuario):
    """Não é rota nova — é o endpoint já existente de servir documento
    (GET /admin/kyc/{id}/documento/{campo}), reaproveitado pela ficha.
    Confirma que a validação de campo não regrediu."""
    user, token_user = criar_usuario(email="kyc-campo-invalido@teste.local")
    _, token_admin = _admin(criar_usuario)
    kyc = verificacao.submeter(db, user, _docs())
    db.commit()

    resposta = client.get(
        f"/api/admin/kyc/{kyc.id}/documento/campo-que-nao-existe", headers=_headers(token_admin)
    )
    assert resposta.status_code == 422


def test_nenhuma_url_de_documento_e_publica(client, db, criar_usuario):
    """A ficha nunca inventa um segundo caminho de servir arquivo — o link
    de cada documento aponta para a MESMA rota admin-only já existente, e
    essa rota continua exigindo admin (403 sem ele)."""
    user, token_user = criar_usuario(email="kyc-url-nao-publica@teste.local")
    admin, token_admin = _admin(criar_usuario)
    kyc = verificacao.submeter(db, user, _docs())
    db.commit()

    ficha = client.get(f"/api/admin/usuarios/{user.id}", headers=_headers(token_admin)).json()
    documentos = ficha["kyc"]["documentos"]
    assert len(documentos) == 6
    selfie = next(d for d in documentos if d["campo"] == "selfie")
    assert selfie["disponivel"] is True
    assert selfie["url"] == f"/api/admin/kyc/{kyc.id}/documento/selfie"

    # A própria URL devolvida, sem token, é 401; com token de médico comum, 403.
    caminho = selfie["url"].removeprefix("/api")
    assert client.get(f"/api{caminho}").status_code == 401
    assert client.get(f"/api{caminho}", headers=_headers(token_user)).status_code == 403
    resposta_admin = client.get(f"/api{caminho}", headers=_headers(token_admin))
    assert resposta_admin.status_code == 200


# ---------------------------------------------------------------------------
# GET /api/admin/usuarios — lista pesquisável e paginada
# ---------------------------------------------------------------------------

def test_lista_filtra_por_status_convidado_investidor(client, db, criar_usuario):
    _, token_admin = _admin(criar_usuario)
    pendente, _ = criar_usuario(email="pendente@teste.local")
    pendente.status = "pendente"
    convidado, _ = criar_usuario(email="convidado@teste.local")
    convidado.status = "aprovado"
    convidado.convidado = True
    investidor, _ = criar_usuario(email="investidor@teste.local")
    investidor.status = "aprovado"
    investidor.investidor = True
    db.commit()

    r_pendente = client.get("/api/admin/usuarios?status=pendente", headers=_headers(token_admin))
    assert r_pendente.status_code == 200
    emails_pendente = {i["email"] for i in r_pendente.json()["items"]}
    assert "pendente@teste.local" in emails_pendente
    assert "convidado@teste.local" not in emails_pendente

    r_convidado = client.get("/api/admin/usuarios?convidado=true", headers=_headers(token_admin))
    emails_convidado = {i["email"] for i in r_convidado.json()["items"]}
    assert emails_convidado == {"convidado@teste.local"}

    r_investidor = client.get("/api/admin/usuarios?investidor=true", headers=_headers(token_admin))
    emails_investidor = {i["email"] for i in r_investidor.json()["items"]}
    assert emails_investidor == {"investidor@teste.local"}


def test_lista_filtra_por_kyc_status_incluindo_sem_kyc(client, db, criar_usuario):
    _, token_admin = _admin(criar_usuario)
    com_kyc, _ = criar_usuario(email="com-kyc@teste.local")
    sem_kyc, _ = criar_usuario(email="sem-kyc@teste.local")
    verificacao.submeter(db, com_kyc, _docs())
    db.commit()

    r_pendente_revisao = client.get(
        "/api/admin/usuarios?kyc_status=aguardando_revisao", headers=_headers(token_admin)
    )
    emails = {i["email"] for i in r_pendente_revisao.json()["items"]}
    assert "com-kyc@teste.local" in emails
    assert "sem-kyc@teste.local" not in emails

    r_sem_kyc = client.get("/api/admin/usuarios?kyc_status=sem_kyc", headers=_headers(token_admin))
    emails_sem_kyc = {i["email"] for i in r_sem_kyc.json()["items"]}
    assert "sem-kyc@teste.local" in emails_sem_kyc
    assert "com-kyc@teste.local" not in emails_sem_kyc


def test_lista_filtra_por_subscription_status_incluindo_sem_assinatura(client, db, criar_usuario):
    _, token_admin = _admin(criar_usuario)
    ativo, _ = criar_usuario(email="assinante-ativo@teste.local")
    sem_assinatura, _ = criar_usuario(email="sem-assinatura@teste.local")
    db.add(Subscription(user_id=ativo.id, kind="meucardio", plano="basico", status="ativo"))
    db.commit()

    r_ativo = client.get("/api/admin/usuarios?subscription_status=ativo", headers=_headers(token_admin))
    emails_ativo = {i["email"] for i in r_ativo.json()["items"]}
    assert "assinante-ativo@teste.local" in emails_ativo
    assert "sem-assinatura@teste.local" not in emails_ativo

    r_sem = client.get(
        "/api/admin/usuarios?subscription_status=sem_assinatura", headers=_headers(token_admin)
    )
    emails_sem = {i["email"] for i in r_sem.json()["items"]}
    assert "sem-assinatura@teste.local" in emails_sem
    assert "assinante-ativo@teste.local" not in emails_sem


def test_lista_filtro_de_status_invalido_e_422(client, db, criar_usuario):
    _, token_admin = _admin(criar_usuario)
    assert client.get("/api/admin/usuarios?status=nao_existe", headers=_headers(token_admin)).status_code == 422
    assert client.get("/api/admin/usuarios?kyc_status=nao_existe", headers=_headers(token_admin)).status_code == 422
    assert (
        client.get("/api/admin/usuarios?subscription_status=nao_existe", headers=_headers(token_admin)).status_code
        == 422
    )


def test_lista_busca_por_nome_email_cpf_e_conselho(client, db, criar_usuario):
    _, token_admin = _admin(criar_usuario)
    alvo, _ = criar_usuario(email="dra.fulana@teste.local", full_name="Dra. Fulana de Tal")
    alvo.cpf = "12345678901"
    alvo.council_number = "SP-138266"
    outro, _ = criar_usuario(email="outro@teste.local", full_name="Outro Médico")

    db.commit()

    for termo in ("Fulana", "dra.fulana@teste.local", "45678", "138266"):
        resposta = client.get(f"/api/admin/usuarios?q={termo}", headers=_headers(token_admin))
        assert resposta.status_code == 200, (termo, resposta.text)
        emails = {i["email"] for i in resposta.json()["items"]}
        assert "dra.fulana@teste.local" in emails, f"termo {termo!r} não achou o alvo"
        assert "outro@teste.local" not in emails, f"termo {termo!r} trouxe quem não devia"


def test_lista_cpf_vem_mascarado(client, db, criar_usuario):
    _, token_admin = _admin(criar_usuario)
    alvo, _ = criar_usuario(email="cpf-mascarado@teste.local")
    alvo.cpf = "12345678901"
    db.commit()

    resposta = client.get("/api/admin/usuarios?q=cpf-mascarado", headers=_headers(token_admin))
    item = resposta.json()["items"][0]
    assert item["cpf_mascarado"] == "***.***.789-01"
    assert "12345678901" not in resposta.text


def test_lista_paginada_com_total_e_has_more(client, db, criar_usuario):
    _, token_admin = _admin(criar_usuario)
    for i in range(3):
        criar_usuario(email=f"pag-{i}@teste.local")

    pagina1 = client.get(
        "/api/admin/usuarios?page=1&page_size=1&q=pag-", headers=_headers(token_admin)
    ).json()
    assert pagina1["page"] == 1
    assert pagina1["page_size"] == 1
    assert pagina1["total"] == 3
    assert pagina1["has_more"] is True
    assert len(pagina1["items"]) == 1

    pagina3 = client.get(
        "/api/admin/usuarios?page=3&page_size=1&q=pag-", headers=_headers(token_admin)
    ).json()
    assert pagina3["has_more"] is False
    assert len(pagina3["items"]) == 1


# ---------------------------------------------------------------------------
# GET /api/admin/usuarios/{id} — a ficha
# ---------------------------------------------------------------------------

def test_ficha_dados_pessoais_e_profissionais(client, db, criar_usuario):
    _, token_admin = _admin(criar_usuario)
    alvo, _ = criar_usuario(email="ficha-completa@teste.local", full_name="Dr. Ficha Completa")
    alvo.cpf = "12345678901"
    alvo.profession = "Médico"
    alvo.council_name = "CRM"
    alvo.council_number = "138266"
    alvo.council_state = "SP"
    alvo.home_city = "São Paulo"
    alvo.home_state = "SP"
    alvo.practice_city = "São Paulo"
    alvo.practice_phone = "11999998888"
    db.commit()

    ficha = client.get(f"/api/admin/usuarios/{alvo.id}", headers=_headers(token_admin)).json()

    assert ficha["cpf_mascarado"] == "***.***.789-01"
    assert ficha["dados_pessoais"]["cpf"] == "12345678901"  # completo, sem máscara — ficha admin
    assert ficha["dados_pessoais"]["full_name"] == "Dr. Ficha Completa"
    assert ficha["dados_pessoais"]["endereco_residencial"]["city"] == "São Paulo"
    assert ficha["dados_profissionais"]["council_number"] == "138266"
    assert ficha["dados_profissionais"]["endereco_profissional"]["phone"] == "11999998888"


@pytest.mark.parametrize(
    "papel,convidado,investidor,tem_subscription_ativa,origem_esperada,tem_acesso_esperado",
    [
        ("admin", False, False, False, "admin", True),
        ("medico", True, False, False, "convidado", True),
        ("medico", False, True, False, "investidor", True),
        ("medico", False, False, True, "assinatura_paga", True),
        ("medico", False, False, False, "sem_acesso", False),
    ],
)
def test_ficha_origem_do_acesso_usa_a_fonte_central_de_entitlement(
    client, db, criar_usuario, papel, convidado, investidor, tem_subscription_ativa,
    origem_esperada, tem_acesso_esperado,
):
    _, token_admin = _admin(criar_usuario)
    alvo, _ = criar_usuario(email=f"origem-{origem_esperada}@teste.local", role=papel)
    alvo.convidado = convidado
    alvo.investidor = investidor
    if tem_subscription_ativa:
        db.add(Subscription(user_id=alvo.id, kind="meucardio", plano="completo", status="ativo"))
    db.commit()

    ficha = client.get(f"/api/admin/usuarios/{alvo.id}", headers=_headers(token_admin)).json()
    assert ficha["assinatura"]["origem_acesso"] == origem_esperada
    assert ficha["assinatura"]["tem_acesso_ao_produto"] is tem_acesso_esperado


def test_ficha_assinatura_nunca_expoe_segredo_so_ids(client, db, criar_usuario):
    _, token_admin = _admin(criar_usuario)
    alvo, _ = criar_usuario(email="assinatura-sem-segredo@teste.local")
    db.add(Subscription(
        user_id=alvo.id, kind="meucardio", plano="completo", status="ativo",
        stripe_customer_id="cus_abc123", stripe_subscription_id="sub_xyz789",
    ))
    db.commit()

    resposta = client.get(f"/api/admin/usuarios/{alvo.id}", headers=_headers(token_admin))
    principal = resposta.json()["assinatura"]["assinatura_principal"]
    assert principal["stripe_customer_id"] == "cus_abc123"
    assert principal["stripe_subscription_id"] == "sub_xyz789"
    # nenhuma chave plausível de segredo/cartão no corpo da resposta inteira
    texto = resposta.text.lower()
    for termo_proibido in ("sk_", "cvv", "card_number", "client_secret", "senha", "password"):
        assert termo_proibido not in texto


def test_ficha_kyc_sem_submissao(client, db, criar_usuario):
    _, token_admin = _admin(criar_usuario)
    alvo, _ = criar_usuario(email="sem-kyc-ficha@teste.local")
    db.commit()

    ficha = client.get(f"/api/admin/usuarios/{alvo.id}", headers=_headers(token_admin)).json()
    assert ficha["kyc"]["existe"] is False
    assert ficha["kyc"]["status"] is None
    assert ficha["kyc"]["documentos"] == []
    assert ficha["kyc"]["ultima_decisao"] is None


def test_ficha_historico_registra_cada_decisao_sem_sobrescrever_anteriores(client, db, criar_usuario):
    """aprovar → rejeitar → solicitar-reenvio: cada chamada é uma linha NOVA
    de AuditLog, o histórico preserva as três, mais recente primeiro."""
    admin, token_admin = _admin(criar_usuario)
    alvo, _ = criar_usuario(email="historico-tres-decisoes@teste.local")
    kyc = verificacao.submeter(db, alvo, _docs())
    db.commit()

    r1 = client.post(f"/api/admin/kyc/{kyc.id}/aprovar", json={"nota": "ok"}, headers=_headers(token_admin))
    assert r1.status_code == 200
    r2 = client.post(
        f"/api/admin/kyc/{kyc.id}/rejeitar", json={"nota": "documento ilegível"}, headers=_headers(token_admin)
    )
    assert r2.status_code == 200
    r3 = client.post(
        f"/api/admin/kyc/{kyc.id}/solicitar-reenvio",
        json={"nota": "selfie muito escura, tire de novo com mais luz"},
        headers=_headers(token_admin),
    )
    assert r3.status_code == 200
    assert r3.json()["status"] == "reenvio_solicitado"

    entradas_kyc = (
        db.query(AuditLog)
        .filter(AuditLog.entity == "kyc_verifications", AuditLog.entity_id == str(kyc.id))
        .all()
    )
    acoes = sorted(e.action for e in entradas_kyc)
    # kyc_submissao (da submissão) + as 3 decisões
    assert acoes == sorted(["kyc_submissao", "kyc_aprovado", "kyc_rejeitado", "kyc_reenvio_solicitado"])

    ficha = client.get(f"/api/admin/usuarios/{alvo.id}", headers=_headers(token_admin)).json()
    acoes_historico = [e["action"] for e in ficha["historico"] if e["entity"] == "kyc_verifications"]
    assert set(acoes_historico) == set(acoes)
    # mais recente primeiro
    datas = [e["created_at"] for e in ficha["historico"]]
    assert datas == sorted(datas, reverse=True)

    # a última decisão exibida é a mais recente: solicitar-reenvio
    ultima = ficha["kyc"]["ultima_decisao"]
    assert ultima["action"] == "kyc_reenvio_solicitado"
    assert ultima["nota"] == "selfie muito escura, tire de novo com mais luz"
    assert ultima["admin_nome"] == admin.full_name

    # e o estado atual do registro reflete a decisão mais recente
    assert ficha["kyc"]["status"] == "reenvio_solicitado"
    assert ficha["kyc"]["nota_revisao"] == "selfie muito escura, tire de novo com mais luz"


def test_ficha_historico_inclui_decisao_de_cadastro_e_assinatura(client, db, criar_usuario):
    admin, token_admin = _admin(criar_usuario)
    alvo, token_alvo = criar_usuario(email="historico-cadastro@teste.local")
    alvo.status = "pendente"
    db.commit()

    r = client.post(
        f"/api/admin/users/{alvo.id}/decidir",
        json={"aprovar": True, "role": "medico"},
        headers=_headers(token_admin),
    )
    assert r.status_code == 200

    sub = Subscription(user_id=alvo.id, kind="meucardio", plano="basico", status="ativo")
    db.add(sub)
    db.commit()
    db.add(AuditLog(
        user_id=alvo.id, action="solicitar_troca_plano", entity="subscription",
        entity_id=str(sub.id), detail={"plano_solicitado": "completo"},
    ))
    db.commit()

    ficha = client.get(f"/api/admin/usuarios/{alvo.id}", headers=_headers(token_admin)).json()
    acoes = {e["action"] for e in ficha["historico"]}
    assert "aprovar_acesso" in acoes
    assert "solicitar_troca_plano" in acoes
    entrada_aprovacao = next(e for e in ficha["historico"] if e["action"] == "aprovar_acesso")
    assert entrada_aprovacao["admin_nome"] == admin.full_name


def test_solicitar_reenvio_exige_nota(client, db, criar_usuario):
    _, token_admin = _admin(criar_usuario)
    alvo, _ = criar_usuario(email="reenvio-sem-nota@teste.local")
    kyc = verificacao.submeter(db, alvo, _docs())
    db.commit()

    resposta = client.post(
        f"/api/admin/kyc/{kyc.id}/solicitar-reenvio", json={"nota": None}, headers=_headers(token_admin)
    )
    assert resposta.status_code == 422

    resposta_vazia = client.post(
        f"/api/admin/kyc/{kyc.id}/solicitar-reenvio", json={"nota": "   "}, headers=_headers(token_admin)
    )
    assert resposta_vazia.status_code == 422


def test_solicitar_reenvio_item_inexistente_e_404(client, db, criar_usuario):
    _, token_admin = _admin(criar_usuario)
    resposta = client.post(
        "/api/admin/kyc/999999/solicitar-reenvio", json={"nota": "qualquer"}, headers=_headers(token_admin)
    )
    assert resposta.status_code == 404


def test_reenvio_solicitado_aparece_para_o_proprio_assinante(client, db, criar_usuario):
    """Confirma que app/api/kyc.py::_status_publico também passou a mostrar
    a nota nesse status novo (mesma régua já usada para 'rejeitado')."""
    admin, token_admin = _admin(criar_usuario)
    alvo, token_alvo = criar_usuario(email="reenvio-visivel-ao-medico@teste.local")
    # GET /api/kyc/status exige assinante_ativo (não está na lista de rotas
    # de acesso livre em app/main.py) — precisa de assinatura para não
    # tomar 402 antes mesmo de chegar à checagem de KYC.
    db.add(Subscription(user_id=alvo.id, kind="meucardio", plano="basico", status="ativo"))
    kyc = verificacao.submeter(db, alvo, _docs())
    db.commit()

    client.post(
        f"/api/admin/kyc/{kyc.id}/solicitar-reenvio",
        json={"nota": "envie o documento profissional sem reflexo de flash"},
        headers=_headers(token_admin),
    )

    status_medico = client.get("/api/kyc/status", headers=_headers(token_alvo)).json()
    assert status_medico["status"] == "reenvio_solicitado"
    assert status_medico["liberado"] is False
    assert status_medico["nota_revisao"] == "envie o documento profissional sem reflexo de flash"
