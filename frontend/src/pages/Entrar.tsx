import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import GrafoConstelacao from "../components/GrafoConstelacao";
import Icone from "../components/Icone";
import { useAuth } from "../lib/auth";
import "../styles/login.css";

/** Tela de entrada da Corvia (issue #52 — subfase de UX de login/onboarding).
 *
 * Estrutura: split screen preservado. A metade esquerda (vitrine) foi
 * deliberadamente ALIVIADA — antes acumulava selo, headline gigante,
 * descrição, três cartões numerados, painel de workspace com pulso, chips de
 * módulos e rodapé ao mesmo tempo. Agora tem um bloco por finalidade: marca,
 * headline, descrição curta, UMA demonstração (o grafo de conhecimento, que
 * é a ideia central do produto) e três benefícios de uma linha.
 *
 * Abaixo de 900px a vitrine some (é densa demais para caber), mas a
 * identidade NÃO some junto: entra `.login-marca-mobile`, um bloco compacto
 * de ~120px com logo, headline curta e o traçado de pulso — identidade sem
 * virar landing page vertical.
 *
 * Nada aqui altera a mecânica de sessão: `entrar()` continua sendo o mesmo
 * `POST /auth/sessao` com `credentials: "include"` de `lib/auth.tsx`. */

const BENEFICIOS = [
  "Busca, evidência e conduta no mesmo lugar",
  "Cada item conectado ao resto do ecossistema",
  "Prescrição, agenda e comunicação integradas",
];

export default function Entrar() {
  const { entrar } = useAuth();
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [mostrarSenha, setMostrarSenha] = useState(false);
  // Padrão DESMARCADO, de propósito: a Corvia é usada em computador de
  // hospital, posto de enfermagem e consultório compartilhado, onde uma
  // sessão de 30 dias herdada pelo próximo usuário é risco real. Quem está
  // no aparelho pessoal marca em um clique. Isto muda só o valor inicial
  // enviado ao servidor — nenhuma regra de sessão, cookie ou expiração foi
  // tocada.
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

        <Link to="/" className="login-vitrine__marca" aria-label="Corvia — página inicial">
          <img src="/corvia-logo.png" alt="Corvia — O caminho do coração" />
          <small>Ecossistema Clínico Cardiológico</small>
        </Link>

        <div className="login-vitrine__conteudo">
          <h1 id="login-vitrine-titulo">
            Cardiologia conectada.
            <br />
            <em>Do conhecimento à decisão.</em>
          </h1>
          <p className="login-vitrine__descricao">
            Um só ambiente clínico, onde cada medicamento, evidência, exame e conduta
            aponta para tudo o que a Corvia sabe sobre o assunto.
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
          <span>Corvia — O caminho do coração</span>
          <span>Uso exclusivo de profissionais autorizados</span>
        </footer>
      </section>

      <section className="login-acesso" aria-labelledby="login-acesso-titulo">
        <div className="login-acesso__topo">
          <Link to="/" aria-label="Corvia — início">
            <img src="/corvia-logo-compacta.png" alt="Corvia" />
          </Link>
          {/* Dois rótulos, um por faixa de largura: em tela estreita o botão
              encolhe para "Conhecer" — nunca para uma seta sem contexto. */}
          <Link to="/produto#acesso" className="login-acesso__conhecer">
            <span className="login-acesso__conhecer-longo">Conhecer a plataforma</span>
            <span className="login-acesso__conhecer-curto">Conhecer</span>
            <Icone nome="seta" aria-hidden="true" />
          </Link>
        </div>

        <div className="login-acesso__conteudo">
          {/* Identidade compacta do mobile — invisível no desktop, onde a
              vitrine já cumpre esse papel. */}
          {/* Sem repetir a logo: ela já está no topo da própria tela. Aqui
              entram só a assinatura da marca e a mensagem central.
              É um <h1> de propósito, e não decoração com aria-hidden: abaixo
              de 900px a vitrine inteira (com o h1 do desktop) sai do ar por
              `display: none` e some também da árvore de acessibilidade — sem
              este título a tela mobile ficaria sem nenhum h1, começando a
              hierarquia no h2. Exatamente um dos dois é exposto por vez. */}
          <div className="login-marca-mobile">
            <small>Ecossistema Clínico Cardiológico</small>
            <h1>
              Cardiologia conectada. <strong>Do conhecimento à decisão.</strong>
            </h1>
            <svg className="login-marca-mobile__pulso" viewBox="0 0 320 22" aria-hidden="true">
              <path d="M0 11h104l11-8 12 16 11-12 9 9 8-5h165" />
            </svg>
          </div>

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

            {/* "Esqueci minha senha" vem DEPOIS do campo, no DOM e na tela:
                antes ficava no cabeçalho do campo e, no teclado, o Tab saía do
                e-mail direto para o link — o médico passava por cima do campo
                de senha. Ordem visual e ordem de foco coincidem aqui. */}
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
              <Link to="/esqueci-senha" className="login-campo__esqueci">
                Esqueci minha senha
              </Link>
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

            {erro && (
              <p id="login-erro" className="login-formulario__erro" role="alert">
                {erro}
              </p>
            )}

            <button
              className="login-formulario__entrar"
              type="submit"
              disabled={enviando || !email.trim() || !senha}
            >
              <span>{enviando ? "Abrindo seu espaço…" : "Entrar na Corvia"}</span>
              {!enviando && <Icone nome="seta" aria-hidden="true" />}
              {enviando && <i className="login-formulario__carregando" aria-hidden="true" />}
            </button>
          </form>

          <div className="login-acesso__novo">
            <span>Primeiro acesso à Corvia?</span>
            <Link to="/solicitar-acesso">
              Solicitar acesso profissional <Icone nome="seta" aria-hidden="true" />
            </Link>
          </div>

          <p className="login-acesso__seguranca">
            <Icone nome="check" aria-hidden="true" /> Acesso pessoal e restrito a profissionais
            autorizados.
          </p>
        </div>

        <footer className="login-acesso__rodape">
          <span>© {new Date().getFullYear()} Corvia</span>
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
