import { useCallback, useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import CardiologySpaceScene, { type CardiologySpaceSceneId } from "../components/CardiologySpaceScene";
import Icone, { type NomeIcone } from "../components/Icone";
import { CoracaoHolografico } from "../components/PreHomeBrand";
import { api, ApiError } from "../lib/api";
import { useAuth } from "../lib/auth";
import { nomeComTratamento } from "../lib/clinicalIdentity";
import "../styles/cardiology-spaces-tour.css";

type Visual = "modes" | "spaces" | "motion" | "layers" | "essential" | "scientific" | "relations" | "care";
type Step = {
  eyebrow:string;
  title:string;
  text:string;
  icon:NomeIcone;
  visual:Visual;
  points:string[];
  action:string;
};

const STEPS: Step[] = [
  {
    eyebrow:"01 · SUA EXPERIÊNCIA",
    title:"Você escolhe o nível de profundidade antes de começar.",
    text:"Completo abre três camadas de decisão. Essencial preserva o contexto e mostra somente os atalhos escolhidos. Ciência & Ensino organiza a jornada acadêmica sem duplicar conteúdo.",
    icon:"configuracao",
    visual:"modes",
    points:["Consultório é o início clínico", "Preferência vale apenas para este acesso", "Nenhuma função desaparece"],
    action:"Experimente alternar os três modos",
  },
  {
    eyebrow:"02 · CINCO AMBIENTES",
    title:"Cada porta representa um lugar real da sua rotina.",
    text:"Consultório, Hospital, Ensino, Pesquisa e Gestão têm interiores, prioridades e linguagem próprios. O CorVIA reorganiza o trabalho sem tirar o médico do centro.",
    icon:"clinica",
    visual:"spaces",
    points:["Interiores exclusivos", "Cores e ícones consistentes", "Mesmo comportamento no toque"],
    action:"Abra as portas para conhecer cada interior",
  },
  {
    eyebrow:"03 · FOCO E PROFUNDIDADE",
    title:"O ambiente em foco avança; os demais aguardam.",
    text:"Passe o mouse, use o teclado ou toque em outra porta. Ela ganha luz e profundidade imediatamente. Ao sair, o ambiente selecionado reassume o foco.",
    icon:"conta",
    visual:"motion",
    points:["Hover antecipa", "Clique ou toque seleciona", "Foco de teclado equivalente"],
    action:"Mude o destaque e observe a profundidade",
  },
  {
    eyebrow:"04 · PRIORIDADE CLÍNICA",
    title:"Agora, em seguida e referências formam uma sequência.",
    text:"A primeira camada reúne ações imediatas. A segunda prepara o próximo passo. A terceira traz somente referências úteis ao ambiente ativo.",
    icon:"agenda",
    visual:"layers",
    points:["Ações distribuídas por igual", "Sem espaços vazios", "Contexto muda com a porta"],
    action:"Percorra as três camadas do Hospital",
  },
  {
    eyebrow:"05 · ESSENCIAL",
    title:"Velocidade sem perder o sistema completo.",
    text:"Monte uma bancada curta com até oito funções. Ela fica salva no seu perfil local, pode ser restaurada e continua ligada a todas as áreas do CorVIA.",
    icon:"configuracao",
    visual:"essential",
    points:["Até oito atalhos", "Personalização reversível", "Acesso integral preservado"],
    action:"Selecione os itens da sua bancada",
  },
  {
    eyebrow:"06 · CIÊNCIA & ENSINO",
    title:"Descobrir, validar, aprender, ensinar e produzir.",
    text:"A jornada científica conecta biblioteca, evidências, estudos, cursos, trilhas, casos, apresentações e documentos assistidos por IA em um fluxo único.",
    icon:"conhecimento",
    visual:"scientific",
    points:["Fontes rastreáveis", "Aprendizagem contínua", "Produção científica conectada"],
    action:"Navegue pelas cinco jornadas científicas",
  },
  {
    eyebrow:"07 · TUDO COM TUDO",
    title:"Uma relação só aparece quando existe contexto clínico.",
    text:"A busca aproxima doenças, exames, medicamentos, diretrizes, evidências e calculadoras por assunto específico. Relações genéricas ou sem sustentação ficam de fora.",
    icon:"sincronizar",
    visual:"relations",
    points:["Assunto no centro", "Relações específicas", "Origem sempre acessível"],
    action:"Siga as conexões de fibrilação atrial",
  },
  {
    eyebrow:"08 · INTELIGÊNCIA INTEGRADA",
    title:"Discussão clínica e acompanhamento continuam no mesmo espaço.",
    text:"O Heart Team Virtual estrutura opiniões independentes e o Assistente CorVIA no WhatsApp acompanha rotinas autorizadas. Confirmação humana e rastreabilidade permanecem obrigatórias.",
    icon:"round",
    visual:"care",
    points:["Heart Team multiprofissional", "WhatsApp com consentimento", "Decisão final sempre humana"],
    action:"Conheça os dois fluxos inteligentes",
  },
];

const CLINICAL: Array<[CardiologySpaceSceneId,string,NomeIcone]> = [
  ["consultorio","Consultório","conta"],
  ["hospital","Hospital","emergencia"],
  ["ensino","Ensino","curso"],
  ["pesquisa","Pesquisa","evidencia"],
  ["gestao","Gestão","gestao"],
];
const SCIENTIFIC: Array<[CardiologySpaceSceneId,string,NomeIcone]> = [
  ["descobrir","Descobrir","busca"],
  ["evidencias","Evidências","evidencia"],
  ["aprender","Aprender","curso"],
  ["ensinar","Ensinar","comunicacao"],
  ["produzir","Produzir","documento"],
];

function Brand() {
  return <span className="cst__brand"><img src="/corvia-mark-canonical.svg" alt=""/><span><strong>Cor<b>VIA</b></strong><small>CARDIOLOGY SPACES</small></span></span>;
}

function DoorsVisual({ items, initial=0 }: { items:Array<[CardiologySpaceSceneId,string,NomeIcone]>; initial?:number }) {
  const [active,setActive] = useState(initial);
  return <div className="cst-doors" role="group" aria-label="Experimentar ambientes">
    {items.map(([id,label,icon],index)=><button type="button" className={index===active?"is-active":""} key={id} onMouseEnter={()=>setActive(index)} onFocus={()=>setActive(index)} onClick={()=>setActive(index)} aria-pressed={index===active}>
      <span><Icone nome={icon}/>{label}</span><i><CardiologySpaceScene space={id}/></i>
    </button>)}
  </div>;
}

function ModesVisual() {
  const [mode,setMode]=useState<"Completo"|"Essencial"|"Ciência & Ensino">("Completo");
  return <div className="cst-modes">
    {(["Completo","Essencial","Ciência & Ensino"] as const).map((item,index)=><button type="button" className={mode===item?"is-active":""} onClick={()=>setMode(item)} key={item}>
      <Icone nome={index===0?"gestao":index===1?"configuracao":"conhecimento"}/>
      <small>{index===0?"TRÊS CAMADAS":index===1?"SUA BANCADA":"JORNADA CIENTÍFICA"}</small>
      <strong>{item}</strong>
      <span>{index===0?"Visão integral por ambiente":index===1?"Atalhos escolhidos por você":"Descobrir, aprender e produzir"}</span>
      <i><Icone nome={mode===item?"check":"seta"}/></i>
    </button>)}
  </div>;
}

function LayersVisual() {
  return <div className="cst-layers">
    <span className="is-now"><small>AGORA</small><strong><Icone nome="round"/> Abrir round</strong><strong><Icone nome="documento"/> Registrar evolução</strong><strong><Icone nome="prescricao"/> Prescrever</strong></span>
    <span><small>EM SEGUIDA</small><strong><Icone nome="ecg"/> Revisar exames</strong><strong><Icone nome="documento"/> Documentos para assinar</strong><strong><Icone nome="check"/> Checklists</strong></span>
    <span><small>REFERÊNCIAS</small><strong><Icone nome="conhecimento"/> Protocolos</strong><strong><Icone nome="calculadora"/> Calculadoras</strong><strong><Icone nome="clinica"/> Cardiologia Intensiva</strong></span>
  </div>;
}

function EssentialVisual() {
  const options=["Agenda","Prescrever","Prontuário","Documentos","Exames","Calculadoras"];
  const [selected,setSelected]=useState(options.slice(0,4));
  return <div className="cst-essential"><header><span><Icone nome="configuracao"/></span><div><small>MEU ESSENCIAL</small><strong>{selected.length}/8 funções escolhidas</strong></div></header><div>{options.map((item,index)=><button type="button" className={selected.includes(item)?"is-active":""} key={item} onClick={()=>setSelected(current=>current.includes(item)?current.filter(value=>value!==item):[...current,item].slice(0,8))}><Icone nome={(["agenda","prescricao","pacientes","documento","ecg","calculadora"] as NomeIcone[])[index]}/><span>{item}</span><Icone nome={selected.includes(item)?"check":"adicionar"}/></button>)}</div></div>;
}

function RelationsVisual() {
  return <div className="cst-relations"><strong><small>ASSUNTO ATIVO</small>Fibrilação atrial</strong>
    <span className="is-disease"><Icone nome="doencas"/><b>Doença</b><small>contexto</small></span>
    <span className="is-exam"><Icone nome="ecg"/><b>Exames</b><small>diagnóstico</small></span>
    <span className="is-drug"><Icone nome="medicamento"/><b>Medicamentos</b><small>tratamento</small></span>
    <span className="is-guideline"><Icone nome="conhecimento"/><b>Diretrizes</b><small>recomendação</small></span>
    <span className="is-evidence"><Icone nome="evidencia"/><b>Evidências</b><small>rastreabilidade</small></span>
    <span className="is-score"><Icone nome="calculadora"/><b>Calculadoras</b><small>risco</small></span>
  </div>;
}

function CareVisual() {
  const [active,setActive]=useState<"heart"|"whatsapp">("heart");
  return <div className="cst-care">
    <button type="button" className={active==="heart"?"is-active":""} onClick={()=>setActive("heart")}><span><Icone nome="round"/></span><small>DISCUSSÃO ESTRUTURADA</small><strong>Heart Team Virtual</strong><p>Cardiologia clínica, intervenção, cirurgia e imagem respondem de forma independente.</p><i>Decisão compartilhada <Icone nome="seta"/></i></button>
    <button type="button" className={active==="whatsapp"?"is-active":""} onClick={()=>setActive("whatsapp")}><span><Icone nome="comunicacao"/></span><small>ROTINA AUTORIZADA</small><strong>Assistente no WhatsApp</strong><p>Lembretes e acompanhamento com consentimento, confirmação e registro.</p><i>Continuidade segura <Icone nome="seta"/></i></button>
  </div>;
}

function TourVisual({ type }: { type:Visual }) {
  if(type==="modes") return <ModesVisual/>;
  if(type==="spaces") return <DoorsVisual items={CLINICAL}/>;
  if(type==="motion") return <DoorsVisual items={CLINICAL} initial={1}/>;
  if(type==="layers") return <LayersVisual/>;
  if(type==="essential") return <EssentialVisual/>;
  if(type==="scientific") return <DoorsVisual items={SCIENTIFIC}/>;
  if(type==="relations") return <RelationsVisual/>;
  return <CareVisual/>;
}

export default function CardiologySpacesTour() {
  const { usuario } = useAuth();
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const [step,setStep] = useState(0);
  const [finishing,setFinishing] = useState(false);
  const [error,setError] = useState("");
  const total = STEPS.length + 2;
  const requested = params.get("retorno") || "/";
  const destination = requested.startsWith("/") && !requested.startsWith("//") ? requested : "/";
  const next = useCallback(()=>setStep(current=>Math.min(current+1,total-1)),[total]);
  const back = useCallback(()=>setStep(current=>Math.max(current-1,0)),[]);

  const finish = useCallback(async()=>{
    if(finishing) return;
    setFinishing(true);
    setError("");
    if(usuario?.onboarding_pendente) {
      try {
        await api.post("/auth/me/onboarding-concluido",{});
      } catch (caught) {
        setError(caught instanceof ApiError ? caught.message : "Não foi possível concluir o tour. Tente novamente.");
        setFinishing(false);
        return;
      }
      window.location.replace(destination);
      return;
    }
    navigate(destination,{replace:true});
  },[destination,finishing,navigate,usuario?.onboarding_pendente]);

  useEffect(()=>{
    const keyboard=(event:KeyboardEvent)=>{
      if(event.key==="ArrowRight") next();
      if(event.key==="ArrowLeft") back();
      if(event.key==="Escape") void finish();
    };
    window.addEventListener("keydown",keyboard);
    return()=>window.removeEventListener("keydown",keyboard);
  },[back,finish,next]);

  const welcome=step===0;
  const final=step===total-1;
  const current=!welcome&&!final?STEPS[step-1]:null;
  const firstName=nomeComTratamento(usuario,true);

  return <main className="cst">
    <header className="cst__header"><Brand/><span>EXPERIÊNCIA GUIADA · {String(step+1).padStart(2,"0")}/{String(total).padStart(2,"0")}</span><button type="button" onClick={()=>void finish()} disabled={finishing}>Pular tour</button></header>
    <div className="cst__progress" aria-hidden="true"><i style={{width:`${((step+1)/total)*100}%`}}/></div>

    {welcome&&<section className="cst__welcome">
      <div className="cst__heart"><CoracaoHolografico/></div>
      <p>O MÉDICO CONTINUA NO CENTRO</p>
      <h1>Bem-vindo, {firstName}.<br/><strong>Entre nos seus Cardiology Spaces.</strong></h1>
      <span>Uma experiência interativa em oito capítulos: escolha modos, abra portas, reorganize prioridades e conheça as conexões inteligentes do CorVIA.</span>
      <div className="cst__welcome-map">{STEPS.map(item=><i key={item.eyebrow}><Icone nome={item.icon}/></i>)}</div>
      <button type="button" onClick={next}>Começar experiência <Icone nome="seta"/></button>
    </section>}

    {current&&<section className="cst__step" aria-live="polite">
      <div className="cst__visual" key={current.visual}><div className="cst__visual-head"><span>DEMONSTRAÇÃO INTERATIVA</span><small>{current.action}</small></div><TourVisual type={current.visual}/></div>
      <article>
        <span className="cst__step-icon"><Icone nome={current.icon}/></span>
        <p>{current.eyebrow}</p>
        <h1>{current.title}</h1>
        <div className="cst__step-copy">{current.text}</div>
        <ul>{current.points.map(point=><li key={point}><Icone nome="check"/>{point}</li>)}</ul>
        <small>O ambiente muda. O médico continua no centro.</small>
      </article>
    </section>}

    {final&&<section className="cst__final">
      <img src="/corvia-mark-canonical.svg" alt=""/>
      <p>EXPERIÊNCIA CONCLUÍDA</p>
      <h1>O espaço está pronto.<br/><strong>Escolha como trabalhar hoje.</strong></h1>
      <span>O tour permanece disponível em Ajuda. Usuários novos o veem uma vez; perfis de investidor o recebem no início de cada nova sessão.</span>
      {error&&<strong className="cst__error" role="alert">{error}</strong>}
      <button type="button" onClick={()=>void finish()} disabled={finishing}>{finishing?"Preparando seu espaço…":"Entrar no Cardiology Spaces"} <Icone nome="seta"/></button>
    </section>}

    {!welcome&&!final&&<footer className="cst__controls">
      <button type="button" onClick={back}>← Voltar</button>
      <div>{Array.from({length:total}).map((_,index)=><button type="button" key={index} aria-label={`Ir para etapa ${index+1}`} className={`${index===step?"is-active":""}${index<step?" is-done":""}`} onClick={()=>setStep(index)}/>)}</div>
      <button type="button" onClick={next}>Próximo →</button>
    </footer>}
  </main>;
}
