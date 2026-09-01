import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../lib/auth";
import PublicCardiologyFrame, { type PublicFrameFeature } from "./PublicCardiologyFrame";

type LegalDocumentFrameProps = {
  children: ReactNode;
  eyebrow: string;
  title: ReactNode;
  description: ReactNode;
  updated: string;
  features: PublicFrameFeature[];
  footer: ReactNode;
  tone?: "blue" | "cyan" | "violet" | "pink";
};

/**
 * A mesma página jurídica vive em dois contextos: pública e dentro do app.
 * O conteúdo e os links são únicos; apenas o enquadramento muda para não
 * inserir uma segunda aplicação de tela cheia dentro do App Frame autenticado.
 */
export default function LegalDocumentFrame({
  children,
  eyebrow,
  title,
  description,
  updated,
  features,
  footer,
  tone = "cyan",
}: LegalDocumentFrameProps) {
  const { usuario } = useAuth();

  if (usuario) {
    return (
      <main className="legal-page" id="conteudo-principal">
        <header>
          <Link to="/" aria-label="Voltar ao CorVIA">
            <img src="/corvia-logo-spaces-dark.svg" alt="CorVIA Cardiology Spaces" />
          </Link>
          <p className="eyebrow">{eyebrow}</p>
          <h1>{title}</h1>
          <p>Última atualização: {updated}.</p>
        </header>
        {children}
        <footer>{footer}</footer>
      </main>
    );
  }

  return (
    <PublicCardiologyFrame
      eyebrow={eyebrow}
      title={title}
      description={description}
      features={features}
      variant="reading"
      tone={tone}
      status={<span>Última atualização · {updated}</span>}
    >
      <div className="public-legal-content">
        {children}
        <footer>{footer}</footer>
      </div>
    </PublicCardiologyFrame>
  );
}
