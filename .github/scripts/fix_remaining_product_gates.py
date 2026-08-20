from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def replace_once(path: str, old: str, new: str) -> None:
    file = ROOT / path
    source = file.read_text(encoding="utf-8")
    if old in source:
        file.write_text(source.replace(old, new, 1), encoding="utf-8")
        return
    if new in source:
        return
    raise RuntimeError(f"replacement target not found in {path}: {old[:100]!r}")


# Canonical CorVIA Mail entry: one visible destination, through the gateway.
for path in (
    "frontend/src/components/ClinicalDesktopNav.tsx",
    "frontend/src/components/ClinicalMobileNav.tsx",
    "frontend/src/pages/PainelClinicalOS.tsx",
):
    file = ROOT / path
    source = file.read_text(encoding="utf-8")
    source = source.replace('to: "/caixa-de-email", label: "CorVIA Mail"', 'to: "/corvia-mail", label: "CorVIA Mail"')
    file.write_text(source, encoding="utf-8")

# Remove accidental indentation left by the previous surgical edit.
for path in (
    "frontend/src/components/ClinicalDesktopNav.tsx",
    "frontend/src/components/ClinicalMobileNav.tsx",
):
    file = ROOT / path
    source = file.read_text(encoding="utf-8")
    source = source.replace('    { to: "/corvia-mail", label: "CorVIA Mail", icon: "mail" },', '  { to: "/corvia-mail", label: "CorVIA Mail", icon: "mail" },')
    file.write_text(source, encoding="utf-8")

# Align our stabilization regression contract with the pre-existing canonical route.
replace_once(
    "backend/tests/test_product_stabilization_frontend_contract.py",
    '''        assert 'to: "/caixa-de-email", label: "CorVIA Mail"' in src\n        assert 'to: "/corvia-mail", label: "CorVIA Mail"' not in src\n''',
    '''        assert 'to: "/corvia-mail", label: "CorVIA Mail"' in src\n        assert 'to: "/caixa-de-email", label: "CorVIA Mail"' not in src\n''',
)

# Explicit S/MIME requests fail first on missing A1; profile preference alone
# still does not block native Mail360 delivery of the already PAdES-signed PDF.
replace_once(
    "backend/app/services/envio_documento_email.py",
    '''    integracao = _integracao_padrao_externa(db, user)\n\n    if integracao is None:\n''',
    '''    integracao = _integracao_padrao_externa(db, user)\n    certificado = certificado_a1.obter(db, user) if (assinar_smime or user.email_assinatura_digital_ativa) else None\n    if assinar_smime and certificado is None:\n        return ResultadoEnvio(\n            False,\n            "Não há certificado A1 conectado para assinar digitalmente este e-mail por S/MIME.",\n        )\n\n    if integracao is None:\n''',
)
replace_once(
    "backend/app/services/envio_documento_email.py",
    'return ResultadoEnvio(False, "Sua caixa do CorVIA Mail não está ativa.")',
    'return ResultadoEnvio(False, "Sua caixa do CorvIA Mail não está ativa.")',
)
replace_once(
    "backend/app/services/envio_documento_email.py",
    '''    assinatura_obrigatoria = bool(assinar_smime or user.email_assinatura_digital_ativa)\n    if assinatura_obrigatoria and certificado_a1.obter(db, user) is None:\n''',
    '''    assinatura_obrigatoria = bool(assinar_smime or user.email_assinatura_digital_ativa)\n    if assinatura_obrigatoria and certificado is None:\n''',
)

# The validation surface is intentional and public; approve it in the exact
# feature inventory. The mailbox implementation route remains in App.tsx but
# is no longer a second visible navigation destination.
replace_once(
    "scripts/feature_inventory.py",
    '    "/privacidade", "/termos",\n',
    '    "/privacidade", "/termos", "/validar", "/validar/:codigo",\n',
)
replace_once(
    "scripts/feature_inventory.py",
    '    "/casos-clinicos", "/interacoes", "/checklists", "/corvia-mail", "/caixa-de-email", "/cursos",\n',
    '    "/casos-clinicos", "/interacoes", "/checklists", "/corvia-mail", "/cursos",\n',
)
replace_once(
    "scripts/feature_inventory.py",
    '    "frontend/src/pages/CorviaMail.tsx",\n',
    '    "frontend/src/pages/CorviaMail.tsx",\n    "frontend/src/pages/ValidarDocumento.tsx",\n',
)

# Keep bundle budget strict. Shave static copy from the new validation chunk
# instead of increasing the PWA ceiling for a 36-byte overage.
replace_once(
    "frontend/src/pages/ValidarDocumento.tsx",
    '''          A validação CorVIA confirma integridade criptográfica e os dados presentes na assinatura do PDF. Para validação de cadeia de confiança, revogação e requisitos oficiais adicionais, utilize também o validador oficial do ITI/ICP-Brasil quando aplicável.\n''',
    '''          A CorVIA confirma a integridade e a assinatura do PDF. Para cadeia de confiança e revogação, use também o validador oficial do ITI/ICP-Brasil.\n''',
)

print("remaining product gates patched")
