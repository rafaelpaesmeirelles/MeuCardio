"""Protege a janela de rollback do deploy em duas fases."""

from pathlib import Path


DEPLOY = Path(__file__).resolve().parents[2] / "deploy.sh"


def test_rollback_permanece_armado_ate_readiness_e_checkout_imutavel():
    fonte = DEPLOY.read_text(encoding="utf-8")
    indice_up_backend = fonte.index(
        '"${COMPOSE[@]}" up -d --no-build --remove-orphans db redis backend frontend-build'
    )
    indice_rollback_on = fonte.rfind("ROLLBACK_NECESSARIO=1", 0, indice_up_backend)
    indice_reconcile = fonte.index("python -m app.commands.reconcile_content --publish-reviewed")
    indice_ready_final = fonte.index(
        "urllib.request.urlopen('http://localhost:8000/api/ready', timeout=5)",
        indice_reconcile,
    )
    indice_checkout_final = fonte.index("validar_checkout_imutavel", indice_ready_final)
    indice_rollback_off = fonte.index("ROLLBACK_NECESSARIO=0", indice_checkout_final)
    indice_caddy = fonte.index('"${COMPOSE[@]}" up -d --no-build caddy')

    assert indice_rollback_on < indice_up_backend
    assert indice_up_backend < indice_reconcile < indice_ready_final
    assert indice_ready_final < indice_checkout_final < indice_rollback_off < indice_caddy
