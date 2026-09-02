import { Fragment, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, ApiError } from "../lib/api";
import { useAuth } from "../lib/auth";
import { Carregando, Erro } from "../components/Estado";
import AssinaturaExternaITI from "../components/AssinaturaExternaITI";
import OfertaEnvioEmailPaciente from "../components/OfertaEnvioEmailPaciente";
import TudoSobreEsteTema from "../components/TudoSobreEsteTema";
import GrafoRelacionados from "../components/GrafoRelacionados";
import { SeletorPacienteModal, type Paciente } from "../components/SeletorPaciente";

/**
 * Página de calculadora única — usada pelas 32 calculadoras do catálogo
 * (`/api/calculators`), não só as de risco cirúrgico.
 *
 * "Gerar documento", acrescentado em 07/08/2026 a pedido do Rafael ("todas
 * as calculadoras habilitadas para... gerar laudo completo do resultado?"):
 * mesmo fluxo já usado em Avaliação Pré-Operatória — dados do
 * paciente/contexto → resultado recalculado no servidor ao gerar
 * (`POST /calculators/{slug}/gerar-documento`, nunca confia no que já está
 * na tela) → assinar/baixar/enviar por e-mail, reaproveitando as rotas
 * genéricas de `document-templates/gerados/*` sem nenhum código novo ali.
 */

const METODOS_MANUAL_EXTERNO = new Set(["GOVBR", "VIDAAS", "BIRDID", "SAFEID", "NEOID", "REMOTEID", "A3_TOKEN"]);
const RESULTADOS_ESTRUTURADOS = new Set(["dose", "assessment"]);

type Provedor = { codigo: string; nome: string; nivel: string; familia: string; disponivel: boolean; motivo: string | null };

type Campo = {
  name: string; label: string; type: string; unit: string | null;
  options: { value: string | number; label: string }[];
  min: number | null; max: number | null; help: string | null; required: boolean;
};
type Calc = {
  slug: string; name: string; theme: string; purpose: string; kind: string;
  reference: string; limitations: string[]; fields: Campo[];
};
type Saida = {
  result: Record<string, unknown>; interpretation: string | null;
  reference: string; limitations: string[];
};

function baixarBlob(blob: Blob, nomeArquivo: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = nomeArquivo;
  a.click();
  URL.revokeObjectURL(url);
}

