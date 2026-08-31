import type { ReactNode } from "react";
import { Link, useLocation } from "react-router-dom";
import Icone, { type NomeIcone } from "./Icone";
import "../styles/cardiology-spaces-command-primitives.css";

type HeaderAction = { to: string; label: string; icon?: NomeIcone; tone?: "default" | "primary" | "danger" };
type SpaceKey = "consultorio" | "hospital" | "ensino" | "pesquisa" | "gestao";

type PageHeaderProps = {
  eyebrow: string;
  title: string;
  description?: string;
  icon?: NomeIcone;
  actions?: HeaderAction[];
  meta?: ReactNode;
};

const SPACE_LABEL: Record<SpaceKey, string> = {
  consultorio: "Consultório",
  hospital: "Hospital",
  ensino: "Ensino",
  pesquisa: "Pesquisa",
  gestao: "Gestão",
};

const SPACE_ROUTES: Array<[string, SpaceKey]> = [
  ["/documentos-cientificos-ia", "pesquisa"], ["/evidencias", "pesquisa"], ["/estudos", "pesquisa"], ["/diretrizes", "pesquisa"], ["/biblioteca", "pesquisa"], ["/busca", "pesquisa"], ["/fluxogramas", "pesquisa"], ["/exportar", "pesquisa"], ["/favoritos", "pesquisa"],
  ["/casos-clinicos", "ensino"], ["/trilhas", "ensino"], ["/material-paciente", "ensino"], ["/galeria", "ensino"], ["/apresentacao", "ensino"],
  ["/heart-team", "hospital"], ["/round", "hospital"], ["/cardiologia-intensiva", "hospital"], ["/checklists", "hospital"], ["/emergencia", "hospital"], ["/exames-ia", "hospital"], ["/ecg-ia", "hospital"],
  ["/corvia-mail", "gestao"], ["/caixa-de-email", "gestao"], ["/whatsapp-assistant", "gestao"], ["/usuarios-online", "gestao"], ["/telediagnostico", "gestao"], ["/fila-telediagnostico", "gestao"], ["/sincronizacao", "gestao"], ["/minha-conta", "gestao"], ["/assinatura", "gestao"], ["/verificacao-identidade", "gestao"], ["/excluir-conta", "gestao"], ["/indicadores", "gestao"], ["/receitas-para-assinatura", "gestao"], ["/admin", "gestao"], ["/privacidade", "gestao"], ["/termos", "gestao"],
];

function spaceFor(pathname: string): SpaceKey {
  return SPACE_ROUTES.find(([prefix]) => pathname === prefix || pathname.startsWith(`${prefix}/`))?.[1] ?? "consultorio";
}

export function ClinicalPageHeader({ eyebrow, title, description, icon = "clinica", actions = [], meta }: PageHeaderProps) {
  const { pathname } = useLocation();
  const space = spaceFor(pathname);
  return (
    <header className={`cc-page-header cs-page-header cs-page-header--${space}`} data-cardiology-space={space}>
      <div className="cs-page-header__space" aria-label={`CorVIA Cardiology Spaces — ${SPACE_LABEL[space]}`}>
        <span className="cs-page-header__beacon" aria-hidden="true" />
        <span>CARDIOLOGY SPACES</span><i>·</i><strong>{SPACE_LABEL[space]}</strong>
      </div>
      <div className="cc-page-header__identity">
        <span className="cc-page-header__icon"><Icone nome={icon} /></span>
        <div>
          <p className="eyebrow">{eyebrow}</p>
          <h1>{title}</h1>
          {description && <p className="cc-page-header__description">{description}</p>}
          {meta && <div className="cc-page-header__meta">{meta}</div>}
        </div>
      </div>
      {actions.length > 0 && (
        <div className="cc-page-header__actions">
          {actions.map((action) => (
            <Link key={`${action.to}-${action.label}`} to={action.to} className={`cc-action cc-action--${action.tone ?? "default"}`}>
              {action.icon && <Icone nome={action.icon} />}
              <span>{action.label}</span>
              <Icone nome="seta" />
            </Link>
          ))}
        </div>
      )}
    </header>
  );
}

export function ClinicalSection({ eyebrow, title, description, action, children, className = "" }: {
  eyebrow?: string;
  title?: string;
  description?: string;
  action?: ReactNode;
  children: ReactNode;
  className?: string;
}) {
  return (
    <section className={`cc-section cs-section${className ? ` ${className}` : ""}`}>
      {(eyebrow || title || description || action) && (
        <div className="cc-section__heading">
          <div>
            {eyebrow && <p className="eyebrow">{eyebrow}</p>}
            {title && <h2>{title}</h2>}
            {description && <p>{description}</p>}
          </div>
          {action && <div className="cc-section__action">{action}</div>}
        </div>
      )}
      {children}
    </section>
  );
}

export function ClinicalMetric({ label, value, detail, icon }: { label: string; value: ReactNode; detail?: string; icon?: NomeIcone }) {
  return (
    <div className="cc-metric cs-metric">
      <div className="cc-metric__top">{icon && <Icone nome={icon} />}<span>{label}</span></div>
      <strong>{value}</strong>
      {detail && <small>{detail}</small>}
    </div>
  );
}

export function ClinicalEmpty({ title, description }: { title: string; description?: string }) {
  return (
    <div className="cc-empty cs-empty">
      <span>◎</span>
      <strong>{title}</strong>
      {description && <p>{description}</p>}
    </div>
  );
}

export function ClinicalContextLink({ to, icon, title, detail }: { to: string; icon: NomeIcone; title: string; detail: string }) {
  return (
    <Link to={to} className="cc-context-link cs-context-link">
      <span><Icone nome={icon} /></span>
      <span><strong>{title}</strong><small>{detail}</small></span>
      <Icone nome="seta" />
    </Link>
  );
}
