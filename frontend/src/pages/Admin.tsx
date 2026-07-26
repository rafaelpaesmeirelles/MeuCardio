import { useEffect, useState } from "react";
import { api } from "../lib/api";
import { Carregando, Erro } from "../components/Estado";

type Usuario = {
  id: number; email: string; full_name: string; crm: string | null;
  birth_date: string | null; cpf: string | null; profession: string | null;
  council_name: string | null; council_number: string | null; council_state: string | null;
  specialty: string | null; role: string; status: string; is_active: boolean;
  rejection_note: string | null; created_at: string;
};

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
      <div style={{ fontSize: "0.82rem", color: "var(--cinza-texto)", marginTop: 2 }}>
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

export default function Admin() {
  const [lista, setLista] = useState<Usuario[] | null>(null);
  const [erro, setErro] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [novo, setNovo] = useState({
    email: "", full_name: "", crm: "", role: "medico", password: "",
  });

  const recarregar = () =>
    api.get<Usuario[]>("/admin/users").then(setLista).catch((e) => setErro(e.message));

  useEffect(() => { recarregar(); }, []);

  async function criar() {
    setErro("");
    setEnviando(true);
    try {
      await api.post("/admin/users", {
        email: novo.email.trim(),
        full_name: novo.full_name.trim(),
        crm: novo.crm.trim() || null,
        role: novo.role,
        password: novo.password,
      });
      setNovo({ email: "", full_name: "", crm: "", role: "medico", password: "" });
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
              <p style={{ color: "var(--cinza-texto)", maxWidth: "60ch" }}>
                Confira o registro no conselho de classe antes de aprovar — o MeuCardio não
                valida isso automaticamente.
              </p>
              <div className="grade" style={{ marginTop: "0.6rem" }}>
                {pendentes.map((u) => (
                  <SolicitacaoCard key={u.id} u={u} aoDecidir={recarregar} />
                ))}
              </div>
            </>
          )}

          <h2 style={{ marginTop: "1.6rem" }}>Criar conta diretamente</h2>
          <p style={{ color: "var(--cinza-texto)", maxWidth: "58ch" }}>
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
                <label htmlFor="crm">CRM (opcional)</label>
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
            <div style={{ marginTop: "0.9rem" }}>
              <label htmlFor="senha">Senha temporária</label>
              <input id="senha" type="text" value={novo.password}
                     onChange={(e) => setNovo({ ...novo, password: e.target.value })}
                     aria-describedby="senha-ajuda" />
              <span id="senha-ajuda" style={{ fontSize: "0.8rem", color: "var(--cinza-texto)" }}>
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
                  <div style={{ fontSize: "0.86rem", color: "var(--cinza-texto)" }}>
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
                  <button className="botao botao--secundario" style={{ padding: "0.35rem 0.75rem" }}
                          onClick={() => alternar(u)}>
                    {u.is_active ? "Desativar" : "Reativar"}
                  </button>
                )}
              </div>
            ))}
          </div>
        </>
      )}
    </>
  );
}
