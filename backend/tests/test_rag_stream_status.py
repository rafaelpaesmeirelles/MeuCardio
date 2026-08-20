from app.services import rag
from app.services.ia.provedor import Resposta


def test_stream_encaminha_status_de_tool_sem_tratar_como_final(monkeypatch):
    class ProvedorFalso:
        def responder_stream(self, *_args, **_kwargs):
            yield {"status": "Consultando agenda plano do dia…"}
            yield {"delta": "Seu plano "}
            yield {"final": Resposta(
                texto="Seu plano está pronto.",
                tokens_entrada=12,
                tokens_saida=8,
                modelo="claude-sonnet-5",
            )}

    monkeypatch.setattr(
        rag,
        "_preparar_por_modo",
        lambda *_args, **_kwargs: (
            "sistema", "PERGUNTA:\nplano", [], [],
            {"rag_ms": 0, "fontes_ms": 0, "trechos": 0, "pubmed": 0},
            [{"name": "agenda_plano_do_dia"}], lambda *_a: {},
        ),
    )
    monkeypatch.setattr(rag, "obter_provedor", lambda: ProvedorFalso())

    eventos = list(rag.perguntar_stream(
        db=None,
        pergunta="Mostre meu plano de trabalho dos próximos 7 dias.",
        historico=[],
        modo="pessoal",
        user=object(),
    ))

    assert eventos[0] == {"status": "Preparando a resposta…"}
    assert eventos[1] == {"status": "Consultando agenda plano do dia…"}
    assert eventos[2] == {"delta": "Seu plano "}
    assert eventos[3]["final"]["texto"] == "Seu plano está pronto."
    assert eventos[3]["final"]["modelo"] == "claude-sonnet-5"
