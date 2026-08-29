import { useEffect, useMemo, useState } from "react";
import { api, ApiError } from "../lib/api";

type Suggestion = {
  id:number; exam_record_id:number; status:"generated"|"accepted"|"rejected";
  payload:Record<string,any>; web_sources:Array<{url:string;title?:string}>;
  model:string; prompt_version:string; created_at:string; review_note?:string|null; accepted_result_id?:number|null;
};
type Exam = {
  id:number; performed_at:string; exam_type:string; exam_type_label:string; original_name:string;
  media_type:string; size_bytes:number; notes:string|null; latest_suggestion:Suggestion|null;
};
type Status = { enabled:boolean; exam_types:Record<string,string>; supported_media_types:string[] };

function messageOf(error:unknown){return error instanceof ApiError?error.message:error instanceof Error?error.message:"Não foi possível concluir a operação.";}
function when(value:string){return new Intl.DateTimeFormat("pt-BR",{dateStyle:"short",timeStyle:"short"}).format(new Date(value));}

export default function PatientMultimodalAssistant({patientId,currentEncounterId,onChanged}:{patientId:number;currentEncounterId:number|null;onChanged?:()=>void}){
  const [status,setStatus]=useState<Status|null>(null),[exams,setExams]=useState<Exam[]>([]),[selected,setSelected]=useState<Exam|null>(null);
  const [file,setFile]=useState<File|null>(null),[examType,setExamType]=useState("echocardiogram"),[performedAt,setPerformedAt]=useState(()=>new Date().toISOString().slice(0,16));
  const [notes,setNotes]=useState(""),[question,setQuestion]=useState(""),[finalInterpretation,setFinalInterpretation]=useState(""),[reviewNote,setReviewNote]=useState("");
  const [busy,setBusy]=useState(false),[error,setError]=useState(""),[info,setInfo]=useState("");
  const suggestion=selected?.latest_suggestion??null;

  async function load(){
    const [s,rows]=await Promise.all([
      api.get<Status>(`/pacientes/${patientId}/exames-multimodais/status`),
      api.get<Exam[]>(`/pacientes/${patientId}/exames-multimodais`),
    ]);
    setStatus(s);setExams(rows);
    setSelected(current=>current?rows.find(row=>row.id===current.id)??rows[0]??null:rows[0]??null);
  }
  useEffect(()=>{setSelected(null);setError("");setInfo("");void load().catch(e=>setError(messageOf(e)));},[patientId]); // eslint-disable-line react-hooks/exhaustive-deps
  const accept=useMemo(()=>status?.supported_media_types.includes(file?.type||"")??true,[status,file]);

  async function upload(){
    if(!file)return;setBusy(true);setError("");setInfo("");
    try{
      const at=new Date(performedAt);if(Number.isNaN(at.getTime()))throw new Error("Informe data e hora válidas.");
      const row=await api.uploadFormulario<Exam>(`/pacientes/${patientId}/exames-multimodais`,[{campo:"arquivo",arquivo:file}],{
        exam_type:examType,performed_at:at.toISOString(),notes:notes.trim(),source_encounter_id:currentEncounterId?String(currentEncounterId):"",
      });
      setFile(null);setNotes("");await load();setSelected(row);setInfo("Exame armazenado de forma cifrada no prontuário.");onChanged?.();
    }catch(e){setError(messageOf(e));}finally{setBusy(false);}
  }
  async function analyze(){
    if(!selected)return;setBusy(true);setError("");setInfo("Analisando o exame junto ao contexto longitudinal do prontuário e pesquisando evidências atuais…");
    try{
      await api.post(`/pacientes/${patientId}/exames-multimodais/${selected.id}/sugestoes`,{confirm_external_processing:true,clinical_question:question.trim()});
      await load();setInfo("Sugestão disponível para revisão médica. Nada foi incorporado como fato clínico automaticamente.");onChanged?.();
    }catch(e){setError(messageOf(e));setInfo("");}finally{setBusy(false);}
  }
  async function review(decision:"accept"|"reject"){
    if(!selected||!suggestion)return;
    if(decision==="accept"&&!finalInterpretation.trim()){setError("Registre sua interpretação médica final antes de aceitar a sugestão.");return;}
    setBusy(true);setError("");setInfo("");
    try{
      await api.post(`/pacientes/${patientId}/exames-multimodais/${selected.id}/sugestoes/${suggestion.id}/revisao`,{
        decision,final_interpretation:decision==="accept"?finalInterpretation.trim():null,review_note:reviewNote.trim()||null,
      });
      setFinalInterpretation("");setReviewNote("");await load();setInfo(decision==="accept"?"Interpretação médica registrada no prontuário.":"Sugestão rejeitada; o exame original permanece preservado.");onChanged?.();
    }catch(e){setError(messageOf(e));}finally{setBusy(false);}
  }
  async function openOriginal(){if(!selected)return;try{const blob=await api.blob(`/pacientes/${patientId}/exames-multimodais/${selected.id}/arquivo`);const url=URL.createObjectURL(blob);window.open(url,"_blank","noopener,noreferrer");window.setTimeout(()=>URL.revokeObjectURL(url),60000);}catch(e){setError(messageOf(e));}}

  return <section className="pep-card" style={{marginTop:"0.8rem"}}>
    <div className="pep-title"><div><p className="eyebrow">Assistência multimodal</p><h2>IA para exames no prontuário</h2></div><small>{exams.length} exame(s) armazenado(s)</small></div>
    <p className="pep-muted">Envie exames gráficos, imagem, PDF ou resultados estruturados. O CorVIA pode correlacionar o exame com o contexto longitudinal e sugerir hipóteses, exames adicionais e possibilidades de condução fundamentadas em fontes atuais.</p>
    <p className="pep-muted"><strong>Apoio à decisão:</strong> a IA não emite laudo autônomo, não prescreve e não substitui julgamento, conduta ou decisão médica. Uma sugestão só vira registro clínico após sua revisão explícita.</p>
    {error&&<p className="pep-error" role="alert">{error}</p>}{info&&<p className="pep-muted" role="status">{info}</p>}

    <div className="grade grade--3">
      <label>Tipo de exame<select value={examType} onChange={e=>setExamType(e.target.value)}>{Object.entries(status?.exam_types??{}).map(([value,label])=><option key={value} value={value}>{label}</option>)}</select></label>
      <label>Data/hora<input type="datetime-local" value={performedAt} onChange={e=>setPerformedAt(e.target.value)}/></label>
      <label>Arquivo<input type="file" accept=".pdf,.jpg,.jpeg,.png,.webp,.txt,.csv" onChange={e=>setFile(e.target.files?.[0]??null)}/></label>
    </div>
    <label style={{display:"block",marginTop:"0.5rem"}}>Observação sobre o exame<input value={notes} onChange={e=>setNotes(e.target.value)} placeholder="Opcional; não use identificadores desnecessários"/></label>
    {file&&!accept&&<p className="pep-error">O formato selecionado não é aceito pelo provedor atual.</p>}
    <button className="botao" style={{marginTop:"0.5rem"}} disabled={!file||busy||!accept} onClick={()=>void upload()}>{busy?"Processando…":"Armazenar exame no prontuário"}</button>

    {!!exams.length&&<div className="grade grade--3" style={{marginTop:"0.8rem"}}>
      <div className="cartao"><strong>Exames armazenados</strong>{exams.map(row=><button key={row.id} type="button" className="botao botao--secundario" style={{display:"block",width:"100%",marginTop:"0.4rem",textAlign:"left"}} onClick={()=>{setSelected(row);setFinalInterpretation("");setReviewNote("");}}>{row.exam_type_label}<small style={{display:"block"}}>{when(row.performed_at)} · {row.latest_suggestion?.status??"sem análise"}</small></button>)}</div>
      <div className="cartao" style={{gridColumn:"span 2"}}>{!selected?<p className="pep-muted">Selecione um exame.</p>:<>
        <div className="pep-title"><div><strong>{selected.exam_type_label}</strong><small style={{display:"block"}}>{selected.original_name} · {when(selected.performed_at)}</small></div><button className="botao botao--secundario" onClick={()=>void openOriginal()}>Abrir original</button></div>
        <label>Pergunta clínica opcional<textarea rows={2} value={question} onChange={e=>setQuestion(e.target.value)} placeholder="Ex.: há achados que mudam a investigação ou a condução?"/></label>
        <button className="botao" disabled={busy||!status?.enabled} onClick={()=>void analyze()}>{suggestion?"Nova análise com IA":"Analisar com IA + prontuário"}</button>
        {!status?.enabled&&<p className="pep-muted">Assistência multimodal indisponível nesta instalação.</p>}
        {suggestion&&<div style={{marginTop:"0.7rem"}}>
          <h3>Sugestão da IA · {suggestion.status}</h3>
          <p>{String(suggestion.payload?.executive_summary??"")}</p>
          {!!suggestion.payload?.integrated_impression?.length&&<><strong>Impressão integrada</strong><ul>{suggestion.payload.integrated_impression.map((x:string)=><li key={x}>{x}</li>)}</ul></>}
          {!!suggestion.payload?.differential_diagnoses?.length&&<><strong>Diagnósticos diferenciais</strong><ul>{suggestion.payload.differential_diagnoses.map((x:any)=><li key={`${x.diagnosis}-${x.likelihood}`}><b>{x.diagnosis}</b> — {x.rationale}</li>)}</ul></>}
          {!!suggestion.payload?.suggested_additional_tests?.length&&<><strong>Exames adicionais sugeridos</strong><ul>{suggestion.payload.suggested_additional_tests.map((x:any)=><li key={`${x.exam}-${x.priority}`}><b>{x.exam}</b> — {x.rationale} ({x.priority})</li>)}</ul></>}
          {!!suggestion.payload?.possible_management?.length&&<><strong>Possibilidades de condução</strong><ul>{suggestion.payload.possible_management.map((x:any)=><li key={`${x.action}-${x.urgency}`}><b>{x.action}</b> — {x.rationale}</li>)}</ul></>}
          {!!suggestion.payload?.guidelines?.length&&<><strong>Diretrizes consultadas</strong><ul>{suggestion.payload.guidelines.map((x:any)=><li key={`${x.title}-${x.url}`}><a href={x.url} target="_blank" rel="noreferrer">{x.organization}: {x.title}</a> — {x.evidence_summary}</li>)}</ul></>}
          <p className="pep-muted">{String(suggestion.payload?.disclaimer??"")}</p>
          {suggestion.status==="generated"&&<><label>Sua interpretação médica final<textarea rows={4} value={finalInterpretation} onChange={e=>setFinalInterpretation(e.target.value)} placeholder="Obrigatória para aceitar e registrar como resultado clínico"/></label><label>Nota de revisão<input value={reviewNote} onChange={e=>setReviewNote(e.target.value)} placeholder="Opcional"/></label><div className="pep-actions"><button className="botao" disabled={busy||!finalInterpretation.trim()} onClick={()=>void review("accept")}>Aceitar após revisão</button><button className="botao botao--secundario" disabled={busy} onClick={()=>void review("reject")}>Rejeitar sugestão</button></div></>}
        </div>}
      </>}</div>
    </div>}
  </section>;
}
