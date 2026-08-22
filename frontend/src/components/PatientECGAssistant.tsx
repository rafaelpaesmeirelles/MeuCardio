import { useEffect, useState } from "react";
import { api } from "../lib/api";

type Payload={
  quality:"adequada"|"limitada"|"inadequada";summary:string;rhythm:string|null;
  heart_rate_bpm:number|null;intervals:{pr_ms:number|null;qrs_ms:number|null;qtc_ms:number|null};
  axis:string|null;conduction:string|null;st_t:string|null;other_findings:string[];
  red_flags:string[];limitations:string[];urgent_review_recommended:boolean;disclaimer:string;
};
type Suggestion={id:number;status:"generated"|"accepted"|"rejected";payload:Payload;provider:string;model:string;created_at:string;reviewed_at:string|null;review_note:string|null;accepted_result_id:number|null};
type ECG={id:number;performed_at:string;original_name:string;media_type:string;size_bytes:number;source_encounter_id:number|null;created_at:string;suggestions:Suggestion[]};

const localDateTime=(value:string|number=Date.now())=>{const d=new Date(value);return new Date(d.getTime()-d.getTimezoneOffset()*60000).toISOString().slice(0,16);};
const when=(value:string)=>new Date(value).toLocaleString("pt-BR");
const measurements=(p:Payload)=>[
  p.heart_rate_bpm!==null?`FC ${p.heart_rate_bpm} bpm`:null,
  p.intervals.pr_ms!==null?`PR ${p.intervals.pr_ms} ms`:null,
  p.intervals.qrs_ms!==null?`QRS ${p.intervals.qrs_ms} ms`:null,
  p.intervals.qtc_ms!==null?`QTc ${p.intervals.qtc_ms} ms`:null,
].filter(Boolean).join(" · ");

