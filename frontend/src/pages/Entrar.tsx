import { useState, type FormEvent } from "react";
import { Link, useLocation } from "react-router-dom";
import Icone from "../components/Icone";
import { useAuth } from "../lib/auth";
import { CORVIA_LOGIN_THEME_KEY, type CorviaTheme } from "../lib/corviaTheme";
import "../styles/corvia-atelier-login.css";

type TemaPublico = CorviaTheme;

function temaPublicoInicial(): TemaPublico {
  try {
    return sessionStorage.getItem(CORVIA_LOGIN_THEME_KEY) === "dark" ? "dark" : "light";
  } catch {
    return "light";
  }
}

function persistirTemaPublico(temaPublico: TemaPublico, limparModo = false) {
  try {
    sessionStorage.setItem(CORVIA_LOGIN_THEME_KEY, temaPublico);
    if (limparModo) sessionStorage.removeItem("corvia:cardiology-spaces:mode");
  } catch {
    // Restrições de armazenamento do navegador não podem impedir o acesso.
  }
}

const TEMAS_PUBLICOS: Array<{
  id: TemaPublico;
  nome: string;
  detalhe: string;
  icone: "sol" | "lua";
}> = [
  { id: "light", nome: "Modo claro", detalhe: "Pérola e champagne", icone: "sol" },
  { id: "dark", nome: "Modo escuro", detalhe: "Grafite e luz suave", icone: "lua" },
];

const ESPACOS = [
  { id: "consultorio", nome: "Consultório", icone: "clinica" as const },
  { id: "hospital", nome: "Hospital", icone: "emergencia" as const },
  { id: "ensino", nome: "Ensino", icone: "curso" as const },
  { id: "pesquisa", nome: "Pesquisa", icone: "evidencia" as const },
  { id: "gestao", nome: "Gestão", icone: "gestao" as const },
];

