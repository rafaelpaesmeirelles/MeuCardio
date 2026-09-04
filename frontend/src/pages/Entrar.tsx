import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import Icone from "../components/Icone";
import { approvedHeartDataUri } from "../assets/approvedHeartData";
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
import "../styles/corvia-approved-fidelity-asset-fix-20260904.css";
import "../styles/corvia-login-final-approved-20260904.css";

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
  { id: "consultorio", nome: "Consultório", icone: "clinica" as const },
  { id: "hospital", nome: "Hospital", icone: "emergencia" as const },
  { id: "ensino", nome: "Ensino", icone: "curso" as const },
  { id: "pesquisa", nome: "Pesquisa", icone: "evidencia" as const },
  { id: "gestao", nome: "Gestão", icone: "gestao" as const },
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

        <div className="login-gateway__motto" aria-hidden="true">CIÊNCIA · PRÁTICA · PESSOAS · SEMPRE JUNTOS</div>

        <div className="login-gateway__top-actions">
          <p className="login-gateway__slogan">UM UNIVERSO<br />MAIS SAUDÁVEL<br />COMEÇA AQUI</p>
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
          <div className="login-gateway__security" aria-label={temaPublico === "light" ? "Sistema seguro" : "Ambiente Protegido"}>
            <Icone nome="seguranca" />
            <span>{temaPublico === "light" ? "Sistema seguro" : "Ambiente Protegido"}</span>
          </div>

        </div>
      </header>

      <section className="login-gateway__scene" aria-labelledby="login-title">
        <header className="login-gateway__hero">
          <h1 id="login-title">Um universo de espaços. <strong>Uma só cardiologia.</strong></h1>
          <span>Consultório, Hospital, Ensino, Pesquisa e Gestão orbitando juntos no seu Universo Profissional.</span>
        </header>

        <div className="login-gateway__universe" aria-hidden="true">
          <div className="login-gateway__milky-way">
            <img className="login-gateway__galaxy-image" src="/spaces/corvia-galaxy-cameo.webp" alt="" aria-hidden="true" draggable={false} />
          </div>
          <div className="login-gateway__core">
            <span className="login-gateway__core-glow" />
            <img className="login-gateway__approved-heart" src={approvedHeartDataUri} alt="" aria-hidden="true" draggable={false} />
            <svg className="login-gateway__pulse" viewBox="0 0 360 48">
              <path className="login-gateway__pulse-baseline" d="M2 29H358" />
              <path className="login-gateway__pulse-trace" d="M2 29H29C35 29 37 23 43 23S52 29 59 29H81L88 32L96 8L105 42L113 29H137C148 29 151 16 164 16S181 29 195 29H224C230 29 232 23 238 23S247 29 254 29H275L282 32L290 8L299 42L307 29H329C340 29 343 17 358 17" />
            </svg>
          </div>
          <div className="login-gateway__spaces">
            {ESPACOS.map((espaco) => (
              <article className={`login-gateway__space login-gateway__space--${espaco.id}`} key={espaco.id}>
                <span><Icone nome={espaco.icone} /></span>
                <div><strong>{espaco.nome}</strong></div>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section className="login-gateway__console" aria-labelledby="login-acesso-titulo">
        <header className="login-gateway__console-head">
          <span><Icone nome="conta" /></span>
          <div><p>IDENTIDADE PROFISSIONAL</p><h2 id="login-acesso-titulo">Entre no CorVIA</h2><small>Seu universo profissional em um só lugar.</small></div>
        </header>

        <form className="login-gateway__form" onSubmit={enviar}>
          <label className="login-gateway__field" htmlFor="email">
            <span>E-mail profissional</span>
            <div><Icone nome="mail" /><input id="email" type="email" inputMode="email" autoCapitalize="none" autoComplete="username" placeholder="seu@email.com" value={email} onChange={(event) => setEmail(event.target.value)} aria-invalid={Boolean(erro)} aria-describedby={erro ? "login-erro" : undefined} required /></div>
          </label>
          <label className="login-gateway__field" htmlFor="senha">
            <span>Senha</span>
            <div className="login-gateway__password"><Icone nome="cadeado" /><input id="senha" type={mostrarSenha ? "text" : "password"} autoComplete="current-password" placeholder="Digite sua senha" value={senha} onChange={(event) => setSenha(event.target.value)} aria-invalid={Boolean(erro)} aria-describedby={erro ? "login-erro" : undefined} required /><button type="button" onClick={() => setMostrarSenha((visivel) => !visivel)} aria-label={mostrarSenha ? "Ocultar senha" : "Mostrar senha"} aria-pressed={mostrarSenha}><Icone nome={mostrarSenha ? "olho-fechado" : "olho"} /></button></div>
          </label>
          <Link className="login-gateway__forgot" to="/esqueci-senha">Esqueceu sua senha?</Link>
          <button className="login-gateway__enter" type="submit" disabled={enviando}>
            <span>{enviando ? "Abrindo seus espaços…" : "Entrar"}</span>
            {!enviando ? <Icone nome="seta" /> : <i className="login-formulario__carregando" aria-hidden="true" />}
          </button>
          {erro && <p id="login-erro" className="login-gateway__error" role="alert">{erro}</p>}
        </form>

        <Link className="login-gateway__join" to="/solicitar-acesso">
          <span><Icone nome="conta" /></span>
          <span><strong>Novo no CorVIA?</strong><small>Solicite seu Acesso</small><em>Faça parte de um universo de conhecimento, prática e pessoas.</em></span>
          <Icone nome="seta" />
        </Link>
      </section>

      <footer className="login-gateway__footer">
        <div>CONTEÚDO · FERRAMENTAS · INTELIGÊNCIA ARTIFICIAL · CONECTIVIDADE · TUDO COM TUDO</div>
        <div><strong>CorVIA</strong><span>|</span>CARDIOLOGY SPACES<span>|</span>VERSÃO 2.0</div>
      </footer>
    </main>
  );
}
