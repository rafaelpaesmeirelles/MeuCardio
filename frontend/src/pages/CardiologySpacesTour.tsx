import { useCallback, useEffect, useState, type CSSProperties } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import CardiologySpaceScene, { type CardiologySpaceSceneId } from "../components/CardiologySpaceScene";
import Icone, { type NomeIcone } from "../components/Icone";
import { CoracaoHolografico } from "../components/PreHomeBrand";
import { api, ApiError } from "../lib/api";
import { useAuth } from "../lib/auth";
import { nomeComTratamento } from "../lib/clinicalIdentity";
import "../styles/cardiology-spaces-tour.css";

const TOUR_KEY = "corvia:cardiology-spaces:tour:v3";
const INVESTOR_TOUR_SESSION_KEY = "corvia:cardiology-spaces:investor-tour-session:v1";
type Visual = "modes" | "spaces" | "layers" | "day" | "orbit" | "relations" | "scientific" | "essential";
type Step = { eyebrow: string; title: string; text: string; detail: string; icon: NomeIcone; visual: Visual };

const STEPS: Step[] = [
  {
    eyebrow: "01 · ESCOLHA A EXPERIÊNCIA",
    title: "O mesmo CorVIA. Três formas de entrar.",
    text: "Completo oferece visão integral. Essencial reduz ruído e prioriza sua rotina. Ciência & Ensino transforma o acervo em uma jornada de descoberta, aprendizagem e produção.",
    detail: "Nenhuma função clínica é perdida ao trocar de experiência.", icon: "gestao", visual: "modes",
  },
  {
    eyebrow: "02 · CARDIOLOGY SPACES",
    title: "Entre no ambiente em que o trabalho acontece.",
    text: "Consultório, Hospital, Ensino, Pesquisa e Gestão aparecem como portais. Passe sobre um ambiente para antever suas prioridades; clique para torná-lo ativo.",
    detail: "O portal selecionado cresce e ilumina, exatamente como um espaço em uso.", icon: "clinica", visual: "spaces",
  },
  {
    eyebrow: "03 · AGORA, DEPOIS, REFERÊNCIA",
    title: "A hierarquia muda com o contexto, não o sistema.",
    text: "Cada espaço reorganiza ações em camadas. O que exige atenção imediata fica em Agora; tarefas seguintes e referências permanecem logo abaixo.",
    detail: "No Essencial, a segunda camada vira Meus Essenciais e pode ser personalizada por espaço.", icon: "agenda", visual: "layers",
  },
  {
    eyebrow: "04 · MEU DIA ENTRE ESPAÇOS",
    title: "Agenda, compromissos e rotinas no mesmo trilho.",
    text: "A lateral direita combina atendimentos, compromissos manuais e rotinas profissionais do dia. Assim, o CorVIA acompanha a sequência real da sua jornada.",
    detail: "O horário e o local vêm das mesmas fontes da Agenda integrada.", icon: "relogio", visual: "day",
  },
  {
    eyebrow: "05 · DESLOCAMENTO",
    title: "O caminho vira uma viagem entre espaços.",
    text: "Ao tocar em Deslocamento, o CorVIA prepara o próximo destino, usa sua localização apenas naquele momento e calcula trânsito, distância e rota recomendada.",
    detail: "A visualização orbital é CorVIA; o botão de navegação abre o mapa real no dispositivo.", icon: "rota", visual: "orbit",
  },
  {
    eyebrow: "06 · TUDO COM TUDO",
    title: "Conhecimento deixa de ser uma coleção de telas.",
    text: "Doenças, exames, medicamentos, diretrizes, estudos, evidências, calculadoras, casos e documentos se conectam para reduzir saltos e reconstrução mental.",
    detail: "A mesma rede atravessa Consultório, Hospital, Ensino e Pesquisa.", icon: "sincronizar", visual: "relations",
  },
  {
    eyebrow: "07 · CIÊNCIA & ENSINO",
    title: "Descobrir, validar, aprender, ensinar e produzir.",
    text: "O ambiente científico usa a mesma linguagem visual, mas troca os portais clínicos por jornadas de conhecimento. Biblioteca, evidências, trilhas, casos, apresentação e documento IA permanecem conectados.",
    detail: "A opção Cursos não faz mais parte da experiência.", icon: "conhecimento", visual: "scientific",
  },
  {
    eyebrow: "08 · SEU CORVIA",
    title: "Essencial é pessoal — e continua completo.",
    text: "Escolha os atalhos que realmente importam em cada espaço. Consultório pode ter uma seleção; Hospital, Pesquisa e os demais podem ter outra.",
    detail: "O catálogo integral continua disponível a qualquer momento.", icon: "configuracao", visual: "essential",
  },
];

