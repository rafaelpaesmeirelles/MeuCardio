from datetime import datetime, timezone
from io import BytesIO
from types import SimpleNamespace

from pypdf import PdfReader

from app.services.receita_controle_especial import (
    MODELO_VERSAO,
    receita_controle_especial,
    validar_requisitos_rce,
)


def _medico(**overrides):
    base = dict(
        full_name="Rafael Paes Meirelles",
        professional_title="Dr.",
        council_name="CRM",
        council_number="138266",
        council_state="SP",
        crm=None,
        cpf="30389435848",
        document_logo_url=None,
        workplace_name="Clínica Corvia",
    )
    base.update(overrides)
    return SimpleNamespace(**base)


def _endereco():
    return {
        "logradouro": "Rua das Flores", "numero": "10", "complemento": None,
        "bairro": "Centro", "cidade": "Ribeirão Preto", "uf": "SP",
        "cep": "14000-000", "telefone": "1630000000",
    }


def test_rce_gera_duas_vias_com_frente_e_verso():
    pdf = receita_controle_especial(
        destinatario={"nome": "Paciente Teste", "documento": "12345678900", "endereco": "Rua A, 1"},
        itens=[{"descricao": "Medicamento controlado", "apresentacao": "20 mg", "posologia": "Tomar 1 comprimido à noite", "lista": "C1"}],
        observacoes="Uso conforme orientação.",
        medico=_medico(), endereco_profissional=_endereco(),
        data_emissao=datetime(2026, 8, 4, tzinfo=timezone.utc),
    )
    assert pdf.startswith(b"%PDF")
    assert pdf.rstrip().endswith(b"%%EOF")
    leitor = PdfReader(BytesIO(pdf))
    assert len(leitor.pages) == 4
    texto = "\n".join((pagina.extract_text() or "") for pagina in leitor.pages)
    assert "RECEITA DE CONTROLE ESPECIAL" in texto
    assert "1ª via - Retenção pela Farmácia" in texto
    assert "2ª via - Paciente" in texto
    assert MODELO_VERSAO in texto


def test_c5_exige_medico_ou_dentista_e_campos_da_lei_9965():
    erros = validar_requisitos_rce(
        medico=_medico(council_name="CRBM", cpf=None),
        destinatario={"nome": "Paciente Teste", "documento": "123", "endereco": ""},
        itens=[{"descricao": "Anabolizante", "lista": "C5"}],
        endereco_profissional=None,
        cid=None,
    )
    mensagem = " | ".join(erros)
    assert "CRM/CRO" in mensagem
    assert "CPF do prescritor" in mensagem
    assert "endereço completo do paciente" in mensagem
    assert "CID" in mensagem
    assert "endereço profissional" in mensagem
    assert "telefone profissional" in mensagem


def test_c5_completo_gera_pdf_com_cid_e_cpf_prescritor():
    pdf = receita_controle_especial(
        destinatario={"nome": "Paciente Teste", "documento": "12345678900", "endereco": "Rua A, 1"},
        itens=[{"descricao": "Testosterona", "apresentacao": "100 mg", "posologia": "Uso conforme prescrição", "lista": "C5"}],
        observacoes="",
        medico=_medico(), endereco_profissional=_endereco(),
        data_emissao=datetime(2026, 8, 4, tzinfo=timezone.utc), cid="E29.1",
    )
    texto = "\n".join((pagina.extract_text() or "") for pagina in PdfReader(BytesIO(pdf)).pages)
    assert "LISTA C5" in texto
    assert "E29.1" in texto
    assert "30389435848" in texto
    assert "cinco anos" in texto
