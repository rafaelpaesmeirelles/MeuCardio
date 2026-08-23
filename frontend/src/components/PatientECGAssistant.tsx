import { useEffect, useRef, useState } from "react";
import { api } from "../lib/api";

type Payload={
  quality:"adequada"|"limitada"|"inadequada";summary:string;rhythm:string|null;
  heart_rate_bpm:number|null;intervals:{pr_ms:number|null;qrs_ms:number|null;qtc_ms:number|null};
  axis:string|null;conduction:string|null;st_t:string|null;other_findings:string[];
  red_flags:string[];limitations:string[];urgent_review_recommended:boolean;disclaimer:string;
};
type Suggestion={id:number;status:"generated"|"accepted"|"rejected";payload:Payload;provider:string;model:string;created_at:string;reviewed_at:string|null;review_note:string|null;accepted_result_id:number|null};
type ECG={id:number;performed_at:string;original_name:string;media_type:string;size_bytes:number;source_encounter_id:number|null;created_at:string;suggestions:Suggestion[]};
type AIStatus={enabled:boolean};

const PAGE_SIZE=30;

const localDateTime=(value:string|number=Date.now())=>{const d=new Date(value);return new Date(d.getTime()-d.getTimezoneOffset()*60000).toISOString().slice(0,16);};
const when=(value:string)=>new Date(value).toLocaleString("pt-BR");
const measurements=(p:Payload)=>[
  p.heart_rate_bpm!==null?`FC ${p.heart_rate_bpm} bpm`:null,
  p.intervals.pr_ms!==null?`PR ${p.intervals.pr_ms} ms`:null,
  p.intervals.qrs_ms!==null?`QRS ${p.intervals.qrs_ms} ms`:null,
  p.intervals.qtc_ms!==null?`QTc ${p.intervals.qtc_ms} ms`:null,
].filter(Boolean).join(" · ");