export default function Calculadora() {
  const { slug } = useParams();
  const { usuario } = useAuth();
  const [calc, setCalc] = useState<Calc | null>(null);
  const [valores, setValores] = useState<Record<string, unknown>>({});
  const [saida, setSaida] = useState<Saida | null>(null);
  const [erro, setErro] = useState("");

  const [provedores, setProvedores] = useState<Provedor[] | null>(null);
  const [mostrarDocumento, setMostrarDocumento] = useState(false);
  const [patientName, setPatientName] = useState("");
  const [pacienteVinculado, setPacienteVinculado] = useState<Paciente | null>(null);
  const [modalPacienteAberto, setModalPacienteAberto] = useState(false);
  const [contexto, setContexto] = useState("");
  const [conduta, setConduta] = useState("");
  // Padrão "Profissional" quando o médico já tem esse endereço cadastrado — mesmo fix aplicado em
  // AvaliacaoPreOperatoria.tsx, 07/08/2026 (ver comentário lá para o motivo).
  const [endereco, setEndereco] = useState<"" | "residencial" | "profissional">(() =>
    usuario?.practice_street || usuario?.practice_city ? "profissional" : "",
  );
  const [gerando, setGerando] = useState(false);
  const [erroGeracao, setErroGeracao] = useState("");
  const [geradoId, setGeradoId] = useState<number | null>(null);
  const [metodo, setMetodo] = useState(usuario?.assinatura_metodo_preferido ?? "MANUAL");
  const [aguardandoExterno, setAguardandoExterno] = useState(false);
  const [assinadoExternoAgora, setAssinadoExternoAgora] = useState(false);
  const [emitido, setEmitido] = useState(false);
  const [email, setEmail] = useState("");
  const [enviando, setEnviando] = useState(false);
  const [resultadoEnvio, setResultadoEnvio] = useState<{ enviado: boolean; link: string | null } | null>(null);

  useEffect(() => {
    api.get<Calc>(`/calculators/${slug}`).then((c) => {
      setCalc(c);
      const iniciais: Record<string, unknown> = {};
      for (const f of c.fields) {
        if (f.type === "boolean") iniciais[f.name] = false;
        if (f.type === "select") iniciais[f.name] = "";
      }
      setValores(iniciais);
    });
    setSaida(null);
    setMostrarDocumento(false);
    setGeradoId(null);
    setResultadoEnvio(null);
  }, [slug]);

  useEffect(() => {
    api.get<Provedor[]>("/assinatura/provedores").then(setProvedores).catch(() => {});
  }, []);

  useEffect(() => {
    if (usuario?.assinatura_metodo_preferido) {
      setMetodo(usuario.assinatura_metodo_preferido);
    }
  }, [usuario?.assinatura_metodo_preferido]);

  async function calcular() {
    setErro("");
    try {
      setSaida(await api.post<Saida>(`/calculators/${slug}/run`, valores));
      setGeradoId(null);
      setResultadoEnvio(null);
    } catch (e) {
      setSaida(null);
      setErro(e instanceof Error ? e.message : "Revise os valores informados.");
    }
  }

  async function gerarDocumento() {
    setGerando(true);
    setErroGeracao("");
    try {
      const r = await api.post<{ id: number }>(`/calculators/${slug}/gerar-documento`, {
        patient_name: patientName.trim() || null,
        patient_profile_id: pacienteVinculado?.id ?? null,
        contexto_clinico: contexto.trim() || null,
        conduta_recomendada: conduta.trim() || null,
        endereco: endereco || null,
        payload: valores,
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
      const blob = await api.blob(`/document-templates/gerados/${geradoId}/pdf?metodo=${encodeURIComponent(metodo)}`);
      baixarBlob(blob, `${slug}-${geradoId}.pdf`);
      setAguardandoExterno(METODOS_MANUAL_EXTERNO.has(metodo));
      setEmitido(true);
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

  if (!calc) return <Carregando />;

  const faltando = calc.fields.some(
    (f) => f.required !== false && f.type !== "boolean"
      && (valores[f.name] === undefined || valores[f.name] === "")
  );

  return (
    <div style={{ maxWidth: 720 }}>
      <Link to="/calculadoras" className="eyebrow">← Calculadoras</Link>
      <p className="eyebrow" style={{ marginTop: "0.8rem" }}>{calc.theme}</p>
      <h1>{calc.name}</h1>
      <p style={{ color: "var(--texto-secundario)" }}>{calc.purpose}</p>
      <p style={{ fontSize: "0.86rem" }}>
        Fluxograma de decisão, resumo dos estudos e demais conteúdo de apoio na{" "}
        <Link to={`/biblioteca?tema=${encodeURIComponent(calc.theme)}`}>Biblioteca — {calc.theme}</Link>.
      </p>

      <div className="cartao cartao--clinico" style={{ marginTop: "1rem" }}>
        {calc.fields.map((f) => (
          <div key={f.name} style={{ marginBottom: "0.9rem" }}>
            {f.type === "boolean" ? (
              <label style={{ display: "flex", gap: 10, alignItems: "flex-start", fontWeight: 400 }}>
                <input
                  type="checkbox"
                  style={{ marginTop: 2 }}
                  checked={Boolean(valores[f.name])}
                  onChange={(e) => setValores({ ...valores, [f.name]: e.target.checked })}
                />
                <span>
                  {f.label}
                  {f.help && (
                    <span style={{ display: "block", fontSize: "0.8rem", color: "var(--texto-secundario)" }}>
                      {f.help}
                    </span>
                  )}
                </span>
              </label>
            ) : f.type === "select" ? (
              <>
                <label htmlFor={f.name}>{f.label}</label>
                <select
                  id={f.name}
                  value={String(valores[f.name] ?? "")}
                  onChange={(e) => {
                    const opt = f.options.find((o) => String(o.value) === e.target.value);
                    setValores({ ...valores, [f.name]: opt?.value });
                  }}
                >
                  <option value="" disabled>Selecione…</option>
                  {f.options.map((o) => (
                    <option key={String(o.value)} value={String(o.value)}>{o.label}</option>
                  ))}
                </select>
              </>
            ) : (
              <>
                <label htmlFor={f.name}>
                  {f.label} {f.required === false && <span className="eyebrow">(opcional)</span>} {f.unit && <span className="eyebrow">({f.unit})</span>}
                </label>
                <input
                  id={f.name}
                  type="number"
                  inputMode="decimal"
                  step="any"
                  min={f.min ?? undefined}
                  max={f.max ?? undefined}
                  value={String(valores[f.name] ?? "")}
                  onChange={(e) => setValores({ ...valores, [f.name]: e.target.value })}
                />
              </>
            )}
          </div>
        ))}

        <button className="botao" onClick={calcular} disabled={faltando}>Calcular</button>
      </div>

      {erro && <div style={{ marginTop: "1rem" }}><Erro mensagem={erro} /></div>}

      {saida && RESULTADOS_ESTRUTURADOS.has(calc.kind) && (
        // Doses e avaliações estruturadas têm vários achados relevantes: a
        // resposta principal é a interpretação em prosa, não o primeiro valor
        // isolado no formato visual reservado aos escores numéricos.
        <div className="cartao" style={{ marginTop: "1rem", borderLeft: "3px solid var(--acento)" }}>
          <p className="eyebrow">Resultado</p>
          {saida.interpretation && (
            <p style={{ fontSize: "1.15rem", fontWeight: 600, margin: "0.3rem 0 0.8rem" }}>
              {saida.interpretation}
            </p>
          )}
          <dl style={{
            display: "grid", gridTemplateColumns: "auto 1fr", columnGap: "0.7rem", rowGap: "0.3rem",
            fontSize: "0.85rem", color: "var(--texto-secundario)", margin: 0,
          }}>
            {Object.entries(saida.result)
              .filter(([chave]) => chave !== "fora_da_faixa")
              .map(([chave, valor]) => (
                <Fragment key={chave}>
                  <dt style={{ textTransform: "capitalize" }}>{chave.replace(/_/g, " ")}</dt>
                  <dd style={{ margin: 0 }}>{String(valor)}</dd>
                </Fragment>
              ))}
          </dl>
        </div>
      )}

      {saida && !RESULTADOS_ESTRUTURADOS.has(calc.kind) && (
        <div className="cartao" style={{ marginTop: "1rem", borderLeft: "3px solid var(--acento)" }}>
          <p className="eyebrow">Resultado</p>
          <p className="dado" style={{ fontSize: "2.4rem", margin: "0.2rem 0", color: "var(--acento)" }}>
            {Object.values(saida.result)[0] as string | number}
            <span style={{ fontSize: "1rem", color: "var(--texto-secundario)", marginLeft: 8 }}>
              {(saida.result.max ? `/ ${saida.result.max}` : (saida.result.unidade as string) ?? "")}
            </span>
          </p>
          {saida.interpretation && <p>{saida.interpretation}</p>}
        </div>
      )}

      {saida && !mostrarDocumento && (
        <button className="botao botao--secundario" style={{ marginTop: "0.8rem" }} onClick={() => setMostrarDocumento(true)}>
          Gerar laudo deste resultado
        </button>
      )}

      {saida && mostrarDocumento && (
        <div className="cartao" style={{ marginTop: "1rem" }}>
          <p className="eyebrow" style={{ marginTop: 0 }}>Laudo — dados do paciente e contexto</p>
          <label style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            Nome do paciente (opcional)
            <button
              type="button"
              className="botao botao--secundario"
              style={{ padding: "0.15rem 0.5rem", fontSize: "0.72rem" }}
              onClick={() => setModalPacienteAberto(true)}
            >
              Selecionar paciente cadastrado
            </button>
          </label>
          <input
            value={patientName}
            onChange={(e) => {
              setPatientName(e.target.value);
              if (pacienteVinculado && e.target.value !== pacienteVinculado.full_name) setPacienteVinculado(null);
            }}
            placeholder="Usado só para organizar o histórico"
          />
          <SeletorPacienteModal
            aberto={modalPacienteAberto}
            onFechar={() => setModalPacienteAberto(false)}
            onSelecionar={(p) => {
              setPacienteVinculado(p);
              setPatientName(p.full_name);
              setModalPacienteAberto(false);
            }}
          />
          <label style={{ marginTop: "0.6rem" }}>Contexto clínico / procedimento (opcional)</label>
          <input
            value={contexto} onChange={(e) => setContexto(e.target.value)}
            placeholder="Ex.: colecistectomia videolaparoscópica eletiva; investigação de palpitações; etc."
          />
          <label style={{ marginTop: "0.6rem" }}>Conduta e recomendações (opcional)</label>
          <textarea rows={3} value={conduta} onChange={(e) => setConduta(e.target.value)} />
          <label style={{ marginTop: "0.6rem" }}>Endereço no cabeçalho/rodapé (opcional)</label>
          <select value={endereco} onChange={(e) => setEndereco(e.target.value as typeof endereco)}>
            <option value="">Nenhum</option>
            <option value="profissional">Profissional (consultório)</option>
            <option value="residencial">Residencial</option>
          </select>

          {!geradoId ? (
            <>
              {erroGeracao && <p role="alert" style={{ color: "var(--alerta)", fontSize: "0.86rem" }}>{erroGeracao}</p>}
              <button className="botao" style={{ marginTop: "0.8rem" }} onClick={gerarDocumento} disabled={gerando}>
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
              {geradoId && (
                <OfertaEnvioEmailPaciente
                  endpointBase={`/document-templates/gerados/${geradoId}`}
                  habilitado={emitido && !aguardandoExterno}
                />
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

      <div className="aviso">
        <strong>Referência:</strong> {calc.reference}
        {calc.limitations.length > 0 && (
          <ul style={{ margin: "0.5rem 0 0", paddingLeft: "1.1rem" }}>
            {calc.limitations.map((l) => <li key={l}>{l}</li>)}
          </ul>
        )}
      </div>

      <TudoSobreEsteTema tema={calc.theme} excluirTipo="calculadora" excluirSlug={slug} />

      <GrafoRelacionados entityType="calculadora" slug={slug} />
    </div>
  );
}
