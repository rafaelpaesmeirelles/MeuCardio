"""Correção coordenada de 03/09/2026, seção "arquitetura de deploy": o tempo
de indisponibilidade do deploy não pode depender do provedor de embeddings, e
não pode existir indexação redundante entre `reconcile_content` e o disparo
do `deploy.sh`. Testes estáticos, mesmo padrão de `test_deploy_rollback_window.py`
(análise posicional do texto do script, sem executar o deploy de verdade)."""

from pathlib import Path

DEPLOY = Path(__file__).resolve().parents[2] / "deploy.sh"


def _fonte() -> str:
    return DEPLOY.read_text(encoding="utf-8")


def _indice_comando_real(fonte: str) -> int:
    """Índice da CHAMADA de fato (`exec -d ... reindex_rag_completo_20260902`),
    não de qualquer menção em comentário/mensagem de aviso."""
    return fonte.index("exec -d backend python -m app.commands.reindex_rag_completo_20260902")


def test_indexacao_rag_roda_depois_do_caddy_reabrir_e_do_rollback_desarmado():
    fonte = _fonte()
    indice_rollback_off = fonte.index("ROLLBACK_NECESSARIO=0")
    indice_caddy_up = fonte.index('"${COMPOSE[@]}" up -d --no-build caddy')
    indice_indexacao = _indice_comando_real(fonte)

    assert indice_rollback_off < indice_indexacao, (
        "A indexação RAG precisa rodar DEPOIS de ROLLBACK_NECESSARIO=0 — "
        "senão uma falha de embedding pode acionar pg_restore de novo."
    )
    assert indice_caddy_up < indice_indexacao, (
        "A indexação RAG precisa rodar DEPOIS do Caddy reabrir — nunca com "
        "tráfego público fechado."
    )


def test_indexacao_rag_e_disparada_em_background_nao_bloqueante():
    fonte = _fonte()
    indice = _indice_comando_real(fonte)
    trecho = fonte[max(0, indice - 60) : indice + 20]
    assert "exec -d" in trecho, (
        "A indexação precisa ser disparada com `exec -d` (background) — o script "
        "não pode ficar preso esperando o backlog inteiro de embeddings terminar "
        "antes de considerar o deploy concluído."
    )


def test_falha_da_indexacao_rag_nao_derruba_o_deploy():
    fonte = _fonte()
    indice = _indice_comando_real(fonte)
    # a chamada precisa estar protegida por `||` (não propaga falha pro
    # `set -Eeuo pipefail` do script) dentro de uma janela pequena depois dela
    janela = fonte[indice : indice + 400]
    assert "||" in janela, (
        "A chamada de indexação RAG precisa ter um `||` de contenção logo em "
        "seguida — sem isso, `set -e` aborta o deploy inteiro (já certificado "
        "e com tráfego aberto) só porque o provedor de embeddings falhou."
    )


def test_nao_ha_segunda_chamada_de_indexacao_redundante_no_deploy():
    """`app.services.indexar` (só cobre `documents`) não pode mais ser
    chamado por deploy.sh — o único responsável por indexação incremental é
    `app.commands.reindex_rag_completo_20260902` (documentos + as 12 frentes
    + calculadoras num só comando, idempotente). A chamada de fato (`exec -d
    ...`) precisa existir uma única vez — comentários/mensagens de aviso
    podem citar o nome do comando mais de uma vez, e isso é esperado."""
    fonte = _fonte()
    assert "app.services.indexar" not in fonte
    import re
    chamadas_reais = re.findall(
        r"exec -d backend python -m app\.commands\.reindex_rag_completo_20260902", fonte,
    )
    assert len(chamadas_reais) == 1


def test_reconcile_content_nao_e_seguido_de_chamada_de_rede_antes_do_readiness():
    """reconcile_content/publish_preserved_content continuam rodando dentro
    da janela crítica (são só Postgres local, rápidos e determinísticos) —
    mas nada de rede externa (embeddings) pode ser intercalado ali."""
    fonte = _fonte()
    inicio = fonte.index("python -m app.commands.reconcile_content --publish-reviewed")
    fim = fonte.index("urllib.request.urlopen('http://localhost:8000/api/ready', timeout=5)")
    trecho = fonte[inicio:fim]
    assert "reindex_rag_completo_20260902" not in trecho
    assert "app.services.indexar" not in trecho
