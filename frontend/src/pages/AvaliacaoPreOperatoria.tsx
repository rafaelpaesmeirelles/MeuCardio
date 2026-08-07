import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, ApiError } from "../lib/api";
import { useAuth } from "../lib/auth";
import AssinaturaExternaITI from "../components/AssinaturaExternaITI";
import CalculadorasPreOperatoriasAvancadas, { type AvancadosState } from "../components/CalculadorasPreOperatoriasAvancadas";

/** Avaliação Cardiológica Pré-Operatória de Risco Cirúrgico.
 * Fonte: ChatGPT nas extensões DASI/AUB-HAS2/VSG-CRI/GSCRI/SORT/S-MPM.
 */
const METODOS_MANUAL_EXTERNO = new Set(["GOVBR", "VIDAAS", "BIRDID", "SAFEID", "NEOID", "REMOTEID"]);
type Provedor = { codigo: string; nome: string; nivel: string; familia: string; disponivel: boolean; motivo: string | null };

type RcriEntrada = { cirurgia_alto_risco: boolean; cardiopatia_isquemica: boolean; insuficiencia_cardiaca_congestiva: boolean; doenca_cerebrovascular: boolean; diabetes_em_uso_de_insulina: boolean; creatinina_maior_2: boolean };
const RCRI_INICIAL: RcriEntrada = { cirurgia_alto_risco: false, cardiopatia_isquemica: false, insuficiencia_cardiaca_congestiva: false, doenca_cerebrovascular: false, diabetes_em_uso_de_insulina: false, creatinina_maior_2: false };
const RCRI_LABELS: Record<keyof RcriEntrada, string> = {
  cirurgia_alto_risco: "Cirurgia de alto risco (intraperitoneal, intratorácica ou vascular suprainguinal)",
  cardiopatia_isquemica: "Cardiopatia isquêmica (IAM prévio, angina, nitrato, teste positivo ou onda Q)",
  insuficiencia_cardiaca_congestiva: "Insuficiência cardíaca congestiva",
  doenca_cerebrovascular: "Doença cerebrovascular (AVC ou AIT prévio)",
  diabetes_em_uso_de_insulina: "Diabetes em uso de insulina",
  creatinina_maior_2: "Creatinina sérica pré-operatória >2,0 mg/dL",
};

type GuptaEntrada = { idade: string; status_funcional: string; asa: string; creatinina_maior_1_5: boolean; tipo_procedimento: string };
const GUPTA_PROCEDIMENTOS: [string, string][] = [
  ["hernia", "Hérnia"], ["anorretal", "Anorretal"], ["aortica", "Aórtica"], ["bariatrica", "Bariátrica"], ["encefalica", "Encefálica"], ["mama", "Mama"], ["cardiaca", "Cardíaca"], ["orl", "Otorrinolaringológica"], ["foregut_hpb", "GI alto/hepatopancreatobiliar"], ["vesicula_apendice_adrenal_baco", "Vesícula/apêndice/adrenal/baço"], ["intestinal", "Intestinal"], ["pescoco", "Pescoço"], ["obstetrica_ginecologica", "Obstétrica/ginecológica"], ["ortopedica", "Ortopédica"], ["abdome_outro", "Abdominal, outra"], ["vascular_periferica", "Vascular periférica"], ["pele", "Pele/tecido subcutâneo"], ["coluna", "Coluna"], ["toracica", "Torácica não cardíaca"], ["veias", "Veias"], ["urologia", "Urológica"],
];

