from pathlib import Path


def test_main_registra_barreira_contra_bypass_generico():
    source = (Path(__file__).resolve().parents[1] / "app" / "main.py").read_text(encoding="utf-8")
    assert "PrescricaoEspecialIsolationMiddleware" in source