export default function Entrar() {
  const { entrar } = useAuth();
  const location = useLocation();
  const [temaPublico, setTemaPublico] = useState<TemaPublico>(temaPublicoInicial);
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [mostrarSenha, setMostrarSenha] = useState(false);
  const [permanecerConectado, setPermanecerConectado] = useState(false);
  const [erro, setErro] = useState("");
  const [enviando, setEnviando] = useState(false);

  function selecionarTemaPublico(proximoTema: TemaPublico) {
    setTemaPublico(proximoTema);
    persistirTemaPublico(proximoTema);
  }

  async function enviar(event?: FormEvent<HTMLFormElement>) {
    event?.preventDefault();
    if (enviando || !email.trim() || !senha) return;
    setEnviando(true);
    setErro("");
    try {
      persistirTemaPublico(temaPublico, true);
      await entrar(email.trim().toLowerCase(), senha, permanecerConectado);
    } catch (e) {
      setErro(e instanceof Error ? e.message : "Não foi possível entrar.");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <main
      id="corvia-login"
      className={`login login-gateway login-gateway--public login-gateway--${temaPublico} corvia-atelier-login`}
      data-login-theme={temaPublico}
    >
      <a className="atelier-login__skip" href="#login-acesso-titulo">Ir para o acesso</a>
      <header className="atelier-login__topbar">
        <Link to="/" className="atelier-login__brand" aria-label="CorVIA — página inicial">
          <img src="/atelier/corvia-logo-atelier.svg" width="900" height="240" alt="CorVIA Cardiology Spaces" />
        </Link>

        <span className="atelier-login__perspective"><i aria-hidden="true" /> Uma nova perspectiva</span>

        <div className="atelier-login__top-actions">
          <Link to="/produto" className="atelier-login__explore">Conhecer o CorVIA <Icone nome="seta" /></Link>
          <fieldset className="login-gateway__theme-choice login-gateway__theme-choice--top" aria-describedby="login-theme-note">
            <legend>Escolha a aparência</legend>
            <div className="login-gateway__theme-choice-options">
              {TEMAS_PUBLICOS.map((opcao) => (
                <label className={temaPublico === opcao.id ? "is-selected" : ""} key={opcao.id} title={opcao.nome}>
                  <input
                    type="radio"
                    name="tema-publico"
                    value={opcao.id}
                    checked={temaPublico === opcao.id}
                    onChange={() => selecionarTemaPublico(opcao.id)}
                  />
                  <span className="login-gateway__theme-choice-icon"><Icone nome={opcao.icone} /></span>
                  <span><strong>{opcao.nome}</strong><small>{opcao.detalhe}</small></span>
                  <i aria-hidden="true"><Icone nome="check" /></i>
                </label>
              ))}
            </div>
            <p id="login-theme-note"><Icone nome="check" /> Preferência visual desta sessão.</p>
          </fieldset>
        </div>
      </header>

      <div className="atelier-login__layout">
        <section className="atelier-login__story" aria-labelledby="login-title">
          <header className="atelier-login__copy">
            <p className="atelier-login__eyebrow">CorVIA · Cardiology Spaces</p>
            <h1 id="login-title">Cinco espaços de trabalho.<br /><em>Uma só cardiologia.</em></h1>
            <p>Os espaços de trabalho mudam.<br />O CorVIA permanece ao seu lado.</p>
          </header>
          <figure className="atelier-login__entrance">
            <img src="/atelier/atelier-entrance.webp" width="1536" height="1024" alt="Recepção com pedra natural, madeira e jardim, na identidade arquitetônica do CorVIA." fetchPriority="high" />
            <figcaption><i aria-hidden="true" /> O cuidado também começa no espaço.</figcaption>
          </figure>
          <div className="atelier-login__spaces" aria-label="Cinco espaços de trabalho">
            {ESPACOS.map((espaco) => (
              <span key={espaco.id}><Icone nome={espaco.icone} />{espaco.nome}</span>
            ))}
          </div>
        </section>

      <section className="atelier-login__access" aria-labelledby="login-acesso-titulo">
        <header className="atelier-login__access-heading">
          <p className="atelier-login__eyebrow">Seu ponto de partida</p>
          <h2 id="login-acesso-titulo" tabIndex={-1}>Bem-vindo<br /> ao seu espaço.</h2>
          <p>Conhecimento, cuidado e rotina.<br />Conectados por você.</p>
        </header>

        {location.state?.todasSessoesEncerradas === true && <p role="status" className="atelier-login__security">Todas as sessões da conta foram encerradas. Entre novamente para continuar.</p>}

        <form className="login-gateway__form" onSubmit={enviar} aria-busy={enviando}>
          <label className="login-gateway__field" htmlFor="email">
            <span>E-mail profissional</span>
            <div><Icone nome="mail" /><input id="email" type="email" inputMode="email" autoCapitalize="none" autoComplete="username" placeholder="seu@email.com" value={email} onChange={(event) => setEmail(event.target.value)} aria-invalid={Boolean(erro)} aria-describedby={erro ? "login-erro" : undefined} required /></div>
          </label>
          <label className="login-gateway__field" htmlFor="senha">
            <span>Senha</span>
            <div className="login-gateway__password"><Icone nome="cadeado" /><input id="senha" type={mostrarSenha ? "text" : "password"} autoComplete="current-password" placeholder="Digite sua senha" value={senha} onChange={(event) => setSenha(event.target.value)} aria-invalid={Boolean(erro)} aria-describedby={erro ? "login-erro" : undefined} required /><button type="button" onClick={() => setMostrarSenha((visivel) => !visivel)} aria-label={mostrarSenha ? "Ocultar senha" : "Mostrar senha"} aria-pressed={mostrarSenha}><Icone nome={mostrarSenha ? "olho-fechado" : "olho"} /></button></div>
          </label>
          <div className="atelier-login__form-options">
            <label className="atelier-login__remember"><input type="checkbox" checked={permanecerConectado} onChange={(event) => setPermanecerConectado(event.target.checked)} />Permanecer conectado</label>
            <Link className="login-gateway__forgot" to="/esqueci-senha">Esqueceu sua senha?</Link>
          </div>
          <button className="login-gateway__enter" type="submit" disabled={enviando}>
            <span>{enviando ? "Abrindo seus espaços…" : "Entrar"}</span>
            {!enviando ? <Icone nome="seta" /> : <i className="login-formulario__carregando" aria-hidden="true" />}
          </button>
          {erro && <p id="login-erro" className="login-gateway__error" role="alert">{erro}</p>}
          <p className="atelier-login__security"><Icone nome="seguranca" /><span>{temaPublico === "light" ? "Sistema seguro" : "Ambiente Protegido"} · Acesso profissional</span></p>
        </form>

        <div className="atelier-login__divider"><span>Novo no CorVIA?</span></div>
        <Link className="atelier-login__join" to="/solicitar-acesso">Solicitar acesso profissional <Icone nome="seta" /></Link>
        <p className="atelier-login__continuity">Cinco maneiras de trabalhar.<br />A mesma continuidade.</p>
      </section>
      </div>

      <footer className="atelier-login__footer">
        <span>Arquitetura para acolher. Inteligência para trabalhar.</span>
        <nav aria-label="Links institucionais"><Link to="/privacidade">Privacidade</Link><Link to="/termos">Termos</Link><a href="mailto:contato@corvia.med.br">Suporte</a></nav>
      </footer>
    </main>
  );
}
