from types import SimpleNamespace

import fitz
from PIL import Image

from app.services import material_paciente


def _bloco_com_texto(pagina, trecho: str):
    for bloco in pagina.get_text("blocks"):
        if trecho in bloco[4]:
            return bloco
    raise AssertionError(f"Texto não encontrado no PDF: {trecho}")


def test_capa_reserva_altura_da_identidade_profissional(monkeypatch, tmp_path):
    logo = tmp_path / "logo-profissional-alta.png"
    Image.new("RGBA", (160, 320), (20, 60, 90, 255)).save(logo)
    monkeypatch.setattr(material_paciente, "rendered_logo_png", lambda _url: logo)

    material = SimpleNamespace(
        titulo="Insuficiência cardíaca: como reconhecer sintomas e cuidar da rotina com segurança",
        subtitulo="Informações práticas para o paciente e para a família acompanharem o dia a dia.",
        secoes=[
            {
                "titulo": "O que observar",
                "paragrafos": ["Observe mudanças nos sintomas e converse com sua equipe."],
                "itens": [],
            }
        ],
        sinais_de_alerta=[],
        perguntas=[],
        fontes=[],
    )
    medico = {
        "full_name": "Mariana Aparecida de Albuquerque e Silva",
        "professional_title": "Dra.",
        "council_name": "CRM",
        "council_number": "123456",
        "council_state": "SP",
        "rqe": "654321",
        "document_logo_url": "/logos/logo-profissional-alta.png",
        "include_workplace_on_documents": True,
        "workplace_name": "Instituto de Cardiologia e Medicina Integrada",
        "workplace_department": "Cardiologia clínica",
        "workplace_role": "Responsável técnica",
        "workplace_notes": "",
    }

    pdf = material_paciente.gerar(material, medico)
    documento = fitz.open(stream=pdf, filetype="pdf")
    pagina = documento[0]
    identidade = _bloco_com_texto(pagina, "Mariana Aparecida")
    titulo = _bloco_com_texto(pagina, "Insuficiência cardíaca")

    # Coordenadas do PyMuPDF começam no topo: o título deve iniciar depois do
    # fim do bloco de identificação, com uma folga visual real.
    assert titulo[1] >= identidade[3] + 12
