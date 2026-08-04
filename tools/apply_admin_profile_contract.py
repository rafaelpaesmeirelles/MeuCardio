#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: str, old: str, new: str) -> None:
    file = ROOT / path
    source = file.read_text(encoding="utf-8")
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"{path}: trecho encontrado {count} vezes: {old[:100]!r}")
    file.write_text(source.replace(old, new, 1), encoding="utf-8")


replace_once(
    "frontend/src/pages/Admin.tsx",
    '''    workplace_name: "", workplace_department: "", workplace_role: "", workplace_notes: "",
    include_workplace_on_documents: false, role: "medico", password: "",
''',
    '''    workplace_name: "", workplace_department: "", workplace_role: "", workplace_notes: "",
    include_workplace_on_documents: false, profile_completion_required: false,
    role: "medico", password: "",
''',
)
replace_once(
    "frontend/src/pages/Admin.tsx",
    '''        crm: novo.crm.trim() || null,
        role: novo.role,
        password: novo.password,
''',
    '''        crm: novo.crm.trim() || null,
        profession: novo.profession.trim() || null,
        council_name: novo.council_name || null,
        council_number: novo.council_number.trim() || null,
        council_state: novo.council_state || null,
        specialty: novo.specialty.trim() || null,
        professional_title: novo.professional_title || null,
        workplace_name: novo.workplace_name.trim() || null,
        workplace_department: novo.workplace_department.trim() || null,
        workplace_role: novo.workplace_role.trim() || null,
        workplace_notes: novo.workplace_notes.trim() || null,
        include_workplace_on_documents: novo.include_workplace_on_documents,
        profile_completion_required: novo.profile_completion_required,
        role: novo.role,
        password: novo.password,
''',
)
replace_once(
    "frontend/src/pages/Admin.tsx",
    '''        workplace_name: "", workplace_department: "", workplace_role: "", workplace_notes: "",
        include_workplace_on_documents: false, role: "medico", password: "" });
''',
    '''        workplace_name: "", workplace_department: "", workplace_role: "", workplace_notes: "",
        include_workplace_on_documents: false, profile_completion_required: false,
        role: "medico", password: "" });
''',
)
replace_once(
    "frontend/src/pages/Admin.tsx",
    '''              Incluir local de trabalho nos documentos
            </label>
            <div style={{ marginTop: "0.9rem" }}>
''',
    '''              Incluir local de trabalho nos documentos
            </label>
            <label style={{ display: "flex", gap: 8, alignItems: "center", fontWeight: 400, marginTop: 8 }}>
              <input type="checkbox" style={{ width: "auto" }} checked={novo.profile_completion_required}
                     onChange={(e) => setNovo({ ...novo, profile_completion_required: e.target.checked })} />
              No primeiro acesso, direcionar para completar dados pessoais e profissionais
            </label>
            <div style={{ marginTop: "0.9rem" }}>
''',
)

# O local de trabalho é opt-in em todos os documentos; a identificação e o
# endereço profissional obrigatórios da RCE continuam independentes dessa opção.
replace_once(
    "backend/app/services/receita_controle_especial.py",
    '''    instituicao = _texto(_valor(medico, "workplace_name"))
    if instituicao:
''',
    '''    instituicao = (
        _texto(_valor(medico, "workplace_name"))
        if bool(_valor(medico, "include_workplace_on_documents")) else ""
    )
    if instituicao:
''',
)

# Gate de contrato entre o formulário administrativo e a API.
test = ROOT / "backend/tests/test_identidade_documentos_audit.py"
with test.open("a", encoding="utf-8") as handle:
    handle.write('''\n\ndef test_admin_envia_todos_os_campos_profissionais_ao_backend():
    source = (ROOT.parent / "frontend/src/pages/Admin.tsx").read_text(encoding="utf-8")
    for field in (
        "profession", "council_name", "council_number", "council_state",
        "specialty", "professional_title", "workplace_name",
        "workplace_department", "workplace_role", "workplace_notes",
        "include_workplace_on_documents", "profile_completion_required",
    ):
        assert f"{field}: novo.{field}" in source, field


def test_rce_respeita_opt_in_do_local_de_trabalho():
    source = _ler("app/services/receita_controle_especial.py")
    assert 'include_workplace_on_documents' in source
''')

Path(__file__).unlink()
print("Contrato completo do cadastro administrativo aplicado.")
