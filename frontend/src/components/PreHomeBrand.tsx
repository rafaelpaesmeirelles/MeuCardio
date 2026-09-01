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

export function CoracaoHolografico() {
  return (
    <svg className="prehome-brand__heart" viewBox="0 0 360 420" role="img" aria-label="Coração anatômico digital do CorVIA">
      <defs>
        <linearGradient id="corvia-anatomy-main" x1=".12" y1=".08" x2=".88" y2=".94">
          <stop offset="0" stopColor="#1be3ee" />
          <stop offset=".31" stopColor="#148eff" />
          <stop offset=".58" stopColor="#4a67ff" />
          <stop offset=".78" stopColor="#9b5cf7" />
          <stop offset="1" stopColor="#ff416c" />
        </linearGradient>
        <linearGradient id="corvia-anatomy-red" x1=".1" y1="0" x2=".75" y2="1">
          <stop offset="0" stopColor="#ff8aa0" />
          <stop offset=".45" stopColor="#ff476e" />
          <stop offset="1" stopColor="#ff214f" />
        </linearGradient>
        <linearGradient id="corvia-anatomy-blue" x1=".12" y1="0" x2=".75" y2="1">
          <stop offset="0" stopColor="#62f1ff" />
          <stop offset=".48" stopColor="#168eff" />
          <stop offset="1" stopColor="#3557ff" />
        </linearGradient>
        <radialGradient id="corvia-anatomy-core" cx="54%" cy="49%" r="56%">
          <stop offset="0" stopColor="#f94570" stopOpacity=".30" />
          <stop offset=".42" stopColor="#245bff" stopOpacity=".13" />
          <stop offset="1" stopColor="#03101f" stopOpacity="0" />
        </radialGradient>
        <filter id="corvia-anatomy-glow" x="-80%" y="-80%" width="260%" height="260%">
          <feGaussianBlur stdDeviation="4.5" result="blur" />
          <feMerge><feMergeNode in="blur" /><feMergeNode in="SourceGraphic" /></feMerge>
        </filter>
        <filter id="corvia-anatomy-soft" x="-80%" y="-80%" width="260%" height="260%">
          <feGaussianBlur stdDeviation="12" />
        </filter>
      </defs>

      <ellipse cx="184" cy="236" rx="132" ry="145" fill="url(#corvia-anatomy-core)" opacity=".95" />
      <ellipse cx="183" cy="356" rx="108" ry="24" fill="#1d75ff" opacity=".13" filter="url(#corvia-anatomy-soft)" />

      {/* vasos da base e grandes vasos */}
      <path d="M160 129C143 99 143 64 160 41c11-15 29-20 42-12 16 10 15 31 6 47-10 18-16 38-11 61" fill="none" stroke="url(#corvia-anatomy-blue)" strokeWidth="14" strokeLinecap="round" filter="url(#corvia-anatomy-glow)" />
      <path d="M197 124c4-34 15-70 39-91 17-15 40-14 50 1 11 17 0 37-17 51-19 15-31 34-35 56" fill="none" stroke="url(#corvia-anatomy-red)" strokeWidth="15" strokeLinecap="round" filter="url(#corvia-anatomy-glow)" />
      <path d="M225 141c17-35 38-57 63-62 20-4 37 8 38 25 1 20-19 29-37 36-15 6-27 17-35 32" fill="none" stroke="#9c5fff" strokeWidth="12" strokeLinecap="round" opacity=".92" filter="url(#corvia-anatomy-glow)" />
      <path d="M139 139c-27-23-56-30-77-19-19 10-24 31-11 46 13 15 34 9 51 6 18-3 35 2 51 14" fill="none" stroke="#28d8ef" strokeWidth="11" strokeLinecap="round" opacity=".90" filter="url(#corvia-anatomy-glow)" />

      {/* massa miocárdica anatômica assimétrica */}
      <path d="M172 127c-36-18-82-5-103 29-21 35-13 79 8 112 18 29 43 48 63 71 14 16 23 36 31 55 3 8 14 9 19 2 17-24 38-46 57-69 26-31 48-68 52-109 4-39-13-78-47-94-26-12-56-8-80 3Z" fill="rgba(5,24,45,.88)" stroke="url(#corvia-anatomy-main)" strokeWidth="4.3" filter="url(#corvia-anatomy-glow)" />
      <path d="M171 135c-17 22-27 47-28 75-2 51 30 93 38 142 7-35 3-75 19-106 14-27 39-44 68-55-14-35-44-61-79-64-7 0-13 3-18 8Z" fill="rgba(255,55,91,.055)" stroke="#ff5275" strokeWidth="1.5" opacity=".88" />
      <path d="M166 139c-35-11-69 4-83 32-13 27-5 59 12 83 18 25 42 43 57 70-4-36-13-72-7-107 5-31 14-55 21-78Z" fill="rgba(26,144,255,.055)" stroke="#2bcff1" strokeWidth="1.4" opacity=".86" />

      {/* septo e coronárias principais */}
      <path d="M172 148c-9 32-8 65 2 96 12 36 11 74 8 112" fill="none" stroke="#ff4a70" strokeWidth="3.8" strokeLinecap="round" filter="url(#corvia-anatomy-glow)" />
      <path d="M166 150c-19 21-29 47-30 76-1 35 15 69 22 103" fill="none" stroke="#31dbee" strokeWidth="3.2" strokeLinecap="round" filter="url(#corvia-anatomy-glow)" />
      <path d="M173 173c23 5 44 18 58 38 15 21 23 49 21 76" fill="none" stroke="#ff5878" strokeWidth="2.8" strokeLinecap="round" />
      <path d="M165 184c-25 4-45 17-58 37-11 18-16 39-14 61" fill="none" stroke="#3fe4f2" strokeWidth="2.6" strokeLinecap="round" />
      <path d="M188 221c25 10 42 28 52 51M151 231c-22 8-37 23-46 43M195 254c19 9 31 22 39 39M149 268c-17 8-29 20-37 34M189 291c16 10 25 21 31 34M157 306c-12 7-21 16-27 26" fill="none" stroke="#7eefff" strokeWidth="1.6" opacity=".68" />

      {/* veias e artérias superficiais */}
      <path d="M114 159c17 8 31 20 41 36M91 190c23 6 42 19 56 38M263 169c-22 7-42 23-55 43M277 205c-25 8-45 24-58 45" fill="none" stroke="#4fb7ff" strokeWidth="1.8" opacity=".65" />
      <path d="M208 142c8 20 8 39 2 58" fill="none" stroke="#ff657f" strokeWidth="3" opacity=".85" />

      <g filter="url(#corvia-anatomy-glow)">
        <circle cx="146" cy="187" r="4" fill="#52edff" />
        <circle cx="207" cy="205" r="4" fill="#ff5679" />
        <circle cx="184" cy="258" r="4" fill="#a66eff" />
        <circle cx="130" cy="274" r="3" fill="#54e9f7" />
        <circle cx="229" cy="277" r="3" fill="#ff4d72" />
      </g>
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
        <span><strong><span className="corvia-word-cor">Cor</span><span className="corvia-via">VIA</span></strong><small>CARDIOLOGY SPACES</small></span>
      </Link>

      <div className="prehome-brand__content">
        <div className="prehome-brand__copy">
          <span className="prehome-brand__badge">CARDIOLOGY SPACES</span>
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
