"""Configuração dos testes automatizados do CorvIA Mail (Tarefa 28/29).

Exige um Postgres real acessível pelas variáveis POSTGRES_* (ou DATABASE_URL)
já com `alembic upgrade head` aplicado — não roda `create_all`, de propósito:
o objetivo é testar contra o mesmo esquema que a migração real produz, não
contra uma aproximação do SQLAlchemy. Ver README dos testes para o passo a
passo de banco local.

As variáveis de ambiente têm que estar definidas ANTES de qualquer `import
app...`, porque `app.core.config.Settings` é instanciada na importação do
módulo (`settings = Settings()`, no fim de `app/core/config.py`).
"""
import os

os.environ.setdefault("POSTGRES_HOST", "localhost")
os.environ.setdefault("POSTGRES_PORT", "5432")
os.environ.setdefault("POSTGRES_USER", "meucardio_test")
os.environ.setdefault("POSTGRES_PASSWORD", "test")
os.environ.setdefault("POSTGRES_DB", "meucardio_test")
os.environ.setdefault("STORAGE_ENCRYPTION_KEY", "MDEyMzQ1Njc4OTAxMjM0NTY3ODkwMTIzNDU2Nzg5MDE=")
os.environ.setdefault("JWT_SECRET", "chave-de-teste-nao-usar-em-producao")
os.environ.setdefault("ADMIN_EMAIL", "admin@teste.local")
os.environ.setdefault("ADMIN_PASSWORD", "admin-teste-123")
# Mail360 "configurado" (as três variáveis não vazias) para exercitar o
# caminho feliz das rotas — as chamadas HTTP de verdade são sempre
# mockadas (`monkeypatch_mail360`), nunca saem para a rede nos testes.
os.environ.setdefault("MAIL360_CLIENT_ID", "id-de-teste")
os.environ.setdefault("MAIL360_CLIENT_SECRET", "secret-de-teste")
os.environ.setdefault("MAIL360_REFRESH_TOKEN", "refresh-de-teste")
os.environ.setdefault("CORVIA_MAIL_PRECO_CENTAVOS", "1000")
os.environ.setdefault("STRIPE_SECRET_KEY", "sk_test_dummy")
os.environ.setdefault("STRIPE_WEBHOOK_SECRET", "whsec_teste_dummy")
os.environ.setdefault("PUBLIC_URL", "https://corvia.med.br")
os.environ.setdefault("AI_ENABLED", "false")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import text  # noqa: E402

from app.core.db import SessionLocal  # noqa: E402
from app.core.security import create_access_token, hash_password  # noqa: E402
from app.main import app  # noqa: E402
from app.models.user import User  # noqa: E402

# Tabelas tocadas pelos testes desta suíte — truncadas (com CASCADE, e
# reiniciando as sequences) antes de cada teste, para isolamento sem
# depender de rollback de transação (a app abre e fecha sua própria sessão
# por request, então uma transação só do teste não cobriria o que a rota
# grava). Nunca inclui tabela de conteúdo clínico: esta suíte não mexe nelas.
TABELAS_PARA_LIMPAR = (
    "password_reset_tokens",
    "email_accounts",
    "subscriptions",
    "audit_logs",
    "convidados_pre_autorizados",
    "users",
)


