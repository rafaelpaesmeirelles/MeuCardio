import { useCallback, useEffect, useMemo, useState, type ReactNode } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import Icone, { type NomeIcone } from "../components/Icone";
import { api, ApiError } from "../lib/api";
import { useAuth } from "../lib/auth";

type Modo = "quick" | "completo";
type Slide = {
  id: string;
  eyebrow: string;
  titulo: string;
  resumo: string;
  promessa: string;
  icone: NomeIcone;
  pontos: string[];
  Mockup: () => ReactNode;
  sinal?: "cyan" | "red" | "green";
};

function MiniTop({ contexto = "Clinical Command Center" }: { contexto?: string }) {
  return (
    <div className="cos-tour-mock__top">
      <span className="cos-tour-mock__brand"><img src="/corvia-logo-compacta.png" alt="" /></span>
      <span className="cos-tour-mock__search"><Icone nome="busca" /> Pesquisar ou executar...</span>
      <span className="cos-tour-mock__context">{contexto}</span>
      <span className="cos-tour-mock__avatar">RM</span>
    </div>
  );
}

function MiniSidebar({ ativo = "Início" }: { ativo?: string }) {
  const itens: Array<[string, NomeIcone]> = [
    ["Início", "hoje"],
    ["Clínica", "clinica"],
    ["Trabalho", "pacientes"],
    ["Conhecimento", "conhecimento"],
    ["CorVIA AI", "assistente"],
  ];
  return (
    <div className="cos-tour-mock__side">
      {itens.map(([nome, icone]) => <span key={nome} className={nome === ativo ? "is-active" : ""}><Icone nome={icone} />{nome}</span>)}
      <span className="cos-tour-mock__assistant"><b>✦</b><em>Assistente Pessoal</em></span>
    </div>
  );
}

function MockHome() {
  return (
    <div className="cos-tour-mock cos-tour-mock--app">
      <MiniSidebar ativo="Início" />
      <div className="cos-tour-mock__appbody">
        <MiniTop />
        <div className="cos-tour-home">
          <span className="cos-tour-kicker">● Clinical Command Center</span>
          <strong>O que você precisa resolver agora?</strong>
          <small>Conhecimento, decisão e ação a partir do mesmo ponto.</small>
          <div className="cos-tour-command"><b>✦</b><span>Pergunte, pesquise ou execute uma ação...</span><em>↗</em></div>
          <div className="cos-tour-quick">
            {[["prescricao","Prescrever"],["documento","Documento"],["calculadora","Calculadoras"],["emergencia","Emergências"],["medicamento","Medicamentos"],["assistente","CorVIA AI"]].map(([icone,nome]) => <span key={nome}><Icone nome={icone as NomeIcone} /><b>{nome}</b></span>)}
          </div>
          <div className="cos-tour-recent"><span>Continuar de onde parei</span><i>ICFER</i><i>Sacubitril/valsartana</i><i>Evidências</i><i>CHA₂DS₂-VASc</i></div>
        </div>
      </div>
    </div>
  );
}

function MockIntelligence() {
  return (
    <div className="cos-tour-mock cos-tour-mock--app">
      <MiniSidebar ativo="Clínica" />
      <div className="cos-tour-mock__appbody">
        <MiniTop contexto="Doenças e condições" />
        <div className="cos-tour-context-page">
          <div className="cos-tour-context-main"><span className="cos-tour-kicker">Condição clínica</span><strong>Insuficiência cardíaca</strong><small>O contexto vira ponto de partida para navegar e agir.</small><div className="cos-tour-lines"><i/><i/><i/></div></div>
          <aside className="cos-tour-intel"><span className="cos-tour-kicker">CorVIA Intelligence</span><strong>Inteligência clínica</strong><small>Conexões mudam conforme o que você abriu.</small>{[["evidencia","Diretrizes"],["medicamento","Medicamentos"],["calculadora","Escores"],["clinica","Exames"]].map(([icone,nome]) => <em key={nome}><Icone nome={icone as NomeIcone}/>{nome}<b>→</b></em>)}<div className="cos-tour-graph"><b>◎</b><span>Tudo com Tudo<small>Explorar relações clínicas</small></span></div></aside>
        </div>
      </div>
    </div>
  );
}

