from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _ler(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_rotas_documentais_usam_identidade_profissional_centralizada():
    for path in (
        "app/api/documents.py",
        "app/api/documentos_publicos.py",
        "app/api/exportacao.py",
        "app/api/receituario.py",
    ):
        source = _ler(path)
        assert "document_identity" in source, path
        assert 'f"Dr. {' not in source, path
        assert 'f"Dr(a). {' not in source, path


def test_todos_os_renderizadores_clinicos_suportam_logo_profissional():
    expected = {
        "app/services/pdf_documento.py": ("logo_path", "_fundo_logo"),
        "app/services/material_paciente.py": ("logo_path", "logo_needs_dark_plate_path"),
        "app/services/receita_controle_especial.py": ("logo_path", "stroke=0"),
        "app/services/apresentacao.py": ("rendered_logo_png", "professional_name"),
    }
    for path, symbols in expected.items():
        source = _ler(path)
        for symbol in symbols:
            assert symbol in source, f"{path}: faltou {symbol}"


def test_forma_de_tratamento_nao_e_inferida_pelo_conselho():
    profile = _ler("app/services/professional_profile.py")
    assert "professional_title" in profile
    assert 'return f"{title} {name}".strip()' in profile


def test_link_publico_preserva_modelo_da_receita_controle_especial():
    source = _ler("app/api/documentos_publicos.py")
    assert 'doc.tipo_codigo == "RCE"' in source
    assert "receita_controle_especial(" in source
    assert 'identidade["cpf"]' in source
    assert "cid=doc.cid" in source


def test_admin_envia_campos_profissionais_para_contas_reais_e_os_omite_no_investidor():
    source = (ROOT.parent / "frontend/src/pages/Admin.tsx").read_text(encoding="utf-8")
    assert 'const investidor = novo.tipo_acesso === "investidor"' in source

    campos_texto = (
        "profession", "council_name", "council_number", "council_state",
        "specialty", "professional_title", "workplace_name",
        "workplace_department", "workplace_role", "workplace_notes",
    )
    for field in campos_texto:
        assert f"{field}: investidor ? null : " in source, field
        assert f"novo.{field}" in source, field

    for field in ("include_workplace_on_documents", "profile_completion_required"):
        assert f"{field}: investidor ? false : novo.{field}" in source, field

    # Investidor mantém a credencial global definida pelo produto. Contas reais
    # não recebem senha escolhida/exibida pelo Admin: nasce uma credencial
    # provisória aleatória e o titular escolhe a própria senha pelo link de uso único.
    assert 'password: investidor ? "CorVIAOS" : senhaProvisoriaAleatoria()' in source
    assert 'role: investidor ? "leitor" : novo.role' in source
    assert 'api.post("/auth/admin/criar-usuario-com-recuperacao"' in source
    assert 'recovery_email: novo.recovery_email.trim().toLowerCase()' in source
    assert 'if (investidor) await api.post("/admin/users", payload)' in source


def test_rce_respeita_opt_in_do_local_de_trabalho():
    source = _ler("app/services/receita_controle_especial.py")
    assert 'include_workplace_on_documents' in source
