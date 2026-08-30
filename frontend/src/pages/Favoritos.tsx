import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, ApiError } from "../lib/api";
import { Carregando, Erro, Vazio } from "../components/Estado";
import Icone from "../components/Icone";

type Favorito = { id: number; item_type: string; item_id: number; title: string; url: string; meta: string };

const RÓTULO: Record<string, string> = {
  documento: "Biblioteca", medicamento: "Medicamento", imagem: "Galeria",
  exame: "Exames", evidencia: "Evidências", estudo: "Estudos",
};

export default function Favoritos() {
  const [itens, setItens] = useState<Favorito[] | null>(null);
  const [filtro, setFiltro] = useState("todos");
  const [removendo, setRemovendo] = useState<string | null>(null);
  const [erro, setErro] = useState("");

  const recarregar = () => api.get<Favorito[]>("/favorites").then((lista) => { setItens(lista); setErro(""); }).catch((e) => setErro(e instanceof ApiError ? e.message : "Não foi possível carregar seus favoritos."));
  useEffect(() => { recarregar(); }, []);

  async function remover(f: Favorito) {
    const chave = `${f.item_type}-${f.item_id}`;
    setRemovendo(chave); setErro("");
    try {
      await api.delete(`/favorites/${f.item_type}/${f.item_id}`);
      setItens((atuais) => atuais?.filter((item) => item.item_type !== f.item_type || item.item_id !== f.item_id) ?? []);
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Não foi possível remover o favorito.");
    } finally { setRemovendo(null); }
  }

  const tipos = Array.from(new Set((itens ?? []).map((item) => item.item_type)));
  const visiveis = filtro === "todos" ? (itens ?? []) : (itens ?? []).filter((item) => item.item_type === filtro);

  return (
    <section className="favorites-page">
      <header className="favorites-page__hero"><div><p className="eyebrow">Contexto pessoal</p><h1>Favoritos</h1><p>Referências clínicas salvas para retomar sem perder o contexto.</p></div><Link className="botao botao--secundario" to="/busca"><Icone nome="busca" /> Buscar conteúdo</Link></header>

      {erro && <Erro mensagem={erro} />}
      {itens === null ? (
        !erro ? <Carregando /> : null
      ) : itens.length === 0 ? (
        <div className="favorites-page__empty"><Vazio titulo="Nenhum favorito ainda" acao="Abra um documento, medicamento, exame, evidência, estudo ou imagem e use Favoritar." /><Link className="botao" to="/busca">Explorar Tudo com Tudo</Link></div>
      ) : (
        <><nav className="favorites-page__filters" aria-label="Filtrar favoritos"><button type="button" className={filtro === "todos" ? "is-active" : ""} aria-pressed={filtro === "todos"} onClick={() => setFiltro("todos")}>Todos · {itens.length}</button>{tipos.map((tipo) => { const total = itens.filter((item) => item.item_type === tipo).length; return <button type="button" key={tipo} className={filtro === tipo ? "is-active" : ""} aria-pressed={filtro === tipo} onClick={() => setFiltro(tipo)}>{RÓTULO[tipo] ?? tipo} · {total}</button>; })}</nav>
        <div className="favorites-page__grid">
          {visiveis.map((f) => { const chave = `${f.item_type}-${f.item_id}`; return <article key={`${f.item_type}-${f.id}`} className="cartao favorites-card"><span className="favorites-card__icon"><Icone nome="favorito" /></span><div><p className="eyebrow">{RÓTULO[f.item_type] ?? f.item_type}{f.meta ? ` · ${f.meta}` : ""}</p><Link to={f.url}><strong>{f.title}</strong></Link></div><button className="favorites-card__remove" disabled={removendo === chave} onClick={() => void remover(f)} aria-label={`Remover ${f.title} dos favoritos`}>{removendo === chave ? "…" : "✕"}</button></article>; })}
        </div></>
      )}
    </section>
  );
}
