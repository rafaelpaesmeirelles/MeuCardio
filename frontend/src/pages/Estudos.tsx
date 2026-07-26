import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import { Carregando, Vazio } from "../components/Estado";

type Item = { slug: string; title: string; study_type: string; journal: string; year: number; theme: string };

const RÓTULO_TIPO: Record<string, string> = {
  ensaio_clinico: "Ensaio clínico", revisao_sistematica: "Revisão sistemática",
  metanalise: "Metanálise", consenso: "Consenso", coorte: "Coorte", caso_controle: "Caso-controle",
};

export default function Estudos() {
  const [tipos, setTipos] = useState<{ study_type: string; count: number }[]>([]);
  const [tipo, setTipo] = useState("");
  const [busca, setBusca] = useState("");
  const [itens, setItens] = useState<Item[] | null>(null);

  useEffect(() => { api.get<{ study_type: string; count: number }[]>("/studies/types").then(setTipos); }, []);

  useEffect(() => {
    setItens(null);
    const atraso = setTimeout(() => {
      const qs = new URLSearchParams();
      if (tipo) qs.set("study_type", tipo);
      if (busca.trim()) qs.set("q", busca.trim());
      api.get<{ items: Item[] }>(`/studies?${qs}`).then((r) => setItens(r.items));
    }, 250);
    return () => clearTimeout(atraso);
  }, [tipo, busca]);

  return (
    <>
      <p className="eyebrow">Estudos</p>
      <h1>Trabalhos científicos</h1>
      <p style={{ color: "var(--cinza-texto)", maxWidth: "60ch" }}>
        Ensaios clínicos, revisões sistemáticas e metanálises — resumo, principais achados e implicação clínica.
      </p>

      <input value={busca} onChange={(e) => setBusca(e.target.value)}
             placeholder="Buscar por título — ex.: DAPA-HF, EMPEROR…" aria-label="Buscar estudo"
             style={{ maxWidth: 420, marginTop: "0.8rem" }} />

      <div style={{ display: "flex", gap: 6, flexWrap: "wrap", margin: "0.8rem 0 1.2rem" }}>
        <button className={`botao ${tipo ? "botao--secundario" : ""}`}
                style={{ padding: "0.35rem 0.75rem", fontSize: "0.82rem" }} onClick={() => setTipo("")}>
          Todos
        </button>
        {tipos.map((t) => (
          <button key={t.study_type} className={`botao ${tipo === t.study_type ? "" : "botao--secundario"}`}
                  style={{ padding: "0.35rem 0.75rem", fontSize: "0.82rem" }} onClick={() => setTipo(t.study_type)}>
            {RÓTULO_TIPO[t.study_type] ?? t.study_type} ({t.count})
          </button>
        ))}
      </div>

      {itens === null ? (
        <Carregando />
      ) : itens.length === 0 ? (
        <Vazio titulo="Nenhum estudo encontrado" acao="Tente outro termo ou tipo." />
      ) : (
        <div className="grade grade--2">
          {itens.map((s) => (
            <Link key={s.slug} to={`/estudos/${s.slug}`} className="cartao" style={{ textDecoration: "none" }}>
              <p className="eyebrow">{RÓTULO_TIPO[s.study_type] ?? s.study_type} · {s.year}</p>
              <strong>{s.title}</strong>
              <div style={{ fontSize: "0.82rem", color: "var(--cinza-texto)", marginTop: 4 }}>{s.journal}</div>
            </Link>
          ))}
        </div>
      )}
    </>
  );
}
