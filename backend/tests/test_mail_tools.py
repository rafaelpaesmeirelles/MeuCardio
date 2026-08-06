"""Testes de `app/services/ia/mail_tools.py` — tools de e-mail (SOMENTE
LEITURA) do assistente de IA clínico.

Segue o padrão de `tests/test_agenda_integrada.py` e `tests/conftest.py`
(fixtures `db`, `client`, `criar_usuario`, `monkeypatch_mail360`) — banco
Postgres real truncado a cada teste, sem sair para a rede (as chamadas ao
Mail360 são sempre mockadas).
"""
from app.models.email_account import EmailAccount
from app.models.subscription import TIPO_EMAIL, Subscription
from app.services import mail360
from app.services.ia.mail_tools import executar_tool_mail


def _ativar_caixa(
    db, user_id: int, *, email_address="medico@corvia.med.br", account_key="chave-conta-1",
) -> EmailAccount:
    """Cria a assinatura de e-mail ativa + a EmailAccount, mesmo par que
    `POST /api/email/conta` produziria — sem passar pela rota HTTP, porque
    aqui o alvo é a tool, não a rota."""
    db.add(Subscription(user_id=user_id, kind=TIPO_EMAIL, status="ativo"))
    conta = EmailAccount(
        user_id=user_id,
        email_address=email_address,
        mail360_account_key=account_key,
        password_hash="hash-de-teste",
        status="ativa",
    )
    db.add(conta)
    db.commit()
    db.refresh(conta)
    return conta


# ---------------------------------------------------------------------------
# 1. Usuário sem EmailAccount -> erro tratado, não exceção
# ---------------------------------------------------------------------------

def test_resumo_caixa_sem_conta_devolve_erro_tratado(db, criar_usuario, monkeypatch_mail360):
    user, _token = criar_usuario(email="sem-caixa@teste.local")

    resultado = executar_tool_mail("mail_resumo_caixa", {}, db, user)

    assert resultado == {
        "erro": "sem_caixa_ativa",
        "mensagem": "Você ainda não tem uma caixa de e-mail CorvIA Mail ativa.",
    }
    # Nenhuma chamada de rede foi feita, porque a resolução da conta falhou
    # antes de qualquer coisa que precisasse do Mail360.
    assert monkeypatch_mail360["mensagens_enviadas"] == []


def test_listar_pastas_sem_conta_devolve_erro_tratado(db, criar_usuario, monkeypatch_mail360):
    user, _token = criar_usuario(email="sem-caixa-pastas@teste.local")

    resultado = executar_tool_mail("mail_listar_pastas", {}, db, user)

    assert resultado["erro"] == "sem_caixa_ativa"


def test_listar_mensagens_sem_conta_devolve_erro_tratado(db, criar_usuario, monkeypatch_mail360):
    user, _token = criar_usuario(email="sem-caixa-msgs@teste.local")

    resultado = executar_tool_mail("mail_listar_mensagens", {}, db, user)

    assert resultado["erro"] == "sem_caixa_ativa"


def test_ler_mensagem_sem_conta_devolve_erro_tratado(db, criar_usuario, monkeypatch_mail360):
    user, _token = criar_usuario(email="sem-caixa-ler@teste.local")

    resultado = executar_tool_mail("mail_ler_mensagem", {"message_id": "msg-1"}, db, user)

    assert resultado["erro"] == "sem_caixa_ativa"


# ---------------------------------------------------------------------------
# 2. `limite` acima do máximo é clampado para 25, não erro
# ---------------------------------------------------------------------------

def test_listar_mensagens_clampa_limite_acima_do_maximo(db, criar_usuario, monkeypatch_mail360, monkeypatch):
    user, _token = criar_usuario(email="limite@teste.local")
    conta = _ativar_caixa(db, user.id)

    chamadas = []

    def _listar_mensagens_espiao(account_key, pasta=None, limite=50, inicio=1):
        chamadas.append({"account_key": account_key, "pasta": pasta, "limite": limite, "inicio": inicio})
        return [
            {"messageId": f"msg-{i}", "subject": f"Assunto {i}", "fromAddress": "x@y.com",
             "receivedTime": "1234567890000", "status": "1"}
            for i in range(1, limite + 1)
        ]

    monkeypatch.setattr(mail360, "listar_mensagens", _listar_mensagens_espiao)

    resultado = executar_tool_mail("mail_listar_mensagens", {"limite": 9999}, db, user)

    assert "erro" not in resultado
    assert len(chamadas) == 1
    assert chamadas[0]["limite"] == 25  # clampado, nunca 9999
    assert chamadas[0]["account_key"] == conta.mail360_account_key
    assert len(resultado["mensagens"]) == 25


