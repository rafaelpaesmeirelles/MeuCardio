"""Trabalho 15 (07/08/2026) — Assistente Clínica × Assistente Pessoal.

`_preparar_por_modo` é o ponto único onde os dois modos divergem
(app/services/rag.py); estes testes cobrem essa função direto, sem
depender de um provedor de IA real (AI_ENABLED=false por padrão em teste —
ver conftest.py). Os testes de rota cobrem o que é da camada HTTP:
validação de `modo`, gravação em `AIConversation.modo`, filtro de
`/ai/conversas`.
"""
from datetime import datetime, timezone

import pytest

from app.core.config import settings
from app.models.rag import AIConversation
from app.models.subscription import Subscription
from app.services import rag
from app.services.rag import PROMPT_FERRAMENTAS, PROMPT_PESSOAL, PROMPT_SISTEMA, _preparar_por_modo


def _sem_chamada_de_embeddings(monkeypatch):
    """`_preparar_contexto` (caminho "clinica") chama a API de embeddings de
    verdade — sem rede neste ambiente de teste, isso derruba com
    `APIConnectionError`. Nenhum teste existente exercitava esse caminho
    antes (achado ao escrever este arquivo); aqui só interessa qual PROMPT/
    ferramentas `_preparar_por_modo` escolhe, não a qualidade da busca —
    substituído por um retorno fixo, sem tocar em `recuperar()`."""
    monkeypatch.setattr(
        rag, "_preparar_contexto",
        lambda db, pergunta, temas: ("[contexto de teste]", [], [], {"rag_ms": 0, "fontes_ms": 0, "trechos": 0, "pubmed": 0}),
    )


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _subscribe(db, user_id: int) -> None:
    db.add(Subscription(user_id=user_id, kind="meucardio", plano="basico", status="ativo"))
    db.commit()


class TestPrepararPorModoUnitario:
    def test_pessoal_pula_rag_e_usa_prompt_pessoal(self, db, criar_usuario):
        user, _ = criar_usuario(email="modo.pessoal.semrag@teste.local")
        prompt, conteudo, fontes, pubmed, metricas, ferramentas, executor = _preparar_por_modo(
            db, "quando é minha próxima consulta?", None, "pessoal", user,
        )
        assert prompt.startswith(PROMPT_PESSOAL)
        assert conteudo == "PERGUNTA:\nquando é minha próxima consulta?"
        assert fontes == []
        assert pubmed == []
        assert metricas["trechos"] == 0
        # Sem instalação nem consentimento (fixture padrão): nenhuma ferramenta.
        assert ferramentas is None
        assert executor is None

    def test_clinica_usa_rag_e_prompt_sistema(self, db, criar_usuario, monkeypatch):
        _sem_chamada_de_embeddings(monkeypatch)
        user, _ = criar_usuario(email="modo.clinica.comrag@teste.local")
        prompt, conteudo, fontes, pubmed, metricas, ferramentas, executor = _preparar_por_modo(
            db, "quais os quatro pilares da ICFEr?", None, "clinica", user,
        )
        assert prompt == PROMPT_SISTEMA
        assert conteudo.startswith("CONTEXTO INSTITUCIONAL:")
        assert "PERGUNTA:\nquais os quatro pilares da ICFEr?" in conteudo
        assert ferramentas is None
        assert executor is None

    def test_pessoal_oferece_ferramentas_quando_instalacao_e_consentimento_liberam(self, db, criar_usuario, monkeypatch):
        monkeypatch.setattr(settings, "ai_assistant_tools_enabled", True)
        user, _ = criar_usuario(email="modo.pessoal.comferramenta@teste.local")
        user.ia_ferramentas_consent_em = datetime.now(timezone.utc)
        db.commit()

        prompt, _, _, _, _, ferramentas, executor = _preparar_por_modo(
            db, "o que eu tenho amanhã na agenda?", None, "pessoal", user,
        )
        assert PROMPT_FERRAMENTAS in prompt
        assert ferramentas is not None
        assert executor is not None

    def test_clinica_nunca_oferece_ferramentas_mesmo_com_instalacao_e_consentimento(self, db, criar_usuario, monkeypatch):
        """A separação em dois modos existe exatamente para isto: mesmo
        médico, mesmo consentimento concedido, mas em Clínica as ferramentas
        de agenda/e-mail nunca são oferecidas — só em Pessoal."""
        _sem_chamada_de_embeddings(monkeypatch)
        monkeypatch.setattr(settings, "ai_assistant_tools_enabled", True)
        user, _ = criar_usuario(email="modo.clinica.semferramenta@teste.local")
        user.ia_ferramentas_consent_em = datetime.now(timezone.utc)
        db.commit()

        prompt, _, _, _, _, ferramentas, executor = _preparar_por_modo(
            db, "o que eu tenho amanhã na agenda?", None, "clinica", user,
        )
        assert prompt == PROMPT_SISTEMA
        assert ferramentas is None
        assert executor is None

    def test_pessoal_sem_consentimento_nao_oferece_ferramentas_mesmo_com_instalacao_ligada(self, db, criar_usuario, monkeypatch):
        monkeypatch.setattr(settings, "ai_assistant_tools_enabled", True)
        user, _ = criar_usuario(email="modo.pessoal.sconsent@teste.local")
        prompt, _, _, _, _, ferramentas, executor = _preparar_por_modo(
            db, "o que eu tenho amanhã?", None, "pessoal", user,
        )
        assert ferramentas is None
        assert executor is None


