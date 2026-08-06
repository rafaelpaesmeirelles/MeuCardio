import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../lib/auth";
import { api, ApiError } from "../lib/api";
import { apiEmail, ApiEmailError, tokenEmail } from "../lib/apiEmail";
import Credito from "../components/Credito";
import LogoCorviaMail from "../components/LogoCorviaMail";

type StatusEmail = {
  status: string; current_period_end: string | null;
  preco_definido: boolean; preco_centavos: number; incluido_no_plano: boolean;
};
type ContaEmail = {
  ativa: boolean; email_address?: string;
  lgpd_aceite_versao?: string | null; lgpd_versao_atual?: string;
};
type TermoLgpd = { versao: string; texto: string };
type SugestaoEndereco = { local_part: string; dominio: string; editavel: boolean };
type VerificacaoEndereco = { disponivel: boolean; motivo: string | null; endereco: string };

const ROTULOS: Record<string, string> = {
  ativo: "Ativa", teste: "Período de teste", inativo: "Inativa", pendente: "Pendente",
  inadimplente: "Pagamento pendente", suspenso: "Suspensa por falta de pagamento",
  cancelado: "Cancelada", pausado: "Pausada",
};
const STATUS_COM_ACESSO = ["ativo", "teste", "inadimplente"];

function reais(centavos: number) {
  return (centavos / 100).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

/** Campo de escolha do endereço — tela de cadastro do novo e-mail pedida
 * pelo Rafael em 30/07/2026: antes disso o endereço era gerado sozinho
 * (nome.sobrenome@corvia.med.br) sem o médico ver ou poder trocar antes de
 * confirmar. Sugestão pré-preenchida vem de `GET /email/sugestao-endereco`;
 * cada edição dispara `GET /email/verificar-endereco` com debounce — mesmas
 * regras de formato que `POST /email/conta` vai validar de novo no
 * servidor (nunca confiar só na checagem do cliente). */
function EscolhaDeEndereco({ valor, onChange, onValidadeMudou }: {
  valor: string; onChange: (v: string) => void; onValidadeMudou: (valido: boolean) => void;
}) {
  const [verificacao, setVerificacao] = useState<VerificacaoEndereco | null>(null);
  const [verificando, setVerificando] = useState(false);

  useEffect(() => {
    if (!valor) { setVerificacao(null); onValidadeMudou(false); return; }
    setVerificando(true);
    const timer = setTimeout(() => {
      api.get<VerificacaoEndereco>(`/email/verificar-endereco?local=${encodeURIComponent(valor)}`)
        .then((r) => { setVerificacao(r); onValidadeMudou(r.disponivel); })
        .catch(() => { setVerificacao(null); onValidadeMudou(false); })
        .finally(() => setVerificando(false));
    }, 500);
    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [valor]);

  return (
    <div style={{ marginTop: "0.8rem" }}>
      <label htmlFor="local-part">Escolha o endereço da sua caixa</label>
      <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
        <input id="local-part" value={valor} style={{ flex: 1 }}
               onChange={(e) => onChange(e.target.value.toLowerCase())} />
        <span className="eyebrow" style={{ margin: 0, whiteSpace: "nowrap" }}>@corvia.med.br</span>
      </div>
      <p className="eyebrow" style={{ margin: "0.3rem 0 0", minHeight: "1.1em" }}>
        {verificando && "verificando…"}
        {!verificando && verificacao?.disponivel && (
          <span style={{ color: "var(--sucesso)" }}>✓ {verificacao.endereco} está disponível</span>
        )}
        {!verificando && verificacao && !verificacao.disponivel && (
          <span style={{ color: "var(--alerta)" }}>{verificacao.motivo}</span>
        )}
        {!verificando && !verificacao && "letras minúsculas, números, ponto, hífen ou underscore — 3 a 30 caracteres"}
      </p>
    </div>
  );
}

/** Aba de assinatura — só faz sentido pra quem já está logado na conta
 * Corvia (decisão do Rafael: CorvIA Mail exige conta Corvia aprovada). */
function AbaAssinar() {
  const [status, setStatus] = useState<StatusEmail | null>(null);
  const [contaEmail, setContaEmail] = useState<ContaEmail | null>(null);
  const [termo, setTermo] = useState<TermoLgpd | null>(null);
  const [carregando, setCarregando] = useState(true);
  const [processando, setProcessando] = useState(false);
  const [localPart, setLocalPart] = useState("");
  const [enderecoValido, setEnderecoValido] = useState(false);
  const [senhaInicial, setSenhaInicial] = useState("");
  const [aceiteLgpd, setAceiteLgpd] = useState(false);
  const [ativando, setAtivando] = useState(false);
  const [erro, setErro] = useState("");

  useEffect(() => {
    Promise.all([
      api.get<StatusEmail>("/billing/status-email"),
      api.get<ContaEmail>("/email/conta"),
      api.get<TermoLgpd>("/email/termo-lgpd"),
    ])
      .then(([s, c, t]) => {
        setStatus(s); setContaEmail(c); setTermo(t);
        // Só busca sugestão pra quem ainda não tem caixa — quem já tem, o
        // endereço já está fixado no Mail360 e não dá pra reescolher aqui.
        if (!c.ativa) {
          api.get<SugestaoEndereco>("/email/sugestao-endereco")
            .then((sug) => setLocalPart(sug.local_part))
            .catch(() => { /* sugestão é conveniência, não bloqueia o formulário */ });
        }
      })
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

  async function abrirPortal() {
    setProcessando(true);
    setErro("");
    try {
      // Mesma rota que a Minha Conta usa para a assinatura principal — o
      // portal do Stripe lista todas as assinaturas ativas de um cliente
      // (plataforma, CorvIA Mail, curso) na mesma tela, então um médico que
      // assina só o e-mail cai direto na assinatura certa. Backend resolve
      // o `customer_id` mesmo sem assinatura principal (ver
      // `_customer_id_do_usuario` em `app/api/billing.py`).
      const { portal_url } = await api.post<{ portal_url: string }>("/billing/portal");
      window.location.assign(portal_url);
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível abrir o portal de assinatura.");
      setProcessando(false);
    }
  }

  async function ativarCaixa() {
    setAtivando(true);
    setErro("");
    try {
      const resultado = await api.post<ContaEmail>("/email/conta", {
        senha: senhaInicial, aceite_lgpd: aceiteLgpd, local_part: localPart,
      });
      setContaEmail(resultado);
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível ativar sua caixa.");
    } finally {
      setAtivando(false);
    }
  }

  if (carregando) return <p className="eyebrow">Carregando…</p>;

  const ativa = status ? STATUS_COM_ACESSO.includes(status.status) : false;
  // Reconsentimento pedido de novo se o termo mudou de versão desde o último
  // aceite — nasce como caso raro, mas é o próprio motivo de existir a versão.
  const precisaReconsentir = !!(
    contaEmail?.lgpd_aceite_versao && contaEmail?.lgpd_versao_atual &&
    contaEmail.lgpd_aceite_versao !== contaEmail.lgpd_versao_atual
  );

  return (
    <div className="cartao" style={{ marginTop: "1rem" }}>
      {!status?.incluido_no_plano && !STATUS_COM_ACESSO.includes(status?.status ?? "") ? (
        <>
          <h1 style={{ fontSize: "1.25rem", margin: "0 0 0.3rem" }}>
            Seu endereço profissional <span style={{ color: "var(--acao)" }}>@corvia.med.br</span>
          </h1>
          <p style={{ margin: "0 0 0.8rem" }}>
            Um e-mail médico, dentro da mesma plataforma onde você já prescreve, documenta e assina.
          </p>
        </>
      ) : (
        <p>
          Um endereço de e-mail próprio no domínio <strong>@corvia.med.br</strong>, com
          webmail integrado — add-on separado da assinatura principal da Corvia, cobrado à parte.
        </p>
      )}

      {!status?.incluido_no_plano && !STATUS_COM_ACESSO.includes(status?.status ?? "") && (
        <ul style={{ margin: "0 0 1.1rem", paddingLeft: "1.1rem", lineHeight: 1.7 }}>
          <li>Envie receita e documento <strong>já assinados digitalmente</strong> direto ao paciente, sem trocar de aplicativo.</li>
          <li>Assinatura de e-mail com seu nome, conselho e logo em toda mensagem que você manda.</li>
          <li>Leia Yahoo, iCloud, Gmail e Outlook <strong>na mesma caixa</strong>, dentro da Corvia.</li>
          <li>Mande material educativo ao paciente por e-mail em um clique.</li>
        </ul>
      )}

      {status?.incluido_no_plano ? (
        <p style={{ color: "var(--sucesso)" }}>
          Incluído no seu plano <strong>Assinatura Completa</strong> — nenhuma cobrança adicional.
        </p>
      ) : (
        <p>
          <strong>{status?.preco_definido ? `${reais(status.preco_centavos)}/mês` : "Em breve"}</strong>
          {!status?.preco_definido && " — o valor ainda está sendo definido."}
          {status?.preco_definido && " — pagamento em Pix ou cartão, à parte da sua assinatura principal."}
        </p>
      )}

      {erro && <p role="alert" style={{ color: "var(--alerta)", fontSize: "0.86rem" }}>{erro}</p>}

      {!ativa && !status?.incluido_no_plano && (
        <button className="botao" style={{ width: "100%", marginTop: "1rem" }}
                onClick={assinar} disabled={processando || !status?.preco_definido}>
          {processando ? "Redirecionando…" : status?.preco_definido ? "Assinar o CorvIA Mail" : "Em breve"}
        </button>
      )}

      {ativa && (!contaEmail?.ativa || precisaReconsentir) && (
        <div style={{ marginTop: "1rem" }}>
          <p style={{ color: "var(--sucesso)" }}>
            {precisaReconsentir
              ? "O termo de transferência internacional de dados foi atualizado — é preciso ler e aceitar de novo."
              : "Assinatura ativa — falta só criar sua caixa."}
          </p>

          {!contaEmail?.ativa && !precisaReconsentir && (
            <EscolhaDeEndereco valor={localPart} onChange={setLocalPart} onValidadeMudou={setEnderecoValido} />
          )}

          <label htmlFor="senha-inicial" style={{ marginTop: "0.8rem", display: "block" }}>
            {precisaReconsentir ? "Confirme a senha da sua caixa de e-mail" : "Crie uma senha para sua caixa de e-mail"}
          </label>
          <input id="senha-inicial" type="password" value={senhaInicial}
                 onChange={(e) => setSenhaInicial(e.target.value)} />
          <p className="eyebrow" style={{ margin: "0.3rem 0 0" }}>
            {precisaReconsentir
              ? "Digite a senha atual da caixa (ou defina uma nova, se preferir)."
              : "Senha própria, diferente da senha da sua conta Corvia."}
          </p>

          {termo && (
            <div style={{ marginTop: "0.8rem" }}>
              <p className="eyebrow" style={{ margin: 0 }}>
                Termo de transferência internacional de dados (versão {termo.versao})
              </p>
              <div style={{
                whiteSpace: "pre-wrap", fontSize: "0.82rem", maxHeight: 220, overflowY: "auto",
                border: "1px solid var(--linha)", borderRadius: 6, padding: "0.6rem", marginTop: "0.4rem",
              }}>
                {termo.texto}
              </div>
              <label style={{ display: "flex", gap: 8, alignItems: "flex-start", marginTop: "0.6rem", fontSize: "0.86rem" }}>
                <input type="checkbox" checked={aceiteLgpd} style={{ width: "auto", marginTop: 3 }}
                       onChange={(e) => setAceiteLgpd(e.target.checked)} />
                Li e concordo com este termo.
              </label>
            </div>
          )}

          <button className="botao" style={{ width: "100%", marginTop: "0.8rem" }}
                  onClick={ativarCaixa}
                  disabled={
                    ativando || !aceiteLgpd || senhaInicial.length < 8 ||
                    (!contaEmail?.ativa && !precisaReconsentir && !enderecoValido)
                  }>
            {ativando ? "Ativando…" : precisaReconsentir ? "Confirmar novo aceite" : "Ativar minha caixa de e-mail"}
          </button>
        </div>
      )}

      {ativa && contaEmail?.ativa && !precisaReconsentir && (
        <p style={{ color: "var(--sucesso)", marginTop: "1rem" }}>
          Sua caixa <strong>{contaEmail.email_address}</strong> está pronta — entre na aba "Entrar" ao lado.
        </p>
      )}

      {ativa && (
        <button className="botao botao--secundario" style={{ width: "100%", marginTop: "0.8rem" }}
                onClick={abrirPortal} disabled={processando}>
          {processando ? "Abrindo…" : "Gerenciar assinatura (cartão, Pix, cancelar)"}
        </button>
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
  const navigate = useNavigate();
  const [aba, setAba] = useState<"entrar" | "esqueci" | "assinar">("entrar");
  // `null` = ainda não sabemos. Decide duas coisas: (1) se a caixa já está
  // ativa E existe sessão de e-mail salva, pula esta tela inteira e vai
  // direto pra caixa — mesma lógica que o atalho do Painel já usa; (2) se a
  // caixa NUNCA foi ativada, "Entrar"/"Esqueci a senha" não servem pra nada
  // (não existe credencial pra usar ali) — só a aba "Assine já" faz
  // sentido, e ela nasce como a única visível.
  const [contaAtiva, setContaAtiva] = useState<boolean | null>(null);

  useEffect(() => {
    if (!usuario) return;
    api.get<ContaEmail>("/email/conta")
      .then((c) => {
        setContaAtiva(c.ativa);
        if (c.ativa && tokenEmail.get()) {
          navigate("/caixa-de-email", { replace: true });
        } else if (!c.ativa) {
          setAba("assinar");
        }
      })
      .catch(() => setContaAtiva(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [usuario]);

  if (carregando || (usuario && contaAtiva === null)) return <p className="eyebrow">Carregando…</p>;
  if (usuario && contaAtiva && tokenEmail.get()) return <p className="eyebrow">Abrindo sua caixa…</p>;

  if (!usuario) {
    return (
      <div className="login">
        <div className="login__cartao">
          <div className="login__brasao">
            <LogoCorviaMail />
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
    <div className="pagina" style={{ maxWidth: "560px" }}>
      <div style={{ marginBottom: "1rem" }}>
        <LogoCorviaMail tamanho="compacto" />
      </div>

      {contaAtiva && (
        <div style={{ display: "flex", gap: 6 }}>
          <button className={aba === "entrar" ? "botao" : "botao botao--secundario"}
                  style={{ flex: 1 }} onClick={() => setAba("entrar")}>Entrar</button>
          <button className={aba === "esqueci" ? "botao" : "botao botao--secundario"}
                  style={{ flex: 1 }} onClick={() => setAba("esqueci")}>Esqueci a senha</button>
          <button className={aba === "assinar" ? "botao" : "botao botao--secundario"}
                  style={{ flex: 1 }} onClick={() => setAba("assinar")}>Gerenciar</button>
        </div>
      )}
      {/* Caixa nunca ativada: "Entrar"/"Esqueci a senha" não levam a lugar
          nenhum (não existe credencial ainda) — só a página de assinatura
          faz sentido, e é ela que carrega a propaganda do serviço. */}

      {aba === "entrar" && <AbaEntrar />}
      {aba === "esqueci" && <AbaEsqueciSenha />}
      {aba === "assinar" && <AbaAssinar />}
    </div>
  );
}
