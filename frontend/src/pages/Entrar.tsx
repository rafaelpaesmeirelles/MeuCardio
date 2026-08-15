import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import Icone from "../components/Icone";
import PreHomeBrand from "../components/PreHomeBrand";
import { useAuth } from "../lib/auth";
import "../styles/login.css";

const BENEFICIOS = [
  { icon: "assistente" as const, title: "Inteligência clínica", detail: "Contexto e apoio à decisão no mesmo ambiente.", tone: "cyan" as const },
  { icon: "evidencia" as const, title: "Evidências atualizadas", detail: "Guidelines, literatura e protocolos conectados.", tone: "violet" as const },
  { icon: "check" as const, title: "Segurança e privacidade", detail: "Acesso profissional protegido e rastreável.", tone: "green" as const },
];

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
    <main className="login prehome prehome--login">
      <PreHomeBrand
        title={<>Tudo o que o cardiologista precisa. <strong>Em um só lugar.</strong></>}
        description={<>Seu Clinical OS conecta conhecimento, decisão, assistência e rotina sem tirar o médico do centro.</>}
        benefits={BENEFICIOS}
      />
      <section className="prehome-access" aria-labelledby="login-acesso-titulo">
        <div className="prehome-card prehome-card--login">
          <header className="prehome-card__header">
            <p className="prehome-card__eyebrow"><Icone nome="conta" /> Acesso profissional</p>
            <h2 id="login-acesso-titulo">Bem-vindo de volta</h2>
            <p>Acesse sua conta para continuar no CorVIA Clinical OS.</p>
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
              <span>{enviando ? "Abrindo seu Clinical OS…" : "Entrar na minha conta"}</span>{!enviando && <Icone nome="seta" aria-hidden="true" />}{enviando && <i className="login-formulario__carregando" aria-hidden="true" />}
            </button>
          </form>
          <div className="prehome-card__actions">
            <div className="prehome-divider">ou continue com</div>
            <Link to="/solicitar-acesso" className="prehome-secondary"><Icone nome="conta" /> Solicitar acesso</Link>
          </div>
          <footer className="prehome-card__footer"><Icone nome="check" /><span>Seus dados estão protegidos · ambiente profissional em conformidade com a LGPD</span></footer>
        </div>
        <nav className="prehome-legal" aria-label="Links institucionais"><Link to="/privacidade">Privacidade</Link><Link to="/termos">Termos</Link><a href="mailto:contato@corvia.med.br">Suporte</a></nav>
      </section>
    </main>
  );
}
