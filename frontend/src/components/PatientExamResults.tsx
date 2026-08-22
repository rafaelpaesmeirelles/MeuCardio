import { useEffect, useState } from "react";
import { api } from "../lib/api";

type Kind = "laboratorial" | "metodo_grafico" | "imagem" | "outro";
type ExamResult = {
  id:number; exam_kind:Kind; exam_name:string; performed_at:string; result:string;
  unit:string|null; reference_range:string|null; notes:string|null;
  lab_test_slug:string|null; source_encounter_id:number|null; correction_of_id:number|null;
};

function agoraLocal(){const d=new Date(Date.now()-new Date().getTimezoneOffset()*60000);return d.toISOString().slice(0,16);}
function quando(v:string){return new Intl.DateTimeFormat("pt-BR",{dateStyle:"short",timeStyle:"short"}).format(new Date(v));}

export default function PatientExamResults({patientId,currentEncounterId,onChanged}:{patientId:number;currentEncounterId:number|null;onChanged?:()=>void}){
  const [itens,setItens]=useState<ExamResult[]>([]),[kind,setKind]=useState<Kind>("laboratorial"),[name,setName]=useState("");
  const [result,setResult]=useState(""),[unit,setUnit]=useState(""),[referenceRange,setReferenceRange]=useState(""),[notes,setNotes]=useState("");
  const [performedAt,setPerformedAt]=useState(agoraLocal()),[erro,setErro]=useState(""),[salvando,setSalvando]=useState(false);

  const carregar=()=>api.get<ExamResult[]>(`/pacientes/${patientId}/resultados`).then(setItens).catch(e=>setErro(e.message));
  useEffect(()=>{
    setItens([]);setKind("laboratorial");setName("");setResult("");setUnit("");setReferenceRange("");setNotes("");
    setPerformedAt(agoraLocal());setErro("");setSalvando(false);carregar();
  },[patientId]); // eslint-disable-line react-hooks/exhaustive-deps

  async function adicionar(){
    if(!name.trim()||!result.trim())return;setSalvando(true);setErro("");
    try{
      await api.post(`/pacientes/${patientId}/resultados`,{
        exam_kind:kind,exam_name:name.trim(),performed_at:performedAt?new Date(performedAt).toISOString():null,
        result:result.trim(),unit:unit.trim()||null,reference_range:referenceRange.trim()||null,
        notes:notes.trim()||null,source_encounter_id:currentEncounterId||null,
      });
      setName("");setResult("");setUnit("");setReferenceRange("");setNotes("");setPerformedAt(agoraLocal());
      await carregar();onChanged?.();
    }catch(e){setErro(e instanceof Error?e.message:"Falha ao registrar resultado.");}
    finally{setSalvando(false);}
  }

  return <section className="pep-card pep-history" style={{marginTop:"0.8rem"}}>
    <div className="pep-title"><div><p className="eyebrow">Exames e resultados</p><h2>Histórico de resultados</h2></div><a href="/exames">Catálogo CorVIA</a></div>
    {erro&&<p role="alert" className="pep-error">{erro}</p>}
    {!itens.length&&<p className="pep-muted">Ainda não há resultados registrados.</p>}
    {itens.slice(0,12).map(item=><article key={item.id}>
      <div><strong>{item.correction_of_id?"Correção · ":""}{item.exam_name}</strong><time>{quando(item.performed_at)}</time></div>
      <p>{item.result}{item.unit?` ${item.unit}`:""}</p>
      <small>{[item.exam_kind,item.reference_range?`Referência: ${item.reference_range}`:null,item.source_encounter_id?`Atendimento #${item.source_encounter_id}`:null].filter(Boolean).join(" · ")}</small>
      {item.notes&&<p className="pep-muted">{item.notes}</p>}
      {item.lab_test_slug&&<a href={`/exames/${item.lab_test_slug}`}>Conteúdo científico</a>}
    </article>)}
    <div className="grade grade--3" style={{marginTop:"0.8rem"}}>
      <label>Tipo<select value={kind} onChange={e=>setKind(e.target.value as Kind)}><option value="laboratorial">Laboratorial</option><option value="metodo_grafico">Método gráfico</option><option value="imagem">Imagem</option><option value="outro">Outro</option></select></label>
      <label>Exame<input value={name} onChange={e=>setName(e.target.value)} placeholder="Troponina, ECG, eco…"/></label>
      <label>Data<input type="datetime-local" value={performedAt} onChange={e=>setPerformedAt(e.target.value)}/></label>
    </div>
    <div className="grade grade--3" style={{marginTop:"0.5rem"}}>
      <label>Resultado / achado<input value={result} onChange={e=>setResult(e.target.value)} placeholder="Valor ou achado"/></label>
      <label>Unidade<input value={unit} onChange={e=>setUnit(e.target.value)} placeholder="Opcional"/></label>
      <label>Referência<input value={referenceRange} onChange={e=>setReferenceRange(e.target.value)} placeholder="Opcional"/></label>
    </div>
    <label style={{display:"block",marginTop:"0.5rem"}}>Observações<textarea rows={2} value={notes} onChange={e=>setNotes(e.target.value)} placeholder="Opcional"/></label>
    <button className="botao" style={{marginTop:"0.5rem"}} onClick={adicionar} disabled={salvando||!name.trim()||!result.trim()}>{salvando?"Registrando…":"+ Registrar resultado"}</button>
  </section>;
}