type DasiEntrada = { autocuidado: boolean; caminhar_casa: boolean; caminhar_quarteiroes: boolean; escada_ladeira: boolean; correr_curto: boolean; trabalho_domestico_leve: boolean; trabalho_domestico_moderado: boolean; trabalho_domestico_pesado: boolean; quintal_jardim: boolean; relacoes_sexuais: boolean; recreacao_moderada: boolean; esporte_extenuante: boolean };
const DASI_INICIAL: DasiEntrada = { autocuidado: false, caminhar_casa: false, caminhar_quarteiroes: false, escada_ladeira: false, correr_curto: false, trabalho_domestico_leve: false, trabalho_domestico_moderado: false, trabalho_domestico_pesado: false, quintal_jardim: false, relacoes_sexuais: false, recreacao_moderada: false, esporte_extenuante: false };
const DASI_LABELS: Record<keyof DasiEntrada, string> = {
  autocuidado: "Autocuidado (+2,75)", caminhar_casa: "Caminha dentro de casa (+1,75)", caminhar_quarteiroes: "Caminha 1–2 quarteirões (+2,75)", escada_ladeira: "Sobe um lance de escadas/ladeira (+5,5)", correr_curto: "Corre curta distância (+8,0)", trabalho_domestico_leve: "Trabalho doméstico leve (+2,7)", trabalho_domestico_moderado: "Trabalho doméstico moderado (+3,5)", trabalho_domestico_pesado: "Trabalho doméstico pesado (+8,0)", quintal_jardim: "Quintal/jardim (+4,5)", relacoes_sexuais: "Relações sexuais (+5,25)", recreacao_moderada: "Recreação moderada (+6,0)", esporte_extenuante: "Esporte extenuante (+7,5)",
};

type AubEntrada = { historia_doenca_cardiaca: boolean; sintomas_cardiacos: boolean; idade_maior_igual_75: boolean; hemoglobina_menor_12: boolean; cirurgia_vascular: boolean; cirurgia_emergencia: boolean };
const AUB_INICIAL: AubEntrada = { historia_doenca_cardiaca: false, sintomas_cardiacos: false, idade_maior_igual_75: false, hemoglobina_menor_12: false, cirurgia_vascular: false, cirurgia_emergencia: false };
const AUB_LABELS: Record<Exclude<keyof AubEntrada, "idade_maior_igual_75">, string> = { historia_doenca_cardiaca: "História de doença cardíaca", sintomas_cardiacos: "Angina ou dispneia", hemoglobina_menor_12: "Hemoglobina <12 g/dL", cirurgia_vascular: "Cirurgia vascular", cirurgia_emergencia: "Cirurgia de emergência" };

type VsgEntrada = { idade: string; doenca_arterial_coronariana: boolean; insuficiencia_cardiaca: boolean; dpoc: boolean; creatinina_maior_1_8: boolean; tabagismo: boolean; diabetes_insulina: boolean; betabloqueador_cronico: boolean; revascularizacao_coronaria_previa: boolean };
const VSG_INICIAL: VsgEntrada = { idade: "", doenca_arterial_coronariana: false, insuficiencia_cardiaca: false, dpoc: false, creatinina_maior_1_8: false, tabagismo: false, diabetes_insulina: false, betabloqueador_cronico: false, revascularizacao_coronaria_previa: false };
const VSG_LABELS: Record<Exclude<keyof VsgEntrada, "idade">, string> = { doenca_arterial_coronariana: "Doença arterial coronariana (+2)", insuficiencia_cardiaca: "Insuficiência cardíaca (+2)", dpoc: "DPOC (+2)", creatinina_maior_1_8: "Creatinina >1,8 mg/dL (+2)", tabagismo: "Tabagismo (+1)", diabetes_insulina: "Diabetes em uso de insulina (+1)", betabloqueador_cronico: "Betabloqueador crônico (+1; variável prognóstica)", revascularizacao_coronaria_previa: "Revascularização coronária prévia (−1)" };

function baixarBlob(blob: Blob, nomeArquivo: string) { const url = URL.createObjectURL(blob); const a = document.createElement("a"); a.href = url; a.download = nomeArquivo; a.click(); URL.revokeObjectURL(url); }

