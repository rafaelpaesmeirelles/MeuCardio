import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import Icone from "../components/Icone";
import { CoracaoHolografico } from "../components/PreHomeBrand";
import { useAuth } from "../lib/auth";
import { CORVIA_LOGIN_THEME_KEY, type CorviaTheme } from "../lib/corviaTheme";
import "../styles/login.css";
import "../styles/login-fullscreen-social.css";
import "../styles/prehome-reference-final.css";
import "../styles/login-viewport-refinement.css";
import "../styles/cardiology-spaces-login.css";
import "../styles/cardiology-spaces-login-approved-final.css";
import "../styles/cardiology-spaces-login-motion-fidelity.css";

type TemaPublico = CorviaTheme;

function temaPublicoInicial(): TemaPublico {
  try {
    return sessionStorage.getItem(CORVIA_LOGIN_THEME_KEY) === "light" ? "light" : "dark";
  } catch {
    return "dark";
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
  { id: "light", nome: "Modo claro", detalhe: "Clareza clínica", icone: "sol" },
  { id: "dark", nome: "Modo escuro", detalhe: "Imersão cósmica", icone: "lua" },
];

const ESPACOS = [
  { id: "consultorio", nome: "Consultório", detalhe: "Assistência", icone: "clinica" as const },
  { id: "hospital", nome: "Hospital", detalhe: "Decisão", icone: "emergencia" as const },
  { id: "ensino", nome: "Ensino", detalhe: "Formação", icone: "curso" as const },
  { id: "pesquisa", nome: "Pesquisa", detalhe: "Evidência", icone: "evidencia" as const },
  { id: "gestao", nome: "Gestão", detalhe: "Estratégia", icone: "gestao" as const },
];

export default function Entrar() {
  const { entrar } = useAuth();
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
      className={`login login-gateway login-gateway--public login-gateway--${temaPublico}`}
      data-login-theme={temaPublico}
    >
      <div className="login-gateway__aurora" aria-hidden="true" />
      <div className="login-gateway__stars" aria-hidden="true"><i /><i /><i /><i /><i /><i /><i /><i /><i /><i /></div>

      <header className="login-gateway__topbar">
        <Link to="/" className="login-gateway__brand" aria-label="CorVIA — página inicial">
          <img src="/corvia-mark-canonical.svg" alt="" aria-hidden="true" />
          <span><strong><span>Cor</span><span className="corvia-via">VIA</span></strong><small>CARDIOLOGY SPACES</small></span>
        </Link>
        <div className="login-gateway__security">
          <span><i /> Ambiente protegido</span>
          <small>Acesso profissional · LGPD</small>
        </div>
      </header>

      <section className="login-gateway__scene" aria-labelledby="login-title">
        <p className="login-gateway__desktop-kicker" aria-hidden="true">CORVIA · CARDIOLOGY SPACES</p>
        <header className="login-gateway__hero">
          <p>CORVIA · CARDIOLOGY SPACES</p>
          <h1 id="login-title">Um universo de espaços. <strong>Uma só cardiologia.</strong></h1>
          <span>Consultório, Hospital, Ensino, Pesquisa e Gestão orbitando juntos no seu Universo Profissional.</span>
        </header>

        <div className="login-gateway__universe" aria-hidden="true">
          <div className="login-gateway__milky-way"><span /></div>
          <div className="login-gateway__core">
            <span className="login-gateway__core-glow" />
            <CoracaoHolografico />
            <svg className="login-gateway__pulse" viewBox="0 0 420 44">
              <path className="login-gateway__pulse-baseline" d="M2 28H418" />
              <path
                className="login-gateway__pulse-trace"
                pathLength="1"
                d="M2 28H32C39 28 42 24 48 24S57 28 64 28H84L91 30L97 18L104 35L111 28H143C153 28 158 21 168 21S186 28 198 28H230C237 28 240 24 246 24S255 28 262 28H282L289 30L295 18L302 35L309 28H341C351 28 356 21 366 21S384 28 396 28H418"
              />
            </svg>
          </div>
          <div className="login-gateway__spaces">
            {ESPACOS.map((espaco) => (
              <article className={`login-gateway__space login-gateway__space--${espaco.id}`} key={espaco.id}>
                <span><Icone nome={espaco.icone} /></span>
                <div><strong>{espaco.nome}</strong><small>{espaco.detalhe}</small></div>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="login-gateway__console" aria-labelledby="login-acesso-titulo">
        <header className="login-gateway__console-head">
          <span><Icone nome="conta" /></span>
          <div><p>IDENTIDADE PROFISSIONAL</p><h2 id="login-acesso-titulo">Entre no CorVIA</h2></div>
        </header>

        <fieldset className="login-gateway__theme-choice" aria-describedby="login-theme-note">
          <legend>Escolha a aparência</legend>
          <div className="login-gateway__theme-choice-options">
            {TEMAS_PUBLICOS.map((opcao) => (
              <label className={temaPublico === opcao.id ? "is-selected" : ""} key={opcao.id}>
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
          <p id="login-theme-note"><Icone nome="check" /> Preferência visual desta sessão. Seu acesso e suas permissões não mudam.</p>
        </fieldset>

        <form className="login-gateway__form" onSubmit={enviar}>
          <label className="login-gateway__field" htmlFor="email">
            <span>E-mail profissional</span>
            <div><Icone nome="mail" /><input id="email" type="email" inputMode="email" autoCapitalize="none" autoComplete="username" placeholder="seu@email.com" value={email} onChange={(event) => setEmail(event.target.value)} aria-invalid={Boolean(erro)} aria-describedby={erro ? "login-erro" : undefined} required /></div>
          </label>
          <label className="login-gateway__field" htmlFor="senha">
            <span>Senha</span>
            <div className="login-gateway__password"><Icone nome="configuracao" /><input id="senha" type={mostrarSenha ? "text" : "password"} autoComplete="current-password" placeholder="Digite sua senha" value={senha} onChange={(event) => setSenha(event.target.value)} aria-invalid={Boolean(erro)} aria-describedby={erro ? "login-erro" : undefined} required /><button type="button" onClick={() => setMostrarSenha((visivel) => !visivel)} aria-label={mostrarSenha ? "Ocultar senha" : "Mostrar senha"} aria-pressed={mostrarSenha}><Icone nome={mostrarSenha ? "olho-fechado" : "olho"} /></button></div>
          </label>
          <button className="login-gateway__enter" type="submit" disabled={enviando}>
            <span>{enviando ? "Abrindo seus espaços…" : "Entrar"}</span>
            {!enviando ? <Icone nome="seta" /> : <i className="login-formulario__carregando" aria-hidden="true" />}
          </button>
          {erro && <p id="login-erro" className="login-gateway__error" role="alert">{erro}</p>}
        </form>

        <Link className="login-gateway__join" to="/solicitar-acesso">
          <span><Icone nome="conta" /></span>
          <span><strong>Novo no CorVIA?</strong><small>Solicite seu Acesso</small></span>
          <Icone nome="seta" />
        </Link>
      </section>

      <footer className="login-gateway__footer">
        <div className="login-gateway__form-meta">
          <label htmlFor="permanecer"><input id="permanecer" type="checkbox" checked={permanecerConectado} onChange={(event) => setPermanecerConectado(event.target.checked)} />Manter este acesso</label>
          <Link to="/esqueci-senha">Esqueci minha senha</Link>
        </div>
        <nav aria-label="Links institucionais"><Link to="/privacidade">Privacidade</Link><Link to="/termos">Termos</Link><a href="mailto:contato@corvia.med.br">Suporte</a></nav>
      </footer>
    </main>
  );
}
