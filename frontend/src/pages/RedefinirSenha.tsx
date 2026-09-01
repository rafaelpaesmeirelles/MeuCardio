import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { api, ApiError } from "../lib/api";
import Icone from "../components/Icone";
import CampoSenha from "../components/CampoSenha";
import PublicCardiologyFrame from "../components/PublicCardiologyFrame";
import "../styles/login.css";

const BENEFICIOS = [
  { icon: "check" as const, title: "Segurança avançada", detail: "O token de recuperação é temporário, vinculado à conta e de uso único.", tone: "cyan" as const },
  { icon: "documento" as const, title: "Proteção de dados", detail: "A senha não é enviada por e-mail e fica armazenada somente de forma protegida.", tone: "violet" as const },
  { icon: "sincronizar" as const, title: "Ambiente confiável", detail: "Depois da troca, o acesso volta ao fluxo normal do Cardiology Spaces.", tone: "green" as const },
];

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
  const regras = { tamanho: senha.length >= 8, maiuscula: /[A-Z]/.test(senha), minuscula: /[a-z]/.test(senha), numero: /\d/.test(senha), especial: /[^A-Za-z0-9]/.test(senha) };
  const pontosForca = Object.values(regras).filter(Boolean).length;
  const nivelForca = senha.length === 0 ? 0 : Math.max(1, Math.min(4, Math.ceil((pontosForca / 5) * 4)));
  const rotuloForca = nivelForca >= 4 ? "Forte" : nivelForca >= 3 ? "Boa" : nivelForca >= 2 ? "Média" : "Inicial";

  async function enviar() {
    setErro(""); setEnviando(true);
    try {
      await api.post("/auth/redefinir-senha", { token, nova_senha: senha });
      setFeito(true);
      setTimeout(() => navigate(alvo === "email" ? "/corvia-mail" : "/entrar"), 2500);
    } catch (e) { setErro(e instanceof ApiError ? e.message : "Não foi possível redefinir a senha."); }
    finally { setEnviando(false); }
  }

  const conteudo = !token ? (
    <div className="prehome-confirmation"><div className="prehome-confirmation__icon prehome-confirmation__icon--pending"><Icone nome="emergencia" /></div><h2>Link inválido</h2><p>O token de redefinição não está presente. Solicite um novo link pelo canal seguro.</p><Link to="/esqueci-senha" className="prehome-primary"><span>Solicitar novo link</span><Icone nome="seta" /></Link></div>
  ) : feito ? (
    <div className="prehome-confirmation" role="status"><div className="prehome-confirmation__icon"><Icone nome="check" /></div><h2>Senha atualizada</h2><p>Pronto. Você será levado para {alvo === "email" ? "o CorVIA Mail" : "o login do Cardiology Spaces"}.</p></div>
  ) : (
    <form className="login-formulario" onSubmit={(e) => { e.preventDefault(); void enviar(); }}>
      <div className="login-campo"><label htmlFor="senha">Nova senha</label><CampoSenha id="senha" autoComplete="new-password" value={senha} onChange={(e) => setSenha(e.target.value)} autoFocus /><div className="prehome-password-meter" data-level={nivelForca} aria-label={`Força da senha: ${rotuloForca}`}><i /><i /><i /><i /><span>{senha ? rotuloForca : ""}</span></div></div>
      <div className="login-campo"><label htmlFor="confirmacao">Confirmar nova senha</label><CampoSenha id="confirmacao" autoComplete="new-password" value={confirmacao} onChange={(e) => setConfirmacao(e.target.value)} />{confirmacao.length > 0 && !senhasBatem && <p className="login-formulario__secao-nota" style={{ color: "#ff9bad" }}>As senhas não coincidem.</p>}</div>
      <div><p className="prehome-card__eyebrow" style={{ marginBottom: 9 }}>Sua senha</p><ul className="prehome-password-rules"><li data-ok={regras.tamanho}><Icone nome="check" /> Mínimo de 8 caracteres</li><li data-ok={regras.maiuscula}><Icone nome="check" /> Letra maiúscula — recomendado</li><li data-ok={regras.minuscula}><Icone nome="check" /> Letra minúscula — recomendado</li><li data-ok={regras.numero}><Icone nome="check" /> Número — recomendado</li><li data-ok={regras.especial}><Icone nome="check" /> Caractere especial — recomendado</li></ul></div>
      {erro && <p role="alert" className="login-formulario__erro">{erro}</p>}
      <button className="login-formulario__entrar" type="submit" disabled={!senhasBatem || senha.length < 8 || enviando}><span>{enviando ? "Salvando…" : "Salvar nova senha"}</span>{!enviando && <Icone nome="seta" aria-hidden="true" />}{enviando && <i className="login-formulario__carregando" aria-hidden="true" />}</button>
    </form>
  );

  return (
    <PublicCardiologyFrame
      eyebrow="Novo ciclo de acesso"
      title={<>Uma nova senha. O mesmo contexto <strong>preservado.</strong></>}
      description={<p>Conclua a recuperação por um elo temporário e volte ao Cardiology Spaces sem reconstruir o seu ambiente.</p>}
      features={BENEFICIOS}
      variant="form"
      tone="violet"
    >
      <div className="prehome-card">
          {token && !feito && <div className="prehome-status-chip"><Icone nome="check" /> Link de recuperação recebido</div>}
          <header className="prehome-card__header" style={{ textAlign: "center" }}><h2 id="reset-titulo">{alvo === "email" ? "Definir nova senha do CorVIA Mail" : "Definir nova senha"}</h2><p style={{ marginLeft: "auto", marginRight: "auto" }}>Crie uma senha forte e exclusiva para acessar o Cardiology Spaces.</p></header>
          {conteudo}
          {!feito && token && <div className="prehome-card__actions"><div className="prehome-divider">ou</div><Link to="/entrar" className="prehome-secondary">← Voltar ao login</Link></div>}
          <footer className="prehome-card__footer"><Icone nome="check" /> Ambiente seguro para uso profissional</footer>
      </div>
    </PublicCardiologyFrame>
  );
}
