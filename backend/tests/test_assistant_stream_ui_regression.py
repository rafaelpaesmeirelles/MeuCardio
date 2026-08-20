"""Regressões focadas do Assistente: layout dinâmico e SSE resiliente."""

from pathlib import Path
from queue import Queue
from threading import Thread
from time import sleep

from app.api.ai import _eventos_sse_da_fila


ROOT = Path(__file__).resolve().parents[2]


def test_sse_emite_keepalive_enquanto_provedor_nao_produz_eventos():
    fila = Queue()
    fim = object()

    def encerrar():
        sleep(0.03)
        fila.put(fim)

    Thread(target=encerrar, daemon=True).start()
    eventos = _eventos_sse_da_fila(fila, fim, heartbeat_seconds=0.005)

    assert next(eventos) == ": keep-alive\n\n"
    for evento in eventos:
        assert evento == ": keep-alive\n\n"


def test_sse_preserva_contrato_json_e_finaliza_no_marcador():
    fila = Queue()
    fim = object()
    fila.put({"tipo": "status", "etapa": "Preparando…"})
    fila.put(fim)

    assert list(_eventos_sse_da_fila(fila, fim, heartbeat_seconds=0.005)) == [
        'data: {"tipo": "status", "etapa": "Preparando…"}\n\n'
    ]


def test_layout_nao_depende_da_quantidade_de_blocos_condicionais():
    css = (ROOT / "frontend/src/styles/clinical-assistant-command.css").read_text()
    pagina = (ROOT / "frontend/src/pages/Assistente.tsx").read_text()

    assert "display:flex; flex-direction:column" in css
    assert "grid-template-rows" not in css
    assert "flex:1 1 auto" in css
    assert "conversaRef.current" in pagina
    assert ".scrollTo(" in pagina
    assert "scrollIntoView" not in pagina


def test_usuario_pode_interromper_espera_sem_repetir_acao_as_cegas():
    pagina = (ROOT / "frontend/src/pages/Assistente.tsx").read_text()
    api = (ROOT / "frontend/src/lib/api.ts").read_text()

    assert "new AbortController()" in pagina
    assert 'pensando ? "Cancelar" : "Enviar"' in pagina
    assert "confira a Agenda antes de repetir" in pagina
    assert "signal?: AbortSignal" in api
    assert "signal," in api