def test_listar_mensagens_limite_negativo_ou_zero_vira_ao_menos_um(db, criar_usuario, monkeypatch, monkeypatch_mail360):
    user, _token = criar_usuario(email="limite-baixo@teste.local")
    _ativar_caixa(db, user.id)

    chamadas = []

    def _listar_mensagens_espiao(account_key, pasta=None, limite=50, inicio=1):
        chamadas.append(limite)
        return []

    monkeypatch.setattr(mail360, "listar_mensagens", _listar_mensagens_espiao)

    resultado = executar_tool_mail("mail_listar_mensagens", {"limite": -5}, db, user)

    assert "erro" not in resultado
    assert chamadas[0] == 1


def test_listar_mensagens_limite_nao_numerico_usa_padrao(db, criar_usuario, monkeypatch, monkeypatch_mail360):
    user, _token = criar_usuario(email="limite-invalido@teste.local")
    _ativar_caixa(db, user.id)

    chamadas = []
    monkeypatch.setattr(
        mail360, "listar_mensagens",
        lambda account_key, pasta=None, limite=50, inicio=1: (chamadas.append(limite), [])[1],
    )

    resultado = executar_tool_mail("mail_listar_mensagens", {"limite": "não é número"}, db, user)

    assert "erro" not in resultado
    assert chamadas[0] == 10  # LIMITE_PADRAO_MENSAGENS


# ---------------------------------------------------------------------------
# 3. `message_id` inexistente -> erro tratado, não exceção
# ---------------------------------------------------------------------------

def test_ler_mensagem_inexistente_devolve_erro_tratado(db, criar_usuario, monkeypatch, monkeypatch_mail360):
    user, _token = criar_usuario(email="msg-inexistente@teste.local")
    _ativar_caixa(db, user.id)

    def _obter_mensagem_falha(account_key, message_id):
        raise mail360.Mail360Error("Mail360 devolveu erro 404.")

    monkeypatch.setattr(mail360, "obter_mensagem", _obter_mensagem_falha)

    resultado = executar_tool_mail("mail_ler_mensagem", {"message_id": "msg-que-nao-existe"}, db, user)

    assert resultado == {
        "erro": "mensagem_nao_encontrada",
        "mensagem": "Não foi possível encontrar ou abrir essa mensagem.",
    }


def test_ler_mensagem_sem_message_id_e_erro_tratado(db, criar_usuario, monkeypatch_mail360):
    user, _token = criar_usuario(email="sem-message-id@teste.local")
    _ativar_caixa(db, user.id)

    resultado = executar_tool_mail("mail_ler_mensagem", {}, db, user)

    assert resultado["erro"] == "parametro_invalido"


def test_tool_desconhecida_nao_lanca_excecao(db, criar_usuario, monkeypatch_mail360):
    user, _token = criar_usuario(email="tool-desconhecida@teste.local")

    resultado = executar_tool_mail("mail_apagar_tudo", {}, db, user)

    assert resultado["erro"] == "tool_desconhecida"


def test_falha_inesperada_no_handler_nunca_propaga(db, criar_usuario, monkeypatch, monkeypatch_mail360):
    """Mesmo um erro totalmente fora do vocabulário tratado (TypeError, bug
    de verdade) tem que virar um dict de erro — o despachante é a última
    rede de segurança antes do loop de tool-calling."""
    user, _token = criar_usuario(email="falha-inesperada@teste.local")
    _ativar_caixa(db, user.id)

    def _explode(account_key):
        raise TypeError("isto não deveria propagar")

    monkeypatch.setattr(mail360, "listar_pastas", _explode)

    resultado = executar_tool_mail("mail_resumo_caixa", {}, db, user)

    assert resultado["erro"] == "falha_interna"