export default function AvaliacaoPreOperatoria() {
  const { usuario } = useAuth();
  const [provedores, setProvedores] = useState<Provedor[] | null>(null);
  const [patientName, setPatientName] = useState(""); const [idade, setIdade] = useState(""); const [procedimento, setProcedimento] = useState(""); const [indicacao, setIndicacao] = useState(""); const [capacidadeFuncional, setCapacidadeFuncional] = useState(""); const [conduta, setConduta] = useState(""); const [endereco, setEndereco] = useState<"" | "residencial" | "profissional">("");

  const [usarRcri, setUsarRcri] = useState(true); const [rcri, setRcri] = useState<RcriEntrada>(RCRI_INICIAL); const [resultadoRcri, setResultadoRcri] = useState<{ pontos: number; classe: string; evento_pct: string } | null>(null); const [interpretacaoRcri, setInterpretacaoRcri] = useState("");
  const [usarGupta, setUsarGupta] = useState(true); const [gupta, setGupta] = useState<GuptaEntrada>({ idade: "", status_funcional: "independente", asa: "2", creatinina_maior_1_5: false, tipo_procedimento: "hernia" }); const [resultadoGupta, setResultadoGupta] = useState<{ risco_pct: number; procedimento: string } | null>(null); const [interpretacaoGupta, setInterpretacaoGupta] = useState("");
  const [usarDasi, setUsarDasi] = useState(true); const [dasi, setDasi] = useState<DasiEntrada>(DASI_INICIAL); const [resultadoDasi, setResultadoDasi] = useState<{ score: number; max: number; capacidade_funcional: string; ponto_decisao: number } | null>(null); const [interpretacaoDasi, setInterpretacaoDasi] = useState("");
  const [usarAub, setUsarAub] = useState(false); const [aub, setAub] = useState<AubEntrada>(AUB_INICIAL); const [resultadoAub, setResultadoAub] = useState<{ score: number; max: number; categoria: string } | null>(null); const [interpretacaoAub, setInterpretacaoAub] = useState("");
  const [usarVsg, setUsarVsg] = useState(false); const [vsg, setVsg] = useState<VsgEntrada>(VSG_INICIAL); const [resultadoVsg, setResultadoVsg] = useState<{ score: number; categoria: string; evento_original_pct: number } | null>(null); const [interpretacaoVsg, setInterpretacaoVsg] = useState("");
  const [avancados, setAvancados] = useState<AvancadosState>({});

  const [erroCalculo, setErroCalculo] = useState(""); const [calculando, setCalculando] = useState(false); const [gerando, setGerando] = useState(false); const [erroGeracao, setErroGeracao] = useState(""); const [geradoId, setGeradoId] = useState<number | null>(null); const [metodo, setMetodo] = useState(usuario?.assinatura_metodo_preferido ?? "MANUAL"); const [aguardandoExterno, setAguardandoExterno] = useState(false); const [assinadoExternoAgora, setAssinadoExternoAgora] = useState(false); const [email, setEmail] = useState(""); const [enviando, setEnviando] = useState(false); const [resultadoEnvio, setResultadoEnvio] = useState<{ enviado: boolean; link: string | null } | null>(null);

  useEffect(() => { api.get<Provedor[]>("/assinatura/provedores").then(setProvedores).catch(() => {}); }, []);
  function aubPayload(): AubEntrada { return { ...aub, idade_maior_igual_75: idade ? Number(idade) >= 75 : aub.idade_maior_igual_75 }; }
  function vsgPayload(): Omit<VsgEntrada, "idade"> & { idade: number } { const x = vsg.idade || idade; if (!x) throw new ApiError(422, "Informe a idade para calcular o VSG-CRI."); return { ...vsg, idade: Number(x) }; }

  async function calcularEscores() {
    setCalculando(true); setErroCalculo("");
    try {
      if (usarRcri) { const x = await api.post<{ result: NonNullable<typeof resultadoRcri>; interpretation: string }>("/calculators/rcri/run", rcri); setResultadoRcri(x.result); setInterpretacaoRcri(x.interpretation); } else setResultadoRcri(null);
      if (usarGupta) { const idadeGupta = gupta.idade || idade; if (!idadeGupta) throw new ApiError(422, "Informe a idade para calcular o Gupta MICA."); const payload = { ...gupta, idade: Number(idadeGupta), asa: Number(gupta.asa) }; const x = await api.post<{ result: NonNullable<typeof resultadoGupta>; interpretation: string }>("/calculators/gupta-mica/run", payload); setResultadoGupta(x.result); setInterpretacaoGupta(x.interpretation); } else setResultadoGupta(null);
      if (usarDasi) { const x = await api.post<{ result: NonNullable<typeof resultadoDasi>; interpretation: string }>("/calculators/dasi/run", dasi); setResultadoDasi(x.result); setInterpretacaoDasi(x.interpretation); } else setResultadoDasi(null);
      if (usarAub) { const x = await api.post<{ result: NonNullable<typeof resultadoAub>; interpretation: string }>("/calculators/aub-has2/run", aubPayload()); setResultadoAub(x.result); setInterpretacaoAub(x.interpretation); } else setResultadoAub(null);
      if (usarVsg) { const x = await api.post<{ result: NonNullable<typeof resultadoVsg>; interpretation: string }>("/calculators/vsg-cri/run", vsgPayload()); setResultadoVsg(x.result); setInterpretacaoVsg(x.interpretation); } else setResultadoVsg(null);
    } catch (e) { setErroCalculo(e instanceof ApiError ? e.message : "Não foi possível calcular os métodos selecionados."); } finally { setCalculando(false); }
  }

  const avancadoComResultado = Object.values(avancados).some((m) => m.selecionado && m.result);
  const temResultado = Boolean(resultadoRcri || resultadoGupta || resultadoDasi || resultadoAub || resultadoVsg || avancadoComResultado);
  const algumMetodoSelecionado = usarRcri || usarGupta || usarDasi || usarAub || usarVsg;
  const podeGerar = procedimento.trim().length > 0 && temResultado;

  async function gerarDocumento() {
    if (!podeGerar) return; setGerando(true); setErroGeracao("");
    try {
      const idadeGupta = gupta.idade || idade;
      const metodoAv = (slug: string) => avancados[slug]?.selecionado && avancados[slug]?.result ? avancados[slug].payload : null;
      const x = await api.post<{ id: number }>("/avaliacao-preoperatoria/gerar", {
        patient_name: patientName.trim() || null, idade: idade ? Number(idade) : null, procedimento_planejado: procedimento.trim(), indicacao_cirurgica: indicacao.trim() || null, capacidade_funcional: capacidadeFuncional.trim() || null, conduta_recomendada: conduta.trim() || null, endereco: endereco || null,
        rcri: usarRcri && resultadoRcri ? rcri : null,
        gupta: usarGupta && resultadoGupta ? { ...gupta, idade: Number(idadeGupta), asa: Number(gupta.asa) } : null,
        dasi: usarDasi && resultadoDasi ? dasi : null, aub_has2: usarAub && resultadoAub ? aubPayload() : null, vsg_cri: usarVsg && resultadoVsg ? vsgPayload() : null,
        gscri: metodoAv("gscri"), sort: metodoAv("sort"), s_mpm: metodoAv("s-mpm"),
      }); setGeradoId(x.id);
    } catch (e) { setErroGeracao(e instanceof ApiError ? e.message : "Não foi possível gerar o documento."); } finally { setGerando(false); }
  }
  async function baixar() { if (!geradoId) return; try { const blob = await api.blob(`/document-templates/gerados/${geradoId}/pdf?metodo=${encodeURIComponent(metodo)}`); baixarBlob(blob, `avaliacao-preoperatoria-${geradoId}.pdf`); setAguardandoExterno(METODOS_MANUAL_EXTERNO.has(metodo)); } catch (e) { setErroGeracao(e instanceof ApiError ? e.message : "Não foi possível baixar o PDF."); } }
  async function enviarPorEmail() { if (!geradoId || !email) return; setEnviando(true); setErroGeracao(""); try { const x = await api.post<{ enviado: boolean; link: string | null }>(`/document-templates/gerados/${geradoId}/enviar-email`, { email }); setResultadoEnvio(x); } catch (e) { setErroGeracao(e instanceof ApiError ? e.message : "Não foi possível enviar o e-mail."); } finally { setEnviando(false); } }

  return <div style={{ maxWidth: 860 }}>
    <p className="eyebrow">Pacientes e prática</p><h1>Avaliação Cardiológica Pré-Operatória de Risco Cirúrgico</h1>
    <p style={{ color: "var(--texto-secundario)", maxWidth: "76ch" }}>Integra risco cardiovascular, capacidade funcional e mortalidade cirúrgica global sem misturar endpoints. Árvores e referências: <Link to={`/biblioteca?tema=${encodeURIComponent("Perioperatório")}`}>Biblioteca — Perioperatório</Link>.</p>

    <div className="cartao" style={{ marginTop: "1rem" }}><p className="eyebrow" style={{ marginTop: 0 }}>Dados do paciente e do procedimento</p><label>Nome do paciente</label><input value={patientName} onChange={(e) => setPatientName(e.target.value)} />
      <div className="grade grade--2" style={{ marginTop: "0.6rem" }}><div><label>Idade</label><input type="number" min={0} max={120} value={idade} onChange={(e) => setIdade(e.target.value)} /></div><div><label>Capacidade funcional — descrição clínica</label><input value={capacidadeFuncional} onChange={(e) => setCapacidadeFuncional(e.target.value)} placeholder="O DASI fornece avaliação estruturada" /></div></div>
      <label style={{ marginTop: "0.6rem" }}>Procedimento planejado</label><input value={procedimento} onChange={(e) => setProcedimento(e.target.value)} /><label style={{ marginTop: "0.6rem" }}>Indicação cirúrgica</label><input value={indicacao} onChange={(e) => setIndicacao(e.target.value)} />
    </div>

    <div className="cartao" style={{ marginTop: "1rem" }}><label style={{ display: "flex", gap: 8, fontWeight: 700 }}><input type="checkbox" checked={usarRcri} onChange={(e) => setUsarRcri(e.target.checked)} />RCRI — Índice de Risco Cardíaco Revisado</label>{usarRcri && <div style={{ marginTop: "0.5rem" }}>{(Object.keys(RCRI_LABELS) as (keyof RcriEntrada)[]).map((k) => <label key={k} style={{ display: "flex", gap: 8, fontWeight: 400, marginBottom: "0.35rem" }}><input type="checkbox" checked={rcri[k]} onChange={(e) => setRcri({ ...rcri, [k]: e.target.checked })} /><span>{RCRI_LABELS[k]}</span></label>)}</div>}</div>

    <div className="cartao" style={{ marginTop: "1rem" }}><label style={{ display: "flex", gap: 8, fontWeight: 700 }}><input type="checkbox" checked={usarGupta} onChange={(e) => setUsarGupta(e.target.checked)} />Gupta MICA — IAM/parada cardíaca</label>{usarGupta && <div className="grade grade--2" style={{ marginTop: "0.5rem" }}><div><label>Idade</label><input type="number" value={gupta.idade} placeholder={idade} onChange={(e) => setGupta({ ...gupta, idade: e.target.value })} /></div><div><label>Status funcional</label><select value={gupta.status_funcional} onChange={(e) => setGupta({ ...gupta, status_funcional: e.target.value })}><option value="independente">Independente</option><option value="parcialmente_dependente">Parcialmente dependente</option><option value="totalmente_dependente">Totalmente dependente</option></select></div><div><label>ASA</label><select value={gupta.asa} onChange={(e) => setGupta({ ...gupta, asa: e.target.value })}>{[1,2,3,4,5].map((n) => <option key={n} value={n}>ASA {n}</option>)}</select></div><div><label>Procedimento</label><select value={gupta.tipo_procedimento} onChange={(e) => setGupta({ ...gupta, tipo_procedimento: e.target.value })}>{GUPTA_PROCEDIMENTOS.map(([v,l]) => <option key={v} value={v}>{l}</option>)}</select></div><label style={{ display: "flex", gap: 8, fontWeight: 400 }}><input type="checkbox" checked={gupta.creatinina_maior_1_5} onChange={(e) => setGupta({ ...gupta, creatinina_maior_1_5: e.target.checked })} />Creatinina &gt;1,5 mg/dL</label></div>}</div>

    <div className="cartao" style={{ marginTop: "1rem" }}><label style={{ display: "flex", gap: 8, fontWeight: 700 }}><input type="checkbox" checked={usarDasi} onChange={(e) => setUsarDasi(e.target.checked)} />DASI — capacidade funcional</label>{usarDasi && <>{(Object.keys(DASI_LABELS) as (keyof DasiEntrada)[]).map((k) => <label key={k} style={{ display: "flex", gap: 8, fontWeight: 400, marginBottom: "0.3rem" }}><input type="checkbox" checked={dasi[k]} onChange={(e) => setDasi({ ...dasi, [k]: e.target.checked })} /><span>{DASI_LABELS[k]}</span></label>)}</>}</div>

    <div className="cartao" style={{ marginTop: "1rem" }}><label style={{ display: "flex", gap: 8, fontWeight: 700 }}><input type="checkbox" checked={usarAub} onChange={(e) => setUsarAub(e.target.checked)} />AUB-HAS2</label>{usarAub && <div><label style={{ display: "flex", gap: 8, fontWeight: 400 }}><input type="checkbox" checked={idade ? Number(idade) >= 75 : aub.idade_maior_igual_75} disabled={Boolean(idade)} onChange={(e) => setAub({ ...aub, idade_maior_igual_75: e.target.checked })} />Idade ≥75</label>{(Object.keys(AUB_LABELS) as (keyof typeof AUB_LABELS)[]).map((k) => <label key={k} style={{ display: "flex", gap: 8, fontWeight: 400 }}><input type="checkbox" checked={aub[k]} onChange={(e) => setAub({ ...aub, [k]: e.target.checked })} />{AUB_LABELS[k]}</label>)}</div>}</div>

    <div className="cartao" style={{ marginTop: "1rem" }}><label style={{ display: "flex", gap: 8, fontWeight: 700 }}><input type="checkbox" checked={usarVsg} onChange={(e) => setUsarVsg(e.target.checked)} />VSG-CRI — cirurgia vascular arterial</label>{usarVsg && <><div><label>Idade</label><input type="number" value={vsg.idade} placeholder={idade} onChange={(e) => setVsg({ ...vsg, idade: e.target.value })} /></div>{(Object.keys(VSG_LABELS) as (keyof typeof VSG_LABELS)[]).map((k) => <label key={k} style={{ display: "flex", gap: 8, fontWeight: 400 }}><input type="checkbox" checked={vsg[k]} onChange={(e) => setVsg({ ...vsg, [k]: e.target.checked })} />{VSG_LABELS[k]}</label>)}</>}</div>

    <div style={{ marginTop: "1rem" }}><p className="eyebrow">Métodos avançados / populações específicas</p><CalculadorasPreOperatoriasAvancadas idade={idade} onChange={setAvancados} /></div>
    <div className="cartao" style={{ marginTop: "1rem", borderLeft: "3px solid var(--acento)" }}><strong>ACS-NSQIP oficial</strong><p style={{ marginBottom: 0 }}>Modelo externo dinâmico; usar a versão oficial vigente e registrar versão/data/CPT. Não congelar coeficientes locais.</p></div>

    {erroCalculo && <p role="alert" style={{ color: "var(--alerta)" }}>{erroCalculo}</p>}
    <button className="botao" style={{ marginTop: "0.8rem" }} onClick={calcularEscores} disabled={calculando || !algumMetodoSelecionado}>{calculando ? "Calculando…" : "Calcular RCRI/Gupta/DASI/AUB/VSG"}</button>

    {temResultado && <div className="cartao" style={{ marginTop: "0.8rem", borderLeft: "3px solid var(--acento)" }}><p className="eyebrow" style={{ marginTop: 0 }}>Resultado integrado</p>
      {resultadoRcri && <p><strong>RCRI:</strong> {resultadoRcri.pontos} — Classe {resultadoRcri.classe}. {interpretacaoRcri}</p>}{resultadoGupta && <p><strong>Gupta MICA:</strong> {resultadoGupta.risco_pct}%. {interpretacaoGupta}</p>}{resultadoDasi && <p><strong>DASI:</strong> {resultadoDasi.score}/58,2. {interpretacaoDasi}</p>}{resultadoAub && <p><strong>AUB-HAS2:</strong> {resultadoAub.score}/6 — {resultadoAub.categoria}. {interpretacaoAub}</p>}{resultadoVsg && <p><strong>VSG-CRI:</strong> {resultadoVsg.score} — {resultadoVsg.categoria}. {interpretacaoVsg}</p>}
      {Object.entries(avancados).filter(([,m]) => m.selecionado && m.result).map(([slug,m]) => <p key={slug}><strong>{slug.toUpperCase()}:</strong> {m.interpretation}</p>)}
      <p style={{ color: "var(--texto-secundario)", fontSize: "0.86rem" }}>Não somar/promediar métodos: endpoints diferentes. Use as árvores da Biblioteca para a próxima etapa.</p>
    </div>}

    {temResultado && <div className="cartao" style={{ marginTop: "1rem" }}><p className="eyebrow" style={{ marginTop: 0 }}>Documento</p><label>Conduta e recomendações</label><textarea rows={4} value={conduta} onChange={(e) => setConduta(e.target.value)} /><label>Endereço</label><select value={endereco} onChange={(e) => setEndereco(e.target.value as typeof endereco)}><option value="">Nenhum</option><option value="profissional">Profissional</option><option value="residencial">Residencial</option></select>
      {!geradoId ? <><button className="botao" style={{ marginTop: "0.8rem" }} onClick={gerarDocumento} disabled={gerando || !podeGerar}>{gerando ? "Gerando…" : "Gerar documento"}</button></> : <><p style={{ color: "var(--sucesso)" }}>Documento gerado.</p><label>Método de assinatura</label><select value={metodo} onChange={(e) => setMetodo(e.target.value)}>{(provedores ?? []).map((p) => <option key={p.codigo} value={p.codigo} disabled={!p.disponivel}>{p.nome}{!p.disponivel ? " — indisponível" : ""}</option>)}</select><button className="botao" onClick={baixar}>Baixar PDF</button>
      {aguardandoExterno && <AssinaturaExternaITI metodo={metodo} nomeProvedor={provedores?.find((p) => p.codigo === metodo)?.nome ?? metodo} enviarUrl={`/document-templates/gerados/${geradoId}/assinatura-externa`} onConcluido={() => { setAguardandoExterno(false); setAssinadoExternoAgora(true); }} />}{assinadoExternoAgora && <p style={{ color: "var(--sucesso)" }}>Assinatura conferida.</p>}
      <label>Enviar por e-mail</label><input type="email" value={email} onChange={(e) => setEmail(e.target.value)} /><button className="botao" onClick={enviarPorEmail} disabled={enviando || !email}>{enviando ? "Enviando…" : "Enviar por e-mail"}</button>{resultadoEnvio && <p>{resultadoEnvio.enviado ? "E-mail enviado." : <>Envio automático indisponível. Link: <code>{resultadoEnvio.link}</code></>}</p>}</>}
      {erroGeracao && <p role="alert" style={{ color: "var(--alerta)" }}>{erroGeracao}</p>}
    </div>}
  </div>;
}