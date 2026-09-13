import BotaoFavorito from "../components/BotaoFavorito";
import ScientificReadingAccess from "../components/ScientificReadingAccess";
import { Fragment, useEffect, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, ApiError } from "../lib/api";
import { useAuth } from "../lib/auth";
import { Carregando, Erro } from "../components/Estado";
import FinalizarDocumentoGerado from "../components/FinalizarDocumentoGerado";
import TudoSobreEsteTema from "../components/TudoSobreEsteTema";
import GrafoRelacionados from "../components/GrafoRelacionados";
import { calculatorFieldRequired, validateCalculatorFields } from "../lib/calculatorValidation";

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

const RESULTADOS_ESTRUTURADOS = new Set(["dose", "assessment"]);

type Campo = {
  name: string; label: string; type: string; unit: string | null;
  options: { value: string | number | boolean; label: string }[];
  min: number | null; max: number | null; help: string | null; required: boolean;
  required_when?: Record<string, (string | number | boolean)[]> | null;
};
type Calc = {
  slug: string; name: string; theme: string; purpose: string; kind: string;
  reference: string; limitations: string[]; fields: Campo[];
  status?: string; external_url?: string | null;
};
type Saida = {
  result: Record<string, unknown>; interpretation: string | null;
  reference: string; limitations: string[];
};

