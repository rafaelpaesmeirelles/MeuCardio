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
      <span className="cos-tour-mock__brand"><img src="/corvia-mark-canonical.svg" alt="" /></span>
      <span className="cos-tour-mock__search"><Icone nome="busca" /> Pergunte, pesquise ou execute...</span>
      <span className="cos-tour-mock__context">{contexto}</span>
      <span className="cos-tour-mock__avatar">RM</span>
    </div>
  );
}

function MiniSidebar({ ativo = "Início" }: { ativo?: string }) {
  const itens: Array<[string, NomeIcone]> = [
    ["Início", "hoje"],
    ["Buscar", "busca"],
    ["Medicamentos", "medicamento"],
    ["Evidências", "evidencia"],
    ["Pacientes", "pacientes"],
    ["Agenda", "agenda"],
    ["Assistente", "assistente"],
  ];
  return (
    <div className="cos-tour-mock__side">
      {itens.map(([nome, icone]) => <span key={nome} className={nome === ativo ? "is-active" : ""}><Icone nome={icone} />{nome}</span>)}
      <span className="cos-tour-mock__assistant"><b>✦</b><em>Assistente Pessoal</em></span>
    </div>
  );
}

function MockHome() {
  const acoes: Array<[NomeIcone, string]> = [
    ["prescricao", "Prescrever"], ["clinica", "Exames"], ["documento", "Documento"], ["calculadora", "Calculadoras"],
    ["emergencia", "Emergências"], ["medicamento", "Medicamentos"], ["conhecimento", "Guidelines"], ["assistente", "Assistente"],
  ];
  return (
    <div className="cos-tour-mock cos-tour-mock--app">
      <MiniSidebar ativo="Início" />
      <div className="cos-tour-mock__appbody">
        <MiniTop />
        <div className="cos-tour-home">
          <span className="cos-tour-kicker">● Clinical Command Center</span>
          <strong>O que você precisa resolver agora?</strong>
          <small>Conhecimento, contexto, decisão e ação a partir do mesmo ponto.</small>
          <div className="cos-tour-command"><b>✦</b><span>Pergunte, pesquise ou execute uma ação...</span><em>↗</em></div>
          <div className="cos-tour-quick">{acoes.map(([icone,nome]) => <span key={nome}><Icone nome={icone} /><b>{nome}</b></span>)}</div>
          <div className="cos-tour-recent"><span>Continuar de onde parei</span><i>ICFER</i><i>Sacubitril/valsartana</i><i>Evidências</i><i>CHA₂DS₂-VASc</i></div>
        </div>
      </div>
    </div>
  );
}

function MockIntelligence() {
  return (
    <div className="cos-tour-mock cos-tour-mock--app">
      <MiniSidebar ativo="Evidências" />
      <div className="cos-tour-mock__appbody">
        <MiniTop contexto="Evidências" />
        <div className="cos-tour-context-page">
          <div className="cos-tour-context-main"><span className="cos-tour-kicker">Contexto clínico</span><strong>Insuficiência cardíaca</strong><small>O conteúdo principal continua protagonista.</small><div className="cos-tour-lines"><i/><i/><i/></div></div>
          <aside className="cos-tour-intel"><span className="cos-tour-kicker">CorVIA Intelligence</span><strong>Relações relevantes</strong><small>O rail aparece quando realmente agrega valor.</small>{[["evidencia","3 estudos relacionados"],["medicamento","ARNI e iSGLT2"],["conhecimento","Guideline atual"],["clinica","Ecocardiograma"]].map(([icone,nome]) => <em key={nome}><Icone nome={icone as NomeIcone}/>{nome}<b>→</b></em>)}<div className="cos-tour-graph"><b>◎</b><span>Explorar relações<small>Clinical Thread</small></span></div></aside>
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
        <header><span>✦</span><div><small>Seu copiloto de rotina · exemplo ilustrativo</small><strong>Assistente Pessoal</strong></div><b>×</b></header>
        <section><span className="cos-tour-kicker">Seu dia</span><div className="cos-tour-assistant-metrics"><i><b>4</b><small>compromissos</small></i><i><b>14:00</b><small>próximo horário</small></i></div><div className="cos-tour-assistant-next"><Icone nome="agenda"/><span><small>Próximo compromisso</small><strong>Consultório</strong><em>14:00</em></span></div></section>
        <section><span className="cos-tour-kicker">Deslocamento</span><div className="cos-tour-route"><Icone nome="pin"/><span><small>Somente com permissão</small><strong>Próximo local</strong></span></div><div className="cos-tour-assistant-metrics cos-tour-assistant-metrics--3"><i><b>27 min</b><small>trajeto</small></i><i><b>12 km</b><small>distância</small></i><i><b>13:18</b><small>saída sugerida</small></i></div></section>
        <section className="cos-tour-assistant-links"><em><Icone nome="documento"/>Documentos<b>→</b></em><em><Icone nome="mail"/>CorVIA Mail<b>→</b></em><em><Icone nome="favorito"/>Favoritos<b>→</b></em></section>
      </aside>
    </div>
  );
}

