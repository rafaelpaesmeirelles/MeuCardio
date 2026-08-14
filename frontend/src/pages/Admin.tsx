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
  rejection_note: string | null; created_at: string; convidado: boolean;
  investidor: boolean;
};

type KycWaiverConfig = {
  professional_front: boolean;
  professional_back: boolean;
  personal_front: boolean;
  personal_back: boolean;
  personal_digital: boolean;
  selfie: boolean;
};

type KycWaiverResponse = {
  user_id: number;
  convidado: boolean;
  waivers: KycWaiverConfig;
  kyc_status?: string | null;
};

const KYC_WAIVERS_VAZIAS: KycWaiverConfig = {
  professional_front: false,
  professional_back: false,
  personal_front: false,
  personal_back: false,
  personal_digital: false,
  selfie: false,
};

const ROTULOS_KYC_WAIVER: Array<[keyof KycWaiverConfig, string]> = [
  ["professional_front", "Documento profissional — frente"],
  ["professional_back", "Documento profissional — verso"],
  ["personal_front", "Documento pessoal — frente"],
  ["personal_back", "Documento pessoal — verso"],
  ["personal_digital", "Documento pessoal digital (PDF)"],
  ["selfie", "Selfie ao vivo"],
];

function KycWaiversEditor({ u }: { u: Usuario }) {
  const [aberto, setAberto] = useState(false);
  const [waivers, setWaivers] = useState<KycWaiverConfig>({ ...KYC_WAIVERS_VAZIAS });
  const [carregado, setCarregado] = useState(false);
  const [salvando, setSalvando] = useState(false);
  const [erro, setErro] = useState("");
  const [status, setStatus] = useState<string | null>(null);

  async function alternarPainel() {
    const proximo = !aberto;
    setAberto(proximo);
    if (proximo && !carregado) {
      setErro("");
      try {
        const r = await api.get<KycWaiverResponse>(`/admin/users/${u.id}/kyc-waivers`);
        setWaivers(r.waivers);
        setCarregado(true);
      } catch (e) {
        setErro(e instanceof Error ? e.message : "Não foi possível carregar as dispensas KYC.");
      }
    }
  }

  async function salvar() {
    setSalvando(true);
    setErro("");
    try {
      const r = await api.put<KycWaiverResponse>(`/admin/users/${u.id}/kyc-waivers`, waivers);
      setWaivers(r.waivers);
      setStatus(r.kyc_status ?? null);
    } catch (e) {
      setErro(e instanceof Error ? e.message : "Não foi possível salvar as dispensas KYC.");
    } finally {
      setSalvando(false);
    }
  }

  if (!u.convidado) return null;
  return (
    <div style={{ marginTop: 8 }}>
      <button className="botao botao--secundario" style={{ padding: "0.3rem 0.65rem" }} onClick={alternarPainel}>
        {aberto ? "Fechar dispensas KYC" : "Dispensas KYC"}
      </button>
      {aberto && (
        <div style={{ border: "1px solid var(--borda)", borderRadius: 8, padding: "0.65rem", marginTop: 8 }}>
          <div style={{ fontSize: "0.78rem", color: "var(--texto-secundario)", marginBottom: 6 }}>
            Marque somente requisitos dispensados para este Convidado. O backend reavalia o KYC imediatamente.
          </div>
          {ROTULOS_KYC_WAIVER.map(([campo, rotulo]) => (
            <label key={campo} style={{ display: "flex", gap: 7, alignItems: "center", fontWeight: 400, marginTop: 5 }}>
              <input type="checkbox" style={{ width: "auto" }} checked={waivers[campo]}
                     onChange={(e) => setWaivers({ ...waivers, [campo]: e.target.checked })} />
              <span>Dispensar {rotulo}</span>
            </label>
          ))}
          {status && <div className="eyebrow" style={{ marginTop: 7 }}>KYC após reavaliação: {status}</div>}
          {erro && <div style={{ color: "var(--alerta)", fontSize: "0.8rem", marginTop: 7 }}>{erro}</div>}
          <button className="botao" style={{ marginTop: 8 }} disabled={salvando || !carregado} onClick={salvar}>
            {salvando ? "Salvando…" : "Salvar dispensas"}
          </button>
        </div>
      )}
    </div>
  );
}

