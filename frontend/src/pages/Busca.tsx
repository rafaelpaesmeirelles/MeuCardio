import { useEffect, useState, type ReactNode } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api } from "../lib/api";
import { Carregando, Vazio } from "../components/Estado";

type Res = { slug: string; title: string; kind: string; theme: string; snippet: string };

function SnippetDestacado({ snippet }: { snippet: string }) {
  const partes = snippet.split(/(<mark>|<\/mark>)/gi);
  let destacado = false;
  const nos: ReactNode[] = [];

  partes.forEach((parte, indice) => {
    if (/^<mark>$/i.test(parte)) {
      destacado = true;
      return;
    }
    if (/^<\/mark>$/i.test(parte)) {
      destacado = false;
      return;
    }
    if (!parte) return;

    // Todo o texto vindo do banco continua como texto React escapado. Somente
    // os delimitadores exatos <mark> gerados pelo PostgreSQL ganham estilo.
    nos.push(
      destacado ? <mark key={indice}>{parte}</mark> : <span key={indice}>{parte}</span>,
    );
  });

  return <>{nos}</>;
}

const RÓTULO_KIND: Record<string, string> = {
  documento: "Documento", estudo: "Estudo", fluxograma: "Fluxograma", protocolo: "Protocolo",
};

export default function Busca() {
  const [params] = useSearchParams();
  const [q, setQ] = useState(params.get("q") ?? "");
  const [res, setRes] = useState<Res[] | null>(null);
  const [buscando, setBuscando] = useState(false);
  // 07/08/2026, pedido do Rafael: toda ferramenta de busca do site precisa de
  // pelo menos duas formas de refinar — aqui, além do termo livre, filtrar
  // pelo tipo de conteúdo (`kind`) já presente nos próprios resultados. Sem
  // rota nova no backend: o filtro é sobre o que já veio, client-side.
  const [tipo, setTipo] = useState("");

  async function buscar(termo: string) {
    if (termo.trim().length < 2) return;
    setBuscando(true);
    try {
      const r = await api.get<{ results: Res[] }>(`/search?q=${encodeURIComponent(termo)}`);
      setRes(r.results);
      setTipo("");
    } finally {
      setBuscando(false);
    }
  }

  useEffect(() => {
    const inicial = params.get("q");
    if (inicial && inicial.trim().length >= 2) buscar(inicial);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const tipos = Array.from(new Set((res ?? []).map((r) => r.kind))).sort();
  const resultados = tipo ? (res ?? []).filter((r) => r.kind === tipo) : res;

  return (
    <>
      <p className="eyebrow">Busca</p>
      <h1>Procurar em todo o conteúdo</h1>

      <div style={{ display: "flex", gap: 8, margin: "1rem 0 1.4rem", maxWidth: 620, flexWrap: "wrap" }}>
        <input
          style={{ flex: 1, minWidth: 240 }}
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && buscar(q)}
          placeholder="anticoagulação em FA, choque cardiogênico, ATP no CDI…"
          aria-label="Termo de busca"
        />
        <button className="botao" onClick={() => buscar(q)} disabled={q.trim().length < 2}>Buscar</button>
      </div>

      {!buscando && tipos.length > 1 && (
        <label style={{ display: "block", maxWidth: 260, margin: "0 0 1rem" }}>
          Tipo de conteúdo
          <select value={tipo} onChange={(e) => setTipo(e.target.value)}>
            <option value="">Todos os tipos ({res?.length ?? 0})</option>
            {tipos.map((k) => (
              <option key={k} value={k}>
                {RÓTULO_KIND[k] ?? k} ({(res ?? []).filter((r) => r.kind === k).length})
              </option>
            ))}
          </select>
        </label>
      )}

      {buscando && <Carregando texto="Procurando…" />}

      {!buscando && res !== null && res.length === 0 && (
        <Vazio titulo="Nada encontrado" acao="Tente um termo mais curto ou um sinônimo." />
      )}

      <div className="grade">
        {resultados?.map((r) => (
          <Link key={r.slug} to={`/biblioteca/${r.slug}`} className="cartao" style={{ color: "inherit" }}>
            <p className="eyebrow">{r.theme} · {r.kind}</p>
            <h3>{r.title}</h3>
            <p style={{ color: "var(--texto-secundario)", fontSize: "0.88rem", margin: 0 }}>
              <SnippetDestacado snippet={r.snippet} />
            </p>
          </Link>
        ))}
      </div>
    </>
  );
}