# ---------------------------------------------------------------------------
# 4. Mensagem HTML é sanitizada antes de voltar (mock do cliente mail360)
# ---------------------------------------------------------------------------

def test_ler_mensagem_sanitiza_corpo_html(db, criar_usuario, monkeypatch, monkeypatch_mail360):
    user, _token = criar_usuario(email="html@teste.local")
    _ativar_caixa(db, user.id)

    corpo_html = (
        "<html><head><style>body{color:red}</style></head><body>"
        "<div>Olá, <b>doutor</b>!</div>"
        "<p>Segue o resultado do exame.</p>"
        "<script>alert('não deveria aparecer')</script>"
        "</body></html>"
    )

    def _obter_mensagem_html(account_key, message_id):
        return {
            "messageId": message_id,
            "subject": "Resultado de exame",
            "fromAddress": "laboratorio@example.com",
            "receivedTime": "1700000000000",
            "content": corpo_html,
        }

    monkeypatch.setattr(mail360, "obter_mensagem", _obter_mensagem_html)
    monkeypatch.setattr(mail360, "alterar_mensagens", lambda *a, **k: None)
    monkeypatch.setattr(mail360, "listar_anexos", lambda account_key, message_id: [])

    resultado = executar_tool_mail("mail_ler_mensagem", {"message_id": "msg-html-1"}, db, user)

    assert "erro" not in resultado
    corpo = resultado["corpo"]
    assert "<div>" not in corpo
    assert "<script>" not in corpo
    assert "<style>" not in corpo
    assert "alert(" not in corpo  # conteúdo do <script>, não só a tag
    assert "color:red" not in corpo  # conteúdo do <style>
    assert "Olá" in corpo
    assert "doutor" in corpo
    assert "Segue o resultado do exame." in corpo
    assert resultado["truncado"] is False
    assert resultado["assunto"] == "Resultado de exame"


def test_ler_mensagem_trunca_corpo_longo_em_4000_caracteres(db, criar_usuario, monkeypatch, monkeypatch_mail360):
    user, _token = criar_usuario(email="corpo-longo@teste.local")
    _ativar_caixa(db, user.id)

    texto_longo = "a" * 5000

    def _obter_mensagem_longa(account_key, message_id):
        return {
            "messageId": message_id, "subject": "Assunto", "fromAddress": "x@y.com",
            "receivedTime": "1700000000000", "content": texto_longo,
        }

    monkeypatch.setattr(mail360, "obter_mensagem", _obter_mensagem_longa)
    monkeypatch.setattr(mail360, "alterar_mensagens", lambda *a, **k: None)
    monkeypatch.setattr(mail360, "listar_anexos", lambda account_key, message_id: [])

    resultado = executar_tool_mail("mail_ler_mensagem", {"message_id": "msg-longa"}, db, user)

    assert resultado["truncado"] is True
    assert len(resultado["corpo"]) == 4000


def test_ler_mensagem_lista_nomes_de_anexos_sem_conteudo(db, criar_usuario, monkeypatch, monkeypatch_mail360):
    user, _token = criar_usuario(email="anexos@teste.local")
    _ativar_caixa(db, user.id)

    monkeypatch.setattr(
        mail360, "obter_mensagem",
        lambda account_key, message_id: {
            "messageId": message_id, "subject": "Com anexo", "fromAddress": "x@y.com",
            "receivedTime": "1700000000000", "content": "<p>Segue anexo.</p>",
        },
    )
    monkeypatch.setattr(mail360, "alterar_mensagens", lambda *a, **k: None)
    monkeypatch.setattr(
        mail360, "listar_anexos",
        lambda account_key, message_id: [
            {"attachmentName": "exame.pdf", "attachmentSize": 1024},
            {"attachmentName": "laudo.docx", "attachmentSize": 2048},
        ],
    )

    resultado = executar_tool_mail("mail_ler_mensagem", {"message_id": "msg-anexo"}, db, user)

    assert resultado["anexos"] == ["exame.pdf", "laudo.docx"]
    # nunca o conteúdo do anexo, só o nome
    assert "attachmentSize" not in str(resultado)