@pytest.fixture(autouse=True)
def _banco_limpo():
    db = SessionLocal()
    try:
        db.execute(text(f"TRUNCATE {', '.join(TABELAS_PARA_LIMPAR)} RESTART IDENTITY CASCADE"))
        db.commit()
    finally:
        db.close()
    yield


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def criar_usuario(db):
    """Cria um médico ativo direto no banco e devolve (user, token_app)."""

    def _criar(email="medico@teste.local", full_name="Dra. Teste da Silva", role="medico"):
        user = User(
            email=email, full_name=full_name, role=role,
            password_hash=hash_password("senha-conta-123"), is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        token = create_access_token(user.email, scope="app")
        return user, token

    return _criar


@pytest.fixture
def monkeypatch_mail360(monkeypatch):
    """Substitui as chamadas de rede do cliente Mail360 por dublês
    determinísticos — nenhum teste desta suíte sai para a internet.
    `contas_criadas` guarda o que `criar_conta_nativa` recebeu, para os
    testes que precisam conferir o endereço gerado."""
    from app.services import mail360

    estado = {
        "contas_criadas": [], "mensagens_enviadas": [], "anexos": [],
        "acoes": [], "respostas": [],
    }

    def _criar_conta_nativa(email_address, nome_exibicao):
        estado["contas_criadas"].append((email_address, nome_exibicao))
        return f"account-key-{len(estado['contas_criadas'])}"

    def _listar_pastas(account_key):
        return [{"folderId": "1", "name": "Inbox"}, {"folderId": "2", "name": "Enviados"}]

    def _listar_mensagens(account_key, pasta=None, limite=50, inicio=1):
        return [{"messageId": "msg-1", "subject": "Bem-vindo ao CorvIA Mail", "folder": pasta or "Inbox"}]

    def _obter_mensagem(account_key, message_id):
        return {"messageId": message_id, "subject": "Assunto de teste", "content": "corpo de teste"}

    def _upload_anexo(account_key, nome_arquivo, conteudo):
        estado["anexos"].append((account_key, nome_arquivo, len(conteudo)))
        return f"file-id-{len(estado['anexos'])}"

    def _enviar_mensagem(account_key, remetente, para, assunto, corpo_html, anexos=None, cc=None, cco=None, mail_format="plaintext"):
        registro = {
            "account_key": account_key, "remetente": remetente, "para": para,
            "assunto": assunto, "corpo": corpo_html, "anexos": anexos or [], "cc": cc, "cco": cco,
            "mail_format": mail_format,
        }
        estado["mensagens_enviadas"].append(registro)
        return {"messageId": "msg-enviada-1"}

    def _excluir_mensagem(account_key, message_id):
        return None

    def _alterar_mensagens(account_key, message_ids, acao, pasta_destino=None, sinalizador=None):
        estado["acoes"].append({
            "account_key": account_key, "message_ids": message_ids, "acao": acao,
            "pasta_destino": pasta_destino, "sinalizador": sinalizador,
        })

    def _responder_mensagem(
        account_key, message_id, remetente, acao, assunto, conteudo,
        para=None, cc=None, cco=None, anexos=None, mail_format="plaintext",
    ):
        estado["respostas"].append({
            "account_key": account_key, "message_id": message_id, "remetente": remetente,
            "acao": acao, "assunto": assunto, "conteudo": conteudo, "para": para,
            "cc": cc, "cco": cco, "anexos": anexos or [], "mail_format": mail_format,
        })
        return {"messageId": "resposta-1"}

    def _listar_anexos(account_key, message_id):
        return [{"attachmentId": "attach-1", "attachmentName": "arquivo.pdf", "attachmentSize": 100}]

    def _baixar_anexo(account_key, message_id, attachment_id):
        return b"arquivo", "application/pdf"

    monkeypatch.setattr(mail360, "criar_conta_nativa", _criar_conta_nativa)
    monkeypatch.setattr(mail360, "listar_pastas", _listar_pastas)
    monkeypatch.setattr(mail360, "listar_mensagens", _listar_mensagens)
    monkeypatch.setattr(mail360, "obter_mensagem", _obter_mensagem)
    monkeypatch.setattr(mail360, "upload_anexo", _upload_anexo)
    monkeypatch.setattr(mail360, "enviar_mensagem", _enviar_mensagem)
    monkeypatch.setattr(mail360, "excluir_mensagem", _excluir_mensagem)
    monkeypatch.setattr(mail360, "alterar_mensagens", _alterar_mensagens)
    monkeypatch.setattr(mail360, "responder_mensagem", _responder_mensagem)
    monkeypatch.setattr(mail360, "listar_anexos", _listar_anexos)
    monkeypatch.setattr(mail360, "baixar_anexo", _baixar_anexo)
    return estado