class TestPrepararPerguntaGravaModo:
    def test_conversa_nova_grava_o_modo_escolhido(self, db, criar_usuario, monkeypatch):
        from app.api.ai import Pergunta, _preparar_pergunta

        monkeypatch.setattr(settings, "ai_enabled", True)
        user, _ = criar_usuario(email="modo.grava.pessoal@teste.local")
        dados = Pergunta(pergunta="o que eu tenho essa semana?", modo="pessoal")
        conv, historico, _ = _preparar_pergunta(dados, db, user)
        assert conv.modo == "pessoal"
        assert historico == []

        db.refresh(conv)
        registrado = db.get(AIConversation, conv.id)
        assert registrado.modo == "pessoal"

    def test_conversa_nova_sem_modo_explicito_e_clinica(self, db, criar_usuario, monkeypatch):
        from app.api.ai import Pergunta, _preparar_pergunta

        monkeypatch.setattr(settings, "ai_enabled", True)
        user, _ = criar_usuario(email="modo.default.clinica@teste.local")
        dados = Pergunta(pergunta="o que é a fração de ejeção?")
        conv, _, _ = _preparar_pergunta(dados, db, user)
        assert conv.modo == "clinica"

    def test_modo_invalido_e_422(self, db, criar_usuario, monkeypatch):
        from fastapi import HTTPException

        from app.api.ai import Pergunta, _preparar_pergunta

        monkeypatch.setattr(settings, "ai_enabled", True)
        user, _ = criar_usuario(email="modo.invalido@teste.local")
        dados = Pergunta(pergunta="pergunta qualquer", modo="nao_existe")
        with pytest.raises(HTTPException) as exc:
            _preparar_pergunta(dados, db, user)
        assert exc.value.status_code == 422


class TestRotaConversasFiltraPorModo:
    def test_lista_so_do_modo_pedido(self, client, criar_usuario, db):
        user, token = criar_usuario(email="modo.rota.filtro@teste.local")
        _subscribe(db, user.id)

        db.add(AIConversation(user_id=user.id, titulo="Pergunta clínica", modo="clinica"))
        db.add(AIConversation(user_id=user.id, titulo="Pergunta de agenda", modo="pessoal"))
        db.commit()

        so_pessoal = client.get("/api/ai/conversas?modo=pessoal", headers=_headers(token))
        assert so_pessoal.status_code == 200
        titulos = [c["titulo"] for c in so_pessoal.json()]
        assert titulos == ["Pergunta de agenda"]

        so_clinica = client.get("/api/ai/conversas?modo=clinica", headers=_headers(token))
        titulos_clinica = [c["titulo"] for c in so_clinica.json()]
        assert titulos_clinica == ["Pergunta clínica"]

    def test_modo_invalido_na_rota_e_422(self, client, criar_usuario, db):
        user, token = criar_usuario(email="modo.rota.invalido@teste.local")
        _subscribe(db, user.id)
        r = client.get("/api/ai/conversas?modo=nao_existe", headers=_headers(token))
        assert r.status_code == 422

    def test_ler_conversa_devolve_o_modo(self, client, criar_usuario, db):
        user, token = criar_usuario(email="modo.rota.detalhe@teste.local")
        _subscribe(db, user.id)
        conv = AIConversation(user_id=user.id, titulo="Teste", modo="pessoal")
        db.add(conv)
        db.commit()
        db.refresh(conv)

        r = client.get(f"/api/ai/conversas/{conv.id}", headers=_headers(token))
        assert r.status_code == 200
        assert r.json()["modo"] == "pessoal"
