import re
from datetime import datetime, timezone
from types import SimpleNamespace

from app.services.receita_controle_especial import (
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
        itens=[{"descricao": "Medicamento controlado", "apresentacao": "20 mg", "quantidade": "60 comprimidos (sessenta comprimidos)", "posologia": "Tomar 1 comprimido à noite", "lista": "C1"}],
        observacoes="Uso conforme orientação.",
        medico=_medico(), endereco_profissional=_endereco(),
        data_emissao=datetime(2026, 8, 4, tzinfo=timezone.utc),
    )
    assert pdf.startswith(b"%PDF")
    assert pdf.rstrip().endswith(b"%%EOF")
    assert len(re.findall(rb"/Type\s*/Page\b", pdf)) == 4


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


def test_c5_completo_gera_pdf_sem_bloqueios():
    medico = _medico()
    destinatario = {"nome": "Paciente Teste", "documento": "12345678900", "endereco": "Rua A, 1"}
    itens = [{"descricao": "Testosterona", "apresentacao": "100 mg", "quantidade": "10 ampolas (dez ampolas)", "posologia": "Uso conforme prescrição", "lista": "C5"}]
    assert validar_requisitos_rce(
        medico=medico, destinatario=destinatario, itens=itens,
        endereco_profissional=_endereco(), cid="E29.1",
    ) == []
    pdf = receita_controle_especial(
        destinatario=destinatario, itens=itens, observacoes="",
        medico=medico, endereco_profissional=_endereco(),
        data_emissao=datetime(2026, 8, 4, tzinfo=timezone.utc), cid="E29.1",
    )
    assert pdf.startswith(b"%PDF")
    assert pdf.rstrip().endswith(b"%%EOF")
    assert len(re.findall(rb"/Type\s*/Page\b", pdf)) == 4


def test_rce_recusa_quantidade_sem_algarismos_e_extenso():
    erros = validar_requisitos_rce(
        medico=_medico(),
        destinatario={"nome": "Paciente", "documento": "123", "endereco": "Rua A, 1"},
        itens=[{"descricao": "Controlado", "quantidade": "60 comprimidos", "lista": "C1"}],
        endereco_profissional=_endereco(), cid=None,
    )
    assert any("algarismos e por extenso" in erro for erro in erros)


def test_uso_continuo_nao_remove_quantidade_obrigatoria_da_rce():
    erros = validar_requisitos_rce(
        medico=_medico(),
        destinatario={"nome": "Paciente", "documento": "123", "endereco": "Rua A, 1"},
        itens=[{"descricao": "Controlado", "uso_continuo": True, "lista": "C1"}],
        endereco_profissional=_endereco(), cid=None,
    )
    assert any("Uso contínuo não dispensa" in erro for erro in erros)
    assert any("algarismos e por extenso" in erro for erro in erros)


def test_rce_recusa_mais_de_tres_substancias_c1():
    itens = [
        {"descricao": f"Controlado {i}", "quantidade": "10 comprimidos (dez comprimidos)", "lista": "C1"}
        for i in range(4)
    ]
    erros = validar_requisitos_rce(
        medico=_medico(),
        destinatario={"nome": "Paciente", "documento": "123", "endereco": "Rua A, 1"},
        itens=itens, endereco_profissional=_endereco(), cid=None,
    )
    assert any("no máximo três substâncias" in erro for erro in erros)


def test_rce_recusa_endereco_profissional_parcial():
    endereco_parcial = {"logradouro": "Rua das Flores", "numero": "", "cidade": "", "uf": ""}
    erros = validar_requisitos_rce(
        medico=_medico(),
        destinatario={"nome": "Paciente", "documento": "123", "endereco": "Rua A, 1"},
        itens=[{
            "descricao": "Controlado", "quantidade": "10 comprimidos (dez comprimidos)",
            "lista": "C1",
        }],
        endereco_profissional=endereco_parcial,
        cid=None,
    )
    assert any("logradouro, número, município e UF" in erro for erro in erros)