function MockAssistant() {
  return (
    <div className="cos-tour-mock cos-tour-mock--assistant">
      <div className="cos-tour-assistant-bg"><MiniTop /></div>
      <aside className="cos-tour-assistant-panel">
        <header><span>✦</span><div><small>Seu copiloto de rotina</small><strong>Assistente Pessoal</strong></div><b>×</b></header>
        <section><span className="cos-tour-kicker">Seu dia</span><div className="cos-tour-assistant-metrics"><i><b>4</b><small>compromissos</small></i><i><b>14:00</b><small>próximo horário</small></i></div><div className="cos-tour-assistant-next"><Icone nome="agenda"/><span><small>Próximo compromisso</small><strong>Consultório</strong><em>14:00</em></span></div></section>
        <section><span className="cos-tour-kicker">Deslocamento</span><div className="cos-tour-route"><Icone nome="pin"/><span><small>Próximo local</small><strong>Consultório</strong></span></div><div className="cos-tour-assistant-metrics cos-tour-assistant-metrics--3"><i><b>27 min</b><small>trajeto</small></i><i><b>12 km</b><small>distância</small></i><i><b>13:18</b><small>saída sugerida</small></i></div></section>
        <section className="cos-tour-assistant-links"><em><Icone nome="documento"/>Documentos<b>→</b></em><em><Icone nome="mail"/>CorVIA Mail<b>→</b></em><em><Icone nome="favorito"/>Favoritos<b>→</b></em></section>
      </aside>
    </div>
  );
}

function MockGraph() {
  const nos = [
    ["ICFER", "n0"], ["ARNI", "n1"], ["Sacubitril/valsartana", "n2"], ["Estudo", "n3"],
    ["Guideline", "n4"], ["Ecocardiograma", "n5"], ["Evidência", "n6"], ["Prescrição", "n7"],
  ];
  return (
    <div className="cos-tour-mock cos-tour-mock--graph">
      <div className="cos-tour-graph-stage">
        <svg viewBox="0 0 720 420" aria-hidden="true">
          <g className="links"><path d="M360 205 190 115"/><path d="M360 205 535 112"/><path d="M360 205 575 250"/><path d="M360 205 170 275"/><path d="M190 115 100 205"/><path d="M535 112 650 185"/><path d="M575 250 480 335"/><path d="M170 275 265 350"/></g>
        </svg>
        {nos.map(([nome, classe]) => <span key={nome} className={`cos-tour-node ${classe}`}><b>◎</b><em>{nome}</em></span>)}
        <div className="cos-tour-thread"><small>Clinical Thread</small><strong>ICFER → ARNI → Sacubitril/valsartana → Evidência → Guideline</strong></div>
      </div>
    </div>
  );
}

function MockAction() {
  return (
    <div className="cos-tour-mock cos-tour-mock--action">
      <MiniTop contexto="Documentos e solicitações" />
      <div className="cos-tour-action-body">
        <div className="cos-tour-action-head"><span className="cos-tour-kicker">Ação clínica</span><strong>Do contexto à execução</strong><small>Sem abandonar o fluxo para abrir outra ferramenta.</small></div>
        <div className="cos-tour-action-grid">
          <span><Icone nome="prescricao"/><b>Prescrever</b><small>Medicamentos e receita digital</small></span>
          <span><Icone nome="clinica"/><b>Solicitar exames</b><small>Pedido clínico estruturado</small></span>
          <span><Icone nome="documento"/><b>Emitir atestado</b><small>Fluxo rápido sem modelo obrigatório</small></span>
          <span><Icone nome="documento"/><b>Documento em branco</b><small>Editor livre e assinatura</small></span>
        </div>
        <div className="cos-tour-document"><header><i/><span><b>Documento clínico</b><small>Conteúdo final sempre editável</small></span></header><div><i/><i/><i/><i/></div><footer><span>Preview</span><b>Assinar →</b></footer></div>
      </div>
    </div>
  );
}

function MockEmergency() {
  return (
    <div className="cos-tour-mock cos-tour-mock--emergency">
      <div className="cos-tour-emergency-head"><Icone nome="emergencia"/><span><small>Modo Emergência</small><strong>Menos interface. Mais decisão.</strong></span></div>
      <div className="cos-tour-emergency-grid">{["Dor torácica / SCA","FA rápida","Taquicardia","Bradicardia","Choque","Edema agudo de pulmão","TEP","PCR"].map((nome,i) => <span key={nome} className={i === 0 ? "is-focus" : ""}><Icone nome="emergencia"/><b>{nome}</b></span>)}</div>
      <div className="cos-tour-emergency-flow"><b>Reconhecer</b><i>→</i><b>Primeiros minutos</b><i>→</i><b>Estratificar</b><i>→</i><b>Tratar</b></div>
    </div>
  );
}

