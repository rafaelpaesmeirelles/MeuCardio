"""Regressão do Assistente Pessoal v2 — automação de rotina sem ids internos.

Os testes são de domínio/tool-calling e não dependem de Anthropic, Google,
Mapbox ou Mail360 reais. O objetivo é provar as invariantes que corrigem a
experiência reportada: endereço -> local/rota, recorrência nativa e envio de
e-mail somente após pedido explícito.
"""
from datetime import date

from app.models.agenda import AvailabilityRule, CalendarCommitmentSeries, CalendarLocation
from app.models.audit import AuditLog
from app.services.ia import assistant_automation_tools as automation
from app.services.ia.assistant_tools import ASSISTANT_TOOLS_SCHEMA, executar_tool_assistente


def _nomes_tools() -> set[str]:
    return {item["name"] for item in ASSISTANT_TOOLS_SCHEMA}


def _geo_falso(endereco: str) -> dict:
    assert endereco
    return {
        "provider": "teste_geocoding",
        "formatted_address": "Rua Teste, 100 - Ribeirão Preto - SP",
        "latitude": -21.1775,
        "longitude": -47.8103,
    }


class TestCatalogoAssistentePessoalV2:
    def test_catalogo_expoe_tools_intuitivas(self):
        nomes = _nomes_tools()
        assert {
            "agenda_listar_locais",
            "agenda_resolver_local",
            "agenda_criar_compromisso_inteligente",
            "agenda_criar_rotina_semanal",
            "agenda_criar_compromisso_recorrente",
            "mail_listar_contas_envio",
            "mail_enviar_mensagem",
            "mail_responder_mensagem",
        }.issubset(nomes)


class TestResolucaoAutomaticaDeLocal:
    def test_endereco_cria_local_geocodificado_sem_location_id(
        self, db, criar_usuario, monkeypatch,
    ):
        user, _ = criar_usuario(email="assistente.local.auto@teste.local")
        monkeypatch.setattr(automation, "geocode_address", _geo_falso)

        resultado = executar_tool_assistente(
            "agenda_resolver_local",
            {
                "local_nome": "Consultório Teste",
                "endereco": "Rua Teste, 100, Ribeirão Preto - SP",
                "criar_se_ausente": True,
            },
            db,
            user,
        )

        assert resultado["resolvido"] is True
        assert resultado["local"]["rota_pronta"] is True
        local = db.query(CalendarLocation).filter_by(owner_id=user.id).one()
        assert local.name == "Consultório Teste"
        assert local.latitude == -21.1775
        assert local.longitude == -47.8103
        assert local.address["geocoding_provider"] == "teste_geocoding"

    def test_local_existente_sem_coordenadas_e_completado_automaticamente(
        self, db, criar_usuario, monkeypatch,
    ):
        user, _ = criar_usuario(email="assistente.local.backfill@teste.local")
        local = CalendarLocation(
            owner_id=user.id,
            name="Hospital Teste",
            address={"formatted": "Rua Teste, 100, Ribeirão Preto - SP"},
            latitude=None,
            longitude=None,
        )
        db.add(local)
        db.commit()
        monkeypatch.setattr(automation, "geocode_address", _geo_falso)

        resultado = executar_tool_assistente(
            "agenda_resolver_local",
            {"local_nome": "Hospital Teste"},
            db,
            user,
        )

        assert resultado["local"]["id"] == local.id
        assert resultado["local"]["rota_pronta"] is True
        db.refresh(local)
        assert local.latitude == -21.1775
        assert local.longitude == -47.8103


class TestRecorrenciaNativa:
    def test_rotina_semanal_sem_data_final_nao_materializa_n_semanas(
        self, db, criar_usuario, monkeypatch,
    ):
        user, _ = criar_usuario(email="assistente.rotina.semanal@teste.local")
        monkeypatch.setattr(automation, "geocode_address", _geo_falso)

        resultado = executar_tool_assistente(
            "agenda_criar_rotina_semanal",
            {
                "dias_semana": ["segunda"],
                "hora_inicio": "10:00",
                "hora_fim": "12:00",
                "titulo": "Hospital — Enfermaria",
                "local_nome": "Hospital Teste",
                "endereco": "Rua Teste, 100, Ribeirão Preto - SP",
            },
            db,
            user,
        )

        assert resultado["criado"] is True
        assert resultado["sem_data_final"] is True
        assert resultado["rota_pronta"] is True
        regras = db.query(AvailabilityRule).filter_by(owner_id=user.id).all()
        assert len(regras) == 1
        assert regras[0].weekday == 0
        assert regras[0].valid_until is None
        assert regras[0].label == "Hospital — Enfermaria"

    def test_serie_semanal_sem_data_final_e_uma_unica_entidade_recorrente(
        self, db, criar_usuario,
    ):
        user, _ = criar_usuario(email="assistente.serie.semanal@teste.local")

        resultado = executar_tool_assistente(
            "agenda_criar_compromisso_recorrente",
            {
                "titulo": "Reunião da Residência",
                "categoria": "reuniao",
                "data_inicio": date.today().isoformat(),
                "hora_inicio": "19:00",
                "duracao_minutos": 90,
                "recorrencia": "weekly",
                "dias_semana": ["segunda"],
            },
            db,
            user,
        )

        assert resultado["criado"] is True
        assert resultado["sem_data_final"] is True
        series = db.query(CalendarCommitmentSeries).filter_by(owner_id=user.id).all()
        assert len(series) == 1
        assert series[0].recurrence == "weekly"
        assert series[0].weekdays == [0]
        assert series[0].ends_on is None


class TestCorviaMailComConfirmacaoExplicita:
    def test_enviar_sem_ordem_explicita_nao_toca_provedor(self, db, criar_usuario):
        user, _ = criar_usuario(email="assistente.mail.semenvio@teste.local")

        resultado = executar_tool_assistente(
            "mail_enviar_mensagem",
            {
                "para": "destino@example.com",
                "assunto": "Teste",
                "corpo": "Não deve sair.",
                "confirmacao_usuario": False,
            },
            db,
            user,
        )

        assert resultado["erro"] == "confirmacao_necessaria"
        log = db.query(AuditLog).filter(
            AuditLog.user_id == user.id,
            AuditLog.action == "ia_tool_mail_enviar_mensagem",
        ).one()
        assert log.detail["sucesso"] is False
        # PII/conteúdo da mensagem não entra no AuditLog central.
        assert "para" not in log.detail["argumentos"]
        assert "assunto" not in log.detail["argumentos"]
        assert "corpo" not in log.detail["argumentos"]

    def test_resposta_sem_ordem_explicita_tambem_e_fail_closed(self, db, criar_usuario):
        user, _ = criar_usuario(email="assistente.mail.semreply@teste.local")
        resultado = executar_tool_assistente(
            "mail_responder_mensagem",
            {
                "message_id": "msg-123",
                "assunto": "Re: teste",
                "corpo": "Rascunho apenas.",
                "acao": "reply",
                "confirmacao_usuario": False,
            },
            db,
            user,
        )
        assert resultado["erro"] == "confirmacao_necessaria"
