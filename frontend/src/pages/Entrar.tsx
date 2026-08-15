import { useEffect, useMemo, useState, type FormEvent } from "react";
import { Link, useSearchParams } from "react-router-dom";
import Icone from "../components/Icone";
import PreHomeBrand from "../components/PreHomeBrand";
import { useAuth } from "../lib/auth";
import "../styles/login.css";
import "../styles/login-fullscreen-social.css";
import "../styles/prehome-reference-final.css";

const BASE = import.meta.env.VITE_API_URL ?? "/api";

type SocialProvider = {
  id: "google" | "microsoft" | "apple" | "yahoo" | "github";
  label: string;
  enabled: boolean;
};

const BENEFICIOS = [
  { icon: "assistente" as const, title: "Inteligência clínica", detail: "Contexto e apoio à decisão no mesmo ambiente.", tone: "cyan" as const },
  { icon: "evidencia" as const, title: "Evidências atualizadas", detail: "Guidelines, literatura e protocolos conectados.", tone: "violet" as const },
  { icon: "check" as const, title: "Segurança e privacidade", detail: "Acesso profissional protegido e rastreável.", tone: "green" as const },
];

const ERROS_SOCIAIS: Record<string, string> = {
  provider_denied: "A autenticação externa foi cancelada.",
  invalid_callback: "Não foi possível validar o retorno do provedor. Tente novamente.",
  invalid_state: "A sessão de autenticação expirou ou não pôde ser confirmada. Tente novamente.",
  identity_failed: "O provedor não conseguiu confirmar sua identidade.",
  account_not_linked: "O e-mail confirmado pelo provedor não corresponde a uma conta CorVIA aprovada. Entre com o mesmo e-mail cadastrado ou solicite acesso.",
  unsupported_provider: "Este provedor de autenticação não está disponível.",
};

function MarcaProvider({ provider }: { provider: SocialProvider["id"] }) {
  if (provider === "microsoft") {
    return <span className="prehome-social__mark prehome-social__mark--microsoft" aria-hidden="true"><i /><i /><i /><i /></span>;
  }
  if (provider === "apple") return <span className="prehome-social__mark prehome-social__mark--apple" aria-hidden="true"></span>;
  if (provider === "yahoo") return <span className="prehome-social__mark prehome-social__mark--yahoo" aria-hidden="true">Y!</span>;
  if (provider === "github") return <span className="prehome-social__mark prehome-social__mark--github" aria-hidden="true">GH</span>;
  return <span className="prehome-social__mark prehome-social__mark--google" aria-hidden="true">G</span>;
}

export default function Entrar() {
  const { entrar } = useAuth();
  const [params] = useSearchParams();
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [mostrarSenha, setMostrarSenha] = useState(false);
  const [permanecerConectado, setPermanecerConectado] = useState(false);
  const [erro, setErro] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [providers, setProviders] = useState<SocialProvider[]>([]);
  const [carregandoProviders, setCarregandoProviders] = useState(true);

  useEffect(() => {
    const code = params.get("social_error") || "";
    if (code) setErro(ERROS_SOCIAIS[code] || "Não foi possível entrar com esta conta externa.");
  }, [params]);

  useEffect(() => {
    let ativo = true;
    fetch(`${BASE}/auth/social/providers`, { credentials: "include", cache: "no-store" })
      .then(async (response) => {
        if (!response.ok) throw new Error("providers");
        return response.json() as Promise<{ providers?: SocialProvider[] }>;
      })
      .then((body) => { if (ativo) setProviders(Array.isArray(body.providers) ? body.providers : []); })
      .catch(() => { if (ativo) setProviders([]); })
      .finally(() => { if (ativo) setCarregandoProviders(false); });
    return () => { ativo = false; };
  }, []);

  const providersAtivos = useMemo(() => providers.filter((provider) => provider.enabled), [providers]);

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

  function entrarCom(provider: SocialProvider["id"]) {
    setErro("");
    window.location.assign(`${BASE}/auth/social/${provider}/start`);
  }

  return (
    <main className="login prehome prehome--login prehome--fullscreen">
      <PreHomeBrand
        title={<>Tudo o que o cardiologista precisa. <strong>Em um só lugar.</strong></>}
        description={<>Seu Clinical OS conecta conhecimento, decisão, assistência e rotina sem tirar o médico do centro.</>}
        benefits={BENEFICIOS}
      />
      <section className="prehome-access" aria-labelledby="login-acesso-titulo">
        <div className="prehome-card prehome-card--login">
          <header className="prehome-card__header">
            <p className="prehome-card__eyebrow"><Icone nome="conta" /> Acesso profissional</p>
            <h2 id="login-acesso-titulo">Bem-vindo de volta</h2>
            <p>Acesse sua conta para continuar no CorVIA Clinical OS.</p>
          </header>
          <form className="login-formulario" onSubmit={enviar}>
            <div className="login-campo">
              <label htmlFor="email">E-mail</label>
              <input id="email" type="email" inputMode="email" autoCapitalize="none" autoComplete="username" placeholder="seu@email.com" value={email} onChange={(event) => setEmail(event.target.value)} aria-invalid={Boolean(erro)} aria-describedby={erro ? "login-erro" : undefined} required autoFocus />
            </div>
            <div className="login-campo">
              <label htmlFor="senha">Senha</label>
              <div className="login-senha">
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
              <span>{enviando ? "Abrindo seu Clinical OS…" : "Entrar na minha conta"}</span>{!enviando && <Icone nome="seta" aria-hidden="true" />}{enviando && <i className="login-formulario__carregando" aria-hidden="true" />}
            </button>
          </form>
          <div className="prehome-card__actions">
            {(providersAtivos.length > 0 || carregandoProviders) && <div className="prehome-divider">ou entre com sua conta</div>}
            {providersAtivos.length > 0 && (
              <div className={`prehome-social prehome-social--${Math.min(providersAtivos.length, 5)}`} aria-label="Entrar com conta externa">
                {providersAtivos.map((provider) => (
                  <button key={provider.id} type="button" className="prehome-social__button" onClick={() => entrarCom(provider.id)} aria-label={`Entrar com ${provider.label}`}>
                    <MarcaProvider provider={provider.id} />
                    <span>{provider.label}</span>
                  </button>
                ))}
              </div>
            )}
            <Link to="/solicitar-acesso" className="prehome-secondary"><Icone nome="conta" /> Solicitar acesso</Link>
          </div>
          <footer className="prehome-card__footer"><Icone nome="check" /><span>Seus dados estão protegidos · ambiente profissional em conformidade com a LGPD</span></footer>
        </div>
        <nav className="prehome-legal" aria-label="Links institucionais"><Link to="/privacidade">Privacidade</Link><Link to="/termos">Termos</Link><a href="mailto:contato@corvia.med.br">Suporte</a></nav>
      </section>
    </main>
  );
}
