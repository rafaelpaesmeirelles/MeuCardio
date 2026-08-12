import { useState } from "react";
import { Link } from "react-router-dom";
import Icone from "../components/Icone";
import ClinicalCommandCenter from "./ClinicalCommandCenter";

const ACOES_MOBILE = [
  { to: "/receituario", rotulo: "Prescrever", icone: "prescricao" as const },
  { to: "/documentos", rotulo: "Solicitar exames", icone: "documento" as const },
  { to: "/calculadoras", rotulo: "Calculadoras", icone: "calculadora" as const },
  { to: "/emergencia", rotulo: "Emergência", icone: "emergencia" as const },
  { to: "/medicamentos", rotulo: "Medicamentos", icone: "medicamento" as const },
  { to: "/diretrizes", rotulo: "Guidelines", icone: "evidencia" as const },
];

export default function LaunchHome() {
  const [acoesAbertas, setAcoesAbertas] = useState(false);

  return (
    <>
      <ClinicalCommandCenter />

      <div className="launch-mobile-dock" aria-label="Comandos rápidos do CorVIA">
        <button
          type="button"
          className={`launch-mobile-dock__action${acoesAbertas ? " ativo" : ""}`}
          onClick={() => setAcoesAbertas((valor) => !valor)}
          aria-expanded={acoesAbertas}
          aria-controls="launch-mobile-actions"
        >
          <span><Icone nome="mais" /></span>
          <strong>Agir</strong>
        </button>
        <Link className="launch-mobile-dock__assistant" to="/assistente">
          <span><Icone nome="assistente" /></span>
          <span><strong>Assistente Pessoal</strong><small>Agenda · deslocamento · rotina</small></span>
          <Icone nome="chevron" />
        </Link>
      </div>

      <div
        className={`launch-mobile-actions-backdrop${acoesAbertas ? " ativo" : ""}`}
        onClick={() => setAcoesAbertas(false)}
        aria-hidden="true"
      />
      <section
        id="launch-mobile-actions"
        className={`launch-mobile-actions${acoesAbertas ? " ativo" : ""}`}
        aria-label="Ações rápidas"
        aria-hidden={!acoesAbertas}
      >
        <header>
          <div>
            <p>CorVIA · Ação</p>
            <strong>O que você precisa fazer agora?</strong>
          </div>
          <button type="button" onClick={() => setAcoesAbertas(false)} aria-label="Fechar ações rápidas">
            <Icone nome="fechar" />
          </button>
        </header>
        <div className="launch-mobile-actions__grid">
          {ACOES_MOBILE.map((acao) => (
            <Link key={acao.to + acao.rotulo} to={acao.to} onClick={() => setAcoesAbertas(false)}>
              <span><Icone nome={acao.icone} /></span>
              <strong>{acao.rotulo}</strong>
            </Link>
          ))}
        </div>
        <Link className="launch-mobile-actions__assistant" to="/assistente" onClick={() => setAcoesAbertas(false)}>
          <Icone nome="assistente" />
          <span><strong>Abrir Assistente Pessoal</strong><small>Continue sua rotina sem perder o contexto.</small></span>
          <Icone nome="seta" />
        </Link>
      </section>
    </>
  );
}
