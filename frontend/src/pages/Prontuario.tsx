import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api, ApiError } from "../lib/api";
import "../styles/prontuario.css";

type Endereco = {
  logradouro?: string | null; numero?: string | null; complemento?: string | null;
  bairro?: string | null; cidade?: string | null; uf?: string | null; cep?: string | null;
};

type Paciente = {
  id: number;
  full_name: string;
  cpf: string | null;
  birth_date: string | null;
  sex: string | null;
  phone: string | null;
  email: string | null;
  endereco: Endereco;
  created_at: string;
  updated_at: string;
};

type Encounter = {
  id: number;
  patient_profile_id: number;
  appointment_id: number | null;
  author_id: number;
  encounter_type: string;
  status: string;
  started_at: string;
  ended_at: string | null;
  finalized_at: string | null;
  amendment_of_id: number | null;
  amendment_reason: string | null;
  chief_complaint: string | null;
  anamnesis: string | null;
  physical_exam: string | null;
  assessment: string | null;
  plan: string | null;
  vital_signs: Record<string, number | string>;
  created_at: string;
  updated_at: string;
};

type EncounterForm = {
  encounter_type: string;
  chief_complaint: string;
  anamnesis: string;
  physical_exam: string;
  assessment: string;
  plan: string;
  pa_sistolica: string;
  pa_diastolica: string;
  fc: string;
  fr: string;
  spo2: string;
  temperatura: string;
};

const FORM_VAZIO: EncounterForm = {
  encounter_type: "consulta",
  chief_complaint: "",
  anamnesis: "",
  physical_exam: "",
  assessment: "",
  plan: "",
  pa_sistolica: "",
  pa_diastolica: "",
  fc: "",
  fr: "",
  spo2: "",
  temperatura: "",
};

function idade(data: string | null) {
  if (!data) return null;
  const nascimento = new Date(`${data}T12:00:00`);
  const hoje = new Date();
  let anos = hoje.getFullYear() - nascimento.getFullYear();
  const aniversarioAindaNaoChegou = hoje.getMonth() < nascimento.getMonth()
    || (hoje.getMonth() === nascimento.getMonth() && hoje.getDate() < nascimento.getDate());
  if (aniversarioAindaNaoChegou) anos -= 1;
  return anos >= 0 ? anos : null;
}

function dataHora(valor: string | null | undefined) {
  if (!valor) return "—";
  return new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "short", timeStyle: "short",
  }).format(new Date(valor));
}

function formDoEncounter(item: Encounter): EncounterForm {
  const sinais = item.vital_signs ?? {};
  const valor = (chave: string) => sinais[chave] === undefined ? "" : String(sinais[chave]);
  return {
    encounter_type: item.encounter_type || "consulta",
    chief_complaint: item.chief_complaint ?? "",
    anamnesis: item.anamnesis ?? "",
    physical_exam: item.physical_exam ?? "",
    assessment: item.assessment ?? "",
    plan: item.plan ?? "",
    pa_sistolica: valor("pa_sistolica"),
    pa_diastolica: valor("pa_diastolica"),
    fc: valor("fc"),
    fr: valor("fr"),
    spo2: valor("spo2"),
    temperatura: valor("temperatura"),
  };
}

function payloadDoForm(form: EncounterForm) {
  const vital_signs: Record<string, number> = {};
  for (const chave of ["pa_sistolica", "pa_diastolica", "fc", "fr", "spo2", "temperatura"] as const) {
    const bruto = form[chave].trim().replace(",", ".");
    if (!bruto) continue;
    const numero = Number(bruto);
    if (Number.isFinite(numero)) vital_signs[chave] = numero;
  }
  return {
    encounter_type: form.encounter_type,
    chief_complaint: form.chief_complaint || null,
    anamnesis: form.anamnesis || null,
    physical_exam: form.physical_exam || null,
    assessment: form.assessment || null,
    plan: form.plan || null,
    vital_signs,
  };
}