export default function Calculadora() {
  const { slug } = useParams();
  const { usuario } = useAuth();
  const [calc, setCalc] = useState<Calc | null>(null);
  const [valores, setValores] = useState<Record<string, unknown>>({});
  const [saida, setSaida] = useState<Saida | null>(null);
  const [erro, setErro] = useState("");
  const revisaoFormulario = useRef(0);
  const revisaoDocumento = useRef(0);
  const operacaoDocumento = useRef<number | null>(null);

  const [mostrarDocumento, setMostrarDocumento] = useState(false);
  const [patientName, setPatientName] = useState("");
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
  const [avisoDocumento, setAvisoDocumento] = useState("");

  useEffect(() => {
    let ativo = true;
    revisaoFormulario.current += 1;
    revisaoDocumento.current += 1;
    operacaoDocumento.current = null;
    setCalc(null);
    setValores({});
    setErro("");
    api.get<Calc>(`/calculators/${slug}`).then((c) => {
      if (!ativo) return;
      setCalc(c);
      const iniciais: Record<string, unknown> = {};
      for (const f of c.fields) {
        if (f.type === "boolean") iniciais[f.name] = false;
        if (f.type === "select") iniciais[f.name] = "";
      }
      setValores(iniciais);
    }).catch((e) => {
      if (ativo) setErro(e instanceof Error ? e.message : "Não foi possível abrir a calculadora.");
    });
    setSaida(null);
    setMostrarDocumento(false);
    setGeradoId(null);
    setErroGeracao("");
    setAvisoDocumento("");
    setGerando(false);
    return () => {
      ativo = false;
      revisaoFormulario.current += 1;
      revisaoDocumento.current += 1;
      operacaoDocumento.current = null;
    };
  }, [slug]);

  function invalidarDocumento(aviso = "") {
    revisaoDocumento.current += 1;
    operacaoDocumento.current = null;
    setGeradoId(null);
    setGerando(false);
    setErroGeracao("");
    setAvisoDocumento(aviso);
  }

  function atualizarDadosLaudo(atualizar: () => void) {
    invalidarDocumento(geradoId !== null || gerando
      ? "Dados do laudo alterados. Gere um novo documento para incluir as alterações."
      : avisoDocumento);
    atualizar();
  }

  function atualizarCampo(nome: string, valor: unknown) {
    revisaoFormulario.current += 1;
    setValores((atuais) => ({ ...atuais, [nome]: valor }));
    setSaida(null);
    setErro("");
    setMostrarDocumento(false);
    invalidarDocumento();
  }

  async function calcular() {
    if (!calc || calc.slug !== slug || calc.status === "referencia_externa") return;
    if (Object.keys(validateCalculatorFields(calc.fields, valores)).length) {
      setSaida(null);
      setErro("Revise os campos indicados antes de calcular.");
      return;
    }
    const revisao = ++revisaoFormulario.current;
    invalidarDocumento();
    setErro("");
    try {
      const resultado = await api.post<Saida>(`/calculators/${slug}/run`, valores);
      if (revisao !== revisaoFormulario.current) return;
      setSaida(resultado);
    } catch (e) {
      if (revisao !== revisaoFormulario.current) return;
      setSaida(null);
      setErro(e instanceof Error ? e.message : "Revise os valores informados.");
    }
  }

  async function gerarDocumento() {
    if (operacaoDocumento.current !== null || !saida || !calc || calc.slug !== slug || calc.status === "referencia_externa") return;
    const revisao = ++revisaoDocumento.current;
    operacaoDocumento.current = revisao;
    setGerando(true);
    setErroGeracao("");
    setAvisoDocumento("");
    try {
      const r = await api.post<{ id: number }>(`/calculators/${slug}/gerar-documento`, {
        patient_name: patientName.trim() || null,
        contexto_clinico: contexto.trim() || null,
        conduta_recomendada: conduta.trim() || null,
        endereco: endereco || null,
        payload: valores,
      });
      if (revisao === revisaoDocumento.current) setGeradoId(r.id);
    } catch (e) {
      if (revisao === revisaoDocumento.current) setErroGeracao(e instanceof ApiError ? e.message : "Não foi possível gerar o documento.");
    } finally {
      if (revisao === revisaoDocumento.current) {
        operacaoDocumento.current = null;
        setGerando(false);
      }
    }
  }

  if (!calc || calc.slug !== slug) return erro ? <Erro mensagem={erro} /> : <Carregando />;

  const externa = calc.status === "referencia_externa";

  const errosCampos = validateCalculatorFields(calc.fields, valores);
  const faltando = Object.keys(errosCampos).length > 0;

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

      {externa ? (
        <div className="cartao cartao--clinico" style={{ marginTop: "1rem" }}>
          <p className="eyebrow">Ferramenta oficial externa</p>
          <p>A ferramenta é disponibilizada pela instituição responsável. O cálculo é realizado no serviço oficial. O CorVIA não envia dados preenchidos.</p>
          {calc.external_url && /^https:\/\//.test(calc.external_url) ? (
            <a className="botao" href={calc.external_url} target="_blank" rel="noopener noreferrer" referrerPolicy="no-referrer">
              Acessar ferramenta oficial ↗
            </a>
          ) : <p>O acesso à ferramenta oficial está indisponível no momento.</p>}
        </div>
      ) : <>
      <div className="cartao cartao--clinico" style={{ marginTop: "1rem" }}>
        {calc.fields.map((f) => (
          <div key={f.name} style={{ marginBottom: "0.9rem" }}>
            {f.type === "boolean" ? (
              <label style={{ display: "flex", gap: 10, alignItems: "flex-start", fontWeight: 400 }}>
                <input
                  type="checkbox"
                  style={{ marginTop: 2 }}
                  checked={Boolean(valores[f.name])}
                  onChange={(e) => atualizarCampo(f.name, e.target.checked)}
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
                    atualizarCampo(f.name, opt?.value);
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
                  {f.label} {!calculatorFieldRequired(f, valores) && <span className="eyebrow">(opcional)</span>} {f.unit && <span className="eyebrow">({f.unit})</span>}
                </label>
                <input
                  id={f.name}
                  type="number"
                  inputMode="decimal"
                  step="any"
                  min={f.min ?? undefined}
                  max={f.max ?? undefined}
                  aria-invalid={Boolean(errosCampos[f.name] && valores[f.name] !== undefined && valores[f.name] !== "")}
                  aria-describedby={errosCampos[f.name] && valores[f.name] !== undefined && valores[f.name] !== "" ? `${f.name}-erro` : undefined}
                  value={String(valores[f.name] ?? "")}
                  onChange={(e) => atualizarCampo(f.name, e.target.value)}
                />
              </>
            )}
            {f.type !== "boolean" && f.help && <p style={{ fontSize: "0.8rem", color: "var(--texto-secundario)", margin: "0.3rem 0 0" }}>{f.help}</p>}
            {errosCampos[f.name] && valores[f.name] !== undefined && valores[f.name] !== "" && <p id={`${f.name}-erro`} role="alert" style={{ margin: "0.3rem 0 0", color: "var(--perigo)", fontSize: "0.86rem" }}>{errosCampos[f.name]}</p>}
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
          <p>Alterar estes dados exige um novo documento e preserva as versões já geradas.</p>
          <label htmlFor="laudo-calculadora-paciente">Nome do paciente (opcional)</label>
          <input id="laudo-calculadora-paciente" value={patientName} onChange={(e) => atualizarDadosLaudo(() => setPatientName(e.target.value))} placeholder="Usado só para organizar o histórico" />
          <label htmlFor="laudo-calculadora-contexto" style={{ marginTop: "0.6rem" }}>Contexto clínico / procedimento (opcional)</label>
          <input
            id="laudo-calculadora-contexto" value={contexto} onChange={(e) => atualizarDadosLaudo(() => setContexto(e.target.value))}
            placeholder="Ex.: colecistectomia videolaparoscópica eletiva; investigação de palpitações; etc."
          />
          <label htmlFor="laudo-calculadora-conduta" style={{ marginTop: "0.6rem" }}>Conduta e recomendações (opcional)</label>
          <textarea id="laudo-calculadora-conduta" rows={3} value={conduta} onChange={(e) => atualizarDadosLaudo(() => setConduta(e.target.value))} />
          <label htmlFor="laudo-calculadora-endereco" style={{ marginTop: "0.6rem" }}>Endereço no cabeçalho/rodapé (opcional)</label>
          <select id="laudo-calculadora-endereco" value={endereco} onChange={(e) => atualizarDadosLaudo(() => setEndereco(e.target.value as typeof endereco))}>
            <option value="">Nenhum</option>
            <option value="profissional">Profissional (consultório)</option>
            <option value="residencial">Residencial</option>
          </select>
          {avisoDocumento && <p role="status">{avisoDocumento}</p>}

          {!geradoId ? (
            <>
              {erroGeracao && <p role="alert" style={{ color: "var(--alerta)", fontSize: "0.86rem" }}>{erroGeracao}</p>}
              <button className="botao" style={{ marginTop: "0.8rem" }} onClick={gerarDocumento} disabled={gerando}>
                {gerando ? "Gerando…" : "Gerar documento"}
              </button>
            </>
          ) : (
            <FinalizarDocumentoGerado
              key={geradoId} geradoId={geradoId} nomeArquivoBase={slug || "calculadora"}
              provedores={null} onFechar={() => setMostrarDocumento(false)}
            />
          )}
        </div>
      )}

      </>}

      <div className="aviso">
        <strong>Referência:</strong> {calc.reference}
        {calc.limitations.length > 0 && (
          <ul style={{ margin: "0.5rem 0 0", paddingLeft: "1.1rem" }}>
            {calc.limitations.map((l) => <li key={l}>{l}</li>)}
          </ul>
        )}
      </div>

      <BotaoFavorito itemType="calculadora" itemSlug={slug} />

      <ScientificReadingAccess entityType="calculadora" slug={slug} />

      <TudoSobreEsteTema tema={calc.theme} excluirTipo="calculadora" excluirSlug={slug} />

      <GrafoRelacionados entityType="calculadora" slug={slug} />
    </div>
  );
}
