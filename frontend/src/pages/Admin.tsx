import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import { Carregando, Erro } from "../components/Estado";

type Usuario = {
  id: number; email: string; full_name: string; crm: string | null;
  birth_date: string | null; cpf: string | null; profession: string | null;
  council_name: string | null; council_number: string | null; council_state: string | null;
  specialty: string | null; professional_title: string | null;
  workplace_name: string | null; workplace_department: string | null;
  workplace_role: string | null; workplace_notes: string | null;
  include_workplace_on_documents: boolean; role: string; status: string; is_active: boolean;
  rejection_note: string | null; created_at: string; convidado: boolean; investidor: boolean;
};

type KycWaiverConfig = {
  professional_front: boolean; professional_back: boolean; personal_front: boolean;
  personal_back: boolean; personal_digital: boolean; selfie: boolean;
};

type KycWaiverResponse = {
  user_id: number; convidado: boolean; waivers: KycWaiverConfig; kyc_status?: string | null;
};

type RecoveryResponse = { user_id: number; login_email: string; recovery_email: string | null };
type EmailStatus = {
  smtp_configurado: boolean; smtp_from_canonico: boolean; smtp_user_canonico: boolean;
  smtp_host_configurado: boolean;
  ultimos_envios: Array<{ tipo: string; sucesso: boolean; erro: string | null; created_at: string; destino_dominio: string }>;
};

type PreAutorizacaoConvidado = {
  id: number; email: string | null; nome_completo: string | null;
  incluir_corvia_mail: boolean; observacao: string | null;
  criado_em: string; usado_em: string | null; usado_por_user_id: number | null;
};

type PedidoTesteGoogle = {
  id: number; user_id: number; google_email: string; status: string;
  created_at: string; liberado_em: string | null;
};

const KYC_WAIVERS_VAZIAS: KycWaiverConfig = {
  professional_front: false, professional_back: false, personal_front: false,
  personal_back: false, personal_digital: false, selfie: false,
};

const ROTULOS_KYC_WAIVER: Array<[keyof KycWaiverConfig, string]> = [
  ["professional_front", "Documento profissional — frente"],
  ["professional_back", "Documento profissional — verso"],
  ["personal_front", "Documento pessoal — frente"],
  ["personal_back", "Documento pessoal — verso"],
  ["personal_digital", "Documento pessoal digital (PDF)"],
  ["selfie", "Selfie ao vivo"],
];

const CONSELHOS = ["CRM", "CRO", "CRBM", "COREN", "CRF", "CREFITO", "CRN", "CRP", "CREF", "CRESS", "OUTRO"];
const TITULOS = ["", "Sr.", "Sra.", "Dr.", "Dra.", "Prof.", "Profa.", "Prof. Dr.", "Profa. Dra.", "Me.", "Ma.", "Esp."];
const UFS = ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"];
const PERFIS = [
  { valor: "admin", rotulo: "Administrador" }, { valor: "medico", rotulo: "Médico" },
  { valor: "residente", rotulo: "Residente" }, { valor: "leitor", rotulo: "Leitor" },
];

function idade(dataISO: string | null): string {
  if (!dataISO) return "";
  return `${Math.floor((Date.now() - new Date(dataISO).getTime()) / (365.25 * 86400000))} anos`;
}

function emailValido(email: string) {
  const v = email.trim().toLowerCase();
  return v.includes("@") && !v.startsWith("@") && !v.endsWith("@");
}

function senhaProvisoriaAleatoria(): string {
  const bytes = new Uint8Array(24);
  crypto.getRandomValues(bytes);
  return Array.from(bytes, (b) => b.toString(16).padStart(2, "0")).join("");
}