export default function PatientECGAssistant({patientId,currentEncounterId,focusOnMount=false,onChanged}:{patientId:number;currentEncounterId:number|null;focusOnMount?:boolean;onChanged?:()=>void}){
  const base=`/pacientes/${patientId}/ecgs`;
  const sectionRef=useRef<HTMLElement>(null),fileRef=useRef<HTMLInputElement>(null);
  const [items,setItems]=useState<ECG[]>([]),[file,setFile]=useState<File|null>(null),[performedAt,setPerformedAt]=useState(localDateTime());
  const [drafts,setDrafts]=useState<Record<number,string>>({}),[notes,setNotes]=useState<Record<number,string>>({});
  const [aiEnabled,setAIEnabled]=useState<boolean|null>(null),[hasMore,setHasMore]=useState(false);
  const [busy,setBusy]=useState(""),[error,setError]=useState("");
  const seedDrafts=(rows:ECG[])=>setDrafts(old=>{const next={...old};for(const ecg of rows)for(const s of ecg.suggestions)if(s.status==="generated"&&next[s.id]===undefined)next[s.id]=s.payload.summary;return next;});
  const load=()=>Promise.all([
    api.get<ECG[]>(`${base}?limite=${PAGE_SIZE}&offset=0`),
    api.get<AIStatus>(`${base}/ia-status`),
  ]).then(([rows,status])=>{setItems(rows);seedDrafts(rows);setHasMore(rows.length===PAGE_SIZE);setAIEnabled(status.enabled);}).catch(e=>setError(e.message));
  useEffect(()=>{setItems([]);setFile(null);setPerformedAt(localDateTime());setDrafts({});setNotes({});setAIEnabled(null);setHasMore(false);setBusy("");setError("");load();},[patientId]); // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(()=>{if(!focusOnMount)return;const frame=requestAnimationFrame(()=>{const reducedMotion=window.matchMedia("(prefers-reduced-motion: reduce)").matches;sectionRef.current?.scrollIntoView({behavior:reducedMotion?"auto":"smooth",block:"start"});fileRef.current?.focus({preventScroll:true});});return()=>cancelAnimationFrame(frame);},[focusOnMount,patientId]);

  async function upload(){
    if(!file||!performedAt)return;setBusy("upload");setError("");
    try{await api.upload<ECG>(base,"arquivo",file,{performed_at:new Date(performedAt).toISOString(),...(currentEncounterId?{source_encounter_id:String(currentEncounterId)}:{})});setFile(null);setPerformedAt(localDateTime());await load();onChanged?.();}
    catch(e){setError(e instanceof Error?e.message:"Falha ao anexar.");}finally{setBusy("");}
  }
  async function analyze(ecg:ECG){
    if(!aiEnabled)return;
    if(!window.confirm("O ECG será enviado ao provedor de IA para gerar sugestão não validada. Continuar?"))return;
    setBusy(`ai-${ecg.id}`);setError("");
    try{await api.post(`${base}/${ecg.id}/sugestoes`,{confirm_external_processing:true});await load();onChanged?.();}
    catch(e){setError(e instanceof Error?e.message:"Falha ao gerar sugestão.");}finally{setBusy("");}
  }
  async function loadMore(){
    setBusy("more");setError("");
    try{const rows=await api.get<ECG[]>(`${base}?limite=${PAGE_SIZE}&offset=${items.length}`);setItems(old=>[...old,...rows]);seedDrafts(rows);setHasMore(rows.length===PAGE_SIZE);}
    catch(e){setError(e instanceof Error?e.message:"Falha ao carregar.");}finally{setBusy("");}
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

  return <section ref={sectionRef} id="assistente-ecg" className="pep-card pep-history pep-ecg-featured" aria-labelledby="assistente-ecg-title">
    <div className="pep-title"><div><p className="eyebrow">Recurso destaque · assistência multimodal</p><h2 id="assistente-ecg-title">IA para ECG</h2></div><span className="pep-featured-badge">Destaque</span></div>
    <p className="pep-ecg-flow">Envie o ECG protegido e revise os achados sugeridos.</p>
    <small className="pep-ecg-review-flow">Sugestão → revisão médica → aceitação explícita</small>
    <p className="pep-muted">A IA não lauda nem registra diagnóstico. Só a interpretação confirmada pelo médico vira fato clínico.</p>
    {error&&<p className="pep-error" role="alert">{error}</p>}
    <div className="grade grade--3">
      <label>Arquivo do ECG<input ref={fileRef} type="file" accept="image/jpeg,image/png,image/webp,application/pdf" onChange={e=>setFile(e.target.files?.[0]||null)}/></label>
      <label>Data clínica<input type="datetime-local" value={performedAt} onChange={e=>setPerformedAt(e.target.value)}/></label>
      <div><small>{currentEncounterId?`Atendimento #${currentEncounterId}`:"Sem atendimento"}</small><br/><button className="botao" disabled={!file||!performedAt||!!busy} onClick={upload}>{busy==="upload"?"Anexando…":"Anexar ECG"}</button></div>
    </div>
    {!items.length&&<p className="pep-muted">Nenhum ECG anexado.</p>}
    {items.map(ecg=><article key={ecg.id}>
      <div><strong>ECG · {ecg.original_name}</strong><time>{when(ecg.performed_at)}</time></div>
      <small>{ecg.media_type} · {(ecg.size_bytes/1024/1024).toFixed(2)} MB · cifrado</small>
      <div className="pep-actions"><button onClick={()=>open(ecg)}>Abrir original</button>{aiEnabled?<button className="botao botao--secundario" disabled={!!busy} onClick={()=>analyze(ecg)}>{busy===`ai-${ecg.id}`?"Analisando…":"Gerar sugestão"}</button>:aiEnabled===false?<small>IA indisponível; ECG preservado.</small>:null}</div>
      {ecg.suggestions.map(s=><details key={s.id} open={s.status==="generated"}>
        <summary>Sugestão IA #{s.id} · {s.status==="generated"?"revisar":s.status==="accepted"?"aceita":"rejeitada"}</summary>
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
          <label>Revisão médica final<textarea rows={5} value={drafts[s.id]||""} onChange={e=>setDrafts(x=>({...x,[s.id]:e.target.value}))}/></label>
          <label>Nota de revisão (opcional)<textarea rows={2} value={notes[s.id]||""} onChange={e=>setNotes(x=>({...x,[s.id]:e.target.value}))}/></label>
          <div className="pep-actions"><button className="botao" disabled={!!busy||!(drafts[s.id]||"").trim()} onClick={()=>review(ecg,s,"accept")}>Aceitar revisão</button><button disabled={!!busy} onClick={()=>review(ecg,s,"reject")}>Rejeitar</button></div>
        </div>:<p><small>{s.status==="accepted"?`Resultado #${s.accepted_result_id} criado após revisão.`:"Rejeitada e preservada no histórico."}{s.review_note?` · ${s.review_note}`:""}</small></p>}
      </details>)}
    </article>)}
    {hasMore&&<div className="pep-actions"><button disabled={!!busy} onClick={loadMore}>{busy==="more"?"Carregando…":"Carregar anteriores"}</button></div>}
  </section>;
}
