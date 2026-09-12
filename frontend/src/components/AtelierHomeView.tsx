import { useEffect, useRef, useState, type FormEvent, type ReactNode, type RefObject } from "react";
import { Link } from "react-router-dom";
import Icone, { type NomeIcone } from "./Icone";
import CorviaThemeSelector from "./CorviaThemeSelector";
import { useAuth } from "../lib/auth";
import { atelierRecentContext } from "../lib/atelierNavigation";

type Space = { id: string; label: string; description: string; icon: NomeIcone };
type Mode = "complete" | "essential" | "scientific";
type Props = {
  spaces: Space[]; active: Space; mode: Mode; interior: boolean;
  onSelect: (id: string) => void; onEnter: () => void; onBack: () => void;
  onMode: (mode: Mode) => void; onCatalog: () => void; onPersonalize: () => void;
  query: string; onQuery: (value: string) => void; onSearch: (event: FormEvent<HTMLFormElement>) => void;
  searchRef: RefObject<HTMLInputElement>; identity: ReactNode; children: ReactNode;
};

/** Architectural navigation only. Clinical data and workflows stay in their real pages. */
export default function AtelierHomeView(props: Props) {
  const { usuario, sair } = useAuth();
  const accountRef = useRef<HTMLDetailsElement>(null);
  useEffect(() => {
    const close = (event: KeyboardEvent | PointerEvent) => {
      const account = accountRef.current;
      if (!account?.open) return;
      if (event instanceof KeyboardEvent && event.key === "Escape") {
        account.open = false;
        account.querySelector("summary")?.focus();
      } else if (event instanceof PointerEvent && !account.contains(event.target as Node)) account.open = false;
    };
    document.addEventListener("keydown", close);
    document.addEventListener("pointerdown", close);
    return () => { document.removeEventListener("keydown", close); document.removeEventListener("pointerdown", close); };
  }, []);
  const [recent] = useState<{ path: string; title: string } | null>(() => {
    try {
      const values: unknown = JSON.parse(sessionStorage.getItem(`corvia:contextos-recentes:${usuario?.id}`) || "[]");
      if (!Array.isArray(values)) return null;
      for (const value of values) {
        const candidate = atelierRecentContext(value, usuario?.role === "admin", window.location.origin);
        if (candidate) return candidate;
      }
      return null;
    } catch { return null; }
  });
  const organization = <label className="atelier-organization"><span>Organização</span><select aria-label="Modo de trabalho" value={props.mode} onChange={(event) => props.onMode(event.target.value as Mode)}><option value="complete">Completo</option><option value="essential">Essencial</option><option value="scientific">Ciência & Ensino</option></select></label>;
  return <>
    <header className="atelier-header">
      <button type="button" className="atelier-brand" onClick={props.onBack} aria-label="CorVIA — escolher espaço"><img src="/atelier/corvia-logo-atelier.svg" alt="CorVIA Cardiology Spaces" /></button>
      <form className="atelier-search" role="search" onSubmit={props.onSearch}><Icone nome="busca" /><input ref={props.searchRef} aria-label="Buscar no Tudo com Tudo" placeholder="Tudo com Tudo — conhecimento e funções" value={props.query} onChange={(event) => props.onQuery(event.target.value)} /><button aria-label="Buscar" type="submit"><Icone nome="seta" /></button></form>
      <button type="button" className="atelier-catalog-trigger" onClick={props.onCatalog}><Icone nome="mais" /><span>Todas as funções</span></button>
      <details ref={accountRef} className="atelier-account"><summary aria-label={`Menu da conta de ${usuario?.full_name || "usuário"}`}>{props.identity}</summary><div><CorviaThemeSelector variant="menu" /><Link to="/minha-conta">Minha conta</Link><Link to="/corvia-mail">CorVIA Mail</Link><Link to="/favoritos">Favoritos</Link>{usuario?.role === "admin" && <Link to="/admin">Administração</Link>}<Link to="/tour">Conhecer a plataforma</Link><button type="button" onClick={() => void sair()}>Sair</button></div></details>
    </header>
    {!props.interior ? <section className="atelier-arrival" aria-labelledby="atelier-home-title">
      <header className="atelier-arrival__heading"><p>CARDIOLOGY SPACES</p><h1 id="atelier-home-title">Onde você vai trabalhar agora?</h1><span>Os espaços de trabalho mudam. O CorVIA permanece ao seu lado.</span></header>
      <nav className="atelier-mobile-spaces" aria-label="Escolher ambiente">{props.spaces.map((space) => <button key={space.id} type="button" aria-pressed={space.id === props.active.id} onClick={() => props.onSelect(space.id)}>{space.label}</button>)}</nav>
      <div className="atelier-portals">{props.spaces.map((space, index) => <button type="button" className={`atelier-portal${space.id === props.active.id ? " is-selected" : ""}`} key={space.id} onClick={() => props.onSelect(space.id)} aria-pressed={space.id === props.active.id} aria-label={`Selecionar ${space.label}`}>
        <img src={`/atelier/atelier-${space.id}-small.webp`} srcSet={`/atelier/atelier-${space.id}-small.webp 640w, /atelier/atelier-${space.id}.webp 1536w`} sizes="(max-width: 700px) 100vw, 24vw" alt={`Interior do espaço ${space.label}`} loading={space.id === props.active.id ? "eager" : "lazy"} />
        <span className="atelier-portal__number">0{index + 1}</span><span className="atelier-portal__label"><Icone nome={space.icon} /><strong>{space.label}</strong></span>{space.id === props.active.id && <span className="atelier-portal__selected"><Icone nome="check" />Selecionado</span>}
      </button>)}</div>
      <div className="atelier-entry"><div className="atelier-entry__identity"><span><Icone nome={props.active.icon} /></span><div><h2>{props.active.label}</h2><p>{props.active.description}</p></div></div><div className="atelier-entry__actions">{organization}<button type="button" className="atelier-primary" onClick={props.onEnter}>Entrar no {props.active.label}<Icone nome="seta" /></button></div></div>
      <footer className="atelier-arrival__footer"><span>Seu repertório, suas ferramentas, seu ritmo.</span>{recent && <Link to={recent.path}>Retomar {recent.title}<Icone nome="seta" /></Link>}</footer>
    </section> : <section className="atelier-space" aria-label={`Espaço ${props.active.label}`}>
      <nav className="atelier-space__breadcrumb"><button type="button" onClick={props.onBack}><Icone nome="chevron" />Trocar de ambiente</button><span>{props.active.label}</span></nav>
      <header className="atelier-space__hero"><img src={`/atelier/atelier-${props.active.id}.webp`} srcSet={`/atelier/atelier-${props.active.id}-small.webp 640w, /atelier/atelier-${props.active.id}.webp 1536w`} sizes="(max-width: 700px) 100vw, 90vw" alt={`Arquitetura do ${props.active.label}`} /><div><p>SEU ESPAÇO DE TRABALHO</p><h1>{props.active.label}</h1><span>{props.active.description}</span></div></header>
      <header className="atelier-shelf-toolbar"><h2>Suas ferramentas</h2><div>{organization}<button type="button" onClick={props.onCatalog}>Todas as funções</button><button type="button" onClick={props.onPersonalize}><Icone nome="configuracao" />Personalizar</button></div></header>
      {props.children}
    </section>}
  </>;
}
