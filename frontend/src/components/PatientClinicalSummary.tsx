import { useEffect, useState } from "react";
import { api } from "../lib/api";
import PatientECGAssistant from "./PatientECGAssistant";
import PatientExamResults from "./PatientExamResults";
import PatientProfileTimeline from "./PatientProfileTimeline";

type Kind = "problema" | "alergia" | "medicacao";
type Item = {
  id:number; kind:Kind; is_active:boolean; name:string; details:string|null;
  source_encounter_id:number|null; created_at:string; ended_at:string|null;
};

const LABEL:Record<Kind,string>={problema:"Problemas ativos",alergia:"Alergias",medicacao:"Medicações em uso"};
const VAZIO:Record<Kind,string>={problema:"Nenhum problema ativo registrado.",alergia:"Nenhuma alergia registrada.",medicacao:"Nenhuma medicação em uso registrada."};

export default function PatientClinicalSummary({patientId,currentEncounterId,focusECG=false}:{patientId:number;currentEncounterId:number|null;focusECG?:boolean}){
  const [itens,setItens]=useState<Item[]>([]),[kind,setKind]=useState<Kind>("problema"),[name,setName]=useState(""),[details,setDetails]=useState(""),[erro,setErro]=useState("");
  const [timelineRevision,setTimelineRevision]=useState(0);
  const carregar=()=>api.get<Item[]>(`/pacientes/${patientId}/resumo-clinico`).then(setItens).catch(e=>setErro(e.message));
  useEffect(()=>{
    setItens([]);setKind("problema");setName("");setDetails("");setErro("");setTimelineRevision(0);carregar();
  },[patientId]); // eslint-disable-line react-hooks/exhaustive-deps

  async function adicionar(){
    const n=name.trim();if(!n)return;setErro("");
    try{
      await api.post(`/pacientes/${patientId}/resumo-clinico`,{kind,name:n,details:details.trim()||null,source_encounter_id:currentEncounterId||null});
      setName("");setDetails("");await carregar();setTimelineRevision(x=>x+1);
    }catch(e){setErro(e instanceof Error?e.message:"Falha ao registrar item clínico.");}
  }
  async function inativar(id:number){
    try{await api.post(`/pacientes/${patientId}/resumo-clinico/${id}/inativar`);await carregar();setTimelineRevision(x=>x+1);}
    catch(e){setErro(e instanceof Error?e.message:"Falha ao inativar item clínico.");}
  }

  return <>
    <PatientECGAssistant patientId={patientId} currentEncounterId={currentEncounterId} focusOnMount={focusECG} onChanged={()=>setTimelineRevision(x=>x+1)}/>
    <section className="pep-card" style={{marginTop:"0.8rem"}}>
      <div className="pep-title"><div><p className="eyebrow">Resumo clínico</p><h2>Problemas, alergias e medicações</h2></div><small>{itens.length} ativo(s)</small></div>
      {erro&&<p role="alert" className="pep-error">{erro}</p>}
      <div className="grade grade--3">
        {(["problema","alergia","medicacao"] as Kind[]).map(k=><div key={k} className="cartao">
          <strong>{LABEL[k]}</strong>
          {!itens.some(i=>i.kind===k)&&<p className="pep-muted">{VAZIO[k]}</p>}
          {itens.filter(i=>i.kind===k).map(i=><div key={i.id} style={{marginTop:"0.5rem"}}>
            <div style={{display:"flex",justifyContent:"space-between",gap:8,alignItems:"start"}}><span><strong>{i.name}</strong>{i.details&&<small style={{display:"block"}}>{i.details}</small>}</span><button className="botao botao--secundario" style={{padding:"0.2rem 0.45rem"}} onClick={()=>inativar(i.id)}>Inativar</button></div>
          </div>)}
        </div>)}
      </div>
      <div className="grade grade--3" style={{marginTop:"0.7rem"}}>
        <label>Adicionar<select value={kind} onChange={e=>setKind(e.target.value as Kind)}><option value="problema">Problema</option><option value="alergia">Alergia</option><option value="medicacao">Medicação</option></select></label>
        <label>Nome<input value={name} onChange={e=>setName(e.target.value)} placeholder={kind==="problema"?"Ex.: Hipertensão arterial":kind==="alergia"?"Ex.: Penicilina":"Ex.: Losartana"}/></label>
        <label>Detalhes<input value={details} onChange={e=>setDetails(e.target.value)} placeholder="Opcional" onKeyDown={e=>{if(e.key==="Enter")adicionar();}}/></label>
      </div>
      <button className="botao" style={{marginTop:"0.5rem"}} onClick={adicionar} disabled={!name.trim()}>+ Registrar</button>
    </section>
    <PatientExamResults key={`results-${patientId}-${timelineRevision}`} patientId={patientId} currentEncounterId={currentEncounterId} onChanged={()=>setTimelineRevision(x=>x+1)}/>
    <PatientProfileTimeline key={`${patientId}-${currentEncounterId||0}-${itens.map(i=>i.id).join("-")}-${timelineRevision}`} patientId={patientId}/>
  </>;
}
