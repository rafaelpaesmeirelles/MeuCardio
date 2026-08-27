import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { Link, useLocation } from "react-router-dom";
import Icone, { type NomeIcone } from "./Icone";
import { useAuth } from "../lib/auth";

type Acao = [id: string, to: string, titulo: string, icone: NomeIcone, tone: string, featured?: boolean];
const TODAS: Acao[] = [
  ["ecg-ia", "/exames-ia", "IA para Exames", "ecg", "green", true],
  ["tudo-com-tudo", "/busca?modo=tudo-com-tudo", "Tudo com Tudo", "busca", "cyan"],
  ["prescrever", "/receituario", "Prescrever", "prescricao", "cyan"],
  ["solicitar-exames", "/documentos", "Solicitar exames", "clinica", "blue"],
  ["calculadoras", "/calculadoras", "Calculadoras", "calculadora", "amber"],
  ["interacoes", "/interacoes", "Interações", "medicamento", "violet"],
  ["emergencias", "/emergencia", "Emergências", "emergencia", "red"],
  ["cardiologia-intensiva", "/cardiologia-intensiva", "Cardiologia Intensiva & UCO", "clinica", "cyan"],
  ["guidelines", "/diretrizes", "Guidelines", "conhecimento", "green"],
  ["corvia-ai", "/assistente", "CorVIA IA", "assistente", "blue"],
  ["documentos", "/documentos", "Documentos", "documento", "violet"],
  ["checklists", "/checklists", "Checklists", "check", "green"],
  ["triagem", "/triagem-sintomas", "Triagem", "triagem", "red"],
  ["pacientes", "/round", "Pacientes", "pacientes", "cyan"],
  ["medicamentos", "/medicamentos", "Medicamentos", "medicamento", "violet"],
  ["agenda", "/agenda", "Agenda", "agenda", "blue"],
  ["evidencias", "/evidencias", "Evidências", "evidencia", "cyan"],
];
const POR_ID = new Map(TODAS.map((a) => [a[0], a]));
const N_DESKTOP = 10;
const PADRAO_DESKTOP = TODAS.slice(0, N_DESKTOP).map((a) => a[0]);
const PADRAO_MOBILE = [
  "calculadoras", "corvia-ai", "emergencias", "guidelines",
  "ecg-ia", "prescrever", "solicitar-exames", "tudo-com-tudo",
];

function ordenarAlfabeticamente(ids: string[]) {
  return [...ids].sort((a, b) =>
    (POR_ID.get(a)?.[2] ?? a).localeCompare(POR_ID.get(b)?.[2] ?? b, "pt-BR", { sensitivity: "base" })
  );
}

function normalizar(valor: unknown, desktop: boolean) {
  const ids = Array.isArray(valor) ? [...new Set(valor.filter((id): id is string => typeof id === "string" && POR_ID.has(id)))] : [];
  if (!desktop) {
    return ids.length >= 4 && ids.length % 4 === 0 ? ordenarAlfabeticamente(ids) : PADRAO_MOBILE;
  }
  if (ids.length !== N_DESKTOP) return PADRAO_DESKTOP;
  return ids.includes("ecg-ia") ? ids : ["ecg-ia", ...ids].slice(0, N_DESKTOP);
}

