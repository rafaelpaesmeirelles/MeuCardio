import { useEffect, useMemo, useState, type CSSProperties } from "react";
import { Link } from "react-router-dom";
import Icone from "../components/Icone";
import { Carregando, Erro } from "../components/Estado";
import { api, ApiError } from "../lib/api";
import "../styles/space-travel-map.css";

type Location = {
  id?:number;
  name?:string;
  address?:Record<string,string|null|undefined>;
  latitude?:number|null;
  longitude?:number|null;
};
type Target = {
  target_key:string;
  target_type:string;
  starts_at:string;
  ends_at?:string|null;
  service_name?:string;
  title?:string;
  source?:string;
  location?:Location|null;
};
type DayContext = {
  stage:string;
  targets:Target[];
  start_location?:Location|null;
  end_location?:Location|null;
};
type RouteResult = {
  status?:string;
  provider?:string;
  routes?:Array<{ duration_text?:string; duration_minutes?:number; distance_text?:string }>;
};

function clock(value:string) {
  const date=new Date(value);
  return Number.isNaN(date.getTime())?"Horário não informado":date.toLocaleTimeString("pt-BR",{hour:"2-digit",minute:"2-digit"});
}
function address(location?:Location|null) {
  if(!location) return "";
  const order=["street","number","complement","neighborhood","district","city","state","postal_code","zip","country"];
  const parts=order.map(key=>String(location.address?.[key]||"").trim()).filter(Boolean);
  return [location.name,...parts].filter(Boolean).filter((item,index,list)=>list.indexOf(item)===index).join(", ");
}
function mapsUrl(target:Target) {
  const location=target.location;
  const destination=location?.latitude!=null&&location?.longitude!=null
    ? `${location.latitude},${location.longitude}`
    : address(location);
  return destination ? `https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(destination)}&travelmode=driving` : "";
}