type PreAutorizacaoConvidado = {
  id: number; email: string | null; nome_completo: string | null;
  incluir_corvia_mail: boolean; observacao: string | null;
  criado_em: string; usado_em: string | null; usado_por_user_id: number | null;
};

const CONSELHOS = ["CRM", "CRO", "CRBM", "COREN", "CRF", "CREFITO", "CRN", "CRP", "CREF", "CRESS", "OUTRO"];
const TITULOS = ["", "Sr.", "Sra.", "Dr.", "Dra.", "Prof.", "Profa.", "Prof. Dr.", "Profa. Dra.", "Me.", "Ma.", "Esp."];
const UFS = ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"];

const PERFIS = [
  { valor: "admin", rotulo: "Administrador" },
  { valor: "medico", rotulo: "Médico" },
  { valor: "residente", rotulo: "Residente" },
  { valor: "leitor", rotulo: "Leitor" },
];

function idade(dataISO: string | null): string {
  if (!dataISO) return "";
  const anos = Math.floor((Date.now() - new Date(dataISO).getTime()) / (365.25 * 86400000));
  return `${anos} anos`;
}

function SolicitacaoCard({ u, aoDecidir }: { u: Usuario; aoDecidir: () => void }) {
  const [perfil, setPerfil] = useState("medico");
  const [rejeitando, setRejeitando] = useState(false);
  const [nota, setNota] = useState("");
  const [erro, setErro] = useState("");
  const [enviando, setEnviando] = useState(false);

  async function decidir(aprovar: boolean) {
    setErro("");
    setEnviando(true);
    try {
      await api.post(`/admin/users/${u.id}/decidir`, { aprovar, role: perfil, nota: nota || null });
      aoDecidir();
    } catch (e) {
      setErro(e instanceof Error ? e.message : "Não foi possível registrar a decisão.");
      setEnviando(false);
    }
  }

  return (
    <div className="cartao cartao--clinico">
      <strong>{u.full_name}</strong>
      <span className="eyebrow" style={{ marginLeft: 8 }}>{idade(u.birth_date)}</span>
      <div style={{ fontSize: "0.88rem", marginTop: 4 }}>
        {u.profession} — {u.council_name} {u.council_number}/{u.council_state}
        {u.specialty && <> · {u.specialty}</>}
      </div>
      <div style={{ fontSize: "0.82rem", color: "var(--texto-secundario)", marginTop: 2 }}>
        {u.email} · CPF {u.cpf} · solicitado em {new Date(u.created_at).toLocaleDateString("pt-BR")}
      </div>

      <div style={{ display: "flex", gap: 8, alignItems: "center", marginTop: "0.8rem", flexWrap: "wrap" }}>
        <select value={perfil} onChange={(e) => setPerfil(e.target.value)} style={{ maxWidth: 180 }}>
          {PERFIS.map((p) => <option key={p.valor} value={p.valor}>{p.rotulo}</option>)}
        </select>
        <button className="botao" onClick={() => decidir(true)} disabled={enviando}>
          Aprovar
        </button>
        <button className="botao botao--secundario" onClick={() => setRejeitando(!rejeitando)}>
          Rejeitar
        </button>
      </div>

      {rejeitando && (
        <div style={{ marginTop: "0.6rem" }}>
          <input placeholder="Motivo (opcional, fica registrado)" value={nota}
                 onChange={(e) => setNota(e.target.value)} />
          <button className="botao botao--secundario" style={{ marginTop: 6 }}
                  onClick={() => decidir(false)} disabled={enviando}>
            Confirmar rejeição
          </button>
        </div>
      )}
      {erro && <p style={{ color: "var(--alerta)", fontSize: "0.82rem", marginTop: 6 }}>{erro}</p>}
    </div>
  );
}

type PedidoTesteGoogle = {
  id: number; user_id: number; google_email: string; status: string;
  created_at: string; liberado_em: string | null;
};

