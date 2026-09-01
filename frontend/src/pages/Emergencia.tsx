import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { api } from "../lib/api";
import Fluxograma from "../components/Fluxograma";
import Icone from "../components/Icone";
import GrafoRelacionados from "../components/GrafoRelacionados";
import "../styles/emergencia.css";
import "../styles/cardiology-spaces-emergency.css";

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
type SecaoClinica = { titulo: string; corpo: string; numero: number | null };

function pacoteValido(valor: unknown): valor is Pacote {
  if (!valor || typeof valor !== "object") return false;
  const candidato = valor as Partial<Pacote>;
  return Array.isArray(candidato.protocolos)
    && Boolean(candidato.documentos)
    && typeof candidato.documentos === "object"
    && !Array.isArray(candidato.documentos);
}

function guardar(p: Pacote) {
  try { localStorage.setItem(CACHE, JSON.stringify({ em: Date.now(), pacote: p })); } catch { /* offline é melhoria, nunca bloqueio */ }
}
function recuperar(): { em: number; pacote: Pacote } | null {
  try {
    const cru = localStorage.getItem(CACHE);
    if (!cru) return null;
    const salvo = JSON.parse(cru) as { em?: unknown; pacote?: unknown };
    if (typeof salvo.em !== "number" || !pacoteValido(salvo.pacote)) {
      localStorage.removeItem(CACHE);
      return null;
    }
    return { em: salvo.em, pacote: salvo.pacote };
  } catch {
    try { localStorage.removeItem(CACHE); } catch { /* armazenamento indisponível */ }
    return null;
  }
}
function fonteMermaid(md: string): string | null {
  const m = md.match(/```mermaid\s*\n([\s\S]*?)```/); return m ? m[1].trim() : null;
}
function secoes(md: string): SecaoClinica[] {
  const semDiagrama = md.replace(/```mermaid[\s\S]*?```/g, "");
  let numero = 0;
  return semDiagrama.split(/\n(?=##\s)/).map((p) => {
    const m = p.match(/^##\s+(.*)\n?([\s\S]*)$/);
    const secao = m ? { titulo: m[1].trim(), corpo: m[2].trim() } : { titulo: "", corpo: p.trim() };
    return { ...secao, numero: secao.titulo ? ++numero : null };
  }).filter((s) => s.titulo || s.corpo);
}
function normalizarBusca(valor: string): string {
  return valor.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLocaleLowerCase("pt-BR").replace(/\s+/g, " ").trim();
}

export default function Emergencia() {
  const emergRootRef = useRef<HTMLDivElement>(null);
  const detailTitleRef = useRef<HTMLHeadingElement>(null);
  const [params, setParams] = useSearchParams();
  const [pacote, setPacote] = useState<Pacote | null>(null);
  const [deCache, setDeCache] = useState<number | null>(null);
  const [erro, setErro] = useState("");
  const [secaoAberta, setSecaoAberta] = useState<number>(-1);
  const [busca, setBusca] = useState("");
  const [tema, setTema] = useState("");
  const [carregando, setCarregando] = useState(true);

  const carregar = useCallback(() => {
    const local = recuperar();
    if (local) { setPacote(local.pacote); setDeCache(local.em); }
    setCarregando(true);
    setErro("");
    api.get<unknown>("/emergencia").then((resposta) => {
      if (!pacoteValido(resposta)) throw new Error("A resposta do Modo Emergência não possui o formato esperado.");
      setPacote(resposta);
      setDeCache(null);
      guardar(resposta);
    }).catch((e) => {
      if (!local) setErro(e?.message || "Sem conexão e sem cópia guardada.");
    }).finally(() => setCarregando(false));
  }, []);

  useEffect(() => {
    carregar();
  }, [carregar]);

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
    const contentScroller = emergRootRef.current?.closest<HTMLElement>(".cv-content");
    if (contentScroller) contentScroller.scrollTo({ top: 0, left: 0, behavior: "auto" });
    else window.scrollTo({ top: 0, left: 0, behavior: "auto" });
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
  useEffect(() => {
    setSecaoAberta(blocos.findIndex((secao) => Boolean(secao.titulo)));
  }, [doc?.body_md, protocolo?.slug]);
  useEffect(() => {
    if (!protocolo?.slug) return;
    const frame = window.requestAnimationFrame(() => detailTitleRef.current?.focus({ preventScroll: true }));
    return () => window.cancelAnimationFrame(frame);
  }, [protocolo?.slug]);
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
    <div ref={emergRootRef} className={`emerg ${protocolo ? "emerg--detail" : "emerg--catalog"}`}>
      <header className="emerg__topo">
        <div className="emerg__mode">
          <span className="emerg__modeIcon"><Icone nome="emergencia" /></span>
          <span><small>HOSPITAL · RESPOSTA IMEDIATA</small><strong>Modo Emergência</strong></span>
        </div>
        <div className="emerg__status" aria-live="polite">
          {pacote && deCache === null && <span className="emerg__online"><i />Conteúdo atualizado</span>}
          {deCache !== null && <span className="emerg__offline"><i />Sem conexão · cópia de {new Date(deCache).toLocaleDateString("pt-BR")}</span>}
        </div>
      </header>

      {erro && (
        <section className="emerg__erro" role="alert">
          <Icone nome="emergencia" />
          <span><strong>Não foi possível abrir os protocolos.</strong><small>{erro} Abra esta tela uma vez com conexão para que ela fique disponível offline.</small></span>
          <button type="button" onClick={carregar}>Tentar novamente</button>
        </section>
      )}

      {!protocolo && <>
        {protocoloInvalido && (
          <p className="emerg__erro emerg__erro--compact">O protocolo solicitado não está publicado ou não existe.</p>
        )}

        <section className="emerg__command" aria-labelledby="emerg-command-title">
          <div className="emerg__commandCopy">
            <p>RECONHECER · LOCALIZAR · AGIR</p>
            <h1 id="emerg-command-title">Qual emergência você precisa conduzir agora?</h1>
            <span className="emerg__aviso">Protocolos de risco imediato de vida. O conteúdo é o mesmo da biblioteca — filtrado e ampliado para leitura rápida.</span>
          </div>
          <div className="emerg__signal" aria-hidden="true"><span /><i /><b /><em /></div>

          <div className="emerg__busca" role="search" aria-label="Localizar protocolo de emergência">
            <label className="emerg__searchField" htmlFor="busca-emergencia">
              <span>Buscar assunto</span>
              <div className="emerg__buscaLinha"><Icone nome="busca" /><input id="busca-emergencia" type="search" value={busca} onChange={(event) => setBusca(event.target.value)} placeholder="Ex.: infarto, choque, arritmia" autoComplete="off" spellCheck={false} />{busca && <button type="button" onClick={() => setBusca("")}>Limpar</button>}</div>
            </label>
            {temas.length > 1 && <label className="emerg__temaLinha" htmlFor="tema-emergencia"><span>Sistema ou tema</span><select id="tema-emergencia" value={tema} onChange={(event) => setTema(event.target.value)}><option value="">Todos os temas ({pacote?.protocolos.length ?? 0})</option>{temas.map(([nome, contagem]) => <option key={nome} value={nome}>{nome} ({contagem})</option>)}</select></label>}
            <div className="emerg__resultCount" aria-live="polite"><strong>{protocolosFiltrados.length}</strong><span>de {pacote?.protocolos.length ?? 0}<small>protocolos</small></span></div>
          </div>
        </section>

        <section className="emerg__protocols" aria-labelledby="emerg-protocols-title">
          <header><div><p>CONDUTAS DE TEMPO CRÍTICO</p><h2 id="emerg-protocols-title">Acesso imediato</h2></div><span>{tema || "Todos os sistemas"}</span></header>
          {carregando && !pacote && <div className="emerg__loading" role="status"><i /><strong>Abrindo protocolos de emergência…</strong></div>}
          <ul className="emerg__lista">{protocolosFiltrados.map((p, index) => <li key={p.slug}><button className="emerg__alvo" onClick={() => abrirProtocolo(p.slug)}><span className="emerg__alvoNumber">{String(index + 1).padStart(2, "0")}</span><span className="emerg__alvoCopy"><strong>{p.titulo}</strong>{p.gatilho && <span>{p.gatilho}</span>}</span><Icone nome="seta" /></button></li>)}</ul>
          {pacote && pacote.protocolos.length === 0 && !erro && <p className="emerg__semResultado">Nenhum protocolo publicado no modo emergência.</p>}
          {pacote && pacote.protocolos.length > 0 && protocolosFiltrados.length === 0 && <p className="emerg__semResultado">{busca.trim() ? `Nenhum protocolo encontrado para “${busca.trim()}”${tema ? ` em ${tema}` : ""}.` : `Nenhum protocolo encontrado em ${tema}.`}</p>}
        </section>

        <footer className="emerg__safety">
          <span><Icone nome="check" /><strong>Conteúdo publicado</strong><small>Mesma base da biblioteca</small></span>
          <span><Icone nome="evidencia" /><strong>Fonte e revisão</strong><small>Proveniência visível no protocolo</small></span>
          <span><Icone nome="sincronizar" /><strong>Continuidade offline</strong><small>Cópia local após o primeiro acesso</small></span>
        </footer>
      </>}

      {protocolo && doc && (
        <article className="emerg__protocolo emerg-command">
          <button type="button" className="emerg__voltar" onClick={() => abrirProtocolo(null)}><Icone nome="seta" />Todos os protocolos</button>
          <header className="emerg-command__hero">
            <div className="emerg-command__heroCopy">
              <small><Icone nome="emergencia" /> PROTOCOLO DE TEMPO CRÍTICO</small>
              <h1 id="emerg-protocol-title" ref={detailTitleRef} tabIndex={-1}>{protocolo.titulo}</h1>
              {protocolo.gatilho && <p>{protocolo.gatilho}</p>}
            </div>
            <div className="emerg-command__trust" aria-label="Proveniência resumida">
              <span><small>Nível de fonte</small><strong>{doc.source_tier}</strong></span>
              <span><small>Status editorial</small><strong>{doc.review_status}</strong></span>
            </div>
          </header>

          <div className="emerg-command__layout">
            <section className="emerg-command__main" aria-labelledby="emerg-protocol-title">
              {doc.gaps.length > 0 && <p className="emerg__lacuna">Este protocolo declara {doc.gaps.length} ponto(s) pendente(s) de verificação humana.</p>}

              {diagrama && <section className="emerg__diagrama"><h2>Árvore de decisão</h2><Fluxograma fonte={diagrama} /></section>}

              <section className="emerg-command__steps" aria-label="Conduta clínica em etapas">
                {blocos.map((s, i) => <section key={i} className={`emerg__secao ${s.titulo ? "emerg__secao--step" : "emerg__secao--intro"}`}>
                  {s.titulo ? <h2 className="emerg__secaoHeading"><button type="button" id={`emerg-step-trigger-${i}`} className={`emerg__secaoTitulo ${secaoAberta === i ? "aberta" : ""}`} onClick={() => setSecaoAberta(secaoAberta === i ? -1 : i)} aria-expanded={secaoAberta === i} aria-controls={`emerg-step-panel-${i}`}><span className="emerg-command__step-number">{String(s.numero).padStart(2, "0")}</span><span>{s.titulo}</span></button></h2> : null}
                  <div id={s.titulo ? `emerg-step-panel-${i}` : undefined} aria-labelledby={s.titulo ? `emerg-step-trigger-${i}` : undefined} hidden={s.titulo ? secaoAberta !== i : undefined} className="emerg__corpo"><Markdown remarkPlugins={[remarkGfm]} components={{ h1: ({ children }) => <h2 className="emerg__markdownTitle">{children}</h2> }}>{s.corpo}</Markdown></div>
                </section>)}
              </section>

              <section className="emerg-command__provenance" aria-labelledby="emerg-provenance-title">
                <header><p>PROVENIÊNCIA CLÍNICA</p><h2 id="emerg-provenance-title">Fonte e revisão</h2></header>
                <dl>
                  <div><dt>Nível de fonte</dt><dd>{doc.source_tier}</dd></div>
                  <div><dt>Status editorial</dt><dd>{doc.review_status}</dd></div>
                </dl>
                <p className="emerg__origem">{doc.title} · nível de fonte {doc.source_tier} · {doc.review_status}</p>
                {doc.source_refs.length > 0 && <details><summary><span>Fontes registradas</span><strong>{doc.source_refs.length}</strong></summary><ol>{doc.source_refs.map((fonte, index) => <li key={`${index}-${fonte}`}>{fonte}</li>)}</ol></details>}
              </section>

              {relacionados.length > 0 && (
                <section className="emerg__related">
                  <p className="eyebrow">Protocolos e documentos relacionados</p>
                  <div className="emerg__relatedLinks">
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
            </section>

            <aside className="emerg-command__quick" aria-label="Acesso rápido">
              <small>ACESSO RÁPIDO</small>
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
          <button type="button" className="emerg__voltar" onClick={() => abrirProtocolo(null)}><Icone nome="seta" />Todos os protocolos</button>
        </section>
      )}
    </div>
  );
}
