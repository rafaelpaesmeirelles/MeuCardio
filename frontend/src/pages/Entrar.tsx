import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import Icone from "../components/Icone";
import PreHomeBrand from "../components/PreHomeBrand";
import { useAuth } from "../lib/auth";
import "../styles/login.css";
import "../styles/login-fullscreen-social.css";
import "../styles/prehome-reference-final.css";
import "../styles/login-viewport-refinement.css";

const BENEFICIOS = [
  { icon: "assistente" as const, title: "Inteligência clínica", detail: "Contexto e apoio à decisão no mesmo ambiente.", tone: "cyan" as const },
  { icon: "evidencia" as const, title: "Evidências atualizadas", detail: "Guidelines, literatura e protocolos conectados.", tone: "violet" as const },
  { icon: "check" as const, title: "Segurança e privacidade", detail: "Acesso profissional protegido e rastreável.", tone: "green" as const },
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
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [mostrarSenha, setMostrarSenha] = useState(false);
  const [permanecerConectado, setPermanecerConectado] = useState(false);
  const [erro, setErro] = useState("");
  const [enviando, setEnviando] = useState(false);
  async function enviar(event?: FormEvent<HTMLFormElement>) {
    event?.preventDefault();
    if (enviando || !email.trim() || !senha) return;
    setEnviando(true);
    setErro("");
    try {
      await entrar(email.trim().toLowerCase(), senha, permanecerConectado);
    } catch (e) {
      setErro(e instanceof Error ? e.message : "Não foi possível entrar.");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <main className="login prehome prehome--login prehome--fullscreen">
      <PreHomeBrand
        title={<>Tudo o que o cardiologista precisa. <strong>Em um só lugar.</strong></>}
        description={<>Seus ambientes de cardiologia conectam conhecimento, decisão, assistência e rotina sem tirar o médico do centro.</>}
        benefits={BENEFICIOS}
      />
      <section className="prehome-access" aria-labelledby="login-acesso-titulo">
        <div className="prehome-card prehome-card--login">
          <header className="prehome-card__header">
            <p className="prehome-card__eyebrow"><Icone nome="conta" /> Acesso profissional</p>
            <h2 id="login-acesso-titulo">Bem-vindo de volta</h2>
            <p>Acesse sua conta para continuar no CorVIA Cardiology Spaces.</p>
          </header>
          <form className="login-formulario" onSubmit={enviar}>
            <div className="login-campo">
              <label htmlFor="email">E-mail</label>
              <input id="email" type="email" inputMode="email" autoCapitalize="none" autoComplete="username" placeholder="seu@email.com" value={email} onChange={(event) => setEmail(event.target.value)} aria-invalid={Boolean(erro)} aria-describedby={erro ? "login-erro" : undefined} required autoFocus />
            </div>
            <div className="login-campo">
              <label htmlFor="senha">Senha</label>
              <div className="login-senha">
                <input id="senha" type={mostrarSenha ? "text" : "password"} autoComplete="current-password" placeholder="Digite sua senha" value={senha} onChange={(event) => setSenha(event.target.value)} aria-invalid={Boolean(erro)} aria-describedby={erro ? "login-erro" : undefined} required />
                <button type="button" onClick={() => setMostrarSenha((visivel) => !visivel)} aria-label={mostrarSenha ? "Ocultar senha" : "Mostrar senha"} aria-pressed={mostrarSenha}>
                  <Icone nome={mostrarSenha ? "olho-fechado" : "olho"} />
                </button>
              </div>
            </div>
            <div className="prehome-card__inline-actions">
              <label htmlFor="permanecer"><input id="permanecer" type="checkbox" checked={permanecerConectado} onChange={(event) => setPermanecerConectado(event.target.checked)} />Lembrar-me</label>
              <Link to="/esqueci-senha" className="prehome-link">Esqueci minha senha</Link>
            </div>
            {erro && <p id="login-erro" className="login-formulario__erro" role="alert">{erro}</p>}
            <button className="login-formulario__entrar" type="submit" disabled={enviando || !email.trim() || !senha}>
              <span>{enviando ? "Abrindo seus Cardiology Spaces…" : "Entrar na minha conta"}</span>{!enviando && <Icone nome="seta" aria-hidden="true" />}{enviando && <i className="login-formulario__carregando" aria-hidden="true" />}
            </button>
          </form>
          <div className="prehome-card__actions">
            <a
              className="prehome-android-download"
              href="/downloads/corvia-cardiology-spaces-android-1.1.0.apk"
              download="CorVIA-Cardiology-Spaces-Android-1.1.0.apk"
            >
              <span className="prehome-android-download__icon"><MarcaAndroid /></span>
              <span><strong>Baixar app para Android</strong><small>Versão 1.1.0 · APK assinado</small></span>
              <Icone nome="seta" aria-hidden="true" />
            </a>
            <a
              className="prehome-windows-download"
              href="/downloads/corvia-os-windows.exe"
              download="CorVIA-Cardiology-Spaces-Windows-Setup.exe"
              aria-label="Baixar instalador do CorVIA Cardiology Spaces para Windows 10 ou 11"
            >
              <span className="prehome-windows-download__icon"><MarcaWindows /></span>
              <span><strong>Baixar instalador para Windows</strong><small>Arquivo .EXE · Windows 10/11</small></span>
              <Icone nome="seta" aria-hidden="true" />
            </a>
            <Link to="/solicitar-acesso" className="prehome-secondary"><Icone nome="conta" /> Solicitar acesso</Link>
          </div>
          <footer className="prehome-card__footer"><Icone nome="check" /><span>Seus dados estão protegidos · ambiente profissional em conformidade com a LGPD</span></footer>
        </div>
        <nav className="prehome-legal" aria-label="Links institucionais"><Link to="/privacidade">Privacidade</Link><Link to="/termos">Termos</Link><a href="mailto:contato@corvia.med.br">Suporte</a></nav>
      </section>
    </main>
  );
}
