import { useRef, useState, type FormEvent } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api, ApiError } from "../lib/api";
import Icone from "../components/Icone";
import PublicCardiologyFrame from "../components/PublicCardiologyFrame";
import "../styles/login.css";

const BENEFICIOS = [
  { icon: "check" as const, title: "Acesso protegido", detail: "O link seguro é entregue somente ao canal externo configurado para a conta.", tone: "cyan" as const },
  { icon: "conta" as const, title: "Exclusivo para você", detail: "O token é temporário, de uso único e vinculado à sua conta profissional.", tone: "violet" as const },
  { icon: "sincronizar" as const, title: "Seu ambiente, seus dados", detail: "A recuperação não depende da caixa CorVIA e não revela se uma conta existe.", tone: "green" as const },
];

export default function EsqueciSenha() {
  const [params] = useSearchParams();
  const ativacao = params.get("modo") === "ativacao";
  return <SolicitarLink key={ativacao ? "ativacao" : "senha"} ativacao={ativacao} />;
}

function SolicitarLink({ ativacao }: { ativacao: boolean }) {
  const [email, setEmail] = useState("");
  const [enviado, setEnviado] = useState(false);
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState("");
  const solicitacaoEmCurso = useRef(false);

  async function enviar(event?: FormEvent<HTMLFormElement>) {
    event?.preventDefault();
    if (!email.includes("@") || solicitacaoEmCurso.current) return;
    solicitacaoEmCurso.current = true;
    setErro("");
    setEnviando(true);
    try {
      await api.post(ativacao ? "/auth/reenviar-ativacao" : "/auth/esqueci-senha", { email: email.trim().toLowerCase() });
      setEnviado(true);
    } catch (error) {
      // Do not expose backend/account details on this public recovery form.
      setErro(error instanceof ApiError && error.status === 429
        ? "Muitas tentativas de recuperação. Aguarde um pouco e tente novamente."
        : "Não foi possível solicitar a recuperação agora. Verifique sua conexão ou tente novamente em instantes.");
    } finally {
      solicitacaoEmCurso.current = false;
      setEnviando(false);
    }
  }

  return (
    <PublicCardiologyFrame
      eyebrow="Segurança da identidade"
      title={ativacao ? <>Solicite um novo <strong>link de acesso.</strong></> : <>Recupere seu acesso sem perder o seu <strong>universo.</strong></>}
      description={<p>{ativacao ? "Informe o e-mail de login usado no cadastro para solicitar novamente o link de ativação." : "O caminho de volta é independente, temporário e protegido para preservar seus cinco espaços e o contexto profissional."}</p>}
      features={ativacao ? [{ icon: "check", title: "Acesso protegido", detail: "A solicitação preserva a privacidade da conta e respeita as condições de acesso do cadastro.", tone: "cyan" }] : BENEFICIOS}
      variant="form"
      tone="violet"
    >
      <div className="prehome-card">
          <header className="prehome-card__header">
            <p className="prehome-card__eyebrow"><Icone nome="sincronizar" /> Segurança da conta</p>
            <h2 id="recovery-titulo">{ativacao ? "Reenviar link de ativação" : "Esqueci minha senha"}</h2>
            <p>{ativacao ? "Não recebeu o link de primeiro acesso? Informe o e-mail de login da conta. A solicitação não altera a análise ou a aprovação do cadastro." : "Informe o e-mail da sua conta de acesso ou o segundo e-mail cadastrado. Se houver uma conta ativa, enviaremos o link ao canal externo seguro."}</p>
          </header>
          {enviado ? (
            <div className="prehome-confirmation" role="status">
              <div className="prehome-confirmation__icon"><Icone nome="check" /></div>
              <h2>{ativacao ? "Solicitação recebida" : "Confira seu canal de recuperação"}</h2>
              <p>{ativacao ? "Se houver uma conta elegível com este e-mail, enviaremos um novo link de acesso. Verifique os canais cadastrados e a pasta de spam." : "Se o endereço estiver vinculado a uma conta ativa, o link de redefinição foi enviado ao canal seguro cadastrado. Ele vale por tempo limitado e é de uso único."}</p>
              <div className="prehome-info"><Icone nome="mail" /><p>Não recebeu? Verifique spam ou lixo eletrônico. Se continuar sem chegar, fale com contato@corvia.med.br.</p></div>
              <Link to="/entrar" className="prehome-primary"><span>Voltar ao login</span><Icone nome="seta" /></Link>
            </div>
          ) : (
            <form className="login-formulario" onSubmit={enviar} aria-busy={enviando}>
              <div className="login-campo"><label htmlFor="email">{ativacao ? "E-mail de login" : "E-mail"}</label><input id="email" type="email" autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="seu@email.com" required autoFocus disabled={enviando} /></div>
              <div className="prehome-info"><Icone nome="check" /><p><strong>Por que pedimos seu e-mail?</strong><br />{ativacao ? "Para solicitar um novo link sem expor a existência ou a situação da conta." : "Para localizar a conta sem expor sua existência e encaminhar a recuperação somente para o canal externo protegido."}</p></div>
              {erro && <p role="alert" className="login-formulario__erro recovery-request-error" style={{ fontSize: "1rem" }}>{erro}</p>}
              <button className="login-formulario__entrar" type="submit" disabled={!email.includes("@") || enviando}>
                <span>{enviando ? "Solicitando…" : ativacao ? "Solicitar novo link de ativação" : "Enviar link de redefinição"}</span>{!enviando && <Icone nome="seta" aria-hidden="true" />}{enviando && <i className="login-formulario__carregando" aria-hidden="true" />}
              </button>
            </form>
          )}
          {!enviado && <div className="prehome-card__actions"><div className="prehome-divider">ou</div><Link to="/entrar" className="prehome-secondary">← Voltar ao login</Link><Link to={ativacao ? "/esqueci-senha" : "/esqueci-senha?modo=ativacao"} className="prehome-link" style={{ textAlign: "center" }}>{ativacao ? "Preciso redefinir minha senha" : "Não recebi o link de ativação"}</Link><a href="mailto:contato@corvia.med.br" className="prehome-link" style={{ textAlign: "center" }}>Preciso de ajuda com meu acesso</a></div>}
          <footer className="prehome-card__footer"><Icone nome="check" /> Ambiente seguro para uso profissional</footer>
      </div>
    </PublicCardiologyFrame>
  );
}
