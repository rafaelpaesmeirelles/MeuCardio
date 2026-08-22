import { useEffect, useState } from "react";
import { api } from "../lib/api";

type Evento = {
  id:string; tipo:string; data:string; titulo:string; resumo:string; status:string|null;
  encounter_id?:number|null; appointment_id?:number; artifact_id?:number;
};

function quando(v:string){
  return new Intl.DateTimeFormat("pt-BR",{dateStyle:"short",timeStyle:"short"}).format(new Date(v));
}

export default function PatientProfileTimeline({patientId}:{patientId:number}){
  const [eventos,setEventos]=useState<Evento[]>([]),[erro,setErro]=useState("");
  const carregar=()=>api.get<Evento[]>(`/pacientes/${patientId}/linha-do-tempo?limite=50`).then(setEventos).catch(e=>setErro(e.message));

  useEffect(()=>{
    carregar();
    const focus=()=>carregar();
    window.addEventListener("focus",focus);
    return()=>window.removeEventListener("focus",focus);
  },[patientId]); // eslint-disable-line react-hooks/exhaustive-deps

  return <section className="pep-card pep-history">
    <div className="pep-title"><div><p className="eyebrow">História longitudinal</p><h2>Linha do tempo</h2></div><button onClick={carregar}>Atualizar</button></div>
    {erro&&<p className="pep-error">{erro}</p>}
    {!eventos.length&&!erro&&<p className="pep-muted">Ainda não há eventos clínicos vinculados.</p>}
    {eventos.map(e=><article key={e.id}>
      <div><strong>{e.titulo}</strong><time>{quando(e.data)}</time></div>
      <p>{e.resumo||"—"}</p>
      <small>{[e.tipo,e.status].filter(Boolean).join(" · ")}</small>
    </article>)}
  </section>;
}
