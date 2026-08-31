import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { ApiError, api } from "../lib/api";
import { Carregando, Erro } from "../components/Estado";

type CorviaMail = {
  id: number;
  email_address: string;
  status: string;
};

type UsuarioGerenciavel = {
  id: number;
  full_name: string;
  email: string;
  role: string;
  birth_date: string | null;
  cpf: string | null;
  profession: string | null;
  council_name: string | null;
  council_number: string | null;
  council_state: string | null;
  specialty: string | null;
  rqe: string | null;
  professional_title: string | null;
  workplace_name: string | null;
  workplace_department: string | null;
  workplace_role: string | null;
  workplace_notes: string | null;
  is_active: boolean;
  tipo_acesso: "normal" | "convidado" | "investidor";
  gratuito: boolean;
  pode_excluir_definitivamente: boolean;
  bloqueio_exclusao: string | null;
  pode_ver_historico_acessos: boolean;
  sessao_unica_ativa: boolean;
  corvia_mail: CorviaMail | null;
};

type MotivoRisco = { code: string; message: string; severity: "medio" | "alto" };
type Acesso = {
  id: number;
  surface: "corvia_os" | "corvia_mail";
  successful: boolean;
  started_at: string;
  last_seen_at: string | null;
  ended_at: string | null;
  end_reason: string | null;
  end_reason_label: string | null;
  active: boolean;
  ip_address: string;
  location: string;
  operating_system: string;
  browser: string;
  device_type: string;
  risk_level: "normal" | "medio" | "alto";
  risk_reasons: MotivoRisco[];
};
type HistoricoAcessos = {
  items: Acesso[];
  total: number;
  offset: number;
  limit: number;
  single_session_enforced: boolean;
};

type CampoTexto =
  | "profession" | "council_name" | "council_number" | "council_state"
  | "specialty" | "rqe" | "professional_title" | "workplace_name"
  | "workplace_department" | "workplace_role" | "workplace_notes";

const PERFIS = [
  ["medico", "Médico"],
  ["residente", "Residente"],
  ["leitor", "Leitor"],
] as const;

const TIPOS = [
  ["normal", "Normal"],
  ["convidado", "Convidado — gratuito"],
  ["investidor", "Investidor — demonstração"],
] as const;

const CAMPOS_TEXTO: Array<[CampoTexto, string, string]> = [
  ["profession", "Profissão", "Ex.: Médico"],
  ["council_name", "Conselho", "Ex.: CRM"],
  ["council_number", "Número do conselho", ""],
  ["council_state", "UF do conselho", "SP"],
  ["specialty", "Especialidade", ""],
  ["rqe", "RQE", ""],
  ["professional_title", "Título profissional", "Ex.: Dr."],
  ["workplace_name", "Instituição / local de trabalho", ""],
  ["workplace_department", "Setor / unidade", ""],
  ["workplace_role", "Cargo / função", ""],
  ["workplace_notes", "Observações profissionais", ""],
];

function mensagemErro(e: unknown, fallback: string) {
  return e instanceof ApiError || e instanceof Error ? e.message : fallback;
}

