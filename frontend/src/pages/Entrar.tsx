import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import Icone from "../components/Icone";
import PreHomeBrand from "../components/PreHomeBrand";
import { useAuth } from "../lib/auth";
import "../styles/login.css";
import "../styles/prehome-canonical.css";

const BENEFICIOS = [
  {
    icon: "check" as const,
    title: "Segurança e privacidade",
    detail: "Acesso profissional protegido, com privacidade e rastreabilidade.",
    tone: "cyan" as const,
  },
  {
    icon: "conhecimento" as const,
    title: "Evidências atualizadas",
    detail: "Guidelines, literatura e protocolos integrados ao seu fluxo de decisão.",
    tone: "violet" as const,
  },
  {
    icon: "assistente" as const,
    title: "Produtividade clínica",
    detail: "Ferramentas inteligentes para reduzir tarefas e apoiar o melhor cuidado.",
    tone: "green" as const,
  },
];

export default function Entrar() {
  const { entrar } = useAuth();
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [mostrarSenha, setMostrarSenha] = useState(false);
  // Desmarcado por padrão: a plataforma também é usada em computadores
  // compartilhados de hospital/consultório. Persistência longa exige gesto.
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
        <div className="prehome-card">
          <header className="prehome-card__header">
            <p className="prehome-card__eyebrow"><Icone nome="conta" /> Acesso profissional</p>
            <h2 id="login-acesso-titulo">Entrar no CorVIA</h2>
            <p>Use suas credenciais para acessar o seu Command Center clínico.</p>
          </header>

          <form className="login-formulario" onSubmit={enviar}>
            <div className="login-campo">
              <label htmlFor="email">E-mail</label>
              <input
                id="email"
                type="email"
                inputMode="email"
                autoCapitalize="none"
                autoComplete="username"
                placeholder="seu@email.com"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                aria-invalid={Boolean(erro)}
                aria-describedby={erro ? "login-erro" : undefined}
                required
                autoFocus
              />
            </div>

            <div className="login-campo">
              <label htmlFor="senha">Senha</label>
              <div className="login-senha">
                <input
                  id="senha"
                  type={mostrarSenha ? "text" : "password"}
                  autoComplete="current-password"
                  placeholder="Digite sua senha"
                  value={senha}
                  onChange={(event) => setSenha(event.target.value)}
                  aria-invalid={Boolean(erro)}
                  aria-describedby={erro ? "login-erro" : undefined}
                  required
                />
                <button
                  type="button"
                  onClick={() => setMostrarSenha((visivel) => !visivel)}
                  aria-label={mostrarSenha ? "Ocultar senha" : "Mostrar senha"}
                  aria-pressed={mostrarSenha}
                >
                  <Icone nome={mostrarSenha ? "olho-fechado" : "olho"} />
                </button>
              </div>
            </div>

            <div className="prehome-card__inline-actions">
              <label htmlFor="permanecer">
                <input
                  id="permanecer"
                  type="checkbox"
                  checked={permanecerConectado}
                  onChange={(event) => setPermanecerConectado(event.target.checked)}
                />
                Manter conectado
              </label>
              <Link to="/esqueci-senha" className="prehome-link">Esqueci minha senha</Link>
            </div>

            {erro && <p id="login-erro" className="login-formulario__erro" role="alert">{erro}</p>}

            <button className="login-formulario__entrar" type="submit" disabled={enviando || !email.trim() || !senha}>
              <span>{enviando ? "Abrindo seu Clinical OS…" : "Entrar"}</span>
              {!enviando && <Icone nome="seta" aria-hidden="true" />}
              {enviando && <i className="login-formulario__carregando" aria-hidden="true" />}
            </button>
          </form>

          <div className="prehome-card__actions">
            <div className="prehome-divider">ou</div>
            <Link to="/solicitar-acesso" className="prehome-secondary">
              <Icone nome="conta" /> Primeiro acesso ou cadastro
            </Link>
          </div>

          <footer className="prehome-card__footer">
            <Icone nome="check" />
            <span>Ambiente seguro para uso profissional · pressione Enter para entrar</span>
          </footer>
        </div>

        <nav className="prehome-legal" aria-label="Links institucionais">
          <Link to="/privacidade">Privacidade</Link>
          <Link to="/termos">Termos</Link>
          <a href="mailto:contato@corvia.med.br">Suporte</a>
        </nav>
      </section>
    </main>
  );
}