# ---------------------------------------------------------------------------
# 5. Isolamento — usuário A não lê mensagem de outro EmailAccount
# ---------------------------------------------------------------------------

def test_ler_mensagem_isola_por_usuario_mesmo_com_message_id_alheio(
    db, criar_usuario, monkeypatch, monkeypatch_mail360,
):
    """Não existe parâmetro de "de quem" em nenhuma tool — toda chamada usa
    a account_key resolvida a partir do `user` autenticado. Este teste prova
    que, mesmo que o modelo passe um `message_id` que pertence à caixa de
    OUTRO usuário, a chamada ao Mail360 sempre usa a account_key do usuário
    que está de fato conversando com o assistente."""
    user_a, _token_a = criar_usuario(email="usuario-a@teste.local")
    user_b, _token_b = criar_usuario(email="usuario-b@teste.local")
    conta_a = _ativar_caixa(db, user_a.id, email_address="a@corvia.med.br", account_key="chave-a")
    conta_b = _ativar_caixa(db, user_b.id, email_address="b@corvia.med.br", account_key="chave-b")

    account_keys_usadas = []

    def _obter_mensagem_espiao(account_key, message_id):
        account_keys_usadas.append(account_key)
        return {
            "messageId": message_id, "subject": "Mensagem", "fromAddress": "x@y.com",
            "receivedTime": "1700000000000", "content": "corpo",
        }

    monkeypatch.setattr(mail360, "obter_mensagem", _obter_mensagem_espiao)
    monkeypatch.setattr(mail360, "alterar_mensagens", lambda *a, **k: None)
    monkeypatch.setattr(mail360, "listar_anexos", lambda account_key, message_id: [])

    # Usuário B pede uma mensagem cujo id "parece" pertencer à caixa de A —
    # não há como ele saber (nem a IA), mas mesmo que soubesse, o parâmetro
    # não influencia qual account_key é usada.
    resultado = executar_tool_mail(
        "mail_ler_mensagem", {"message_id": "mensagem-supostamente-de-outra-caixa"}, db, user_b,
    )

    assert "erro" not in resultado
    assert account_keys_usadas == [conta_b.mail360_account_key]
    assert conta_a.mail360_account_key not in account_keys_usadas


def test_listar_mensagens_isola_por_usuario(db, criar_usuario, monkeypatch, monkeypatch_mail360):
    user_a, _token_a = criar_usuario(email="isolamento-lista-a@teste.local")
    user_b, _token_b = criar_usuario(email="isolamento-lista-b@teste.local")
    conta_a = _ativar_caixa(db, user_a.id, email_address="lista-a@corvia.med.br", account_key="chave-lista-a")
    conta_b = _ativar_caixa(db, user_b.id, email_address="lista-b@corvia.med.br", account_key="chave-lista-b")

    account_keys_usadas = []

    def _listar_mensagens_espiao(account_key, pasta=None, limite=50, inicio=1):
        account_keys_usadas.append(account_key)
        return []

    monkeypatch.setattr(mail360, "listar_mensagens", _listar_mensagens_espiao)

    executar_tool_mail("mail_listar_mensagens", {}, db, user_a)
    executar_tool_mail("mail_listar_mensagens", {}, db, user_b)

    assert account_keys_usadas == [conta_a.mail360_account_key, conta_b.mail360_account_key]


def test_resumo_caixa_isola_por_usuario(db, criar_usuario, monkeypatch, monkeypatch_mail360):
    user_a, _token_a = criar_usuario(email="isolamento-resumo-a@teste.local")
    user_b, _token_b = criar_usuario(email="isolamento-resumo-b@teste.local")
    _ativar_caixa(db, user_a.id, email_address="resumo-a@corvia.med.br", account_key="chave-resumo-a")
    conta_b = _ativar_caixa(db, user_b.id, email_address="resumo-b@corvia.med.br", account_key="chave-resumo-b")

    monkeypatch.setattr(mail360, "listar_pastas", lambda account_key: [])

    account_keys_usadas = []

    def _listar_mensagens_espiao(account_key, pasta=None, limite=50, inicio=1):
        account_keys_usadas.append(account_key)
        return []

    monkeypatch.setattr(mail360, "listar_mensagens", _listar_mensagens_espiao)

    resultado = executar_tool_mail("mail_resumo_caixa", {}, db, user_b)

    assert resultado["email_address"] == conta_b.email_address
    assert account_keys_usadas == [conta_b.mail360_account_key]


