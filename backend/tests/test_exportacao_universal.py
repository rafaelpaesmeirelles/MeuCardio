"""Exportação universal: conteúdo canônico → PDF → download ou CorVIA Mail.

Os testes usam um documento clínico mínimo publicado e não dependem do corpus
carregado no banco de teste. A rota é exercitada de ponta a ponta com a mesma
dependência global de assinatura principal usada em produção.
"""
import pytest
from sqlalchemy import text

from app.models.content import Document
from app.models.email_account import EmailAccount
from app.models.subscription import Subscription


PREFIXO = "teste-exportacao-universal-"


@pytest.fixture(autouse=True)
def _limpar_documentos_teste(db):
    db.execute(text("DELETE FROM documents WHERE slug LIKE :prefixo"), {"prefixo": f"{PREFIXO}%"})
    db.commit()
    yield
    db.execute(text("DELETE FROM documents WHERE slug LIKE :prefixo"), {"prefixo": f"{PREFIXO}%"})
    db.commit()


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _assinatura_principal(db, user):
    db.add(Subscription(user_id=user.id, kind="meucardio", plano="basico", status="ativo"))
    db.commit()


def _ativar_corvia_mail(db, user, endereco: str):
    db.add(Subscription(user_id=user.id, kind="email", status="ativo"))
    db.add(EmailAccount(
        user_id=user.id,
        email_address=endereco,
        mail360_account_key=f"mail-key-{user.id}",
        status="ativa",
    ))
    db.commit()


def _documento(db, sufixo: str, *, publicado: bool = True) -> Document:
    doc = Document(
        slug=f"{PREFIXO}{sufixo}",
        title="Insuficiência cardíaca — documento de teste",
        kind="modulo",
        theme="Insuficiência cardíaca",
        summary="Resumo clínico validado para o teste de exportação.",
        body_md="## Conduta\n\nTexto clínico publicado.\n\n## Pontos-chave\n\n- Primeiro ponto\n- Segundo ponto",
        source_refs=["Diretriz de teste 2026"],
        review_status="revisado",
        published=publicado,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


class TestCatalogoEPdf:
    def test_catalogo_encontra_item_e_pdf_e_real(self, client, db, criar_usuario):
        user, token = criar_usuario(email="exportador@teste.local")
        _assinatura_principal(db, user)
        doc = _documento(db, "pdf")

        catalogo = client.get(
            f"/api/exportar/catalogo?tipo=documento&slug={doc.slug}&limite=1",
            headers=_headers(token),
        )
        assert catalogo.status_code == 200, catalogo.text
        assert catalogo.json()["itens"][0]["slug"] == doc.slug

        resposta = client.post(
            "/api/exportar/conteudo",
            headers=_headers(token),
            json={
                "itens": [{"tipo": "documento", "slug": doc.slug}],
                "incluir_dados_assinante": True,
            },
        )
        assert resposta.status_code == 200, resposta.text
        assert resposta.headers["content-type"].startswith("application/pdf")
        assert resposta.content.startswith(b"%PDF")
        assert len(resposta.content) > 1000

    def test_fail_closed_quando_item_nao_esta_publicado(self, client, db, criar_usuario):
        user, token = criar_usuario(email="exportador-retido@teste.local")
        _assinatura_principal(db, user)
        doc = _documento(db, "retido", publicado=False)

        resposta = client.post(
            "/api/exportar/conteudo",
            headers=_headers(token),
            json={"itens": [{"tipo": "documento", "slug": doc.slug}]},
        )
        assert resposta.status_code == 409, resposta.text
        assert doc.slug in resposta.text


class TestCorviaMail:
    def test_status_indisponivel_sem_addon(self, client, db, criar_usuario):
        user, token = criar_usuario(email="sem-mail-export@teste.local")
        _assinatura_principal(db, user)

        resposta = client.get("/api/exportar/corvia-mail", headers=_headers(token))
        assert resposta.status_code == 200, resposta.text
        assert resposta.json()["disponivel"] is False

    def test_gera_anexa_e_envia_pela_caixa_do_assinante(
        self, client, db, criar_usuario, monkeypatch_mail360,
    ):
        user, token = criar_usuario(email="com-mail-export@teste.local")
        _assinatura_principal(db, user)
        _ativar_corvia_mail(db, user, "medico-export@corvia.med.br")
        doc = _documento(db, "email")

        status = client.get("/api/exportar/corvia-mail", headers=_headers(token))
        assert status.status_code == 200, status.text
        assert status.json() == {
            "disponivel": True,
            "motivo": None,
            "email_address": "medico-export@corvia.med.br",
        }

        resposta = client.post(
            "/api/exportar/conteudo/enviar-email",
            headers=_headers(token),
            json={
                "itens": [{"tipo": "documento", "slug": doc.slug}],
                "incluir_dados_assinante": True,
                "para": "destinatario@teste.local",
                "cc": "copia@teste.local",
                "assunto": "Conteúdo para discussão",
                "mensagem": "Segue o PDF selecionado no CorVIA.",
            },
        )
        assert resposta.status_code == 201, resposta.text
        corpo = resposta.json()
        assert corpo["enviado"] is True
        assert corpo["remetente"] == "medico-export@corvia.med.br"
        assert corpo["para"] == "destinatario@teste.local"
        assert corpo["message_id"] == "msg-enviada-1"

        assert len(monkeypatch_mail360["anexos"]) == 1
        account_key, nome, tamanho = monkeypatch_mail360["anexos"][0]
        assert account_key == f"mail-key-{user.id}"
        assert nome.endswith(".pdf")
        assert tamanho > 1000

        assert len(monkeypatch_mail360["mensagens_enviadas"]) == 1
        enviada = monkeypatch_mail360["mensagens_enviadas"][0]
        assert enviada["remetente"] == "medico-export@corvia.med.br"
        assert enviada["para"] == "destinatario@teste.local"
        assert enviada["cc"] == "copia@teste.local"
        assert enviada["anexos"] == ["file-id-1"]

    def test_destinatario_invalido_e_rejeitado_antes_do_envio(
        self, client, db, criar_usuario, monkeypatch_mail360,
    ):
        user, token = criar_usuario(email="mail-invalido-export@teste.local")
        _assinatura_principal(db, user)
        _ativar_corvia_mail(db, user, "medico-invalid@corvia.med.br")
        doc = _documento(db, "email-invalido")

        resposta = client.post(
            "/api/exportar/conteudo/enviar-email",
            headers=_headers(token),
            json={
                "itens": [{"tipo": "documento", "slug": doc.slug}],
                "para": "endereco-invalido",
            },
        )
        assert resposta.status_code == 422, resposta.text
        assert monkeypatch_mail360["anexos"] == []
        assert monkeypatch_mail360["mensagens_enviadas"] == []