function MockMedication() {
  return (
    <div className="cos-tour-mock cos-tour-mock--knowledge">
      <MiniTop contexto="Medication Command Center" />
      <div className="cos-tour-knowledge-head"><span className="cos-tour-kicker">Medicamento</span><strong>Sacubitril/Valsartana</strong><small>Visão geral, doses, indicações, evidências e interações no mesmo contexto.</small></div>
      <div className="cos-tour-knowledge-grid">
        {[["medicamento","Dose","Posologia e ajustes"],["doencas","Indicações","Quando usar"],["evidencia","Evidências","Estudos e desfechos"],["medicamento","Interações","Segurança"],["conhecimento","Guidelines","Recomendações"],["prescricao","Prescrever","Ação clínica"]].map(([icone,titulo,detalhe]) => <span key={titulo}><Icone nome={icone as NomeIcone}/><b>{titulo}</b><small>{detalhe}</small><em>→</em></span>)}
      </div>
    </div>
  );
}

function MockPatient() {
  return (
    <div className="cos-tour-mock cos-tour-mock--action">
      <MiniTop contexto="Patient Command Center" />
      <div className="cos-tour-action-body">
        <div className="cos-tour-action-head"><span className="cos-tour-kicker">Paciente como contexto</span><strong>Resumo, timeline e ação.</strong><small>O paciente entra quando ele é relevante — não domina o produto inteiro.</small></div>
        <div className="cos-tour-action-grid">
          <span><Icone nome="pacientes"/><b>Resumo</b><small>Problemas e pendências</small></span>
          <span><Icone nome="medicamento"/><b>Medicamentos</b><small>Tratamento atual</small></span>
          <span><Icone nome="clinica"/><b>Exames</b><small>Resultados e contexto</small></span>
          <span><Icone nome="prescricao"/><b>Prescrever</b><small>Ação a partir do paciente</small></span>
        </div>
      </div>
    </div>
  );
}

function MockAction() {
  return (
    <div className="cos-tour-mock cos-tour-mock--action">
      <MiniTop contexto="Documentos e Solicitações" />
      <div className="cos-tour-action-body">
        <div className="cos-tour-action-head"><span className="cos-tour-kicker">Ação clínica</span><strong>Do contexto à execução.</strong><small>Os três fluxos principais não dependem de template.</small></div>
        <div className="cos-tour-action-grid">
          <span><Icone nome="clinica"/><b>Solicitar exames</b><small>Pedido clínico estruturado</small></span>
          <span><Icone nome="documento"/><b>Emitir atestado</b><small>Fluxo direto</small></span>
          <span><Icone nome="documento"/><b>Documento em branco</b><small>Editor livre</small></span>
          <span><Icone nome="prescricao"/><b>Prescrever</b><small>Receita digital</small></span>
        </div>
        <div className="cos-tour-document"><header><i/><span><b>Documento clínico</b><small>Conteúdo final sempre revisável</small></span></header><div><i/><i/><i/><i/></div><footer><span>Preview</span><b>Revisar →</b></footer></div>
      </div>
    </div>
  );
}