export default function PatientECGAssistant({patientId,currentEncounterId,onChanged}:{patientId:number;currentEncounterId:number|null;onChanged?:()=>void}){
  const base=`/pacientes/${patientId}/ecgs`;
  const [items,setItems]=useState<ECG[]>([]),[file,setFile]=useState<File|null>(null),[performedAt,setPerformedAt]=useState(localDateTime());
  const [drafts,setDrafts]=useState<Record<number,string>>({}),[notes,setNotes]=useState<Record<number,string>>({});
  const [busy,setBusy]=useState(""),[error,setError]=useState("");
  const load=()=>api.get<ECG[]>(base).then(rows=>{setItems(rows);setDrafts(old=>{const next={...old};for(const ecg of rows)for(const s of ecg.suggestions)if(s.status==="generated"&&next[s.id]===undefined)next[s.id]=s.payload.summary;return next;});}).catch(e=>setError(e.message));
  useEffect(()=>{setItems([]);setFile(null);setPerformedAt(localDateTime());setDrafts({});setNotes({});setBusy("");setError("");load();},[patientId]); // eslint-disable-line react-hooks/exhaustive-deps

  async function upload(){
    if(!file||!performedAt)return;setBusy("upload");setError("");
    try{await api.upload<ECG>(base,"arquivo",file,{performed_at:new Date(performedAt).toISOString(),...(currentEncounterId?{source_encounter_id:String(currentEncounterId)}:{})});setFile(null);setPerformedAt(localDateTime());await load();onChanged?.();}
    catch(e){setError(e instanceof Error?e.message:"Falha ao anexar ECG.");}finally{setBusy("");}
  }
  async function analyze(ecg:ECG){
    if(!window.confirm("O arquivo do ECG será enviado ao provedor de IA configurado para gerar uma sugestão não validada. Deseja continuar?"))return;
    setBusy(`ai-${ecg.id}`);setError("");
    try{await api.post(`${base}/${ecg.id}/sugestoes`,{confirm_external_processing:true});await load();onChanged?.();}
    catch(e){setError(e instanceof Error?e.message:"Falha ao gerar sugestão.");}finally{setBusy("");}
  }
  async function open(ecg:ECG){
    try{const blob=await api.blob(`${base}/${ecg.id}/arquivo`);const url=URL.createObjectURL(blob);window.open(url,"_blank","noopener,noreferrer");window.setTimeout(()=>URL.revokeObjectURL(url),60000);}
    catch(e){setError(e instanceof Error?e.message:"Falha ao abrir ECG.");}
  }
  async function review(ecg:ECG,s:Suggestion,decision:"accept"|"reject"){
    const final=drafts[s.id]?.trim()||"";if(decision==="accept"&&!final)return;
    setBusy(`review-${s.id}`);setError("");
    try{await api.post(`${base}/${ecg.id}/sugestoes/${s.id}/revisao`,{decision,final_interpretation:decision==="accept"?final:null,review_note:notes[s.id]?.trim()||null});await load();onChanged?.();}
    catch(e){setError(e instanceof Error?e.message:"Falha ao revisar sugestão.");}finally{setBusy("");}
  }

  return <section className="pep-card pep-history">
    <div className="pep-title"><div><p className="eyebrow">Assistência multimodal</p><h2>ECG com apoio de IA</h2></div><small>Sugestão → revisão médica → aceitação explícita</small></div>
    <p className="pep-muted">A IA não lauda nem grava diagnóstico automaticamente. O arquivo original permanece protegido no prontuário e somente a interpretação confirmada pelo médico vira resultado clínico.</p>
    {error&&<p className="pep-error" role="alert">{error}</p>}
    <div className="grade grade--3">
      <label>Arquivo do ECG<input type="file" accept="image/jpeg,image/png,image/webp,application/pdf" onChange={e=>setFile(e.target.files?.[0]||null)}/></label>
      <label>Data clínica<input type="datetime-local" value={performedAt} onChange={e=>setPerformedAt(e.target.value)}/></label>
      <div><small>{currentEncounterId?`Vinculado ao atendimento #${currentEncounterId}`:"Sem atendimento vinculado"}</small><br/><button className="botao" disabled={!file||!performedAt||!!busy} onClick={upload}>{busy==="upload"?"Protegendo e enviando…":"Anexar ECG"}</button></div>
    </div>
    {!items.length&&<p className="pep-muted">Nenhum ECG anexado para este paciente.</p>}
    {items.map(ecg=><article key={ecg.id}>
      <div><strong>ECG · {ecg.original_name}</strong><time>{when(ecg.performed_at)}</time></div>
      <small>{ecg.media_type} · {(ecg.size_bytes/1024/1024).toFixed(2)} MB · arquivo cifrado</small>
      <div className="pep-actions"><button onClick={()=>open(ecg)}>Abrir original</button><button className="botao botao--secundario" disabled={!!busy} onClick={()=>analyze(ecg)}>{busy===`ai-${ecg.id}`?"Analisando…":"Gerar nova sugestão"}</button></div>
      {ecg.suggestions.map(s=><details key={s.id} open={s.status==="generated"}>
        <summary>Sugestão IA #{s.id} · {s.status==="generated"?"aguardando revisão":s.status==="accepted"?"aceita pelo médico":"rejeitada"}</summary>
        <p><strong>Qualidade:</strong> {s.payload.quality}{s.payload.urgent_review_recommended?" · revisão prioritária sugerida":""}</p>
        {measurements(s.payload)&&<p>{measurements(s.payload)}</p>}
        {s.payload.rhythm&&<p><strong>Ritmo:</strong> {s.payload.rhythm}</p>}
        {s.payload.axis&&<p><strong>Eixo:</strong> {s.payload.axis}</p>}
        {s.payload.conduction&&<p><strong>Condução:</strong> {s.payload.conduction}</p>}
        {s.payload.st_t&&<p><strong>ST-T:</strong> {s.payload.st_t}</p>}
        {!!s.payload.other_findings.length&&<p><strong>Outros achados:</strong> {s.payload.other_findings.join(" · ")}</p>}
        {!!s.payload.red_flags.length&&<p role="alert"><strong>Sinais para revisão prioritária:</strong> {s.payload.red_flags.join(" · ")}</p>}
        {!!s.payload.limitations.length&&<p><strong>Limitações:</strong> {s.payload.limitations.join(" · ")}</p>}
        <small>{s.payload.disclaimer} · {s.provider}/{s.model}</small>
        {s.status==="generated"?<div>
          <label>Interpretação médica final<textarea rows={5} value={drafts[s.id]||""} onChange={e=>setDrafts(x=>({...x,[s.id]:e.target.value}))}/></label>
          <label>Nota de revisão (opcional)<textarea rows={2} value={notes[s.id]||""} onChange={e=>setNotes(x=>({...x,[s.id]:e.target.value}))}/></label>
          <div className="pep-actions"><button className="botao" disabled={!!busy||!(drafts[s.id]||"").trim()} onClick={()=>review(ecg,s,"accept")}>Aceitar interpretação revisada</button><button disabled={!!busy} onClick={()=>review(ecg,s,"reject")}>Rejeitar sugestão</button></div>
        </div>:<p><small>{s.status==="accepted"?`Resultado clínico #${s.accepted_result_id} criado após revisão médica.`:"Sugestão preservada no histórico, sem virar fato clínico."}{s.review_note?` · ${s.review_note}`:""}</small></p>}
      </details>)}
    </article>)}
  </section>;
}
