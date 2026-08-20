from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def save(path: str, text: str) -> None:
    (ROOT / path).write_text(text, encoding="utf-8")


def replace_once(path: str, old: str, new: str) -> None:
    text = load(path)
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: esperado 1 match, encontrado {count}: {old[:100]!r}")
    save(path, text.replace(old, new, 1))


def replace_all(path: str, old: str, new: str, minimum: int = 1) -> None:
    text = load(path)
    count = text.count(old)
    if count < minimum:
        raise RuntimeError(f"{path}: esperado >= {minimum} matches, encontrado {count}: {old!r}")
    save(path, text.replace(old, new))


def regex_once(path: str, pattern: str, replacement: str) -> None:
    text = load(path)
    new, count = re.subn(pattern, lambda _m: replacement, text, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError(f"{path}: regex esperado 1 match, encontrado {count}: {pattern[:100]!r}")
    save(path, new)


# ---------------------------------------------------------------------------
# Public validation route works without login/onboarding redirects.
# ---------------------------------------------------------------------------
replace_once(
    "frontend/src/App.tsx",
    'const Tour = lazy(() => import("./pages/Tour"));\n',
    'const Tour = lazy(() => import("./pages/Tour"));\n'
    'const ValidarDocumento = lazy(() => import("./pages/ValidarDocumento"));\n',
)
replace_once(
    "frontend/src/App.tsx",
    '  if (carregando) return <Carregando texto="Abrindo a Corvia…" />;\n',
    '  const validacaoPublica = location.pathname === "/validar" || location.pathname.startsWith("/validar/");\n'
    '  if (validacaoPublica) {\n'
    '    return (\n'
    '      <RotasSuspensas>\n'
    '        <Routes>\n'
    '          <Route path="/validar" element={<ValidarDocumento />} />\n'
    '          <Route path="/validar/:codigo" element={<ValidarDocumento />} />\n'
    '        </Routes>\n'
    '      </RotasSuspensas>\n'
    '    );\n'
    '  }\n\n'
    '  if (carregando) return <Carregando texto="Abrindo a Corvia…" />;\n',
)

# ---------------------------------------------------------------------------
# Navigation: one single user-facing mail surface.
# ---------------------------------------------------------------------------
for path in ("frontend/src/components/ClinicalDesktopNav.tsx", "frontend/src/components/ClinicalMobileNav.tsx"):
    text = load(path)
    text = text.replace('{ to: "/corvia-mail", label: "CorVIA Mail", icon: "mail" },\n', '')
    text = text.replace('{ to: "/caixa-de-email", label: "Caixa de e-mail", icon: "mail" },', '{ to: "/caixa-de-email", label: "CorVIA Mail", icon: "mail" },')
    text = text.replace('  { to: "/corvia-mail", label: "Comunicação profissional", icon: "mail" },\n', '')
    text = text.replace('  { to: "/corvia-mail", label: "Comunicação", icon: "mail" },\n', '')
    save(path, text)

text = load("frontend/src/pages/PainelClinicalOS.tsx")
text = text.replace('      { to: "/corvia-mail", label: "CorVIA Mail", icon: "mail" },\n', '')
text = text.replace('      { to: "/caixa-de-email", label: "Caixa de e-mail", icon: "mail" },', '      { to: "/caixa-de-email", label: "CorVIA Mail", icon: "mail" },')
text = text.replace('      { to: "/corvia-mail", label: "Comunicação profissional", icon: "mail" },\n', '')
save("frontend/src/pages/PainelClinicalOS.tsx", text)

# ---------------------------------------------------------------------------
# CorVIA Mail: bulk deletion actually deletes every selected message.
# ---------------------------------------------------------------------------
replace_once(
    "frontend/src/pages/CaixaDeEmailProfessional.tsx",
    '  async function excluirMensagem(m: Mensagem) {\n'
    '    const origem = m.origem ?? contaId; const id = idMensagem(m); if (!id || !window.confirm("Mover esta mensagem para a lixeira?")) return; setAtualizando(true);\n'
    '    try { await apiEmail.delete(`${prefixo(origem)}/mensagens/${encodeURIComponent(id)}`); setMensagens((ls) => ls.filter((x) => !(idMensagem(x) === id && (!combinadas || (x.origem ?? "corvia") === origem)))); if (aberta && idMensagem(aberta) === id) setAberta(null); setAviso("Mensagem removida."); }\n'
    '    catch (e) { setErro(falha(e, "Não foi possível remover a mensagem.")); } finally { setAtualizando(false); }\n'
    '  }\n',
    '  async function excluirMensagem(m: Mensagem) {\n'
    '    const origem = m.origem ?? contaId; const id = idMensagem(m); if (!id || !window.confirm("Mover esta mensagem para a lixeira?")) return; setAtualizando(true);\n'
    '    try { await apiEmail.delete(`${prefixo(origem)}/mensagens/${encodeURIComponent(id)}`); setMensagens((ls) => ls.filter((x) => !(idMensagem(x) === id && (!combinadas || (x.origem ?? "corvia") === origem)))); if (aberta && idMensagem(aberta) === id) setAberta(null); setSelecionadas((ids) => { const n = new Set(ids); n.delete(id); return n; }); setAviso("Mensagem removida."); }\n'
    '    catch (e) { setErro(falha(e, "Não foi possível remover a mensagem.")); } finally { setAtualizando(false); }\n'
    '  }\n\n'
    '  async function excluirSelecionadas() {\n'
    '    if (combinadas || selecionadas.size === 0) return;\n'
    '    const ids = [...selecionadas];\n'
    '    if (!window.confirm(`Mover ${ids.length} ${ids.length === 1 ? "mensagem" : "mensagens"} para a lixeira?`)) return;\n'
    '    setAtualizando(true); setErro(null);\n'
    '    try {\n'
    '      await Promise.all(ids.map((id) => apiEmail.delete(`${prefixo(contaId)}/mensagens/${encodeURIComponent(id)}`)));\n'
    '      const removidas = new Set(ids);\n'
    '      setMensagens((ls) => ls.filter((m) => !removidas.has(idMensagem(m))));\n'
    '      if (aberta && removidas.has(idMensagem(aberta))) setAberta(null);\n'
    '      setSelecionadas(new Set());\n'
    '      setAviso(`${ids.length} ${ids.length === 1 ? "mensagem removida" : "mensagens removidas"}.`);\n'
    '    } catch (e) { setErro(falha(e, "Não foi possível remover todas as mensagens selecionadas.")); }\n'
    '    finally { setAtualizando(false); }\n'
    '  }\n',
)
replace_once(
    "frontend/src/pages/CaixaDeEmailProfessional.tsx",
    '<button className="danger" onClick={() => { const ids = [...selecionadas]; if (ids.length === 1) { const m = mensagens.find((x) => idMensagem(x) === ids[0]); if (m) void excluirMensagem(m); } }}>Excluir</button>',
    '<button className="danger" disabled={atualizando} onClick={() => void excluirSelecionadas()}>Excluir</button>',
)

# ---------------------------------------------------------------------------
# Connected accounts: automatic means automatic. Manual sync is not a normal UX.
# ---------------------------------------------------------------------------
regex_once(
    "frontend/src/pages/Sincronizacao.tsx",
    r'type ResultadoSync = \{.*?\};\n\n',
    '',
)
replace_once("frontend/src/pages/Sincronizacao.tsx", '  const [sincronizando, setSincronizando] = useState<number | null>(null);\n', '')
regex_once(
    "frontend/src/pages/Sincronizacao.tsx",
    r'\n  async function sincronizarConta\(id: number\) \{.*?\n  \}\n\n  function reconectar',
    '\n  function reconectar',
)
replace_once(
    "frontend/src/pages/Sincronizacao.tsx",
    '  async function desconectar(id: number, nome: string) {\n'
    '    if (!window.confirm(`Desconectar ${nome}? Os contatos sincronizados dela serão removidos do Corvia.`)) return;\n'
    '    setErro("");\n'
    '    try {\n'
    '      await api.delete(`/agenda/integrations/${id}`);\n'
    '      await carregar();\n'
    '    } catch (e) {\n'
    '      setErro(e instanceof ApiError ? e.message : "Não foi possível desconectar.");\n'
    '    }\n'
    '  }\n',
    '  async function removerConta(id: number, nome: string) {\n'
    '    if (!window.confirm(`Remover ${nome} do CorVIA? O vínculo e as credenciais salvas no CorVIA serão excluídos, assim como os contatos importados dessa conta. Sua conta no provedor não será apagada.`)) return;\n'
    '    setErro("");\n'
    '    try {\n'
    '      await api.delete(`/agenda/integrations/${id}`);\n'
    '      setMensagem("Conta removida do CorVIA.");\n'
    '      await carregar();\n'
    '    } catch (e) {\n'
    '      setErro(e instanceof ApiError ? e.message : "Não foi possível remover a conta.");\n'
    '    }\n'
    '  }\n',
)
regex_once(
    "frontend/src/pages/Sincronizacao.tsx",
    r'\s*\{!item\.enabled \|\| item\.status === "reauth_required" \? \(\n\s*<button className="botao".*?\n\s*\) : temComponenteSincronizavel && \(\n\s*<button className="botao botao--secundario".*?\n\s*</button>\n\s*\)\}\n',
    '\n                  {(!item.enabled || item.status === "reauth_required") && (\n'
    '                    <button className="botao" style={{ padding: "0.2rem 0.6rem", fontSize: "0.78rem" }} onClick={() => reconectar(item)}>\n'
    '                      Reconectar\n'
    '                    </button>\n'
    '                  )}\n',
)
replace_once(
    "frontend/src/pages/Sincronizacao.tsx",
    '                          onClick={() => desconectar(item.id, item.display_name)}>\n                    Desconectar\n',
    '                          onClick={() => removerConta(item.id, item.display_name)}>\n                    Remover conta\n',
)
replace_once(
    "frontend/src/pages/Sincronizacao.tsx",
    '                  Conexão ativa · última verificação/sincronização: {new Date(item.last_success_at).toLocaleString("pt-BR")}\n',
    '                  Conectada e ativa · manutenção automática · última verificação: {new Date(item.last_success_at).toLocaleString("pt-BR")}\n',
)
replace_once(
    "frontend/src/pages/Sincronizacao.tsx",
    '                  Conectada; aguardando a primeira verificação automática. Você também pode usar "Sincronizar agora".\n',
    '                  Conectada · primeira verificação automática pendente. Não é necessário sincronizar manualmente.\n',
)
replace_once(
    "frontend/src/pages/Sincronizacao.tsx",
    '        OAuth é renovado automaticamente, Yahoo/iCloud recebem heartbeat de credencial e a Agenda\n'
    '        é atualizada continuamente em segundo plano. O CorvIA Mail consulta caixas externas ao vivo.\n',
    '        A manutenção é automática: OAuth é renovado em segundo plano, Yahoo/iCloud recebem heartbeat\n'
    '        de credencial e o CorVIA Mail consulta caixas externas ao vivo. Reconectar só aparece quando\n'
    '        a autorização realmente expirar; para encerrar o vínculo, use Remover conta.\n',
)

# ---------------------------------------------------------------------------
# Tour: canonical assets, no broken profile square, tighter viewport geometry.
# ---------------------------------------------------------------------------
replace_all("frontend/src/pages/TourClinicalOS.tsx", '/corvia-logo-compacta.png', '/corvia-mark-canonical.svg', minimum=3)
replace_once(
    "frontend/src/pages/TourClinicalOS.tsx",
    '<div className="cos-tour__brand"><img src="/corvia-mark-canonical.svg" alt="CorVIA"/><span><strong>CorVIA</strong><small>Clinical OS do médico</small></span></div>',
    '<div className="cos-tour__brand"><img src="/corvia-logo-canonical-dark.svg" alt="CorVIA Clinical OS"/></div>',
)
regex_once(
    "frontend/src/pages/TourClinicalOS.tsx",
    r'\nfunction iniciais\(nome\?: string \| null\) \{.*?\n\}\n',
    '\n',
)
replace_once("frontend/src/pages/TourClinicalOS.tsx", '  const [fotoFalhou, setFotoFalhou] = useState(false);\n', '')
regex_once(
    "frontend/src/pages/TourClinicalOS.tsx",
    r'\n\s*<div className="cos-tour-welcome__avatar">.*?</div>',
    '',
)

# ---------------------------------------------------------------------------
# Legal pages: direct canonical assets instead of legacy/runtime swaps.
# ---------------------------------------------------------------------------
replace_all("frontend/src/pages/TermosUso.tsx", '/corvia-logo-compacta.png', '/corvia-logo-canonical.svg')
replace_all("frontend/src/pages/PoliticaPrivacidade.tsx", '/corvia-logo-compacta.png', '/corvia-logo-canonical.svg')

# ---------------------------------------------------------------------------
# Account copy and semantic grid hook.
# ---------------------------------------------------------------------------
replace_once(
    "frontend/src/pages/MinhaConta.tsx",
    ' * Google/Microsoft/Yahoo/iCloud também usam S/MIME; a caixa nativa fica\n * bloqueada para nunca degradar silenciosamente para envio sem assinatura. */',
    ' * Google/Microsoft/Yahoo/iCloud também podem usar S/MIME. A caixa nativa\n * continua apta a transportar PDFs clínicos já assinados por PAdES; S/MIME\n * é uma camada adicional do envelope quando o transporte é compatível. */',
)
replace_once(
    "frontend/src/pages/MinhaConta.tsx",
    '? "S/MIME ativo para este usuário. Google, Microsoft, Yahoo e iCloud enviam assinados; a caixa nativa é bloqueada para não enviar sem assinatura."',
    '? "S/MIME ativo quando o transporte é compatível. PDFs clínicos mantêm sua assinatura PAdES independentemente do provedor de e-mail."',
)
replace_once(
    "frontend/src/pages/MinhaConta.tsx",
    '<div style={{ display: "grid", gap: "1rem", maxWidth: 560 }}>',
    '<div className="conta__grid">',
)

# ---------------------------------------------------------------------------
# Final contrast/form/layout rules in existing canonical contract files.
# ---------------------------------------------------------------------------
contrast = load("frontend/src/styles/clinical-form-control-contrast.css")
contrast += '''\n\n/* Product stabilization 2026-08-20: prescription and form controls must remain legible. */\n.clinical-os input:not([type="checkbox"]):not([type="radio"]),\n.clinical-os select,\n.clinical-os textarea { width:100%; min-width:0; box-sizing:border-box; }\n.clinical-os .grade > *, .clinical-os [class*="grid"] > * { min-width:0; }\n.clinical-os .prescricao-selecao {\n  background:linear-gradient(145deg,#0d2534,#0a1b28)!important;\n  border:1px solid rgba(94,205,218,.28)!important;\n  color:#eaf8fb!important;\n  box-shadow:0 12px 28px rgba(0,0,0,.14);\n}\n.clinical-os .prescricao-selecao strong,\n.clinical-os .prescricao-selecao b,\n.clinical-os .prescricao-selecao h2,\n.clinical-os .prescricao-selecao h3 { color:#f4fdff!important; }\n.clinical-os .prescricao-selecao small,\n.clinical-os .prescricao-selecao p,\n.clinical-os .prescricao-selecao span { color:#a9c7d0!important; }\n.clinical-os .prescricao-selecao .botao,\n.clinical-os .prescricao-selecao button { color:#dffbfe!important; }\n'''
save("frontend/src/styles/clinical-form-control-contrast.css", contrast)

account = load("frontend/src/styles/clinical-account-admin-command.css")
account = account.replace('body.corvia-route--conta .clinical-os .pagina > div[style*="max-width: 560"]', 'body.corvia-route--conta .clinical-os .conta__grid')
account += '''\n\nbody.corvia-route--conta .clinical-os .conta__grid {\n  display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:.62rem;\n  width:100%; max-width:none; align-items:stretch; grid-auto-flow:row dense;\n}\nbody.corvia-route--conta .clinical-os .conta__grid > .cartao { height:100%; min-width:0; }\n@media(max-width:900px){ body.corvia-route--conta .clinical-os .conta__grid{grid-template-columns:1fr;} }\n'''
save("frontend/src/styles/clinical-account-admin-command.css", account)

home = load("frontend/src/styles/postdeploy-home-density.css")
home += '''\n\n@media (min-width: 901px) {\n  .ccc-reference-board { align-content:start!important; grid-auto-rows:max-content; row-gap:.62rem!important; }\n  .ccc-reference-board .ccc-home__welcome,\n  .ccc-reference-board .ccc-actions-section,\n  .ccc-reference-board .ccc-reference-summary { margin:0!important; }\n}\n'''
save("frontend/src/styles/postdeploy-home-density.css", home)

# Tour source assets now canonical; runtime content/display swaps are no longer needed.
save("frontend/src/styles/tour-branding-hotfix.css", '''/* Canonical Tour branding: source assets are canonical; CSS controls geometry only. */\n.cos-tour__brand > img {\n  display:block; width:clamp(150px,18vw,210px); height:48px; object-fit:contain; object-position:left center;\n}\n.cos-tour-mock__brand img,.cos-tour-phone>header img,.cos-tour-final__mark img { object-fit:contain; }\n@media (min-width:701px) and (max-width:1180px){\n  .cos-tour__top{grid-template-columns:minmax(170px,1fr) auto minmax(100px,1fr);gap:.75rem;padding-inline:1.25rem;}\n  .cos-tour__brand>img{width:180px;height:44px;}\n}\n@media(max-width:700px){.cos-tour__brand>img{width:142px;height:38px;}}\n''')

tour_css = load("frontend/src/styles/tour-clinical-os.css")
tour_css += '''\n\n/* Product stabilization: every tour step fits the viewport without a fake/broken profile tile. */\n.cos-tour { grid-template-rows:60px 3px minmax(0,1fr) 60px; }\n.cos-tour__stage { overflow:auto; overscroll-behavior:contain; }\n.cos-tour-welcome,.cos-tour-final { min-height:100%; padding:clamp(1rem,3vh,2.2rem) clamp(1rem,4vw,3rem); }\n.cos-tour-welcome h1,.cos-tour-final h1 { font-size:clamp(2rem,4.8vw,4.5rem); }\n.cos-tour-welcome__lead,.cos-tour-final>p { margin-top:.75rem; line-height:1.5; }\n.cos-tour-welcome__pillars { margin:.9rem 0; }\n.cos-tour-feature { padding:clamp(.8rem,2vw,1.6rem) clamp(1rem,3vw,2.6rem); gap:clamp(1rem,2.8vw,2.5rem); }\n.cos-tour-feature__visual { height:min(60vh,560px); }\n@media(max-height:760px) and (min-width:901px){\n  .cos-tour{grid-template-rows:54px 3px minmax(0,1fr) 54px;}\n  .cos-tour-welcome h1,.cos-tour-final h1{font-size:clamp(1.9rem,4.2vw,3.6rem);}\n  .cos-tour-welcome__lead,.cos-tour-final>p{font-size:.78rem;}\n  .cos-tour-welcome__pillars{margin:.65rem 0;padding:.45rem .6rem;}\n  .cos-tour-feature__visual{height:min(56vh,480px);}\n  .cos-tour-feature__counter{margin-bottom:.65rem}.cos-tour-feature blockquote{margin:.65rem 0;}\n}\n@media(max-width:900px){\n  .cos-tour{grid-template-rows:54px 3px minmax(0,1fr) 64px;}\n  .cos-tour-feature{grid-template-columns:1fr;height:auto;align-content:start;overflow:visible;}\n  .cos-tour-feature__visual{height:42vh;min-height:280px;}\n  .cos-tour-feature__copy{max-width:none;}\n}\n'''
save("frontend/src/styles/tour-clinical-os.css", tour_css)

# Regression contracts.
(ROOT / "backend/tests/test_product_stabilization_frontend_contract.py").write_text('''from pathlib import Path\n\nROOT = Path(__file__).resolve().parents[2]\n\ndef text(path: str) -> str:\n    return (ROOT / path).read_text(encoding="utf-8")\n\ndef test_mail_navigation_has_one_user_facing_entry():\n    for path in ("frontend/src/components/ClinicalDesktopNav.tsx", "frontend/src/components/ClinicalMobileNav.tsx"):\n        src = text(path)\n        assert 'to: "/caixa-de-email", label: "CorVIA Mail"' in src\n        assert 'to: "/corvia-mail", label: "CorVIA Mail"' not in src\n        assert 'label: "Caixa de e-mail"' not in src\n\ndef test_mail_bulk_delete_is_real():\n    src = text("frontend/src/pages/CaixaDeEmailProfessional.tsx")\n    assert "async function excluirSelecionadas" in src\n    assert "Promise.all(ids.map" in src\n    assert "if (ids.length === 1)" not in src\n\ndef test_connected_accounts_are_automatic_and_removable():\n    src = text("frontend/src/pages/Sincronizacao.tsx")\n    assert "Sincronizar agora" not in src\n    assert "sincronizarConta" not in src\n    assert "Remover conta" in src\n    assert "manutenção automática" in src\n\ndef test_public_validation_page_is_wired_before_auth_gates():\n    src = text("frontend/src/App.tsx")\n    assert 'location.pathname.startsWith("/validar/")' in src\n    assert '<Route path="/validar/:codigo" element={<ValidarDocumento />}' in src\n\ndef test_legacy_brand_sources_removed_from_reported_pages():\n    for path in ("frontend/src/pages/TermosUso.tsx", "frontend/src/pages/PoliticaPrivacidade.tsx", "frontend/src/pages/TourClinicalOS.tsx"):\n        assert "/corvia-logo-compacta.png" not in text(path)\n\ndef test_tour_has_no_broken_user_avatar_tile():\n    src = text("frontend/src/pages/TourClinicalOS.tsx")\n    assert "cos-tour-welcome__avatar" not in src\n    assert "fotoFalhou" not in src\n\ndef test_prescription_selected_product_has_explicit_contrast():\n    src = text("frontend/src/styles/clinical-form-control-contrast.css")\n    assert ".clinical-os .prescricao-selecao" in src\n    assert "#f4fdff" in src\n''', encoding="utf-8")

print("frontend product stabilization patches applied")
