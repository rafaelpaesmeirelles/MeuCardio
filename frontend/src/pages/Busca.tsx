import { useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import { Carregando, Vazio } from "../components/Estado";

type Res = { slug: string; title: string; kind: string; theme: string; snippet: string };

export default function Busca() {
  const [q, setQ] = useState("");
  const [res, setRes] = useState<Res[] | null>(null);
  const [buscando, setBuscando] = useState(false);

  async function buscar() {
    if (q.trim().length < 2) return;
    setBuscando(true);
    try {
      const r = await api.get<{ results: Res[] }>(`/search?q=${encodeURIComponent(q)}`);
      setRes(r.results);
    } finally {
      setBuscando(false);
    }
  }

  return (
    <>
      <p className="eyebrow">Busca</p>
      <h1>Procurar em todo o conteúdo</h1>

      <div style={{ display: "flex", gap: 8, margin: "1rem 0 1.4rem", maxWidth: 620 }}>
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && buscar()}
          placeholder="anticoagulação em FA, choque cardiogênico, ATP no CDI…"
          aria-label="Termo de busca"
        />
        <button className="botao" onClick={buscar} disabled={q.trim().length < 2}>Buscar</button>
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
            <p
              style={{ color: "var(--texto-secundario)", fontSize: "0.88rem", margin: 0 }}
              dangerouslySetInnerHTML={{ __html: r.snippet }}
            />
          </Link>
        ))}
      </div>
    </>
  );
}