function MockKnowledge() {
  return (
    <div className="cos-tour-mock cos-tour-mock--knowledge">
      <MiniTop contexto="Conhecimento" />
      <div className="cos-tour-knowledge-head"><span className="cos-tour-kicker">Base clínica</span><strong>Conhecimento sem virar um portal de links</strong><small>Diretrizes, estudos, evidências, medicamentos, exames e casos dentro da mesma linguagem.</small></div>
      <div className="cos-tour-knowledge-grid">
        {[["evidencia","Evidências","Classe, nível e fonte"],["evidencia","Estudos","Literatura original"],["conhecimento","Biblioteca","Conteúdo clínico"],["clinica","Exames","Critérios e interpretação"],["doencas","Casos clínicos","Raciocínio aplicado"],["curso","Trilhas","Estudo estruturado"]].map(([icone,titulo,detalhe]) => <span key={titulo}><Icone nome={icone as NomeIcone}/><b>{titulo}</b><small>{detalhe}</small><em>→</em></span>)}
      </div>
    </div>
  );
}

function MockCommunication() {
  return (
    <div className="cos-tour-mock cos-tour-mock--communication">
      <MiniTop contexto="Comunicação" />
      <div className="cos-tour-communication-grid">
        <section><div className="cos-tour-mail-title"><Icone nome="mail"/><span><small>CorVIA Mail</small><strong>Comunicação profissional</strong></span></div>{["Paciente — retorno de exames","Equipe — discussão clínica","Convite científico"].map((texto,i) => <em key={texto} className={i===0?"is-new":""}><i/><span><b>{texto}</b><small>Mensagem profissional</small></span><time>{i===0?"Agora":"Ontem"}</time></em>)}</section>
        <section><div className="cos-tour-mail-title"><Icone nome="comunicacao"/><span><small>CorVIA Chat</small><strong>Rede profissional</strong></span></div><div className="cos-tour-chat"><i>Tenho uma dúvida sobre este caso...</i><i className="mine">Vamos revisar o contexto.</i><i>Perfeito.</i></div></section>
      </div>
    </div>
  );
}

function MockMobile() {
  return (
    <div className="cos-tour-mock cos-tour-mock--mobile">
      <div className="cos-tour-phone">
        <header><img src="/corvia-logo-compacta.png" alt=""/><Icone nome="busca"/></header>
        <main><span className="cos-tour-kicker">Clinical Command Center</span><strong>O que você precisa resolver agora?</strong><div className="cos-tour-mobile-command">✦ <span>Pergunte ou execute...</span></div><div className="cos-tour-mobile-actions">{[["prescricao","Prescrever"],["clinica","Exames"],["documento","Documento"],["emergencia","Emergência"]].map(([icone,nome])=><i key={nome}><Icone nome={icone as NomeIcone}/><b>{nome}</b></i>)}</div><div className="cos-tour-mobile-day"><small>Seu dia</small><b>Próximo compromisso · 14:00</b><em>Assistente acompanha sua rotina</em></div></main>
        <footer><i><Icone nome="hoje"/><small>Início</small></i><i><Icone nome="busca"/><small>Buscar</small></i><i className="assistant"><b>✦</b><small>Assistente</small></i><i><Icone nome="agenda"/><small>Agenda</small></i><i><Icone nome="mais"/><small>Mais</small></i></footer>
      </div>
      <div className="cos-tour-mobile-copy"><span>Desktop para profundidade.</span><span>Mobile para velocidade.</span><strong>O mesmo CorVIA, sem comprimir a experiência.</strong></div>
    </div>
  );
}

