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

const PILARES: Array<{ icon: NomeIcone; label: string; line2: string }> = [
  { icon: "assistente", label: "Inteligência", line2: "Artificial" },
  { icon: "check", label: "Evidências", line2: "atualizadas" },
  { icon: "sincronizar", label: "Tudo com", line2: "Tudo" },
  { icon: "conta", label: "Segurança", line2: "e Privacidade" },
];

export default function PreHomeBrand({ title, description }: Props) {
  return (
    <section className="prehome-brand prehome-showcase" aria-label="CorVIA Clinical OS">
      <div className="prehome-showcase__badge">A PLATAFORMA Nº 1</div>
      <h1>Inteligência clínica<br />que <strong>transforma decisões</strong></h1>
      <div className="prehome-showcase__pillars">
        {PILARES.map((p) => (
          <span key={p.label}><Icone nome={p.icon} /><small>{p.label}<br />{p.line2}</small></span>
        ))}
      </div>
      <img className="prehome-showcase__art" src="/corvia-prehome-showcase.svg" alt="" aria-hidden="true" />
      <div className="prehome-showcase__context" aria-hidden="true"><span>{title}</span><small>{description}</small></div>
    </section>
  );
}
