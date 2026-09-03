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

function MarcaAndroid() {
  return (
    <svg viewBox="0 0 24 24" focusable="false" aria-hidden="true">
      <path fill="currentColor" d="m7.1 6.55-1.3-2.26a.5.5 0 0 1 .87-.5l1.32 2.3A8.1 8.1 0 0 1 12 5.05c1.45 0 2.82.38 4.01 1.04l1.32-2.3a.5.5 0 0 1 .87.5l-1.3 2.26A7.42 7.42 0 0 1 20 12H4a7.42 7.42 0 0 1 3.1-5.45ZM8 9.5a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Zm8 0A.75.75 0 1 0 16 8a.75.75 0 0 0 0 1.5ZM4 13h16v6a2 2 0 0 1-2 2h-1v1.25a.75.75 0 0 1-1.5 0V21h-7v1.25a.75.75 0 0 1-1.5 0V21H6a2 2 0 0 1-2-2v-6Z" />
    </svg>
  );
}

function MarcaWindows() {
  return (
    <svg viewBox="0 0 24 24" focusable="false" aria-hidden="true">
      <path fill="currentColor" d="M2 3.4 10.7 2v9.3H2V3.4Zm9.7-1.55L22 0v11.3H11.7V1.85ZM2 12.3h8.7v9.3L2 20.2v-7.9Zm9.7 0H22V24l-10.3-1.85V12.3Z" />
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
        <div className="login-gateway__security">
          <span><i /> Ambiente protegido</span>
          <small>Acesso profissional · LGPD</small>
        </div>
      </header>

      <section className="login-gateway__scene" aria-labelledby="login-title">
        <header className="login-gateway__hero">
          <p>CORVIA · CARDIOLOGY SPACES</p>
          <h1 id="login-title">Um universo de espaços. <strong>Uma só cardiologia.</strong></h1>
          <span>Consultório, Hospital, Ensino, Pesquisa e Gestão orbitam a mesma identidade clínica — com continuidade, confiança e contexto.</span>
        </header>

        <div className="login-gateway__universe" aria-hidden="true">
          <svg className="login-gateway__routes" viewBox="0 0 1200 390" preserveAspectRatio="none">
            <path d="M70 245C240 64 412 48 600 164C788 48 960 64 1130 245" />
            <path d="M64 273C252 143 430 133 600 218C770 133 948 143 1136 273" />
            <path d="M128 315C315 253 458 251 600 292C742 251 885 253 1072 315" />
          </svg>
          <div className="login-gateway__milky-way">
            <span />
          </div>
          <div className="login-gateway__core">
            <span className="login-gateway__core-glow" />
            <CoracaoHolografico />
            <svg className="login-gateway__pulse" viewBox="0 0 360 48">
              <path className="login-gateway__pulse-baseline" d="M2 29H358" />
              <path className="login-gateway__pulse-trace" d="M2 29H29C35 29 37 23 43 23S52 29 59 29H81L88 32L96 8L105 42L113 29H137C148 29 151 16 164 16S181 29 195 29H224C230 29 232 23 238 23S247 29 254 29H275L282 32L290 8L299 42L307 29H329C340 29 343 17 358 17" />
            </svg>
            <i className="login-gateway__ring login-gateway__ring--one" />
            <i className="login-gateway__ring login-gateway__ring--two" />
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
      </section>

      <footer className="login-gateway__footer">
        <div className="login-gateway__form-meta">
          <label htmlFor="permanecer"><input id="permanecer" type="checkbox" checked={permanecerConectado} onChange={(event) => setPermanecerConectado(event.target.checked)} />Manter este acesso</label>
          <Link to="/esqueci-senha">Esqueci minha senha</Link>
        </div>
        <div className="login-gateway__utilities">
          <a href="/downloads/corvia-cardiology-spaces-android-1.2.0.apk" download="CorVIA-Cardiology-Spaces-Android-1.2.0.apk"><span><MarcaAndroid /></span><strong>Android</strong><small>Baixar app</small><Icone nome="seta" /></a>
          <div role="status" aria-label="Aplicativo para Windows pendente de assinatura"><span><MarcaWindows /></span><strong>Windows</strong><small>Em breve</small></div>
          <Link to="/solicitar-acesso"><span><Icone nome="conta" /></span><strong>Novo no CorVIA?</strong><small>Solicitar acesso</small><Icone nome="seta" /></Link>
        </div>
        <nav aria-label="Links institucionais"><Link to="/privacidade">Privacidade</Link><Link to="/termos">Termos</Link><a href="mailto:contato@corvia.med.br">Suporte</a></nav>
      </footer>
    </main>
  );
}
