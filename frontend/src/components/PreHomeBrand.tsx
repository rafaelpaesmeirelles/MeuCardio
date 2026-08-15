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

const PILARES: Array<{ icon: NomeIcone; title: string; detail: string }> = [
  { icon: "assistente", title: "Inteligência Artificial", detail: "Contexto clínico" },
  { icon: "evidencia", title: "Evidências atualizadas", detail: "Fontes rastreáveis" },
  { icon: "sincronizar", title: "Tudo com Tudo", detail: "Conhecimento conectado" },
  { icon: "check", title: "Segurança e Privacidade", detail: "Proteção por padrão" },
];

function CoracaoHolografico() {
  return (
    <svg className="prehome-brand__heart" viewBox="0 0 320 360" role="img" aria-label="Coração digital do CorVIA">
      <defs>
        <linearGradient id="corvia-heart-main" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#12dce7" />
          <stop offset="0.48" stopColor="#2088ff" />
          <stop offset="0.72" stopColor="#8b5cf6" />
          <stop offset="1" stopColor="#ff416c" />
        </linearGradient>
        <linearGradient id="corvia-heart-vein" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#72f5ff" />
          <stop offset="1" stopColor="#ff5477" />
        </linearGradient>
        <radialGradient id="corvia-heart-core" cx="50%" cy="45%" r="55%">
          <stop offset="0" stopColor="#fc4b75" stopOpacity=".72" />
          <stop offset=".55" stopColor="#285ff4" stopOpacity=".25" />
          <stop offset="1" stopColor="#071425" stopOpacity="0" />
        </radialGradient>
        <filter id="corvia-heart-glow" x="-80%" y="-80%" width="260%" height="260%">
          <feGaussianBlur stdDeviation="5" result="blur" />
          <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
      </defs>
      <ellipse cx="160" cy="182" rx="121" ry="136" fill="url(#corvia-heart-core)" opacity=".78" />
      <path className="heart-body" d="M168 88c-18-29-51-36-76-18-31 22-39 69-23 109 22 57 78 103 98 120 7 6 17 6 24 0 22-19 75-67 94-126 14-44 1-91-34-108-27-13-58-4-73 23-2 3-8 3-10 0Z" fill="rgba(12,33,65,.78)" stroke="url(#corvia-heart-main)" strokeWidth="4.2" filter="url(#corvia-heart-glow)" />
      <path d="M151 91c-3-31 1-58 15-72 11-11 27-13 36-3 11 13 2 31-7 45-8 13-9 29-6 45" fill="none" stroke="#1ecff2" strokeWidth="8" strokeLinecap="round" opacity=".9" />
      <path d="M178 88c7-31 18-54 34-65 13-9 29-6 34 6 6 16-8 28-20 39-11 10-17 24-18 40" fill="none" stroke="#217bff" strokeWidth="7" strokeLinecap="round" opacity=".88" />
      <path d="M201 93c15-27 31-43 48-47 15-3 28 5 29 18 1 16-15 23-29 30-12 6-21 17-27 30" fill="none" stroke="#8d55ff" strokeWidth="7" strokeLinecap="round" opacity=".84" />
      <path d="M137 103c-19-17-43-23-59-15-15 7-20 24-10 36 10 11 26 8 40 5 13-3 27 0 40 9" fill="none" stroke="#26c8ff" strokeWidth="6" strokeLinecap="round" opacity=".8" />
      <path d="M110 133c36 22 56 44 60 72 4 30-3 57 5 84" fill="none" stroke="url(#corvia-heart-vein)" strokeWidth="3.4" strokeLinecap="round" filter="url(#corvia-heart-glow)" />
      <path d="M211 126c-30 25-45 52-43 84 2 25 16 45 11 77" fill="none" stroke="#ff4d73" strokeWidth="3" strokeLinecap="round" filter="url(#corvia-heart-glow)" />
      <path d="M96 174c22 4 42 14 58 31M91 205c27 2 48 11 66 27M214 158c-18 7-32 20-42 38M228 190c-24 7-39 22-52 43" fill="none" stroke="#55e7ff" strokeWidth="1.8" opacity=".82" />
      <circle cx="112" cy="137" r="5" fill="#4cecff" /><circle cx="205" cy="130" r="5" fill="#a878ff" /><circle cx="174" cy="207" r="5" fill="#ff5276" />
    </svg>
  );
}

export default function PreHomeBrand({
  title,
  description,
  benefits,
  trustTitle = "Ambiente seguro para uso profissional",
  trustText = "Dados protegidos. Decisões mais seguras.",
  celebratory = false,
}: Props) {
  return (
    <section className={`prehome-brand${celebratory ? " prehome-brand--celebratory" : ""}`}>
      <div className="prehome-brand__aurora prehome-brand__aurora--cyan" aria-hidden="true" />
      <div className="prehome-brand__aurora prehome-brand__aurora--violet" aria-hidden="true" />
      <div className="prehome-brand__network" aria-hidden="true"><i /><i /><i /><i /><i /><i /><i /><i /></div>

      <Link to="/" className="prehome-brand__logo" aria-label="CorVIA — página inicial">
        <img src="/corvia-mark-canonical.svg" alt="" aria-hidden="true" />
        <span><strong>CorVIA</strong><small>CLINICAL OS</small></span>
      </Link>

      <div className="prehome-brand__content">
        <div className="prehome-brand__copy">
          <span className="prehome-brand__badge">A PLATAFORMA Nº 1</span>
          <h1>Inteligência clínica<br />que <strong>transforma decisões.</strong></h1>
        </div>

        <div className="prehome-brand__pillars" aria-label="Pilares do CorVIA">
          {PILARES.map((pilar) => (
            <div className="prehome-pillar" key={pilar.title}>
              <span><Icone nome={pilar.icon} aria-hidden="true" /></span>
              <strong>{pilar.title}</strong>
              <small>{pilar.detail}</small>
            </div>
          ))}
        </div>

        <div className="prehome-brand__hologram" aria-hidden="true">
          <div className="prehome-brand__heart-glow" />
          <CoracaoHolografico />
          <svg className="prehome-brand__pulse" viewBox="0 0 260 42" focusable="false"><path d="M2 23h56l10-14 14 28 13-22 14 14 13-8h136" /></svg>
          <i className="prehome-brand__ring prehome-brand__ring--1" />
          <i className="prehome-brand__ring prehome-brand__ring--2" />
          <i className="prehome-brand__ring prehome-brand__ring--3" />
        </div>

        <div className="prehome-brand__journey">
          <p className="prehome-brand__journey-kicker">Jornada de acesso</p>
          <h2>{title}</h2>
          <p>{description}</p>
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
        <span><Icone nome="check" aria-hidden="true" /> LGPD</span>
        <span>Criptografia ponta a ponta</span>
        <span>Logs de auditoria</span>
      </footer>
    </section>
  );
}