function MockEmergency() {
  return (
    <div className="cos-tour-mock cos-tour-mock--emergency">
      <div className="cos-tour-emergency-head"><Icone nome="emergencia"/><span><small>Emergency Command Center</small><strong>Menos interface. Mais decisão.</strong></span></div>
      <div className="cos-tour-emergency-grid">{["Dor torácica / SCA","FA rápida","Taquicardia","Bradicardia","Choque","Edema agudo de pulmão","TEP","PCR"].map((nome,i) => <span key={nome} className={i === 0 ? "is-focus" : ""}><Icone nome="emergencia"/><b>{nome}</b></span>)}</div>
      <div className="cos-tour-emergency-flow"><b>Reconhecer</b><i>→</i><b>Primeiros minutos</b><i>→</i><b>Estratificar</b><i>→</i><b>Tratar</b></div>
    </div>
  );
}

function MockKnowledge() {
  return (
    <div className="cos-tour-mock cos-tour-mock--knowledge">
      <MiniTop contexto="Conhecimento conectado" />
      <div className="cos-tour-knowledge-head"><span className="cos-tour-kicker">Base clínica</span><strong>Conhecimento sem virar portal de links.</strong><small>Diretrizes, estudos, evidências, exames, casos e trilhas usam a mesma linguagem.</small></div>
      <div className="cos-tour-knowledge-grid">
        {[["evidencia","Evidências","Classe, nível e fonte"],["evidencia","Estudos","Literatura original"],["conhecimento","Guidelines","Recomendações"],["clinica","Exames","Critérios e interpretação"],["doencas","Casos clínicos","Raciocínio aplicado"],["curso","Trilhas","Estudo estruturado"]].map(([icone,titulo,detalhe]) => <span key={titulo}><Icone nome={icone as NomeIcone}/><b>{titulo}</b><small>{detalhe}</small><em>→</em></span>)}
      </div>
    </div>
  );
}

function MockCommunication() {
  return (
    <div className="cos-tour-mock cos-tour-mock--communication">
      <MiniTop contexto="CorVIA Mail" />
      <div className="cos-tour-communication-grid">
        <section><div className="cos-tour-mail-title"><Icone nome="mail"/><span><small>CorVIA Mail</small><strong>Comunicação profissional</strong></span></div>{["Paciente — retorno de exames","Equipe — discussão clínica","Convite científico"].map((texto,i) => <em key={texto} className={i===0?"is-new":""}><i/><span><b>{texto}</b><small>Mensagem profissional</small></span><time>{i===0?"Agora":"Ontem"}</time></em>)}</section>
        <section><div className="cos-tour-mail-title"><Icone nome="assistente"/><span><small>Assistente Pessoal</small><strong>Resumo sob demanda</strong></span></div><div className="cos-tour-chat"><i>Quais e-mails precisam da minha atenção?</i><i className="mine">Resuma apenas os não lidos.</i><i>Com sua autorização, eu organizo a prioridade.</i></div></section>
      </div>
    </div>
  );
}