export default function AdminGerenciarUsuario() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [usuario, setUsuario] = useState<UsuarioGerenciavel | null>(null);
  const [erro, setErro] = useState("");
  const [salvando, setSalvando] = useState(false);
  const [mensagem, setMensagem] = useState("");
  const [novaSenha, setNovaSenha] = useState("");
  const [senha2, setSenha2] = useState("");
  const [alterandoSenha, setAlterandoSenha] = useState(false);
  const [novaSenhaMail, setNovaSenhaMail] = useState("");
  const [senhaMail2, setSenhaMail2] = useState("");
  const [alterandoSenhaMail, setAlterandoSenhaMail] = useState(false);
  const [confirmarEmail, setConfirmarEmail] = useState("");
  const [confirmarExclusao, setConfirmarExclusao] = useState(false);
  const [excluindo, setExcluindo] = useState(false);
  const [historico, setHistorico] = useState<HistoricoAcessos | null>(null);
  const [carregandoAcessos, setCarregandoAcessos] = useState(false);
  const [revogandoSessao, setRevogandoSessao] = useState(false);

  function carregar() {
    if (!id) return;
    setErro("");
    api.get<UsuarioGerenciavel>(`/admin/user-management/${id}`)
      .then(setUsuario)
      .catch((e) => setErro(mensagemErro(e, "Não foi possível carregar a conta.")));
  }

  useEffect(() => { carregar(); }, [id]);

  async function carregarAcessos(offset = 0, append = false) {
    if (!id) return;
    setCarregandoAcessos(true);
    try {
      const pagina = await api.get<HistoricoAcessos>(`/admin/user-management/${id}/accesses?offset=${offset}&limit=200`);
      setHistorico((atual) => append && atual
        ? { ...pagina, items: [...atual.items, ...pagina.items], offset: 0 }
        : pagina);
    } catch (e) {
      setErro(mensagemErro(e, "Não foi possível carregar o histórico de acessos."));
    } finally { setCarregandoAcessos(false); }
  }

  useEffect(() => {
    if (usuario?.pode_ver_historico_acessos) void carregarAcessos();
  }, [id, usuario?.pode_ver_historico_acessos]);

  const emailConfere = useMemo(
    () => !!usuario && confirmarEmail.trim().toLowerCase() === usuario.email.trim().toLowerCase(),
    [confirmarEmail, usuario],
  );

  async function salvar() {
    if (!usuario || !id) return;
    setSalvando(true); setErro(""); setMensagem("");
    try {
      const atualizado = await api.patch<UsuarioGerenciavel>(`/admin/user-management/${id}`, {
        full_name: usuario.full_name,
        email: usuario.email,
        role: usuario.role,
        birth_date: usuario.birth_date || null,
        cpf: usuario.cpf || null,
        profession: usuario.profession || null,
        council_name: usuario.council_name || null,
        council_number: usuario.council_number || null,
        council_state: usuario.council_state || null,
        specialty: usuario.specialty || null,
        rqe: usuario.rqe || null,
        professional_title: usuario.professional_title || null,
        workplace_name: usuario.workplace_name || null,
        workplace_department: usuario.workplace_department || null,
        workplace_role: usuario.workplace_role || null,
        workplace_notes: usuario.workplace_notes || null,
        is_active: usuario.is_active,
        tipo_acesso: usuario.tipo_acesso,
      });
      setUsuario(atualizado);
      setMensagem("Dados atualizados com sucesso.");
    } catch (e) {
      setErro(mensagemErro(e, "Não foi possível atualizar o usuário."));
    } finally { setSalvando(false); }
  }

  async function trocarSenha() {
    if (!id) return;
    if (novaSenha.length < 8) { setErro("A nova senha precisa ter pelo menos 8 caracteres."); return; }
    if (novaSenha !== senha2) { setErro("As duas senhas não conferem."); return; }
    setAlterandoSenha(true); setErro(""); setMensagem("");
    try {
      await api.post(`/admin/users/${id}/senha`, { password: novaSenha });
      setNovaSenha(""); setSenha2("");
      setMensagem("Senha do Cardiology Spaces alterada. As sessões anteriores foram revogadas.");
    } catch (e) {
      setErro(mensagemErro(e, "Não foi possível alterar a senha."));
    } finally { setAlterandoSenha(false); }
  }

  async function trocarSenhaMail() {
    if (!id || !usuario?.corvia_mail) return;
    if (novaSenhaMail.length < 8) { setErro("A nova senha do CorVIA Mail precisa ter pelo menos 8 caracteres."); return; }
    if (novaSenhaMail !== senhaMail2) { setErro("As duas senhas do CorVIA Mail não conferem."); return; }
    setAlterandoSenhaMail(true); setErro(""); setMensagem("");
    try {
      await api.post(`/admin/user-management/${id}/corvia-mail/senha`, { password: novaSenhaMail });
      setNovaSenhaMail(""); setSenhaMail2("");
      setMensagem("Senha do CorVIA Mail alterada. As sessões anteriores da caixa foram revogadas.");
    } catch (e) {
      setErro(mensagemErro(e, "Não foi possível alterar a senha do CorVIA Mail."));
    } finally { setAlterandoSenhaMail(false); }
  }

  async function excluirDefinitivamente() {
    if (!usuario || !id || !emailConfere || !confirmarExclusao) return;
    setExcluindo(true); setErro(""); setMensagem("");
    try {
      await api.delete(`/admin/user-management/${id}`, {
        confirmar_email: confirmarEmail.trim().toLowerCase(),
        excluir_corvia_mail: true,
      });
      navigate("/admin/usuarios", { replace: true });
    } catch (e) {
      setErro(mensagemErro(e, "Não foi possível excluir definitivamente a conta."));
      setExcluindo(false);
    }
  }

  async function revogarSessoes() {
    if (!id) return;
    setRevogandoSessao(true); setErro(""); setMensagem("");
    try {
      await api.post(`/admin/user-management/${id}/revoke-session`, {});
      setMensagem("A sessão atual do Cardiology Spaces e do CorVIA Mail foi encerrada.");
      await carregarAcessos();
    } catch (e) {
      setErro(mensagemErro(e, "Não foi possível encerrar a sessão do usuário."));
    } finally { setRevogandoSessao(false); }
  }

  if (erro && !usuario) return <><Link to="/admin/usuarios">← Voltar</Link><Erro mensagem={erro} /></>;
  if (!usuario) return <Carregando texto="Carregando gestão da conta…" />;

  const alterar = <K extends keyof UsuarioGerenciavel>(campo: K, valor: UsuarioGerenciavel[K]) =>
    setUsuario((u) => u ? { ...u, [campo]: valor } : u);

  return (
    <>
      <Link to={`/admin/usuarios/${usuario.id}`} style={{ fontSize: "0.88rem" }}>← Voltar para a ficha</Link>
      <p className="eyebrow" style={{ marginTop: "1rem" }}>Administração · usuário #{usuario.id}</p>
      <h1>Gerenciar conta</h1>
      <p style={{ color: "var(--texto-secundario)", maxWidth: "72ch" }}>
        Edite dados, redefina as senhas do Cardiology Spaces e do CorVIA Mail e, quando permitido,
        remova definitivamente contas gratuitas ou de demonstração.
      </p>

      {mensagem && <div className="cartao" style={{ marginBottom: 12, borderColor: "rgba(52,211,153,.35)" }}>{mensagem}</div>}
      {erro && <div style={{ marginBottom: 12 }}><Erro mensagem={erro} /></div>}

      <section className="cartao cartao--clinico" style={{ maxWidth: 900 }}>
        <p className="eyebrow">Dados da conta</p>
        <div className="grade grade--2">
          <div><label>Nome completo</label><input value={usuario.full_name} onChange={(e) => alterar("full_name", e.target.value)} /></div>
          <div><label>E-mail de login</label><input type="email" value={usuario.email} onChange={(e) => alterar("email", e.target.value)} /></div>
          <div><label>CPF</label><input value={usuario.cpf ?? ""} onChange={(e) => alterar("cpf", e.target.value)} /></div>
          <div><label>Data de nascimento</label><input type="date" value={usuario.birth_date ?? ""} onChange={(e) => alterar("birth_date", e.target.value || null)} /></div>
          <div><label>Perfil</label><select value={usuario.role} onChange={(e) => alterar("role", e.target.value)}>{PERFIS.map(([v, r]) => <option key={v} value={v}>{r}</option>)}</select></div>
          <div><label>Tipo de acesso</label><select value={usuario.tipo_acesso} onChange={(e) => alterar("tipo_acesso", e.target.value as UsuarioGerenciavel["tipo_acesso"])}>{TIPOS.map(([v, r]) => <option key={v} value={v}>{r}</option>)}</select></div>
          {CAMPOS_TEXTO.map(([campo, rotulo, placeholder]) => (
            <div key={campo}>
              <label>{rotulo}</label>
              <input placeholder={placeholder} value={usuario[campo] ?? ""} onChange={(e) => setUsuario((u) => u ? { ...u, [campo]: e.target.value } : u)} />
            </div>
          ))}
        </div>
        <label style={{ display: "flex", alignItems: "center", gap: 8, marginTop: 12, fontWeight: 500 }}>
          <input type="checkbox" style={{ width: "auto" }} checked={usuario.is_active} onChange={(e) => alterar("is_active", e.target.checked)} />
          Conta ativa
        </label>
        <button className="botao" style={{ marginTop: 14 }} disabled={salvando} onClick={salvar}>{salvando ? "Salvando…" : "Salvar alterações"}</button>
      </section>

      {usuario.pode_ver_historico_acessos && (
        <section className="cartao cartao--clinico" style={{ maxWidth: 900, marginTop: 16 }}>
          <p className="eyebrow">Segurança · visível somente para o proprietário</p>
          <div style={{ display: "flex", justifyContent: "space-between", gap: 12, alignItems: "flex-start", flexWrap: "wrap" }}>
            <div>
              <h2 style={{ marginTop: 4 }}>Histórico completo de acessos</h2>
              <p style={{ color: "var(--texto-secundario)", fontSize: ".88rem", maxWidth: "68ch" }}>
                Sessão única ativa: um novo login invalida imediatamente o anterior no Cardiology Spaces e no CorVIA Mail.
                Localização depende dos dados enviados pelo provedor de rede e pode ser imprecisa com VPN ou rede móvel.
              </p>
            </div>
            <button className="botao botao--secundario" disabled={revogandoSessao} onClick={revogarSessoes}>
              {revogandoSessao ? "Encerrando…" : "Encerrar acesso atual"}
            </button>
          </div>

          {carregandoAcessos && !historico && <Carregando texto="Carregando acessos…" />}
          {historico && (
            <>
              <div style={{ display: "flex", gap: 8, flexWrap: "wrap", margin: "12px 0" }}>
                <span className="selo selo--info">{historico.total} registro{historico.total === 1 ? "" : "s"}</span>
                <span className="selo selo--sucesso">Sessão única protegida</span>
                {historico.items.some((item) => item.risk_level === "alto") && <span className="selo selo--atencao">Alerta de segurança</span>}
              </div>
              <div style={{ display: "grid", gap: 10 }}>
                {historico.items.map((item) => (
                  <article key={item.id} style={{ border: "1px solid var(--borda)", borderRadius: 12, padding: 12 }}>
                    <div style={{ display: "flex", justifyContent: "space-between", gap: 8, flexWrap: "wrap" }}>
                      <strong>{item.surface === "corvia_mail" ? "CorVIA Mail" : "Cardiology Spaces"} · {new Date(item.started_at).toLocaleString("pt-BR")}</strong>
                      <span className={`selo ${item.active ? "selo--sucesso" : item.risk_level === "alto" ? "selo--atencao" : "selo--info"}`}>
                        {!item.successful ? "Tentativa recusada" : item.active ? "Sessão ativa" : item.risk_level === "alto" ? "Risco alto" : item.risk_level === "medio" ? "Atenção" : "Encerrada"}
                      </span>
                    </div>
                    <div className="grade grade--2" style={{ marginTop: 8, fontSize: ".88rem" }}>
                      <div><small style={{ color: "var(--texto-secundario)" }}>Local</small><br />{item.location}</div>
                      <div><small style={{ color: "var(--texto-secundario)" }}>IP</small><br /><code>{item.ip_address}</code></div>
                      <div><small style={{ color: "var(--texto-secundario)" }}>Sistema e dispositivo</small><br />{item.operating_system} · {item.device_type}</div>
                      <div><small style={{ color: "var(--texto-secundario)" }}>Navegador</small><br />{item.browser}</div>
                    </div>
                    {item.last_seen_at && <p style={{ margin: "8px 0 0", fontSize: ".82rem", color: "var(--texto-secundario)" }}>Última atividade: {new Date(item.last_seen_at).toLocaleString("pt-BR")}</p>}
                    {item.end_reason_label && <p style={{ margin: "6px 0 0", fontSize: ".82rem", color: "var(--texto-secundario)" }}>Situação: {item.end_reason_label}</p>}
                    {item.risk_reasons.length > 0 && (
                      <ul style={{ margin: "8px 0 0", paddingLeft: 20, color: item.risk_level === "alto" ? "var(--alerta)" : "var(--texto-secundario)" }}>
                        {item.risk_reasons.map((reason) => <li key={reason.code}>{reason.message}</li>)}
                      </ul>
                    )}
                  </article>
                ))}
                {!historico.items.length && <p style={{ color: "var(--texto-secundario)" }}>Nenhum acesso registrado desde a ativação deste controle.</p>}
              </div>
              {historico.total > historico.items.length && (
                <button className="botao botao--secundario" style={{ marginTop: 12 }} disabled={carregandoAcessos} onClick={() => carregarAcessos(historico.items.length, true)}>
                  {carregandoAcessos ? "Carregando…" : `Mostrar mais (${historico.total - historico.items.length} restantes)`}
                </button>
              )}
            </>
          )}
        </section>
      )}

      <section className="cartao" style={{ maxWidth: 900, marginTop: 16 }}>
        <p className="eyebrow">Senha do Cardiology Spaces</p>
        <p style={{ color: "var(--texto-secundario)", fontSize: ".88rem" }}>A troca administrativa revoga as sessões anteriores da conta.</p>
        <div className="grade grade--2">
          <div><label>Nova senha</label><input type="password" value={novaSenha} autoComplete="new-password" onChange={(e) => setNovaSenha(e.target.value)} /></div>
          <div><label>Confirmar nova senha</label><input type="password" value={senha2} autoComplete="new-password" onChange={(e) => setSenha2(e.target.value)} /></div>
        </div>
        <button className="botao botao--secundario" style={{ marginTop: 12 }} disabled={alterandoSenha || novaSenha.length < 8 || novaSenha !== senha2} onClick={trocarSenha}>{alterandoSenha ? "Alterando…" : "Alterar senha"}</button>
      </section>

      {usuario.corvia_mail && (
        <section className="cartao" style={{ maxWidth: 900, marginTop: 16 }}>
          <p className="eyebrow">Senha do CorVIA Mail</p>
          <strong>{usuario.corvia_mail.email_address}</strong>
          <p style={{ color: "var(--texto-secundario)", fontSize: ".88rem" }}>
            A caixa possui senha própria, independente do Cardiology Spaces. A redefinição também revoga sessões anteriores do e-mail.
          </p>
          <div className="grade grade--2">
            <div><label>Nova senha do e-mail</label><input type="password" value={novaSenhaMail} autoComplete="new-password" onChange={(e) => setNovaSenhaMail(e.target.value)} /></div>
            <div><label>Confirmar senha do e-mail</label><input type="password" value={senhaMail2} autoComplete="new-password" onChange={(e) => setSenhaMail2(e.target.value)} /></div>
          </div>
          <button className="botao botao--secundario" style={{ marginTop: 12 }} disabled={alterandoSenhaMail || novaSenhaMail.length < 8 || novaSenhaMail !== senhaMail2} onClick={trocarSenhaMail}>{alterandoSenhaMail ? "Alterando…" : "Alterar senha do CorVIA Mail"}</button>
        </section>
      )}

      <section className="cartao" style={{ maxWidth: 900, marginTop: 16, borderColor: "rgba(251,113,133,.5)" }}>
        <p className="eyebrow" style={{ color: "#fb7185" }}>Zona de exclusão definitiva</p>
        <h2 style={{ marginTop: 4 }}>Excluir definitivamente do Cardiology Spaces + CorVIA Mail</h2>
        <p style={{ color: "var(--texto-secundario)" }}>
          Esta ação é irreversível. Remove a conta local e, se houver, a caixa nativa do CorVIA Mail.
          Contas administrativas e qualquer conta com cobrança Stripe relevante são bloqueadas.
        </p>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 10 }}>
          <span className={`selo ${usuario.gratuito ? "selo--sucesso" : "selo--atencao"}`}>{usuario.gratuito ? "Conta sem cobrança ativa" : "Revisar cobrança"}</span>
          {usuario.corvia_mail && <span className="selo selo--info">CorVIA Mail: {usuario.corvia_mail.email_address}</span>}
        </div>
        {!usuario.pode_excluir_definitivamente && <p style={{ color: "var(--alerta)" }}>{usuario.bloqueio_exclusao}</p>}
        <label>Para confirmar, digite exatamente: <strong>{usuario.email}</strong></label>
        <input value={confirmarEmail} onChange={(e) => setConfirmarEmail(e.target.value)} placeholder={usuario.email} />
        <label style={{ display: "flex", gap: 8, alignItems: "flex-start", marginTop: 10, fontWeight: 500 }}>
          <input type="checkbox" style={{ width: "auto", marginTop: 3 }} checked={confirmarExclusao} onChange={(e) => setConfirmarExclusao(e.target.checked)} />
          <span>Entendo que a exclusão é definitiva e autorizo remover também a caixa do CorVIA Mail, se existir.</span>
        </label>
        <button
          className="botao botao--secundario"
          style={{ marginTop: 12, borderColor: "#fb7185" }}
          disabled={!usuario.pode_excluir_definitivamente || !emailConfere || !confirmarExclusao || excluindo}
          onClick={excluirDefinitivamente}
        >
          {excluindo ? "Excluindo…" : "Excluir definitivamente do OS e Mail"}
        </button>
      </section>
    </>
  );
}
