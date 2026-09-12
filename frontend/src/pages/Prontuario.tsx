import { useEffect, useMemo, useRef, useState } from "react";
import { useSearchParams } from "react-router-dom";
import PatientClinicalSummary from "../components/PatientClinicalSummary";
import { api } from "../lib/api";
import { parseVitalSigns } from "../lib/clinicalInput";
import "../styles/prontuario.css";

type Paciente = { id:number; full_name:string; birth_date:string|null; sex:string|null; phone:string|null };
type Encounter = {
  id:number; appointment_id:number|null; encounter_type:string; status:string; started_at:string; finalized_at:string|null;
  chief_complaint:string|null; anamnesis:string|null; physical_exam:string|null;
  assessment:string|null; plan:string|null; vital_signs:Record<string,number|string>;
  amendment_of_id?:number|null; amendment_reason?:string|null;
};
type Fila = {appointment_id:number;scheduled_at:string;patient_name:string;patient_profile_id:number|null;state:string;arrived_at:string|null;encounter_id:number|null};
type Artefato = {id?:number;tipo:"prescricao"|"documento";artifact_id:number;created_at:string;titulo:string;doc_type?:string|null;detalhes?:Array<{tipo:string;status:string}>};
type Form = {
  encounter_type:string; chief_complaint:string; anamnesis:string; physical_exam:string;
  assessment:string; plan:string; pa_sistolica:string; pa_diastolica:string;
  fc:string; fr:string; spo2:string; temperatura:string;
  amendment_of_id:string; amendment_reason:string;
};

const VAZIO:Form={encounter_type:"consulta",chief_complaint:"",anamnesis:"",physical_exam:"",assessment:"",plan:"",pa_sistolica:"",pa_diastolica:"",fc:"",fr:"",spo2:"",temperatura:"",amendment_of_id:"",amendment_reason:""};
const VITAIS:Array<[keyof Form,string]>=[["pa_sistolica","PA sist."],["pa_diastolica","PA diast."],["fc","FC"],["fr","FR"],["spo2","SpO₂"],["temperatura","Temp."]];
const TEXTOS:Array<[keyof Form,string,number]>=[["chief_complaint","Motivo / queixa principal",2],["anamnesis","Anamnese",5],["physical_exam","Exame físico",3],["assessment","Avaliação",3],["plan","Plano / conduta",4]];
const ESTADOS:Record<string,string>={scheduled:"Agendado",arrived:"Aguardando",called:"Chamado",in_service:"Em atendimento",completed:"Concluído"};

function quando(v:string){return new Intl.DateTimeFormat("pt-BR",{dateStyle:"short",timeStyle:"short"}).format(new Date(v));}
function hora(v:string){return new Date(v).toLocaleTimeString("pt-BR",{hour:"2-digit",minute:"2-digit"});}
function espera(v:string|null){return v?`${Math.max(0,Math.floor((Date.now()-new Date(v).getTime())/60000))} min`:"—";}
function doEncounter(e:Encounter):Form{
  const s=e.vital_signs||{}; const v=(k:string)=>s[k]===undefined?"":String(s[k]);
  return {...VAZIO,encounter_type:e.encounter_type||"consulta",chief_complaint:e.chief_complaint||"",anamnesis:e.anamnesis||"",physical_exam:e.physical_exam||"",assessment:e.assessment||"",plan:e.plan||"",pa_sistolica:v("pa_sistolica"),pa_diastolica:v("pa_diastolica"),fc:v("fc"),fr:v("fr"),spo2:v("spo2"),temperatura:v("temperatura"),amendment_of_id:e.amendment_of_id?String(e.amendment_of_id):"",amendment_reason:e.amendment_reason||""};
}
function payload(f:Form){
  const vital_signs = parseVitalSigns(f);
  return {encounter_type:f.encounter_type,chief_complaint:f.chief_complaint||null,anamnesis:f.anamnesis||null,physical_exam:f.physical_exam||null,assessment:f.assessment||null,plan:f.plan||null,vital_signs,...(f.amendment_of_id?{amendment_of_id:Number(f.amendment_of_id),amendment_reason:f.amendment_reason.trim()}: {})};
}

