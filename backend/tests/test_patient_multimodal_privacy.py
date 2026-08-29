from pathlib import Path

from app.api.patient_multimodal_ai import _safe_fragment


def test_fragmento_com_identificador_e_omitido_antes_do_provedor():
    value = _safe_fragment("Paciente: João da Silva, telefone 11999998888")
    assert value is not None
    assert "omitido pelo CorVIA" in value
    assert "João" not in value


def test_observacao_local_do_exame_nao_e_usada_como_legenda_externa():
    source = (
        Path(__file__).resolve().parents[1]
        / "app" / "api" / "patient_multimodal_ai.py"
    ).read_text(encoding="utf-8")
    assert "label=_notes(row)" not in source
    assert "label=cardiovascular_exam_assist.EXAM_TYPES[row.exam_type]" in source