function RecoveryEditor({ u }: { u: Usuario }) {
  const [aberto, setAberto] = useState(false);
  const [email, setEmail] = useState("");
  const [original, setOriginal] = useState<string | null>(null);
  const [carregando, setCarregando] = useState(false);
  const [acao, setAcao] = useState("");
  const [mensagem, setMensagem] = useState("");
  const [erro, setErro] = useState("");

  if (u.investidor) return null;

  async function abrir() {
    const proximo = !aberto;
    setAberto(proximo);
    if (!proximo || original !== null) return;
    setCarregando(true); setErro("");
    try {
      const r = await api.get<RecoveryResponse>(`/admin/users/${u.id}/recovery-email`);
      setOriginal(r.recovery_email);
      setEmail(r.recovery_email ?? "");
    } catch (e) {
      setErro(e instanceof Error ? e.message : "Não foi possível consultar o canal de recuperação.");
    } finally { setCarregando(false); }
  }

  async function salvar() {
    setAcao("salvar"); setErro(""); setMensagem("");
    try {
      const r = await api.put<RecoveryResponse>(`/admin/users/${u.id}/recovery-email`, { recovery_email: email.trim().toLowerCase() });
      setOriginal(r.recovery_email); setEmail(r.recovery_email ?? "");
      setMensagem("E-mail secundário salvo; a confirmação foi enviada para esse endereço.");
    } catch (e) { setErro(e instanceof Error ? e.message : "Não foi possível salvar."); }
    finally { setAcao(""); }
  }

  async function disparar(tipo: "reset" | "acesso") {
    setAcao(tipo); setErro(""); setMensagem("");
    try {
      const rota = tipo === "reset" ? "enviar-recuperacao" : "reenviar-acesso";
      await api.post(`/admin/users/${u.id}/${rota}`, {});
      setMensagem(tipo === "reset" ? "Link de redefinição enviado ao e-mail secundário." : "Mensagem de acesso reenviada ao e-mail secundário.");
    } catch (e) { setErro(e instanceof Error ? e.message : "Falha no envio."); }
    finally { setAcao(""); }
  }

  const diferente = email.trim().toLowerCase() !== u.email.trim().toLowerCase();
  return (
    <div style={{ marginTop: 8 }}>
      <button className="botao botao--secundario" style={{ padding: "0.3rem 0.65rem" }} onClick={abrir}>
        {aberto ? "Fechar recuperação" : "Acesso e recuperação"}
      </button>
      {aberto && (
        <div className="cartao" style={{ marginTop: 8, padding: "0.75rem" }}>
          <strong style={{ fontSize: "0.86rem" }}>Segundo e-mail independente</strong>
          <p style={{ color: "var(--texto-secundario)", fontSize: "0.78rem", margin: "0.25rem 0 0.6rem" }}>
            Obrigatório para contas reais. Se o login for @corvia.med.br, use Gmail, Outlook, iCloud ou outro endereço externo.
          </p>
          {carregando ? <Carregando texto="Consultando…" /> : (
            <>
              <input type="email" value={email} placeholder="email.externo@provedor.com"
                     onChange={(e) => setEmail(e.target.value)} />
              <div style={{ display: "flex", gap: 7, flexWrap: "wrap", marginTop: 7 }}>
                <button className="botao" disabled={!emailValido(email) || !diferente || !!acao} onClick={salvar}>
                  {acao === "salvar" ? "Salvando…" : "Salvar canal"}
                </button>
                <button className="botao botao--secundario" disabled={!original || !!acao} onClick={() => disparar("reset")}>Enviar troca de senha</button>
                <button className="botao botao--secundario" disabled={!original || !!acao || u.status !== "aprovado" || !u.is_active} onClick={() => disparar("acesso")}>Reenviar acesso</button>
              </div>
            </>
          )}
          {mensagem && <p style={{ color: "var(--sucesso)", fontSize: "0.78rem", marginTop: 7 }}>{mensagem}</p>}
          {erro && <p style={{ color: "var(--alerta)", fontSize: "0.78rem", marginTop: 7 }}>{erro}</p>}
        </div>
      )}
    </div>
  );
}

function KycWaiversEditor({ u }: { u: Usuario }) {
  const [aberto, setAberto] = useState(false);
  const [waivers, setWaivers] = useState<KycWaiverConfig>({ ...KYC_WAIVERS_VAZIAS });
  const [carregado, setCarregado] = useState(false);
  const [salvando, setSalvando] = useState(false);
  const [erro, setErro] = useState("");
  const [status, setStatus] = useState<string | null>(null);

  async function alternarPainel() {
    const proximo = !aberto; setAberto(proximo);
    if (proximo && !carregado) {
      setErro("");
      try {
        const r = await api.get<KycWaiverResponse>(`/admin/users/${u.id}/kyc-waivers`);
        setWaivers(r.waivers); setCarregado(true);
      } catch (e) { setErro(e instanceof Error ? e.message : "Não foi possível carregar as dispensas KYC."); }
    }
  }

  async function salvar() {
    setSalvando(true); setErro("");
    try {
      const r = await api.put<KycWaiverResponse>(`/admin/users/${u.id}/kyc-waivers`, waivers);
      setWaivers(r.waivers); setStatus(r.kyc_status ?? null);
    } catch (e) { setErro(e instanceof Error ? e.message : "Não foi possível salvar as dispensas KYC."); }
    finally { setSalvando(false); }
  }

  if (!u.convidado) return null;
  return <div style={{ marginTop: 8 }}>
    <button className="botao botao--secundario" style={{ padding: "0.3rem 0.65rem" }} onClick={alternarPainel}>{aberto ? "Fechar dispensas KYC" : "Dispensas KYC"}</button>
    {aberto && <div className="cartao" style={{ padding: "0.65rem", marginTop: 8 }}>
      <div style={{ fontSize: "0.78rem", color: "var(--texto-secundario)", marginBottom: 6 }}>Marque somente requisitos dispensados. O backend reavalia o KYC imediatamente.</div>
      {ROTULOS_KYC_WAIVER.map(([campo, rotulo]) => <label key={campo} style={{ display: "flex", gap: 7, alignItems: "center", fontWeight: 400, marginTop: 5 }}>
        <input type="checkbox" style={{ width: "auto" }} checked={waivers[campo]} onChange={(e) => setWaivers({ ...waivers, [campo]: e.target.checked })} />
        <span>Dispensar {rotulo}</span>
      </label>)}
      {status && <div className="eyebrow" style={{ marginTop: 7 }}>KYC após reavaliação: {status}</div>}
      {erro && <div style={{ color: "var(--alerta)", fontSize: "0.8rem", marginTop: 7 }}>{erro}</div>}
      <button className="botao" style={{ marginTop: 8 }} disabled={salvando || !carregado} onClick={salvar}>{salvando ? "Salvando…" : "Salvar dispensas"}</button>
    </div>}
  </div>;
}

