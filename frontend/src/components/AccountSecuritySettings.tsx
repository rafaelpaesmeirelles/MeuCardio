import { useEffect, useRef, useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { api, ApiError, READ_TIMEOUT_MS } from "../lib/api";
import { useAuth } from "../lib/auth";

type RecoveryEmail = { recovery_email: string | null };

export function EmailRecuperacao({ loginEmail }: { loginEmail: string }) {
  const [atual, setAtual] = useState<string | null>(null);
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [carregando, setCarregando] = useState(true);
  const [erroLeitura, setErroLeitura] = useState("");
  const [tentativa, setTentativa] = useState(0);
  const [salvando, setSalvando] = useState(false);
  const [erro, setErro] = useState("");
  const [ok, setOk] = useState(false);
  const operacao = useRef(false);
  const montado = useRef(false);

  useEffect(() => {
    montado.current = true;
    return () => { montado.current = false; };
  }, []);

  useEffect(() => {
    let ativo = true;
    const controller = new AbortController();
    setCarregando(true);
    setErroLeitura("");
    api.get<RecoveryEmail>("/auth/email-recuperacao", { signal: controller.signal, timeoutMs: READ_TIMEOUT_MS })
      .then((resposta) => {
        if (!ativo) return;
        setAtual(resposta.recovery_email);
        setEmail(resposta.recovery_email ?? "");
      })
      .catch(() => { if (ativo) setErroLeitura("Não foi possível consultar o e-mail de recuperação. Tente novamente."); })
      .finally(() => { if (ativo) setCarregando(false); });
    return () => { ativo = false; controller.abort(); };
  }, [loginEmail, tentativa]);

  const normalizado = email.trim().toLowerCase();
  const igualAoLogin = normalizado === loginEmail.trim().toLowerCase();
  const valido = /^[^\s@]+@[^\s@]+$/.test(normalizado) && !igualAoLogin;
  const alterado = normalizado !== (atual ?? "");

  async function salvar(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (operacao.current || carregando || erroLeitura || !valido || !alterado || !senha) return;
    operacao.current = true;
    setSalvando(true);
    setErro("");
    setOk(false);
    try {
      const resposta = await api.put<RecoveryEmail>("/auth/email-recuperacao", {
        recovery_email: normalizado, senha_atual: senha,
      });
      if (!montado.current) return;
      setAtual(resposta.recovery_email);
      setEmail(resposta.recovery_email ?? "");
      setOk(true);
    } catch (error) {
      if (montado.current) setErro(error instanceof ApiError ? error.message : "Não foi possível atualizar o e-mail de recuperação. Tente novamente.");
    } finally {
      operacao.current = false;
      if (montado.current) { setSenha(""); setSalvando(false); }
    }
  }

  return (
    <section className="cartao" aria-labelledby="email-recuperacao-titulo">
      <h2 id="email-recuperacao-titulo" style={{ marginTop: 0 }}>E-mail de recuperação</h2>
      <p id="email-recuperacao-ajuda" style={{ color: "var(--texto-secundario)" }}>
        Use um endereço externo ao qual você tenha acesso, diferente do e-mail de login. Os links de recuperação serão enviados para ele.
      </p>
      {carregando ? <p role="status">Consultando e-mail de recuperação…</p> : erroLeitura ? (
        <div>
          <p role="alert">{erroLeitura}</p>
          <button type="button" className="botao botao--secundario" onClick={() => setTentativa((valor) => valor + 1)}>Tentar consultar novamente</button>
        </div>
      ) : (
        <form onSubmit={salvar} aria-busy={salvando}>
          <p>{atual ? <>Endereço atual: <strong>{atual}</strong></> : "Nenhum e-mail de recuperação cadastrado."}</p>
          <label htmlFor="email-recuperacao">E-mail de recuperação</label>
          <input id="email-recuperacao" type="email" autoComplete="email" required value={email} disabled={salvando}
            aria-describedby="email-recuperacao-ajuda email-recuperacao-validacao" aria-invalid={!!email && !valido}
            onChange={(event) => { setEmail(event.target.value); setErro(""); setOk(false); }} />
          <p id="email-recuperacao-validacao" style={{ color: "var(--alerta)" }}>
            {igualAoLogin ? "Informe um endereço diferente do e-mail de login." : ""}
          </p>
          <label htmlFor="email-recuperacao-senha">Senha atual</label>
          <input id="email-recuperacao-senha" type="password" autoComplete="current-password" required value={senha} disabled={salvando}
            onChange={(event) => { setSenha(event.target.value); setErro(""); setOk(false); }} />
          {erro && <p role="alert" style={{ color: "var(--alerta)" }}>{erro}</p>}
          {ok && <p role="status" style={{ color: "var(--sucesso)" }}>E-mail de recuperação atualizado.</p>}
          <button type="submit" className="botao" style={{ marginTop: "0.8rem" }} disabled={salvando || !valido || !alterado || !senha}>
            {salvando ? "Salvando…" : "Salvar e-mail de recuperação"}
          </button>
        </form>
      )}
    </section>
  );
}

export function SessoesConta() {
  const { usuario, sair } = useAuth();
  const navigate = useNavigate();
  const [encerrando, setEncerrando] = useState(false);
  const [erro, setErro] = useState("");
  const operacao = useRef(false);
  const montado = useRef(false);
  const identidadeAtual = useRef(usuario?.id);
  const geracao = useRef(0);
  identidadeAtual.current = usuario?.id;

  useEffect(() => {
    montado.current = true;
    geracao.current++;
    operacao.current = false;
    setEncerrando(false);
    setErro("");
    return () => { montado.current = false; };
  }, [usuario?.id]);

  async function encerrar() {
    if (operacao.current || !usuario) return;
    if (!window.confirm("Encerrar todas as sessões desta conta, incluindo a sessão em uso? Você precisará entrar novamente em cada dispositivo.")) return;
    const identidade = usuario.id;
    const versao = geracao.current;
    const vigente = () => montado.current && identidadeAtual.current === identidade && geracao.current === versao;
    operacao.current = true;
    setEncerrando(true);
    setErro("");
    try {
      await api.post("/auth/encerrar-todas-sessoes");
    } catch (error) {
      if (!vigente()) return;
      setErro(error instanceof ApiError ? error.message : "Não foi possível confirmar o encerramento das sessões. Tente novamente.");
      operacao.current = false;
      setEncerrando(false);
      return;
    }
    if (!vigente()) return;
    try {
      // AuthProvider clears React identity and clinical caches even if the
      // additional local logout request fails; revocation already succeeded.
      await sair();
    } catch { /* The confirmed revocation must still return to the login. */ }
    if (!vigente()) return;
    navigate("/entrar", { replace: true, state: { todasSessoesEncerradas: true } });
  }

  return (
    <section className="cartao" aria-labelledby="sessoes-conta-titulo" aria-busy={encerrando}>
      <h2 id="sessoes-conta-titulo" style={{ marginTop: 0 }}>Sessões da conta</h2>
      <p id="sessoes-conta-ajuda" style={{ color: "var(--texto-secundario)" }}>
        Encerre o acesso desta conta em todos os dispositivos, incluindo este. Sua senha continuará válida para entrar novamente.
      </p>
      {erro && <p role="alert" style={{ color: "var(--alerta)" }}>{erro}</p>}
      <button type="button" className="botao botao--secundario" aria-describedby="sessoes-conta-ajuda" onClick={encerrar} disabled={encerrando}>
        {encerrando ? "Encerrando sessões…" : "Encerrar todas as sessões"}
      </button>
    </section>
  );
}
