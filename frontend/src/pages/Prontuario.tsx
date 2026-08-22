import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api } from "../lib/api";
import "../styles/prontuario.css";

type Paciente = { id:number; full_name:string; birth_date:string|null; sex:string|null; phone:string|null };
type Encounter = {
  id:number; appointment_id:number|null; encounter_type:string; status:string; started_at:string; finalized_at:string|null;
  chief_complaint:string|null; anamnesis:string|null; physical_exam:string|null;
  assessment:string|null; plan:string|null; vital_signs:Record<string,number|string>;
};
type Fila = {appointment_id:number;scheduled_at:string;patient_name:string;patient_profile_id:number|null;state:string;arrived_at:string|null;encounter_id:number|null};
type Artefato = {id?:number;tipo:"prescricao"|"documento";artifact_id:number;created_at:string;titulo:string;doc_type?:string|null;detalhes?:Array<{tipo:string;status:string}>};
type Form = {
  encounter_type:string; chief_complaint:string; anamnesis:string; physical_exam:string;
  assessment:string; plan:string; pa_sistolica:string; pa_diastolica:string;
  fc:string; fr:string; spo2:string; temperatura:string;
};

const VAZIO:Form={encounter_type:"consulta",chief_complaint:"",anamnesis:"",physical_exam:"",assessment:"",plan:"",pa_sistolica:"",pa_diastolica:"",fc:"",fr:"",spo2:"",temperatura:""};
const VITAIS:Array<[keyof Form,string]>=[["pa_sistolica","PA sist."],["pa_diastolica","PA diast."],["fc","FC"],["fr","FR"],["spo2","SpO₂"],["temperatura","Temp."]];
const TEXTOS:Array<[keyof Form,string,number]>=[["chief_complaint","Motivo / queixa principal",2],["anamnesis","Anamnese",5],["physical_exam","Exame físico",3],["assessment","Avaliação",3],["plan","Plano / conduta",4]];
const ESTADOS:Record<string,string>={scheduled:"Agendado",arrived:"Aguardando",called:"Chamado",in_service:"Em atendimento",completed:"Concluído"};

function quando(v:string){return new Intl.DateTimeFormat("pt-BR",{dateStyle:"short",timeStyle:"short"}).format(new Date(v));}
function hora(v:string){return new Date(v).toLocaleTimeString("pt-BR",{hour:"2-digit",minute:"2-digit"});}
function espera(v:string|null){return v?`${Math.max(0,Math.floor((Date.now()-new Date(v).getTime())/60000))} min`:"—";}
function doEncounter(e:Encounter):Form{
  const s=e.vital_signs||{}; const v=(k:string)=>s[k]===undefined?"":String(s[k]);
  return {...VAZIO,encounter_type:e.encounter_type||"consulta",chief_complaint:e.chief_complaint||"",anamnesis:e.anamnesis||"",physical_exam:e.physical_exam||"",assessment:e.assessment||"",plan:e.plan||"",pa_sistolica:v("pa_sistolica"),pa_diastolica:v("pa_diastolica"),fc:v("fc"),fr:v("fr"),spo2:v("spo2"),temperatura:v("temperatura")};
}
function payload(f:Form){
  const vital_signs:Record<string,number>={};
  for(const [k] of VITAIS){const n=Number(String(f[k]).replace(",","."));if(String(f[k]).trim()&&Number.isFinite(n))vital_signs[k]=n;}
  return {encounter_type:f.encounter_type,chief_complaint:f.chief_complaint||null,anamnesis:f.anamnesis||null,physical_exam:f.physical_exam||null,assessment:f.assessment||null,plan:f.plan||null,vital_signs};
}