export default function SpaceTravelMap() {
  const [context,setContext]=useState<DayContext|null>(null);
  const [loading,setLoading]=useState(true);
  const [error,setError]=useState("");
  const [routing,setRouting]=useState("");
  const [etas,setEtas]=useState<Record<string,string>>({});

  useEffect(()=>{
    let active=true;
    api.get<DayContext>("/agenda/mobility/day-context")
      .then(data=>{if(active)setContext({...data,targets:Array.isArray(data.targets)?data.targets:[]});})
      .catch(caught=>{if(active)setError(caught instanceof ApiError?caught.message:"Não foi possível montar seu percurso.");})
      .finally(()=>{if(active)setLoading(false);});
    return()=>{active=false;};
  },[]);

  const targets=useMemo(()=>[...(context?.targets||[])].sort((a,b)=>new Date(a.starts_at).getTime()-new Date(b.starts_at).getTime()),[context?.targets]);

  function calculate(target:Target) {
    if(!navigator.geolocation) {
      setError("Geolocalização não está disponível neste dispositivo.");
      return;
    }
    setRouting(target.target_key);
    setError("");
    navigator.geolocation.getCurrentPosition(async position=>{
      try {
        const result=await api.post<RouteResult>("/agenda/mobility/commute-target",{
          latitude:position.coords.latitude,
          longitude:position.coords.longitude,
          target_key:target.target_key,
        });
        const route=result.routes?.[0];
        const label=route?.duration_text
          ||(route?.duration_minutes!=null?`${Math.round(route.duration_minutes)} min`:result.status==="destination_without_location"?"Destino sem endereço":"Rota preparada");
        setEtas(current=>({...current,[target.target_key]:route?.distance_text?`${label} · ${route.distance_text}`:label}));
      } catch(caught) {
        setError(caught instanceof ApiError?caught.message:"Não foi possível calcular o deslocamento.");
      } finally {
        setRouting("");
      }
    },()=>{
      setRouting("");
      setError("Permita o uso pontual da localização para calcular o trajeto. Sua origem não é armazenada.");
    },{enableHighAccuracy:false,timeout:12000,maximumAge:60000});
  }

  if(loading) return <main className="space-travel"><Carregando texto="Preparando sua rota orbital…"/></main>;
  if(!context&&error) return <main className="space-travel"><Erro mensagem={error}/><Link className="botao" to="/agenda">Voltar à Agenda</Link></main>;

  return <main className="space-travel">
    <header className="space-travel__hero">
      <div><p className="eyebrow">MEU DIA ENTRE ESPAÇOS</p><h1>Mapa de deslocamento <strong>orbital</strong></h1><p>Seus compromissos presenciais de hoje em ordem cronológica. O desenho representa a jornada; o botão de navegação abre o percurso geográfico real.</p></div>
      <Link to="/agenda"><Icone nome="agenda"/> Abrir Agenda</Link>
    </header>

    {error&&<p className="space-travel__error" role="alert">{error}</p>}

    {targets.length===0?<section className="space-travel__empty">
      <span><Icone nome="rota"/></span><p className="eyebrow">ÓRBITA LIVRE</p><h2>Nenhum deslocamento presencial hoje.</h2><p>Teleconsultas continuam na Agenda. Adicione um endereço a um compromisso presencial para vê-lo neste mapa.</p><Link className="botao" to="/agenda">Organizar meu dia</Link>
    </section>:<div className="space-travel__layout">
      <section className="space-travel__map" aria-label="Percurso visual do dia">
        <div className="space-travel__stars" aria-hidden="true">{Array.from({length:32}).map((_,index)=><i key={index}/>)}</div>
        <svg viewBox="0 0 1000 430" preserveAspectRatio="none" aria-hidden="true">
          <defs><linearGradient id="space-route" x1="0" x2="1"><stop stopColor="#22d7e6"/><stop offset=".45" stopColor="#4b82ff"/><stop offset=".75" stopColor="#a363ee"/><stop offset="1" stopColor="#ef5c98"/></linearGradient><filter id="space-glow"><feGaussianBlur stdDeviation="5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
          <path className="space-travel__orbit-shadow" d="M55 315 C180 80 320 350 465 175 S730 55 945 235"/>
          <path className="space-travel__orbit" d="M55 315 C180 80 320 350 465 175 S730 55 945 235"/>
        </svg>
        <div className="space-travel__origin"><span><Icone nome="conta"/></span><small>PARTIDA</small><strong>{context?.start_location?.name||"Sua localização"}</strong></div>
        {targets.map((target,index)=>{
          const count=Math.max(targets.length-1,1);
          const left=18+(index/count)*68;
          const top=targets.length===1?43:index%3===0?25:index%3===1?58:37;
          const style={"--travel-left":`${left}%`,"--travel-top":`${top}%`} as CSSProperties;
          return <button type="button" style={style} className="space-travel__planet" key={target.target_key} onClick={()=>calculate(target)} aria-label={`Calcular rota para ${target.location?.name||target.title||"compromisso"}`}>
            <i/><span><Icone nome={target.source==="work_routine"?"gestao":target.source==="appointment"?"clinica":"agenda"}/></span><small>{clock(target.starts_at)}</small><strong>{target.location?.name||target.title||target.service_name||"Destino"}</strong>{etas[target.target_key]&&<em>{etas[target.target_key]}</em>}{routing===target.target_key&&<em>Calculando órbita…</em>}
          </button>;
        })}
        <div className="space-travel__ship" aria-hidden="true"><Icone nome="rota"/></div>
        <div className="space-travel__legend"><span><i/>Percurso cronológico</span><span><Icone nome="conta"/>Toque em um planeta para calcular o trajeto real</span></div>
      </section>

      <aside className="space-travel__manifest">
        <header><p className="eyebrow">DIÁRIO DE BORDO</p><h2>{targets.length} destino{targets.length>1?"s":""} hoje</h2></header>
        <ol>{targets.map((target,index)=>{
          const url=mapsUrl(target);
          return <li key={target.target_key}>
            <time>{clock(target.starts_at)}</time><i/><div><small>ETAPA {String(index+1).padStart(2,"0")}</small><strong>{target.service_name||target.title||"Compromisso"}</strong><span>{address(target.location)||"Local ainda não informado"}</span>{etas[target.target_key]&&<em>{etas[target.target_key]}</em>}<div><button type="button" onClick={()=>calculate(target)} disabled={routing===target.target_key}><Icone nome="rota"/> Calcular da posição atual</button>{url&&<a href={url} target="_blank" rel="noreferrer"><Icone nome="seta"/> Abrir navegação real</a>}</div></div>
          </li>;
        })}</ol>
        <footer><Icone nome="check"/><span><strong>Privacidade por desenho</strong><small>A posição atual é usada somente no cálculo solicitado e não é persistida.</small></span></footer>
      </aside>
    </div>}
  </main>;
}