function SolicitacaoCard({ u, aoDecidir }: { u: Usuario; aoDecidir: () => void }) {
  const [perfil, setPerfil] = useState("medico");
  const [rejeitando, setRejeitando] = useState(false);
  const [nota, setNota] = useState("");
  const [erro, setErro] = useState("");
  const [enviando, setEnviando] = useState(false);
  async function decidir(aprovar: boolean) {
    setErro(""); setEnviando(true);
    try { await api.post(`/admin/users/${u.id}/decidir`, { aprovar, role: perfil, nota: nota || null }); aoDecidir(); }
    catch (e) { setErro(e instanceof Error ? e.message : "Não foi possível registrar a decisão."); setEnviando(false); }
  }
  return <div className="cartao cartao--clinico">
    <strong>{u.full_name}</strong><span className="eyebrow" style={{ marginLeft: 8 }}>{idade(u.birth_date)}</span>
    <div style={{ fontSize: "0.88rem", marginTop: 4 }}>{u.profession} — {u.council_name} {u.council_number}/{u.council_state}{u.specialty && <> · {u.specialty}</>}</div>
    <div style={{ fontSize: "0.82rem", color: "var(--texto-secundario)", marginTop: 2 }}>{u.email} · CPF {u.cpf} · solicitado em {new Date(u.created_at).toLocaleDateString("pt-BR")}</div>
    <RecoveryEditor u={u} />
    <div style={{ display: "flex", gap: 8, alignItems: "center", marginTop: "0.8rem", flexWrap: "wrap" }}>
      <select value={perfil} onChange={(e) => setPerfil(e.target.value)} style={{ maxWidth: 180 }}>{PERFIS.map((p) => <option key={p.valor} value={p.valor}>{p.rotulo}</option>)}</select>
      <button className="botao" onClick={() => decidir(true)} disabled={enviando}>Aprovar</button>
      <button className="botao botao--secundario" onClick={() => setRejeitando(!rejeitando)}>Rejeitar</button>
    </div>
    {rejeitando && <div style={{ marginTop: "0.6rem" }}><input placeholder="Motivo (opcional, fica registrado)" value={nota} onChange={(e) => setNota(e.target.value)} /><button className="botao botao--secundario" style={{ marginTop: 6 }} onClick={() => decidir(false)} disabled={enviando}>Confirmar rejeição</button></div>}
    {erro && <p style={{ color: "var(--alerta)", fontSize: "0.82rem", marginTop: 6 }}>{erro}</p>}
  </div>;
}

function PedidoTesteGoogleCard({ p, aoLiberar }: { p: PedidoTesteGoogle; aoLiberar: () => void }) {
  const [enviando, setEnviando] = useState(false); const [erro, setErro] = useState("");
  async function liberar() { setErro(""); setEnviando(true); try { await api.post(`/admin/google-teste/${p.id}/liberar`, {}); aoLiberar(); } catch (e) { setErro(e instanceof Error ? e.message : "Não foi possível liberar o pedido."); setEnviando(false); } }
  return <div className="cartao cartao--clinico"><strong>{p.google_email}</strong><div style={{ fontSize: "0.82rem", color: "var(--texto-secundario)", marginTop: 2 }}>pedido em {new Date(p.created_at).toLocaleString("pt-BR")}</div><p style={{ fontSize: "0.82rem", marginTop: 6 }}>Adicione este e-mail como testador no Google Cloud Console e só então confirme abaixo.</p><button className="botao" style={{ marginTop: 8 }} onClick={liberar} disabled={enviando}>{enviando ? "Liberando…" : "Já adicionei — marcar como liberado"}</button>{erro && <p style={{ color: "var(--alerta)", fontSize: "0.82rem", marginTop: 6 }}>{erro}</p>}</div>;
}

