import { useEffect, useRef, useState } from "react";
import { api } from "../lib/api";

type Kind="laboratorial"|"metodo_grafico"|"imagem"|"outro";
type Result={id:number;exam_kind:Kind;exam_name:string;performed_at:string;structured_result:string|null;report_text:string|null;unit:string|null;reference_range:string|null;notes:string|null;source:string|null;lab_test_id:number|null;lab_test_slug:string|null;source_encounter_id:number|null;correction_of_id:number|null;corrected_by_id:number|null;correction_reason:string|null;is_superseded:boolean;created_at:string};
type Form={kind:Kind;name:string;value:string;report:string;unit:string;reference:string;notes:string;source:string;performedAt:string;reason:string};

export const toDateTimeLocal=(value:Date|string=new Date())=>{const date=value instanceof Date?value:new Date(value);return new Date(date.getTime()-date.getTimezoneOffset()*60000).toISOString().slice(0,16);};
const now=()=>toDateTimeLocal();
const empty=():Form=>({kind:"laboratorial",name:"",value:"",report:"",unit:"",reference:"",notes:"",source:"",performedAt:now(),reason:""});
const when=(v:string)=>new Date(v).toLocaleString("pt-BR");

export default function PatientExamResults({patientId,currentEncounterId,onChanged}:{patientId:number;currentEncounterId:number|null;onChanged?:()=>void}){
  const base=`/pacientes/${patientId}/resultados`;
  const [items,setItems]=useState<Result[]>([]),[form,setForm]=useState<Form>(empty()),[correction,setCorrection]=useState<Result|null>(null);
  const [error,setError]=useState(""),[saving,setSaving]=useState(false);
  const activePatientId=useRef(patientId);activePatientId.current=patientId;
  const change=<K extends keyof Form>(key:K,value:Form[K])=>setForm(x=>({...x,[key]:value}));
  const load=(expectedPatientId=patientId)=>api.get<Result[]>(`/pacientes/${expectedPatientId}/resultados`)
    .then(data=>{if(activePatientId.current===expectedPatientId)setItems(data);})
    .catch(e=>{if(activePatientId.current===expectedPatientId)setError(e.message);});
  const clear=()=>{setForm(empty());setCorrection(null);};
  const field=(label:string,key:keyof Form)=><label>{label}<input value={form[key]} onChange={e=>change(key,e.target.value)}/></label>;
  useEffect(()=>{setItems([]);setError("");setSaving(false);clear();load();},[patientId]); // eslint-disable-line react-hooks/exhaustive-deps

  function correct(x:Result){setCorrection(x);setForm({kind:x.exam_kind,name:x.exam_name,value:x.structured_result||"",report:x.report_text||"",unit:x.unit||"",reference:x.reference_range||"",notes:x.notes||"",source:x.source||"",performedAt:toDateTimeLocal(x.performed_at),reason:""});}
  async function save(){
    const expectedPatientId=patientId,expectedBase=base;
    if(!form.performedAt||!form.name.trim()||(!form.value.trim()&&!form.report.trim())||(correction&&!form.reason.trim()))return;
    setSaving(true);setError("");
    const body={exam_kind:form.kind,exam_name:form.name.trim(),performed_at:new Date(form.performedAt).toISOString(),structured_result:form.value.trim()||null,report_text:form.report.trim()||null,unit:form.unit.trim()||null,reference_range:form.reference.trim()||null,notes:form.notes.trim()||null,source:form.source.trim()||null,lab_test_id:correction?.lab_test_id||null,source_encounter_id:currentEncounterId||correction?.source_encounter_id||null,...(correction?{correction_reason:form.reason.trim()}:{})};
    try{await api.post(correction?`${expectedBase}/${correction.id}/correcoes`:expectedBase,body);if(activePatientId.current!==expectedPatientId)return;clear();await load(expectedPatientId);if(activePatientId.current===expectedPatientId)onChanged?.();}
    catch(e){if(activePatientId.current===expectedPatientId)setError(e instanceof Error?e.message:"Falha.");}finally{if(activePatientId.current===expectedPatientId)setSaving(false);}
  }

  return <section className="pep-card pep-history">
    <h2>Exames e resultados</h2>
    {error&&<p role="alert" className="pep-error">{error}</p>}
    {items.slice(0,12).map(x=><article key={x.id}>
      <div><strong>{x.correction_of_id?"Correção · ":""}{x.exam_name}</strong><time>{when(x.performed_at)}</time></div>
      <p>{x.structured_result}{x.structured_result&&x.unit?` ${x.unit}`:""}{!x.structured_result&&x.report_text}</p>
      <small>{[x.exam_kind,x.source,x.is_superseded?"Substituído":null].filter(Boolean).join(" · ")}</small>
      <details><summary>Detalhes</summary><small>{[x.reference_range?`Referência: ${x.reference_range}`:null,x.notes,x.correction_of_id?`Corrige #${x.correction_of_id}`:null,x.corrected_by_id?`Substituído por #${x.corrected_by_id}`:null,x.correction_reason].filter(Boolean).join(" · ")}</small></details>
      {x.lab_test_slug&&<a href={`/exames/${x.lab_test_slug}`}>Catálogo</a>}{!x.is_superseded&&<button onClick={()=>correct(x)}>Corrigir</button>}
    </article>)}
    <div className="pep-title"><h2>{correction?`Corrigir #${correction.id}`:"Registrar resultado"}</h2>{correction&&<button onClick={clear}>Cancelar</button>}</div>
    <div className="grade grade--3">
      <label>Tipo<select value={form.kind} onChange={e=>change("kind",e.target.value as Kind)}><option value="laboratorial">Laboratorial</option><option value="metodo_grafico">Método gráfico</option><option value="imagem">Imagem</option><option value="outro">Outro</option></select></label>
      {field("Exame","name")}
      <label>Data clínica<input type="datetime-local" value={form.performedAt} onChange={e=>change("performedAt",e.target.value)} required/></label>
    </div>
    <div className="grade grade--3">
      {field("Valor estruturado","value")}{field("Unidade","unit")}{field("Referência","reference")}
    </div>
    <label>Laudo / resultado textual<textarea rows={3} value={form.report} onChange={e=>change("report",e.target.value)}/></label>
    <div className="grade grade--2">{field("Origem","source")}{field("Observações","notes")}</div>
    {correction&&<label>Motivo da correção<textarea rows={2} value={form.reason} onChange={e=>change("reason",e.target.value)} required/></label>}
    <button className="botao" onClick={save} disabled={saving||!form.performedAt||!form.name.trim()||(!form.value.trim()&&!form.report.trim())||!!correction&&!form.reason.trim()}>{saving?"Registrando…":correction?"Registrar correção":"+ Registrar resultado"}</button>
  </section>;
}
