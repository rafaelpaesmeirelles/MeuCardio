import type { ReactNode, SVGProps } from "react";

/** Símbolo próprio da página Hoje: casa, coração e pulso clínico usando
 * exclusivamente as três cores de identidade da CorvIA. */
export function IconeHoje(props: SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 48 48" aria-hidden="true" focusable="false" {...props}>
      <path d="M7 22.5 24 8l17 14.5v17a3 3 0 0 1-3 3H10a3 3 0 0 1-3-3Z" fill="#fff" stroke="#6fd0d9" strokeWidth="3" strokeLinejoin="round" />
      <path d="M24 37.5S14 31.2 14 24.7c0-3.3 2.5-5.7 5.6-5.7 1.8 0 3.4.9 4.4 2.3 1-1.4 2.6-2.3 4.4-2.3 3.1 0 5.6 2.4 5.6 5.7 0 6.5-10 12.8-10 12.8Z" fill="#d5001d" />
      <path d="M17 27h4l2-4 2.4 7 2-4H31" fill="none" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

/** Marca de acesso imediato: o círculo vermelho recupera a leitura visual do
 * primeiro atalho do Modo Emergência e o pulso o integra à família CorvIA. */
export function IconeEmergencia(props: SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 48 48" aria-hidden="true" focusable="false" {...props}>
      <circle cx="24" cy="24" r="22" fill="#d5001d" />
      <path d="M20 10h8v10h10v8H28v10h-8V28H10v-8h10Z" fill="#fff" />
      <path d="M9 25h8l2.5-5 3.8 10 3.2-7 2.4 2H39" fill="none" stroke="#0b2e45" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export type AreaClinicaMarca = "pediatrica" | "neonatal" | "congenita" | "geriatria" | "gestacao" | "oncologia";

const simbolos: Record<AreaClinicaMarca, ReactNode> = {
  pediatrica: (
    <>
      <circle cx="16" cy="15" r="5" />
      <path d="M8 35c.8-7 4-11 8-11s7.2 4 8 11M31 35s-8-5.2-8-11a5.5 5.5 0 0 1 10-3.2A5.5 5.5 0 0 1 43 24c0 5.8-12 11-12 11Z" />
    </>
  ),
  neonatal: (
    <>
      <path d="M24 39S8 29.6 8 18.5A8.5 8.5 0 0 1 24 14a8.5 8.5 0 0 1 16 4.5C40 29.6 24 39 24 39Z" />
      <path d="M17 23h5l2-5 3 10 2.2-5H34M12 9l1.2 2.5L16 13l-2.8 1.4L12 17l-1.2-2.6L8 13l2.8-1.5Z" />
    </>
  ),
  congenita: (
    <>
      <path d="M24 40S8 30.6 8 19.5A8.5 8.5 0 0 1 24 15a8.5 8.5 0 0 1 16 4.5C40 30.6 24 40 24 40Z" />
      <path d="M24 15v25M16 25h16M18 18c3 4 3 8 0 12M30 18c-3 4-3 8 0 12" />
    </>
  ),
  geriatria: (
    <>
      <path d="M25 39S10 30 10 20a8 8 0 0 1 15-4.2A8 8 0 0 1 40 20c0 10-15 19-15 19Z" />
      <path d="M9 38c0-10 3-16 8-18M9 38h7M17 20v18M14 28h6" />
    </>
  ),
  gestacao: (
    <>
      <circle cx="20" cy="11" r="4" />
      <path d="M19 16c-5 4-6 15-2 23M20 17c12 1 14 16 4 20M13 39h16" />
      <path d="M27 31s-6-3.7-6-8a3.5 3.5 0 0 1 6-2.4 3.5 3.5 0 0 1 6 2.4c0 4.3-6 8-6 8Z" />
    </>
  ),
  oncologia: (
    <>
      <path d="M19 9c7 2 12 7 12 13 0 8-8 15-16 18 5-7 7-12 6-18-.7-4-2-8-2-13Z" />
      <path d="M29 9c-7 2-12 7-12 13 0 5 3 10 9 14M11 25h7l2-4 3 8 2-4h9" />
    </>
  ),
};

export function AreaClinicaIcone({ area, ...props }: { area: AreaClinicaMarca } & SVGProps<SVGSVGElement>) {
  return (
    <svg viewBox="0 0 48 48" fill="none" stroke="currentColor" strokeWidth="2.35" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" focusable="false" {...props}>
      {simbolos[area]}
    </svg>
  );
}
