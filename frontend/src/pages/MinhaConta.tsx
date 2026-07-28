import { useEffect, useState } from "react";
import { api, ApiError, type Usuario } from "../lib/api";
import { useAuth } from "../lib/auth";

const CONSELHOS = ["CRM", "COREN", "CRF", "CREFITO", "CRN", "CRP", "CRO", "Outro"];
const UFS = [
  "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG",
  "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO",
];

type StatusAssinatura = {
  status: string;
  current_period_end: string | null;
};

const ROTULOS: Record<string, string> = {
  ativo: "Ativa",
  teste: "Período de teste",
  inativo: "Inativa",
  pendente: "Pendente",
  inadimplente: "Pagamento pendente",
  suspenso: "Suspensa por falta de pagamento",
  cancelado: "Cancelada",
  pausado: "Pausada",
};

// Mesmo conjunto de ACESSO_LIBERADO em backend/app/core/security.py.
const STATUS_COM_ACESSO = ["ativo", "teste", "inadimplente"];

function DadosPessoais({ perfil, aoSalvar }: { perfil: Usuario; aoSalvar: (u: Usuario) => void }) {
  const [dados, setDados] = useState({
    full_name: perfil.full_name ?? "",
    profession: perfil.profession ?? "",
    council_name: perfil.council_name ?? "CRM",
    council_number: perfil.council_number ?? "",
    council_state: perfil.council_state ?? "",
    specialty: perfil.specialty ?? "",
  });
  const [salvando, setSalvando] = useState(false);
  const [erro, setErro] = useState("");
  const [ok, setOk] = useState(false);

  function set<K extends keyof typeof dados>(campo: K, valor: string) {
    setDados((d) => ({ ...d, [campo]: valor }));
    setOk(false);
  }

  const valido = dados.full_name.trim().split(/\s+/).length >= 2;

  async function salvar() {
    setErro("");
    setSalvando(true);
    try {
      const atualizado = await api.patch<Usuario>("/auth/me", {
        ...dados,
        profession: dados.profession.trim() || null,
        council_number: dados.council_number.trim() || null,
        council_state: dados.council_state || null,
        specialty: dados.specialty.trim() || null,
      });
      aoSalvar(atualizado);
      setOk(true);
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível salvar seus dados.");
    } finally {
      setSalvando(false);
    }
  }

  return (
    <div className="cartao">
      <h2 style={{ marginTop: 0 }}>Dados pessoais</h2>

      <label htmlFor="conta-nome">Nome completo</label>
      <input id="conta-nome" value={dados.full_name} onChange={(e) => set("full_name", e.target.value)} />
      {!valido && (
        // Sem esta mensagem o botão fica desabilitado sem explicação, e quem
        // tem só um nome cadastrado (contas criadas pelo admin, por exemplo)
        // não descobre por que não consegue salvar nada da página.
        <p style={{ color: "var(--alerta)", fontSize: "0.82rem", margin: "0.3rem 0 0" }}>
          Informe nome e sobrenome — é o que o cadastro exige para salvar.
        </p>
      )}

      <label htmlFor="conta-profissao" style={{ marginTop: "0.8rem" }}>Profissão</label>
      <input id="conta-profissao" value={dados.profession} onChange={(e) => set("profession", e.target.value)} />

      <div className="grade grade--3" style={{ marginTop: "0.8rem" }}>
        <div>
          <label htmlFor="conta-conselho">Conselho</label>
          <select id="conta-conselho" value={dados.council_name} onChange={(e) => set("council_name", e.target.value)}>
            {CONSELHOS.map((c) => <option key={c} value={c}>{c}</option>)}
          </select>
        </div>
        <div>
          <label htmlFor="conta-numero">Nº de registro</label>
          <input id="conta-numero" value={dados.council_number} onChange={(e) => set("council_number", e.target.value)} />
        </div>
        <div>
          <label htmlFor="conta-uf">Estado</label>
          <select id="conta-uf" value={dados.council_state} onChange={(e) => set("council_state", e.target.value)}>
            <option value="">—</option>
            {UFS.map((uf) => <option key={uf} value={uf}>{uf}</option>)}
          </select>
        </div>
      </div>

      <label htmlFor="conta-especialidade" style={{ marginTop: "0.8rem" }}>
        Especialidade <span className="eyebrow">(opcional)</span>
      </label>
      <input id="conta-especialidade" value={dados.specialty} onChange={(e) => set("specialty", e.target.value)} />


      <p style={{ fontSize: "0.86rem", opacity: 0.8, margin: 0 }}>
        E-mail de acesso: <strong>{perfil.email}</strong>
        {perfil.cpf_mascarado && <> · CPF: <strong>{perfil.cpf_mascarado}</strong></>}
      </p>
      <p style={{ fontSize: "0.82rem", opacity: 0.7, marginTop: "0.3rem" }}>
        E-mail, CPF e data de nascimento são os dados conferidos na aprovação do cadastro —
        para alterá-los, fale com a administração.
      </p>

      {erro && <p role="alert" style={{ color: "var(--alerta)", fontSize: "0.86rem" }}>{erro}</p>}
      {ok && <p style={{ color: "var(--sucesso)", fontSize: "0.86rem" }}>Dados salvos.</p>}

      <button className="botao" style={{ marginTop: "0.8rem" }} onClick={salvar} disabled={!valido || salvando}>
        {salvando ? "Salvando…" : "Salvar dados"}
      </button>
    </div>
  );
}

