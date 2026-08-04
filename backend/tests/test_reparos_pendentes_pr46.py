import re
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

from app.services.receita_controle_especial import (
    receita_controle_especial,
    validar_requisitos_rce,
)

ROOT = Path(__file__).resolve().parents[2]


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
        include_workplace_on_documents=True,
    )
    base.update(overrides)
    return SimpleNamespace(**base)


def _endereco():
    return {
        "logradouro": "Rua das Flores",
        "numero": "10",
        "complemento": None,
        "bairro": "Centro",
        "cidade": "Ribeirão Preto",
        "uf": "SP",
        "cep": "14000-000",
        "telefone": "1630000000",
    }


def _item(indice: int) -> dict:
    return {
        "descricao": f"Medicamento controlado número {indice} com descrição clínica extensa",
        "apresentacao": "20 mg comprimidos revestidos",
        "quantidade": "60 comprimidos (sessenta comprimidos)",
        "posologia": "Tomar um comprimido por via oral à noite, conforme orientação médica.",
        "lista": "C1" if indice <= 3 else "C2",
    }


def test_rce_paginação_explícita_não_trunca_itens():
    itens = [_item(i) for i in range(1, 14)]
    pdf = receita_controle_especial(
        destinatario={
            "nome": "Paciente Teste",
            "documento": "12345678900",
            "endereco": "Rua A, 1",
        },
        itens=itens,
        observacoes="Prescrição paginada sem exclusão de itens.",
        medico=_medico(),
        endereco_profissional=_endereco(),
        data_emissao=datetime(2026, 8, 4, tzinfo=timezone.utc),
    )
    paginas = len(re.findall(rb"/Type\s*/Page\b", pdf))
    assert paginas > 4
    assert paginas % 4 == 0

    fonte = (ROOT / "backend/app/services/receita_controle_especial.py").read_text(encoding="utf-8")
    assert "itens[:12]" not in fonte
    assert "PÁGINA" in fonte
    assert "CONTINUAÇÃO" in fonte


def test_rce_exige_conselho_numero_e_uf_completos():
    erros = validar_requisitos_rce(
        medico=_medico(council_number=None, council_state=None, crm=None),
        destinatario={"nome": "Paciente", "documento": "123", "endereco": "Rua A, 1"},
        itens=[_item(1)],
        endereco_profissional=_endereco(),
        cid=None,
    )
    assert any("número" in erro.lower() and "uf" in erro.lower() for erro in erros)


def test_primeiro_acesso_não_pode_ser_liberado_por_patch_incompleto():
    fonte = (ROOT / "backend/app/api/auth.py").read_text(encoding="utf-8")
    assert "user.profile_completion_required = False" not in fonte
    assert "profile_completion_required" in fonte
    assert "council_number" in fonte
    assert "council_state" in fonte
    assert "profession" in fonte


def test_frontend_exibe_detalhes_estruturados_da_api():
    fonte = (ROOT / "frontend/src/lib/api.ts").read_text(encoding="utf-8")
    assert "detail.erro" in fonte or "detail?.erro" in fonte
    assert "detail.campos" in fonte or "detail?.campos" in fonte
    assert "detail.bloqueios" in fonte or "detail?.bloqueios" in fonte
    assert "detail.itens" in fonte or "detail?.itens" in fonte


def test_históricos_são_paginados_após_filtrar_todo_o_acervo_do_usuário():
    receituario = (ROOT / "backend/app/api/receituario.py").read_text(encoding="utf-8")
    documentos = (ROOT / "backend/app/api/documents.py").read_text(encoding="utf-8")
    for fonte in (receituario, documentos):
        assert ".limit(500)" not in fonte
        assert "page_size" in fonte
        assert "page" in fonte
        assert "has_more" in fonte


def test_existe_uma_só_regra_do_atalho_explícito_de_emergência():
    shell = (ROOT / "frontend/src/styles/shell.css").read_text(encoding="utf-8")
    emergencia = (ROOT / "frontend/src/styles/emergencia.css").read_text(encoding="utf-8")
    assert ".emerg-atalho {" not in shell
    assert emergencia.count(".emerg-atalho {") == 1
    assert "padding: 0.8rem 1.15rem" in emergencia
    assert "border-radius: 999px" in emergencia


def test_apresentação_comercial_escolhida_é_o_texto_prescrito_e_impresso():
    frontend = (ROOT / "frontend/src/pages/Receituario.tsx").read_text(encoding="utf-8")
    backend = (ROOT / "backend/app/api/receituario.py").read_text(encoding="utf-8")

    # Ao selecionar, o item deve assumir exatamente o produto e a apresentação
    # escolhidos, em vez de manter a descrição genérica ou uma dose anterior.
    assert "descricao: ap.produto" in frontend
    assert "apresentacao: ap.apresentacao" in frontend
    assert "apresentacao: it.apresentacao || ap.apresentacao" not in frontend

    # Defesa no backend para clientes antigos: a marca explícita prevalece no
    # texto da prescrição, mas a substância genérica continua sendo usada apenas
    # para classificação regulatória do tipo de receituário.
    assert "i.brand_name or i.descricao" in backend
    assert "substancia = d.generic_name" in backend
