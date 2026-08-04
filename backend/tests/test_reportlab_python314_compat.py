"""Protege a atualização do ReportLab e os dois renderizadores clínicos centrais."""

from datetime import datetime
from importlib.metadata import version
from pathlib import Path
import subprocess
import sys
from zoneinfo import ZoneInfo

from app.services.pdf_documento import documento_generico, receituario_comum


BACKEND_ROOT = Path(__file__).resolve().parents[1]
EMITIDO_EM = datetime(2026, 8, 3, 22, 0, tzinfo=ZoneInfo("America/Sao_Paulo"))
MEDICO = {
    "full_name": "Rafael Paes Meirelles",
    "council_name": "CRM",
    "council_state": "SP",
    "council_number": "138266",
    "rqe": "134798",
    "specialty": "Cardiologia",
}
ENDERECO = {
    "logradouro": "Rua de Teste",
    "numero": "100",
    "bairro": "Centro",
    "cidade": "Ribeirão Preto",
    "uf": "SP",
    "cep": "14000-000",
    "telefone": "(16) 0000-0000",
}


def _assert_pdf_valido(pdf: bytes) -> None:
    assert isinstance(pdf, bytes)
    assert pdf.startswith(b"%PDF-")
    assert b"%%EOF" in pdf[-64:]
    assert len(pdf) > 1_000


def test_reportlab_permanece_na_linha_4_certificada():
    assert version("reportlab") == "4.4.10"


def test_import_reportlab_nao_emite_warning_ast_nameconstant():
    resultado = subprocess.run(
        [
            sys.executable,
            "-W",
            "error::DeprecationWarning",
            "-c",
            "import reportlab.lib.rl_safe_eval",
        ],
        cwd=BACKEND_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert resultado.returncode == 0, resultado.stderr
    assert "NameConstant" not in resultado.stderr


def test_receituario_comum_continua_gerando_pdf_valido():
    pdf = receituario_comum(
        destinatario={"nome": "Paciente de Teste", "endereco": "Ribeirão Preto/SP"},
        itens=[{
            "substancia": "Losartana potássica",
            "apresentacao": "50 mg — comprimidos",
            "posologia": "Tomar 1 comprimido por via oral a cada 12 horas.",
        }],
        medico=MEDICO,
        data_emissao=EMITIDO_EM,
        observacoes="Uso contínuo.",
        endereco=ENDERECO,
    )

    _assert_pdf_valido(pdf)


def test_documento_generico_continua_gerando_pdf_valido():
    pdf = documento_generico(
        titulo="Atestado médico",
        corpo=(
            "Atesto, para os devidos fins, que o paciente foi avaliado nesta data.\n\n"
            "Documento de regressão do renderizador clínico."
        ),
        medico=MEDICO,
        data_emissao=EMITIDO_EM,
        endereco=ENDERECO,
    )

    _assert_pdf_valido(pdf)