function EmailTransacionalPanel() {
  const [status, setStatus] = useState<EmailStatus | null>(null);
  const [destino, setDestino] = useState("");
  const [mensagem, setMensagem] = useState("");
  const [erro, setErro] = useState("");
  const [testando, setTestando] = useState(false);
  const carregar = () => api.get<EmailStatus>("/admin/account-access/email-status").then(setStatus).catch((e) => setErro(e instanceof Error ? e.message : "Falha ao consultar SMTP."));
  useEffect(() => { carregar(); }, []);
  async function testar() {
    setTestando(true); setErro(""); setMensagem("");
    try { await api.post("/admin/account-access/email-probe", { email: destino.trim().toLowerCase() }); setMensagem(`Servidor confirmou envio por contato@corvia.med.br para ${destino.trim()}. Confirme também o recebimento externo.`); carregar(); }
    catch (e) { setErro(e instanceof Error ? e.message : "O SMTP não confirmou o envio."); }
    finally { setTestando(false); }
  }
  const verde = status && status.smtp_configurado && status.smtp_from_canonico && status.smtp_user_canonico && status.smtp_host_configurado;
  return <div className="cartao cartao--clinico" style={{ marginTop: "0.8rem", maxWidth: 760 }}>
    <p className="eyebrow">E-mail transacional</p><h2 style={{ margin: "0.2rem 0 0.5rem", fontSize: "1rem" }}>contato@corvia.med.br</h2>
    {status ? <div style={{ display: "flex", gap: 7, flexWrap: "wrap" }}>
      <span className={`selo ${status.smtp_configurado ? "selo--revisado" : "selo--pendente"}`}>SMTP {status.smtp_configurado ? "configurado" : "ausente"}</span>
      <span className={`selo ${status.smtp_user_canonico ? "selo--revisado" : "selo--pendente"}`}>autenticação {status.smtp_user_canonico ? "canônica" : "incorreta"}</span>
      <span className={`selo ${status.smtp_from_canonico ? "selo--revisado" : "selo--pendente"}`}>remetente {status.smtp_from_canonico ? "correto" : "incorreto"}</span>
    </div> : <Carregando texto="Consultando SMTP…" />}
    <p style={{ color: "var(--texto-secundario)", fontSize: "0.8rem", margin: "0.6rem 0" }}>{verde ? "Configuração declarada completa. Faça um probe para provar a entrega real." : "Bloqueador de release: o canal transacional ainda não está completamente configurado."}</p>
    <div style={{ display: "flex", gap: 7, flexWrap: "wrap" }}><input type="email" placeholder="e-mail externo para teste" value={destino} onChange={(e) => setDestino(e.target.value)} style={{ flex: "1 1 260px" }} /><button className="botao" disabled={!emailValido(destino) || testando || !verde} onClick={testar}>{testando ? "Testando…" : "Enviar teste real"}</button></div>
    {mensagem && <p style={{ color: "var(--sucesso)", fontSize: "0.8rem", marginTop: 7 }}>{mensagem}</p>}{erro && <p style={{ color: "var(--alerta)", fontSize: "0.8rem", marginTop: 7 }}>{erro}</p>}
  </div>;
}

