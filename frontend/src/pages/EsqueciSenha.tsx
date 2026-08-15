import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import Icone from "../components/Icone";
import PreHomeBrand from "../components/PreHomeBrand";
import "../styles/login.css";

const BENEFICIOS = [
  { icon: "check" as const, title: "Acesso protegido", detail: "O link seguro é entregue somente ao canal externo configurado para a conta.", tone: "cyan" as const },
  { icon: "conta" as const, title: "Exclusivo para você", detail: "O token é temporário, de uso único e vinculado à sua conta profissional.", tone: "violet" as const },
  { icon: "sincronizar" as const, title: "Seu ambiente, seus dados", detail: "A recuperação não depende da caixa CorVIA e não revela se uma conta existe.", tone: "green" as const },
];

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
      setEnviado(true);
    }
  }

  return (
    <main className="login prehome prehome--recovery">
      <PreHomeBrand
        title={<>Recupere seu acesso com <strong>segurança</strong></>}
        description={<>Retome o controle do seu Clinical Command Center com um fluxo independente, protegido e rastreável.</>}
        benefits={BENEFICIOS}
        trustTitle="Segurança que protege o que importa"
        trustText="Seu acesso profissional e os dados do seu ambiente permanecem protegidos."
      />
      <section className="prehome-access" aria-labelledby="recovery-titulo">
        <div className="prehome-card">
          <header className="prehome-card__header">
            <p className="prehome-card__eyebrow"><Icone nome="sincronizar" /> Segurança da conta</p>
            <h2 id="recovery-titulo">Esqueci minha senha</h2>
            <p>Informe o e-mail da sua conta de acesso ou o segundo e-mail cadastrado. Se houver uma conta ativa, enviaremos o link ao canal externo seguro.</p>
          </header>
          {enviado ? (
            <div className="prehome-confirmation" role="status">
              <div className="prehome-confirmation__icon"><Icone nome="check" /></div>
              <h2>Confira seu canal de recuperação</h2>
              <p>Se o endereço estiver vinculado a uma conta ativa, o link de redefinição foi enviado ao canal seguro cadastrado. Ele vale por tempo limitado e é de uso único.</p>
              <div className="prehome-info"><Icone nome="mail" /><p>Não recebeu? Verifique spam ou lixo eletrônico. Se continuar sem chegar, fale com contato@corvia.med.br.</p></div>
              <Link to="/entrar" className="prehome-primary"><span>Voltar ao login</span><Icone nome="seta" /></Link>
            </div>
          ) : (
            <form className="login-formulario" onSubmit={enviar}>
              <div className="login-campo"><label htmlFor="email">E-mail</label><input id="email" type="email" autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="seu@email.com" required autoFocus /></div>
              <div className="prehome-info"><Icone nome="check" /><p><strong>Por que pedimos seu e-mail?</strong><br />Para localizar a conta sem expor sua existência e encaminhar a recuperação somente para o canal externo protegido.</p></div>
              <button className="login-formulario__entrar" type="submit" disabled={!email.includes("@") || enviando}>
                <span>{enviando ? "Solicitando…" : "Enviar link de redefinição"}</span>{!enviando && <Icone nome="seta" aria-hidden="true" />}{enviando && <i className="login-formulario__carregando" aria-hidden="true" />}
              </button>
            </form>
          )}
          {!enviado && <div className="prehome-card__actions"><div className="prehome-divider">ou</div><Link to="/entrar" className="prehome-secondary">← Voltar ao login</Link><a href="mailto:contato@corvia.med.br" className="prehome-link" style={{ textAlign: "center" }}>Preciso de ajuda com meu acesso</a></div>}
          <footer className="prehome-card__footer"><Icone nome="check" /> Ambiente seguro para uso profissional</footer>
        </div>
        <nav className="prehome-legal" aria-label="Links institucionais"><Link to="/privacidade">Privacidade</Link><Link to="/termos">Termos</Link></nav>
      </section>
    </main>
  );
}