export default function HomeQuickActionsPersonalizer() {
  const { pathname } = useLocation();
  const { usuario } = useAuth();
  const [desktop, setDesktop] = useState(() => matchMedia("(min-width:901px)").matches);
  const [alvos, setAlvos] = useState<{ a: HTMLElement; h: HTMLElement } | null>(null);
  const [selecionadas, setSelecionadas] = useState<string[]>(() =>
    matchMedia("(min-width:901px)").matches ? PADRAO_DESKTOP : PADRAO_MOBILE
  );
  const [rascunho, setRascunho] = useState<string[]>(() =>
    matchMedia("(min-width:901px)").matches ? PADRAO_DESKTOP : PADRAO_MOBILE
  );
  const [aberto, setAberto] = useState(false);
  const chave = usuario?.id
    ? desktop ? `corvia:acoes-rapidas:${usuario.id}` : `corvia:acoes-rapidas-mobile-v2:${usuario.id}`
    : "";
  const padrao = desktop ? PADRAO_DESKTOP : PADRAO_MOBILE;
  const selecaoValida = desktop
    ? rascunho.length === N_DESKTOP
    : rascunho.length >= 4 && rascunho.length % 4 === 0;

  useEffect(() => {
    const media = matchMedia("(min-width:901px)"), atualizar = () => setDesktop(media.matches);
    // iOS/iPadOS antigos expõem MediaQueryList.addListener, mas não
    // addEventListener. Uma exceção neste efeito desmontava a raiz logo após
    // o login do primeiro acesso.
    if (typeof media.addEventListener === "function") {
      media.addEventListener("change", atualizar);
      return () => media.removeEventListener("change", atualizar);
    }
    media.addListener(atualizar);
    return () => media.removeListener(atualizar);
  }, []);

  useEffect(() => {
    if (!chave) return setSelecionadas(padrao);
    try { setSelecionadas(normalizar(JSON.parse(localStorage.getItem(chave) || "[]"), desktop)); } catch { setSelecionadas(padrao); }
  }, [chave, desktop]);

  useEffect(() => {
    setAlvos(null);
    if (pathname !== "/") return;
    let raf = 0, a: HTMLElement | null = null, h: HTMLElement | null = null;
    const localizar = () => {
      a = document.querySelector(".ccc-actions-section .ccc-actions");
      h = document.querySelector(".ccc-actions-section .ccc-section__head");
      if (!a || !h) return void (raf = requestAnimationFrame(localizar));
      a.classList.add("qa-active"); h.classList.add("qa-head-active"); setAlvos({ a, h });
    };
    localizar();
    return () => { cancelAnimationFrame(raf); a?.classList.remove("qa-active"); h?.classList.remove("qa-head-active"); };
  }, [pathname]);

  const alternar = (id: string) => setRascunho((a) => {
    if (a.includes(id)) return a.filter((x) => x !== id);
    if (desktop && a.length >= N_DESKTOP) return a;
    return desktop ? [...a, id] : ordenarAlfabeticamente([...a, id]);
  });
  const mover = (id: string, passo: -1 | 1) => setRascunho((a) => {
    const i = a.indexOf(id), j = i + passo;
    if (i < 0 || j < 0 || j >= a.length) return a;
    const b = [...a]; [b[i], b[j]] = [b[j], b[i]]; return b;
  });
  const salvar = () => {
    if (!selecaoValida) return;
    const novas = desktop ? [...rascunho] : ordenarAlfabeticamente(rascunho);
    setSelecionadas(novas);
    if (chave) try { localStorage.setItem(chave, JSON.stringify(novas)); } catch { /* preferência local */ }
    setAberto(false);
  };

  if (!alvos) return null;
  return <>
    {createPortal((desktop ? selecionadas : ordenarAlfabeticamente(selecionadas)).map((id) => {
      const acao = POR_ID.get(id); if (!acao) return null;
      const [, to, titulo, icone, tone, featured] = acao;
      return <Link to={to} key={id} className={`ccc-action qa-action ccc-action--${icone}${featured ? " is-featured" : ""}`} data-tone={tone}>{featured && <em className="ccc-action__featured">Destaque</em>}<span className="ccc-action__icon"><Icone nome={icone} /></span><strong>{titulo}</strong></Link>;
    }), alvos.a)}
    {createPortal(<button type="button" className="qa-edit" onClick={() => { setRascunho([...selecionadas]); setAberto(true); }}><Icone nome="configuracao" /> Personalizar</button>, alvos.h)}
    {aberto && createPortal(<div className="qa-modal" onMouseDown={() => setAberto(false)}><section className="qa-dialog" role="dialog" aria-modal="true" aria-labelledby="qa-title" onMouseDown={(e) => e.stopPropagation()}>
      <header className="qa-head"><span><h2 id="qa-title">Personalizar ações rápidas</h2>{!desktop && <small>Escolha 4, 8, 12 ou 16 itens. A ordem será alfabética.</small>}</span><button type="button" aria-label="Fechar" onClick={() => setAberto(false)}>×</button></header>
      <div className="qa-list">{TODAS.map(([id,, titulo, icone]) => {
        const i = rascunho.indexOf(id), ativa = i >= 0;
        return <div className="qa-item" key={id}><button type="button" className="qa-toggle" disabled={(desktop && id === "ecg-ia") || (desktop && !ativa && rascunho.length >= N_DESKTOP)} onClick={() => alternar(id)}><Icone nome={icone} /><strong>{titulo}</strong>{desktop && id === "ecg-ia" && <small>Destaque fixo</small>}</button>{desktop && ativa && <span className="qa-order"><button type="button" disabled={i === 0} onClick={() => mover(id, -1)}>↑</button><button type="button" disabled={i === rascunho.length - 1} onClick={() => mover(id, 1)}>↓</button></span>}</div>;
      })}</div>
      <footer className="qa-foot"><span>{desktop ? `${rascunho.length}/${N_DESKTOP}` : `${rascunho.length} itens · ${rascunho.length / 4 || 0} fileira(s)`}</span><button type="button" onClick={() => setRascunho([...padrao])}>Padrão</button><button type="button" onClick={() => setAberto(false)}>Cancelar</button><button type="button" className="qa-save" disabled={!selecaoValida} onClick={salvar}>Salvar</button></footer>
    </section></div>, document.body)}
  </>;
}
