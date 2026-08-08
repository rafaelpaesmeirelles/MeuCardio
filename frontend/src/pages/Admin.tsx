import { useEffect, useState } from "react";
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
};

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
  });

  const [pedidosGoogle, setPedidosGoogle] = useState<PedidoTesteGoogle[] | null>(null);

  const recarregar = () =>
    api.get<Usuario[]>("/admin/users").then(setLista).catch((e) => setErro(e.message));

  const recarregarPedidosGoogle = () =>
    api.get<PedidoTesteGoogle[]>("/admin/google-teste?status=pendente").then(setPedidosGoogle).catch(() => setPedidosGoogle([]));

  useEffect(() => { recarregar(); recarregarPedidosGoogle(); }, []);

  async function criar() {
    setErro("");
    setEnviando(true);
    try {
      await api.post("/admin/users", {
        email: novo.email.trim(),
        full_name: novo.full_name.trim(),
        crm: novo.crm.trim() || null,
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
      });
      setNovo({ email: "", full_name: "", crm: "", profession: "", council_name: "CRM",
        council_number: "", council_state: "", specialty: "", professional_title: "",
        workplace_name: "", workplace_department: "", workplace_role: "", workplace_notes: "",
        include_workplace_on_documents: false, profile_completion_required: false,
        role: "medico", password: "" });
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

  const senhaFraca = novo.password.length > 0 && novo.password.length < 8;
  const podeCriar = novo.email && novo.full_name && novo.password.length >= 8 && !enviando;

  const pendentes = lista?.filter((u) => u.status === "pendente") ?? [];
  const decididos = lista?.filter((u) => u.status !== "pendente") ?? [];

  return (
    <>
      <p className="eyebrow">Administração</p>
      <h1>Usuários</h1>

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
            Pula a fila de solicitação — a conta já nasce aprovada. Repasse a senha
            temporária por um canal seguro.
          </p>

          <div className="cartao cartao--clinico" style={{ marginTop: "0.8rem", maxWidth: 560 }}>
            <p className="eyebrow">Nova conta</p>
            <div className="grade grade--2" style={{ marginTop: "0.6rem" }}>
              <div>
                <label htmlFor="nome">Nome completo</label>
                <input id="nome" value={novo.full_name}
                       onChange={(e) => setNovo({ ...novo, full_name: e.target.value })} />
              </div>
              <div>
                <label htmlFor="email">E-mail</label>
                <input id="email" type="email" value={novo.email}
                       onChange={(e) => setNovo({ ...novo, email: e.target.value })} />
              </div>
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
            </div>
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
            <button className="botao" style={{ marginTop: "1rem" }} onClick={criar} disabled={!podeCriar}>
              {enviando ? "Criando…" : "Criar conta"}
            </button>
          </div>

          <h2 style={{ marginTop: "1.6rem" }}>Contas decididas</h2>
          <div className="grade">
            {decididos.map((u) => (
              <div key={u.id} className="cartao" style={{ display: "flex", alignItems: "center", gap: 12 }}>
                <div style={{ flex: 1 }}>
                  <strong>{u.full_name}</strong>{" "}
                  <span className="eyebrow">{PERFIS.find((p) => p.valor === u.role)?.rotulo}</span>
                  {u.convidado && <span className="selo selo--revisado" style={{ marginLeft: 6 }}>convidado</span>}
                  <div style={{ fontSize: "0.86rem", color: "var(--texto-secundario)" }}>
                    {u.email}
                    {u.council_name && ` · ${u.council_name} ${u.council_number}/${u.council_state}`}
                    {u.crm && !u.council_name && ` · CRM ${u.crm}`}
                  </div>
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
                            title="Acesso cortesia completo: assinatura liberada sem cobrança e KYC aprovado automaticamente.">
                      {u.convidado ? "Remover convidado" : "Marcar convidado"}
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
