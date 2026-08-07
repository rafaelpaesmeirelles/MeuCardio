import { useEffect, useMemo, useState } from "react";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { api } from "../lib/api";
import Fluxograma from "../components/Fluxograma";
import "../styles/emergencia.css";

/**
 * Tarefa 15 — Modo Emergência.
 *
 * Três regras que separam esta tela do resto do sistema, e as três vêm do
 * momento em que ela é usada, não de gosto:
 *
 * 1. **Não busca nada depois de aberta.** Todo o pacote — protocolos,
 *    documentos, fluxogramas — chega numa requisição só e fica guardado. Tocar
 *    num protocolo não dispara chamada de rede. Uma tela de emergência que
 *    precisa da rede falha exatamente onde a rede falha: no corredor.
 * 2. **Funciona a partir do que já foi guardado.** Se a requisição falhar, a
 *    tela abre com o último pacote salvo e diz de quando ele é. Melhor um
 *    protocolo de duas semanas atrás, com a data à vista, do que uma tela de
 *    erro.
 * 3. **Contraste e corpo grande, com pouca coisa por vez.** A prioridade é
 *    velocidade de leitura sob estresse. O que estava numa página densa de
 *    consulta vira uma lista de alvos grandes.
 *
 * O conteúdo é o mesmo da biblioteca, sem uma linha própria: o modo é seleção
 * e apresentação. Se um protocolo for corrigido lá, esta tela serve a correção
 * na próxima abertura, porque não tem cópia para envelhecer.
 */

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
  try {
    localStorage.setItem(CACHE, JSON.stringify({ em: Date.now(), pacote: p }));
  } catch {
    // Cota estourada não pode derrubar a tela: quem tem rede segue com o que
    // acabou de chegar, e só perde o benefício do offline.
  }
}

function recuperar(): { em: number; pacote: Pacote } | null {
  try {
    const cru = localStorage.getItem(CACHE);
    return cru ? JSON.parse(cru) : null;
  } catch {
    return null;
  }
}

/** Extrai o bloco ```mermaid``` do corpo, para desenhá-lo antes do texto. */
function fonteMermaid(md: string): string | null {
  const m = md.match(/```mermaid\s*\n([\s\S]*?)```/);
  return m ? m[1].trim() : null;
}

