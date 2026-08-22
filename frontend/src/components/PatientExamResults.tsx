import { useEffect, useState } from "react";
import { api } from "../lib/api";

type Kind = "laboratorial" | "metodo_grafico" | "imagem" | "outro";
type CatalogItem = {id:number;slug:string;name:string;category:string};
type CatalogResponse = {items:CatalogItem[]};
type ExamResult = {
  id:number; exam_kind:Kind; exam_name:string; performed_at:string; result:string;
  unit:string|null; reference_range:string|null; notes:string|null;
  lab_test_id:number|null; lab_test_slug:string|null; lab_test_name:string|null;
  source_encounter_id:number|null; correction_of_id:number|null; correction_reason:string|null;
};

const KIND_LABEL:Record<Kind,string>={
  laboratorial:"Laboratorial",metodo_grafico:"Método gráfico",imagem:"Imagem",outro:"Outro",
};

function agoraLocal(){
  const d=new Date(Date.now()-new Date().getTimezoneOffset()*60000);
  return d.toISOString().slice(0,16);
}
function quando(v:string){return new Intl.DateTimeFormat("pt-BR",{dateStyle:"short",timeStyle:"short"}).format(new Date(v));}

export default function PatientExamResults({patientId,currentEncounterId,onChanged}:{patientId:number;currentEncounterId:number|null;onChanged?:()=>void}){
  const [itens,setItens]=useState<ExamResult[]>([]),[kind,setKind]=useState<Kind>("laboratorial"),[name,setName]=useState("");
  const [result,setResult]=useState(""),[unit,setUnit]=useState(""),[referenceRange,setReferenceRange]=useState(""),[notes,setNotes]=useState("");
  const [performedAt,setPerformedAt]=useState(agoraLocal()),[catalog,setCatalog]=useState<CatalogItem[]>([]),[catalogId,setCatalogId]=useState("");
  const [erro,setErro]=useState(""),[salvando,setSalvando]=useState(false);

  const carregar=()=>api.get<ExamResult[]>(`/pacientes/${patientId}/resultados`).then(setItens).catch(e=>setErro(e.message));
  useEffect(()=>{carregar();},[patientId]); // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(()=>{
    const q=name.trim();
    if(q.length<2){setCatalog([]);setCatalogId("");return;}
    const timer=window.setTimeout(()=>{
      api.get<CatalogResponse>(`/lab-tests?q=${encodeURIComponent(q)}&limit=8`)
        .then(r=>setCatalog(r.items||[])).catch(()=>setCatalog([]));
    },250);
    return()=>window.clearTimeout(timer);
  },[name]);

  function selecionarCatalogo(valor:string){
    setCatalogId(valor);
    const id=Number(valor);const item=catalog.find(x=>x.id===id);
    if(!item)return;
    setName(item.name);
    if(["laboratorial","metodo_grafico","imagem"].includes(item.category))setKind(item.category as Kind);
  }

  async function adicionar(){
    if(!name.trim()||!result.trim())return;setSalvando(true);setErro("");
    try{
      await api.post(`/pacientes/${patientId}/resultados`,{
        exam_kind:kind,exam_name:name.trim(),performed_at:performedAt?new Date(performedAt).toISOString():null,
        result:result.trim(),unit:unit.trim()||null,reference_range:referenceRange.trim()||null,
        notes:notes.trim()||null,lab_test_id:catalogId?Number(catalogId):null,
        source_encounter_id:currentEncounterId||null,
      });
      setName("");setResult("");setUnit("");setReferenceRange("");setNotes("");setCatalogId("");setCatalog([]);setPerformedAt(agoraLocal());
      await carregar();onChanged?.();
    }catch(e){setErro(e instanceof Error?e.message:"Falha ao registrar resultado de exame.");}
    finally{setSalvando(false);}
  }

  return <section className="pep-card pep-history" style={{marginTop:"0.8rem"}}>
    <div className="pep-title"><div><p className="eyebrow">Exames e resultados</p><h2>Histórico de resultados</h2></div><small>{itens.length} registro(s)</small></div>
    {erro&&<p role="alert" className="pep-error">{erro}</p>}
    {!itens.length&&<p className="pep-muted">Ainda não há resultados registrados para este paciente.</p>}
    {itens.slice(0,12).map(item=><article key={item.id}>
      <div><strong>{item.correction_of_id?"Correção · ":""}{item.exam_name}</strong><time>{quando(item.performed_at)}</time></div>
      <p>{item.result}{item.unit?` ${item.unit}`:""}</p>
      <small>{[KIND_LABEL[item.exam_kind],item.reference_range?`Referência: ${item.reference_range}`:null,item.source_encounter_id?`Atendimento #${item.source_encounter_id}`:null].filter(Boolean).join(" · ")}</small>
      {item.notes&&<p className="pep-muted">{item.notes}</p>}
      {item.lab_test_slug&&<a href={`/exames/${item.lab_test_slug}`}>Abrir conteúdo científico CorVIA</a>}
    </article>)}
    <div className="grade grade--3" style={{marginTop:"0.8rem"}}>
      <label>Tipo<select value={kind} onChange={e=>setKind(e.target.value as Kind)}><option value="laboratorial">Laboratorial</option><option value="metodo_grafico">Método gráfico</option><option value="imagem">Imagem</option><option value="outro">Outro</option></select></label>
      <label>Exame<input value={name} onChange={e=>{setName(e.target.value);setCatalogId("");}} placeholder="Ex.: Troponina, ECG, Ecocardiograma"/></label>
      <label>Data do exame<input type="datetime-local" value={performedAt} onChange={e=>setPerformedAt(e.target.value)}/></label>
    </div>
    {!!catalog.length&&<label style={{display:"block",marginTop:"0.5rem"}}>Vincular ao catálogo científico CorVIA (opcional)<select value={catalogId} onChange={e=>selecionarCatalogo(e.target.value)}><option value="">Sem vínculo</option>{catalog.map(item=><option key={item.id} value={item.id}>{item.name}</option>)}</select></label>}
    <div className="grade grade--3" style={{marginTop:"0.5rem"}}>
      <label>Resultado / achado<input value={result} onChange={e=>setResult(e.target.value)} placeholder="Valor, conclusão ou achado principal"/></label>
      <label>Unidade<input value={unit} onChange={e=>setUnit(e.target.value)} placeholder="Opcional"/></label>
      <label>Referência<input value={referenceRange} onChange={e=>setReferenceRange(e.target.value)} placeholder="Opcional"/></label>
    </div>
    <label style={{display:"block",marginTop:"0.5rem"}}>Observações<textarea rows={2} value={notes} onChange={e=>setNotes(e.target.value)} placeholder="Opcional; não substitui o laudo original quando houver arquivo/documento."/></label>
    <button className="botao" style={{marginTop:"0.5rem"}} onClick={adicionar} disabled={salvando||!name.trim()||!result.trim()}>{salvando?"Registrando…":"+ Registrar resultado"}</button>
  </section>;
}