function PedidoTesteGoogleCard({ p, aoLiberar }: { p: PedidoTesteGoogle; aoLiberar: () => void }) {
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState("");

  async function liberar() {
    setErro("");
    setEnviando(true);
    try {
      await api.post(`/admin/google-teste/${p.id}/liberar`, {});
      aoLiberar();
    } catch (e) {
      setErro(e instanceof Error ? e.message : "Não foi possível liberar o pedido.");
      setEnviando(false);
    }
  }

  return (
    <div className="cartao cartao--clinico">
      <strong>{p.google_email}</strong>
      <div style={{ fontSize: "0.82rem", color: "var(--texto-secundario)", marginTop: 2 }}>
        pedido em {new Date(p.created_at).toLocaleString("pt-BR")}
      </div>
      <p style={{ fontSize: "0.82rem", marginTop: 6 }}>
        Antes de clicar: adicione este e-mail como testador no Google Cloud Console
        (OAuth consent screen → Test users) — este botão só registra e avisa o assinante,
        não fala com o Google.
      </p>
      <button className="botao" style={{ marginTop: 8 }} onClick={liberar} disabled={enviando}>
        {enviando ? "Liberando…" : "Já adicionei — marcar como liberado"}
      </button>
      {erro && <p style={{ color: "var(--alerta)", fontSize: "0.82rem", marginTop: 6 }}>{erro}</p>}
    </div>
  );
}

