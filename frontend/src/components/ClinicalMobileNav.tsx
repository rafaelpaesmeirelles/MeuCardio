import { useEffect, useRef, useState } from "react";
import { NavLink } from "react-router-dom";
import { useAuth } from "../lib/auth";
import usePrescriptionQueueBadge from "../hooks/usePrescriptionQueueBadge";
import Icone, { type NomeIcone } from "./Icone";
import { IconeHoje } from "./IdentidadeClinica";

type LinkItem = { to: string; label: string; icon: NomeIcone; adminOnly?: boolean; badge?: number; featured?: boolean };
type MobileSection = { title: string; items: LinkItem[] };

const CLINICA_DECISAO: LinkItem[] = [
  { to: "/doencas", label: "Condições", icon: "doencas" },
  { to: "/medicamentos", label: "Medicamentos", icon: "medicamento" },
  { to: "/exames", label: "Exames", icon: "clinica" },
  { to: "/calculadoras", label: "Calculadoras", icon: "calculadora" },
  { to: "/interacoes", label: "Interações medicamentosas", icon: "medicamento" },
  { to: "/emergencia", label: "Emergências", icon: "emergencia" },
  { to: "/checklists", label: "Checklists", icon: "check" },
  { to: "/triagem-sintomas", label: "Triagem", icon: "triagem" },
  { to: "/condicoes", label: "Condições especiais", icon: "check" },
  { to: "/fluxogramas", label: "Fluxogramas", icon: "seta" },
  { to: "/avaliacao-preoperatoria", label: "Pré-operatório", icon: "clinica" },
];

const ESTUDO_EDUCACAO: LinkItem[] = [
  { to: "/evidencias", label: "Evidências", icon: "evidencia" },
  { to: "/estudos", label: "Estudos", icon: "evidencia" },
  { to: "/diretrizes", label: "Guidelines", icon: "conhecimento" },
  { to: "/trilhas/timeline", label: "Timeline", icon: "seta" },
  { to: "/trilhas", label: "Trilhas", icon: "seta" },
  { to: "/casos-clinicos", label: "Casos clínicos", icon: "doencas" },
  { to: "/biblioteca", label: "Biblioteca", icon: "conhecimento" },
  { to: "/galeria", label: "Atlas & Galeria", icon: "galeria" },
  { to: "/cursos", label: "Cursos", icon: "curso" },
  { to: "/material-paciente", label: "Material ao paciente", icon: "documento" },
];

const TRABALHO_ASSISTENCIA: LinkItem[] = [
  { to: "/prontuario?acao=ecg", label: "IA para ECG", icon: "ecg", featured: true },
  { to: "/prontuario", label: "Prontuário", icon: "pacientes" },
  { to: "/round", label: "Round hospitalar", icon: "pacientes" },
  { to: "/receituario", label: "Prescrição", icon: "prescricao" },
  { to: "/documentos", label: "Documentos", icon: "documento" },
  { to: "/corvia-mail", label: "CorVIA Mail", icon: "mail" },
  { to: "/assistente", label: "Assistente Clínica", icon: "assistente" },
  { to: "/telediagnostico", label: "Telediagnóstico", icon: "evidencia" },
];

const FERRAMENTAS: LinkItem[] = [
  { to: "/calculadoras", label: "Calculadoras avançadas", icon: "calculadora" },
  { to: "/indicadores", label: "Indicadores", icon: "indicadores" },
  { to: "/apresentacao", label: "Apresentação", icon: "documento" },
  { to: "/exportar", label: "Exportar PDF", icon: "documento" },
  { to: "/favoritos", label: "Notas & Favoritos", icon: "favorito" },
  { to: "/busca", label: "Busca avançada", icon: "busca" },
];

const REDE: LinkItem[] = [
  { to: "/usuarios-online", label: "Rede profissional", icon: "pacientes" },
  { to: "/sincronizacao", label: "Contas conectadas", icon: "sincronizar" },
  { to: "/telediagnostico", label: "Consultoria", icon: "evidencia" },
];

const CONTA_ADMIN: LinkItem[] = [
  { to: "/minha-conta", label: "Minha conta", icon: "conta" },
  { to: "/tour?origem=assinatura&modo=quick", label: "Tour CorVIA", icon: "check" },
  { to: "/privacidade", label: "Segurança & Privacidade", icon: "check" },
  { to: "/termos", label: "Termos", icon: "documento" },
  { to: "/tour", label: "Suporte & Ajuda", icon: "curso" },
  { to: "/admin", label: "Administração", icon: "gestao", adminOnly: true },
  { to: "/admin/usuarios", label: "Usuários & Permissões", icon: "pacientes", adminOnly: true },
  { to: "/fila-telediagnostico", label: "Fila telediagnóstico", icon: "evidencia", adminOnly: true },
  { to: "/receitas-para-assinatura", label: "Receitas para assinatura", icon: "prescricao", adminOnly: true },
];

