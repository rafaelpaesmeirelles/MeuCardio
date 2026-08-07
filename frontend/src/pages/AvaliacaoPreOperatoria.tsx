import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, ApiError } from "../lib/api";
import { useAuth } from "../lib/auth";
import { Carregando } from "../components/Estado";
import AssinaturaExternaITI from "../components/AssinaturaExternaITI";

/**
 * Avaliação Cardiológica Pré-Operatória de Risco Cirúrgico — pedido do
 * Rafael, 07/08/2026.
 *
 * Reúne conteúdo científico (link para a Biblioteca filtrada em
 * Perioperatório) e as calculadoras de risco cirúrgico validadas (RCRI,
 * Gupta MICA — mesmo registro de `Calculadoras.tsx`, mas com formulário
 * dedicado aqui em vez de mandar o médico pra tela genérica) num único
 * fluxo: preencher dados do paciente → calcular os escores → gerar o
 * documento → assinar (mesmo catálogo de provedores da Receituário/
 * Documentos, inclusive gov.br via Assinador ITI) → baixar ou enviar por
 * e-mail ao paciente (CorvIA Mail).
 *
 * Não reimplementa PDF, assinatura nem e-mail: o documento gerado é um
 * `GeneratedDocument` como qualquer outro do Documentos, então as rotas
 * genéricas de `/document-templates/gerados/{id}/...` servem este aqui sem
 * nenhum código novo — mesma identidade visual Corvia + logo pessoal
 * opcional + endereço (perfil do médico em Minha Conta).
 */

const METODOS_MANUAL_EXTERNO = new Set(["GOVBR", "VIDAAS", "BIRDID", "SAFEID", "NEOID", "REMOTEID"]);

type Provedor = { codigo: string; nome: string; nivel: string; familia: string; disponivel: boolean; motivo: string | null };

type RcriEntrada = {
  cirurgia_alto_risco: boolean;
  cardiopatia_isquemica: boolean;
  insuficiencia_cardiaca_congestiva: boolean;
  doenca_cerebrovascular: boolean;
  diabetes_em_uso_de_insulina: boolean;
  creatinina_maior_2: boolean;
};
const RCRI_INICIAL: RcriEntrada = {
  cirurgia_alto_risco: false, cardiopatia_isquemica: false, insuficiencia_cardiaca_congestiva: false,
  doenca_cerebrovascular: false, diabetes_em_uso_de_insulina: false, creatinina_maior_2: false,
};
const RCRI_LABELS: Record<keyof RcriEntrada, string> = {
  cirurgia_alto_risco: "Cirurgia de alto risco (intraperitoneal, intratorácica ou vascular suprainguinal)",
  cardiopatia_isquemica: "Cardiopatia isquêmica (IAM prévio, angina, uso de nitrato, teste positivo ou onda Q)",
  insuficiencia_cardiaca_congestiva: "Insuficiência cardíaca congestiva",
  doenca_cerebrovascular: "Doença cerebrovascular (AVC ou AIT prévio)",
  diabetes_em_uso_de_insulina: "Diabetes em uso de insulina",
  creatinina_maior_2: "Creatinina sérica pré-operatória > 2,0 mg/dL",
};

type GuptaEntrada = {
  idade: string; status_funcional: string; asa: string;
  creatinina_maior_1_5: boolean; tipo_procedimento: string;
};
const GUPTA_PROCEDIMENTOS: [string, string][] = [
  ["hernia", "Hérnia"], ["anorretal", "Anorretal"], ["aortica", "Aórtica"], ["bariatrica", "Bariátrica"],
  ["encefalica", "Encefálica (neurocirurgia)"], ["mama", "Mama"], ["cardiaca", "Cardíaca"],
  ["orl", "Otorrinolaringológica"], ["foregut_hpb", "Trato gastrointestinal alto / hepatopancreatobiliar"],
  ["vesicula_apendice_adrenal_baco", "Vesícula biliar, apêndice, adrenal ou baço"], ["intestinal", "Intestinal"],
  ["pescoco", "Pescoço (tireoide/paratireoide)"], ["obstetrica_ginecologica", "Obstétrica ou ginecológica"],
  ["ortopedica", "Ortopédica não vertebral"], ["abdome_outro", "Abdominal, outra"],
  ["vascular_periferica", "Vascular periférica"], ["pele", "Pele/tecido subcutâneo"],
  ["coluna", "Coluna vertebral"], ["toracica", "Torácica não cardíaca"], ["veias", "Veias (varizes etc.)"],
  ["urologia", "Urológica"],
];

