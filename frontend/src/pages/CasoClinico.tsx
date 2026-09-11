import BotaoFavorito from "../components/BotaoFavorito";
import ScientificReadingAccess from "../components/ScientificReadingAccess";
import { CSSProperties, useEffect, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { api, ApiError, READ_TIMEOUT_MS } from "../lib/api";
import TudoSobreEsteTema from "../components/TudoSobreEsteTema";
import GrafoRelacionados from "../components/GrafoRelacionados";

type Caso = {
  slug: string;
  titulo: string;
  tema: string | null;
  nivel: string | null;
  enunciado: string;
  pergunta: string;
  opcoes: string[];
  source_refs: string[];
};

type Resultado = { acertou: boolean; resposta_correta: number; explicacao: string };

export default function CasoClinico() {
  const { slug = "" } = useParams();
  const [caso, setCaso] = useState<Caso | null>(null);
  const [erro, setErro] = useState("");
  const [escolhida, setEscolhida] = useState<number | null>(null);
  const [resultado, setResultado] = useState<Resultado | null>(null);
  const [enviando, setEnviando] = useState(false);
  const [tentativa, setTentativa] = useState(0);
  const context = useRef(slug);
  context.current = slug;
  const generation = useRef(0);
  const submission = useRef<number | null>(null);

  useEffect(() => {
    const sequence = ++generation.current;
    const controller = new AbortController();
    let active = true;
    const current = () => active && sequence === generation.current && context.current === slug;
    setCaso(null);
    setEscolhida(null);
    setResultado(null);
    setErro("");
    setEnviando(false);
    submission.current = null;
    api
      .get<Caso>(`/casos-clinicos/${slug}`, { signal: controller.signal, timeoutMs: READ_TIMEOUT_MS })
      .then(value => {
        if (!current()) return;
        if (value.slug !== slug || !value.titulo?.trim() || !value.enunciado?.trim() || !value.pergunta?.trim() || !Array.isArray(value.opcoes) || !value.opcoes.length || value.opcoes.some(option => typeof option !== "string" || !option.trim()) || !Array.isArray(value.source_refs)) {
          throw new Error("Incomplete case content");
        }
        setCaso(value);
      })
      .catch((e) => { if (current()) setErro(e instanceof ApiError ? e.message : "Não foi possível carregar o conteúdo completo do caso. Tente novamente."); });
    return () => { active = false; generation.current++; controller.abort(); };
  }, [slug, tentativa]);

  async function responder() {
    if (escolhida === null || enviando || resultado !== null || caso?.slug !== slug || submission.current !== null) return;
    const sequence = generation.current;
    submission.current = sequence;
    setErro("");
    setEnviando(true);
    try {
      const r = await api.post<Resultado>(`/casos-clinicos/${slug}/responder`, {
        opcao_escolhida: escolhida,
      });
      if (sequence === generation.current && context.current === slug) setResultado(r);
    } catch (e) {
      if (sequence === generation.current && context.current === slug) setErro(e instanceof ApiError ? e.message : "Não foi possível registrar a resposta.");
    } finally {
      if (sequence === generation.current && context.current === slug) { submission.current = null; setEnviando(false); }
    }
  }

  if (erro && !caso) return <div><p role="alert" style={{ color: "var(--alerta)" }}>{erro}</p><button className="botao" type="button" onClick={() => setTentativa(v => v + 1)}>Tentar novamente</button></div>;
  if (!caso || caso.slug !== slug) return <p role="status">Carregando…</p>;

  return (
    <div>
      <p className="curso__voltar">
        <Link to="/casos-clinicos">← Todos os casos</Link>
      </p>
      <p className="eyebrow">
        {caso.tema}
        {caso.nivel && ` · ${caso.nivel}`}
      </p>
      <h1>{caso.titulo}</h1>

      {erro && <p role="alert" style={{ color: "var(--alerta)" }}>{erro}</p>}

      <div className="cartao" style={{ maxWidth: "72ch" }}>
        <Markdown remarkPlugins={[remarkGfm]}>{caso.enunciado}</Markdown>
        <p style={{ fontWeight: 600, marginTop: "1rem" }}>{caso.pergunta}</p>

        <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem", marginTop: "0.8rem" }}>
          {caso.opcoes.map((op, i) => {
            const revelada = resultado !== null;
            const éCorreta = i === resultado?.resposta_correta;
            const éEscolhida = i === escolhida;
            let estilo: CSSProperties = {
              textAlign: "left",
              padding: "0.6rem 0.9rem",
              borderRadius: "var(--r)",
              border: "1px solid var(--borda)",
              cursor: revelada ? "default" : "pointer",
              background: "var(--superficie)",
            };
            if (revelada && éCorreta) {
              estilo = { ...estilo, borderColor: "var(--sucesso)", background: "var(--acento-tinta)" };
            } else if (revelada && éEscolhida && !éCorreta) {
              estilo = { ...estilo, borderColor: "var(--alerta)" };
            } else if (!revelada && éEscolhida) {
              estilo = { ...estilo, borderColor: "var(--acento)" };
            }
            return (
              <button
                key={i}
                type="button"
                disabled={revelada || enviando}
                onClick={() => setEscolhida(i)}
                style={estilo}
              >
                {op}
                {revelada && éCorreta && " ✓"}
                {revelada && éEscolhida && !éCorreta && " ✗"}
              </button>
            );
          })}
        </div>

        {!resultado && (
          <button
            className="botao"
            style={{ marginTop: "1rem" }}
            onClick={responder}
            disabled={escolhida === null || enviando}
          >
            {enviando ? "Enviando…" : "Confirmar resposta"}
          </button>
        )}

        {resultado && (
          <div style={{ marginTop: "1.2rem", borderTop: "1px solid var(--borda)", paddingTop: "1rem" }}>
            <p style={{ fontWeight: 600, color: resultado.acertou ? "var(--sucesso)" : "var(--alerta)" }}>
              {resultado.acertou ? "Resposta correta." : "Não foi essa a conduta recomendada."}
            </p>
            <Markdown remarkPlugins={[remarkGfm]}>{resultado.explicacao}</Markdown>
            {caso.source_refs.length > 0 && (
              <p style={{ fontSize: "0.8rem", color: "var(--texto-secundario)", marginTop: "0.8rem" }}>
                Fonte: {caso.source_refs.join(" · ")}
              </p>
            )}
          </div>
        )}
      </div>

      <BotaoFavorito itemType="caso_clinico" itemSlug={slug} />

      <ScientificReadingAccess entityType="caso_clinico" slug={slug} />

      <TudoSobreEsteTema tema={caso.tema} excluirTipo="caso_clinico" excluirSlug={slug} />

      <GrafoRelacionados entityType="caso_clinico" slug={slug} />
    </div>
  );
}