const CLINICAL: Array<[CardiologySpaceSceneId, string]> = [["consultorio", "Consultório"], ["hospital", "Hospital"], ["ensino", "Ensino"], ["pesquisa", "Pesquisa"], ["gestao", "Gestão"]];
const SCIENTIFIC: Array<[CardiologySpaceSceneId, string]> = [["descobrir", "Descobrir"], ["evidencias", "Evidências"], ["aprender", "Aprender"], ["ensinar", "Ensinar"], ["produzir", "Produzir"]];

function Brand() {
  return <span className="cst__brand"><img src="/corvia-mark-canonical.svg" alt="" /><span><strong>Cor<b>VIA</b></strong><small>CARDIOLOGY SPACES</small></span></span>;
}

function Doors({ items, activeIndex = 1 }: { items: Array<[CardiologySpaceSceneId, string]>; activeIndex?: number }) {
  return <div className="cst-doors">{items.map(([id, label], index) => <span className={index === activeIndex ? "is-active" : ""} key={id}><b>{label}</b><i><CardiologySpaceScene space={id} /></i></span>)}</div>;
}

function TourVisual({ type }: { type: Visual }) {
  if (type === "modes") return <div className="cst-modes"><section><small>COMPLETO</small><strong>Visão integral</strong><span>Agora · Em seguida · Referências</span></section><section className="is-active"><small>ESSENCIAL</small><strong>Sua rotina</strong><span>Agora · Meus essenciais</span></section><section><small>CIÊNCIA & ENSINO</small><strong>Conhecimento conectado</strong><span>Descobrir · Aprender · Produzir</span></section></div>;
  if (type === "spaces") return <Doors items={CLINICAL} />;
  if (type === "scientific") return <Doors items={SCIENTIFIC} activeIndex={2} />;
  if (type === "layers") return <div className="cst-layers"><span className="is-now"><small>AGORA</small><b>Abrir round</b><b>Registrar evolução</b><b>Prescrever</b></span><span><small>EM SEGUIDA</small><b>Revisar exames</b><b>Documentos</b><b>Checklists</b></span><span><small>REFERÊNCIAS</small><b>Diretrizes</b><b>Calculadoras</b><b>Emergências</b></span></div>;
  if (type === "day") return <div className="cst-day"><h3>Meu dia entre espaços</h3><span className="blue"><i /><b>Hospital</b><small>07:00–13:00</small></span><span className="cyan"><i /><b>Consultório</b><small>15:00–18:00</small></span><span className="violet"><i /><b>Estudo</b><small>20:00</small></span><strong><Icone nome="rota" /> Deslocamento <small>18 min</small></strong></div>;
  if (type === "orbit") return <div className="cst-orbit"><span className="planet origin"><i /><b>AGORA</b></span><span className="route"><i /></span><span className="planet destination"><i /><b>HOSPITAL</b></span><em>18 min · rota recomendada</em></div>;
  if (type === "relations") return <div className="cst-relations"><strong>Tudo com Tudo</strong>{["Doença", "Exame", "Medicamento", "Diretriz", "Evidência", "Calculadora", "Caso", "Documento"].map((label, index) => <span style={{ "--i": index } as CSSProperties} key={label}>{label}</span>)}</div>;
  return <div className="cst-essential"><section><small>CONSULTÓRIO</small><strong>Prescrever</strong><span>Agenda · Prontuário · Exames</span></section><section className="is-active"><small>HOSPITAL</small><strong>Round</strong><span>Exames · Documentos · Checklists</span></section><section><small>PESQUISA</small><strong>Evidências</strong><span>Estudos · Biblioteca · Exportar</span></section></div>;
}

