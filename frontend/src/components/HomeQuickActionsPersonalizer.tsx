import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { Link, useLocation } from "react-router-dom";
import Icone, { type NomeIcone } from "./Icone";
import { useAuth } from "../lib/auth";

type Acao = [id: string, to: string, titulo: string, icone: NomeIcone, tone: string, featured?: boolean];
const N = 10;
const TODAS: Acao[] = [
  ["ecg-ia", "/prontuario?acao=ecg", "IA para ECG", "ecg", "green", true],
  ["prescrever", "/receituario", "Prescrever", "prescricao", "cyan"],
  ["solicitar-exames", "/documentos", "Solicitar exames", "clinica", "blue"],
  ["calculadoras", "/calculadoras", "Calculadoras", "calculadora", "amber"],
  ["interacoes", "/interacoes", "Interações", "medicamento", "violet"],
  ["emergencias", "/emergencia", "Emergências", "emergencia", "red"],
  ["guidelines", "/diretrizes", "Guidelines", "conhecimento", "green"],
  ["corvia-ai", "/assistente", "CorVIA AI", "assistente", "blue"],
  ["documentos", "/documentos", "Documentos", "documento", "violet"],
  ["checklists", "/checklists", "Checklists", "check", "green"],
  ["triagem", "/triagem-sintomas", "Triagem", "triagem", "red"],
  ["pacientes", "/round", "Pacientes", "pacientes", "cyan"],
  ["medicamentos", "/medicamentos", "Medicamentos", "medicamento", "violet"],
  ["agenda", "/agenda", "Agenda", "agenda", "blue"],
  ["evidencias", "/evidencias", "Evidências", "evidencia", "cyan"],
];
const POR_ID = new Map(TODAS.map((a) => [a[0], a]));
const PADRAO = TODAS.slice(0, N).map((a) => a[0]);

function normalizar(valor: unknown) {
  const ids = Array.isArray(valor) ? [...new Set(valor.filter((id): id is string => typeof id === "string" && POR_ID.has(id)))] : [];
  if (ids.length !== N) return PADRAO;
  return ids.includes("ecg-ia") ? ids : ["ecg-ia", ...ids].slice(0, N);
}

export default function HomeQuickActionsPersonalizer() {
  const { pathname } = useLocation();
  const { usuario } = useAuth();
  const [desktop, setDesktop] = useState(() => matchMedia("(min-width:901px)").matches);
  const [alvos, setAlvos] = useState<{ a: HTMLElement; h: HTMLElement } | null>(null);
  const [selecionadas, setSelecionadas] = useState<string[]>(PADRAO);
  const [rascunho, setRascunho] = useState<string[]>(PADRAO);
  const [aberto, setAberto] = useState(false);
  const chave = usuario?.id ? `corvia:acoes-rapidas:${usuario.id}` : "";

  useEffect(() => {
    const media = matchMedia("(min-width:901px)"), atualizar = () => setDesktop(media.matches);
    media.addEventListener("change", atualizar);
    return () => media.removeEventListener("change", atualizar);
  }, []);

  useEffect(() => {
    if (!chave) return setSelecionadas(PADRAO);
    try { setSelecionadas(normalizar(JSON.parse(localStorage.getItem(chave) || "[]"))); } catch { setSelecionadas(PADRAO); }
  }, [chave]);

  useEffect(() => {
    setAlvos(null);
    if (pathname !== "/" || !desktop) return;
    let raf = 0, a: HTMLElement | null = null, h: HTMLElement | null = null;
    const localizar = () => {
      a = document.querySelector(".ccc-actions-section .ccc-actions");
      h = document.querySelector(".ccc-actions-section .ccc-section__head");
      if (!a || !h) return void (raf = requestAnimationFrame(localizar));
      a.classList.add("qa-active"); h.classList.add("qa-head-active"); setAlvos({ a, h });
    };
    localizar();
    return () => { cancelAnimationFrame(raf); a?.classList.remove("qa-active"); h?.classList.remove("qa-head-active"); };
  }, [desktop, pathname]);

  const alternar = (id: string) => setRascunho((a) => a.includes(id) ? a.filter((x) => x !== id) : a.length < N ? [...a, id] : a);
  const mover = (id: string, passo: -1 | 1) => setRascunho((a) => {
    const i = a.indexOf(id), j = i + passo;
    if (i < 0 || j < 0 || j >= a.length) return a;
    const b = [...a]; [b[i], b[j]] = [b[j], b[i]]; return b;
  });
  const salvar = () => {
    if (rascunho.length !== N) return;
    setSelecionadas([...rascunho]);
    if (chave) try { localStorage.setItem(chave, JSON.stringify(rascunho)); } catch { /* preferência local */ }
    setAberto(false);
  };

  if (!alvos) return null;
  return <>
    {createPortal(selecionadas.map((id) => {
      const acao = POR_ID.get(id); if (!acao) return null;
      const [, to, titulo, icone, tone, featured] = acao;
      return <Link to={to} key={id} className={`ccc-action qa-action ccc-action--${icone}${featured ? " is-featured" : ""}`} data-tone={tone}>{featured && <em className="ccc-action__featured">Destaque</em>}<span className="ccc-action__icon"><Icone nome={icone} /></span><strong>{titulo}</strong></Link>;
    }), alvos.a)}
    {createPortal(<button type="button" className="qa-edit" onClick={() => { setRascunho([...selecionadas]); setAberto(true); }}><Icone nome="configuracao" /> Personalizar</button>, alvos.h)}
    {aberto && createPortal(<div className="qa-modal" onMouseDown={() => setAberto(false)}><section className="qa-dialog" role="dialog" aria-modal="true" aria-labelledby="qa-title" onMouseDown={(e) => e.stopPropagation()}>
      <header className="qa-head"><h2 id="qa-title">Personalizar ações rápidas</h2><button type="button" aria-label="Fechar" onClick={() => setAberto(false)}>×</button></header>
      <div className="qa-list">{TODAS.map(([id,, titulo, icone]) => {
        const i = rascunho.indexOf(id), ativa = i >= 0;
        return <div className="qa-item" key={id}><button type="button" className="qa-toggle" disabled={!ativa && rascunho.length >= N} onClick={() => alternar(id)}><Icone nome={icone} /><strong>{titulo}</strong></button>{ativa && <span className="qa-order"><button type="button" disabled={i === 0} onClick={() => mover(id, -1)}>↑</button><button type="button" disabled={i === rascunho.length - 1} onClick={() => mover(id, 1)}>↓</button></span>}</div>;
      })}</div>
      <footer className="qa-foot"><span>{rascunho.length}/{N}</span><button type="button" onClick={() => setRascunho([...PADRAO])}>Padrão</button><button type="button" onClick={() => setAberto(false)}>Cancelar</button><button type="button" className="qa-save" disabled={rascunho.length !== N} onClick={salvar}>Salvar</button></footer>
    </section></div>, document.body)}
  </>;
}