/** Divide o documento em seções de nível 2, para virarem blocos abertos um a um. */
function secoes(md: string): { titulo: string; corpo: string }[] {
  const semDiagrama = md.replace(/```mermaid[\s\S]*?```/g, "");
  const partes = semDiagrama.split(/\n(?=##\s)/);
  return partes
    .map((p) => {
      const m = p.match(/^##\s+(.*)\n?([\s\S]*)$/);
      return m
        ? { titulo: m[1].trim(), corpo: m[2].trim() }
        : { titulo: "", corpo: p.trim() };
    })
    .filter((s) => s.titulo || s.corpo);
}

function normalizarBusca(valor: string): string {
  return valor
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLocaleLowerCase("pt-BR")
    .replace(/\s+/g, " ")
    .trim();
}

export default function Emergencia() {
  const [pacote, setPacote] = useState<Pacote | null>(null);
  const [deCache, setDeCache] = useState<number | null>(null);
  const [erro, setErro] = useState("");
  const [aberto, setAberto] = useState<string | null>(null);
  const [secaoAberta, setSecaoAberta] = useState<number>(0);
  const [busca, setBusca] = useState("");
  // 07/08/2026, pedido do Rafael: toda busca do site precisa de pelo menos
  // duas formas de refinar. Aqui é 100% local — o pacote inteiro já está
  // carregado (regra 1 do offline-first desta tela, acima), então filtrar por
  // tema não dispara rede nenhuma, mesma garantia do texto livre.
  const [tema, setTema] = useState("");

  useEffect(() => {
    const local = recuperar();
    if (local) {
      setPacote(local.pacote);
      setDeCache(local.em);
    }
    api
      .get<Pacote>("/emergencia")
      .then((p) => {
        setPacote(p);
        setDeCache(null);
        guardar(p);
      })
      .catch((e) => {
        if (!local) setErro(e?.message || "Sem conexão e sem cópia guardada.");
      });
  }, []);

  const temas = useMemo(() => {
    const contagem = new Map<string, number>();
    (pacote?.protocolos || []).forEach((p) => {
      const t = pacote?.documentos[p.documento_slug]?.theme;
      if (t) contagem.set(t, (contagem.get(t) ?? 0) + 1);
    });
    return [...contagem.entries()].sort((a, b) => a[0].localeCompare(b[0], "pt-BR"));
  }, [pacote]);

  const protocolosFiltrados = useMemo(() => {
    const protocolos = pacote?.protocolos || [];
    const termos = normalizarBusca(busca).split(" ").filter(Boolean);

    return protocolos.filter((p) => {
      const documento = pacote?.documentos[p.documento_slug];
      if (tema && documento?.theme !== tema) return false;
      if (termos.length === 0) return true;
      const texto = normalizarBusca([
        p.titulo,
        p.gatilho || "",
        documento?.title || "",
        documento?.theme || "",
      ].join(" "));
      return termos.every((termo) => texto.includes(termo));
    });
  }, [busca, tema, pacote]);

  const protocolo = useMemo(
    () => pacote?.protocolos.find((p) => p.slug === aberto) || null,
    [pacote, aberto]
  );
  const doc = protocolo ? pacote?.documentos[protocolo.documento_slug] : null;
  const fluxo = protocolo?.fluxograma_slug
    ? pacote?.documentos[protocolo.fluxograma_slug]
    : null;
  const diagrama = fluxo ? fonteMermaid(fluxo.body_md) : null;
  const blocos = doc ? secoes(doc.body_md) : [];

  return (
    <div className="emerg">
      <header className="emerg__topo">
        <span className="emerg__marca">Modo emergência</span>
        {deCache !== null && (
          <span className="emerg__offline">
            Sem conexão · cópia de {new Date(deCache).toLocaleDateString("pt-BR")}
          </span>
        )}
      </header>

      {erro && (
        <p className="emerg__erro">
          {erro} Abra esta tela uma vez com conexão para que ela fique disponível
          offline.
        </p>
      )}

      {!aberto && (
        <>
          <p className="emerg__aviso">
            Protocolos de risco imediato de vida. O conteúdo é o mesmo da
            biblioteca — aqui ele está filtrado e ampliado para leitura rápida.
          </p>

          <div className="emerg__busca">
            <label htmlFor="busca-emergencia">Buscar assunto</label>
            <div className="emerg__buscaLinha">
              <input
                id="busca-emergencia"
                type="search"
                value={busca}
                onChange={(event) => setBusca(event.target.value)}
                placeholder="Ex.: infarto, choque, arritmia"
                autoComplete="off"
                spellCheck={false}
              />
              {busca && (
                <button type="button" onClick={() => setBusca("")}>
                  Limpar
                </button>
              )}
            </div>
            {temas.length > 1 && (
              <div className="emerg__temaLinha">
                <label htmlFor="tema-emergencia">Filtrar por sistema/tema</label>
                <select id="tema-emergencia" value={tema} onChange={(event) => setTema(event.target.value)}>
                  <option value="">Todos os temas ({pacote?.protocolos.length ?? 0})</option>
                  {temas.map(([nome, contagem]) => (
                    <option key={nome} value={nome}>{nome} ({contagem})</option>
                  ))}
                </select>
              </div>
            )}
            {pacote && (
              <small aria-live="polite">
                {protocolosFiltrados.length} de {pacote.protocolos.length} protocolo(s)
              </small>
            )}
          </div>

          <ul className="emerg__lista">
            {protocolosFiltrados.map((p) => (
              <li key={p.slug}>
                <button
                  className="emerg__alvo"
                  onClick={() => {
                    setAberto(p.slug);
                    setSecaoAberta(0);
                    window.scrollTo(0, 0);
                  }}
                >
                  <strong>{p.titulo}</strong>
                  {p.gatilho && <span>{p.gatilho}</span>}
                </button>
              </li>
            ))}
          </ul>

          {pacote && pacote.protocolos.length === 0 && !erro && (
            <p className="emerg__aviso">Nenhum protocolo publicado no modo emergência.</p>
          )}
          {pacote && pacote.protocolos.length > 0 && protocolosFiltrados.length === 0 && (
            <p className="emerg__semResultado">
              {busca.trim()
                ? `Nenhum protocolo encontrado para “${busca.trim()}”${tema ? ` em ${tema}` : ""}.`
                : `Nenhum protocolo encontrado em ${tema}.`}
            </p>
          )}
        </>
      )}

      {protocolo && doc && (
        <article className="emerg__protocolo">
          <button className="emerg__voltar" onClick={() => setAberto(null)}>
            ← Todos os protocolos
          </button>
          <h1>{protocolo.titulo}</h1>

          {doc.gaps.length > 0 && (
            <p className="emerg__lacuna">
              Este protocolo declara {doc.gaps.length} ponto(s) pendente(s) de
              verificação humana.
            </p>
          )}

          {diagrama && (
            <section className="emerg__diagrama">
              <h2>Árvore de decisão</h2>
              <Fluxograma fonte={diagrama} />
            </section>
          )}

          {blocos.map((s, i) => (
            <section key={i} className="emerg__secao">
              {s.titulo ? (
                <button
                  className={`emerg__secaoTitulo ${secaoAberta === i ? "aberta" : ""}`}
                  onClick={() => setSecaoAberta(secaoAberta === i ? -1 : i)}
                  aria-expanded={secaoAberta === i}
                >
                  {s.titulo}
                </button>
              ) : null}
              {(secaoAberta === i || !s.titulo) && (
                <div className="emerg__corpo">
                  <Markdown remarkPlugins={[remarkGfm]}>{s.corpo}</Markdown>
                </div>
              )}
            </section>
          ))}

          <p className="emerg__origem">
            {doc.title} · nível de fonte {doc.source_tier} · {doc.review_status}
          </p>
        </article>
      )}
    </div>
  );
}