function baixarBlob(blob: Blob, nomeArquivo: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = nomeArquivo;
  a.click();
  URL.revokeObjectURL(url);
}

export default function AvaliacaoPreOperatoria() {
  const { usuario } = useAuth();
  const [provedores, setProvedores] = useState<Provedor[] | null>(null);

  // Dados do paciente/procedimento
  const [patientName, setPatientName] = useState("");
  const [idade, setIdade] = useState("");
  const [procedimento, setProcedimento] = useState("");
  const [indicacao, setIndicacao] = useState("");
  const [capacidadeFuncional, setCapacidadeFuncional] = useState("");
  const [conduta, setConduta] = useState("");
  const [endereco, setEndereco] = useState<"" | "residencial" | "profissional">("");

  // RCRI
  const [usarRcri, setUsarRcri] = useState(true);
  const [rcri, setRcri] = useState<RcriEntrada>(RCRI_INICIAL);
  const [resultadoRcri, setResultadoRcri] = useState<{ pontos: number; classe: string; evento_pct: string } | null>(null);
  const [interpretacaoRcri, setInterpretacaoRcri] = useState("");

  // Gupta MICA
  const [usarGupta, setUsarGupta] = useState(true);
  const [gupta, setGupta] = useState<GuptaEntrada>({
    idade: "", status_funcional: "independente", asa: "2", creatinina_maior_1_5: false, tipo_procedimento: "hernia",
  });
  const [resultadoGupta, setResultadoGupta] = useState<{ risco_pct: number; procedimento: string } | null>(null);
  const [interpretacaoGupta, setInterpretacaoGupta] = useState("");

  const [erroCalculo, setErroCalculo] = useState("");
  const [calculando, setCalculando] = useState(false);

  // Geração/assinatura/envio — mesmo fluxo de Templates.tsx
  const [gerando, setGerando] = useState(false);
  const [erroGeracao, setErroGeracao] = useState("");
  const [geradoId, setGeradoId] = useState<number | null>(null);
  const [metodo, setMetodo] = useState(usuario?.assinatura_metodo_preferido ?? "MANUAL");
  const [aguardandoExterno, setAguardandoExterno] = useState(false);
  const [assinadoExternoAgora, setAssinadoExternoAgora] = useState(false);
  const [email, setEmail] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [resultadoEnvio, setResultadoEnvio] = useState<{ enviado: boolean; link: string | null } | null>(null);

  useEffect(() => {
    api.get<Provedor[]>("/assinatura/provedores").then(setProvedores).catch(() => {});
  }, []);

  async function calcularEscores() {
    setCalculando(true);
    setErroCalculo("");
    try {
      if (usarRcri) {
        const r = await api.post<{ result: typeof resultadoRcri; interpretation: string }>(
          "/calculators/rcri/run", rcri,
        );
        setResultadoRcri(r.result);
        setInterpretacaoRcri(r.interpretation);
      } else {
        setResultadoRcri(null);
      }
      if (usarGupta) {
        if (!gupta.idade) throw new ApiError(422, "Informe a idade para calcular o Gupta MICA.");
        const r = await api.post<{ result: typeof resultadoGupta; interpretation: string }>(
          "/calculators/gupta-mica/run",
          { ...gupta, idade: Number(gupta.idade), asa: Number(gupta.asa) },
        );
        setResultadoGupta(r.result);
        setInterpretacaoGupta(r.interpretation);
      } else {
        setResultadoGupta(null);
      }
    } catch (e) {
      setErroCalculo(e instanceof ApiError ? e.message : "Não foi possível calcular os escores.");
    } finally {
      setCalculando(false);
    }
  }

  const podeGerar = procedimento.trim().length > 0 && (
    (usarRcri && resultadoRcri) || (usarGupta && resultadoGupta)
  );

  async function gerarDocumento() {
    if (!podeGerar) return;
    setGerando(true);
    setErroGeracao("");
    try {
      const r = await api.post<{ id: number }>("/avaliacao-preoperatoria/gerar", {
        patient_name: patientName.trim() || null,
        idade: idade ? Number(idade) : null,
        procedimento_planejado: procedimento.trim(),
        indicacao_cirurgica: indicacao.trim() || null,
        capacidade_funcional: capacidadeFuncional.trim() || null,
        conduta_recomendada: conduta.trim() || null,
        endereco: endereco || null,
        rcri: usarRcri && resultadoRcri ? rcri : null,
        gupta: usarGupta && resultadoGupta ? { ...gupta, idade: Number(gupta.idade), asa: Number(gupta.asa) } : null,
      });
      setGeradoId(r.id);
    } catch (e) {
      setErroGeracao(e instanceof ApiError ? e.message : "Não foi possível gerar o documento.");
    } finally {
      setGerando(false);
    }
  }

  async function baixar() {
    if (!geradoId) return;
    try {
      const blob = await api.blob(
        `/document-templates/gerados/${geradoId}/pdf?metodo=${encodeURIComponent(metodo)}`,
      );
      baixarBlob(blob, `avaliacao-preoperatoria-${geradoId}.pdf`);
      setAguardandoExterno(METODOS_MANUAL_EXTERNO.has(metodo));
    } catch (e) {
      setErroGeracao(e instanceof ApiError ? e.message : "Não foi possível baixar o PDF.");
    }
  }

  async function enviarPorEmail() {
    if (!geradoId || !email) return;
    setEnviando(true);
    setErroGeracao("");
    try {
      const r = await api.post<{ enviado: boolean; link: string | null }>(
        `/document-templates/gerados/${geradoId}/enviar-email`, { email },
      );
      setResultadoEnvio(r);
    } catch (e) {
      setErroGeracao(e instanceof ApiError ? e.message : "Não foi possível enviar o e-mail.");
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div style={{ maxWidth: 820 }}>
      <p className="eyebrow">Pacientes e prática</p>
      <h1>Avaliação Cardiológica Pré-Operatória de Risco Cirúrgico</h1>
      <p style={{ color: "var(--texto-secundario)", maxWidth: "70ch" }}>
        Reúne os escores de risco cirúrgico validados nacional e internacionalmente com um
        documento pronto para imprimir, assinar digitalmente e enviar ao paciente. Conteúdo
        científico de apoio: <Link to={`/biblioteca?tema=${encodeURIComponent("Perioperatório")}`}>biblioteca — tema Perioperatório</Link>.
      </p>

      <div className="cartao" style={{ marginTop: "1rem" }}>
        <p className="eyebrow" style={{ marginTop: 0 }}>Dados do paciente e do procedimento</p>
        <label>Nome do paciente</label>
        <input value={patientName} onChange={(e) => setPatientName(e.target.value)} placeholder="Usado só para organizar o histórico" />
        <div className="grade grade--2" style={{ marginTop: "0.6rem" }}>
          <div>
            <label>Idade</label>
            <input type="number" min={0} max={120} value={idade} onChange={(e) => setIdade(e.target.value)} />
          </div>
          <div>
            <label>Capacidade funcional (opcional)</label>
            <input value={capacidadeFuncional} onChange={(e) => setCapacidadeFuncional(e.target.value)}
                   placeholder="Ex.: sobe 2 lances de escada sem dispneia (>4 METs)" />
          </div>
        </div>
        <label style={{ marginTop: "0.6rem" }}>Procedimento planejado</label>
        <input value={procedimento} onChange={(e) => setProcedimento(e.target.value)} placeholder="Ex.: colecistectomia videolaparoscópica eletiva" />
        <label style={{ marginTop: "0.6rem" }}>Indicação cirúrgica (opcional)</label>
        <input value={indicacao} onChange={(e) => setIndicacao(e.target.value)} />
      </div>

      <div className="cartao" style={{ marginTop: "1rem" }}>
        <label style={{ display: "flex", gap: 8, alignItems: "center", fontWeight: 700 }}>
          <input type="checkbox" checked={usarRcri} onChange={(e) => setUsarRcri(e.target.checked)} />
          RCRI — Índice de Risco Cardíaco Revisado (Lee 1999)
        </label>
        {usarRcri && (
          <div style={{ marginTop: "0.5rem" }}>
            {(Object.keys(RCRI_LABELS) as (keyof RcriEntrada)[]).map((chave) => (
              <label key={chave} style={{ display: "flex", gap: 8, alignItems: "flex-start", fontWeight: 400, marginBottom: "0.4rem" }}>
                <input type="checkbox" checked={rcri[chave]}
                       onChange={(e) => setRcri({ ...rcri, [chave]: e.target.checked })} style={{ marginTop: 3 }} />
                <span>{RCRI_LABELS[chave]}</span>
              </label>
            ))}
          </div>
        )}
      </div>

      <div className="cartao" style={{ marginTop: "1rem" }}>
        <label style={{ display: "flex", gap: 8, alignItems: "center", fontWeight: 700 }}>
          <input type="checkbox" checked={usarGupta} onChange={(e) => setUsarGupta(e.target.checked)} />
          Gupta MICA — risco de infarto ou parada cardíaca perioperatória
        </label>
        {usarGupta && (
          <div className="grade grade--2" style={{ marginTop: "0.5rem" }}>
            <div>
              <label>Idade</label>
              <input type="number" min={18} max={110} value={gupta.idade}
                     onChange={(e) => setGupta({ ...gupta, idade: e.target.value })} />
            </div>
            <div>
              <label>Status funcional</label>
              <select value={gupta.status_funcional} onChange={(e) => setGupta({ ...gupta, status_funcional: e.target.value })}>
                <option value="independente">Independente</option>
                <option value="parcialmente_dependente">Parcialmente dependente</option>
                <option value="totalmente_dependente">Totalmente dependente</option>
              </select>
            </div>
            <div>
              <label>Classe ASA</label>
              <select value={gupta.asa} onChange={(e) => setGupta({ ...gupta, asa: e.target.value })}>
                <option value="1">ASA I — saudável</option>
                <option value="2">ASA II — doença sistêmica leve</option>
                <option value="3">ASA III — doença sistêmica grave</option>
                <option value="4">ASA IV — ameaça constante à vida</option>
                <option value="5">ASA V — moribundo</option>
              </select>
            </div>
            <div>
              <label>Tipo de procedimento</label>
              <select value={gupta.tipo_procedimento} onChange={(e) => setGupta({ ...gupta, tipo_procedimento: e.target.value })}>
                {GUPTA_PROCEDIMENTOS.map(([valor, rotulo]) => <option key={valor} value={valor}>{rotulo}</option>)}
              </select>
            </div>
            <label style={{ display: "flex", gap: 8, alignItems: "center", fontWeight: 400 }}>
              <input type="checkbox" checked={gupta.creatinina_maior_1_5}
                     onChange={(e) => setGupta({ ...gupta, creatinina_maior_1_5: e.target.checked })} />
              Creatinina pré-operatória &gt; 1,5 mg/dL
            </label>
          </div>
        )}
      </div>

      {erroCalculo && <p role="alert" style={{ color: "var(--alerta)", fontSize: "0.86rem", marginTop: "0.6rem" }}>{erroCalculo}</p>}
      <button className="botao" style={{ marginTop: "0.8rem" }} onClick={calcularEscores}
              disabled={calculando || (!usarRcri && !usarGupta)}>
        {calculando ? "Calculando…" : "Calcular escore(s)"}
      </button>

      {(resultadoRcri || resultadoGupta) && (
        <div className="cartao" style={{ marginTop: "0.8rem", borderLeft: "3px solid var(--acento)" }}>
          <p className="eyebrow" style={{ marginTop: 0 }}>Resultado</p>
          {resultadoRcri && (
            <p><strong>RCRI:</strong> {resultadoRcri.pontos} ponto(s) — Classe {resultadoRcri.classe}. {interpretacaoRcri}</p>
          )}
          {resultadoGupta && (
            <p><strong>Gupta MICA:</strong> {resultadoGupta.risco_pct}%. {interpretacaoGupta}</p>
          )}
        </div>
      )}

      {(resultadoRcri || resultadoGupta) && (
        <div className="cartao" style={{ marginTop: "1rem" }}>
          <p className="eyebrow" style={{ marginTop: 0 }}>Documento</p>
          <label>Conduta e recomendações (opcional)</label>
          <textarea rows={4} value={conduta} onChange={(e) => setConduta(e.target.value)}
                     placeholder="Ex.: manter betabloqueador em uso crônico; sem indicação de exame cardiológico adicional." />
          <label style={{ marginTop: "0.5rem" }}>Endereço no cabeçalho/rodapé (opcional)</label>
          <select value={endereco} onChange={(e) => setEndereco(e.target.value as typeof endereco)}>
            <option value="">Nenhum</option>
            <option value="profissional">Profissional (consultório)</option>
            <option value="residencial">Residencial</option>
          </select>

          {!geradoId ? (
            <>
              {erroGeracao && <p role="alert" style={{ color: "var(--alerta)", fontSize: "0.86rem" }}>{erroGeracao}</p>}
              <button className="botao" style={{ marginTop: "0.8rem" }} onClick={gerarDocumento} disabled={gerando || !podeGerar}>
                {gerando ? "Gerando…" : "Gerar documento"}
              </button>
            </>
          ) : (
            <>
              <p style={{ color: "var(--sucesso)", marginTop: "0.6rem" }}>Documento gerado.</p>
              <label>Método de assinatura</label>
              <select value={metodo} onChange={(e) => setMetodo(e.target.value)}>
                {(provedores ?? []).map((p) => (
                  <option key={p.codigo} value={p.codigo} disabled={!p.disponivel}>
                    {p.nome}{!p.disponivel ? " — indisponível" : ""}
                  </option>
                ))}
              </select>
              <button className="botao" style={{ marginTop: "0.6rem" }} onClick={baixar}>Baixar PDF</button>

              {aguardandoExterno && (
                <AssinaturaExternaITI
                  metodo={metodo}
                  nomeProvedor={provedores?.find((p) => p.codigo === metodo)?.nome ?? metodo}
                  enviarUrl={`/document-templates/gerados/${geradoId}/assinatura-externa`}
                  onConcluido={() => { setAguardandoExterno(false); setAssinadoExternoAgora(true); }}
                />
              )}
              {assinadoExternoAgora && (
                <p style={{ color: "var(--sucesso)", fontSize: "0.86rem", marginTop: "0.4rem" }}>
                  Assinatura conferida com sucesso — o documento já está assinado.
                </p>
              )}

              <div style={{ marginTop: "0.8rem" }}>
                <label>Enviar por e-mail ao paciente (link seguro, válido por 7 dias — exige CorvIA Mail ativo)</label>
                <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="paciente@exemplo.com" />
                <button className="botao" style={{ marginTop: "0.4rem" }} onClick={enviarPorEmail} disabled={enviando || !email}>
                  {enviando ? "Enviando…" : "Enviar por e-mail"}
                </button>
              </div>
              {resultadoEnvio && (
                resultadoEnvio.enviado ? (
                  <p style={{ color: "var(--sucesso)", fontSize: "0.86rem" }}>E-mail enviado.</p>
                ) : (
                  <p style={{ fontSize: "0.86rem" }}>
                    O envio automático não está disponível agora. Copie o link e envie manualmente:{" "}
                    <code style={{ wordBreak: "break-all" }}>{resultadoEnvio.link}</code>
                  </p>
                )
              )}
              {erroGeracao && <p role="alert" style={{ color: "var(--alerta)", fontSize: "0.86rem" }}>{erroGeracao}</p>}
            </>
          )}
        </div>
      )}
    </div>
  );
}
