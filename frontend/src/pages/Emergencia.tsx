import { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { api } from "../lib/api";
import Fluxograma from "../components/Fluxograma";
import Icone from "../components/Icone";
import GrafoRelacionados from "../components/GrafoRelacionados";
import "../styles/emergencia.css";

const CACHE = "corvia.emergencia";

type Doc = {
  slug: string; title: string; theme: string; body_md: string;
  source_refs: string[]; source_tier: string; review_status: string; gaps: string[];
};
type Protocolo = {
  slug: string; titulo: string; gatilho: string | null;
  documento_slug: string; fluxograma_slug: string | null; relacionados: string[];
};
type Pacote = { protocolos: Protocolo[]; documentos: Record<string, Doc> };

function guardar(p: Pacote) {
  try { localStorage.setItem(CACHE, JSON.stringify({ em: Date.now(), pacote: p })); } catch { /* offline é melhoria, nunca bloqueio */ }
}
function recuperar(): { em: number; pacote: Pacote } | null {
  try { const cru = localStorage.getItem(CACHE); return cru ? JSON.parse(cru) : null; } catch { return null; }
}
function fonteMermaid(md: string): string | null {
  const m = md.match(/```mermaid\s*\n([\s\S]*?)```/); return m ? m[1].trim() : null;
}
function secoes(md: string): { titulo: string; corpo: string }[] {
  const semDiagrama = md.replace(/```mermaid[\s\S]*?```/g, "");
  return semDiagrama.split(/\n(?=##\s)/).map((p) => {
    const m = p.match(/^##\s+(.*)\n?([\s\S]*)$/);
    return m ? { titulo: m[1].trim(), corpo: m[2].trim() } : { titulo: "", corpo: p.trim() };
  }).filter((s) => s.titulo || s.corpo);
}
function normalizarBusca(valor: string): string {
  return valor.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLocaleLowerCase("pt-BR").replace(/\s+/g, " ").trim();
}

export default function Emergencia() {
  const [params, setParams] = useSearchParams();
  const [pacote, setPacote] = useState<Pacote | null>(null);
  const [deCache, setDeCache] = useState<number | null>(null);
  const [erro, setErro] = useState("");
  const [secaoAberta, setSecaoAberta] = useState<number>(0);
  const [busca, setBusca] = useState("");
  const [tema, setTema] = useState("");

  useEffect(() => {
    const local = recuperar();
    if (local) { setPacote(local.pacote); setDeCache(local.em); }
    api.get<Pacote>("/emergencia").then((p) => { setPacote(p); setDeCache(null); guardar(p); }).catch((e) => { if (!local) setErro(e?.message || "Sem conexão e sem cópia guardada."); });
  }, []);

  const temas = useMemo(() => {
    const contagem = new Map<string, number>();
    (pacote?.protocolos || []).forEach((p) => { const t = pacote?.documentos[p.documento_slug]?.theme; if (t) contagem.set(t, (contagem.get(t) ?? 0) + 1); });
    return [...contagem.entries()].sort((a, b) => a[0].localeCompare(b[0], "pt-BR"));
  }, [pacote]);

  const protocolosFiltrados = useMemo(() => {
    const protocolos = pacote?.protocolos || [];
    const termos = normalizarBusca(busca).split(" ").filter(Boolean);
    return protocolos.filter((p) => {
      const documento = pacote?.documentos[p.documento_slug];
      if (tema && documento?.theme !== tema) return false;
      if (termos.length === 0) return true;
      const texto = normalizarBusca([p.titulo, p.gatilho || "", documento?.title || "", documento?.theme || ""].join(" "));
      return termos.every((termo) => texto.includes(termo));
    });
  }, [busca, tema, pacote]);

  const slugAberto = params.get("protocolo");
  useEffect(() => {
    setSecaoAberta(0);
    window.scrollTo({ top: 0, left: 0 });
  }, [slugAberto]);
  const protocolo = useMemo(
    () => pacote?.protocolos.find((p) => p.slug === slugAberto) || null,
    [pacote, slugAberto],
  );
  const protocoloInvalido = Boolean(pacote && slugAberto && !protocolo);
  const doc = protocolo ? pacote?.documentos[protocolo.documento_slug] : null;
  const fluxo = protocolo?.fluxograma_slug ? pacote?.documentos[protocolo.fluxograma_slug] : null;
  const diagrama = fluxo ? fonteMermaid(fluxo.body_md) : null;
  const blocos = doc ? secoes(doc.body_md) : [];
  const relacionados = useMemo(() => (protocolo?.relacionados || []).map((slug) => {
    const documento = pacote?.documentos[slug];
    const protocoloRelacionado = pacote?.protocolos.find((item) => item.slug === slug);
    if (documento) return { slug, titulo: documento.title, tipo: "documento" as const };
    if (protocoloRelacionado) return { slug, titulo: protocoloRelacionado.titulo, tipo: "protocolo" as const };
    return null;
  }).filter((item): item is NonNullable<typeof item> => item !== null), [pacote, protocolo]);

  function abrirProtocolo(slug: string | null) {
    const proximos = new URLSearchParams(params);
    if (slug) proximos.set("protocolo", slug);
    else proximos.delete("protocolo");
    setParams(proximos);
  }

  return (
    <div className="emerg">
      <header className="emerg__topo"><span className="emerg__marca">Modo emergência</span>{deCache !== null && <span className="emerg__offline">Sem conexão · cópia de {new Date(deCache).toLocaleDateString("pt-BR")}</span>}</header>

      {erro && <p className="emerg__erro">{erro} Abra esta tela uma vez com conexão para que ela fique disponível offline.</p>}

      {!protocolo && <>
        {protocoloInvalido && (
          <p className="emerg__erro">O protocolo solicitado não está publicado ou não existe.</p>
        )}
        <p className="emerg__aviso">Protocolos de risco imediato de vida. O conteúdo é o mesmo da biblioteca — aqui ele está filtrado e ampliado para leitura rápida.</p>
        <div className="emerg__busca">
          <label htmlFor="busca-emergencia">Buscar assunto</label>
          <div className="emerg__buscaLinha"><input id="busca-emergencia" type="search" value={busca} onChange={(event) => setBusca(event.target.value)} placeholder="Ex.: infarto, choque, arritmia" autoComplete="off" spellCheck={false} />{busca && <button type="button" onClick={() => setBusca("")}>Limpar</button>}</div>
          {temas.length > 1 && <div className="emerg__temaLinha"><label htmlFor="tema-emergencia">Filtrar por sistema/tema</label><select id="tema-emergencia" value={tema} onChange={(event) => setTema(event.target.value)}><option value="">Todos os temas ({pacote?.protocolos.length ?? 0})</option>{temas.map(([nome, contagem]) => <option key={nome} value={nome}>{nome} ({contagem})</option>)}</select></div>}
          {pacote && <small aria-live="polite">{protocolosFiltrados.length} de {pacote.protocolos.length} protocolo(s)</small>}
        </div>

        <ul className="emerg__lista">{protocolosFiltrados.map((p) => <li key={p.slug}><button className="emerg__alvo" onClick={() => abrirProtocolo(p.slug)}><strong>{p.titulo}</strong>{p.gatilho && <span>{p.gatilho}</span>}</button></li>)}</ul>
        {pacote && pacote.protocolos.length === 0 && !erro && <p className="emerg__aviso">Nenhum protocolo publicado no modo emergência.</p>}
        {pacote && pacote.protocolos.length > 0 && protocolosFiltrados.length === 0 && <p className="emerg__semResultado">{busca.trim() ? `Nenhum protocolo encontrado para “${busca.trim()}”${tema ? ` em ${tema}` : ""}.` : `Nenhum protocolo encontrado em ${tema}.`}</p>}
      </>}

      {protocolo && doc && (
        <article className="emerg__protocolo emerg-command">
          <button className="emerg__voltar" onClick={() => abrirProtocolo(null)}>← Todos os protocolos</button>
          <div className="emerg-command__layout">
            <main className="emerg-command__main">
              <header className="emerg-command__hero">
                <small><Icone nome="emergencia" /> Emergências</small>
                <h1>{protocolo.titulo}</h1>
                {protocolo.gatilho && <p>{protocolo.gatilho}</p>}
              </header>

              {doc.gaps.length > 0 && <p className="emerg__lacuna">Este protocolo declara {doc.gaps.length} ponto(s) pendente(s) de verificação humana.</p>}

              {diagrama && <section className="emerg__diagrama"><h2>Árvore de decisão</h2><Fluxograma fonte={diagrama} /></section>}

              <div className="emerg-command__steps">
                {blocos.map((s, i) => <section key={i} className="emerg__secao">
                  {s.titulo ? <button className={`emerg__secaoTitulo ${secaoAberta === i ? "aberta" : ""}`} onClick={() => setSecaoAberta(secaoAberta === i ? -1 : i)} aria-expanded={secaoAberta === i}><span className="emerg-command__step-number">{i + 1}</span>{s.titulo}</button> : null}
                  {(secaoAberta === i || !s.titulo) && <div className="emerg__corpo"><Markdown remarkPlugins={[remarkGfm]}>{s.corpo}</Markdown></div>}
                </section>)}
              </div>

              <p className="emerg__origem">{doc.title} · nível de fonte {doc.source_tier} · {doc.review_status}</p>

              {relacionados.length > 0 && (
                <section className="cartao" style={{ marginTop: "0.8rem" }}>
                  <p className="eyebrow">Protocolos e documentos relacionados</p>
                  <div style={{ display: "flex", flexWrap: "wrap", gap: "0.45rem" }}>
                    {relacionados.map((item) => item.tipo === "protocolo" ? (
                      <button
                        type="button"
                        className="chip"
                        key={item.slug}
                        onClick={() => abrirProtocolo(item.slug)}
                      >
                        {item.titulo}
                      </button>
                    ) : (
                      <Link className="chip" key={item.slug} to={`/biblioteca/${item.slug}`}>
                        {item.titulo}
                      </Link>
                    ))}
                  </div>
                </section>
              )}
            </main>

            <aside className="emerg-command__quick" aria-label="Acesso rápido">
              <small>Acesso rápido</small>
              <Link to="/medicamentos"><Icone nome="medicamento" /><span>Drogas</span></Link>
              <Link to="/checklists"><Icone nome="check" /><span>Checklist</span></Link>
              <Link to="/calculadoras"><Icone nome="calculadora" /><span>Escores</span></Link>
              <Link to="/exames"><Icone nome="clinica" /><span>ECG · Achados</span></Link>
              <Link to="/fluxogramas"><Icone nome="seta" /><span>Fluxogramas</span></Link>
              <Link to="/diretrizes"><Icone nome="evidencia" /><span>Diretrizes</span></Link>
            </aside>
          </div>
          <GrafoRelacionados entityType="protocolo_emergencia" slug={protocolo.slug} />
          <footer className="emerg-command__footer"><strong>Emergência é tempo. Aja rápido.</strong><span className="emerg-command__ecg" aria-hidden="true" /></footer>
        </article>
      )}
      {protocolo && !doc && (
        <section className="emerg__erro">
          <p>O documento clínico deste protocolo não está publicado ou não foi encontrado.</p>
          <button type="button" className="emerg__voltar" onClick={() => abrirProtocolo(null)}>
            ← Todos os protocolos
          </button>
        </section>
      )}
    </div>
  );
}