export default function ClinicalMobileNav() {
  const { usuario } = useAuth();
  const [maisAberto, setMaisAberto] = useState(false);
  const pendentesAssinatura = usePrescriptionQueueBadge(usuario?.role === "admin");
  const triggerRef = useRef<HTMLButtonElement>(null);
  const closeRef = useRef<HTMLButtonElement>(null);
  const sheetRef = useRef<HTMLElement>(null);

  const contaAdmin=CONTA_ADMIN
    .filter(item=>item.to!=="/receitas-para-assinatura"||pendentesAssinatura!==undefined)
    .map(item=>item.to==="/receitas-para-assinatura"?{...item,badge:pendentesAssinatura}:item);

  const secoes: MobileSection[] = [
    { title: "Clínica & Decisão", items: CLINICA_DECISAO },
    { title: "Estudos & Educação", items: ESTUDO_EDUCACAO },
    { title: "Trabalho & Assistência", items: TRABALHO_ASSISTENCIA },
    { title: "Ferramentas & Produtividade", items: FERRAMENTAS },
    { title: "Rede & Conectividade", items: REDE },
    { title: "Administração & Conta", items: contaAdmin },
  ];

  function fecharMais(restaurar = true) { setMaisAberto(false); if (restaurar) requestAnimationFrame(() => triggerRef.current?.focus()); }

  function abrirAssistentePessoal() {
    setMaisAberto(false);
    requestAnimationFrame(() => {
      document.querySelector<HTMLButtonElement>(".cos-assistant-sidebar")?.click();
    });
  }

  useEffect(() => {
    document.body.classList.toggle("cc-mobile-more-open", maisAberto);
    if (!maisAberto) return () => document.body.classList.remove("cc-mobile-more-open");
    requestAnimationFrame(() => closeRef.current?.focus());
    function teclado(evento: KeyboardEvent) {
      if (evento.key === "Escape") { evento.preventDefault(); fecharMais(true); return; }
      if (evento.key !== "Tab") return;
      const elementos = Array.from(sheetRef.current?.querySelectorAll<HTMLElement>('a[href],button:not([disabled]),[tabindex]:not([tabindex="-1"])') ?? []).filter((elemento) => elemento.offsetParent !== null);
      if (!elementos.length) return;
      const primeiro = elementos[0]; const ultimo = elementos[elementos.length - 1];
      if (evento.shiftKey && document.activeElement === primeiro) { evento.preventDefault(); ultimo.focus(); }
      else if (!evento.shiftKey && document.activeElement === ultimo) { evento.preventDefault(); primeiro.focus(); }
    }
    document.addEventListener("keydown", teclado);
    return () => { document.removeEventListener("keydown", teclado); document.body.classList.remove("cc-mobile-more-open"); };
  }, [maisAberto]);

  function SheetLink({ item }: { item: LinkItem }) {
    return <NavLink to={item.to} className={item.featured ? "is-featured" : undefined} onClick={() => setMaisAberto(false)}><span><Icone nome={item.icon} /></span><strong>{item.label}{item.featured&&<small>Destaque</small>}{!!item.badge&&<span className="cos-account-menu__badge" aria-label={`${item.badge} pendentes`}>{item.badge}</span>}</strong></NavLink>;
  }

  return <>
    <nav className="cc-mobile-nav" aria-label="Navegação principal móvel">
      <NavLink to="/" end><IconeHoje /><span>Início</span></NavLink>
      <NavLink to="/busca"><Icone nome="busca" /><span>Buscar</span></NavLink>
      <NavLink to="/prontuario"><Icone nome="pacientes" /><span>Prontuário</span></NavLink>
      <NavLink to="/agenda"><Icone nome="agenda" /><span>Agenda</span></NavLink>
      <button ref={triggerRef} type="button" onClick={() => setMaisAberto(true)} aria-expanded={maisAberto}><Icone nome="mais" /><span>Mais</span></button>
    </nav>
    {maisAberto && <>
      <div className="cc-mobile-more-backdrop is-open" aria-hidden="true" onClick={() => fecharMais(true)} />
      <aside ref={sheetRef} className="cc-mobile-more is-open" role="dialog" aria-modal="true" aria-label="Todas as áreas do CorVIA">
        <header className="cc-mobile-more__head"><div><img src="/corvia-mark-canonical.svg" alt="" /><span><strong>CorVIA</strong><small>Clinical OS</small></span></div><button ref={closeRef} type="button" onClick={() => fecharMais(true)} aria-label="Fechar menu"><Icone nome="fechar" /></button></header>
        <button type="button" className="cc-mobile-more__assistant" onClick={abrirAssistentePessoal}><span className="cc-mobile-more__assistant-icon">✦</span><span><strong>Assistente Pessoal</strong><small>Agenda, deslocamentos e pendências</small></span><Icone nome="seta" /></button>
        {secoes.map((secao) => {
          const itens = secao.items.filter((item) => !item.adminOnly || usuario?.role === "admin");
          return <section key={secao.title} className="cc-mobile-more__section"><p>{secao.title}</p><div className="cc-mobile-more__grid">{itens.map((item) => <SheetLink key={`${secao.title}-${item.label}-${item.to}`} item={item} />)}</div></section>;
        })}
      </aside>
    </>}
  </>;
}

