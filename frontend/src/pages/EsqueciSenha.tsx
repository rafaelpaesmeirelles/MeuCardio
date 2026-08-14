import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import Icone from "../components/Icone";
import GrafoConstelacao from "../components/GrafoConstelacao";
import "../styles/login.css";

export default function EsqueciSenha() {
  const [email, setEmail] = useState("");
  const [enviado, setEnviado] = useState(false);
  const [enviando, setEnviando] = useState(false);

  async function enviar(event?: FormEvent<HTMLFormElement>) {
    event?.preventDefault();
    if (!email.includes("@") || enviando) return;
    setEnviando(true);
    try {
      await api.post("/auth/esqueci-senha", { email: email.trim().toLowerCase() });
    } finally {
      setEnviando(false);
      setEnviado(true); // resposta uniforme: não revela se a conta existe
    }
  }

  return (
    <main className="login login--recovery">
      <section className="login-vitrine" aria-labelledby="recovery-vitrine-titulo">
        <div className="login-vitrine__luz login-vitrine__luz--um" aria-hidden="true" />
        <div className="login-vitrine__luz login-vitrine__luz--dois" aria-hidden="true" />
        <Link to="/" className="login-vitrine__marca" aria-label="CorVIA — página inicial">
          <img src="/corvia-logo.png" alt="CorVIA" />
          <small>Clinical OS do médico</small>
        </Link>
        <div className="login-vitrine__conteudo">
          <h1 id="recovery-vitrine-titulo">Recupere o acesso.<br /><em>Sem depender da caixa CorVIA.</em></h1>
          <p className="login-vitrine__descricao">
            O segundo e-mail existe justamente para continuar acessível quando o login ou o CorVIA Mail não estiverem disponíveis.
          </p>
          <GrafoConstelacao variante="escuro" className="login-vitrine__grafo" />
          <ul className="login-vitrine__beneficios">
            <li><Icone nome="check" aria-hidden="true" />Link de redefinição de uso único</li>
            <li><Icone nome="check" aria-hidden="true" />Entrega no canal externo cadastrado</li>
            <li><Icone nome="check" aria-hidden="true" />Senha nunca enviada por e-mail</li>
          </ul>
        </div>
        <footer className="login-vitrine__rodape"><span>CorVIA — Clinical OS do médico</span><span>Acesso protegido</span></footer>
      </section>

      <section className="login-acesso" aria-labelledby="recovery-titulo">
        <div className="login-acesso__topo">
          <Link to="/" aria-label="CorVIA — início"><img src="/corvia-logo-compacta.png" alt="CorVIA" /></Link>
          <Link to="/entrar" className="login-acesso__conhecer"><span>Voltar ao login</span><Icone nome="seta" aria-hidden="true" /></Link>
        </div>

        <div className="login-acesso__conteudo">
          <div className="login-acesso__introducao">
            <p className="eyebrow">Segurança da conta</p>
            <h2 id="recovery-titulo">Redefinir sua senha.</h2>
            <p>Informe o e-mail de login ou o segundo e-mail de recuperação cadastrado.</p>
          </div>

          {enviado ? (
            <div className="login-confirmacao">
              <div className="login-confirmacao__selo"><Icone nome="check" aria-hidden="true" width={24} height={24} /></div>
              <h2>Confira seu canal de recuperação</h2>
              <p>
                Se o endereço estiver vinculado a uma conta ativa, enviamos um link de redefinição ao canal seguro cadastrado. O link vale por 1 hora.
              </p>
              <p className="login-formulario__secao-nota">
                Não recebeu? Verifique spam/lixo eletrônico. Se continuar sem chegar, contate contato@corvia.med.br.
              </p>
              <Link to="/entrar" className="login-formulario__entrar" style={{ width: "fit-content" }}><span>Voltar ao login</span><Icone nome="seta" /></Link>
            </div>
          ) : (
            <form className="login-formulario" onSubmit={enviar}>
              <div className="login-formulario__secao">
                <div className="login-campo">
                  <label htmlFor="email">E-mail de login ou recuperação</label>
                  <input id="email" type="email" autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="nome@exemplo.com" required autoFocus />
                </div>
              </div>
              <button className="login-formulario__entrar" type="submit" disabled={!email.includes("@") || enviando}>
                <span>{enviando ? "Solicitando…" : "Enviar link de redefinição"}</span>
                {!enviando && <Icone nome="seta" aria-hidden="true" />}
                {enviando && <i className="login-formulario__carregando" aria-hidden="true" />}
              </button>
            </form>
          )}

          <p className="login-acesso__seguranca"><Icone nome="check" aria-hidden="true" /> A resposta é deliberadamente igual para endereços existentes e inexistentes.</p>
        </div>

        <footer className="login-acesso__rodape">
          <span>© {new Date().getFullYear()} CorVIA</span>
          <nav aria-label="Links institucionais"><Link to="/privacidade">Privacidade</Link><Link to="/termos">Termos</Link><a href="mailto:contato@corvia.med.br">Suporte</a></nav>
        </footer>
      </section>
    </main>
  );
}