function PreAutorizacoesConvidado() {
  const [lista, setLista] = useState<PreAutorizacaoConvidado[] | null>(null);
  const [erro, setErro] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [dados, setDados] = useState({
    email: "", nome_completo: "", incluir_corvia_mail: true, observacao: "",
  });

  const recarregar = () =>
    api.get<PreAutorizacaoConvidado[]>("/admin/convidados-pre-autorizados")
      .then(setLista).catch((e) => setErro(e instanceof Error ? e.message : "Erro ao carregar."));

  useEffect(() => { recarregar(); }, []);

  async function cadastrar() {
    setErro("");
    setEnviando(true);
    try {
      await api.post("/admin/convidados-pre-autorizados", {
        email: dados.email.trim() || null,
        nome_completo: dados.nome_completo.trim() || null,
        incluir_corvia_mail: dados.incluir_corvia_mail,
        observacao: dados.observacao.trim() || null,
      });
      setDados({ email: "", nome_completo: "", incluir_corvia_mail: true, observacao: "" });
      recarregar();
    } catch (e) {
      setErro(e instanceof Error ? e.message : "Não foi possível cadastrar a pré-autorização.");
    } finally {
      setEnviando(false);
    }
  }

  async function revogar(id: number) {
    if (!confirm("Revogar esta pré-autorização? Quem ainda não se cadastrou perde o acesso automático.")) return;
    try {
      await api.delete(`/admin/convidados-pre-autorizados/${id}`);
      recarregar();
    } catch (e) {
      setErro(e instanceof Error ? e.message : "Não foi possível revogar.");
    }
  }

  const podeCadastrar = (dados.email.trim() || dados.nome_completo.trim()) && !enviando;
  const pendentes = lista?.filter((l) => !l.usado_em) ?? [];
  const usadas = lista?.filter((l) => l.usado_em) ?? [];

  return (
    <>
      <h2 style={{ marginTop: "1.6rem" }}>
        Pré-autorizações de convidado
        {pendentes.length > 0 && <span className="selo selo--pendente" style={{ marginLeft: 8 }}>{pendentes.length} pendente(s)</span>}
      </h2>
      <p style={{ color: "var(--texto-secundario)", maxWidth: "60ch" }}>
        Cadastre aqui um novo convidado ANTES dele se registrar — pelo e-mail que ele vai
        usar no cadastro e/ou pelo nome completo. Quando o cadastro dele casar com esta
        linha, o acesso libera automaticamente (sem revisão manual), já no plano escolhido.
      </p>

      <div className="cartao" style={{ maxWidth: 460, marginTop: "0.6rem" }}>
        <label htmlFor="pa-email">E-mail pessoal <span className="eyebrow">(opcional se tiver o nome)</span></label>
        <input id="pa-email" type="email" value={dados.email}
               onChange={(e) => setDados((d) => ({ ...d, email: e.target.value }))} />

        <label htmlFor="pa-nome" style={{ marginTop: "0.6rem" }}>
          Nome completo <span className="eyebrow">(opcional se tiver o e-mail)</span>
        </label>
        <input id="pa-nome" value={dados.nome_completo}
               onChange={(e) => setDados((d) => ({ ...d, nome_completo: e.target.value }))} />

        <label style={{ display: "flex", gap: 8, alignItems: "center", fontWeight: 400, marginTop: "0.8rem" }}>
          <input type="checkbox" style={{ width: "auto" }} checked={dados.incluir_corvia_mail}
                 onChange={(e) => setDados((d) => ({ ...d, incluir_corvia_mail: e.target.checked }))} />
          Incluir acesso ao CorvIA Mail
        </label>

        <label htmlFor="pa-obs" style={{ marginTop: "0.6rem" }}>
          Observação <span className="eyebrow">(opcional, só para você)</span>
        </label>
        <input id="pa-obs" placeholder="Ex.: amigo, vai trabalhar com a Corvia" value={dados.observacao}
               onChange={(e) => setDados((d) => ({ ...d, observacao: e.target.value }))} />

        <button className="botao" style={{ marginTop: "0.8rem" }} onClick={cadastrar} disabled={!podeCadastrar}>
          {enviando ? "Cadastrando…" : "Cadastrar pré-autorização"}
        </button>
        {erro && <p style={{ color: "var(--alerta)", fontSize: "0.82rem", marginTop: 6 }}>{erro}</p>}
      </div>

      {lista === null ? (
        <Carregando />
      ) : lista.length === 0 ? (
        <p style={{ color: "var(--texto-secundario)", marginTop: "0.8rem" }}>Nenhuma pré-autorização cadastrada ainda.</p>
      ) : (
        <div className="grade" style={{ marginTop: "0.8rem" }}>
          {pendentes.map((l) => (
            <div className="cartao cartao--clinico" key={l.id}>
              <strong>{l.nome_completo || l.email}</strong>
              {l.nome_completo && l.email && (
                <div style={{ fontSize: "0.82rem", color: "var(--texto-secundario)" }}>{l.email}</div>
              )}
              <div style={{ fontSize: "0.82rem", marginTop: 4 }}>
                {l.incluir_corvia_mail ? "Com CorvIA Mail" : "Sem CorvIA Mail"}
              </div>
              {l.observacao && <p style={{ fontSize: "0.82rem", marginTop: 4 }}>{l.observacao}</p>}
              <button className="botao botao--secundario" style={{ marginTop: 8 }} onClick={() => revogar(l.id)}>
                Revogar
              </button>
            </div>
          ))}
          {usadas.map((l) => (
            <div className="cartao cartao--clinico" key={l.id} style={{ opacity: 0.6 }}>
              <strong>{l.nome_completo || l.email}</strong>
              <span className="selo selo--revisado" style={{ marginLeft: 6 }}>já cadastrado</span>
              <div style={{ fontSize: "0.82rem", color: "var(--texto-secundario)", marginTop: 4 }}>
                usado em {new Date(l.usado_em as string).toLocaleString("pt-BR")}
              </div>
            </div>
          ))}
        </div>
      )}
    </>
  );
}