# ---------------------------------------------------------------------------
# Caminho feliz básico — schema e despacho
# ---------------------------------------------------------------------------

def test_schema_tem_as_quatro_tools_com_input_schema_valido():
    from app.services.ia.mail_tools import MAIL_TOOLS_SCHEMA

    nomes = {tool["name"] for tool in MAIL_TOOLS_SCHEMA}
    assert nomes == {
        "mail_resumo_caixa", "mail_listar_pastas", "mail_listar_mensagens", "mail_ler_mensagem",
    }
    for tool in MAIL_TOOLS_SCHEMA:
        assert "description" in tool and tool["description"]
        schema = tool["input_schema"]
        assert schema["type"] == "object"
        assert "properties" in schema
        assert "required" in schema

    por_nome = {tool["name"]: tool for tool in MAIL_TOOLS_SCHEMA}
    assert por_nome["mail_ler_mensagem"]["input_schema"]["required"] == ["message_id"]
    assert por_nome["mail_resumo_caixa"]["input_schema"]["required"] == []
    assert por_nome["mail_listar_pastas"]["input_schema"]["required"] == []
    assert por_nome["mail_listar_mensagens"]["input_schema"]["required"] == []


def test_resumo_caixa_caminho_feliz(db, criar_usuario, monkeypatch, monkeypatch_mail360):
    user, _token = criar_usuario(email="feliz@teste.local")
    _ativar_caixa(db, user.id)

    monkeypatch.setattr(
        mail360, "listar_pastas",
        lambda account_key: [{"folderId": "1", "folderType": "inbox", "folderName": "Entrada"}],
    )
    monkeypatch.setattr(
        mail360, "listar_mensagens",
        lambda account_key, pasta=None, limite=50, inicio=1: [
            {"messageId": "m1", "status": "0"},  # não lida
            {"messageId": "m2", "status": "1"},  # lida
            {"messageId": "m3", "status": "0"},  # não lida
        ],
    )

    resultado = executar_tool_mail("mail_resumo_caixa", {}, db, user)

    assert resultado["ativa"] is True
    assert resultado["nao_lidas"] == 2
    assert resultado["aproximado"] is False


def test_listar_mensagens_apenas_nao_lidas(db, criar_usuario, monkeypatch, monkeypatch_mail360):
    user, _token = criar_usuario(email="nao-lidas@teste.local")
    _ativar_caixa(db, user.id)

    monkeypatch.setattr(
        mail360, "listar_mensagens",
        lambda account_key, pasta=None, limite=50, inicio=1: [
            {"messageId": "m1", "status": "0", "subject": "Não lida 1", "fromAddress": "a@a.com", "receivedTime": "1"},
            {"messageId": "m2", "status": "1", "subject": "Lida", "fromAddress": "b@b.com", "receivedTime": "2"},
        ],
    )

    resultado = executar_tool_mail(
        "mail_listar_mensagens", {"apenas_nao_lidas": True}, db, user,
    )

    assert len(resultado["mensagens"]) == 1
    assert resultado["mensagens"][0]["id"] == "m1"
    assert resultado["mensagens"][0]["lida"] is False


def test_listar_mensagens_provedor_externo_nao_conectado(db, criar_usuario, monkeypatch_mail360):
    user, _token = criar_usuario(email="externo-nao-conectado@teste.local")
    _ativar_caixa(db, user.id)

    resultado = executar_tool_mail("mail_listar_mensagens", {"provedor": "google"}, db, user)

    assert resultado["erro"] == "provedor_nao_conectado"


def test_listar_mensagens_provedor_invalido(db, criar_usuario, monkeypatch_mail360):
    user, _token = criar_usuario(email="provedor-invalido@teste.local")
    _ativar_caixa(db, user.id)

    resultado = executar_tool_mail("mail_listar_mensagens", {"provedor": "yahoo"}, db, user)

    assert resultado["erro"] == "provedor_invalido"
