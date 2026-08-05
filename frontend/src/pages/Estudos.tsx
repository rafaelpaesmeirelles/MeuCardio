import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import { Carregando, Vazio } from "../components/Estado";
import { areaDaCardiologia } from "../lib/taxonomiaCardiologia";

type Item = { slug: string; title: string; study_type: string; journal: string; year: number; theme: string };

// `estudo_de_coorte` é o valor que os JSON usam de fato — `coorte` estava no mapa
// mas não existe nos dados, e sem esta linha o filtro aparecia ao assinante como
// "estudo_de_coorte", com underscore. O rótulo é "Estudo observacional" porque o
// grupo reúne coortes e estudos transversais; chamá-lo de "Coorte" classificaria
// errado os transversais.
const RÓTULO_TIPO: Record<string, string> = {
  ensaio_clinico: "Ensaio clínico", revisao_sistematica: "Revisão sistemática",
  metanalise: "Metanálise", consenso: "Consenso", coorte: "Coorte", caso_controle: "Caso-controle",
  estudo_de_coorte: "Estudo observacional",
};

export default function Estudos() {
  const [tipos, setTipos] = useState<{ study_type: string; count: number }[]>([]);
  const [tipo, setTipo] = useState("");
  const [temas, setTemas] = useState<{ theme: string; count: number }[]>([]);
  const [tema, setTema] = useState("");
  const [area, setArea] = useState("");
  const [busca, setBusca] = useState("");
  const [itens, setItens] = useState<Item[] | null>(null);

  useEffect(() => {
    Promise.all([
      api.get<{ study_type: string; count: number }[]>("/studies/types"),
      api.get<{ theme: string; count: number }[]>("/studies/themes"),
    ]).then(([tiposResposta, temasResposta]) => {
      setTipos(tiposResposta);
      setTemas(temasResposta);
    });
  }, []);

  useEffect(() => {
    setItens(null);
    const atraso = setTimeout(() => {
      const qs = new URLSearchParams();
      if (tipo) qs.set("study_type", tipo);
      if (tema) qs.set("theme", tema);
      if (busca.trim()) qs.set("q", busca.trim());
      qs.set("limit", "500");
      api.get<{ items: Item[] }>(`/studies?${qs}`).then((r) => setItens(r.items));
    }, 250);
    return () => clearTimeout(atraso);
  }, [tipo, tema, busca]);

  const areas = useMemo(() => {
    const agrupadas = new Map<string, { id: string; label: string; count: number }>();
    temas.forEach((item) => {
      const encontrada = areaDaCardiologia(item.theme);
      const atual = agrupadas.get(encontrada.id);
      agrupadas.set(encontrada.id, { id: encontrada.id, label: encontrada.label, count: (atual?.count ?? 0) + item.count });
    });
    return [...agrupadas.values()].sort((a, b) => a.label.localeCompare(b.label, "pt-BR"));
  }, [temas]);

  const visiveis = useMemo(() => {
    if (!itens) return null;
    return itens.filter((item) => !area || areaDaCardiologia(item.theme, item.title).id === area);
  }, [itens, area]);

  return (
    <>
      <p className="eyebrow">Estudos</p>
      <h1>Trabalhos científicos</h1>
      <p style={{ color: "var(--texto-secundario)", maxWidth: "60ch" }}>
        Ensaios clínicos, revisões sistemáticas e metanálises — resumo, principais achados e implicação clínica.
      </p>

      <section className="filtros-conteudo filtros-conteudo--3">
        <label><strong>Buscar estudo ou patologia</strong><input value={busca} onChange={(e) => setBusca(e.target.value)} placeholder="Ex.: DAPA-HF, fibrilação atrial, insuficiência cardíaca…" aria-label="Buscar estudo" /></label>
        <label><strong>Área da Cardiologia</strong><select value={area} onChange={(e) => setArea(e.target.value)}><option value="">Todas as áreas</option>{areas.map((item) => <option key={item.id} value={item.id}>{item.label} ({item.count})</option>)}</select></label>
        <label><strong>Patologia ou assunto</strong><select value={tema} onChange={(e) => setTema(e.target.value)}><option value="">Todas as patologias</option>{temas.map((item) => <option key={item.theme} value={item.theme}>{item.theme} ({item.count})</option>)}</select></label>
      </section>

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

      {visiveis === null ? (
        <Carregando />
      ) : visiveis.length === 0 ? (
        <Vazio titulo="Nenhum estudo encontrado" acao="Tente outro termo, área, patologia ou tipo de estudo." />
      ) : (
        <div className="grade grade--2">
          {visiveis.map((s) => (
            <Link key={s.slug} to={`/estudos/${s.slug}`} className="cartao" style={{ textDecoration: "none" }}>
              <p className="eyebrow">{areaDaCardiologia(s.theme, s.title).label} · {s.theme}</p>
              <strong>{s.title}</strong>
              <div style={{ fontSize: "0.82rem", color: "var(--texto-secundario)", marginTop: 4 }}>{RÓTULO_TIPO[s.study_type] ?? s.study_type} · {s.journal} · {s.year}</div>
            </Link>
          ))}
        </div>
      )}
    </>
  );
}