export default function Prontuario(){
  const [qs,setQs]=useSearchParams();
  const [pacientes,setPacientes]=useState<Paciente[]>([]),[encounters,setEncounters]=useState<Encounter[]>([]),[fila,setFila]=useState<Fila[]>([]);
  const [artefatos,setArtefatos]=useState<Artefato[]>([]),[candidatos,setCandidatos]=useState<Artefato[]>([]);
  const [busca,setBusca]=useState(""),[novoNome,setNovoNome]=useState(""),[erro,setErro]=useState("");
  const [editor,setEditor]=useState(false),[editando,setEditando]=useState<number|null>(null),[form,setForm]=useState<Form>(VAZIO),[salvando,setSalvando]=useState(false);
  const pid=Number(qs.get("paciente")||0)||null;
  const paciente=pacientes.find(p=>p.id===pid)||null;

  const carregarFila=()=>api.get<Fila[]>("/agenda-clinica/hoje").then(setFila).catch(e=>setErro(e.message));
  const carregarArtefatos=()=>{if(!pid||!editando)return;const b=`/pacientes/${pid}/atendimentos/${editando}/artefatos`;Promise.all([api.get<Artefato[]>(b),api.get<Artefato[]>(`${b}/candidatos`)]).then(([a,c])=>{setArtefatos(a);setCandidatos(c);}).catch(e=>setErro(e.message));};
  useEffect(()=>{api.get<Paciente[]>("/pacientes").then(lista=>{setPacientes(lista);if(!pid&&lista[0])setQs({paciente:String(lista[0].id)},{replace:true});}).catch(e=>setErro(e.message));carregarFila();},[]); // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(()=>{if(!pid){setEncounters([]);return;}api.get<Encounter[]>(`/pacientes/${pid}/atendimentos`).then(setEncounters).catch(e=>setErro(e.message));},[pid]);
  useEffect(()=>{if(!editando){setArtefatos([]);setCandidatos([]);return;}carregarArtefatos();const f=()=>carregarArtefatos();window.addEventListener("focus",f);return()=>window.removeEventListener("focus",f);},[pid,editando]); // eslint-disable-line react-hooks/exhaustive-deps

  const filtrados=useMemo(()=>{const q=busca.trim().toLocaleLowerCase("pt-BR");return q?pacientes.filter(p=>p.full_name.toLocaleLowerCase("pt-BR").includes(q)):pacientes;},[busca,pacientes]);
  const selecionar=(id:number)=>{setQs({paciente:String(id)});setEditor(false);setEditando(null);setForm(VAZIO);};

  async function criarPaciente(){
    const nome=novoNome.trim(); if(!nome)return;
    try{const p=await api.post<Paciente>("/pacientes",{full_name:nome});setPacientes(x=>[p,...x]);setNovoNome("");selecionar(p.id);}catch(e){setErro(e instanceof Error?e.message:"Falha ao cadastrar paciente.");}
  }
  function abrirNovo(){setEditando(null);setForm(VAZIO);setEditor(true);}
  function abrir(e:Encounter){if(e.status==="finalized")return;setEditando(e.id);setForm(doEncounter(e));setEditor(true);}
  async function salvar(){
    if(!pid)return null;setSalvando(true);setErro("");
    try{const p=payload(form);const e=editando?await api.patch<Encounter>(`/pacientes/${pid}/atendimentos/${editando}`,p):await api.post<Encounter>(`/pacientes/${pid}/atendimentos`,p);setEditando(e.id);setEncounters(x=>[e,...x.filter(i=>i.id!==e.id)]);return e;}catch(e){setErro(e instanceof Error?e.message:"Falha ao salvar atendimento.");return null;}finally{setSalvando(false);}
  }
  async function finalizar(){
    const salvo=await salvar();if(!pid||!salvo)return;setSalvando(true);
    try{
      const e=await api.post<Encounter>(`/pacientes/${pid}/atendimentos/${salvo.id}/finalizar`);setEncounters(x=>[e,...x.filter(i=>i.id!==e.id)]);setEditor(false);setEditando(null);setForm(VAZIO);
      if(e.appointment_id)try{await api.post(`/agenda-clinica/${e.appointment_id}/transicao`,{action:"complete"});await carregarFila();}catch{setErro("Atendimento finalizado; fila pendente de atualização.");}
    }catch(e){setErro(e instanceof Error?e.message:"Falha ao finalizar atendimento.");}finally{setSalvando(false);}
  }
  async function anexar(a:Artefato){if(!pid||!editando)return;try{await api.post(`/pacientes/${pid}/atendimentos/${editando}/artefatos`,{tipo:a.tipo,artifact_id:a.artifact_id});await carregarArtefatos();}catch(e){setErro(e instanceof Error?e.message:"Falha ao vincular artefato.");}}
  async function vincular(item:Fila,id:number){try{await api.post(`/agenda-clinica/${item.appointment_id}/vincular`,{patient_profile_id:id});await carregarFila();}catch(e){setErro(e instanceof Error?e.message:"Falha ao vincular paciente.");}}
  async function acaoFila(item:Fila,action:string){
    try{
      const r=await api.post<Fila>(`/agenda-clinica/${item.appointment_id}/transicao`,{action});
      if(action==="start"&&r.patient_profile_id&&r.encounter_id){const e=await api.get<Encounter>(`/pacientes/${r.patient_profile_id}/atendimentos/${r.encounter_id}`);setQs({paciente:String(r.patient_profile_id)});setEditando(e.id);setForm(doEncounter(e));setEditor(true);setEncounters(x=>[e,...x.filter(i=>i.id!==e.id)]);}else await carregarFila();
    }catch(e){setErro(e instanceof Error?e.message:"Falha ao atualizar sala de espera.");}
  }

  return <div className="pep">
    <header className="pep-head"><div><p className="eyebrow">Prontuário Eletrônico CorVIA</p><h1>Pacientes e atendimentos</h1></div><div className="pep-add"><input aria-label="Nome do novo paciente" placeholder="Nome do novo paciente" value={novoNome} onChange={e=>setNovoNome(e.target.value)} onKeyDown={e=>{if(e.key==="Enter")criarPaciente();}}/><button className="botao" onClick={criarPaciente}>+ Paciente</button></div></header>
    {erro&&<p className="pep-error" role="alert">{erro}</p>}
    {!!fila.length&&<section className="pep-card pep-history"><h2>Sala de espera</h2>{fila.map(item=><article key={item.appointment_id}><div><strong>{hora(item.scheduled_at)} · {item.patient_name}</strong><time>{ESTADOS[item.state]||item.state}</time></div><p>Chegada {item.arrived_at?hora(item.arrived_at):"—"} · espera {espera(item.arrived_at)}</p><div className="pep-actions">{!item.patient_profile_id?<select aria-label={`Vincular ${item.patient_name}`} defaultValue="" onChange={e=>{const id=Number(e.target.value);if(id)vincular(item,id);}}><option value="" disabled>Vincular prontuário…</option>{pacientes.map(p=><option key={p.id} value={p.id}>{p.full_name}</option>)}</select>:item.state==="scheduled"?<button onClick={()=>acaoFila(item,"arrive")}>Chegou</button>:item.state==="arrived"?<button onClick={()=>acaoFila(item,"call")}>Chamar</button>:item.state!=="completed"?<button onClick={()=>acaoFila(item,"start")}>{item.state==="in_service"?"Abrir atendimento":"Atender"}</button>:null}</div></article>)}</section>}
    <div className="pep-grid">
      <aside className="pep-list"><input aria-label="Buscar paciente" placeholder="Buscar paciente" value={busca} onChange={e=>setBusca(e.target.value)}/><div>{filtrados.map(p=><button key={p.id} className={p.id===pid?"is-active":""} onClick={()=>selecionar(p.id)}><span>{p.full_name[0]?.toUpperCase()}</span><strong>{p.full_name}</strong></button>)}{!filtrados.length&&<small>Nenhum paciente.</small>}</div></aside>
      <main className="pep-main">
        {!paciente?<section className="pep-card pep-empty">Selecione ou cadastre um paciente.</section>:<>
          <section className="pep-card pep-patient"><div><p className="eyebrow">Paciente</p><h2>{paciente.full_name}</h2><small>{[paciente.birth_date,paciente.sex,paciente.phone].filter(Boolean).join(" · ")||"Dados complementares não informados"}</small></div><button className="botao" onClick={abrirNovo}>+ Iniciar atendimento</button></section>
          <div className="pep-clinical">
            <section className="pep-card pep-history"><div className="pep-title"><h2>Histórico</h2><small>{encounters.length} atendimento(s)</small></div>{!encounters.length&&<p className="pep-muted">Ainda não há atendimentos.</p>}{encounters.map(e=><article key={e.id}><div><strong>{e.encounter_type==="adendo"?"Adendo":"Atendimento"}</strong><time>{quando(e.started_at)}</time></div><p>{e.chief_complaint||e.assessment||"Sem resumo registrado."}</p>{e.status==="finalized"?<small>Finalizado · histórico preservado</small>:<button onClick={()=>abrir(e)}>Continuar</button>}</article>)}</section>
            <section className="pep-card pep-editor">
              {!editor?<div className="pep-empty"><strong>Novo atendimento</strong><p>Registre a evolução e finalize quando concluída.</p><button className="botao" onClick={abrirNovo}>Iniciar</button></div>:<>
                <div className="pep-title"><div><p className="eyebrow">{editando?"Em andamento":"Novo atendimento"}</p><h2>Evolução clínica</h2></div><button onClick={()=>setEditor(false)}>Fechar</button></div>
                <label>Tipo<select value={form.encounter_type} onChange={e=>setForm({...form,encounter_type:e.target.value})}><option value="consulta">Consulta</option><option value="retorno">Retorno</option><option value="pre_operatorio">Pré-operatório</option><option value="teleconsulta">Teleconsulta</option><option value="outro">Outro</option></select></label>
                <div className="pep-vitals">{VITAIS.map(([k,l])=><label key={k}>{l}<input value={String(form[k])} inputMode="decimal" onChange={e=>setForm({...form,[k]:e.target.value})}/></label>)}</div>
                {TEXTOS.map(([k,l,r])=><label key={k}>{l}{r===2?<input value={String(form[k])} onChange={e=>setForm({...form,[k]:e.target.value})}/>:<textarea rows={r} value={String(form[k])} onChange={e=>setForm({...form,[k]:e.target.value})}/>}</label>)}
                {editando&&<div><p className="eyebrow">Prescrições e documentos</p><div className="pep-actions"><a className="botao botao--secundario" href={`/receituario?paciente=${pid}&atendimento=${editando}`} target="_blank" rel="noreferrer">Abrir Receituário</a><a className="botao botao--secundario" href={`/documentos?paciente=${pid}&atendimento=${editando}`} target="_blank" rel="noreferrer">Abrir Documentos</a></div>{artefatos.map(a=><p className="pep-muted" key={`${a.tipo}-${a.artifact_id}`}>✓ {a.titulo} · {quando(a.created_at)}</p>)}{!!candidatos.length&&<div><small>Recentes do mesmo paciente:</small>{candidatos.slice(0,6).map(a=><button key={`${a.tipo}-${a.artifact_id}`} onClick={()=>anexar(a)}>+ Vincular {a.titulo} · {quando(a.created_at)}</button>)}</div>}</div>}
                <div className="pep-actions"><button className="botao botao--secundario" disabled={salvando} onClick={salvar}>Salvar rascunho</button><button className="botao" disabled={salvando} onClick={finalizar}>Finalizar</button></div>
              </>}
            </section>
          </div>
        </>}
      </main>
    </div>
  </div>;
}