function MockMobile() {
  const nav: Array<[NomeIcone,string]> = [["hoje","Início"],["busca","Buscar"],["pacientes","Pacientes"],["agenda","Agenda"],["mais","Mais"]];
  return (
    <div className="cos-tour-mock cos-tour-mock--mobile">
      <div className="cos-tour-phone">
        <header><img src="/corvia-mark-canonical.svg" alt=""/><Icone nome="menu"/></header>
        <main><span className="cos-tour-kicker">Clinical Command Center</span><strong>O que você precisa resolver agora?</strong><div className="cos-tour-mobile-command">✦ <span>Pergunte ou execute...</span></div><div className="cos-tour-mobile-actions">{[["prescricao","Prescrever"],["clinica","Exames"],["documento","Documento"],["emergencia","Emergência"]].map(([icone,nome])=><i key={nome}><Icone nome={icone as NomeIcone}/><b>{nome}</b></i>)}</div><div className="cos-tour-mobile-day"><small>Assistente Pessoal</small><b>Próximo compromisso · 14:00</b><em>Acesso pelo menu e pelo contexto da Home</em></div></main>
        <footer>{nav.map(([icone,nome]) => <i key={nome}><Icone nome={icone}/><small>{nome}</small></i>)}</footer>
      </div>
      <div className="cos-tour-mobile-copy"><span>Desktop para profundidade.</span><span>Mobile para velocidade.</span><strong>O mesmo CorVIA, desenhado para uma mão.</strong></div>
    </div>
  );
}

const SLIDES: Slide[] = [
  { id:"home", eyebrow:"Princípio-mãe", titulo:"Comece pela sua necessidade, não por um módulo.", resumo:"A Home pergunta o que você precisa resolver agora e aproxima pesquisa, conhecimento e ação.", promessa:"Pesquisar + perguntar + executar convergem no mesmo ponto.", icone:"hoje", pontos:["Command Bar universal", "Oito ações rápidas", "Continuidade por contexto, não apenas por paciente"], Mockup:MockHome },
  { id:"intelligence", eyebrow:"Contexto", titulo:"A inteligência aparece quando o contexto pede.", resumo:"CorVIA Intelligence mostra relações relevantes sem roubar espaço quando não há nada útil a acrescentar.", promessa:"Busca encontra. Intelligence percebe. Assistente conversa e executa com autorização.", icone:"clinica", pontos:["Rail contextual", "Clinical Thread sob demanda", "Workspace expande quando o rail não agrega"], Mockup:MockIntelligence },
  { id:"assistant", eyebrow:"Assistência contínua", titulo:"Clínica e rotina são inteligências diferentes, mas conectadas.", resumo:"Assistente Clínica pensa medicina; Assistente Pessoal organiza agenda, deslocamentos, e-mail e pendências com permissões reais.", promessa:"O médico não precisa carregar toda a própria rotina na cabeça.", icone:"assistente", pontos:["Consentimento explícito", "Briefing do dia", "Nada sensível é inventado ou carregado sem necessidade"], Mockup:MockAssistant, sinal:"green" },
  { id:"medication", eyebrow:"Medication Command Center", titulo:"Medicamento deixa de ser verbete e vira contexto de decisão.", resumo:"Dose, indicação, evidência, interação e prescrição vivem na mesma superfície.", promessa:"Conhecimento longo continua disponível, mas a decisão vem primeiro.", icone:"medicamento", pontos:["Status de revisão visível", "Prescrever como ação contextual", "Sem markdown cru ou resíduos editoriais"], Mockup:MockMedication },
  { id:"patient", eyebrow:"Patient Command Center", titulo:"Quando você entra no paciente, o paciente vira contexto — não o produto inteiro.", resumo:"Resumo, timeline, medicamentos, exames, prescrições e documentos se organizam ao redor da necessidade clínica.", promessa:"Paciente quando necessário; médico sempre no centro.", icone:"pacientes", pontos:["Resumo clínico condensado", "Ações rápidas", "Privacidade preservada"], Mockup:MockPatient },
  { id:"action", eyebrow:"Ação", titulo:"Quando a decisão termina, a execução já está ali.", resumo:"Prescrição, exames e documentos fazem parte do fluxo clínico e não de um sistema paralelo.", promessa:"Menos troca de contexto entre pensar, documentar e agir.", icone:"prescricao", pontos:["Solicitar Exames", "Emitir Atestado Médico", "Documento em Branco sem template obrigatório"], Mockup:MockAction },
  { id:"emergency", eyebrow:"Risco imediato", titulo:"Na emergência, o CorVIA fica mais simples — de propósito.", resumo:"Reconhecimento, primeiros minutos, estratificação e tratamento ganham prioridade visual.", promessa:"O visual acompanha a urgência em vez de competir com ela.", icone:"emergencia", pontos:["Protocolos rápidos", "Ações críticas próximas", "Vermelho reservado para risco"], Mockup:MockEmergency, sinal:"red" },
  { id:"knowledge", eyebrow:"Conhecimento", titulo:"Estudar, consultar e decidir usam a mesma base.", resumo:"Evidências, estudos, guidelines, exames, casos e trilhas deixam de parecer ilhas separadas.", promessa:"Aprofunde quando quiser sem perder aplicação clínica.", icone:"conhecimento", pontos:["Fontes rastreáveis", "Filtros progressivos", "Enums internos nunca chegam ao usuário"], Mockup:MockKnowledge },
  { id:"communication", eyebrow:"Comunicação", titulo:"Seu trabalho continua depois da consulta.", resumo:"CorVIA Mail permanece integrado ao Clinical OS e pode ser resumido pelo Assistente apenas quando autorizado.", promessa:"Comunicação profissional dentro do mesmo ambiente de trabalho.", icone:"mail", pontos:["Inbox premium", "CorVIA Chat permanece separado do Assistente", "HTML recebido isolado", "Assistente não lê caixa sem necessidade"], Mockup:MockCommunication },
  { id:"mobile", eyebrow:"Mobile", titulo:"No celular, a prioridade é alcançar a ação com uma mão.", resumo:"Mobile não é desktop empilhado: busca, pacientes, agenda e Mais têm ergonomia própria.", promessa:"O mesmo produto, com outra ergonomia.", icone:"menu", pontos:["Início · Buscar · Pacientes · Agenda · Mais", "Command Bar compacta", "Nenhum floating button cobre conteúdo"], Mockup:MockMobile },
];