export default function Prontuario(){
  const [qs,setQs]=useSearchParams();
  const [pacientes,setPacientes]=useState<Paciente[]>([]),[encounters,setEncounters]=useState<Encounter[]>([]),[fila,setFila]=useState<Fila[]>([]);
  const [artefatos,setArtefatos]=useState<Artefato[]>([]),[candidatos,setCandidatos]=useState<Artefato[]>([]);
  const [busca,setBusca]=useState(""),[novoNome,setNovoNome]=useState(""),[erro,setErro]=useState("");
  const [editor,setEditor]=useState(false),[editando,setEditando]=useState<number|null>(null),[form,setForm]=useState<Form>(VAZIO),[salvando,setSalvando]=useState(false);
  const pid=Number(qs.get("paciente")||0)||null;
  const paciente=pacientes.find(p=>p.id===pid)||null;
  const contexto=useMemo(()=>({pid}),[pid]),contextoAtual=useRef(contexto),montado=useRef(false);
  // A response is owned by this selection, not just by an ID that may be selected again.
  contextoAtual.current=contexto;
  const versaoEditor=useRef(0),consultaHistorico=useRef(0),consultaArtefatos=useRef(0),consultaFila=useRef(0);
  const operacao=useRef<object|null>(null),acaoFilaPendente=useRef(false),cadastroPendente=useRef(false);
  const [contextoExibido,setContextoExibido]=useState(contexto),[carregandoHistorico,setCarregandoHistorico]=useState(true),[erroHistorico,setErroHistorico]=useState("");
  const [criando,setCriando]=useState(false),[filaOcupada,setFilaOcupada]=useState(false);
  const atendimentoDaFila=useRef<{pid:number;encounter:Encounter}|null>(null);
  const [formSalvo,setFormSalvo]=useState<Form>(VAZIO);
  const descarteAprovado=useRef(false),restaurarPaciente=useRef<number|null>(null);
  const registroAberto=encounters.find(e=>e.id===editando);
  const somenteLeitura=Boolean(registroAberto && ["finalized","amended","cancelled"].includes(registroAberto.status));
  const alterado=editor&&!somenteLeitura&&JSON.stringify(form)!==JSON.stringify(formSalvo);
  function confirmarDescarte(){return !alterado||window.confirm("Há alterações não salvas neste atendimento. Deseja descartá-las?");}
  useEffect(()=>{
    if(!alterado)return;
    const avisar=(e:BeforeUnloadEvent)=>{e.preventDefault();e.returnValue="";};
    const navegar=(e:MouseEvent)=>{const a=(e.target as Element)?.closest?.("a[href]") as HTMLAnchorElement|null;if(!a||a.target==="_blank"||a.download||e.defaultPrevented||e.ctrlKey||e.metaKey||e.shiftKey||e.altKey)return;if(new URL(a.href).pathname===window.location.pathname)return;if(!confirmarDescarte()){e.preventDefault();e.stopPropagation();}};
    window.addEventListener("beforeunload",avisar);document.addEventListener("click",navegar,true);
    return()=>{window.removeEventListener("beforeunload",avisar);document.removeEventListener("click",navegar,true);};
  },[alterado]);
  const atual=()=>montado.current&&contextoAtual.current===contexto;

  async function carregarFila(){
    const consulta=++consultaFila.current;
    try{const lista=await api.get<Fila[]>("/agenda-clinica/hoje");if(montado.current&&consulta===consultaFila.current)setFila(lista);}
    catch(e){if(atual()&&consulta===consultaFila.current)setErro(e instanceof Error?e.message:"Falha ao carregar sala de espera.");}
  }
  async function carregarHistorico(){
    const consulta=++consultaHistorico.current;
    setCarregandoHistorico(true);setErroHistorico("");
    if(!pid){setCarregandoHistorico(false);return;}
    try{const lista=await api.get<Encounter[]>(`/pacientes/${pid}/atendimentos`);if(atual()&&consulta===consultaHistorico.current)setEncounters(lista);}
    catch(e){if(atual()&&consulta===consultaHistorico.current)setErroHistorico(e instanceof Error?e.message:"Falha ao carregar histórico.");}
    finally{if(atual()&&consulta===consultaHistorico.current)setCarregandoHistorico(false);}
  }
  async function carregarArtefatos(){
    if(!pid||!editando)return;
    const consulta=++consultaArtefatos.current,versao=versaoEditor.current,b=`/pacientes/${pid}/atendimentos/${editando}/artefatos`;
    try{const [a,c]=await Promise.all([api.get<Artefato[]>(b),somenteLeitura?Promise.resolve([]):api.get<Artefato[]>(`${b}/candidatos`)]);if(atual()&&consulta===consultaArtefatos.current&&versao===versaoEditor.current){setArtefatos(a);setCandidatos(c);}}
    catch(e){if(atual()&&consulta===consultaArtefatos.current&&versao===versaoEditor.current)setErro(e instanceof Error?e.message:"Falha ao carregar documentos do atendimento.");}
  }
  useEffect(()=>{
    montado.current=true;let ativo=true;
    api.get<Paciente[]>("/pacientes").then(lista=>{if(!ativo)return;setPacientes(lista);if(lista[0])setQs(atualQs=>{if(atualQs.get("paciente"))return atualQs;const next=new URLSearchParams(atualQs);next.set("paciente",String(lista[0].id));return next;},{replace:true});}).catch(e=>{if(ativo)setErro(e.message);});
    carregarFila();return()=>{ativo=false;montado.current=false;};
  },[]); // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(()=>{
    if(restaurarPaciente.current!==null&&restaurarPaciente.current===pid){restaurarPaciente.current=null;setContextoExibido(contexto);carregarHistorico();return()=>{consultaHistorico.current++;consultaArtefatos.current++;};}
    if(contextoExibido.pid!==pid&&alterado&&!descarteAprovado.current&&!confirmarDescarte()){
      restaurarPaciente.current=contextoExibido.pid;
      const anterior=new URLSearchParams(qs);if(contextoExibido.pid)anterior.set("paciente",String(contextoExibido.pid));else anterior.delete("paciente");
      setQs(anterior,{replace:true});return;
    }
    descarteAprovado.current=false;
    versaoEditor.current+=1;consultaArtefatos.current+=1;operacao.current=null;
    setContextoExibido(contexto);setEncounters([]);setArtefatos([]);setCandidatos([]);setErro("");setSalvando(false);
    const pendente=atendimentoDaFila.current;atendimentoDaFila.current=null;
    const inicial=pendente?.pid===pid?doEncounter(pendente.encounter):VAZIO;
    setEditor(pendente?.pid===pid);setEditando(pendente?.pid===pid?pendente.encounter.id:null);setForm(inicial);setFormSalvo(inicial);
    carregarHistorico();
    return()=>{consultaHistorico.current+=1;consultaArtefatos.current+=1;};
  },[contexto]); // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(()=>{setArtefatos([]);setCandidatos([]);if(!editando||contextoExibido!==contexto)return;carregarArtefatos();const f=()=>carregarArtefatos();window.addEventListener("focus",f);return()=>{consultaArtefatos.current+=1;window.removeEventListener("focus",f);};},[contexto,editando,contextoExibido]); // eslint-disable-line react-hooks/exhaustive-deps

  const filtrados=useMemo(()=>{const q=busca.trim().toLocaleLowerCase("pt-BR");return q?pacientes.filter(p=>p.full_name.toLocaleLowerCase("pt-BR").includes(q)):pacientes;},[busca,pacientes]);
  const selecionar=(id:number,descarteConfirmado=false)=>{if(id===pid||operacao.current||(!descarteConfirmado&&!confirmarDescarte()))return;descarteAprovado.current=true;const next=new URLSearchParams(qs);next.set("paciente",String(id));setQs(next);};

  async function criarPaciente(){
    const nome=novoNome.trim(); if(!nome||cadastroPendente.current)return;
    cadastroPendente.current=true;setCriando(true);
    try{const p=await api.post<Paciente>("/pacientes",{full_name:nome});if(!montado.current)return;setPacientes(x=>[p,...x]);setNovoNome("");if(atual())selecionar(p.id);}catch(e){if(atual())setErro(e instanceof Error?e.message:"Falha ao cadastrar paciente.");}finally{cadastroPendente.current=false;if(montado.current)setCriando(false);}
  }
  function invalidarEditor(){versaoEditor.current+=1;consultaArtefatos.current+=1;setArtefatos([]);setCandidatos([]);setErro("");}
  function abrirNovo(){if(operacao.current||!confirmarDescarte())return;invalidarEditor();setEditando(null);setForm(VAZIO);setFormSalvo(VAZIO);setEditor(true);}
  function abrir(e:Encounter,descarteConfirmado=false){if(operacao.current||(editor&&editando===e.id)||(!descarteConfirmado&&!confirmarDescarte()))return;invalidarEditor();const inicial=doEncounter(e);setEditando(e.id);setForm(inicial);setFormSalvo(inicial);setEditor(true);}
  function abrirAdendo(){if(!registroAberto||!["finalized","amended"].includes(registroAberto.status)||operacao.current||!confirmarDescarte())return;const inicial={...VAZIO,encounter_type:"adendo",amendment_of_id:String(registroAberto.id)};invalidarEditor();setEditando(null);setForm(inicial);setFormSalvo(inicial);setEditor(true);}
  function fecharEditor(){if(operacao.current||!confirmarDescarte())return;invalidarEditor();setEditor(false);setEditando(null);setForm(VAZIO);setFormSalvo(VAZIO);}
  async function salvar(finalizarDepois=false){
    if(!pid||operacao.current||contextoExibido!==contexto||somenteLeitura)return;
    if(form.amendment_of_id&&!form.amendment_reason.trim()){setErro("Informe o motivo do adendo.");return;}
    const token={},versao=versaoEditor.current;
    operacao.current=token;setSalvando(true);setErro("");
    const aceita=()=>atual()&&operacao.current===token&&versao===versaoEditor.current;
    try{
      const p=payload(form),salvo=editando?await api.patch<Encounter>(`/pacientes/${pid}/atendimentos/${editando}`,p):await api.post<Encounter>(`/pacientes/${pid}/atendimentos`,p);
      if(!aceita())return;
      const canonico=doEncounter(salvo);setForm(canonico);setFormSalvo(canonico);
      consultaHistorico.current+=1;setCarregandoHistorico(true);setErroHistorico("");setEditando(salvo.id);setEncounters(x=>[salvo,...x.filter(i=>i.id!==salvo.id)]);
      if(!finalizarDepois){void carregarHistorico();return;}
      let e:Encounter;
      try{e=await api.post<Encounter>(`/pacientes/${pid}/atendimentos/${salvo.id}/finalizar`);}
      finally{if(aceita())void carregarHistorico();}
      if(!aceita())return;
      setEncounters(x=>[e,...x.filter(i=>i.id!==e.id)]);setEditor(false);setEditando(null);setForm(VAZIO);consultaArtefatos.current+=1;
      if(e.appointment_id)try{await api.post(`/agenda-clinica/${e.appointment_id}/transicao`,{action:"complete"});if(aceita())await carregarFila();}catch{if(aceita())setErro("Atendimento finalizado; fila pendente de atualização.");}
    }catch(e){if(aceita())setErro(e instanceof Error?e.message:"Falha ao salvar ou finalizar atendimento.");}
    finally{if(aceita()){operacao.current=null;setSalvando(false);}}
  }
  async function anexar(a:Artefato){
    if(!pid||!editando||operacao.current||somenteLeitura)return;
    const token={},versao=versaoEditor.current;operacao.current=token;setSalvando(true);setErro("");
    const aceita=()=>atual()&&operacao.current===token&&versao===versaoEditor.current;
    try{await api.post(`/pacientes/${pid}/atendimentos/${editando}/artefatos`,{tipo:a.tipo,artifact_id:a.artifact_id});if(aceita())await carregarArtefatos();}catch(e){if(aceita())setErro(e instanceof Error?e.message:"Falha ao vincular artefato.");}finally{if(aceita()){operacao.current=null;setSalvando(false);}}
  }
  async function vincular(item:Fila,id:number){if(acaoFilaPendente.current)return;acaoFilaPendente.current=true;setFilaOcupada(true);try{await api.post(`/agenda-clinica/${item.appointment_id}/vincular`,{patient_profile_id:id});if(montado.current)await carregarFila();}catch(e){if(atual())setErro(e instanceof Error?e.message:"Falha ao vincular paciente.");}finally{acaoFilaPendente.current=false;if(montado.current)setFilaOcupada(false);}}
  async function acaoFila(item:Fila,action:string){
    if(action==="start"&&!confirmarDescarte())return;
    if(acaoFilaPendente.current||operacao.current)return;acaoFilaPendente.current=true;setFilaOcupada(true);const versao=versaoEditor.current;
    try{
      const r=await api.post<Fila>(`/agenda-clinica/${item.appointment_id}/transicao`,{action});
      if(!atual()||versao!==versaoEditor.current||operacao.current)return;
      if(action==="start"&&r.patient_profile_id&&r.encounter_id){const e=await api.get<Encounter>(`/pacientes/${r.patient_profile_id}/atendimentos/${r.encounter_id}`);if(!atual()||versao!==versaoEditor.current||operacao.current)return;if(r.patient_profile_id===pid){abrir(e,true);setEncounters(x=>[e,...x.filter(i=>i.id!==e.id)]);void carregarHistorico();}else{atendimentoDaFila.current={pid:r.patient_profile_id,encounter:e};selecionar(r.patient_profile_id,true);}}else await carregarFila();
    }catch(e){if(atual()&&versao===versaoEditor.current)setErro(e instanceof Error?e.message:"Falha ao atualizar sala de espera.");}finally{acaoFilaPendente.current=false;if(montado.current)setFilaOcupada(false);}
  }

  return <div className="pep">
    <header className="pep-head"><div><p className="eyebrow">Prontuário Eletrônico CorVIA</p><h1>Pacientes e atendimentos</h1></div><div className="pep-add"><input aria-label="Nome do novo paciente" placeholder="Nome do novo paciente" disabled={criando} value={novoNome} onChange={e=>setNovoNome(e.target.value)} onKeyDown={e=>{if(e.key==="Enter")criarPaciente();}}/><button className="botao" disabled={criando} onClick={criarPaciente}>{criando?"Cadastrando…":"+ Paciente"}</button></div></header>
    {erro&&<p className="pep-error" role="alert">{erro}</p>}
    {!!fila.length&&<section className="pep-card pep-history"><h2>Sala de espera</h2>{fila.map(item=><article key={item.appointment_id}><div><strong>{hora(item.scheduled_at)} · {item.patient_name}</strong><time>{ESTADOS[item.state]||item.state}</time></div><p>Chegada {item.arrived_at?hora(item.arrived_at):"—"} · espera {espera(item.arrived_at)}</p><div className="pep-actions">{!item.patient_profile_id?<select disabled={filaOcupada||salvando} aria-label={`Vincular ${item.patient_name}`} value="" onChange={e=>{const id=Number(e.target.value);if(id)vincular(item,id);}}><option value="" disabled>Vincular prontuário…</option>{pacientes.map(p=><option key={p.id} value={p.id}>{p.full_name}</option>)}</select>:item.state==="scheduled"?<button disabled={filaOcupada||salvando} onClick={()=>acaoFila(item,"arrive")}>Chegou</button>:item.state==="arrived"?<button disabled={filaOcupada||salvando} onClick={()=>acaoFila(item,"call")}>Chamar</button>:item.state!=="completed"?<button disabled={filaOcupada||salvando} onClick={()=>acaoFila(item,"start")}>{item.state==="in_service"?"Abrir atendimento":"Atender"}</button>:null}</div></article>)}</section>}
    <div className="pep-grid">
      <aside className="pep-list"><input aria-label="Buscar paciente" placeholder="Buscar paciente" value={busca} onChange={e=>setBusca(e.target.value)}/><div>{filtrados.map(p=><button key={p.id} className={p.id===pid?"is-active":""} onClick={()=>selecionar(p.id)}><span>{p.full_name[0]?.toUpperCase()}</span><strong>{p.full_name}</strong></button>)}{!filtrados.length&&<small>Nenhum paciente.</small>}</div></aside>
      <main className="pep-main">
        {!paciente?<section className="pep-card pep-empty">Selecione ou cadastre um paciente.</section>:contextoExibido!==contexto?<p role="status">Carregando prontuário…</p>:<>
          <section className="pep-card pep-patient"><div><p className="eyebrow">Paciente</p><h2>{paciente.full_name}</h2><small>{[paciente.birth_date,paciente.sex,paciente.phone].filter(Boolean).join(" · ")||"Dados complementares não informados"}</small></div><button className="botao" disabled={salvando} onClick={abrirNovo}>+ Iniciar atendimento</button></section>
          <PatientClinicalSummary key={paciente.id} patientId={paciente.id} currentEncounterId={editando} focusECG={qs.get("acao")==="ecg"}/>
          <div className="pep-clinical">
            <section className="pep-card pep-history"><div className="pep-title"><h2>Histórico</h2>{!carregandoHistorico&&!erroHistorico&&<small>{encounters.length} atendimento(s)</small>}</div>{carregandoHistorico?<p role="status">Carregando histórico…</p>:erroHistorico?<><p role="alert" className="pep-error">{erroHistorico}</p><button className="botao botao--secundario" onClick={carregarHistorico}>Recarregar histórico</button></>:!encounters.length&&<p className="pep-muted">Ainda não há atendimentos.</p>}{encounters.map(e=><article key={e.id}><div><strong>{e.encounter_type==="adendo"?"Adendo":"Atendimento"}</strong><time>{quando(e.started_at)}</time></div><p>{e.chief_complaint||e.assessment||"Sem resumo registrado."}</p>{["finalized","amended","cancelled"].includes(e.status)&&<small>Encerrado · histórico preservado</small>}<button disabled={salvando} onClick={()=>abrir(e)}>{["finalized","amended","cancelled"].includes(e.status)?"Ver atendimento completo":"Continuar"}</button></article>)}</section>
            <section className="pep-card pep-editor">
              {!editor?<div className="pep-empty"><strong>Novo atendimento</strong><p>Registre a evolução e finalize quando concluída.</p><button className="botao" onClick={abrirNovo}>Iniciar</button></div>:<>
                <div className="pep-title"><div><p className="eyebrow">{somenteLeitura?"Histórico · somente leitura":form.amendment_of_id?"Adendo":editando?"Em andamento":"Novo atendimento"}</p><h2>Evolução clínica</h2></div><button disabled={salvando} onClick={fecharEditor}>Fechar</button></div>
                {somenteLeitura?<>
                  <p>Atendimento encerrado em {registroAberto?.finalized_at?quando(registroAberto.finalized_at):"data não informada"}. O registro original permanece imutável.</p>
                  {form.amendment_of_id&&<p>Adendo do atendimento #{form.amendment_of_id} · Motivo: {form.amendment_reason}</p>}
                  <dl>{VITAIS.map(([k,l])=><div key={k}><dt>{l}</dt><dd>{form[k]||"Não registrado"}</dd></div>)}{TEXTOS.map(([k,l])=><div key={k}><dt><strong>{l}</strong></dt><dd style={{whiteSpace:"pre-wrap",overflowWrap:"anywhere",marginLeft:0}}>{form[k]||"Não registrado"}</dd></div>)}</dl>
                  <div><p className="eyebrow">Prescrições e documentos vinculados</p>{!artefatos.length&&<p>Nenhum documento vinculado.</p>}{artefatos.map(a=><p key={`${a.tipo}-${a.artifact_id}`}><a href={a.tipo==="prescricao"?`/receituario?prescricao=${a.artifact_id}`:`/documentos?paciente=${pid}`} target="_blank" rel="noreferrer">{a.titulo} · {quando(a.created_at)}</a></p>)}</div>
                  {registroAberto&&["finalized","amended"].includes(registroAberto.status)&&<button className="botao botao--secundario" onClick={abrirAdendo}>Registrar adendo</button>}
                </>:<>
                <fieldset className="pep-editor-fields" disabled={salvando} style={{border:0,padding:0,margin:0,minWidth:0,display:"grid",gap:".5rem"}} aria-label="Dados do atendimento">
                <label>Tipo<select aria-label="Tipo" disabled={Boolean(form.amendment_of_id)} value={form.encounter_type} onChange={e=>setForm({...form,encounter_type:e.target.value})}><option value="consulta">Consulta</option><option value="retorno">Retorno</option><option value="pre_operatorio">Pré-operatório</option><option value="teleconsulta">Teleconsulta</option><option value="outro">Outro</option>{form.amendment_of_id&&<option value="adendo">Adendo</option>}</select></label>
                {form.amendment_of_id&&<label>Motivo do adendo ao atendimento #{form.amendment_of_id}<textarea required readOnly={Boolean(editando)} value={form.amendment_reason} onChange={e=>setForm({...form,amendment_reason:e.target.value})}/></label>}
                <div className="pep-vitals">{VITAIS.map(([k,l])=><label key={k}>{l}<input value={String(form[k])} inputMode="decimal" onChange={e=>setForm({...form,[k]:e.target.value})}/></label>)}</div>
                {TEXTOS.map(([k,l,r])=><label key={k}>{l}{r===2?<input value={String(form[k])} onChange={e=>setForm({...form,[k]:e.target.value})}/>:<textarea rows={r} value={String(form[k])} onChange={e=>setForm({...form,[k]:e.target.value})}/>}</label>)}
                {editando&&<div><p className="eyebrow">Prescrições e documentos</p><div className="pep-actions"><a className="botao botao--secundario" href={`/receituario?paciente=${pid}&atendimento=${editando}`} target="_blank" rel="noreferrer">Abrir Receituário</a><a className="botao botao--secundario" href={`/documentos?paciente=${pid}&atendimento=${editando}`} target="_blank" rel="noreferrer">Abrir Documentos</a></div>{artefatos.map(a=><p className="pep-muted" key={`${a.tipo}-${a.artifact_id}`}>✓ {a.titulo} · {quando(a.created_at)}</p>)}{!!candidatos.length&&<div><small>Recentes do mesmo paciente:</small>{candidatos.slice(0,6).map(a=><button key={`${a.tipo}-${a.artifact_id}`} onClick={()=>anexar(a)}>+ Vincular {a.titulo} · {quando(a.created_at)}</button>)}</div>}</div>}
                </fieldset>
                <div className="pep-actions"><button className="botao botao--secundario" disabled={salvando} onClick={()=>salvar()}>Salvar rascunho</button><button className="botao" disabled={salvando} onClick={()=>salvar(true)}>Finalizar</button></div>
                </>}
              </>}
            </section>
          </div>
        </>}
      </main>
    </div>
  </div>;
}
