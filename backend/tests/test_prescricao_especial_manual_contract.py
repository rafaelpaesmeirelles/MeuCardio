from pathlib import Path


def test_manual_tem_estado_terminal_sem_upload_externo():
    source = (Path(__file__).resolve().parents[1] / "app" / "api" / "prescricao_especial.py").read_text(encoding="utf-8")
    assert 'novo_status = "emitida_manual"' in source
    assert '_status(g) != "emitida_manual"' in source
