import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { api, ApiError } from "../lib/api";
import Icone from "../components/Icone";
import GrafoConstelacao from "../components/GrafoConstelacao";
import CampoSenha from "../components/CampoSenha";
import "../styles/login.css";

export default function RedefinirSenha() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const token = params.get("token") ?? "";
  const alvo = params.get("alvo") === "email" ? "email" : "conta";
  const [senha, setSenha] = useState("");
  const [confirmacao, setConfirmacao] = useState("");
  const [erro, setErro] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [feito, setFeito] = useState(false);

  const senhasBatem = senha.length > 0 && senha === confirmacao;

  async function enviar() {
    setErro("");
    setEnviando(true);
    try {
      await api.post("/auth/redefinir-senha", { token, nova_senha: senha });
      setFeito(true);
      const destino = alvo === "email" ? "/corvia-mail" : "/entrar";
      setTimeout(() => navigate(destino), 2500);
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível redefinir a senha.");
    } finally {
      setEnviando(false);
    }
  }

  const conteudo = !token ? (
    <div className="login-confirmacao">
      <div className="login-confirmacao__selo login-confirmacao__selo--pendente"><Icone nome="emergencia" aria-hidden="true" width={24} height={24} /></div>
      <h2>Link inválido.</h2>
      <p>O token de redefinição não está presente. Solicite um novo link pelo canal seguro.</p>
      <Link to="/esqueci-senha" className="login-formulario__entrar" style={{ width: "fit-content" }}><span>Solicitar novo link</span><Icone nome="seta" /></Link>
    </div>
  ) : feito ? (
    <div className="login-confirmacao">
      <div className="login-confirmacao__selo"><Icone nome="check" aria-hidden="true" width={24} height={24} /></div>
      <h2>Senha atualizada.</h2>
      <p>Pronto. Você será levado para {alvo === "email" ? "o CorVIA Mail" : "o login"}.</p>
    </div>
  ) : (
    <form className="login-formulario" onSubmit={(e) => { e.preventDefault(); void enviar(); }}>
      <div className="login-formulario__secao">
        <div className="login-campo">
          <label htmlFor="senha">Nova senha</label>
          <CampoSenha id="senha" autoComplete="new-password" value={senha} onChange={(e) => setSenha(e.target.value)} autoFocus />
          {senha.length > 0 && senha.length < 8 && <p className="login-formulario__secao-nota" style={{ color: "#e8a1ab" }}>Mínimo 8 caracteres.</p>}
        </div>
        <div className="login-campo">
          <label htmlFor="confirmacao">Confirmar nova senha</label>
          <CampoSenha id="confirmacao" autoComplete="new-password" value={confirmacao} onChange={(e) => setConfirmacao(e.target.value)} />
          {confirmacao.length > 0 && !senhasBatem && <p className="login-formulario__secao-nota" style={{ color: "#e8a1ab" }}>As senhas não coincidem.</p>}
        </div>
      </div>
      {erro && <p role="alert" className="login-formulario__erro">{erro}</p>}
      <button className="login-formulario__entrar" type="submit" disabled={!senhasBatem || senha.length < 8 || enviando}>
        <span>{enviando ? "Salvando…" : "Redefinir senha"}</span>
        {!enviando && <Icone nome="seta" aria-hidden="true" />}
        {enviando && <i className="login-formulario__carregando" aria-hidden="true" />}
      </button>
    </form>
  );

  return (
    <main className="login login--recovery">
      <section className="login-vitrine" aria-labelledby="reset-vitrine-titulo">
        <div className="login-vitrine__luz login-vitrine__luz--um" aria-hidden="true" />
        <div className="login-vitrine__luz login-vitrine__luz--dois" aria-hidden="true" />
        <Link to="/" className="login-vitrine__marca" aria-label="CorVIA — página inicial"><img src="/corvia-logo.png" alt="CorVIA" /><small>Clinical OS do médico</small></Link>
        <div className="login-vitrine__conteudo">
          <h1 id="reset-vitrine-titulo">Novo acesso.<br /><em>Mesmo Clinical OS.</em></h1>
          <p className="login-vitrine__descricao">Escolha uma senha nova. O token é de uso único e expira automaticamente.</p>
          <GrafoConstelacao variante="escuro" className="login-vitrine__grafo" />
          <ul className="login-vitrine__beneficios">
            <li><Icone nome="check" aria-hidden="true" />Link de uso único</li>
            <li><Icone nome="check" aria-hidden="true" />Senha armazenada apenas como hash</li>
            <li><Icone nome="check" aria-hidden="true" />Nenhuma senha enviada por e-mail</li>
          </ul>
        </div>
        <footer className="login-vitrine__rodape"><span>CorVIA — Clinical OS do médico</span><span>Acesso protegido</span></footer>
      </section>

      <section className="login-acesso" aria-labelledby="reset-titulo">
        <div className="login-acesso__topo">
          <Link to="/" aria-label="CorVIA — início"><img src="/corvia-logo-compacta.png" alt="CorVIA" /></Link>
          <Link to="/entrar" className="login-acesso__conhecer"><span>Voltar ao login</span><Icone nome="seta" aria-hidden="true" /></Link>
        </div>
        <div className="login-acesso__conteudo">
          <div className="login-acesso__introducao">
            <p className="eyebrow">Segurança da conta</p>
            <h2 id="reset-titulo">{alvo === "email" ? "Nova senha do CorVIA Mail." : "Defina sua nova senha."}</h2>
            <p>Use ao menos 8 caracteres e não reutilize uma senha comprometida em outro serviço.</p>
          </div>
          {conteudo}
          <p className="login-acesso__seguranca"><Icone nome="check" aria-hidden="true" /> Em caso de dúvida, fale com contato@corvia.med.br.</p>
        </div>
        <footer className="login-acesso__rodape"><span>© {new Date().getFullYear()} CorVIA</span><nav aria-label="Links institucionais"><Link to="/privacidade">Privacidade</Link><Link to="/termos">Termos</Link><a href="mailto:contato@corvia.med.br">Suporte</a></nav></footer>
      </section>
    </main>
  );
}
