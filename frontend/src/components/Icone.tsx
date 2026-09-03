import type { ReactNode, SVGProps } from "react";

export type NomeIcone =
  | "hoje" | "clinica" | "pacientes" | "conhecimento" | "comunicacao"
  | "gestao" | "agenda" | "busca" | "emergencia" | "menu" | "fechar"
  | "chevron" | "mail" | "prescricao" | "documento" | "triagem"
  | "assistente" | "doencas" | "calculadora" | "medicamento" | "round"
  | "evidencia" | "curso" | "galeria" | "favorito" | "conta" | "sair"
  | "indicadores" | "check" | "mais" | "seta" | "pin" | "rota"
  | "relogio" | "sincronizar" | "filtro" | "configuracao" | "olho" | "olho-fechado"
  | "adicionar" | "notificacao" | "ecg" | "camera" | "sol" | "lua";

const caminhos: Record<NomeIcone, ReactNode> = {
  hoje: <><path d="M3 11.5 12 4l9 7.5"/><path d="M5.5 10.5V20h13v-9.5M9 20v-6h6v6"/></>,
  clinica: <><path d="M6 3v5a4 4 0 0 0 8 0V3"/><path d="M4 3h4M12 3h4M10 16a5 5 0 0 0 10 0v-2"/><circle cx="20" cy="11.5" r="2"/></>,
  pacientes: <><circle cx="9" cy="8" r="3"/><circle cx="17" cy="9" r="2.5"/><path d="M3.5 20v-2.5A4.5 4.5 0 0 1 8 13h2a4.5 4.5 0 0 1 4.5 4.5V20M14 14.5a4 4 0 0 1 6.5 3V20"/></>,
  conhecimento: <><path d="M4 5.5A3.5 3.5 0 0 1 7.5 2H11v17H7.5A3.5 3.5 0 0 0 4 22Z"/><path d="M20 5.5A3.5 3.5 0 0 0 16.5 2H13v17h3.5A3.5 3.5 0 0 1 20 22Z"/></>,
  comunicacao: <path d="M4 4h16v12H8l-4 4Z"/>,
  gestao: <><path d="M4 20V10h4v10M10 20V4h4v16M16 20v-7h4v7"/><path d="M2 20h20"/></>,
  agenda: <><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M7 3v4M17 3v4M3 10h18"/></>,
  busca: <><circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/></>,
  emergencia: <path d="M9.5 3h5v6.5H21v5h-6.5V21h-5v-6.5H3v-5h6.5Z"/>,
  menu: <path d="M4 7h16M4 12h16M4 17h16"/>,
  fechar: <path d="m6 6 12 12M18 6 6 18"/>,
  chevron: <path d="m9 7 5 5-5 5"/>,
  mail: <><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m4 7 8 6 8-6"/></>,
  prescricao: <><path d="M5 3h10l4 4v14H5Z"/><path d="M14 3v5h5M8 13h8M8 17h5"/></>,
  documento: <><path d="M6 2h9l4 4v16H6Z"/><path d="M14 2v5h5M9 12h7M9 16h7"/></>,
  triagem: <><path d="M9 4h6M12 1v6"/><path d="M5 8h14v13H5Z"/><path d="m8 15 2 2 5-5"/></>,
  assistente: <><path d="M4 6h16v11H8l-4 4Z"/><path d="M8 10h8M8 13h5"/></>,
  ecg: <><path d="M3 12h4l2-5 4 10 2-5h6"/><path d="M5 4.5h14a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-11a2 2 0 0 1 2-2Z"/></>,
  camera: <><path d="M4 7h3l1.5-2h7L17 7h3a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V9a2 2 0 0 1 2-2Z"/><circle cx="12" cy="13" r="4"/></>,
  sol: <><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.42 1.42M17.65 17.65l1.42 1.42M2 12h2M20 12h2M4.93 19.07l1.42-1.42M17.65 6.35l1.42-1.42"/></>,
  lua: <path d="M20.2 15.2A8.4 8.4 0 0 1 8.8 3.8 8.6 8.6 0 1 0 20.2 15.2Z"/>,
  doencas: <><path d="M3 12h4l2-5 4 10 2-5h6"/><path d="M12 21C7 18 3 15 3 10a5 5 0 0 1 9-3 5 5 0 0 1 9 3c0 5-4 8-9 11Z"/></>,
  calculadora: <><rect x="5" y="2" width="14" height="20" rx="2"/><path d="M8 6h8M8 11h1M12 11h1M16 11h1M8 15h1M12 15h1M16 15h1M8 19h1M12 19h5"/></>,
  medicamento: <><path d="m7 17 10-10a4 4 0 0 0-6-6L1 11a4 4 0 0 0 6 6Z"/><path d="m7 7 10 10"/></>,
  round: <><path d="M3 19V8h18v11M3 14h18M7 8V5h5a3 3 0 0 1 3 3"/><path d="M5 19v2M19 19v2"/></>,
  evidencia: <><path d="M5 3h14v18H5Z"/><path d="M8 8h8M8 12h8M8 16h5"/></>,
  curso: <><path d="m2 9 10-5 10 5-10 5Z"/><path d="M6 11v5c3 2 9 2 12 0v-5"/></>,
  galeria: <><rect x="3" y="4" width="18" height="16" rx="2"/><circle cx="9" cy="9" r="2"/><path d="m4 17 5-5 4 4 3-3 4 4"/></>,
  favorito: <path d="m12 3 2.8 5.7 6.2.9-4.5 4.4 1.1 6.2-5.6-3-5.6 3 1.1-6.2L3 9.6l6.2-.9Z"/>,
  conta: <><circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/></>,
  sair: <><path d="M10 4H4v16h6M14 8l4 4-4 4M8 12h10"/></>,
  indicadores: <><path d="M4 20V9M10 20V4M16 20v-7M22 20H2"/></>,
  check: <path d="m5 12 4 4L19 6"/>,
  mais: <><circle cx="5" cy="12" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/></>,
  seta: <path d="M5 12h14M13 6l6 6-6 6"/>,
  pin: <><path d="M20 10c0 5-8 12-8 12S4 15 4 10a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="2.5"/></>,
  rota: <><circle cx="6" cy="18" r="2"/><circle cx="18" cy="6" r="2"/><path d="M8 18h3a3 3 0 0 0 3-3v-6a3 3 0 0 1 3-3"/></>,
  relogio: <><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></>,
  sincronizar: <><path d="M20 7h-5V2"/><path d="M20 7a8 8 0 0 0-14-2M4 17h5v5"/><path d="M4 17a8 8 0 0 0 14 2"/></>,
  filtro: <path d="M3 5h18l-7 8v6l-4 2v-8Z"/>,
  configuracao: <><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1-2.8 2.8-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.6v.2h-4V21a1.7 1.7 0 0 0-1-1.6 1.7 1.7 0 0 0-1.9.3l-.1.1L4.2 17l.1-.1a1.7 1.7 0 0 0 .3-1.9A1.7 1.7 0 0 0 3 14H2.8v-4H3a1.7 1.7 0 0 0 1.6-1 1.7 1.7 0 0 0-.3-1.9L4.2 7 7 4.2l.1.1A1.7 1.7 0 0 0 9 4.6a1.7 1.7 0 0 0 1-1.6v-.2h4V3a1.7 1.7 0 0 0 1 1.6 1.7 1.7 0 0 0 1.9-.3l.1-.1L19.8 7l-.1.1a1.7 1.7 0 0 0-.3 1.9 1.7 1.7 0 0 0 1.6 1h.2v4H21a1.7 1.7 0 0 0-1.6 1Z"/></>,
  olho: <><path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></>,
  "olho-fechado": <><path d="M3 3l18 18"/><path d="M10.6 5.2A10.8 10.8 0 0 1 12 5c6.4 0 10 7 10 7a17.9 17.9 0 0 1-3.5 4.5M6.6 6.6C3.8 8.4 2 12 2 12s3.6 7 10 7a10 10 0 0 0 3.4-.6"/><path d="M9.9 10a3 3 0 0 0 4.2 4.2"/></>,
  adicionar: <path d="M12 5v14M5 12h14"/>,
  notificacao: <><path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9"/><path d="M10 21h4"/></>,
};

export default function Icone({ nome, ...props }: { nome: NomeIcone } & SVGProps<SVGSVGElement>) {
  return <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" focusable="false" {...props}>{caminhos[nome]}</svg>;
}
