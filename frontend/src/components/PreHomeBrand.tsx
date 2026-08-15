import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import Icone, { type NomeIcone } from "./Icone";

export type PreHomeBenefit = {
  icon: NomeIcone;
  title: string;
  detail: string;
  tone?: "cyan" | "violet" | "green";
};

type Props = {
  title: ReactNode;
  description: ReactNode;
  benefits: PreHomeBenefit[];
  trustTitle?: string;
  trustText?: string;
  celebratory?: boolean;
};

export default function PreHomeBrand({
  title,
  description,
  benefits,
  trustTitle = "Ambiente seguro para uso profissional",
  trustText = "Dados protegidos. Decisões mais seguras.",
  celebratory = false,
}: Props) {
  return (
    <section
      className={`prehome-brand${celebratory ? " prehome-brand--celebratory" : ""}`}
      style={{ alignSelf: "start" }}
    >
      <div className="prehome-brand__aurora prehome-brand__aurora--cyan" aria-hidden="true" />
      <div className="prehome-brand__aurora prehome-brand__aurora--violet" aria-hidden="true" />

      <Link to="/" className="prehome-brand__logo" aria-label="CorVIA — página inicial">
        <img src="/corvia-mark-canonical.svg" alt="" aria-hidden="true" />
        <span>
          <strong>CorVIA</strong>
          <small>Clinical OS do médico</small>
        </span>
      </Link>

      <div className="prehome-brand__content">
        <div className="prehome-brand__copy">
          <h1>{title}</h1>
          <p>{description}</p>
        </div>

        <div className="prehome-brand__hologram" aria-hidden="true">
          <div className="prehome-brand__hud prehome-brand__hud--left"><span /><span /><span /></div>
          <div className="prehome-brand__hud prehome-brand__hud--right"><span /><span /><span /></div>
          <div className="prehome-brand__heart-glow" />
          <img src="/corvia-mark-canonical.svg" alt="" />
          <svg className="prehome-brand__pulse" viewBox="0 0 240 42" focusable="false">
            <path d="M2 23h55l10-14 14 28 13-22 13 14 12-8h119" />
          </svg>
          <i className="prehome-brand__ring prehome-brand__ring--1" />
          <i className="prehome-brand__ring prehome-brand__ring--2" />
          <i className="prehome-brand__ring prehome-brand__ring--3" />
        </div>

        <div className="prehome-brand__benefits">
          {benefits.map((benefit) => (
            <div className="prehome-benefit" data-tone={benefit.tone ?? "cyan"} key={benefit.title}>
              <span className="prehome-benefit__icon"><Icone nome={benefit.icon} aria-hidden="true" /></span>
              <span><strong>{benefit.title}</strong><small>{benefit.detail}</small></span>
            </div>
          ))}
        </div>

        <div className="prehome-brand__trust">
          <Icone nome="check" aria-hidden="true" />
          <span><strong>{trustTitle}</strong><small>{trustText}</small></span>
        </div>
      </div>

      <footer className="prehome-brand__footer">
        <span><Icone nome="check" aria-hidden="true" /> Conformidade: LGPD</span>
        <span>Criptografia em trânsito e repouso</span>
        <span>Logs de auditoria</span>
      </footer>
    </section>
  );
}
