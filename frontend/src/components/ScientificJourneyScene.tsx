import { useId } from "react";
import Icone, { type NomeIcone } from "./Icone";

export type ScientificJourney = "descobrir" | "evidencias" | "aprender" | "ensinar" | "produzir";
const icons: Record<ScientificJourney, NomeIcone> = {
  descobrir: "descobrir", evidencias: "validar-evidencia", aprender: "aprender", ensinar: "ensinar", produzir: "produzir",
};

/** Purpose-built vector portals: their symbols stay crisp in both themes and
 * at mobile sizes, with no extra image download or reused clinical room. */
export default function ScientificJourneyScene({ journey }: { journey: ScientificJourney }) {
  const id = useId().replaceAll(":", "");
  return <svg className="spaces-science-scene" viewBox="0 0 320 200" aria-hidden="true" focusable="false" data-journey={journey}>
    <defs>
      <radialGradient id={`${id}-halo`}><stop stopColor="currentColor" stopOpacity=".2" /><stop offset="1" stopColor="currentColor" stopOpacity="0" /></radialGradient>
      <linearGradient id={`${id}-glass`} x2="1" y2="1"><stop className="spaces-science-scene__glass" /><stop offset="1" className="spaces-science-scene__glass-end" /></linearGradient>
    </defs>
    <rect width="320" height="200" className="spaces-science-scene__background" />
    <ellipse cx="160" cy="104" rx="154" ry="102" fill={`url(#${id}-halo)`} />
    <g fill="none" stroke="currentColor" strokeWidth=".7" opacity=".23">
      <path d="M0 166h320M0 190l160-63 160 63M60 200l100-73 100 73M160 127v73" />
      <ellipse cx="160" cy="148" rx="110" ry="28" /><ellipse cx="160" cy="148" rx="79" ry="17" />
      <path d="M24 44v-20h32M264 24h32v20M24 134v20h24M272 154h24v-20" />
    </g>
    <g fill={`url(#${id}-glass)`} stroke="currentColor" strokeWidth=".8">
      <rect x="103" y="29" width="114" height="122" rx="22" />
      <rect x="48" y="65" width="41" height="59" rx="7" opacity=".45" transform="rotate(-9 68 95)" />
      <rect x="231" y="65" width="41" height="59" rx="7" opacity=".45" transform="rotate(9 252 95)" />
    </g>
    <g stroke="currentColor" strokeWidth="1.2" fill="none" opacity=".5">
      <path d="M59 82h18M59 90h13M59 99h16M243 83h18M243 91h12M243 100h16" />
      <path d="M89 95h14M217 95h14" strokeDasharray="2 4" />
    </g>
    <Icone nome={icons[journey]} x="121" y="49" width="78" height="78" strokeWidth="1.15" className="spaces-science-scene__symbol" />
    <g fill="currentColor"><circle cx="70" cy="36" r="2" opacity=".5" /><circle cx="256" cy="43" r="1.5" opacity=".6" /><circle cx="286" cy="120" r="1" opacity=".7" /></g>
  </svg>;
}
