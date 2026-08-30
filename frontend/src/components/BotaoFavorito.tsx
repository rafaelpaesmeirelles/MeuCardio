import { useEffect, useState } from "react";
import { api } from "../lib/api";

type Tipo = "documento" | "medicamento" | "imagem" | "exame" | "evidencia" | "estudo";

export default function BotaoFavorito({ itemType, itemId }: { itemType: Tipo; itemId: number }) {
  const [favoritado, setFavoritado] = useState<boolean | null>(null);
  const [ocupado, setOcupado] = useState(false);
  const [erro, setErro] = useState("");

  useEffect(() => {
    api.get<any[]>("/favorites").then((lista) => {
      setFavoritado(lista.some((f) => f.item_type === itemType && f.item_id === itemId));
    }).catch(() => setFavoritado(false));
  }, [itemType, itemId]);

  async function alternar() {
    if (ocupado) return;
    setOcupado(true); setErro("");
    try {
      if (favoritado) {
        await api.delete(`/favorites/${itemType}/${itemId}`);
        setFavoritado(false);
      } else {
        await api.post("/favorites", { item_type: itemType, item_id: itemId });
        setFavoritado(true);
      }
    } catch {
      setErro("Não foi possível atualizar o favorito.");
    } finally { setOcupado(false); }
  }

  if (favoritado === null) return null;

  return <span className="favorite-control"><button className="botao botao--secundario favorite-control__button" disabled={ocupado} onClick={() => void alternar()} aria-pressed={favoritado}>
    {ocupado ? "Atualizando…" : favoritado ? "★ Favoritado" : "☆ Favoritar"}
  </button>{erro && <small role="status">{erro}</small>}</span>;
}
