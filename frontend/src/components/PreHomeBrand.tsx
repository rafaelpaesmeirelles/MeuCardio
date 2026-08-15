import type { ReactNode } from "react";
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

const PILARES: Array<{ icon: NomeIcone; label: string }> = [
  { icon: "assistente", label: "Inteligência\nArtificial" },
  { icon: "check", label: "Evidências\natualizadas" },
  { icon: "sincronizar", label: "Tudo com\nTudo" },
  { icon: "conta", label: "Segurança\ne Privacidade" },
];

const ACOES: Array<{ icon: NomeIcone; label: string; tone: string }> = [
  { icon: "prescricao", label: "Prescrever", tone: "green" },
  { icon: "clinica", label: "Exames", tone: "violet" },
  { icon: "calculadora", label: "Calculadoras", tone: "blue" },
  { icon: "emergencia", label: "Emergências", tone: "red" },
  { icon: "medicamento", label: "Medicamentos", tone: "teal" },
  { icon: "conhecimento", label: "Guidelines", tone: "amber" },
];

function HeartVisual() {
  return (
    <svg className="prehome-showcase__heart" viewBox="0 0 360 390" aria-hidden="true" focusable="false">
      <defs>
        <linearGradient id="heartStroke" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#37a7ff" />
          <stop offset="0.56" stopColor="#7f74ff" />
          <stop offset="1" stopColor="#ff3d62" />
        </linearGradient>
        <radialGradient id="heartGlow" cx="50%" cy="48%" r="58%">
          <stop offset="0" stopColor="#2b7cff" stopOpacity=".35" />
          <stop offset=".55" stopColor="#173b73" stopOpacity=".12" />
          <stop offset="1" stopColor="#08111f" stopOpacity="0" />
        </radialGradient>
        <filter id="heartBlur"><feGaussianBlur stdDeviation="9" /></filter>
      </defs>
      <ellipse cx="180" cy="198" rx="145" ry="148" fill="url(#heartGlow)" filter="url(#heartBlur)" />
      <path className="heart-major" d="M174 92c-11-43 17-69 45-72 25-2 42 14 49 37 8 25 3 50-7 67 30 11 51 37 48 73-4 49-33 92-74 132-21 20-44 35-57 44-13-10-37-28-59-50-39-39-67-82-66-131 1-39 26-69 59-79-11-19-15-40-9-61 7-25 26-41 49-40 29 1 52 25 52 59" fill="rgba(8,20,38,.86)" stroke="url(#heartStroke)" strokeWidth="4.5" />
      <path d="M151 112c-5-31-2-69 20-88m26 86c4-39 24-73 47-84m-60 105c-29 13-48 41-45 75 4 39 31 72 61 101m2-169c28 4 51 29 54 60 4 37-16 68-43 98" fill="none" stroke="#4b8eff" strokeOpacity=".82" strokeWidth="3" />
      <path d="M118 134c24 4 42 18 55 37m-65 13c29-1 51 11 69 32m-53 28c23-6 49 0 70 16m37-118c-16 22-27 48-29 76m66-51c-22 13-37 31-48 56m39 13c-20 8-38 21-53 40" fill="none" stroke="#ff4866" strokeOpacity=".72" strokeWidth="2.2" />
      <g fill="#53b9ff">
        <circle cx="145" cy="155" r="4" /><circle cx="169" cy="187" r="3" /><circle cx="127" cy="219" r="3" /><circle cx="205" cy="153" r="3" /><circle cx="229" cy="202" r="4" /><circle cx="194" cy="257" r="3" />
      </g>
      <g fill="#ff5a76"><circle cx="214" cy="132" r="3" /><circle cx="236" cy="174" r="3" /><circle cx="219" cy="239" r="3" /></g>
    </svg>
  );
}

function MiniCommandCenter() {
  return (
    <div className="prehome-mini" aria-hidden="true">
      <aside className="prehome-mini__side">
        <b>CorVIA</b><small>CLINICAL OS</small>
        {[["hoje", "Página inicial"], ["pacientes", "Pacientes"], ["agenda", "Agenda"], ["documento", "Prontuários"], ["prescricao", "Prescrever"], ["clinica", "Exames"]].map(([icon, text], i) => (
          <span className={i === 0 ? "is-active" : ""} key={text}><Icone nome={icon as NomeIcone} />{text}</span>
        ))}
      </aside>
      <div className="prehome-mini__main">
        <div className="prehome-mini__search">⌕ &nbsp; Buscar pacientes, doenças, diretrizes, medicamentos...</div>
        <div className="prehome-mini__actions">{ACOES.map((a) => <i data-tone={a.tone} key={a.label}><Icone nome={a.icon} /><small>{a.label}</small></i>)}</div>
        <section className="prehome-mini__route">
          <div><small>DESLOCAMENTO</small><p>● Origem: Clínica CorVIA</p><p>● Destino: Hospital</p><strong>23 min</strong><em>via Av. Paulista</em></div>
          <div className="prehome-mini__map"><i /><b /><span /></div>
        </section>
        <div className="prehome-mini__tiles"><span>SEU CORVIA</span><span>TUDO COM TUDO</span><span>CORVIA INTELLIGENCE</span><span>ASSISTENTE</span></div>
      </div>
    </div>
  );
}

export default function PreHomeBrand({ title, description }: Props) {
  return (
    <section className="prehome-brand prehome-showcase" aria-label="CorVIA Clinical OS">
      <div className="prehome-showcase__badge">A PLATAFORMA Nº 1</div>
      <h1>Inteligência clínica<br />que <strong>transforma decisões</strong></h1>
      <div className="prehome-showcase__pillars">
        {PILARES.map((p) => <span key={p.label}><Icone nome={p.icon} /><small>{p.label.split("\n").map((part, i) => <span key={part}>{part}{i === 0 && <br />}</span>)}</small></span>)}
      </div>
      <div className="prehome-showcase__visual">
        <div className="prehome-showcase__network" aria-hidden="true"><i /><i /><i /><i /><i /><i /></div>
        <HeartVisual />
      </div>
      <MiniCommandCenter />
      <div className="prehome-showcase__context" aria-hidden="true"><span>{title}</span><small>{description}</small></div>
    </section>
  );
}
