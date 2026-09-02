"""Regressão (Parte L da correção coordenada de 02/09/2026): DASI, AUB-HAS2 e
VSG-CRI (PERIOPERATIVE_REGISTRY) precisam estar em `calculators.REGISTRY`
mesmo quando só `app.services.knowledge_graph` é importado — sem passar por
`app.api.calculators`, que é o caminho que o reconciliador do grafo de
conhecimento (`reconcile_content.py`) realmente usa.

Causa-raiz do bug original: o merge de PERIOPERATIVE_REGISTRY só acontecia
como efeito colateral de `app/api/calculators.py` (o router HTTP), nunca em
`app/services/__init__.py`. `reconcile_content.py` importa só `app.services.*`,
então nunca via essas 3 calculadoras — o backfill do grafo as arquivava a
cada rodada, achando que tinham sido removidas do registro."""

from app.services import calculators as calc


PERIOPERATIVE_LEGADAS = {"dasi", "aub-has2", "vsg-cri"}


def test_registry_completo_sem_importar_app_api_calculators():
    # Nenhum `import app.api.calculators` neste teste, de propósito — é
    # exatamente o cenário que expunha o bug (reconcile_content.py não
    # importa esse módulo).
    assert PERIOPERATIVE_LEGADAS.issubset(calc.REGISTRY.keys())


def test_calculadoras_perioperatorias_legadas_nao_ganham_fonte_chatgpt_indevida():
    # Provêm de antes da leva "chatgpt" (arquivo sem sufixo _chatgpt) — não
    # devem ganhar `fonte_producao="chatgpt"`, ao contrário das irmãs
    # perioperatórias mais novas (frailty/geriatria/mortalidade/sort).
    for slug in PERIOPERATIVE_LEGADAS:
        calculadora = calc.REGISTRY[slug]
        assert getattr(calculadora, "fonte_producao", None) is None
