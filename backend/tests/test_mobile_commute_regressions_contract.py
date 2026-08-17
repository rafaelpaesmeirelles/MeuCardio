"""Trava as três correções de mobile/deslocamento (PR fix/mobile-commute-regressions).

1. O mapa do Próximo Deslocamento preserva a instância do Google Maps entre
   atualizações de dados — o flicker vinha de recriar ``new google.maps.Map``
   a cada refresh de rota/origem, apagando os tiles por segundos e rebaixando
   tiles/API em todo ciclo.
2. O campo CHEGADA usa o referencial do compromisso (``scheduled_at`` menos o
   buffer de chegada do local), nunca "agora + duração" — que era um segundo
   referencial temporal misturado no mesmo card.
3. O card do Assistente permanece visível na Home MOBILE, na ordem canônica
   (… Seu dia → Assistente → Atualizações). Ocultá-lo é correto apenas no
   desktop (min-width: 901px), onde o rail lateral dedicado existe.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_mapa_preserva_instancia_entre_atualizacoes():
    mapa = (ROOT / "frontend/src/components/MapaDeslocamento.tsx").read_text(encoding="utf-8")
    # Uma única criação de mapa em todo o componente; atualizações redesenham
    # sobre a MESMA instância (refs), nunca reinstanciam.
    assert mapa.count("new google.maps.Map(") == 1
    assert "mapaInstanciaRef" in mapa
    assert "preserva a instância entre atualizações de dados" in mapa
    assert "sobreposicoesRef" in mapa
    # fitBounds só quando a geometria realmente muda — sem "pulos" de viewport.
    assert "assinaturaEnquadramento" in mapa


def test_chegada_usa_referencial_do_compromisso():
    home = (ROOT / "frontend/src/pages/PainelClinicalOS.tsx").read_text(encoding="utf-8")
    assert "new Date(proximo.scheduled_at).getTime() - destino.arrival_buffer_minutes * 60000" in home
    # A fórmula antiga ("updated_at/agora + duração") não pode voltar.
    assert "Date.now()) + rota.duration_seconds" not in home
    # A SAÍDA recomendada preexistente permanece intacta.
    assert "rota.duration_seconds + destino.arrival_buffer_minutes * 60" in home


def test_assistente_visivel_na_home_mobile_na_ordem_canonica():
    board = (ROOT / "frontend/src/styles/clinical-reference-board-final.css").read_text(encoding="utf-8")
    fidelity = (ROOT / "frontend/src/styles/clinical-reference-fidelity-release.css").read_text(encoding="utf-8")
    # Nenhuma LINHA pode ocultar o card do Assistente (a regra desktop legítima
    # oculta via seletor em linha própria, sem display na mesma linha).
    for nome, css in (("board-final", board), ("fidelity-release", fidelity)):
        for linha in css.splitlines():
            if "display: none" in linha and ("assistant-summary" in linha or "card--assistant" in linha):
                raise AssertionError(f"card do Assistente oculto indevidamente em {nome}: {linha.strip()}")
    # Ordem canônica do mobile: Deslocamento(1) → Seu dia(2) → Assistente(3) → Atualizações(4).
    assert ".ccc-reference-summary > .ccc-reference-assistant-summary { order: 3; }" in board
    assert ".ccc-reference-summary > .ccc-reference-updates-summary { order: 4; }" in board


def test_parent_nao_recria_referencias_identicas():
    home = (ROOT / "frontend/src/pages/PainelClinicalOS.tsx").read_text(encoding="utf-8")
    # Guardas de identidade: origem e alvo só trocam de referência quando o
    # conteúdo muda — evita invalidar deps e redesenhar o mapa à toa.
    assert "atual.latitude === origemAtual.latitude" in home
    assert "JSON.stringify(atual) === JSON.stringify(resultado.destination)" in home