function TrocarSenha() {
  const [senhaAtual, setSenhaAtual] = useState("");
  const [novaSenha, setNovaSenha] = useState("");
  const [confirmacao, setConfirmacao] = useState("");
  const [mostrar, setMostrar] = useState(false);
  const [salvando, setSalvando] = useState(false);
  const [erro, setErro] = useState("");
  const [ok, setOk] = useState(false);

  const curta = novaSenha.length > 0 && novaSenha.length < 8;
  const divergente = confirmacao.length > 0 && confirmacao !== novaSenha;
  const valido = senhaAtual.length > 0 && novaSenha.length >= 8 && confirmacao === novaSenha;

  async function alterar() {
    setErro("");
    setOk(false);
    setSalvando(true);
    try {
      await api.post("/auth/alterar-senha", { senha_atual: senhaAtual, nova_senha: novaSenha });
      setSenhaAtual("");
      setNovaSenha("");
      setConfirmacao("");
      setOk(true);
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível alterar a senha.");
    } finally {
      setSalvando(false);
    }
  }

  const tipo = mostrar ? "text" : "password";

  return (
    <div className="cartao">
      <h2 style={{ marginTop: 0 }}>Senha</h2>

      <label htmlFor="senha-atual">Senha atual</label>
      <input id="senha-atual" type={tipo} value={senhaAtual} autoComplete="current-password"
             onChange={(e) => setSenhaAtual(e.target.value)} />

      <label htmlFor="senha-nova" style={{ marginTop: "0.8rem" }}>Nova senha</label>
      <input id="senha-nova" type={tipo} value={novaSenha} autoComplete="new-password"
             onChange={(e) => setNovaSenha(e.target.value)} />
      {curta && (
        <p style={{ color: "var(--alerta)", fontSize: "0.82rem", margin: "0.3rem 0 0" }}>
          Mínimo 8 caracteres.
        </p>
      )}

      <label htmlFor="senha-confirma" style={{ marginTop: "0.8rem" }}>Repita a nova senha</label>
      <input id="senha-confirma" type={tipo} value={confirmacao} autoComplete="new-password"
             onChange={(e) => setConfirmacao(e.target.value)} />
      {divergente && (
        <p style={{ color: "var(--alerta)", fontSize: "0.82rem", margin: "0.3rem 0 0" }}>
          As senhas não coincidem.
        </p>
      )}

      <label style={{ display: "flex", alignItems: "center", gap: "0.4rem", marginTop: "0.6rem", fontWeight: 400 }}>
        <input type="checkbox" checked={mostrar} onChange={(e) => setMostrar(e.target.checked)}
               style={{ width: "auto", margin: 0 }} />
        Mostrar senhas
      </label>

      {erro && <p role="alert" style={{ color: "var(--alerta)", fontSize: "0.86rem" }}>{erro}</p>}
      {ok && <p style={{ color: "var(--sucesso)", fontSize: "0.86rem" }}>Senha alterada.</p>}

      <button className="botao" style={{ marginTop: "0.8rem" }} onClick={alterar} disabled={!valido || salvando}>
        {salvando ? "Alterando…" : "Alterar senha"}
      </button>
    </div>
  );
}

