"""Protege a ordem do snapshot usado pelo rollback automático."""

from pathlib import Path


DEPLOY = Path(__file__).resolve().parents[2] / "deploy.sh"


def test_snapshot_ocorre_depois_do_build_e_da_parada_dos_escritores():
    fonte = DEPLOY.read_text(encoding="utf-8")
    indice_build = fonte.index('"${COMPOSE[@]}" build backend frontend-build')
    indice_stop_caddy = fonte.index("parar_servico_se_existir caddy", indice_build)
    indice_stop_backend = fonte.index("parar_servico_se_existir backend", indice_stop_caddy)
    indice_backup = fonte.index("criar_backup_pre_deploy", indice_stop_backend)
    indice_rollback = fonte.index("ROLLBACK_NECESSARIO=1", indice_backup)
    indice_up = fonte.index(
        '"${COMPOSE[@]}" up -d --no-build --remove-orphans db redis backend frontend-build'
    )

    assert indice_build < indice_stop_caddy < indice_stop_backend
    assert indice_stop_backend < indice_backup < indice_rollback < indice_up
    assert "Todas as requisições aceitas antes da indisponibilidade já terminaram" in fonte