const SLIDES: Slide[] = [
  {
    id: "home", eyebrow: "Princípio-mãe", titulo: "Comece pela sua necessidade, não por um módulo.",
    resumo: "A Home não presume que você está em consultório, no hospital ou estudando. Ela pergunta o que você precisa resolver agora.",
    promessa: "Pesquisar + perguntar + executar convergem no mesmo ponto.", icone: "hoje",
    pontos: ["Clinical Command Bar como protagonista", "Ações clínicas universais a um clique", "Continuidade por contexto — não apenas por paciente"], Mockup: MockHome,
  },
  {
    id: "intelligence", eyebrow: "Contexto", titulo: "O sistema muda de inteligência quando o contexto muda.",
    resumo: "CorVIA Intelligence acompanha a tela em que você está e aproxima relações clínicas relevantes sem tomar o lugar do conteúdo principal.",
    promessa: "A interface deixa de ser uma coleção de módulos e passa a se comportar como um workspace.", icone: "clinica",
    pontos: ["Doença → diretriz, medicamento, exame e escore", "Medicamento → segurança, evidência e prescrição", "Estudo → recomendação e aplicação prática"], Mockup: MockIntelligence,
  },
  {
    id: "assistant", eyebrow: "Assistência contínua", titulo: "Seu assistente pessoal entende que médico também tem uma rotina.",
    resumo: "Agenda, próximo compromisso, deslocamento e continuidade profissional vivem numa camada diferente da inteligência clínica.",
    promessa: "Agenda é onde estão os compromissos. O Assistente ajuda você a chegar, lembrar e agir.", icone: "assistente",
    pontos: ["Briefing do dia", "Deslocamento sob demanda com dados reais", "Acesso contínuo a documentos, Mail e favoritos"], Mockup: MockAssistant, sinal: "green",
  },
  {
    id: "graph", eyebrow: "Knowledge Graph", titulo: "Tudo com Tudo — sem transformar a tela inteira num grafo.",
    resumo: "As entidades clínicas formam uma rede navegável. O grafo é uma camada de inteligência, não uma obrigação visual.",
    promessa: "Você abre um ponto e descobre o caminho clínico ao redor dele.", icone: "conhecimento",
    pontos: ["Clinical Thread mostra o caminho quando existe contexto", "Explorar relações fica disponível sob demanda", "Conhecimento e ação continuam conectados"], Mockup: MockGraph,
  },
  {
    id: "action", eyebrow: "Ação", titulo: "Quando a decisão termina, a execução já está ali.",
    resumo: "Prescrição, solicitações e documentos fazem parte do fluxo clínico — não são um sistema paralelo.",
    promessa: "Menos troca de contexto entre pensar, documentar e agir.", icone: "prescricao",
    pontos: ["Prescrição a partir do contexto", "Solicitação de exames em fluxo dedicado", "Documento sempre editável antes de gerar e assinar"], Mockup: MockAction,
  },
  {
    id: "emergency", eyebrow: "Risco imediato", titulo: "Na emergência, o CorVIA fica mais simples — de propósito.",
    resumo: "A interface reduz ornamentação e privilegia reconhecimento, primeiros minutos, estratificação e conduta.",
    promessa: "O visual acompanha a urgência clínica em vez de competir com ela.", icone: "emergencia",
    pontos: ["Protocolos acessíveis rapidamente", "Drogas, escores e checklists próximos", "Vermelho reservado para sinal clínico e risco"], Mockup: MockEmergency, sinal: "red",
  },
  {
    id: "knowledge", eyebrow: "Conhecimento", titulo: "Estudar, consultar e decidir usam a mesma base.",
    resumo: "Biblioteca, evidências, estudos, diretrizes, exames, casos e trilhas deixam de parecer ilhas separadas.",
    promessa: "O médico aprofunda quando quer — sem perder a aplicação clínica.", icone: "conhecimento",
    pontos: ["Fontes e rastreabilidade continuam visíveis", "Atualizações clínicas entram sem inventar conteúdo", "Favoritos e histórico ajudam a retomar"], Mockup: MockKnowledge,
  },
  {
    id: "communication", eyebrow: "Comunicação", titulo: "Seu trabalho continua depois da consulta.",
    resumo: "CorVIA Mail e CorVIA Chat permanecem ferramentas próprias, integradas à rotina e sem se confundir com a IA clínica.",
    promessa: "Comunicação profissional fica dentro do mesmo ambiente de trabalho.", icone: "mail",
    pontos: ["CorVIA Mail para comunicação profissional", "CorVIA Chat para rede entre profissionais", "O Assistente pode levar você ao que precisa de atenção"], Mockup: MockCommunication,
  },
  {
    id: "mobile", eyebrow: "Mobile", titulo: "No celular, a prioridade é alcançar a ação com uma mão.",
    resumo: "A experiência móvel não é o desktop espremido. Ações, busca, agenda e Assistente ganham hierarquia própria.",
    promessa: "O mesmo produto, com outra ergonomia.", icone: "menu",
    pontos: ["Barra inferior orientada à rotina", "Assistente sempre acessível", "Command Bar continua sendo a porta de entrada"], Mockup: MockMobile,
  },
];