export default function CardiologySpacesTour() {
  const { usuario } = useAuth();
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const [step, setStep] = useState(0);
  const [finishing, setFinishing] = useState(false);
  const total = STEPS.length + 2;
  const requested = params.get("retorno") || "/";
  const destination = (() => {
    try {
      const resolved = new URL(requested, window.location.origin);
      if (resolved.origin !== window.location.origin) return "/";
      return `${resolved.pathname}${resolved.search}${resolved.hash}`;
    } catch {
      return "/";
    }
  })();
  const next = useCallback(() => setStep((current) => Math.min(current + 1, total - 1)), [total]);
  const back = useCallback(() => setStep((current) => Math.max(current - 1, 0)), []);
  const manual = !usuario?.onboarding_pendente && !usuario?.investidor;
  const callName = nomeComTratamento(usuario, true);

  async function finish() {
    if (finishing) return;
    setFinishing(true);
    localStorage.setItem(TOUR_KEY, "seen");
    if (usuario?.investidor) sessionStorage.setItem(INVESTOR_TOUR_SESSION_KEY, "seen");
    if (usuario?.onboarding_pendente) {
      try { await api.post("/auth/me/onboarding-concluido", {}); }
      catch (error) { if (!(error instanceof ApiError)) throw error; }
      finally { window.location.replace(destination); }
      return;
    }
    navigate(destination, { replace: true });
  }

  useEffect(() => {
    const keyboard = (event: KeyboardEvent) => {
      if (event.key === "ArrowRight") next();
      if (event.key === "ArrowLeft") back();
      if (event.key === "Escape" && manual) navigate(destination, { replace: true });
    };
    window.addEventListener("keydown", keyboard);
    return () => window.removeEventListener("keydown", keyboard);
  }, [back, destination, manual, navigate, next]);

  const welcome = step === 0;
  const final = step === total - 1;
  const current = !welcome && !final ? STEPS[step - 1] : null;

  return <main className="cst">
    <header className="cst__header"><Brand /><span>TOUR CARDIOLOGY SPACES</span>{manual ? <button onClick={() => navigate(destination, { replace: true })}>Sair</button> : <em>{usuario?.investidor ? "MODO INVESTIDOR" : "NOVO USUÁRIO"}</em>}</header>
    <div className="cst__progress"><i style={{ width: `${((step + 1) / total) * 100}%` }} /></div>

    {welcome && <section className="cst__welcome"><div className="cst__heart"><CoracaoHolografico /></div><p>O MÉDICO CONTINUA NO CENTRO</p><h1>Bem-vindo, {callName}.<br /><strong>Isto é Cardiology Spaces.</strong></h1><span>Não é um menu novo. É uma forma de o CorVIA reconhecer onde você está, o que importa agora e qual conhecimento precisa estar ao alcance.</span><button onClick={next}>Entrar nos espaços <Icone nome="seta" /></button></section>}

    {current && <section className="cst__step"><div className="cst__visual"><TourVisual type={current.visual} /></div><article><span className="cst__step-icon"><Icone nome={current.icon} /></span><p>{current.eyebrow}</p><h1>{current.title}</h1><div>{current.text}</div><small>{current.detail}</small></article></section>}

    {final && <section className="cst__final"><div className="cst__heart cst__heart--final"><CoracaoHolografico /></div><img src="/corvia-mark-canonical.svg" alt="" /><p>PRONTO PARA COMEÇAR</p><h1>Escolha seu espaço.<br /><strong>O CorVIA acompanha a jornada.</strong></h1><span>{usuario?.investidor ? "A demonstração abre em modo somente leitura. Este tour volta a aparecer em uma nova sessão do perfil Investidor." : "A partir de agora, o tour não será exibido automaticamente novamente."}</span><button onClick={() => void finish()} disabled={finishing}>{finishing ? "Abrindo…" : "Entrar no Cardiology Spaces"} <Icone nome="seta" /></button></section>}

    {!welcome && !final && <footer className="cst__controls"><button onClick={back}>← Voltar</button><div>{Array.from({ length: total }).map((_, index) => <button key={index} aria-label={`Ir para etapa ${index + 1}`} className={`${index === step ? "is-active" : ""}${index < step ? " is-done" : ""}`} onClick={() => setStep(index)} />)}</div><button onClick={next}>Próximo →</button></footer>}
  </main>;
}