const QUICK_IDS = ["home", "intelligence", "assistant", "medication", "patient", "emergency"];

function slidesDoModo(modo: Modo) {
  if (modo === "completo") return SLIDES;
  const ordem = new Map(QUICK_IDS.map((id, indice) => [id, indice]));
  return SLIDES.filter((slide) => ordem.has(slide.id)).sort((a, b) => (ordem.get(a.id) ?? 0) - (ordem.get(b.id) ?? 0));
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

  const slides = useMemo(() => {
    const base = slidesDoModo(modo);
    if (!usuario?.investidor) return base;
    return base.map((slide) => slide.id !== "communication" ? slide : { ...slide, pontos:[...slide.pontos, "Na conta de investidor, CorVIA Mail permanece em modo demonstração sem operações reais."] });
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
    try { await api.post("/auth/me/onboarding-concluido", {}); }
    catch (erro) { if (!(erro instanceof ApiError)) throw erro; }
    finally { window.location.replace("/"); }
  }

  function abrirCompleto() { setModo("completo"); setPasso(1); }

  return (
    <div className="cos-tour">
      <header className="cos-tour__top">
        <div className="cos-tour__brand"><img src="/corvia-logo-canonical-dark.svg" alt="CorVIA Clinical OS"/></div>
        <div className="cos-tour__mode"><i/><span>{modo === "quick" ? "Início rápido" : "Tour completo"}</span></div>
        <button type="button" className="cos-tour__skip" onClick={() => void concluir()} disabled={concluindo}>{pendente ? "Pular" : "Fechar"}</button>
      </header>

      <div className="cos-tour__progress" aria-label="Progresso do tour"><div style={{ width:`${((passo + 1) / total) * 100}%` }} /></div>
      <main className="cos-tour__stage">
        {boasVindas && <section className="cos-tour-welcome">
          <div className="cos-tour-welcome__glow" aria-hidden="true" />
          <p className="cos-tour-welcome__kicker">Bem-vindo ao CorVIA Clinical OS</p>
          <h1>Um sistema que começa pelo que você precisa resolver.</h1>
          <p className="cos-tour-welcome__lead">Não é prontuário. Não é só IA. Não é portal de conteúdo. É o workspace clínico inteligente do médico para pesquisar, decidir, executar e organizar o trabalho.</p>
          {usuario?.socio && <p className="cos-tour-welcome__entitlement">Acesso de sócio.</p>}
          {usuario?.investidor && <p className="cos-tour-welcome__entitlement">Modo investidor: arquitetura completa; CorVIA Mail demonstrativo e sem operações reais.</p>}
          <div className="cos-tour-welcome__pillars"><span>Necessidade</span><i>→</i><span>Contexto</span><i>→</i><span>Conhecimento</span><i>→</i><span>Decisão</span><i>→</i><span>Ação</span></div>
          <button type="button" className="cos-tour__primary" onClick={avancar}>Ver como o CorVIA trabalha <Icone nome="seta" /></button>
          <small className="cos-tour-welcome__hint">Use ← → no teclado. Você pode rever este tour depois.</small>
        </section>}

        {atual && <section className={`cos-tour-feature is-${atual.sinal ?? "cyan"}`} key={atual.id}>
          <div className="cos-tour-feature__visual"><atual.Mockup /></div>
          <div className="cos-tour-feature__copy">
            <div className="cos-tour-feature__counter"><span><Icone nome={atual.icone}/></span><small>{String(passo).padStart(2,"0")} / {String(total - 2).padStart(2,"0")}</small></div>
            <p className="cos-tour-feature__eyebrow">{atual.eyebrow}</p><h1>{atual.titulo}</h1><p className="cos-tour-feature__lead">{atual.resumo}</p><blockquote>“{atual.promessa}”</blockquote>
            <div className="cos-tour-feature__points">{atual.pontos.map((ponto) => <span key={ponto}><i><Icone nome="check"/></i>{ponto}</span>)}</div>
          </div>
        </section>}

        {final && <section className="cos-tour-final">
          <span className="cos-tour-final__mark"><img src="/corvia-mark-canonical.svg" alt="" /></span>
          <p className="cos-tour-welcome__kicker">Agora começa a rotina real</p>
          <h1>Entre pelo problema. O CorVIA aproxima o resto.</h1>
          <p>Pesquise, aprenda, decida, execute e organize seu dia sem precisar pensar primeiro em qual módulo abrir.</p>
          <div className="cos-tour-final__map"><span><b>Necessidade</b><small>O que preciso resolver?</small></span><i>→</i><span><b>Contexto</b><small>Onde estou?</small></span><i>→</i><span><b>Decisão</b><small>O que faz sentido?</small></span><i>→</i><span><b>Ação</b><small>Faça agora.</small></span></div>
          <button type="button" className="cos-tour__primary" onClick={() => void concluir()} disabled={concluindo}>{concluindo ? "Abrindo o CorVIA…" : "Abrir meu Clinical Command Center"} <Icone nome="seta" /></button>
          {modo === "quick" && <button type="button" className="cos-tour__secondary" onClick={abrirCompleto}>Quero ver o tour completo</button>}
        </section>}
      </main>

      {!boasVindas && !final && <footer className="cos-tour__controls">
        <button type="button" className="cos-tour__back" onClick={voltar}><span>←</span> Voltar</button>
        <div className="cos-tour__dots" role="progressbar" aria-valuenow={passo+1} aria-valuemin={1} aria-valuemax={total}>{Array.from({ length:total }).map((_,indice)=><button key={indice} type="button" aria-label={`Ir para etapa ${indice+1}`} className={`${indice===passo?"is-current":""}${indice<passo?" is-done":""}`} onClick={()=>setPasso(indice)}/>)}</div>
        <button type="button" className="cos-tour__next" onClick={avancar}>Próximo <span>→</span></button>
      </footer>}
    </div>
  );
}