const QUICK_IDS = ["home", "intelligence", "assistant", "graph", "action", "emergency"];

function slidesDoModo(modo: Modo) {
  if (modo === "completo") return SLIDES;
  const ordem = new Map(QUICK_IDS.map((id, indice) => [id, indice]));
  return SLIDES.filter((slide) => ordem.has(slide.id)).sort((a, b) => (ordem.get(a.id) ?? 0) - (ordem.get(b.id) ?? 0));
}

function iniciais(nome?: string | null) {
  if (!nome) return "CV";
  return nome.trim().split(/\s+/).slice(0, 2).map((p) => p[0]?.toUpperCase()).join("") || "CV";
}

export default function TourClinicalOS() {
  const { usuario } = useAuth();
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const pendente = Boolean(usuario?.onboarding_pendente);
  const urlModo = params.get("modo");
  const [modo, setModo] = useState<Modo>(urlModo === "quick" || urlModo === "completo" ? urlModo : pendente ? "quick" : "completo");
  const [passo, setPasso] = useState(0);
  const [concluindo, setConcluindo] = useState(false);
  const [fotoFalhou, setFotoFalhou] = useState(false);

  const slides = useMemo(() => {
    const base = slidesDoModo(modo);
    if (!usuario?.investidor) return base;
    return base.map((slide) => slide.id !== "communication" ? slide : {
      ...slide,
      pontos: [...slide.pontos, "Na conta de investidor, CorVIA Mail permanece em modo demonstração sem operações reais."],
    });
  }, [modo, usuario?.investidor]);

  const total = slides.length + 2;
  const boasVindas = passo === 0;
  const final = passo === total - 1;
  const atual = !boasVindas && !final ? slides[passo - 1] : null;

  const avancar = useCallback(() => setPasso((valor) => Math.min(valor + 1, total - 1)), [total]);
  const voltar = useCallback(() => setPasso((valor) => Math.max(valor - 1, 0)), []);

  useEffect(() => {
    function teclado(evento: KeyboardEvent) {
      const alvo = evento.target as HTMLElement | null;
      if (alvo && /^(INPUT|TEXTAREA|SELECT)$/.test(alvo.tagName)) return;
      if (evento.key === "ArrowRight") avancar();
      if (evento.key === "ArrowLeft") voltar();
      if (evento.key === "Escape" && !pendente) navigate("/");
    }
    window.addEventListener("keydown", teclado);
    return () => window.removeEventListener("keydown", teclado);
  }, [avancar, voltar, navigate, pendente]);

  async function concluir() {
    if (!pendente) { navigate("/"); return; }
    setConcluindo(true);
    try {
      await api.post("/auth/me/onboarding-concluido", {});
    } catch (erro) {
      if (!(erro instanceof ApiError)) throw erro;
    } finally {
      window.location.replace("/");
    }
  }

  function abrirCompleto() { setModo("completo"); setPasso(1); }

  return (
    <div className="cos-tour">
      <header className="cos-tour__top">
        <div className="cos-tour__brand"><img src="/corvia-logo-compacta.png" alt="CorVIA"/><span><strong>CorVIA</strong><small>Clinical OS</small></span></div>
        <div className="cos-tour__mode"><i/><span>{modo === "quick" ? "Início rápido" : "Tour completo"}</span></div>
        <button type="button" className="cos-tour__skip" onClick={() => void concluir()} disabled={concluindo}>{pendente ? "Pular" : "Fechar"}</button>
      </header>

      <div className="cos-tour__progress" aria-label="Progresso do tour"><div style={{ width: `${((passo + 1) / total) * 100}%` }} /></div>

      <main className="cos-tour__stage">
        {boasVindas && (
          <section className="cos-tour-welcome">
            <div className="cos-tour-welcome__glow" aria-hidden="true" />
            <div className="cos-tour-welcome__avatar">
              {usuario?.instagram_photo_url && !fotoFalhou ? <img src={usuario.instagram_photo_url} alt="" onError={() => setFotoFalhou(true)}/> : <span>{iniciais(usuario?.full_name)}</span>}
              <i>✦</i>
            </div>
            <p className="cos-tour-welcome__kicker">Bem-vindo ao CorVIA Clinical OS</p>
            <h1>Um sistema que começa pelo que você precisa resolver.</h1>
            <p className="cos-tour-welcome__lead">Não é só prontuário. Não é só IA. Não é só conteúdo. É o seu workspace clínico para pesquisar, decidir, executar e organizar o trabalho médico.</p>
            {usuario?.convidado && <p className="cos-tour-welcome__entitlement">Acesso de médico convidado ativo conforme as permissões da sua conta.</p>}
            {usuario?.investidor && <p className="cos-tour-welcome__entitlement">Modo investidor: conheça a arquitetura completa; CorVIA Mail permanece demonstrativo e sem operações reais.</p>}
            <div className="cos-tour-welcome__pillars"><span>Conhecimento</span><i>→</i><span>Contexto</span><i>→</i><span>Decisão</span><i>→</i><span>Ação</span><i>→</i><span>Assistência</span></div>
            <button type="button" className="cos-tour__primary" onClick={avancar}>Ver como o CorVIA pensa <Icone nome="seta" /></button>
            <small className="cos-tour-welcome__hint">Use ← → no teclado. Você pode rever este tour depois.</small>
          </section>
        )}

        {atual && (
          <section className={`cos-tour-feature is-${atual.sinal ?? "cyan"}`} key={atual.id}>
            <div className="cos-tour-feature__visual"><atual.Mockup /></div>
            <div className="cos-tour-feature__copy">
              <div className="cos-tour-feature__counter"><span><Icone nome={atual.icone}/></span><small>{String(passo).padStart(2,"0")} / {String(total - 2).padStart(2,"0")}</small></div>
              <p className="cos-tour-feature__eyebrow">{atual.eyebrow}</p>
              <h1>{atual.titulo}</h1>
              <p className="cos-tour-feature__lead">{atual.resumo}</p>
              <blockquote>“{atual.promessa}”</blockquote>
              <div className="cos-tour-feature__points">{atual.pontos.map((ponto) => <span key={ponto}><i><Icone nome="check"/></i>{ponto}</span>)}</div>
            </div>
          </section>
        )}

        {final && (
          <section className="cos-tour-final">
            <span className="cos-tour-final__mark"><img src="/corvia-logo-compacta.png" alt="" /></span>
            <p className="cos-tour-welcome__kicker">Agora começa a rotina real</p>
            <h1>Entre pelo problema. O CorVIA aproxima o resto.</h1>
            <p>Pesquise, aprenda, decida, execute e organize seu dia sem precisar pensar em qual módulo abrir primeiro.</p>
            <div className="cos-tour-final__map"><span><b>Necessidade</b><small>O que preciso resolver?</small></span><i>→</i><span><b>Contexto</b><small>Onde estou?</small></span><i>→</i><span><b>Decisão</b><small>O que faz sentido?</small></span><i>→</i><span><b>Ação</b><small>Faça agora.</small></span></div>
            <button type="button" className="cos-tour__primary" onClick={() => void concluir()} disabled={concluindo}>{concluindo ? "Abrindo o CorVIA…" : "Abrir meu Clinical Command Center"} <Icone nome="seta" /></button>
            {modo === "quick" && <button type="button" className="cos-tour__secondary" onClick={abrirCompleto}>Quero ver o tour completo</button>}
          </section>
        )}
      </main>

      {!boasVindas && !final && (
        <footer className="cos-tour__controls">
          <button type="button" className="cos-tour__back" onClick={voltar}><span>←</span> Voltar</button>
          <div className="cos-tour__dots" role="progressbar" aria-valuenow={passo+1} aria-valuemin={1} aria-valuemax={total}>{Array.from({ length: total }).map((_,indice)=><button key={indice} type="button" aria-label={`Ir para etapa ${indice+1}`} className={`${indice===passo?"is-current":""}${indice<passo?" is-done":""}`} onClick={()=>setPasso(indice)}/>)}</div>
          <button type="button" className="cos-tour__next" onClick={avancar}>Próximo <span>→</span></button>
        </footer>
      )}
    </div>
  );
}
