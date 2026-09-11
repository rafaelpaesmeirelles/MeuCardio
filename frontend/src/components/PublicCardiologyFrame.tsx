import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import Icone, { type NomeIcone } from "./Icone";
import "../styles/corvia-atelier-public.css";

export type PublicFrameFeature = {
  icon: NomeIcone;
  title: string;
  detail: string;
  tone?: "blue" | "cyan" | "violet" | "pink" | "green";
};

type PublicCardiologyFrameProps = {
  children: ReactNode;
  eyebrow: string;
  title: ReactNode;
  description: ReactNode;
  features?: PublicFrameFeature[];
  variant?: "form" | "reading" | "validator";
  tone?: "blue" | "cyan" | "violet" | "pink";
  status?: ReactNode;
};

export function PublicCorviaBrand({ to = "/entrar" }: { to?: string }) {
  return (
    <Link to={to} className="public-corvia-brand public-corvia-brand--atelier" aria-label="CorVIA Cardiology Spaces">
      <img src="/atelier/corvia-logo-atelier.svg" width="900" height="240" alt="CorVIA Cardiology Spaces" />
    </Link>
  );
}

export default function PublicCardiologyFrame({
  children,
  eyebrow,
  title,
  description,
  features = [],
  variant = "form",
  tone = "blue",
  status,
}: PublicCardiologyFrameProps) {
  return (
    <div className={`public-space public-space--${variant} public-space--${tone} corvia-atelier-public`}>
      <a className="public-space__skip" href="#conteudo-principal">Ir para o conteúdo</a>

      <header className="public-space__topbar">
        <PublicCorviaBrand />
        <nav aria-label="Navegação pública">
          <Link to="/produto">Conhecer o CorVIA</Link>
          <Link to="/entrar" className="public-space__access">Entrar</Link>
        </nav>
        <div className="public-space__security">
          <span><i /> Ambiente protegido</span>
          <small>Acesso profissional · LGPD</small>
        </div>
      </header>

      <main className="public-space__workspace" id="conteudo-principal" tabIndex={-1}>
        <section className="public-space__context" aria-labelledby="public-space-title">
          <div className="public-space__signal" aria-hidden="true">
            <span><Icone nome="ecg" /></span>
          </div>
          <p>{eyebrow}</p>
          <h1 id="public-space-title">{title}</h1>
          <div className="public-space__description">{description}</div>
          <figure className="atelier-public__scene" aria-hidden="true">
            <img src="/atelier/atelier-entrance.webp" width="1536" height="1024" alt="" />
          </figure>
          {features.length > 0 && (
            <div className="public-space__features" aria-label="Informações importantes">
              {features.map((feature) => (
                <article data-tone={feature.tone ?? "cyan"} key={feature.title}>
                  <span><Icone nome={feature.icon} aria-hidden="true" /></span>
                  <div><strong>{feature.title}</strong><small>{feature.detail}</small></div>
                </article>
              ))}
            </div>
          )}
          {status && <div className="public-space__context-status">{status}</div>}
        </section>

        <section className="public-space__surface">
          {children}
        </section>
      </main>

      <footer className="public-space__footer">
        <span><Icone nome="check" aria-hidden="true" /> Privacidade por padrão</span>
        <nav aria-label="Links institucionais">
          <Link to="/privacidade">Privacidade</Link>
          <Link to="/termos">Termos</Link>
          <Link to="/excluir-conta">Excluir conta</Link>
          <a href="mailto:contato@corvia.med.br">Suporte</a>
        </nav>
      </footer>
    </div>
  );
}
