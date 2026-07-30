import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../lib/auth";
import { api, ApiError } from "../lib/api";
import { apiEmail, ApiEmailError } from "../lib/apiEmail";
import Credito from "../components/Credito";

type StatusEmail = { status: string; current_period_end: string | null; preco_definido: boolean };
type ContaEmail = { ativa: boolean; email_address?: string };

const ROTULOS: Record<string, string> = {
  ativo: "Ativa", teste: "Período de teste", inativo: "Inativa", pendente: "Pendente",
  inadimplente: "Pagamento pendente", suspenso: "Suspensa por falta de pagamento",
  cancelado: "Cancelada", pausado: "Pausada",
};
const STATUS_COM_ACESSO = ["ativo", "teste", "inadimplente"];

function reais(centavos: number) {
  return (centavos / 100).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

/** Aba de assinatura — só faz sentido pra quem já está logado na conta
 * Corvia (decisão do Rafael: CorvIA Mail exige conta Corvia aprovada). */
function AbaAssinar() {
  const [status, setStatus] = useState<StatusEmail | null>(null);
  const [contaEmail, setContaEmail] = useState<ContaEmail | null>(null);
  const [carregando, setCarregando] = useState(true);
  const [processando, setProcessando] = useState(false);
  const [senhaInicial, setSenhaInicial] = useState("");
  const [ativando, setAtivando] = useState(false);
  const [erro, setErro] = useState("");

  useEffect(() => {
    Promise.all([
      api.get<StatusEmail>("/billing/status-email"),
      api.get<ContaEmail>("/email/conta"),
    ])
      .then(([s, c]) => { setStatus(s); setContaEmail(c); })
      .catch((e) => setErro(e instanceof ApiError ? e.message : "Não foi possível carregar seu CorvIA Mail."))
      .finally(() => setCarregando(false));
  }, []);

  async function assinar() {
    setProcessando(true);
    setErro("");
    try {
      const { checkout_url } = await api.post<{ checkout_url: string }>("/billing/checkout-email");
      window.location.assign(checkout_url);
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível iniciar o pagamento.");
      setProcessando(false);
    }
  }

  async function ativarCaixa() {
    setAtivando(true);
    setErro("");
    try {
      const resultado = await api.post<ContaEmail>("/email/conta", { senha: senhaInicial });
      setContaEmail(resultado);
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível ativar sua caixa.");
    } finally {
      setAtivando(false);
    }
  }

  if (carregando) return <p className="eyebrow">Carregando…</p>;

  const ativa = status ? STATUS_COM_ACESSO.includes(status.status) : false;

  return (
    <div className="cartao" style={{ marginTop: "1rem" }}>
      <p>
        Um endereço de e-mail próprio no domínio <strong>@corvia.med.br</strong>, com
        webmail integrado — add-on separado da assinatura principal da Corvia, cobrado à parte.
      </p>

      <p>
        <strong>{status?.preco_definido ? "valor sob consulta" : "Em breve"}</strong>
        {!status?.preco_definido && " — o valor ainda está sendo definido."}
      </p>

      {erro && <p role="alert" style={{ color: "var(--alerta)", fontSize: "0.86rem" }}>{erro}</p>}

      {!ativa && (
        <button className="botao" style={{ width: "100%", marginTop: "1rem" }}
                onClick={assinar} disabled={processando || !status?.preco_definido}>
          {processando ? "Redirecionando…" : status?.preco_definido ? "Assinar o CorvIA Mail" : "Em breve"}
        </button>
      )}

      {ativa && !contaEmail?.ativa && (
        <div style={{ marginTop: "1rem" }}>
          <p style={{ color: "var(--sucesso)" }}>Assinatura ativa — falta só criar sua caixa.</p>
          <label htmlFor="senha-inicial">Crie uma senha para sua caixa de e-mail</label>
          <input id="senha-inicial" type="password" value={senhaInicial}
                 onChange={(e) => setSenhaInicial(e.target.value)} />
          <p className="eyebrow" style={{ margin: "0.3rem 0 0" }}>
            Senha própria, diferente da senha da sua conta Corvia.
          </p>
          <button className="botao" style={{ width: "100%", marginTop: "0.8rem" }}
                  onClick={ativarCaixa} disabled={ativando || senhaInicial.length < 8}>
            {ativando ? "Ativando…" : "Ativar minha caixa de e-mail"}
          </button>
        </div>
      )}

      {ativa && contaEmail?.ativa && (
        <p style={{ color: "var(--sucesso)", marginTop: "1rem" }}>
          Sua caixa <strong>{contaEmail.email_address}</strong> está pronta — entre na aba "Entrar" ao lado.
        </p>
      )}
    </div>
  );
}

function AbaEntrar() {
  const navigate = useNavigate();
  const [endereco, setEndereco] = useState("");
  const [senha, setSenha] = useState("");
  const [erro, setErro] = useState("");
  const [enviando, setEnviando] = useState(false);

  async function enviar() {
    setErro("");
    setEnviando(true);
    try {
      await apiEmail.entrar(endereco.trim().toLowerCase(), senha);
      navigate("/caixa-de-email");
    } catch (e) {
      setErro(e instanceof ApiEmailError ? e.message : "Não foi possível entrar.");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="cartao" style={{ marginTop: "1rem" }}>
      <label htmlFor="endereco-email">Endereço @corvia.med.br</label>
      <input id="endereco-email" value={endereco} onChange={(e) => setEndereco(e.target.value)}
             onKeyDown={(e) => e.key === "Enter" && enviar()} />
      <label htmlFor="senha-email" style={{ marginTop: "0.8rem" }}>Senha da caixa de e-mail</label>
      <input id="senha-email" type="password" value={senha} onChange={(e) => setSenha(e.target.value)}
             onKeyDown={(e) => e.key === "Enter" && enviar()} />
      {erro && <p role="alert" style={{ color: "var(--alerta)", fontSize: "0.86rem" }}>{erro}</p>}
      <button className="botao" style={{ width: "100%", marginTop: "1rem" }}
              onClick={enviar} disabled={enviando || !endereco || !senha}>
        {enviando ? "Entrando…" : "Entrar na caixa de e-mail"}
      </button>
    </div>
  );
}

function AbaEsqueciSenha() {
  const [endereco, setEndereco] = useState("");
  const [enviado, setEnviado] = useState(false);
  const [enviando, setEnviando] = useState(false);

  async function enviar() {
    setEnviando(true);
    try {
      await apiEmail.post("/email/esqueci-senha", { endereco: endereco.trim().toLowerCase() });
    } finally {
      setEnviando(false);
      setEnviado(true);
    }
  }

  return (
    <div className="cartao" style={{ marginTop: "1rem" }}>
      {enviado ? (
        <p>
          Se o endereço existir e estiver ativo, um link de redefinição foi enviado para o
          e-mail principal da sua conta Corvia — não para a própria caixa @corvia.med.br.
        </p>
      ) : (
        <>
          <label htmlFor="endereco-recuperar">Endereço @corvia.med.br</label>
          <input id="endereco-recuperar" value={endereco} onChange={(e) => setEndereco(e.target.value)} />
          <button className="botao" style={{ width: "100%", marginTop: "1rem" }}
                  onClick={enviar} disabled={!endereco.includes("@") || enviando}>
            {enviando ? "Enviando…" : "Solicitar redefinição"}
          </button>
        </>
      )}
    </div>
  );
}

export default function CorviaMail() {
  const { usuario, carregando } = useAuth();
  const [aba, setAba] = useState<"entrar" | "esqueci" | "assinar">("entrar");

  if (carregando) return <p className="eyebrow">Carregando…</p>;

  if (!usuario) {
    return (
      <div className="login">
        <div className="login__cartao">
          <div className="login__brasao">
            <h1 style={{ fontSize: "1.4rem", marginTop: 14 }}>CorvIA Mail</h1>
          </div>
          <p className="aviso">
            O CorvIA Mail é um add-on da Corvia — é preciso ter conta aprovada na plataforma
            para assinar. Entre na Corvia primeiro.
          </p>
          <Link to="/entrar" className="botao" style={{ display: "block", textAlign: "center", marginTop: "1rem" }}>
            Entrar na Corvia
          </Link>
          <Link to="/solicitar-acesso" style={{ display: "block", textAlign: "center", marginTop: "0.8rem", fontSize: "0.86rem" }}>
            Ainda não tem conta? Solicitar cadastro
          </Link>
          <Credito compacto />
        </div>
      </div>
    );
  }

  return (
    <div className="login">
      <div className="login__cartao">
        <div className="login__brasao">
          <h1 style={{ fontSize: "1.4rem", marginTop: 14 }}>CorvIA Mail</h1>
        </div>

        <div style={{ display: "flex", gap: 6, justifyContent: "center", marginTop: "0.6rem" }}>
          <button className={aba === "entrar" ? "botao" : "botao botao--secundario"}
                  style={{ flex: 1 }} onClick={() => setAba("entrar")}>Entrar</button>
          <button className={aba === "esqueci" ? "botao" : "botao botao--secundario"}
                  style={{ flex: 1 }} onClick={() => setAba("esqueci")}>Esqueci a senha</button>
          <button className={aba === "assinar" ? "botao" : "botao botao--secundario"}
                  style={{ flex: 1 }} onClick={() => setAba("assinar")}>Assine já</button>
        </div>

        {aba === "entrar" && <AbaEntrar />}
        {aba === "esqueci" && <AbaEsqueciSenha />}
        {aba === "assinar" && <AbaAssinar />}

        <Credito compacto />
      </div>
    </div>
  );
}
