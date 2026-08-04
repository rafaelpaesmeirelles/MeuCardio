#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, content: str) -> None:
    (ROOT / path).write_text(content, encoding="utf-8")


def replace_once(path: str, old: str, new: str) -> None:
    content = read(path)
    count = content.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: esperado 1 trecho, encontrado {count}: {old[:80]!r}")
    write(path, content.replace(old, new, 1))


def regex_once(path: str, pattern: str, replacement: str) -> None:
    content = read(path)
    new, count = re.subn(pattern, replacement, content, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError(f"{path}: padrão não encontrado: {pattern[:80]}")
    write(path, new)


# ------------------------------------------------------------------ normalização e Pillow sem warning
replace_once(
    "backend/app/services/professional_profile.py",
    "from pathlib import Path\n",
    "from pathlib import Path\nimport unicodedata\n",
)
replace_once(
    "backend/app/services/professional_profile.py",
    "def professional_name(source: Any) -> str:\n",
    '''def normalize_search_text(value: str | None) -> str:
    """Normaliza busca parcial sem expor ou persistir uma segunda cópia do nome."""
    decomposed = unicodedata.normalize("NFKD", (value or "").strip().casefold())
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def professional_name(source: Any) -> str:
''',
)
replace_once(
    "backend/app/services/professional_profile.py",
    '''            luminances: list[float] = []
            for red, green, blue, alpha in image.getdata():
''',
    '''            luminances: list[float] = []
            pixels = image.get_flattened_data() if hasattr(image, "get_flattened_data") else image.getdata()
            for red, green, blue, alpha in pixels:
''',
)

for path in ("backend/app/api/documents.py", "backend/app/api/receituario.py"):
    replace_once(
        path,
        "from app.services.professional_profile import document_identity, professional_name\n",
        "from app.services.professional_profile import (\n"
        "    document_identity, normalize_search_text, professional_name,\n"
        ")\n",
    )
    replace_once(path, '    busca = (nome or "").strip().casefold()\n', '    busca = normalize_search_text(nome)\n')
    replace_once(
        path,
        '        if busca and busca not in (patient_name or "").casefold():\n',
        '        if busca and busca not in normalize_search_text(patient_name):\n',
    )

replace_once(
    "backend/tests/test_professional_profile.py",
    "    normalize_professional_title,\n",
    "    normalize_professional_title, normalize_search_text,\n",
)
with (ROOT / "backend/tests/test_professional_profile.py").open("a", encoding="utf-8") as f:
    f.write('''\n\ndef test_busca_normaliza_acentos_maiusculas_e_espacos():
    assert normalize_search_text("  JOSÉ da Conceição  ") == "jose da conceicao"
    assert "concei" in normalize_search_text("José da Conceição")
''')

# ------------------------------------------------------------------ criação direta pelo administrador
replace_once(
    "backend/app/api/admin.py",
    "from pydantic import BaseModel\n",
    "from pydantic import BaseModel, field_validator\n",
)
replace_once(
    "backend/app/api/admin.py",
    "from app.models.content import Document\n",
    "from app.models.content import Document\n"
    "from app.services.professional_profile import normalize_council, normalize_professional_title\n",
)
regex_once(
    "backend/app/api/admin.py",
    r'class NovoUsuario\(BaseModel\):.*?\n\n\nclass SenhaTemporaria',
    '''class NovoUsuario(BaseModel):
    email: str
    full_name: str
    crm: str | None = None
    profession: str | None = None
    council_name: str | None = None
    council_number: str | None = None
    council_state: str | None = None
    specialty: str | None = None
    professional_title: str | None = None
    workplace_name: str | None = None
    workplace_department: str | None = None
    workplace_role: str | None = None
    workplace_notes: str | None = None
    include_workplace_on_documents: bool = False
    role: str = "medico"  # admin | medico | residente | leitor
    password: str

    @field_validator("professional_title")
    @classmethod
    def _title(cls, value: str | None) -> str | None:
        return normalize_professional_title(value)

    @field_validator("council_name")
    @classmethod
    def _council(cls, value: str | None) -> str | None:
        return normalize_council(value)

    @field_validator("council_state")
    @classmethod
    def _state(cls, value: str | None) -> str | None:
        value = (value or "").strip().upper()
        if value and (len(value) != 2 or not value.isalpha()):
            raise ValueError("UF inválida.")
        return value or None


class SenhaTemporaria''',
)
replace_once(
    "backend/app/api/admin.py",
    '        "council_state": u.council_state, "specialty": u.specialty,\n',
    '        "council_state": u.council_state, "specialty": u.specialty,\n'
    '        "professional_title": u.professional_title,\n'
    '        "workplace_name": u.workplace_name,\n'
    '        "workplace_department": u.workplace_department,\n'
    '        "workplace_role": u.workplace_role,\n'
    '        "workplace_notes": u.workplace_notes,\n'
    '        "include_workplace_on_documents": u.include_workplace_on_documents,\n',
)
replace_once(
    "backend/app/api/admin.py",
    '''    novo = User(
        email=email, full_name=dados.full_name.strip(), crm=dados.crm,
        role=dados.role, password_hash=hash_password(dados.password), is_active=True,
    )
''',
    '''    novo = User(
        email=email, full_name=dados.full_name.strip(), crm=dados.crm,
        profession=(dados.profession or "").strip() or None,
        council_name=dados.council_name,
        council_number=(dados.council_number or "").strip() or None,
        council_state=dados.council_state,
        specialty=(dados.specialty or "").strip() or None,
        professional_title=dados.professional_title,
        workplace_name=(dados.workplace_name or "").strip() or None,
        workplace_department=(dados.workplace_department or "").strip() or None,
        workplace_role=(dados.workplace_role or "").strip() or None,
        workplace_notes=(dados.workplace_notes or "").strip() or None,
        include_workplace_on_documents=dados.include_workplace_on_documents,
        role=dados.role, password_hash=hash_password(dados.password), is_active=True,
    )
''',
)

# Admin frontend
replace_once(
    "frontend/src/pages/Admin.tsx",
    '  specialty: string | null; role: string; status: string; is_active: boolean;\n',
    '  specialty: string | null; professional_title: string | null;\n'
    '  workplace_name: string | null; workplace_department: string | null;\n'
    '  workplace_role: string | null; workplace_notes: string | null;\n'
    '  include_workplace_on_documents: boolean; role: string; status: string; is_active: boolean;\n',
)
replace_once(
    "frontend/src/pages/Admin.tsx",
    'const PERFIS = [\n',
    'const CONSELHOS = ["CRM", "CRO", "CRBM", "COREN", "CRF", "CREFITO", "CRN", "CRP", "CREF", "CRESS", "OUTRO"];\n'
    'const TITULOS = ["", "Sr.", "Sra.", "Dr.", "Dra.", "Prof.", "Profa.", "Prof. Dr.", "Profa. Dra.", "Me.", "Ma.", "Esp."];\n'
    'const UFS = ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"];\n\n'
    'const PERFIS = [\n',
)
replace_once(
    "frontend/src/pages/Admin.tsx",
    '''  const [novo, setNovo] = useState({
    email: "", full_name: "", crm: "", role: "medico", password: "",
  });
''',
    '''  const [novo, setNovo] = useState({
    email: "", full_name: "", crm: "", profession: "", council_name: "CRM",
    council_number: "", council_state: "", specialty: "", professional_title: "",
    workplace_name: "", workplace_department: "", workplace_role: "", workplace_notes: "",
    include_workplace_on_documents: false, role: "medico", password: "",
  });
''',
)
replace_once(
    "frontend/src/pages/Admin.tsx",
    '      setNovo({ email: "", full_name: "", crm: "", role: "medico", password: "" });\n',
    '      setNovo({ email: "", full_name: "", crm: "", profession: "", council_name: "CRM",\n'
    '        council_number: "", council_state: "", specialty: "", professional_title: "",\n'
    '        workplace_name: "", workplace_department: "", workplace_role: "", workplace_notes: "",\n'
    '        include_workplace_on_documents: false, role: "medico", password: "" });\n',
)
replace_once(
    "frontend/src/pages/Admin.tsx",
    '''              <div>
                <label htmlFor="crm">CRM (opcional)</label>
                <input id="crm" value={novo.crm}
                       onChange={(e) => setNovo({ ...novo, crm: e.target.value })} />
              </div>
              <div>
                <label htmlFor="perfil">Perfil</label>
''',
    '''              <div>
                <label htmlFor="tratamento-admin">Como será chamado(a)</label>
                <select id="tratamento-admin" value={novo.professional_title}
                        onChange={(e) => setNovo({ ...novo, professional_title: e.target.value })}>
                  {TITULOS.map((t) => <option key={t || "sem"} value={t}>{t || "Sem título"}</option>)}
                </select>
              </div>
              <div>
                <label htmlFor="profissao-admin">Profissão</label>
                <input id="profissao-admin" value={novo.profession}
                       onChange={(e) => setNovo({ ...novo, profession: e.target.value })} />
              </div>
              <div>
                <label htmlFor="conselho-admin">Conselho</label>
                <select id="conselho-admin" value={novo.council_name}
                        onChange={(e) => setNovo({ ...novo, council_name: e.target.value })}>
                  {CONSELHOS.map((c) => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>
              <div>
                <label htmlFor="registro-admin">Nº de registro</label>
                <input id="registro-admin" value={novo.council_number}
                       onChange={(e) => setNovo({ ...novo, council_number: e.target.value })} />
              </div>
              <div>
                <label htmlFor="uf-admin">UF</label>
                <select id="uf-admin" value={novo.council_state}
                        onChange={(e) => setNovo({ ...novo, council_state: e.target.value })}>
                  <option value="">—</option>{UFS.map((uf) => <option key={uf} value={uf}>{uf}</option>)}
                </select>
              </div>
              <div>
                <label htmlFor="especialidade-admin">Especialidade</label>
                <input id="especialidade-admin" value={novo.specialty}
                       onChange={(e) => setNovo({ ...novo, specialty: e.target.value })} />
              </div>
              <div>
                <label htmlFor="crm">CRM legado (opcional)</label>
                <input id="crm" value={novo.crm}
                       onChange={(e) => setNovo({ ...novo, crm: e.target.value })} />
              </div>
              <div>
                <label htmlFor="perfil">Perfil</label>
''',
)
replace_once(
    "frontend/src/pages/Admin.tsx",
    '''            </div>
            <div style={{ marginTop: "0.9rem" }}>
              <label htmlFor="senha">Senha temporária</label>
''',
    '''            </div>
            <h3 style={{ fontSize: "1rem", marginTop: "1rem" }}>Local de trabalho (opcional)</h3>
            <div className="grade grade--2">
              <input placeholder="Instituição, clínica ou consultório" value={novo.workplace_name}
                     onChange={(e) => setNovo({ ...novo, workplace_name: e.target.value })} />
              <input placeholder="Setor/unidade" value={novo.workplace_department}
                     onChange={(e) => setNovo({ ...novo, workplace_department: e.target.value })} />
              <input placeholder="Cargo/função" value={novo.workplace_role}
                     onChange={(e) => setNovo({ ...novo, workplace_role: e.target.value })} />
              <input placeholder="Outras informações" value={novo.workplace_notes}
                     onChange={(e) => setNovo({ ...novo, workplace_notes: e.target.value })} />
            </div>
            <label style={{ display: "flex", gap: 8, alignItems: "center", fontWeight: 400, marginTop: 8 }}>
              <input type="checkbox" style={{ width: "auto" }} checked={novo.include_workplace_on_documents}
                     onChange={(e) => setNovo({ ...novo, include_workplace_on_documents: e.target.checked })} />
              Incluir local de trabalho nos documentos
            </label>
            <div style={{ marginTop: "0.9rem" }}>
              <label htmlFor="senha">Senha temporária</label>
''',
)

# ------------------------------------------------------------------ documentos públicos usam a identidade completa
replace_once(
    "backend/app/api/documentos_publicos.py",
    "from app.services.assinatura import emissao as assinatura_emissao\n",
    "from app.services.assinatura import emissao as assinatura_emissao\n"
    "from app.services.professional_profile import document_identity\n",
)
regex_once(
    "backend/app/api/documentos_publicos.py",
    r'medico=\{\n                "full_name": medico\.full_name if medico else "",.*?\n            \},\n            endereco=',
    'medico=document_identity(medico) if medico else {"full_name": ""},\n            endereco=',
)
replace_once(
    "backend/app/api/documentos_publicos.py",
    '''    pdf = svc_material.gerar(m, {
        "full_name": medico.full_name if medico else "",
        "council_name": medico.council_name if medico else None,
        "council_number": medico.council_number if medico else None,
        "council_state": medico.council_state if medico else None,
        "rqe": medico.rqe if medico else None,
    })
''',
    '    pdf = svc_material.gerar(m, document_identity(medico) if medico else {"full_name": ""})\n',
)
regex_once(
    "backend/app/api/documentos_publicos.py",
    r'medico=\{\n                "full_name": emissor\.full_name if emissor else "",.*?\n            \},\n            endereco=',
    'medico=document_identity(emissor) if emissor else {"full_name": ""},\n            endereco=',
)

# ------------------------------------------------------------------ material ao paciente com título, local e logo
replace_once(
    "backend/app/services/material_paciente.py",
    "from datetime import datetime, timezone\n",
    "from datetime import datetime, timezone\n"
    "import tempfile\n\n"
    "from PIL import Image, UnidentifiedImageError\n",
)
replace_once(
    "backend/app/services/material_paciente.py",
    '''from .pdf.marca import (
    NAVY, NEUTRO, TEAL, TINTA, TINTA_TEAL, TINTA_VERMELHA, VERMELHO,
)
''',
    '''from .pdf.marca import (
    BRANCO, NAVY, NEUTRO, TEAL, TINTA, TINTA_TEAL, TINTA_VERMELHA, VERMELHO,
)
from .professional_profile import (
    logo_needs_dark_plate_path, logo_path, professional_name, workplace_lines,
)
''',
)
replace_once(
    "backend/app/services/material_paciente.py",
    '    nome = (medico.get("full_name") or "").strip()\n',
    '    nome = professional_name(medico)\n',
)
replace_once(
    "backend/app/services/material_paciente.py",
    '''    d.capa_simples(material.titulo, material.subtitulo or "",
                   etiqueta="Material para o paciente")

    # Quem entrega.''',
    '''    d.capa_simples(material.titulo, material.subtitulo or "",
                   etiqueta="Material para o paciente")

    # Logo profissional: o núcleo PDF aceita PNG; Pillow converte JPEG/WEBP
    # apenas em memória/arquivo temporário, sem alterar o upload original.
    caminho_logo = logo_path(medico.get("document_logo_url"))
    if caminho_logo:
        try:
            with Image.open(caminho_logo) as original:
                imagem = original.convert("RGBA")
                imagem.thumbnail((360, 160))
                largura = 92.0
                altura = largura * imagem.height / max(imagem.width, 1)
                d._garantir(altura + 28)
                y_base = d.y - altura
                fundo = NAVY if logo_needs_dark_plate_path(caminho_logo) else BRANCO
                d.pdf.retangulo(d.margem, y_base - 7, largura + 14, altura + 14, fundo)
                with tempfile.NamedTemporaryFile(suffix=".png") as temp:
                    imagem.save(temp.name, format="PNG")
                    d.pdf.imagem("LogoProfissional", temp.name, d.margem + 7, y_base, largura, altura)
                d.y = y_base - 18
        except (OSError, UnidentifiedImageError):
            pass

    # Quem entrega.''',
)
replace_once(
    "backend/app/services/material_paciente.py",
    '''        d.pdf.texto(d.margem + 16, d.y - 32, nome + (f"  ·  {registro}" if registro else ""),
                    10, NAVY, negrito=True)
        d.y -= 54
''',
    '''        d.pdf.texto(d.margem + 16, d.y - 32, nome + (f"  ·  {registro}" if registro else ""),
                    10, NAVY, negrito=True)
        d.y -= 54
        for linha in workplace_lines(medico):
            d.pdf.texto(d.margem + 16, d.y - 9, linha, 8.5, NEUTRO)
            d.y -= 13
''',
)

# O material público e as rotas normais devem fornecer document_identity. A
# rota normal fica em exportacao.py.
replace_once(
    "backend/app/api/exportacao.py",
    "from app.services import material_paciente as svc_material\n",
    "from app.services import material_paciente as svc_material\n"
    "from app.services.professional_profile import document_identity\n",
)
regex_once(
    "backend/app/api/exportacao.py",
    r'svc_material\.gerar\(material, \{.*?\}\)',
    'svc_material.gerar(material, document_identity(user))',
)

# Remove o próprio aplicador antes do commit final.
(ROOT / "tools/apply_profile_followup.py").unlink(missing_ok=True)
print("Complemento aplicado.")
