import { useEffect, useMemo, useState } from "react";
import { createPortal } from "react-dom";
import { Link, useLocation } from "react-router-dom";
import Icone, { type NomeIcone } from "./Icone";
import { useAuth } from "../lib/auth";

type AcaoRapida = {
  id: string;
  to: string;
  titulo: string;
  detalhe: string;
  icone: NomeIcone;
  tone: string;
};

const LIMITE_ACOES = 10;

const ACOES_DISPONIVEIS: AcaoRapida[] = [
  { id: "prescrever", to: "/receituario", titulo: "Prescrever", detalhe: "Novo receituário", icone: "prescricao", tone: "cyan" },
  { id: "solicitar-exames", to: "/documentos", titulo: "Solicitar exames", detalhe: "Adicionar solicitação", icone: "clinica", tone: "blue" },
  { id: "calculadoras", to: "/calculadoras", titulo: "Calculadoras", detalhe: "Escores e índices", icone: "calculadora", tone: "amber" },
  { id: "interacoes", to: "/interacoes", titulo: "Interações", detalhe: "Segurança medicamentosa", icone: "medicamento", tone: "violet" },
  { id: "emergencias", to: "/emergencia", titulo: "Emergências", detalhe: "Condutas rápidas", icone: "emergencia", tone: "red" },
  { id: "guidelines", to: "/diretrizes", titulo: "Guidelines", detalhe: "Diretrizes atuais", icone: "conhecimento", tone: "green" },
  { id: "corvia-ai", to: "/assistente", titulo: "CorVIA AI", detalhe: "Assistente Clínica", icone: "assistente", tone: "blue" },
  { id: "documentos", to: "/documentos", titulo: "Documentos", detalhe: "Atestado, relatório...", icone: "documento", tone: "violet" },
  { id: "checklists", to: "/checklists", titulo: "Checklists", detalhe: "Condutas estruturadas", icone: "check", tone: "green" },
  { id: "triagem", to: "/triagem-sintomas", titulo: "Triagem", detalhe: "Triagem de sintomas", icone: "triagem", tone: "red" },
  { id: "pacientes", to: "/round", titulo: "Pacientes", detalhe: "Round e acompanhamento", icone: "pacientes", tone: "cyan" },
  { id: "medicamentos", to: "/medicamentos", titulo: "Medicamentos", detalhe: "Consulta farmacológica", icone: "medicamento", tone: "violet" },
  { id: "agenda", to: "/agenda", titulo: "Agenda", detalhe: "Compromissos e rotas", icone: "agenda", tone: "blue" },
  { id: "evidencias", to: "/evidencias", titulo: "Evidências", detalhe: "Base científica", icone: "evidencia", tone: "cyan" },
];

const ACOES_PADRAO_IDS = ACOES_DISPONIVEIS.slice(0, LIMITE_ACOES).map((acao) => acao.id);

function chaveAcoesRapidas(userId?: number) {
  return userId ? `corvia:acoes-rapidas:${userId}` : "";
}

function normalizarIds(valor: unknown) {
  if (!Array.isArray(valor)) return ACOES_PADRAO_IDS;
  const ids = valor.filter(
    (id, indice, lista): id is string =>
      typeof id === "string" &&
      lista.indexOf(id) === indice &&
      ACOES_DISPONIVEIS.some((acao) => acao.id === id),
  );
  return ids.length === LIMITE_ACOES ? ids : ACOES_PADRAO_IDS;
}

