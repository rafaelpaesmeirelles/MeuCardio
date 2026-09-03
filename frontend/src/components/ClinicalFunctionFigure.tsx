import type { FunctionalSpace, RouteGroup } from "../lib/clinicalRouteRegistry";
import Icone, { type NomeIcone } from "./Icone";
import "../styles/cardiology-function-figure.css";

type FigureComposition = "monitor" | "workflow" | "knowledge" | "network";

type GroupFigureDefinition = {
  composition: FigureComposition;
  motifs: readonly [NomeIcone, NomeIcone];
};

const FALLBACK_FIGURE: GroupFigureDefinition = {
  composition: "network",
  motifs: ["clinica", "sincronizar"],
};

/**
 * Complementos visuais por família funcional. `satisfies` transforma a união
 * RouteGroup em contrato: uma nova família clínica não pode ficar sem figura.
 */
const GROUP_FIGURES = {
  documentos: { composition: "workflow", motifs: ["documento", "check"] },
  pacientes: { composition: "monitor", motifs: ["pacientes", "ecg"] },
  prescricao: { composition: "workflow", motifs: ["prescricao", "medicamento"] },
  agenda: { composition: "workflow", motifs: ["agenda", "relogio"] },
  mail: { composition: "network", motifs: ["mail", "comunicacao"] },
  assistente: { composition: "network", motifs: ["assistente", "sincronizar"] },
  integracoes: { composition: "network", motifs: ["sincronizar", "check"] },
  conhecimento: { composition: "knowledge", motifs: ["evidencia", "conhecimento"] },
  ferramentas: { composition: "monitor", motifs: ["ecg", "check"] },
  emergencia: { composition: "monitor", motifs: ["emergencia", "ecg"] },
  rede: { composition: "network", motifs: ["pacientes", "comunicacao"] },
  telediagnostico: { composition: "monitor", motifs: ["ecg", "comunicacao"] },
  conta: { composition: "workflow", motifs: ["conta", "configuracao"] },
  admin: { composition: "network", motifs: ["indicadores", "gestao"] },
  geral: FALLBACK_FIGURE,
} satisfies Record<RouteGroup, GroupFigureDefinition>;

function figureForGroup(group: RouteGroup): GroupFigureDefinition {
  // O fallback também protege a renderização caso um valor externo inválido
  // atravesse o limite em runtime, sem enfraquecer a cobertura tipada acima.
  return GROUP_FIGURES[group] ?? FALLBACK_FIGURE;
}

export default function ClinicalFunctionFigure({
  icon,
  group,
  space,
}: {
  icon: NomeIcone;
  group: RouteGroup;
  space: FunctionalSpace;
}) {
  const { composition, motifs } = figureForGroup(group);

  return (
    <div
      className="cv-function-figure"
      data-composition={composition}
      data-function-group={group}
      data-function-space={space}
      aria-hidden="true"
    >
      <svg
        className="cv-function-figure__diagram"
        viewBox="0 0 460 116"
        preserveAspectRatio="none"
        aria-hidden="true"
        focusable="false"
      >
        <g className="cv-function-figure__grid">
          <path d="M12 22H448M12 58H448M12 94H448" />
          <path d="M76 8V108M166 8V108M256 8V108M346 8V108" />
        </g>
        <path
          className="cv-function-figure__trace"
          d="M6 67h72l9-8 10 15 14-31 17 48 15-26h38l10-6 11 8h41l12-18 13 34 16-22h65l12-8 13 14h80"
        />
        <path
          className="cv-function-figure__flow"
          d="M24 29h76c24 0 20 28 45 28h43c25 0 22-24 49-24h47c28 0 26 49 56 49h95"
        />
        <g className="cv-function-figure__nodes">
          <circle cx="100" cy="29" r="3" />
          <circle cx="188" cy="57" r="3" />
          <circle cx="284" cy="33" r="3" />
          <circle cx="340" cy="82" r="3" />
          <circle cx="435" cy="82" r="3" />
        </g>
      </svg>

      <span className="cv-function-figure__motif cv-function-figure__motif--one">
        <Icone nome={motifs[0]} />
      </span>
      <span className="cv-function-figure__motif cv-function-figure__motif--two">
        <Icone nome={motifs[1]} />
      </span>

      <span className="cv-function-figure__primary">
        <span><Icone nome={icon} /></span>
        <i /><i /><i />
      </span>

      <span className="cv-function-figure__data-card">
        <i /><i /><i /><i />
      </span>
    </div>
  );
}