function PreAutorizacoesConvidado() {
  const [lista, setLista] = useState<PreAutorizacaoConvidado[] | null>(null); const [erro, setErro] = useState(""); const [enviando, setEnviando] = useState(false);
  const [dados, setDados] = useState({ email: "", nome_completo: "", incluir_corvia_mail: true, observacao: "" });
  const recarregar = () => api.get<PreAutorizacaoConvidado[]>("/admin/convidados-pre-autorizados").then(setLista).catch((e) => setErro(e instanceof Error ? e.message : "Erro ao carregar."));
  useEffect(() => { recarregar(); }, []);
  async function cadastrar() { setErro(""); setEnviando(true); try { await api.post("/admin/convidados-pre-autorizados", { email: dados.email.trim() || null, nome_completo: dados.nome_completo.trim() || null, incluir_corvia_mail: dados.incluir_corvia_mail, observacao: dados.observacao.trim() || null }); setDados({ email: "", nome_completo: "", incluir_corvia_mail: true, observacao: "" }); recarregar(); } catch (e) { setErro(e instanceof Error ? e.message : "Não foi possível cadastrar a pré-autorização."); } finally { setEnviando(false); } }
  async function revogar(id: number) { if (!confirm("Revogar esta pré-autorização?")) return; try { await api.delete(`/admin/convidados-pre-autorizados/${id}`); recarregar(); } catch (e) { setErro(e instanceof Error ? e.message : "Não foi possível revogar."); } }
  const podeCadastrar = Boolean((dados.email.trim() || dados.nome_completo.trim()) && !enviando); const pendentes = lista?.filter((l) => !l.usado_em) ?? []; const usadas = lista?.filter((l) => l.usado_em) ?? [];
  return <><h2 style={{ marginTop: "1.6rem" }}>Pré-autorizações de convidado {pendentes.length > 0 && <span className="selo selo--pendente">{pendentes.length}</span>}</h2><p style={{ color: "var(--texto-secundario)", maxWidth: "60ch" }}>Pré-autorize um convidado antes do autocadastro. O autocadastro em si continuará exigindo e-mail secundário de recuperação.</p><div className="cartao" style={{ maxWidth: 560, marginTop: "0.6rem" }}><label htmlFor="pa-email">E-mail de login</label><input id="pa-email" type="email" value={dados.email} onChange={(e) => setDados((d) => ({ ...d, email: e.target.value }))} /><label htmlFor="pa-nome" style={{ marginTop: "0.6rem" }}>Nome completo</label><input id="pa-nome" value={dados.nome_completo} onChange={(e) => setDados((d) => ({ ...d, nome_completo: e.target.value }))} /><label style={{ display: "flex", gap: 8, alignItems: "center", fontWeight: 400, marginTop: "0.8rem" }}><input type="checkbox" style={{ width: "auto" }} checked={dados.incluir_corvia_mail} onChange={(e) => setDados((d) => ({ ...d, incluir_corvia_mail: e.target.checked }))} />Incluir CorVIA Mail</label><input style={{ marginTop: "0.6rem" }} placeholder="Observação opcional" value={dados.observacao} onChange={(e) => setDados((d) => ({ ...d, observacao: e.target.value }))} /><button className="botao" style={{ marginTop: "0.8rem" }} onClick={cadastrar} disabled={!podeCadastrar}>{enviando ? "Cadastrando…" : "Cadastrar pré-autorização"}</button>{erro && <p style={{ color: "var(--alerta)", fontSize: "0.82rem" }}>{erro}</p>}</div>{lista === null ? <Carregando /> : <div className="grade" style={{ marginTop: "0.8rem" }}>{pendentes.map((l) => <div className="cartao cartao--clinico" key={l.id}><strong>{l.nome_completo || l.email}</strong>{l.email && <div style={{ color: "var(--texto-secundario)", fontSize: "0.82rem" }}>{l.email}</div>}<button className="botao botao--secundario" style={{ marginTop: 8 }} onClick={() => revogar(l.id)}>Revogar</button></div>)}{usadas.map((l) => <div className="cartao" key={l.id} style={{ opacity: .6 }}><strong>{l.nome_completo || l.email}</strong> <span className="selo selo--revisado">já cadastrado</span></div>)}</div>}</>;
}

