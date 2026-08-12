import { useEffect, useRef, useState } from "react";
import { NavLink } from "react-router-dom";
import { useAuth } from "../lib/auth";
import Icone, { type NomeIcone } from "./Icone";
import { IconeHoje } from "./IdentidadeClinica";

type LinkItem = { to: string; label: string; icon: NomeIcone };

const CLINICA: LinkItem[] = [
  { to: "/doencas", label: "Condições", icon: "doencas" },
  { to: "/medicamentos", label: "Medicamentos", icon: "medicamento" },
  { to: "/exames", label: "Exames", icon: "clinica" },
  { to: "/evidencias", label: "Evidências", icon: "evidencia" },
  { to: "/estudos", label: "Estudos", icon: "evidencia" },
  { to: "/diretrizes", label: "Guidelines", icon: "conhecimento" },
  { to: "/calculadoras", label: "Calculadoras", icon: "calculadora" },
  { to: "/emergencia", label: "Emergências", icon: "emergencia" },
  { to: "/checklists", label: "Checklists", icon: "check" },
  { to: "/casos-clinicos", label: "Casos clínicos", icon: "doencas" },
  { to: "/trilhas", label: "Trilhas", icon: "seta" },
];

const TRABALHO: LinkItem[] = [
  { to: "/receituario", label: "Prescrição", icon: "prescricao" },
  { to: "/documentos", label: "Documentos", icon: "documento" },
  { to: "/corvia-mail", label: "CorVIA Mail", icon: "mail" },
  { to: "/usuarios-online", label: "Rede profissional", icon: "pacientes" },
  { to: "/favoritos", label: "Favoritos", icon: "favorito" },
];

export default function ClinicalMobileNav() {
  const { usuario } = useAuth();
  const [maisAberto, setMaisAberto] = useState(false);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const closeRef = useRef<HTMLButtonElement>(null);
  const sheetRef = useRef<HTMLElement>(null);

  function abrirAssistente() {
    setMaisAberto(false);
    window.dispatchEvent(new Event("corvia:abrir-assistente-pessoal"));
  }

  function fecharMais(restaurar = true) {
    setMaisAberto(false);
    if (restaurar) requestAnimationFrame(() => triggerRef.current?.focus());
  }

  useEffect(() => {
    document.body.classList.toggle("cc-mobile-more-open", maisAberto);
    if (!maisAberto) return () => document.body.classList.remove("cc-mobile-more-open");

    requestAnimationFrame(() => closeRef.current?.focus());
    function teclado(evento: KeyboardEvent) {
      if (evento.key === "Escape") {
        evento.preventDefault();
        fecharMais(true);
        return;
      }
      if (evento.key !== "Tab") return;
      const elementos = Array.from(
        sheetRef.current?.querySelectorAll<HTMLElement>('a[href],button:not([disabled]),[tabindex]:not([tabindex="-1"])') ?? [],
      ).filter((elemento) => elemento.offsetParent !== null);
      if (!elementos.length) return;
      const primeiro = elementos[0];
      const ultimo = elementos[elementos.length - 1];
      if (evento.shiftKey && document.activeElement === primeiro) {
        evento.preventDefault();
        ultimo.focus();
      } else if (!evento.shiftKey && document.activeElement === ultimo) {
        evento.preventDefault();
        primeiro.focus();
      }
    }
    document.addEventListener("keydown", teclado);
    return () => {
      document.removeEventListener("keydown", teclado);
      document.body.classList.remove("cc-mobile-more-open");
    };
  }, [maisAberto]);

  function SheetLink({ item }: { item: LinkItem }) {
    return (
      <NavLink to={item.to} onClick={() => setMaisAberto(false)}>
        <span><Icone nome={item.icon} /></span>
        <strong>{item.label}</strong>
      </NavLink>
    );
  }

  return (
    <>
      <button
        type="button"
        className="cc-mobile-menu-trigger"
        onClick={() => setMaisAberto(true)}
        aria-label="Abrir menu do CorVIA"
        aria-expanded={maisAberto}
      >
        <Icone nome="menu" />
      </button>

      <nav className="cc-mobile-nav" aria-label="Navegação principal móvel">
        <NavLink to="/" end>
          <IconeHoje />
          <span>Início</span>
        </NavLink>
        <NavLink to="/busca">
          <Icone nome="busca" />
          <span>Buscar</span>
        </NavLink>
        <NavLink to="/round">
          <Icone nome="pacientes" />
          <span>Pacientes</span>
        </NavLink>
        <NavLink to="/agenda">
          <Icone nome="agenda" />
          <span>Agenda</span>
        </NavLink>
        <button ref={triggerRef} type="button" onClick={() => setMaisAberto(true)} aria-expanded={maisAberto}>
          <Icone nome="mais" />
          <span>Mais</span>
        </button>
      </nav>

      <div className={`cc-mobile-more-backdrop${maisAberto ? " is-open" : ""}`} aria-hidden="true" onClick={() => fecharMais(true)} />
      <aside ref={sheetRef} className={`cc-mobile-more${maisAberto ? " is-open" : ""}`} aria-hidden={!maisAberto} aria-label="Mais áreas do CorVIA">
        <header className="cc-mobile-more__head">
          <div><img src="/corvia-logo-compacta.png" alt="" /><span><strong>CorVIA</strong><small>Clinical OS do médico</small></span></div>
          <button ref={closeRef} type="button" onClick={() => fecharMais(true)} aria-label="Fechar menu"><Icone nome="fechar" /></button>
        </header>

        <button type="button" className="cc-mobile-more__assistant" onClick={abrirAssistente}>
          <span className="cc-mobile-more__spark">✦</span>
          <span><strong>Assistente Pessoal</strong><small>Agenda, deslocamento, pendências e briefing</small></span>
          <Icone nome="seta" />
        </button>

        <section className="cc-mobile-more__section">
          <p>Clínica</p>
          <div className="cc-mobile-more__grid">
            {CLINICA.map((item) => <SheetLink key={item.to} item={item} />)}
          </div>
        </section>

        <section className="cc-mobile-more__section">
          <p>Trabalho e conta</p>
          <div className="cc-mobile-more__grid">
            {TRABALHO.map((item) => <SheetLink key={item.to} item={item} />)}
            <SheetLink item={{ to: "/material-paciente", label: "Material ao paciente", icon: "documento" }} />
            <SheetLink item={{ to: "/galeria", label: "Galeria", icon: "galeria" }} />
            <SheetLink item={{ to: "/sincronizacao", label: "Contas conectadas", icon: "sincronizar" }} />
            <SheetLink item={{ to: "/minha-conta", label: "Minha conta", icon: "conta" }} />
            {usuario?.role === "admin" && <SheetLink item={{ to: "/admin", label: "Administração", icon: "gestao" }} />}
          </div>
        </section>
      </aside>
    </>
  );
}
