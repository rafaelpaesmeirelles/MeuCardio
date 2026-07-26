import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import { Carregando, Vazio } from "../components/Estado";

type Favorito = { id: number; item_type: string; item_id: number; title: string; url: string; meta: string };

const RÓTULO: Record<string, string> = {
  documento: "Biblioteca", medicamento: "Medicamento", imagem: "Galeria",
  exame: "Exames", evidencia: "Evidências", estudo: "Estudos",
};

export default function Favoritos() {
  const [itens, setItens] = useState<Favorito[] | null>(null);

  const recarregar = () => api.get<Favorito[]>("/favorites").then(setItens);
  useEffect(() => { recarregar(); }, []);

  async function remover(f: Favorito) {
    await api.delete(`/favorites/${f.item_type}/${f.item_id}`);
    recarregar();
  }

  return (
    <>
      <p className="eyebrow">Favoritos</p>
      <h1>Seus itens salvos</h1>

      {itens === null ? (
        <Carregando />
      ) : itens.length === 0 ? (
        <Vazio titulo="Nenhum favorito ainda" acao="Marque documentos, medicamentos ou imagens com a estrela." />
      ) : (
        <div className="grade" style={{ marginTop: "1rem" }}>
          {itens.map((f) => (
            <div key={`${f.item_type}-${f.id}`} className="cartao" style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <div style={{ flex: 1 }}>
                <p className="eyebrow" style={{ margin: 0 }}>{RÓTULO[f.item_type] ?? f.item_type} · {f.meta}</p>
                <Link to={f.url}><strong>{f.title}</strong></Link>
              </div>
              <button className="botao botao--secundario" style={{ padding: "0.3rem 0.6rem" }}
                      onClick={() => remover(f)} aria-label="Remover dos favoritos">
                ✕
              </button>
            </div>
          ))}
        </div>
      )}
    </>
  );
}