export default function Admin() {
  const [lista, setLista] = useState<Usuario[] | null>(null);
  const [erro, setErro] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [novo, setNovo] = useState({
    email: "", full_name: "", crm: "", profession: "", council_name: "CRM",
    council_number: "", council_state: "", specialty: "", professional_title: "",
    workplace_name: "", workplace_department: "", workplace_role: "", workplace_notes: "",
    include_workplace_on_documents: false, profile_completion_required: false,
    role: "medico", password: "",
    // Normal mantém cobrança/KYC. Convidado mantém cortesia operacional com
    // KYC completo automático. Investidor é DEMO observacional: sem KYC,
    // sem conclusão de perfil, senha fixa CorVIAOS e tour direto.
    tipo_acesso: "normal" as "normal" | "convidado" | "investidor",
  });

  const [waiversNovo, setWaiversNovo] = useState<KycWaiverConfig>({ ...KYC_WAIVERS_VAZIAS });
  const [pedidosGoogle, setPedidosGoogle] = useState<PedidoTesteGoogle[] | null>(null);

  const recarregar = () =>
    api.get<Usuario[]>("/admin/users").then(setLista).catch((e) => setErro(e.message));

  const recarregarPedidosGoogle = () =>
    api.get<PedidoTesteGoogle[]>("/admin/google-teste?status=pendente").then(setPedidosGoogle).catch(() => setPedidosGoogle([]));

  useEffect(() => { recarregar(); recarregarPedidosGoogle(); }, []);

  async function criar() {
    setErro("");
    setEnviando(true);
    const investidor = novo.tipo_acesso === "investidor";
    try {
      await api.post("/admin/users", {
        email: novo.email.trim(),
        full_name: novo.full_name.trim(),
        crm: investidor ? null : (novo.crm.trim() || null),
        profession: investidor ? null : (novo.profession.trim() || null),
        council_name: investidor ? null : (novo.council_name || null),
        council_number: investidor ? null : (novo.council_number.trim() || null),
        council_state: investidor ? null : (novo.council_state || null),
        specialty: investidor ? null : (novo.specialty.trim() || null),
        professional_title: investidor ? null : (novo.professional_title || null),
        workplace_name: investidor ? null : (novo.workplace_name.trim() || null),
        workplace_department: investidor ? null : (novo.workplace_department.trim() || null),
        workplace_role: investidor ? null : (novo.workplace_role.trim() || null),
        workplace_notes: investidor ? null : (novo.workplace_notes.trim() || null),
        include_workplace_on_documents: investidor ? false : novo.include_workplace_on_documents,
        profile_completion_required: investidor ? false : novo.profile_completion_required,
        role: investidor ? "leitor" : novo.role,
        password: investidor ? "CorVIAOS" : novo.password,
        tipo_acesso: novo.tipo_acesso,
        kyc_waivers: novo.tipo_acesso === "convidado" ? waiversNovo : null,
      });
      setNovo({ email: "", full_name: "", crm: "", profession: "", council_name: "CRM",
        council_number: "", council_state: "", specialty: "", professional_title: "",
        workplace_name: "", workplace_department: "", workplace_role: "", workplace_notes: "",
        include_workplace_on_documents: false, profile_completion_required: false,
        role: "medico", password: "", tipo_acesso: "normal" });
      setWaiversNovo({ ...KYC_WAIVERS_VAZIAS });
      recarregar();
    } catch (e) {
      setErro(e instanceof Error ? e.message : "Não foi possível criar o usuário.");
    } finally {
      setEnviando(false);
    }
  }

  async function alternar(u: Usuario) {
    try {
      await api.patch(`/admin/users/${u.id}/ativo?ativo=${!u.is_active}`, {});
      recarregar();
    } catch (e) {
      setErro(e instanceof Error ? e.message : "Não foi possível alterar o usuário.");
    }
  }

  async function alternarConvidado(u: Usuario) {
    try {
      await api.patch(`/admin/users/${u.id}/convidado?convidado=${!u.convidado}`, {});
      recarregar();
    } catch (e) {
      setErro(e instanceof Error ? e.message : "Não foi possível alterar o status de convidado.");
    }
  }

  async function alternarInvestidor(u: Usuario) {
    try {
      await api.patch(`/admin/users/${u.id}/investidor?investidor=${!u.investidor}`, {});
      recarregar();
    } catch (e) {
      setErro(e instanceof Error ? e.message : "Não foi possível alterar o status de investidor.");
    }
  }

  const investidorNovo = novo.tipo_acesso === "investidor";
  const senhaFraca = !investidorNovo && novo.password.length > 0 && novo.password.length < 8;
  const podeCriar = Boolean(
    novo.email.trim() && novo.full_name.trim() &&
    (investidorNovo || novo.password.length >= 8) && !enviando
  );

  const pendentes = lista?.filter((u) => u.status === "pendente") ?? [];
  const decididos = lista?.filter((u) => u.status !== "pendente") ?? [];

  return (
    <>
      <p className="eyebrow">Administração</p>
      <h1>Usuários</h1>

      <Link to="/admin/usuarios" className="cartao cartao--clinico" style={{ display: "block", marginTop: "0.8rem", maxWidth: 560, textDecoration: "none" }}>
        <strong>Ficha completa de assinantes →</strong>
        <p style={{ margin: "0.3rem 0 0", color: "var(--texto-secundario)", fontSize: "0.86rem" }}>
          Busca e filtro por status, KYC e assinatura, com a ficha administrativa completa
          de cada cadastro (dados pessoais/profissionais, documentos de verificação e
          histórico de decisões).
        </p>
      </Link>

      {erro && <div style={{ marginTop: "0.8rem", maxWidth: 560 }}><Erro mensagem={erro} /></div>}

      {lista === null ? (
        <Carregando />
      ) : (
        <>
          {pendentes.length > 0 && (
            <>
              <h2 style={{ marginTop: "1.2rem" }}>
                Solicitações de acesso <span className="selo selo--pendente">{pendentes.length}</span>
              </h2>
              <p style={{ color: "var(--texto-secundario)", maxWidth: "60ch" }}>
                Confira o registro no conselho de classe antes de aprovar — a Corvia não
                valida isso automaticamente.
              </p>
              <div className="grade" style={{ marginTop: "0.6rem" }}>
                {pendentes.map((u) => (
                  <SolicitacaoCard key={u.id} u={u} aoDecidir={recarregar} />
                ))}
              </div>
            </>
          )}

          {pedidosGoogle !== null && pedidosGoogle.length > 0 && (
            <>
              <h2 style={{ marginTop: "1.6rem" }}>
                Liberação de teste do Google <span className="selo selo--pendente">{pedidosGoogle.length}</span>
              </h2>
              <p style={{ color: "var(--texto-secundario)", maxWidth: "60ch" }}>
                O app OAuth da Corvia está em modo "Testing" no Google Cloud (teto de 100
                contas, sem API para automatizar). Cada assinante abaixo pediu para conectar
                o Google — adicione o e-mail como testador no Console e só então marque
                como liberado aqui.
              </p>
              <div className="grade" style={{ marginTop: "0.6rem" }}>
                {pedidosGoogle.map((p) => (
                  <PedidoTesteGoogleCard key={p.id} p={p} aoLiberar={recarregarPedidosGoogle} />
                ))}
              </div>
            </>
          )}

          <PreAutorizacoesConvidado />

          <h2 style={{ marginTop: "1.6rem" }}>Criar conta diretamente</h2>
          <p style={{ color: "var(--texto-secundario)", maxWidth: "58ch" }}>
            A conta já nasce aprovada. Convidados seguem o onboarding próprio; Investidor
            entra diretamente no tour com a credencial fixa de demonstração.
          </p>

          <div className="cartao cartao--clinico" style={{ marginTop: "0.8rem", maxWidth: 560 }}>
            <p className="eyebrow">Nova conta</p>

            <fieldset style={{ border: "1px solid var(--borda)", borderRadius: 8, padding: "0.7rem 0.9rem", margin: 0 }}>
              <legend style={{ padding: "0 0.3rem", fontWeight: 650 }}>Tipo de acesso</legend>
              <label style={{ display: "flex", gap: 8, alignItems: "flex-start", fontWeight: 400, marginTop: 4 }}>
                <input type="radio" name="tipo-acesso" style={{ width: "auto", marginTop: 3 }}
                       checked={novo.tipo_acesso === "normal"}
                       onChange={() => setNovo({ ...novo, tipo_acesso: "normal" })} />
                <span>
                  <strong>Assinante normal</strong>
                  <br /><small style={{ color: "var(--texto-secundario)" }}>
                    Fluxo normal de cobrança/Stripe, KYC normal, regras normais existentes.
                  </small>
                </span>
              </label>
              <label style={{ display: "flex", gap: 8, alignItems: "flex-start", fontWeight: 400, marginTop: 8 }}>
                <input type="radio" name="tipo-acesso" style={{ width: "auto", marginTop: 3 }}
                       checked={novo.tipo_acesso === "convidado"}
                       onChange={() => setNovo({ ...novo, tipo_acesso: "convidado" })} />
                <span>
                  <strong>Convidado — acesso gratuito</strong>
                  <br /><small style={{ color: "var(--texto-secundario)" }}>
                    Nunca cobra. No primeiro acesso completa perfil pessoal + profissional e envia
                    os requisitos de KYC aplicáveis; a aprovação é automática, sem revisão final do admin.
                  </small>
                </span>
              </label>
              <label style={{ display: "flex", gap: 8, alignItems: "flex-start", fontWeight: 400, marginTop: 8 }}>
                <input type="radio" name="tipo-acesso" style={{ width: "auto", marginTop: 3 }}
                       checked={novo.tipo_acesso === "investidor"}
                       onChange={() => setNovo({
                         ...novo,
                         tipo_acesso: "investidor",
                         role: "leitor",
                         profile_completion_required: false,
                         password: "",
                       })} />
                <span>
                  <strong>Investidor — demonstração somente leitura</strong>
                  <br /><small style={{ color: "var(--texto-secundario)" }}>
                    Nunca cobra. Não completa dados, não envia documento e não faz selfie/KYC.
                    Entra direto no tour e depois pode conhecer toda a plataforma sem gerar, editar,
                    enviar, conectar, sincronizar ou persistir operações reais.
                  </small>
                </span>
              </label>
            </fieldset>

            {novo.tipo_acesso === "convidado" && (
              <fieldset style={{ border: "1px solid var(--borda)", borderRadius: 8, padding: "0.7rem 0.9rem", marginTop: "0.8rem" }}>
                <legend style={{ padding: "0 0.3rem", fontWeight: 650 }}>Dispensas KYC individuais</legend>
                <small style={{ color: "var(--texto-secundario)" }}>
                  Opcional. Requisitos não marcados continuam obrigatórios; quando todos os requisitos remanescentes forem válidos, a aprovação é automática.
                </small>
                {ROTULOS_KYC_WAIVER.map(([campo, rotulo]) => (
                  <label key={campo} style={{ display: "flex", gap: 8, alignItems: "center", fontWeight: 400, marginTop: 7 }}>
                    <input type="checkbox" style={{ width: "auto" }} checked={waiversNovo[campo]}
                           onChange={(e) => setWaiversNovo({ ...waiversNovo, [campo]: e.target.checked })} />
                    <span>Dispensar {rotulo}</span>
                  </label>
                ))}
              </fieldset>
            )}

            <div className="grade grade--2" style={{ marginTop: "0.9rem" }}>
              <div>
                <label htmlFor="nome">Nome da conta</label>
                <input id="nome" value={novo.full_name}
                       onChange={(e) => setNovo({ ...novo, full_name: e.target.value })} />
              </div>
              <div>
                <label htmlFor="email">E-mail</label>
                <input id="email" type="email" value={novo.email}
                       onChange={(e) => setNovo({ ...novo, email: e.target.value })} />
              </div>

              {!investidorNovo && (
                <>
                  <div>
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
                    <select id="perfil" value={novo.role}
                            onChange={(e) => setNovo({ ...novo, role: e.target.value })}>
                      {PERFIS.map((p) => <option key={p.valor} value={p.valor}>{p.rotulo}</option>)}
                    </select>
                  </div>
                </>
              )}
            </div>

            {!investidorNovo && (
              <>
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
                <label style={{ display: "flex", gap: 8, alignItems: "center", fontWeight: 400, marginTop: 8 }}>
                  <input type="checkbox" style={{ width: "auto" }} checked={novo.profile_completion_required}
                         onChange={(e) => setNovo({ ...novo, profile_completion_required: e.target.checked })} />
                  No primeiro acesso, direcionar para completar dados pessoais e profissionais
                </label>
              </>
            )}

            {investidorNovo ? (
              <div className="cartao" style={{ marginTop: "0.9rem", borderColor: "rgba(66,202,216,.28)" }}>
                <p className="eyebrow">Credencial fixa da demonstração</p>
                <strong style={{ fontFamily: "var(--fonte-dados)", fontSize: "1.05rem" }}>CorVIAOS</strong>
                <p style={{ margin: "0.35rem 0 0", color: "var(--texto-secundario)", fontSize: "0.82rem" }}>
                  Não há senha temporária nem troca obrigatória. A conta é protegida pelo modo global
                  somente leitura e não deve conter dados clínicos ou operacionais reais.
                </p>
              </div>
            ) : (
              <div style={{ marginTop: "0.9rem" }}>
                <label htmlFor="senha">Senha temporária</label>
                <input id="senha" type="text" value={novo.password}
                       onChange={(e) => setNovo({ ...novo, password: e.target.value })}
                       aria-describedby="senha-ajuda" />
                <span id="senha-ajuda" style={{ fontSize: "0.8rem", color: "var(--texto-secundario)" }}>
                  Mínimo 8 caracteres. Fica visível aqui de propósito, para você copiar e repassar.
                </span>
                {senhaFraca && (
                  <p style={{ color: "var(--alerta)", fontSize: "0.82rem", margin: "0.3rem 0 0" }}>
                    Muito curta.
                  </p>
                )}
              </div>
            )}

            <button className="botao" style={{ marginTop: "1rem" }} onClick={criar} disabled={!podeCriar}>
              {enviando ? "Criando…" : investidorNovo ? "Criar conta Investidor" : "Criar conta"}
            </button>
          </div>

          <h2 style={{ marginTop: "1.6rem" }}>Contas decididas</h2>
          <div className="grade">
            {decididos.map((u) => (
              <div key={u.id} className="cartao" style={{ display: "flex", alignItems: "center", gap: 12 }}>
                <div style={{ flex: 1 }}>
                  <strong>{u.full_name}</strong>{" "}
                  <span className="eyebrow">{PERFIS.find((p) => p.valor === u.role)?.rotulo}</span>
                  {u.convidado && (
                    <span className="selo selo--revisado" style={{ marginLeft: 6 }} title="Acesso completo gratuito, inclusive CorvIA Mail real">
                      convidado — acesso completo gratuito
                    </span>
                  )}
                  {u.investidor && (
                    <span className="selo selo--pendente" style={{ marginLeft: 6 }} title="Demonstração global — somente visualização, sem operações reais">
                      investidor — somente visualização
                    </span>
                  )}
                  <div style={{ fontSize: "0.86rem", color: "var(--texto-secundario)" }}>
                    {u.email}
                    {u.council_name && ` · ${u.council_name} ${u.council_number}/${u.council_state}`}
                    {u.crm && !u.council_name && ` · CRM ${u.crm}`}
                  </div>
                  <KycWaiversEditor u={u} />
                  {u.status === "rejeitado" && u.rejection_note && (
                    <div style={{ fontSize: "0.8rem", color: "var(--alerta)" }}>
                      Rejeitado: {u.rejection_note}
                    </div>
                  )}
                </div>
                <span className={`selo ${u.is_active ? "selo--revisado" : "selo--pendente"}`}>
                  {u.status === "rejeitado" ? "rejeitado" : u.is_active ? "ativo" : "desativado"}
                </span>
                {u.status !== "rejeitado" && (
                  <>
                    <button className="botao botao--secundario" style={{ padding: "0.35rem 0.75rem" }}
                            onClick={() => alternarConvidado(u)}
                            title="Acesso completo e gratuito — inclusive CorvIA Mail real (enviar, receber, provisionar caixa).">
                      {u.convidado ? "Remover convidado" : "Marcar convidado"}
                    </button>
                    <button className="botao botao--secundario" style={{ padding: "0.35rem 0.75rem" }}
                            onClick={() => alternarInvestidor(u)}
                            title="Demonstração somente leitura — sem KYC, sem cobrança e sem operações reais.">
                      {u.investidor ? "Remover investidor" : "Marcar investidor"}
                    </button>
                    <button className="botao botao--secundario" style={{ padding: "0.35rem 0.75rem" }}
                            onClick={() => alternar(u)}>
                      {u.is_active ? "Desativar" : "Reativar"}
                    </button>
                  </>
                )}
              </div>
            ))}
          </div>
        </>
      )}
    </>
  );
}