export default function Prontuario() {
  const [params, setParams] = useSearchParams();
  const [pacientes, setPacientes] = useState<Paciente[]>([]);
  const [busca, setBusca] = useState("");
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");
  const [novoPacienteAberto, setNovoPacienteAberto] = useState(false);
  const [novoPaciente, setNovoPaciente] = useState({
    full_name: "", cpf: "", birth_date: "", sex: "", phone: "", email: "",
  });
  const [salvandoPaciente, setSalvandoPaciente] = useState(false);
  const [encounters, setEncounters] = useState<Encounter[]>([]);
  const [carregandoEncounters, setCarregandoEncounters] = useState(false);
  const [editorAberto, setEditorAberto] = useState(false);
  const [encounterEditando, setEncounterEditando] = useState<number | null>(null);
  const [form, setForm] = useState<EncounterForm>(FORM_VAZIO);
  const [salvando, setSalvando] = useState(false);

  const pacienteId = Number(params.get("paciente") || 0) || null;
  const paciente = pacientes.find((item) => item.id === pacienteId) ?? null;

  async function carregarPacientes() {
    setCarregando(true);
    setErro("");
    try {
      const lista = await api.get<Paciente[]>("/pacientes");
      setPacientes(lista);
      const atual = Number(params.get("paciente") || 0);
      if (!atual && lista.length) setParams({ paciente: String(lista[0].id) }, { replace: true });
    } catch (e) {
      setErro(e instanceof Error ? e.message : "Não foi possível abrir os pacientes.");
    } finally {
      setCarregando(false);
    }
  }

  useEffect(() => { carregarPacientes(); }, []); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (!pacienteId) { setEncounters([]); return; }
    setCarregandoEncounters(true);
    setErro("");
    api.get<Encounter[]>(`/pacientes/${pacienteId}/atendimentos`)
      .then(setEncounters)
      .catch((e) => setErro(e instanceof Error ? e.message : "Não foi possível abrir o prontuário."))
      .finally(() => setCarregandoEncounters(false));
  }, [pacienteId]);

  const pacientesFiltrados = useMemo(() => {
    const termo = busca.trim().toLocaleLowerCase("pt-BR");
    if (!termo) return pacientes;
    return pacientes.filter((item) => [item.full_name, item.cpf, item.phone]
      .filter(Boolean).some((valor) => String(valor).toLocaleLowerCase("pt-BR").includes(termo)));
  }, [busca, pacientes]);

  const encontroEditando = encounters.find((item) => item.id === encounterEditando) ?? null;

  function selecionarPaciente(id: number) {
    setParams({ paciente: String(id) });
    setEditorAberto(false);
    setEncounterEditando(null);
    setForm(FORM_VAZIO);
  }

  async function criarPaciente() {
    if (!novoPaciente.full_name.trim()) return;
    setSalvandoPaciente(true);
    setErro("");
    try {
      const criado = await api.post<Paciente>("/pacientes", {
        full_name: novoPaciente.full_name.trim(),
        cpf: novoPaciente.cpf.trim() || null,
        birth_date: novoPaciente.birth_date || null,
        sex: novoPaciente.sex || null,
        phone: novoPaciente.phone.trim() || null,
        email: novoPaciente.email.trim() || null,
        endereco: null,
      });
      setPacientes((lista) => [criado, ...lista]);
      setNovoPaciente({ full_name: "", cpf: "", birth_date: "", sex: "", phone: "", email: "" });
      setNovoPacienteAberto(false);
      selecionarPaciente(criado.id);
    } catch (e) {
      setErro(e instanceof Error ? e.message : "Não foi possível cadastrar o paciente.");
    } finally {
      setSalvandoPaciente(false);
    }
  }

  function novoAtendimento() {
    setEncounterEditando(null);
    setForm(FORM_VAZIO);
    setEditorAberto(true);
  }

  function editarAtendimento(item: Encounter) {
    if (["finalized", "amended", "cancelled"].includes(item.status)) return;
    setEncounterEditando(item.id);
    setForm(formDoEncounter(item));
    setEditorAberto(true);
  }

  async function salvarRascunho(): Promise<Encounter | null> {
    if (!pacienteId) return null;
    setSalvando(true);
    setErro("");
    try {
      const payload = payloadDoForm(form);
      const salvo = encounterEditando
        ? await api.patch<Encounter>(`/pacientes/${pacienteId}/atendimentos/${encounterEditando}`, payload)
        : await api.post<Encounter>(`/pacientes/${pacienteId}/atendimentos`, payload);
      setEncounterEditando(salvo.id);
      setEncounters((lista) => [salvo, ...lista.filter((item) => item.id !== salvo.id)]);
      return salvo;
    } catch (e) {
      setErro(e instanceof Error ? e.message : "Não foi possível salvar o atendimento.");
      return null;
    } finally {
      setSalvando(false);
    }
  }

  async function finalizar() {
    if (!pacienteId) return;
    const salvo = encounterEditando
      ? encounters.find((item) => item.id === encounterEditando) ?? await salvarRascunho()
      : await salvarRascunho();
    if (!salvo) return;
    setSalvando(true);
    setErro("");
    try {
      const finalizado = await api.post<Encounter>(
        `/pacientes/${pacienteId}/atendimentos/${salvo.id}/finalizar`, {},
      );
      setEncounters((lista) => [finalizado, ...lista.filter((item) => item.id !== finalizado.id)]);
      setEditorAberto(false);
      setEncounterEditando(null);
      setForm(FORM_VAZIO);
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível finalizar o atendimento.");
    } finally {
      setSalvando(false);
    }
  }

  return (
    <div className="corvia-prontuario">
      <header className="corvia-prontuario__topbar">
        <div>
          <p className="eyebrow">Prontuário Eletrônico CorVIA</p>
          <h1>Pacientes e atendimentos</h1>
          <p>Um paciente identificável, uma história longitudinal e atendimentos clínicos preservados.</p>
        </div>
        <button className="botao" type="button" onClick={() => setNovoPacienteAberto((v) => !v)}>
          + Novo paciente
        </button>
      </header>

      {erro && <div className="corvia-prontuario__alerta" role="alert">{erro}</div>}

      {novoPacienteAberto && (
        <section className="corvia-prontuario__novo-paciente" aria-label="Cadastrar novo paciente">
          <div className="corvia-prontuario__section-head">
            <div><p className="eyebrow">Cadastro</p><h2>Novo paciente</h2></div>
            <button type="button" className="corvia-prontuario__link" onClick={() => setNovoPacienteAberto(false)}>Fechar</button>
          </div>
          <div className="corvia-prontuario__form-grid">
            <label className="span-2">Nome completo<input value={novoPaciente.full_name} onChange={(e) => setNovoPaciente({ ...novoPaciente, full_name: e.target.value })} /></label>
            <label>CPF<input value={novoPaciente.cpf} onChange={(e) => setNovoPaciente({ ...novoPaciente, cpf: e.target.value })} /></label>
            <label>Data de nascimento<input type="date" value={novoPaciente.birth_date} onChange={(e) => setNovoPaciente({ ...novoPaciente, birth_date: e.target.value })} /></label>
            <label>Sexo<select value={novoPaciente.sex} onChange={(e) => setNovoPaciente({ ...novoPaciente, sex: e.target.value })}><option value="">Não informado</option><option value="M">Masculino</option><option value="F">Feminino</option></select></label>
            <label>Telefone<input value={novoPaciente.phone} onChange={(e) => setNovoPaciente({ ...novoPaciente, phone: e.target.value })} /></label>
            <label className="span-2">E-mail<input type="email" value={novoPaciente.email} onChange={(e) => setNovoPaciente({ ...novoPaciente, email: e.target.value })} /></label>
          </div>
          <div className="corvia-prontuario__actions">
            <button className="botao" type="button" disabled={salvandoPaciente || !novoPaciente.full_name.trim()} onClick={criarPaciente}>{salvandoPaciente ? "Salvando…" : "Cadastrar paciente"}</button>
          </div>
        </section>
      )}

      <div className="corvia-prontuario__layout">
        <aside className="corvia-prontuario__directory" aria-label="Pacientes cadastrados">
          <div className="corvia-prontuario__directory-head">
            <div><p className="eyebrow">Pacientes</p><strong>{pacientes.length}</strong></div>
            <input aria-label="Buscar paciente" placeholder="Buscar nome, CPF ou telefone" value={busca} onChange={(e) => setBusca(e.target.value)} />
          </div>
          <div className="corvia-prontuario__patient-list">
            {carregando && <p className="corvia-prontuario__muted">Carregando pacientes…</p>}
            {!carregando && pacientesFiltrados.length === 0 && <p className="corvia-prontuario__muted">Nenhum paciente encontrado.</p>}
            {pacientesFiltrados.map((item) => {
              const anos = idade(item.birth_date);
              return (
                <button key={item.id} type="button" className={`corvia-prontuario__patient${item.id === pacienteId ? " is-active" : ""}`} onClick={() => selecionarPaciente(item.id)}>
                  <span className="corvia-prontuario__avatar">{item.full_name.trim().slice(0, 1).toUpperCase()}</span>
                  <span><strong>{item.full_name}</strong><small>{anos !== null ? `${anos} anos` : "Idade não informada"}{item.phone ? ` · ${item.phone}` : ""}</small></span>
                </button>
              );
            })}
          </div>
        </aside>

        <main className="corvia-prontuario__workspace">
          {!paciente ? (
            <section className="corvia-prontuario__empty">
              <strong>Selecione um paciente</strong>
              <p>Abra um cadastro existente ou crie um novo paciente para iniciar o prontuário.</p>
            </section>
          ) : (
            <>
              <section className="corvia-prontuario__patient-header">
                <div className="corvia-prontuario__identity">
                  <span className="corvia-prontuario__avatar is-large">{paciente.full_name.trim().slice(0, 1).toUpperCase()}</span>
                  <div><p className="eyebrow">Paciente</p><h2>{paciente.full_name}</h2><p>{[idade(paciente.birth_date) !== null ? `${idade(paciente.birth_date)} anos` : null, paciente.sex === "M" ? "Masculino" : paciente.sex === "F" ? "Feminino" : null, paciente.phone].filter(Boolean).join(" · ") || "Dados demográficos incompletos"}</p></div>
                </div>
                <button className="botao" type="button" onClick={novoAtendimento}>+ Iniciar atendimento</button>
              </section>

              <section className="corvia-prontuario__summary-strip">
                <span><small>Atendimentos</small><strong>{encounters.length}</strong></span>
                <span><small>Último atendimento</small><strong>{encounters[0] ? dataHora(encounters[0].started_at) : "Nenhum"}</strong></span>
                <span><small>CPF</small><strong>{paciente.cpf || "Não informado"}</strong></span>
                <span><small>Contato</small><strong>{paciente.email || paciente.phone || "Não informado"}</strong></span>
              </section>

              <div className="corvia-prontuario__clinical-grid">
                <section className="corvia-prontuario__timeline">
                  <div className="corvia-prontuario__section-head"><div><p className="eyebrow">Histórico</p><h2>Atendimentos</h2></div></div>
                  {carregandoEncounters && <p className="corvia-prontuario__muted">Abrindo histórico…</p>}
                  {!carregandoEncounters && encounters.length === 0 && <div className="corvia-prontuario__timeline-empty"><strong>Sem atendimentos</strong><p>Inicie a primeira consulta para construir a linha do tempo clínica.</p></div>}
                  <div className="corvia-prontuario__encounters">
                    {encounters.map((item) => (
                      <article key={item.id} className={`corvia-prontuario__encounter ${item.status === "finalized" ? "is-finalized" : ""}`}>
                        <div className="corvia-prontuario__encounter-head">
                          <div><span className={`corvia-prontuario__status is-${item.status}`}>{item.status === "finalized" ? "Finalizado" : item.status === "in_progress" ? "Em atendimento" : item.status === "draft" ? "Rascunho" : item.status}</span><strong>{item.encounter_type === "adendo" ? "Adendo" : "Atendimento"}</strong></div>
                          <time>{dataHora(item.started_at)}</time>
                        </div>
                        <p>{item.chief_complaint || item.assessment || "Atendimento sem resumo registrado."}</p>
                        <div className="corvia-prontuario__encounter-actions">
                          {item.status === "finalized" ? <span>Histórico preservado</span> : <button type="button" onClick={() => editarAtendimento(item)}>Continuar atendimento</button>}
                        </div>
                      </article>
                    ))}
                  </div>
                </section>

                <section className={`corvia-prontuario__editor${editorAberto ? " is-open" : ""}`}>
                  {!editorAberto ? (
                    <div className="corvia-prontuario__editor-placeholder">
                      <span>+</span><strong>Novo atendimento</strong><p>Registre a evolução clínica como rascunho e finalize quando estiver concluída.</p><button className="botao" type="button" onClick={novoAtendimento}>Iniciar atendimento</button>
                    </div>
                  ) : (
                    <>
                      <div className="corvia-prontuario__section-head">
                        <div><p className="eyebrow">{encounterEditando ? "Atendimento em andamento" : "Novo atendimento"}</p><h2>{encontroEditando?.encounter_type === "adendo" ? "Adendo" : "Evolução clínica"}</h2></div>
                        <button type="button" className="corvia-prontuario__link" onClick={() => setEditorAberto(false)}>Fechar</button>
                      </div>

                      <div className="corvia-prontuario__form-grid">
                        <label>Tipo<select value={form.encounter_type} onChange={(e) => setForm({ ...form, encounter_type: e.target.value })}><option value="consulta">Consulta</option><option value="retorno">Retorno</option><option value="pre_operatorio">Pré-operatório</option><option value="teleconsulta">Teleconsulta</option><option value="outro">Outro</option></select></label>
                        <div className="corvia-prontuario__vitals span-2">
                          <label>PA sist.<input inputMode="numeric" value={form.pa_sistolica} onChange={(e) => setForm({ ...form, pa_sistolica: e.target.value })} /></label>
                          <label>PA diast.<input inputMode="numeric" value={form.pa_diastolica} onChange={(e) => setForm({ ...form, pa_diastolica: e.target.value })} /></label>
                          <label>FC<input inputMode="numeric" value={form.fc} onChange={(e) => setForm({ ...form, fc: e.target.value })} /></label>
                          <label>FR<input inputMode="numeric" value={form.fr} onChange={(e) => setForm({ ...form, fr: e.target.value })} /></label>
                          <label>SpO₂<input inputMode="numeric" value={form.spo2} onChange={(e) => setForm({ ...form, spo2: e.target.value })} /></label>
                          <label>Temp.<input inputMode="decimal" value={form.temperatura} onChange={(e) => setForm({ ...form, temperatura: e.target.value })} /></label>
                        </div>
                        <label className="span-2">Motivo / queixa principal<input value={form.chief_complaint} onChange={(e) => setForm({ ...form, chief_complaint: e.target.value })} /></label>
                        <label className="span-2">Anamnese<textarea rows={6} value={form.anamnesis} onChange={(e) => setForm({ ...form, anamnesis: e.target.value })} /></label>
                        <label className="span-2">Exame físico<textarea rows={4} value={form.physical_exam} onChange={(e) => setForm({ ...form, physical_exam: e.target.value })} /></label>
                        <label className="span-2">Avaliação<textarea rows={4} value={form.assessment} onChange={(e) => setForm({ ...form, assessment: e.target.value })} /></label>
                        <label className="span-2">Plano / conduta<textarea rows={5} value={form.plan} onChange={(e) => setForm({ ...form, plan: e.target.value })} /></label>
                      </div>
                      <div className="corvia-prontuario__actions is-sticky">
                        <button className="botao botao--secundario" type="button" disabled={salvando} onClick={() => salvarRascunho()}>{salvando ? "Salvando…" : "Salvar rascunho"}</button>
                        <button className="botao" type="button" disabled={salvando} onClick={finalizar}>Finalizar atendimento</button>
                      </div>
                    </>
                  )}
                </section>
              </div>
            </>
          )}
        </main>
      </div>
    </div>
  );
}
