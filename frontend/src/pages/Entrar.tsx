import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import Icone, { type NomeIcone } from "../components/Icone";
import { useAuth } from "../lib/auth";
import "../styles/login.css";

const FLUXO: Array<{ icone: NomeIcone; titulo: string; texto: string }> = [
  { icone: "evidencia", titulo: "Evidência", texto: "Fontes clínicas identificadas" },
  { icone: "assistente", titulo: "Decisão", texto: "Contexto no momento da dúvida" },
  { icone: "prescricao", titulo: "Continuidade", texto: "Da conduta à rotina do paciente" },
];

export default function Entrar() {
  const { entrar } = useAuth();
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [mostrarSenha, setMostrarSenha] = useState(false);
  const [erro, setErro] = useState("");
  const [enviando, setEnviando] = useState(false);

  async function enviar(event?: FormEvent<HTMLFormElement>) {
    event?.preventDefault();
    if (enviando || !email.trim() || !senha) return;
    setEnviando(true);
    setErro("");
    try {
      await entrar(email.trim().toLowerCase(), senha);
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

        <Link to="/" className="login-vitrine__marca" aria-label="Corvia — página inicial">
          <img src="/corvia-logo.png" alt="Corvia — O caminho do coração" />
          <span><small>Ecossistema Clínico Cardiológico</small></span>
        </Link>

        <div className="login-vitrine__conteudo">
          <p className="login-vitrine__selo"><span /> Cardiologia conectada à prática</p>
          <h1 id="login-vitrine-titulo">Toda a jornada clínica.<br /><em>Um só fluxo.</em></h1>
          <p className="login-vitrine__descricao">
            Conhecimento, decisão, prescrição, organização e comunicação trabalhando
            juntos para manter o médico próximo do que realmente importa.
          </p>

          <div className="login-vitrine__fluxo" aria-label="Fluxo clínico integrado">
            {FLUXO.map((etapa, indice) => (
              <article key={etapa.titulo}>
                <span className="login-vitrine__numero">0{indice + 1}</span>
                <span className="login-vitrine__icone"><Icone nome={etapa.icone} /></span>
                <div><strong>{etapa.titulo}</strong><small>{etapa.texto}</small></div>
              </article>
            ))}
          </div>

          <div className="login-vitrine__contexto">
            <div>
              <span className="login-vitrine__pulso"><i /><i /><i /></span>
              <p><small>Workspace clínico</small><strong>Do primeiro questionamento à continuidade do cuidado.</strong></p>
            </div>
            <div className="login-vitrine__modulos" aria-label="Recursos integrados">
              <span>Assistente clínico</span><span>Agenda inteligente</span><span>Prescrição</span><span>Corvia Mail</span>
            </div>
          </div>
        </div>

        <footer className="login-vitrine__rodape">
          <span>Corvia — O caminho do coração</span>
          <span>Uso exclusivo de profissionais autorizados</span>
        </footer>
      </section>

      <section className="login-acesso" aria-labelledby="login-acesso-titulo">
        <div className="login-acesso__topo">
          <Link to="/" aria-label="Corvia — início"><img src="/corvia-logo-compacta.png" alt="Corvia" /></Link>
          <Link to="/produto#acesso">Conhecer a plataforma <Icone nome="seta" /></Link>
        </div>

        <div className="login-acesso__conteudo">
          <div className="login-acesso__introducao">
            <p className="eyebrow">Acesso profissional</p>
            <h2 id="login-acesso-titulo">Bem-vindo de volta.</h2>
            <p>Entre no seu espaço de trabalho clínico.</p>
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
              <div className="login-campo__cabecalho">
                <label htmlFor="senha">Senha</label>
                <Link to="/esqueci-senha">Esqueci minha senha</Link>
              </div>
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
            </div>

            {erro && <p id="login-erro" className="login-formulario__erro" role="alert">{erro}</p>}

            <button className="login-formulario__entrar" type="submit" disabled={enviando || !email.trim() || !senha}>
              <span>{enviando ? "Abrindo seu espaço…" : "Entrar na Corvia"}</span>
              {!enviando && <Icone nome="seta" />}
              {enviando && <i className="login-formulario__carregando" aria-hidden="true" />}
            </button>
          </form>

          <div className="login-acesso__novo">
            <span>Primeiro acesso à Corvia?</span>
            <Link to="/solicitar-acesso">Solicitar acesso profissional <Icone nome="seta" /></Link>
          </div>

          <p className="login-acesso__seguranca"><Icone nome="check" /> Acesso pessoal e restrito a profissionais autorizados.</p>
        </div>

        <footer className="login-acesso__rodape">
          <span>© {new Date().getFullYear()} Corvia</span>
          <nav aria-label="Links institucionais"><Link to="/privacidade">Privacidade</Link><Link to="/termos">Termos</Link><a href="mailto:contato@corvia.med.br">Suporte</a></nav>
        </footer>
      </section>
    </main>
  );
}
