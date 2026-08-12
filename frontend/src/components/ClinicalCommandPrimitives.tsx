import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import Icone, { type NomeIcone } from "./Icone";

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
  return (
    <header className="cc-page-header">
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
    <section className={`cc-section${className ? ` ${className}` : ""}`}>
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
    <div className="cc-metric">
      <div className="cc-metric__top">{icon && <Icone nome={icon} />}<span>{label}</span></div>
      <strong>{value}</strong>
      {detail && <small>{detail}</small>}
    </div>
  );
}

export function ClinicalEmpty({ title, description }: { title: string; description?: string }) {
  return (
    <div className="cc-empty">
      <span>◎</span>
      <strong>{title}</strong>
      {description && <p>{description}</p>}
    </div>
  );
}

export function ClinicalContextLink({ to, icon, title, detail }: { to: string; icon: NomeIcone; title: string; detail: string }) {
  return (
    <Link to={to} className="cc-context-link">
      <span><Icone nome={icon} /></span>
      <span><strong>{title}</strong><small>{detail}</small></span>
      <Icone nome="seta" />
    </Link>
  );
}