function Assinatura() {
  const [carregando, setCarregando] = useState(true);
  const [status, setStatus] = useState<StatusAssinatura | null>(null);
  const [processando, setProcessando] = useState(false);
  const [erro, setErro] = useState("");

  useEffect(() => {
    api
      .get<StatusAssinatura>("/billing/status")
      .then(setStatus)
      .catch((e) => setErro(e instanceof ApiError ? e.message : "Não foi possível carregar sua assinatura."))
      .finally(() => setCarregando(false));
  }, []);

  async function ir(rota: "/billing/portal" | "/billing/checkout", campo: "portal_url" | "checkout_url") {
    setErro("");
    setProcessando(true);
    try {
      const resposta = await api.post<Record<string, string>>(rota);
      window.location.assign(resposta[campo]);
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível abrir a página de pagamento.");
      setProcessando(false);
    }
  }

  const ativa = status ? STATUS_COM_ACESSO.includes(status.status) : false;
  // Sem passagem pelo Stripe ainda não existe cliente, e o portal não tem o que abrir.
  const temCliente = status ? status.status !== "inativo" : false;

  return (
    <div className="cartao">
      <h2 style={{ marginTop: 0 }}>Assinatura</h2>

      {carregando ? (
        <p>Carregando…</p>
      ) : (
        <>
          <p>
            Status atual: <strong>{status ? ROTULOS[status.status] ?? status.status : "—"}</strong>
          </p>
          {status?.current_period_end && (
            <p style={{ fontSize: "0.86rem", opacity: 0.8 }}>
              {ativa ? "Renovação em: " : "Válida até: "}
              {new Date(status.current_period_end).toLocaleDateString("pt-BR")}
            </p>
          )}


          <p><strong>R$ 20,00/mês</strong> — acesso completo à plataforma.</p>

          {erro && <p role="alert" style={{ color: "var(--alerta)", fontSize: "0.86rem" }}>{erro}</p>}

          {!ativa && (
            <button className="botao" style={{ marginTop: "0.8rem" }}
                    onClick={() => ir("/billing/checkout", "checkout_url")} disabled={processando}>
              {processando ? "Redirecionando…" : "Assinar agora"}
            </button>
          )}

          {temCliente && (
            <>
              <button className="botao botao--secundario" style={{ marginTop: "0.8rem", marginLeft: ativa ? 0 : "0.5rem" }}
                      onClick={() => ir("/billing/portal", "portal_url")} disabled={processando}>
                {processando ? "Abrindo…" : "Gerenciar assinatura"}
              </button>
              <p style={{ fontSize: "0.82rem", opacity: 0.7, marginTop: "0.5rem" }}>
                No portal você troca a forma de pagamento, baixa os recibos e cancela a assinatura.
              </p>
            </>
          )}
        </>
      )}
    </div>
  );
}

export default function MinhaConta() {
  const { usuario, recarregar } = useAuth();
  const [perfil, setPerfil] = useState<Usuario | null>(usuario);

  useEffect(() => {
    api.get<Usuario>("/auth/me").then(setPerfil).catch(() => {});
  }, []);

  if (!perfil) return <div className="pagina"><h1>Minha conta</h1><p>Carregando…</p></div>;

  return (
    <div className="pagina">
      <h1>Minha conta</h1>

      <div style={{ display: "grid", gap: "1rem", maxWidth: 560 }}>
        <DadosPessoais
          perfil={perfil}
          aoSalvar={(u) => {
            setPerfil(u);
            recarregar();
          }}
        />
        <TrocarSenha />
        <Assinatura />
      </div>
    </div>
  );
}
