import { useEffect, useMemo, useState, type FormEvent } from "react";
import { Link, useSearchParams } from "react-router-dom";
import Icone from "../components/Icone";
import PreHomeBrand from "../components/PreHomeBrand";
import { useAuth } from "../lib/auth";
import "../styles/login.css";
import "../styles/login-fullscreen-social.css";
import "../styles/prehome-reference-final.css";
import "../styles/login-viewport-refinement.css";

const BASE = import.meta.env.VITE_API_URL ?? "/api";

type SocialProvider = {
  id: "google" | "microsoft" | "apple" | "github";
  label: string;
  enabled: boolean;
};

const ORDEM_PROVEDORES: SocialProvider["id"][] = ["google", "microsoft", "apple", "github"];

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
  if (provider === "google") {
    return (
      <span className="prehome-social__mark prehome-social__mark--google" aria-hidden="true">
        <svg viewBox="0 0 24 24" focusable="false">
          <path fill="#4285F4" d="M21.6 12.23c0-.71-.06-1.4-.18-2.06H12v3.9h5.38a4.6 4.6 0 0 1-2 3.02v2.53h3.24c1.9-1.75 2.98-4.33 2.98-7.39Z" />
          <path fill="#34A853" d="M12 22c2.7 0 4.97-.9 6.62-2.38l-3.24-2.53c-.9.6-2.05.96-3.38.96-2.6 0-4.81-1.76-5.6-4.13H3.06v2.61A10 10 0 0 0 12 22Z" />
          <path fill="#FBBC05" d="M6.4 13.92A6 6 0 0 1 6.08 12c0-.67.12-1.32.32-1.92V7.47H3.06A10 10 0 0 0 2 12c0 1.61.38 3.13 1.06 4.53l3.34-2.61Z" />
          <path fill="#EA4335" d="M12 5.95c1.47 0 2.79.5 3.83 1.5l2.87-2.87A9.64 9.64 0 0 0 12 2 10 10 0 0 0 3.06 7.47l3.34 2.61C7.19 7.71 9.4 5.95 12 5.95Z" />
        </svg>
      </span>
    );
  }
  if (provider === "microsoft") {
    return (
      <span className="prehome-social__mark prehome-social__mark--microsoft" aria-hidden="true">
        <svg viewBox="0 0 24 24" focusable="false">
          <path fill="#F35325" d="M2 2h9v9H2z" /><path fill="#81BC06" d="M13 2h9v9h-9z" />
          <path fill="#05A6F0" d="M2 13h9v9H2z" /><path fill="#FFBA08" d="M13 13h9v9h-9z" />
        </svg>
      </span>
    );
  }
  if (provider === "apple") {
    return (
      <span className="prehome-social__mark prehome-social__mark--apple" aria-hidden="true">
        <svg viewBox="0 0 24 24" focusable="false">
          <path fill="currentColor" d="M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.59 9.05 7.31c1.34-.24 2.2.74 2.96.74.74 0 1.89-1.06 3.19-.9.54.02 2.06.22 3.03 1.64-2.62 1.52-2.2 4.97.45 6.03-.53 1.4-1.21 2.79-1.63 3.46ZM12.03 7.25c-.15-2.08 1.55-3.8 3.49-3.97.27 2.41-2.18 4.21-3.49 3.97Z" />
        </svg>
      </span>
    );
  }
  return <span className="prehome-social__mark prehome-social__mark--github" aria-hidden="true">GH</span>;
}

function MarcaAndroid() {
  return (
    <svg viewBox="0 0 24 24" focusable="false" aria-hidden="true">
      <path fill="currentColor" d="m7.1 6.55-1.3-2.26a.5.5 0 0 1 .87-.5l1.32 2.3A8.1 8.1 0 0 1 12 5.05c1.45 0 2.82.38 4.01 1.04l1.32-2.3a.5.5 0 0 1 .87.5l-1.3 2.26A7.42 7.42 0 0 1 20 12H4a7.42 7.42 0 0 1 3.1-5.45ZM8 9.5a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Zm8 0A.75.75 0 1 0 16 8a.75.75 0 0 0 0 1.5ZM4 13h16v6a2 2 0 0 1-2 2h-1v1.25a.75.75 0 0 1-1.5 0V21h-7v1.25a.75.75 0 0 1-1.5 0V21H6a2 2 0 0 1-2-2v-6Z" />
    </svg>
  );
}

function MarcaWindows() {
  return (
    <svg viewBox="0 0 24 24" focusable="false" aria-hidden="true">
      <path fill="currentColor" d="M2 3.4 10.7 2v9.3H2V3.4Zm9.7-1.55L22 0v11.3H11.7V1.85ZM2 12.3h8.7v9.3L2 20.2v-7.9Zm9.7 0H22V24l-10.3-1.85V12.3Z" />
    </svg>
  );
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

  const providersAtivos = useMemo(
    () => providers
      .filter((provider) => provider.enabled)
      .sort((a, b) => ORDEM_PROVEDORES.indexOf(a.id) - ORDEM_PROVEDORES.indexOf(b.id)),
    [providers],
  );

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
            <a
              className="prehome-android-download"
              href="/downloads/corvia-os-android-1.0.1.apk"
              download="CorVIA-OS-Android-1.0.1.apk"
            >
              <span className="prehome-android-download__icon"><MarcaAndroid /></span>
              <span><strong>Baixar app para Android</strong><small>Versão 1.0.1 · APK assinado</small></span>
              <Icone nome="seta" aria-hidden="true" />
            </a>
            <a
              className="prehome-windows-download"
              href="/downloads/corvia-os-windows.exe"
              download="CorVIA-OS-Windows-Setup.exe"
              aria-label="Baixar instalador EXE do CorVIA OS para Windows 10 ou 11"
            >
              <span className="prehome-windows-download__icon"><MarcaWindows /></span>
              <span><strong>Baixar instalador para Windows</strong><small>Arquivo .EXE · Windows 10/11</small></span>
              <Icone nome="seta" aria-hidden="true" />
            </a>
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
