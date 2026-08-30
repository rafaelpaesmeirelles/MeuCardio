import type { NomeIcone } from "../components/Icone";

export type ClinicalContextAction = {
  to: string;
  label: string;
  detail: string;
  icon: NomeIcone;
};

export type ClinicalNavigationContext = {
  key: string;
  title: string;
  detail: string;
  icon: NomeIcone;
  actions: ClinicalContextAction[];
};

const contexts: Array<{ prefixes: string[]; context: ClinicalNavigationContext }> = [
  {
    prefixes: ["/medicamentos", "/interacoes"],
    context: { key: "farmacologia", title: "Farmacologia clínica", detail: "Medicamentos, segurança e ação", icon: "medicamento", actions: [
      { to: "/interacoes", label: "Interações", detail: "Revisar segurança", icon: "medicamento" },
      { to: "/evidencias", label: "Evidências", detail: "Conferir recomendações", icon: "evidencia" },
      { to: "/receituario", label: "Prescrição", detail: "Levar para a prática", icon: "prescricao" },
    ] },
  },
  {
    prefixes: ["/doencas", "/triagem-sintomas", "/condicoes", "/calculadoras"],
    context: { key: "decisao", title: "Decisão clínica", detail: "Doença, triagem e conduta", icon: "doencas", actions: [
      { to: "/diretrizes", label: "Diretrizes", detail: "Conduta recomendada", icon: "evidencia" },
      { to: "/calculadoras", label: "Escores", detail: "Estratificar risco", icon: "calculadora" },
      { to: "/medicamentos", label: "Medicamentos", detail: "Explorar tratamento", icon: "medicamento" },
    ] },
  },
  {
    prefixes: ["/evidencias", "/estudos", "/diretrizes", "/biblioteca", "/trilhas", "/cursos", "/casos-clinicos"],
    context: { key: "ciencia", title: "Conhecimento científico", detail: "Evidência, estudo e aplicação", icon: "conhecimento", actions: [
      { to: "/busca", label: "Tudo com Tudo", detail: "Cruzar o tema", icon: "busca" },
      { to: "/favoritos", label: "Favoritos", detail: "Salvar e retomar", icon: "favorito" },
      { to: "/assistente", label: "Assistente", detail: "Discutir o contexto", icon: "assistente" },
    ] },
  },
  {
    prefixes: ["/exames-ia", "/ecg-ia", "/exames", "/galeria"],
    context: { key: "diagnostico", title: "Diagnóstico", detail: "Exames, achados e critérios", icon: "clinica", actions: [
      { to: "/doencas", label: "Doenças", detail: "Relacionar achados", icon: "doencas" },
      { to: "/calculadoras", label: "Critérios", detail: "Aplicar escores", icon: "calculadora" },
      { to: "/favoritos", label: "Favoritos", detail: "Guardar referência", icon: "favorito" },
    ] },
  },
  {
    prefixes: ["/prontuario", "/round"],
    context: { key: "paciente", title: "Contexto do paciente", detail: "Registro e continuidade do cuidado", icon: "pacientes", actions: [
      { to: "/receituario", label: "Prescrever", detail: "Abrir receituário", icon: "prescricao" },
      { to: "/documentos", label: "Documentos", detail: "Gerar solicitações", icon: "documento" },
      { to: "/agenda", label: "Agenda", detail: "Organizar seguimento", icon: "agenda" },
    ] },
  },
  {
    prefixes: ["/receituario", "/documentos", "/avaliacao-preoperatoria"],
    context: { key: "producao", title: "Produção clínica", detail: "Prescrição, documentos e solicitações", icon: "documento", actions: [
      { to: "/prontuario", label: "Prontuário", detail: "Retomar paciente", icon: "pacientes" },
      { to: "/agenda", label: "Agenda", detail: "Programar continuidade", icon: "agenda" },
      { to: "/corvia-mail", label: "CorVIA Mail", detail: "Comunicar com segurança", icon: "mail" },
    ] },
  },
  {
    prefixes: ["/agenda", "/corvia-mail", "/caixa-de-email", "/usuarios-online", "/telediagnostico"],
    context: { key: "coordenacao", title: "Coordenação do cuidado", detail: "Agenda, comunicação e colaboração", icon: "agenda", actions: [
      { to: "/prontuario", label: "Prontuário", detail: "Abrir contexto clínico", icon: "pacientes" },
      { to: "/documentos", label: "Documentos", detail: "Resolver pendências", icon: "documento" },
      { to: "/assistente", label: "Assistente", detail: "Organizar próximos passos", icon: "assistente" },
    ] },
  },
  {
    prefixes: ["/emergencia", "/cardiologia-intensiva", "/checklists", "/fluxogramas"],
    context: { key: "agudo", title: "Decisão em cenário agudo", detail: "Protocolos, fluxos e segurança", icon: "emergencia", actions: [
      { to: "/fluxogramas", label: "Fluxogramas", detail: "Seguir algoritmo", icon: "seta" },
      { to: "/checklists", label: "Checklists", detail: "Confirmar etapas", icon: "check" },
      { to: "/calculadoras", label: "Escores", detail: "Estratificar risco", icon: "calculadora" },
    ] },
  },
  {
    prefixes: ["/favoritos"],
    context: { key: "favoritos", title: "Favoritos", detail: "Referências clínicas salvas", icon: "favorito", actions: [
      { to: "/busca", label: "Buscar", detail: "Encontrar novo conteúdo", icon: "busca" },
      { to: "/biblioteca", label: "Biblioteca", detail: "Explorar documentos", icon: "conhecimento" },
      { to: "/medicamentos", label: "Medicamentos", detail: "Abrir farmacologia", icon: "medicamento" },
    ] },
  },
  {
    prefixes: ["/busca"],
    context: { key: "busca", title: "Tudo com Tudo", detail: "Busca clínica conectada", icon: "busca", actions: [
      { to: "/favoritos", label: "Favoritos", detail: "Retomar referências", icon: "favorito" },
      { to: "/evidencias", label: "Evidências", detail: "Filtrar recomendações", icon: "evidencia" },
      { to: "/biblioteca", label: "Biblioteca", detail: "Explorar o acervo", icon: "conhecimento" },
    ] },
  },
];

