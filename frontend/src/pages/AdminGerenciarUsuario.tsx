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
  corvia_mail: CorviaMail | null;
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

  function carregar() {
    if (!id) return;
    setErro("");
    api.get<UsuarioGerenciavel>(`/admin/user-management/${id}`)
      .then(setUsuario)
      .catch((e) => setErro(mensagemErro(e, "Não foi possível carregar a conta.")));
  }

  useEffect(() => { carregar(); }, [id]);

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
      setMensagem("Senha do Clinical OS alterada. As sessões anteriores foram revogadas.");
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
        Edite dados, redefina as senhas do Clinical OS e do CorVIA Mail e, quando permitido,
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

      <section className="cartao" style={{ maxWidth: 900, marginTop: 16 }}>
        <p className="eyebrow">Senha do Clinical OS</p>
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
            A caixa possui senha própria, independente do Clinical OS. A redefinição também revoga sessões anteriores do e-mail.
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
        <h2 style={{ marginTop: 4 }}>Excluir usuário do CorVIA</h2>
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
          {excluindo ? "Excluindo…" : "Excluir definitivamente"}
        </button>
      </section>
    </>
  );
}