export default function Admin() {
  const [lista, setLista] = useState<Usuario[] | null>(null); const [erro, setErro] = useState(""); const [enviando, setEnviando] = useState(false);
  const [novo, setNovo] = useState({ email: "", recovery_email: "", full_name: "", crm: "", profession: "", council_name: "CRM", council_number: "", council_state: "", specialty: "", professional_title: "", workplace_name: "", workplace_department: "", workplace_role: "", workplace_notes: "", include_workplace_on_documents: false, profile_completion_required: false, role: "medico", tipo_acesso: "normal" as "normal" | "convidado" | "investidor" });
  const [waiversNovo, setWaiversNovo] = useState<KycWaiverConfig>({ ...KYC_WAIVERS_VAZIAS }); const [pedidosGoogle, setPedidosGoogle] = useState<PedidoTesteGoogle[] | null>(null);
  const recarregar = () => api.get<Usuario[]>("/admin/users").then(setLista).catch((e) => setErro(e.message));
  const recarregarPedidosGoogle = () => api.get<PedidoTesteGoogle[]>("/admin/google-teste?status=pendente").then(setPedidosGoogle).catch(() => setPedidosGoogle([]));
  useEffect(() => { recarregar(); recarregarPedidosGoogle(); }, []);

  async function criar() {
    setErro(""); setEnviando(true); const investidor = novo.tipo_acesso === "investidor";
    const payload = { email: novo.email.trim().toLowerCase(), full_name: novo.full_name.trim(), crm: investidor ? null : (novo.crm.trim() || null), profession: investidor ? null : (novo.profession.trim() || null), council_name: investidor ? null : (novo.council_name || null), council_number: investidor ? null : (novo.council_number.trim() || null), council_state: investidor ? null : (novo.council_state || null), specialty: investidor ? null : (novo.specialty.trim() || null), professional_title: investidor ? null : (novo.professional_title || null), workplace_name: investidor ? null : (novo.workplace_name.trim() || null), workplace_department: investidor ? null : (novo.workplace_department.trim() || null), workplace_role: investidor ? null : (novo.workplace_role.trim() || null), workplace_notes: investidor ? null : (novo.workplace_notes.trim() || null), include_workplace_on_documents: investidor ? false : novo.include_workplace_on_documents, profile_completion_required: investidor ? false : novo.profile_completion_required, role: investidor ? "leitor" : novo.role, password: investidor ? "CorVIAOS" : senhaProvisoriaAleatoria(), tipo_acesso: novo.tipo_acesso, kyc_waivers: novo.tipo_acesso === "convidado" ? waiversNovo : null };
    try {
      if (investidor) await api.post("/admin/users", payload);
      else await api.post("/auth/admin/criar-usuario-com-recuperacao", { ...payload, recovery_email: novo.recovery_email.trim().toLowerCase() });
      setNovo({ email: "", recovery_email: "", full_name: "", crm: "", profession: "", council_name: "CRM", council_number: "", council_state: "", specialty: "", professional_title: "", workplace_name: "", workplace_department: "", workplace_role: "", workplace_notes: "", include_workplace_on_documents: false, profile_completion_required: false, role: "medico", tipo_acesso: "normal" }); setWaiversNovo({ ...KYC_WAIVERS_VAZIAS }); recarregar();
    } catch (e) { setErro(e instanceof Error ? e.message : "Não foi possível criar o usuário."); }
    finally { setEnviando(false); }
  }

  async function alternar(u: Usuario) { try { await api.patch(`/admin/users/${u.id}/ativo?ativo=${!u.is_active}`, {}); recarregar(); } catch (e) { setErro(e instanceof Error ? e.message : "Não foi possível alterar o usuário."); } }
  async function alternarConvidado(u: Usuario) { try { await api.patch(`/admin/users/${u.id}/convidado?convidado=${!u.convidado}`, {}); recarregar(); } catch (e) { setErro(e instanceof Error ? e.message : "Não foi possível alterar o status de convidado."); } }
  async function alternarInvestidor(u: Usuario) { try { await api.patch(`/admin/users/${u.id}/investidor?investidor=${!u.investidor}`, {}); recarregar(); } catch (e) { setErro(e instanceof Error ? e.message : "Não foi possível alterar o status de investidor."); } }

  const investidorNovo = novo.tipo_acesso === "investidor";
  const recoveryOk = investidorNovo || (emailValido(novo.recovery_email) && novo.recovery_email.trim().toLowerCase() !== novo.email.trim().toLowerCase());
  const podeCriar = Boolean(emailValido(novo.email) && novo.full_name.trim() && recoveryOk && !enviando);
  const pendentes = lista?.filter((u) => u.status === "pendente") ?? []; const decididos = lista?.filter((u) => u.status !== "pendente") ?? [];

  return <>
    <p className="eyebrow">Administração</p><h1>Usuários</h1>
    <Link to="/admin/usuarios" className="cartao cartao--clinico" style={{ display: "block", marginTop: "0.8rem", maxWidth: 760, textDecoration: "none" }}><strong>Ficha completa de assinantes →</strong><p style={{ margin: "0.3rem 0 0", color: "var(--texto-secundario)", fontSize: "0.86rem" }}>Busca, KYC, assinatura, documentos e histórico administrativo.</p></Link>
    <EmailTransacionalPanel />
    {erro && <div style={{ marginTop: "0.8rem", maxWidth: 760 }}><Erro mensagem={erro} /></div>}
    {lista === null ? <Carregando /> : <>
      {pendentes.length > 0 && <><h2 style={{ marginTop: "1.2rem" }}>Solicitações de acesso <span className="selo selo--pendente">{pendentes.length}</span></h2><p style={{ color: "var(--texto-secundario)", maxWidth: "60ch" }}>Confira o registro profissional e, para cadastros legados, garanta um segundo e-mail antes de aprovar.</p><div className="grade" style={{ marginTop: "0.6rem" }}>{pendentes.map((u) => <SolicitacaoCard key={u.id} u={u} aoDecidir={recarregar} />)}</div></>}
      {pedidosGoogle !== null && pedidosGoogle.length > 0 && <><h2 style={{ marginTop: "1.6rem" }}>Liberação de teste do Google <span className="selo selo--pendente">{pedidosGoogle.length}</span></h2><div className="grade" style={{ marginTop: "0.6rem" }}>{pedidosGoogle.map((p) => <PedidoTesteGoogleCard key={p.id} p={p} aoLiberar={recarregarPedidosGoogle} />)}</div></>}
      <PreAutorizacoesConvidado />

      <h2 style={{ marginTop: "1.6rem" }}>Criar conta diretamente</h2>
      <p style={{ color: "var(--texto-secundario)", maxWidth: "68ch" }}>Contas reais exigem um segundo e-mail externo. O CorVIA envia a ele um link de primeiro acesso para o usuário escolher a própria senha; nenhuma senha é copiada ou enviada em texto. A conta Investidor global continua sem dados pessoais.</p>
      <div className="cartao cartao--clinico" style={{ marginTop: "0.8rem", maxWidth: 760 }}><p className="eyebrow">Nova conta</p>
        <fieldset style={{ border: "1px solid var(--borda)", borderRadius: 8, padding: "0.7rem 0.9rem", margin: 0 }}><legend style={{ padding: "0 0.3rem", fontWeight: 650 }}>Tipo de acesso</legend>{([ ["normal", "Assinante normal"], ["convidado", "Convidado — acesso gratuito"], ["investidor", "Investidor — demonstração somente leitura"] ] as const).map(([valor, rotulo]) => <label key={valor} style={{ display: "flex", gap: 8, alignItems: "flex-start", fontWeight: 400, marginTop: 7 }}><input type="radio" name="tipo-acesso" style={{ width: "auto", marginTop: 3 }} checked={novo.tipo_acesso === valor} onChange={() => setNovo({ ...novo, tipo_acesso: valor, role: valor === "investidor" ? "leitor" : novo.role, profile_completion_required: valor === "investidor" ? false : novo.profile_completion_required, recovery_email: valor === "investidor" ? "" : novo.recovery_email })} /><span><strong>{rotulo}</strong></span></label>)}</fieldset>
        {novo.tipo_acesso === "convidado" && <fieldset style={{ border: "1px solid var(--borda)", borderRadius: 8, padding: "0.7rem 0.9rem", marginTop: "0.8rem" }}><legend>Dispensas KYC individuais</legend>{ROTULOS_KYC_WAIVER.map(([campo, rotulo]) => <label key={campo} style={{ display: "flex", gap: 8, alignItems: "center", fontWeight: 400, marginTop: 7 }}><input type="checkbox" style={{ width: "auto" }} checked={waiversNovo[campo]} onChange={(e) => setWaiversNovo({ ...waiversNovo, [campo]: e.target.checked })} /><span>Dispensar {rotulo}</span></label>)}</fieldset>}
        <div className="grade grade--2" style={{ marginTop: "0.9rem" }}><div><label htmlFor="nome">Nome da conta</label><input id="nome" value={novo.full_name} onChange={(e) => setNovo({ ...novo, full_name: e.target.value })} /></div><div><label htmlFor="email">E-mail de login</label><input id="email" type="email" value={novo.email} onChange={(e) => setNovo({ ...novo, email: e.target.value })} /></div>{!investidorNovo && <div style={{ gridColumn: "1 / -1" }}><label htmlFor="recovery-email-admin">Segundo e-mail externo para recuperação</label><input id="recovery-email-admin" type="email" placeholder="Gmail, Outlook, iCloud ou outro endereço independente" value={novo.recovery_email} onChange={(e) => setNovo({ ...novo, recovery_email: e.target.value })} /><small style={{ color: "var(--texto-secundario)" }}>Obrigatório e diferente do login. Receberá confirmação, primeiro acesso e futuras trocas de senha.</small></div>}
          {!investidorNovo && <><div><label htmlFor="tratamento-admin">Como será chamado(a)</label><select id="tratamento-admin" value={novo.professional_title} onChange={(e) => setNovo({ ...novo, professional_title: e.target.value })}>{TITULOS.map((t) => <option key={t || "sem"} value={t}>{t || "Sem título"}</option>)}</select></div><div><label htmlFor="profissao-admin">Profissão</label><input id="profissao-admin" value={novo.profession} onChange={(e) => setNovo({ ...novo, profession: e.target.value })} /></div><div><label htmlFor="conselho-admin">Conselho</label><select id="conselho-admin" value={novo.council_name} onChange={(e) => setNovo({ ...novo, council_name: e.target.value })}>{CONSELHOS.map((c) => <option key={c} value={c}>{c}</option>)}</select></div><div><label htmlFor="registro-admin">Nº de registro</label><input id="registro-admin" value={novo.council_number} onChange={(e) => setNovo({ ...novo, council_number: e.target.value })} /></div><div><label htmlFor="uf-admin">UF</label><select id="uf-admin" value={novo.council_state} onChange={(e) => setNovo({ ...novo, council_state: e.target.value })}><option value="">—</option>{UFS.map((uf) => <option key={uf} value={uf}>{uf}</option>)}</select></div><div><label htmlFor="especialidade-admin">Especialidade</label><input id="especialidade-admin" value={novo.specialty} onChange={(e) => setNovo({ ...novo, specialty: e.target.value })} /></div><div><label htmlFor="crm">CRM legado (opcional)</label><input id="crm" value={novo.crm} onChange={(e) => setNovo({ ...novo, crm: e.target.value })} /></div><div><label htmlFor="perfil">Perfil</label><select id="perfil" value={novo.role} onChange={(e) => setNovo({ ...novo, role: e.target.value })}>{PERFIS.map((p) => <option key={p.valor} value={p.valor}>{p.rotulo}</option>)}</select></div></>}
        </div>
        {!investidorNovo && <><h3 style={{ fontSize: "1rem", marginTop: "1rem" }}>Local de trabalho (opcional)</h3><div className="grade grade--2"><input placeholder="Instituição, clínica ou consultório" value={novo.workplace_name} onChange={(e) => setNovo({ ...novo, workplace_name: e.target.value })} /><input placeholder="Setor/unidade" value={novo.workplace_department} onChange={(e) => setNovo({ ...novo, workplace_department: e.target.value })} /><input placeholder="Cargo/função" value={novo.workplace_role} onChange={(e) => setNovo({ ...novo, workplace_role: e.target.value })} /><input placeholder="Outras informações" value={novo.workplace_notes} onChange={(e) => setNovo({ ...novo, workplace_notes: e.target.value })} /></div><label style={{ display: "flex", gap: 8, alignItems: "center", fontWeight: 400, marginTop: 8 }}><input type="checkbox" style={{ width: "auto" }} checked={novo.include_workplace_on_documents} onChange={(e) => setNovo({ ...novo, include_workplace_on_documents: e.target.checked })} />Incluir local de trabalho nos documentos</label><label style={{ display: "flex", gap: 8, alignItems: "center", fontWeight: 400, marginTop: 8 }}><input type="checkbox" style={{ width: "auto" }} checked={novo.profile_completion_required} onChange={(e) => setNovo({ ...novo, profile_completion_required: e.target.checked })} />No primeiro acesso, completar dados pessoais e profissionais</label></>}
        {investidorNovo && <div className="cartao" style={{ marginTop: "0.9rem", borderColor: "rgba(66,202,216,.28)" }}><p className="eyebrow">Credencial fixa da demonstração</p><strong style={{ fontFamily: "var(--fonte-dados)", fontSize: "1.05rem" }}>CorVIAOS</strong><p style={{ color: "var(--texto-secundario)", fontSize: "0.82rem" }}>Sem e-mail pessoal de recuperação, KYC ou dados clínicos reais.</p></div>}
        <button className="botao" style={{ marginTop: "1rem" }} onClick={criar} disabled={!podeCriar}>{enviando ? "Criando…" : investidorNovo ? "Criar conta Investidor" : "Criar e enviar primeiro acesso"}</button>
      </div>

      <h2 style={{ marginTop: "1.6rem" }}>Contas decididas</h2><div className="grade">{decididos.map((u) => <div key={u.id} className="cartao" style={{ display: "flex", alignItems: "flex-start", gap: 12, flexWrap: "wrap" }}><div style={{ flex: "1 1 280px" }}><strong>{u.full_name}</strong> <span className="eyebrow">{PERFIS.find((p) => p.valor === u.role)?.rotulo}</span>{u.convidado && <span className="selo selo--revisado" style={{ marginLeft: 6 }}>convidado</span>}{u.investidor && <span className="selo selo--pendente" style={{ marginLeft: 6 }}>investidor — somente visualização</span>}<div style={{ fontSize: "0.86rem", color: "var(--texto-secundario)" }}>{u.email}{u.council_name && ` · ${u.council_name} ${u.council_number}/${u.council_state}`}</div><RecoveryEditor u={u} /><KycWaiversEditor u={u} />{u.status === "rejeitado" && u.rejection_note && <div style={{ color: "var(--alerta)", fontSize: "0.8rem" }}>Rejeitado: {u.rejection_note}</div>}</div><span className={`selo ${u.is_active ? "selo--revisado" : "selo--pendente"}`}>{u.status === "rejeitado" ? "rejeitado" : u.is_active ? "ativo" : "desativado"}</span>{u.status !== "rejeitado" && <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}><button className="botao botao--secundario" onClick={() => alternarConvidado(u)}>{u.convidado ? "Remover convidado" : "Marcar convidado"}</button><button className="botao botao--secundario" onClick={() => alternarInvestidor(u)}>{u.investidor ? "Remover investidor" : "Marcar investidor"}</button><button className="botao botao--secundario" onClick={() => alternar(u)}>{u.is_active ? "Desativar" : "Reativar"}</button></div>}</div>)}</div>
    </>}
  </>;
}
