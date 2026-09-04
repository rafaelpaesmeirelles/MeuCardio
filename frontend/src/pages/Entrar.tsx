import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import Icone from "../components/Icone";
import { useAuth } from "../lib/auth";
import { CORVIA_LOGIN_THEME_KEY, type CorviaTheme } from "../lib/corviaTheme";
import "../styles/login.css";
import "../styles/login-fullscreen-social.css";
import "../styles/prehome-reference-final.css";
import "../styles/login-viewport-refinement.css";
import "../styles/cardiology-spaces-login.css";
import "../styles/cardiology-spaces-login-approved-final.css";
import "../styles/cardiology-spaces-login-galaxy-kinematics.css";
import "../styles/cardiology-spaces-login-production-approved.css";
import "../styles/corvia-approved-fidelity-20260904.css";

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

function CoracaoLoginAprovado() {
  return (
    <svg
      className="prehome-brand__heart login-gateway__approved-heart"
      viewBox="0 0 260 310"
      role="img"
      aria-label="Coração anatômico luminoso do CorVIA"
    >
      <defs>
        <linearGradient id="approved-heart-shell" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#0dd9ee" />
          <stop offset=".42" stopColor="#176dff" />
          <stop offset=".72" stopColor="#7348f4" />
          <stop offset="1" stopColor="#ff4c86" />
        </linearGradient>
        <linearGradient id="approved-heart-red" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#ff8ca8" />
          <stop offset=".45" stopColor="#ff4e76" />
          <stop offset="1" stopColor="#ff2758" />
        </linearGradient>
        <linearGradient id="approved-heart-blue" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#6af5ff" />
          <stop offset=".45" stopColor="#1ba2ff" />
          <stop offset="1" stopColor="#365cff" />
        </linearGradient>
        <radialGradient id="approved-heart-fill" cx="48%" cy="42%" r="66%">
          <stop offset="0" stopColor="#0a2448" stopOpacity=".98" />
          <stop offset=".58" stopColor="#051428" stopOpacity=".98" />
          <stop offset="1" stopColor="#020912" stopOpacity=".98" />
        </radialGradient>
        <filter id="approved-heart-glow" x="-80%" y="-80%" width="260%" height="260%">
          <feGaussianBlur stdDeviation="3.2" result="blur" />
          <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
      </defs>

      <g filter="url(#approved-heart-glow)">
        <path d="M103 92C88 66 89 39 104 20c10-12 26-15 37-7 12 9 11 25 4 39-8 15-12 29-8 45" fill="none" stroke="url(#approved-heart-blue)" strokeWidth="12" strokeLinecap="round" />
        <path d="M142 88c2-27 12-54 31-70 14-12 32-10 40 3 9 14 0 29-13 40-15 12-24 26-27 44" fill="none" stroke="url(#approved-heart-red)" strokeWidth="13" strokeLinecap="round" />
        <path d="M166 100c13-25 29-40 47-43 15-2 28 7 28 20 0 14-14 21-27 26-11 4-20 12-26 22" fill="none" stroke="#9e62ff" strokeWidth="10" strokeLinecap="round" />
        <path d="M87 104c-20-17-42-21-57-11-14 9-16 25-7 36 10 11 25 6 38 4 13-2 25 1 36 10" fill="none" stroke="#25dce9" strokeWidth="9" strokeLinecap="round" />
      </g>

      <path d="M116 88c-31-15-68-3-85 26-18 30-11 67 7 95 15 25 36 40 52 59 12 14 20 31 26 46 3 7 12 8 16 2 14-20 32-38 48-57 22-27 39-58 43-92 3-33-11-65-40-79-21-10-46-7-67 0Z" fill="url(#approved-heart-fill)" stroke="url(#approved-heart-shell)" strokeWidth="4" filter="url(#approved-heart-glow)" />

      <path d="M120 101c-14 18-22 39-23 62-1 42 25 77 31 118 6-30 3-63 16-89 12-23 33-37 57-47-12-29-36-50-65-52-6 0-11 3-16 8Z" fill="rgba(255,70,105,.08)" stroke="#ff5478" strokeWidth="1.5" />
      <path d="M115 103c-29-9-56 3-68 27-11 22-4 48 10 68 15 21 35 36 47 58-3-30-10-60-5-89 4-26 12-45 16-64Z" fill="rgba(32,157,255,.07)" stroke="#2ed9ea" strokeWidth="1.5" />

      <g fill="none" strokeLinecap="round" filter="url(#approved-heart-glow)">
        <path d="M119 111c-8 27-7 54 2 80 10 30 9 62 6 94" stroke="#ff4f74" strokeWidth="3.5" />
        <path d="M114 114c-16 18-24 39-25 63-1 29 12 57 18 85" stroke="#36dfea" strokeWidth="3" />
        <path d="M121 132c19 4 36 15 48 31 12 18 19 40 18 63" stroke="#ff567b" strokeWidth="2.6" />
        <path d="M112 140c-20 3-37 14-47 30-9 15-13 33-11 51" stroke="#41e5f1" strokeWidth="2.4" />
        <path d="M131 171c20 8 34 23 42 42M101 180c-18 7-30 19-38 35M138 198c15 7 25 18 31 32M100 210c-14 6-24 16-30 27M133 229c13 8 20 18 25 28" stroke="#82efff" strokeWidth="1.55" opacity=".72" />
        <path d="M143 125c7 16 7 32 2 48" stroke="#ff6683" strokeWidth="2.8" />
      </g>

      <g filter="url(#approved-heart-glow)">
        <circle cx="97" cy="144" r="3.2" fill="#56efff" />
        <circle cx="145" cy="158" r="3.2" fill="#ff5b7e" />
        <circle cx="126" cy="201" r="3" fill="#a56fff" />
        <circle cx="90" cy="214" r="2.4" fill="#58e9f7" />
        <circle cx="161" cy="216" r="2.4" fill="#ff5275" />
      </g>
    </svg>
  );
}

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

        <div className="login-gateway__top-actions">
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

          <div className="login-gateway__security">
            <span><i /> Protegido</span>
          </div>
        </div>
      </header>

      <section className="login-gateway__scene" aria-labelledby="login-title">
        <header className="login-gateway__hero">
          <p>CORVIA · CARDIOLOGY SPACES</p>
          <h1 id="login-title">Um universo de espaços. <strong>Uma só cardiologia.</strong></h1>
          <span>Consultório, Hospital, Ensino, Pesquisa e Gestão orbitando juntos no seu Universo Profissional.</span>
        </header>

        <div className="login-gateway__universe" aria-hidden="true">
          <div className="login-gateway__milky-way">
            <video
              className="login-gateway__galaxy-video"
              src="/spaces/galaxy-loop-v2.mp4"
              poster="/spaces/galaxy-loop-poster.webp"
              autoPlay
              muted
              loop
              playsInline
              preload="auto"
              tabIndex={-1}
              controls={false}
              disablePictureInPicture
            />
          </div>
          <div className="login-gateway__core">
            <span className="login-gateway__core-glow" />
            <CoracaoLoginAprovado />
            <svg className="login-gateway__pulse" viewBox="0 0 360 48">
              <path className="login-gateway__pulse-baseline" d="M2 29H358" />
              <path className="login-gateway__pulse-trace" d="M2 29H29C35 29 37 23 43 23S52 29 59 29H81L88 32L96 8L105 42L113 29H137C148 29 151 16 164 16S181 29 195 29H224C230 29 232 23 238 23S247 29 254 29H275L282 32L290 8L299 42L307 29H329C340 29 343 17 358 17" />
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