const fallback: ClinicalNavigationContext = {
  key: "workspace",
  title: "Clinical Command Center",
  detail: "Conhecimento, decisão e assistência",
  icon: "clinica",
  actions: [
    { to: "/busca", label: "Tudo com Tudo", detail: "Pesquisar o acervo", icon: "busca" },
    { to: "/favoritos", label: "Favoritos", detail: "Retomar conteúdo", icon: "favorito" },
    { to: "/assistente", label: "Assistente", detail: "Perguntar no contexto", icon: "assistente" },
  ],
};

export function getClinicalNavigationContext(pathname: string) {
  return contexts.find(({ prefixes }) => prefixes.some((prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`)))?.context ?? fallback;
}

export function getContextActions(pathname: string) {
  return getClinicalNavigationContext(pathname).actions.filter(({ to }) => {
    const path = to.split("?")[0];
    return pathname !== path && !pathname.startsWith(`${path}/`);
  });
}

export function commandDestination(value: string) {
  const term = value.trim();
  const normalized = term.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLocaleLowerCase("pt-BR");
  const commands: Array<[RegExp, string]> = [
    [/\b(ecg|eletrocardiograma|holter|mapa|ecocardiograma|ressonancia|tomografia|exame cardiovascular)\b/, "/exames-ia"],
    [/\b(prescrev\w*|prescri\w*|receit\w*)\b/, "/receituario"],
    [/\b(atestado|documento|relatorio|encaminhamento|solicitar exames?|pedido de exames?)\b/, "/documentos"],
    [/\b(calcul\w*|escore\w*|score\w*)\b/, "/calculadoras"],
    [/\b(emergencia|urgencia)\b/, "/emergencia"],
    [/\b(interacao|interacoes)\b/, "/interacoes"],
    [/\b(favorit\w*|salvos?)\b/, "/favoritos"],
    [/\b(agenda|compromisso)\b/, "/agenda"],
    [/\b(prontuario|paciente)\b/, "/prontuario"],
    [/\b(round|internados?)\b/, "/round"],
    [/\b(e-?mail|corvia mail|mensagem)\b/, "/corvia-mail"],
    [/\b(minha conta|perfil|configuracao)\b/, "/minha-conta"],
  ];
  return commands.find(([pattern]) => pattern.test(normalized))?.[1] ?? `/busca?q=${encodeURIComponent(term)}`;
}
