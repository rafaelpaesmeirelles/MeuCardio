import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import GrafoConstelacao from "../components/GrafoConstelacao";
import Icone from "../components/Icone";
import { useAuth } from "../lib/auth";
import "../styles/login.css";

const BENEFICIOS = [
  "Pesquisa, conhecimento, decisão e ação no mesmo workspace",
  "Contexto clínico conectado sem transformar tudo em chatbot",
  "Paciente, agenda, documentos e comunicação dentro do mesmo Clinical OS",
];

export default function Entrar() {
  const { entrar } = useAuth();
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [mostrarSenha, setMostrarSenha] = useState(false);
  // Desmarcado por padrão: a plataforma é usada também em computadores de
  // hospital e consultório compartilhados. Persistência longa exige gesto
  // explícito do profissional em seu próprio dispositivo.
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
    <main className="login login--entrar">
      <section className="login-vitrine" aria-labelledby="login-vitrine-titulo">
        <div className="login-vitrine__luz login-vitrine__luz--um" aria-hidden="true" />
        <div className="login-vitrine__luz login-vitrine__luz--dois" aria-hidden="true" />

        <Link to="/" className="login-vitrine__marca" aria-label="CorVIA — página inicial">
          <img src="/corvia-logo.png" alt="CorVIA" />
          <small>Clinical OS do médico</small>
        </Link>

        <div className="login-vitrine__conteudo">
          <h1 id="login-vitrine-titulo">
            Comece pelo que você
            <br />
            <em>precisa resolver agora.</em>
          </h1>
          <p className="login-vitrine__descricao">
            Conhecimento, contexto, paciente, decisão e ação conectados em um único
            workspace construído para o trabalho médico.
          </p>

          <GrafoConstelacao variante="escuro" className="login-vitrine__grafo" />

          <ul className="login-vitrine__beneficios">
            {BENEFICIOS.map((texto) => (
              <li key={texto}>
                <Icone nome="check" aria-hidden="true" />
                {texto}
              </li>
            ))}
          </ul>
        </div>

        <footer className="login-vitrine__rodape">
          <span>CorVIA — Clinical OS do médico</span>
          <span>Uso exclusivo de profissionais autorizados</span>
        </footer>
      </section>

      <section className="login-acesso" aria-labelledby="login-acesso-titulo">
        <div className="login-acesso__topo">
          <Link to="/" aria-label="CorVIA — início">
            <img src="/corvia-logo-compacta.png" alt="CorVIA" />
          </Link>
          <Link to="/produto#acesso" className="login-acesso__conhecer">
            <span className="login-acesso__conhecer-longo">Conhecer o Clinical OS</span>
            <span className="login-acesso__conhecer-curto">Conhecer</span>
            <Icone nome="seta" aria-hidden="true" />
          </Link>
        </div>

        <div className="login-acesso__conteudo">
          <div className="login-marca-mobile">
            <small>Clinical OS do médico</small>
            <h1>
              O que você precisa <strong>resolver agora?</strong>
            </h1>
            <svg className="login-marca-mobile__pulso" viewBox="0 0 320 22" aria-hidden="true">
              <path d="M0 11h104l11-8 12 16 11-12 9 9 8-5h165" />
            </svg>
          </div>

          <div className="login-acesso__introducao">
            <p className="eyebrow">Acesso profissional</p>
            <h2 id="login-acesso-titulo">Bem-vindo de volta.</h2>
            <p>Entre no seu Clinical Command Center.</p>
          </div>

          <form className="login-formulario" onSubmit={enviar}>
            <div className="login-campo">
              <label htmlFor="email">E-mail profissional</label>
              <input
                id="email"
                type="email"
                inputMode="email"
                autoCapitalize="none"
                autoComplete="username"
                placeholder="nome@exemplo.com.br"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                aria-invalid={Boolean(erro)}
                aria-describedby={erro ? "login-erro" : undefined}
                required
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
                  {mostrarSenha ? "Ocultar" : "Mostrar"}
                </button>
              </div>
              <Link to="/esqueci-senha" className="login-campo__esqueci">Esqueci minha senha</Link>
            </div>

            <div className="login-permanecer">
              <input
                id="permanecer"
                type="checkbox"
                checked={permanecerConectado}
                onChange={(event) => setPermanecerConectado(event.target.checked)}
                aria-describedby="permanecer-ajuda"
              />
              <div>
                <label htmlFor="permanecer">Manter conectado neste dispositivo</label>
                <p id="permanecer-ajuda">
                  Use apenas em aparelho pessoal. Em computador compartilhado do hospital ou
                  do consultório, deixe desmarcado.
                </p>
              </div>
            </div>

            {erro && <p id="login-erro" className="login-formulario__erro" role="alert">{erro}</p>}

            <button className="login-formulario__entrar" type="submit" disabled={enviando || !email.trim() || !senha}>
              <span>{enviando ? "Abrindo seu Clinical OS…" : "Entrar no CorVIA"}</span>
              {!enviando && <Icone nome="seta" aria-hidden="true" />}
              {enviando && <i className="login-formulario__carregando" aria-hidden="true" />}
            </button>
          </form>

          <div className="login-acesso__novo">
            <span>Primeiro acesso ao CorVIA?</span>
            <Link to="/solicitar-acesso">Solicitar acesso profissional <Icone nome="seta" aria-hidden="true" /></Link>
          </div>

          <p className="login-acesso__seguranca">
            <Icone nome="check" aria-hidden="true" /> Acesso pessoal e restrito a profissionais autorizados.
          </p>
        </div>

        <footer className="login-acesso__rodape">
          <span>© {new Date().getFullYear()} CorVIA</span>
          <nav aria-label="Links institucionais">
            <Link to="/privacidade">Privacidade</Link>
            <Link to="/termos">Termos</Link>
            <a href="mailto:contato@corvia.med.br">Suporte</a>
          </nav>
        </footer>
      </section>
    </main>
  );
}
