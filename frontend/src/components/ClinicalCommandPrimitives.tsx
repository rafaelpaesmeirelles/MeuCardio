import type { ReactNode } from "react";
import { Link, useLocation } from "react-router-dom";
import { CLINICAL_SPACES, findClinicalRoute, type FunctionalSpace } from "../lib/clinicalRouteRegistry";
import Icone, { type NomeIcone } from "./Icone";
import "../styles/cardiology-spaces-command-primitives.css";

type HeaderAction = { to: string; label: string; icon?: NomeIcone; tone?: "default" | "primary" | "danger" };

type PageHeaderProps = {
  eyebrow: string;
  title: string;
  description?: string;
  icon?: NomeIcone;
  actions?: HeaderAction[];
  meta?: ReactNode;
};

export function ClinicalPageHeader({ eyebrow, title, description, icon = "clinica", actions = [], meta }: PageHeaderProps) {
  const { pathname } = useLocation();
  const definition = findClinicalRoute(pathname);
  const space: FunctionalSpace = definition && definition.space !== "home" ? definition.space : "consultorio";
  const spaceLabel = CLINICAL_SPACES[space].label;
  return (
    <header className={`cv-page-hero cv-page-hero--${space}`} data-cardiology-space={space}>
      <div className="cv-page-hero__space" aria-label={`CorVIA Cardiology Spaces — ${spaceLabel}`}>
        <span className="cv-page-hero__beacon" aria-hidden="true" />
        <span>CARDIOLOGY SPACES</span><i>·</i><strong>{spaceLabel}</strong>
      </div>
      <div className="cv-page-hero__identity">
        <span className="cv-page-hero__icon"><Icone nome={icon} /></span>
        <div>
          <p className="eyebrow">{eyebrow}</p>
          <h1>{title}</h1>
          {description && <p className="cv-page-hero__description">{description}</p>}
          {meta && <div className="cv-page-hero__meta">{meta}</div>}
        </div>
      </div>
      {actions.length > 0 && (
        <div className="cv-page-hero__actions">
          {actions.map((action) => (
            <Link key={`${action.to}-${action.label}`} to={action.to} className={`cv-action cv-action--${action.tone ?? "default"}`}>
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
    <section className={`cv-section${className ? ` ${className}` : ""}`}>
      {(eyebrow || title || description || action) && (
        <div className="cv-section__heading">
          <div>
            {eyebrow && <p className="eyebrow">{eyebrow}</p>}
            {title && <h2>{title}</h2>}
            {description && <p>{description}</p>}
          </div>
          {action && <div className="cv-section__action">{action}</div>}
        </div>
      )}
      {children}
    </section>
  );
}

export function ClinicalMetric({ label, value, detail, icon }: { label: string; value: ReactNode; detail?: string; icon?: NomeIcone }) {
  return (
    <div className="cv-metric">
      <div className="cv-metric__top">{icon && <Icone nome={icon} />}<span>{label}</span></div>
      <strong>{value}</strong>
      {detail && <small>{detail}</small>}
    </div>
  );
}

export function ClinicalEmpty({ title, description }: { title: string; description?: string }) {
  return (
    <div className="cv-empty">
      <span>◎</span>
      <strong>{title}</strong>
      {description && <p>{description}</p>}
    </div>
  );
}

export function ClinicalContextLink({ to, icon, title, detail }: { to: string; icon: NomeIcone; title: string; detail: string }) {
  return (
    <Link to={to} className="cv-context-link">
      <span><Icone nome={icon} /></span>
      <span><strong>{title}</strong><small>{detail}</small></span>
      <Icone nome="seta" />
    </Link>
  );
}
