import { CSSProperties, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { api, ApiError } from "../lib/api";
import TudoSobreEsteTema from "../components/TudoSobreEsteTema";

type Caso = {
  slug: string;
  titulo: string;
  tema: string | null;
  nivel: string | null;
  enunciado: string;
  pergunta: string;
  opcoes: string[];
  resposta_correta: number;
  explicacao: string;
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

  useEffect(() => {
    setCaso(null);
    setEscolhida(null);
    setResultado(null);
    setErro("");
    api
      .get<Caso>(`/casos-clinicos/${slug}`)
      .then(setCaso)
      .catch((e) => setErro(e instanceof ApiError ? e.message : "Não foi possível carregar o caso."));
  }, [slug]);

  async function responder() {
    if (escolhida === null) return;
    setEnviando(true);
    try {
      const r = await api.post<Resultado>(`/casos-clinicos/${slug}/responder`, {
        opcao_escolhida: escolhida,
      });
      setResultado(r);
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível registrar a resposta.");
    } finally {
      setEnviando(false);
    }
  }

  if (erro) return <p role="alert" style={{ color: "var(--alerta)" }}>{erro}</p>;
  if (!caso) return <p>Carregando…</p>;

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
                disabled={revelada}
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

      <TudoSobreEsteTema tema={caso.tema} excluirTipo="caso_clinico" excluirSlug={slug} />
    </div>
  );
}
