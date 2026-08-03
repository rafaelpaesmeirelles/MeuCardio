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

export default function Busca() {
  const [params] = useSearchParams();
  const [q, setQ] = useState(params.get("q") ?? "");
  const [res, setRes] = useState<Res[] | null>(null);
  const [buscando, setBuscando] = useState(false);

  async function buscar(termo: string) {
    if (termo.trim().length < 2) return;
    setBuscando(true);
    try {
      const r = await api.get<{ results: Res[] }>(`/search?q=${encodeURIComponent(termo)}`);
      setRes(r.results);
    } finally {
      setBuscando(false);
    }
  }

  useEffect(() => {
    const inicial = params.get("q");
    if (inicial && inicial.trim().length >= 2) buscar(inicial);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <>
      <p className="eyebrow">Busca</p>
      <h1>Procurar em todo o conteúdo</h1>

      <div style={{ display: "flex", gap: 8, margin: "1rem 0 1.4rem", maxWidth: 620 }}>
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && buscar(q)}
          placeholder="anticoagulação em FA, choque cardiogênico, ATP no CDI…"
          aria-label="Termo de busca"
        />
        <button className="botao" onClick={() => buscar(q)} disabled={q.trim().length < 2}>Buscar</button>
      </div>

      {buscando && <Carregando texto="Procurando…" />}

      {!buscando && res !== null && res.length === 0 && (
        <Vazio titulo="Nada encontrado" acao="Tente um termo mais curto ou um sinônimo." />
      )}

      <div className="grade">
        {res?.map((r) => (
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
