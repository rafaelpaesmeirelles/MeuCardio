import { useCallback, useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import CardiologySpaceScene, { type CardiologySpaceSceneId } from "../components/CardiologySpaceScene";
import Icone, { type NomeIcone } from "../components/Icone";
import { CoracaoHolografico } from "../components/PreHomeBrand";
import { api, ApiError } from "../lib/api";
import { useAuth } from "../lib/auth";
import "../styles/cardiology-spaces-tour.css";

const TOUR_KEY = "corvia:cardiology-spaces:tour:v2";
type Visual = "spaces" | "layers" | "relations" | "essential" | "scientific";
const STEPS: Array<{ eyebrow:string; title:string; text:string; icon:NomeIcone; visual:Visual }> = [
  { eyebrow:"01 · AMBIENTES", title:"Comece por onde você está trabalhando.", text:"Consultório, Hospital, Ensino, Pesquisa e Gestão reorganizam o sistema sem esconder nenhuma função.", icon:"clinica", visual:"spaces" },
  { eyebrow:"02 · PRIORIDADE", title:"O que importa agora vem primeiro.", text:"Cada ambiente mostra Agora, Em seguida e Referências. Ao trocar de espaço, as ações mudam com o contexto.", icon:"agenda", visual:"layers" },
  { eyebrow:"03 · TUDO COM TUDO", title:"Conhecimento e ação permanecem conectados.", text:"Doenças, exames, medicamentos, diretrizes, estudos, calculadoras e documentos se aproximam quando fazem sentido.", icon:"sincronizar", visual:"relations" },
  { eyebrow:"04 · SEU JEITO", title:"Completo quando precisar. Essencial quando quiser velocidade.", text:"Personalize seus atalhos sem perder acesso ao sistema integral. Em ambos, o Consultório é o ponto inicial.", icon:"configuracao", visual:"essential" },
  { eyebrow:"05 · CIÊNCIA & ENSINO", title:"Descubra, aprenda, ensine e produza em uma jornada própria.", text:"O terceiro ambiente reúne biblioteca, Tudo com Tudo, diretrizes, evidências, estudos, cursos, trilhas, casos, apresentações e exportações sem duplicar o conteúdo.", icon:"conhecimento", visual:"scientific" },
];
const CLINICAL: Array<[CardiologySpaceSceneId,string]> = [["consultorio","Consultório"],["hospital","Hospital"],["ensino","Ensino"],["pesquisa","Pesquisa"],["gestao","Gestão"]];
const SCIENTIFIC: Array<[CardiologySpaceSceneId,string]> = [["descobrir","Descobrir"],["evidencias","Evidências"],["aprender","Aprender"],["ensinar","Ensinar"],["produzir","Produzir"]];

function Brand() { return <span className="cst__brand"><img src="/corvia-mark-canonical.svg" alt=""/><span><strong>Cor<b>VIA</b></strong><small>CARDIOLOGY SPACES</small></span></span>; }
function Doors({ items }: { items:Array<[CardiologySpaceSceneId,string]> }) { return <div className="cst-doors">{items.map(([id,label],i)=><span className={i===0?"is-active":""} key={id}><b>{label}</b><i><CardiologySpaceScene space={id}/></i></span>)}</div>; }
function TourVisual({ type }:{ type:Visual }) {
  if (type === "spaces") return <Doors items={CLINICAL}/>;
  if (type === "scientific") return <Doors items={SCIENTIFIC}/>;
  if (type === "layers") return <div className="cst-layers"><span><small>AGORA</small><b>Abrir agenda</b><b>Prescrever</b><b>Prontuário</b></span><span><small>EM SEGUIDA</small><b>Solicitar exames</b><b>Revisar resultados</b></span><span><small>REFERÊNCIAS</small><b>Diretrizes</b><b>Calculadoras</b><b>Interações</b></span></div>;
  if (type === "relations") return <div className="cst-relations"><strong>Tudo com Tudo</strong>{["Doença","Exame","Medicamento","Diretriz","Evidência","Calculadora"].map(label=><span key={label}>{label}</span>)}</div>;
  return <div className="cst-essential"><section><small>COMPLETO</small><strong>Visão integral</strong><span>3 camadas · todos os ambientes</span></section><section className="is-active"><small>ESSENCIAL</small><strong>Sua rotina</strong><span>Atalhos escolhidos por você</span></section></div>;
}

export default function CardiologySpacesTour() {
  const { usuario } = useAuth();
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const [step,setStep] = useState(0);
  const [finishing,setFinishing] = useState(false);
  const total = STEPS.length + 2;
  const requested = params.get("retorno") || "/";
  const destination = requested.startsWith("/") && !requested.startsWith("//") ? requested : "/";
  const next = useCallback(()=>setStep(current=>Math.min(current+1,total-1)),[total]);
  const back = useCallback(()=>setStep(current=>Math.max(current-1,0)),[]);

  async function finish() {
    if (finishing) return;
    setFinishing(true);
    localStorage.setItem(TOUR_KEY,"seen");
    if (usuario?.onboarding_pendente) {
      try { await api.post("/auth/me/onboarding-concluido",{}); }
      catch (error) { if (!(error instanceof ApiError)) throw error; }
      finally { window.location.replace(destination); }
      return;
    }
    navigate(destination,{ replace:true });
  }
  useEffect(()=>{
    const keyboard=(event:KeyboardEvent)=>{ if(event.key==="ArrowRight")next(); if(event.key==="ArrowLeft")back(); if(event.key==="Escape"&&!usuario?.onboarding_pendente)void finish(); };
    window.addEventListener("keydown",keyboard); return()=>window.removeEventListener("keydown",keyboard);
  });
  const welcome=step===0; const final=step===total-1; const current=!welcome&&!final?STEPS[step-1]:null;
  return <main className="cst">
    <header className="cst__header"><Brand/><span>TOUR CARDIOLOGY SPACES</span><button onClick={()=>void finish()} disabled={finishing}>Pular</button></header>
    <div className="cst__progress"><i style={{width:`${((step+1)/total)*100}%`}}/></div>
    {welcome&&<section className="cst__welcome"><div className="cst__heart"><CoracaoHolografico/></div><p>O MÉDICO CONTINUA NO CENTRO</p><h1>Bem-vindo aos seus<br/><strong>ambientes de cardiologia.</strong></h1><span>Veja como o CorVIA organiza sua rotina, sua aprendizagem e seu ensino.</span><button onClick={next}>Começar o tour <Icone nome="seta"/></button></section>}
    {current&&<section className="cst__step"><div className="cst__visual"><TourVisual type={current.visual}/></div><article><span className="cst__step-icon"><Icone nome={current.icon}/></span><p>{current.eyebrow}</p><h1>{current.title}</h1><div>{current.text}</div><small>O ambiente muda. O médico continua no centro.</small></article></section>}
    {final&&<section className="cst__final"><img src="/corvia-mark-canonical.svg" alt=""/><p>PRONTO PARA COMEÇAR</p><h1>Escolha seu modo.<br/><strong>O CorVIA acompanha você.</strong></h1><span>Você pode rever este tour a qualquer momento em Ajuda.</span><button onClick={()=>void finish()} disabled={finishing}>{finishing?"Abrindo…":"Entrar no Cardiology Spaces"} <Icone nome="seta"/></button></section>}
    {!welcome&&!final&&<footer className="cst__controls"><button onClick={back}>← Voltar</button><div>{Array.from({length:total}).map((_,index)=><button key={index} aria-label={`Ir para etapa ${index+1}`} className={`${index===step?"is-active":""}${index<step?" is-done":""}`} onClick={()=>setStep(index)}/>)}</div><button onClick={next}>Próximo →</button></footer>}
  </main>;
}