export default function HomeQuickActionsPersonalizer() {
  const { pathname } = useLocation();
  const { usuario } = useAuth();
  const [desktop, setDesktop] = useState(() => typeof window !== "undefined" && window.matchMedia("(min-width: 901px)").matches);
  const [actionsTarget, setActionsTarget] = useState<HTMLElement | null>(null);
  const [headerTarget, setHeaderTarget] = useState<HTMLElement | null>(null);
  const [acoesRapidas, setAcoesRapidas] = useState<string[]>(ACOES_PADRAO_IDS);
  const [rascunho, setRascunho] = useState<string[]>(ACOES_PADRAO_IDS);
  const [aberto, setAberto] = useState(false);

  useEffect(() => {
    const media = window.matchMedia("(min-width: 901px)");
    const atualizar = () => setDesktop(media.matches);
    atualizar();
    media.addEventListener("change", atualizar);
    return () => media.removeEventListener("change", atualizar);
  }, []);

  useEffect(() => {
    const chave = chaveAcoesRapidas(usuario?.id);
    if (!chave) {
      setAcoesRapidas(ACOES_PADRAO_IDS);
      return;
    }
    try {
      setAcoesRapidas(normalizarIds(JSON.parse(localStorage.getItem(chave) || "[]")));
    } catch {
      setAcoesRapidas(ACOES_PADRAO_IDS);
    }
  }, [usuario?.id]);

  useEffect(() => {
    if (pathname !== "/" || !desktop) {
      setActionsTarget(null);
      setHeaderTarget(null);
      return;
    }

    function localizar() {
      const actions = document.querySelector<HTMLElement>(".ccc-actions-section .ccc-actions");
      const header = document.querySelector<HTMLElement>(".ccc-actions-section .ccc-section__head");
      if (actions) setActionsTarget(actions);
      if (header) setHeaderTarget(header);
      return Boolean(actions && header);
    }

    if (localizar()) return;
    const observer = new MutationObserver(() => {
      if (localizar()) observer.disconnect();
    });
    observer.observe(document.body, { childList: true, subtree: true });
    return () => observer.disconnect();
  }, [desktop, pathname]);

  useEffect(() => {
    const ativa = pathname === "/" && desktop && Boolean(actionsTarget && headerTarget);
    document.body.classList.toggle("ccc-actions-personalized-active", ativa);
    return () => document.body.classList.remove("ccc-actions-personalized-active");
  }, [actionsTarget, desktop, headerTarget, pathname]);

  const acoesVisiveis = useMemo(
    () => acoesRapidas
      .map((id) => ACOES_DISPONIVEIS.find((acao) => acao.id === id))
      .filter((acao): acao is AcaoRapida => Boolean(acao)),
    [acoesRapidas],
  );

  function abrirPersonalizacao() {
    setRascunho([...acoesRapidas]);
    setAberto(true);
  }

  function alternar(id: string) {
    setRascunho((atuais) => {
      if (atuais.includes(id)) return atuais.filter((item) => item !== id);
      if (atuais.length >= LIMITE_ACOES) return atuais;
      return [...atuais, id];
    });
  }

  function mover(id: string, deslocamento: -1 | 1) {
    setRascunho((atuais) => {
      const indice = atuais.indexOf(id);
      const destino = indice + deslocamento;
      if (indice < 0 || destino < 0 || destino >= atuais.length) return atuais;
      const copia = [...atuais];
      [copia[indice], copia[destino]] = [copia[destino], copia[indice]];
      return copia;
    });
  }

  function salvar() {
    if (rascunho.length !== LIMITE_ACOES) return;
    const proximas = [...rascunho];
    setAcoesRapidas(proximas);
    const chave = chaveAcoesRapidas(usuario?.id);
    if (chave) {
      try { localStorage.setItem(chave, JSON.stringify(proximas)); } catch { /* preferência local não bloqueia a Home */ }
    }
    setAberto(false);
  }

  if (pathname !== "/" || !desktop || !actionsTarget || !headerTarget) return null;

  return (
    <>
      {createPortal(
        acoesVisiveis.map((acao) => (
          <Link
            to={acao.to}
            key={acao.id}
            className={`ccc-action ccc-action--personalized ccc-action--${acao.icone}`}
            data-tone={acao.tone}
          >
            <span className="ccc-action__icon"><Icone nome={acao.icone} /></span>
            <span><strong>{acao.titulo}</strong><small>{acao.detalhe}</small></span>
          </Link>
        )),
        actionsTarget,
      )}

      {createPortal(
        <button type="button" className="ccc-quick-actions-personalize" onClick={abrirPersonalizacao}>
          <Icone nome="configuracao" /> Personalizar
        </button>,
        headerTarget,
      )}

      {aberto && createPortal(
        <div className="ccc-quick-actions-picker" onMouseDown={() => setAberto(false)}>
          <section
            className="ccc-quick-actions-picker__dialog"
            role="dialog"
            aria-modal="true"
            aria-labelledby="ccc-quick-actions-picker-title"
            onMouseDown={(evento) => evento.stopPropagation()}
          >
            <header className="ccc-quick-actions-picker__header">
              <h2 id="ccc-quick-actions-picker-title">Personalizar ações rápidas</h2>
              <button type="button" aria-label="Fechar" onClick={() => setAberto(false)}>×</button>
            </header>
            <p className="ccc-quick-actions-picker__intro">
              Escolha exatamente 10 atalhos. Eles serão exibidos em duas fileiras de cinco, na ordem definida abaixo.
            </p>
            <div className="ccc-quick-actions-picker__catalog">
              {ACOES_DISPONIVEIS.map((acao) => {
                const posicao = rascunho.indexOf(acao.id);
                const selecionada = posicao >= 0;
                return (
                  <div className="ccc-quick-actions-picker__item" data-selected={selecionada} key={acao.id}>
                    <button
                      type="button"
                      className="ccc-quick-actions-picker__toggle"
                      aria-pressed={selecionada}
                      onClick={() => alternar(acao.id)}
                      disabled={!selecionada && rascunho.length >= LIMITE_ACOES}
                    >
                      <span className="ccc-quick-actions-picker__icon"><Icone nome={acao.icone} /></span>
                      <span className="ccc-quick-actions-picker__copy"><strong>{acao.titulo}</strong><small>{acao.detalhe}</small></span>
                    </button>
                    {selecionada && (
                      <span className="ccc-quick-actions-picker__order">
                        <span className="ccc-quick-actions-picker__position">{posicao + 1}</span>
                        <button type="button" aria-label={`Mover ${acao.titulo} para cima`} disabled={posicao === 0} onClick={() => mover(acao.id, -1)}>↑</button>
                        <button type="button" aria-label={`Mover ${acao.titulo} para baixo`} disabled={posicao === rascunho.length - 1} onClick={() => mover(acao.id, 1)}>↓</button>
                      </span>
                    )}
                  </div>
                );
              })}
            </div>
            <footer className="ccc-quick-actions-picker__footer">
              <span>{rascunho.length}/{LIMITE_ACOES} selecionadas</span>
              <span className="ccc-quick-actions-picker__footer-actions">
                <button type="button" onClick={() => setRascunho([...ACOES_PADRAO_IDS])}>Restaurar padrão</button>
                <button type="button" onClick={() => setAberto(false)}>Cancelar</button>
                <button type="button" data-primary="true" disabled={rascunho.length !== LIMITE_ACOES} onClick={salvar}>Salvar</button>
              </span>
            </footer>
          </section>
        </div>,
        document.body,
      )}
    </>
  );
}
