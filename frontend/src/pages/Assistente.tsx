import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { api } from "../lib/api";
import { Carregando } from "../components/Estado";

type Fonte = {
  referencia: string; slug: string; titulo: string; tema: string; review_status: string;
};
type FontePubmed = { pmid: string; titulo: string; autores: string; revista: string; ano: string; url: string };
type Mensagem = { papel: "user" | "assistant"; conteudo: string; fontes?: Fonte[]; fontesPubmed?: FontePubmed[] };
type Status = {
  ativo: boolean; provedor: string; modelo: string;
  limite_diario: number; usado_hoje: number; restante_hoje: number;
};
type ConversaResumo = { id: number; titulo: string; updated_at: string };

export default function Assistente() {
  const [status, setStatus] = useState<Status | null>(null);
  const [mensagens, setMensagens] = useState<Mensagem[]>([]);
  const [pergunta, setPergunta] = useState("");
  const [conversa, setConversa] = useState<number | null>(null);
  const [pensando, setPensando] = useState(false);
  const [erro, setErro] = useState("");
  const [historico, setHistorico] = useState<ConversaResumo[]>([]);
  const [mostrarHistorico, setMostrarHistorico] = useState(false);
  const fim = useRef<HTMLDivElement>(null);

  useEffect(() => { api.get<Status>("/ai/status").then(setStatus).catch(() => setStatus(null)); }, []);
  useEffect(() => { fim.current?.scrollIntoView({ behavior: "smooth" }); }, [mensagens, pensando]);

  const recarregarHistorico = () => api.get<ConversaResumo[]>("/ai/conversas").then(setHistorico).catch(() => {});
  useEffect(() => { recarregarHistorico(); }, []);

  async function abrirConversa(id: number) {
    const c = await api.get<{
      mensagens: { papel: "user" | "assistant"; conteudo: string; fontes: Fonte[]; fontes_pubmed: FontePubmed[] }[]
    }>(`/ai/conversas/${id}`);
    setConversa(id);
    setMensagens(c.mensagens.map((m) => ({
      ...m, fontes: m.fontes.length ? m.fontes : undefined,
      fontesPubmed: m.fontes_pubmed?.length ? m.fontes_pubmed : undefined,
    })));
    setMostrarHistorico(false);
  }

  function novaConversa() {
    setConversa(null);
    setMensagens([]);
    setMostrarHistorico(false);
  }

  async function apagarConversa(id: number, e: React.MouseEvent) {
    e.stopPropagation();
    await api.delete(`/ai/conversas/${id}`);
    if (conversa === id) novaConversa();
    recarregarHistorico();
  }

  async function enviar() {
    const texto = pergunta.trim();
    if (!texto || pensando) return;
    setPergunta("");
    setErro("");
    setMensagens((m) => [...m, { papel: "user", conteudo: texto }]);
    setPensando(true);
    try {
      const r = await api.post<{
        conversation_id: number; resposta: string; fontes: Fonte[]; fontes_pubmed: FontePubmed[];
      }>("/ai/perguntar", { pergunta: texto, conversation_id: conversa });
      setConversa(r.conversation_id);
      setMensagens((m) => [...m, {
        papel: "assistant", conteudo: r.resposta, fontes: r.fontes,
        fontesPubmed: r.fontes_pubmed?.length ? r.fontes_pubmed : undefined,
      }]);
      setStatus((s) => s && { ...s, usado_hoje: s.usado_hoje + 1, restante_hoje: s.restante_hoje - 1 });
      recarregarHistorico();
    } catch (e) {
      setErro(e instanceof Error ? e.message : "Não foi possível consultar o assistente.");
    } finally {
      setPensando(false);
    }
  }

  if (!status) return <Carregando />;

  if (!status.ativo) {
    return (
      <>
        <p className="eyebrow">Assistente clínico</p>
        <h1>Assistente desligado</h1>
        <div className="cartao">
          <p style={{ marginTop: 0 }}>
            Defina <code>AI_ENABLED=true</code> e a chave do provedor no <code>.env</code>,
            depois rode a indexação da base científica.
          </p>
          <pre className="bloco-comando">docker compose exec backend python -m app.services.indexar</pre>
        </div>
      </>
    );
  }

  return (
    <div className="ia">
      <header className="ia__topo">
        <div>
          <p className="eyebrow">Assistente clínico</p>
          <h1 style={{ marginBottom: 2 }}>Perguntar à base</h1>
        </div>
        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <button className="botao botao--secundario" style={{ padding: "0.35rem 0.7rem", fontSize: "0.82rem" }}
                  onClick={novaConversa}>
            + Nova
          </button>
          <button className="botao botao--secundario" style={{ padding: "0.35rem 0.7rem", fontSize: "0.82rem" }}
                  onClick={() => setMostrarHistorico((v) => !v)}>
            Histórico ({historico.length})
          </button>
          <span className="selo dado">
            {status.restante_hoje} de {status.limite_diario} hoje
          </span>
        </div>
      </header>

      {mostrarHistorico && (
        <div className="cartao" style={{ marginBottom: "0.8rem", maxHeight: 260, overflowY: "auto" }}>
          {historico.length === 0 ? (
            <p style={{ margin: 0, color: "var(--cinza-texto)", fontSize: "0.88rem" }}>
              Nenhuma conversa anterior ainda.
            </p>
          ) : (
            historico.map((c) => (
              <div key={c.id}
                   onClick={() => abrirConversa(c.id)}
                   style={{
                     display: "flex", justifyContent: "space-between", alignItems: "center",
                     padding: "0.5rem 0.3rem", borderBottom: "1px solid var(--cinza-borda)",
                     cursor: "pointer", background: conversa === c.id ? "var(--cinza-fundo)" : "transparent",
                   }}>
                <span style={{ fontSize: "0.88rem" }}>{c.titulo}</span>
                <button className="botao botao--secundario" style={{ padding: "0.2rem 0.5rem", fontSize: "0.76rem" }}
                        onClick={(e) => apagarConversa(c.id, e)} aria-label="Apagar conversa">
                  ✕
                </button>
              </div>
            ))
          )}
        </div>
      )}

      <div className="ia__conversa">
        {mensagens.length === 0 && (
          <div className="ia__abertura">
            <p>
              As respostas saem da base científica do serviço e vêm com as fontes usadas.
              Quando a base não sustenta a resposta, o assistente diz isso.
            </p>
            <p className="ia__privacidade">
              Descreva o caso sem identificar o paciente. CPF, telefone, cartão SUS e e-mail
              são bloqueados no envio.
            </p>
            <div className="ia__sugestoes">
              {[
                "Quando indicar anticoagulação em FA com CHA₂DS₂-VASc 1?",
                "Ajuste de dose de apixabana na doença renal crônica",
                "Quais os quatro pilares da ICFER e a ordem de introdução?",
              ].map((s) => (
                <button key={s} className="ia__sugestao" onClick={() => setPergunta(s)}>
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {mensagens.map((m, i) => (
          <div key={i} className={`ia__msg ia__msg--${m.papel}`}>
            {m.papel === "assistant" ? (
              <>
                <Markdown remarkPlugins={[remarkGfm]}>{m.conteudo}</Markdown>
                {m.fontes && m.fontes.length > 0 && (
                  <div className="ia__fontes">
                    <p className="eyebrow">Fontes consultadas</p>
                    {m.fontes.map((f) => (
                      <Link key={f.slug} to={`/biblioteca/${f.slug}`} className="ia__fonte">
                        <span className="dado ia__fonte__marca">{f.referencia}</span>
                        <span>{f.titulo}</span>
                        {f.review_status === "verificacao_humana_necessaria" && (
                          <span className="selo selo--pendente">verificar</span>
                        )}
                      </Link>
                    ))}
                  </div>
                )}
                {m.fontesPubmed && m.fontesPubmed.length > 0 && (
                  <div className="ia__fontes">
                    <p className="eyebrow">Literatura pública (PubMed) — fonte externa, não institucional</p>
                    {m.fontesPubmed.map((f) => (
                      <a key={f.pmid} href={f.url} target="_blank" rel="noopener noreferrer" className="ia__fonte">
                        <span className="dado ia__fonte__marca">PM</span>
                        <span>{f.titulo} — {f.autores} et al. {f.revista}, {f.ano}</span>
                      </a>
                    ))}
                  </div>
                )}
              </>
            ) : (
              m.conteudo
            )}
          </div>
        ))}

        {pensando && (
          <div className="ia__msg ia__msg--assistant ia__pensando">
            <span /><span /><span />
          </div>
        )}
        <div ref={fim} />
      </div>

      {erro && <p className="ia__erro" role="alert">{erro}</p>}

      <div className="ia__envio">
        <textarea
          rows={2}
          value={pergunta}
          onChange={(e) => setPergunta(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); enviar(); }
          }}
          placeholder="Descreva a dúvida clínica, sem identificar o paciente…"
          aria-label="Pergunta"
        />
        <button className="botao" onClick={enviar} disabled={!pergunta.trim() || pensando}>
          Enviar
        </button>
      </div>
      <p className="ia__rodape">
        Apoio à decisão. Não substitui julgamento clínico, bula nem diretriz vigente.
      </p>
    </div>
  );
}
