import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import Icone from "../components/Icone";
import PreHomeBrand from "../components/PreHomeBrand";
import { useAuth } from "../lib/auth";
import "../styles/login.css";

const BENEFICIOS = [
  { icon: "check" as const, title: "Segurança e privacidade", detail: "Acesso profissional protegido, com privacidade e rastreabilidade.", tone: "cyan" as const },
  { icon: "conhecimento" as const, title: "Evidências atualizadas", detail: "Guidelines, literatura e protocolos integrados ao seu fluxo de decisão.", tone: "violet" as const },
  { icon: "assistente" as const, title: "Produtividade clínica", detail: "Ferramentas inteligentes para reduzir tarefas e apoiar o melhor cuidado.", tone: "green" as const },
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
        title={<>Entre no <strong>CorVIA</strong></>}
        description={<>Acesse o Clinical Command Center completo e tome decisões com mais segurança, evidência e eficiência.</>}
        benefits={BENEFICIOS}
      />

      <section className="prehome-access" aria-labelledby="login-acesso-titulo">
        <div className="prehome-access__identity" aria-label="CorVIA Clinical OS">
          <img src="/corvia-logo.png" alt="CorVIA" />
          <p>Tudo o que o cardiologista precisa.<br />Em um só lugar.</p>
        </div>

        <div className="prehome-card prehome-card--login">
          <header className="prehome-card__header">
            <h2 id="login-acesso-titulo">Bem-vindo de volta</h2>
            <p>Acesse sua conta para continuar</p>
          </header>

          <form className="login-formulario" onSubmit={enviar}>
            <div className="login-campo">
              <label htmlFor="email">E-mail</label>
              <div className="login-field-icon">
                <Icone nome="mail" aria-hidden="true" />
                <input id="email" type="email" inputMode="email" autoCapitalize="none" autoComplete="username" placeholder="seu@email.com" value={email} onChange={(event) => setEmail(event.target.value)} aria-invalid={Boolean(erro)} aria-describedby={erro ? "login-erro" : undefined} required autoFocus />
              </div>
            </div>

            <div className="login-campo">
              <label htmlFor="senha">Senha</label>
              <div className="login-senha login-field-icon">
                <Icone nome="check" aria-hidden="true" />
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
              <span>{enviando ? "Abrindo seu Clinical OS…" : "Entrar na minha conta"}</span>
              {!enviando && <Icone nome="seta" aria-hidden="true" />}
              {enviando && <i className="login-formulario__carregando" aria-hidden="true" />}
            </button>
          </form>

          <div className="prehome-card__actions">
            <div className="prehome-divider">ou continue com</div>
            <div className="prehome-security-option" aria-label="Proteção da conta">
              <Icone nome="check" />
              <span><strong>Acesso protegido</strong><small>Sessão segura, rastreável e protegida.</small></span>
            </div>
            <Link to="/solicitar-acesso" className="prehome-secondary prehome-secondary--request">
              <Icone nome="conta" />
              <span><strong>Solicitar acesso</strong><small>Ainda não tem uma conta? Solicite aqui</small></span>
              <Icone nome="seta" />
            </Link>
          </div>

          <footer className="prehome-card__footer"><Icone nome="check" /><span><strong>Seus dados estão protegidos</strong><small>Criptografia em trânsito e repouso, com conformidade LGPD.</small></span></footer>
        </div>

        <footer className="prehome-access__copyright">© 2026 CorVIA Clinical OS. Todos os direitos reservados.</footer>
      </section>
    </main>
  );
}
