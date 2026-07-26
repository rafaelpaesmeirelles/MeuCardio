import { useEffect, useState } from "react";
import { api } from "../lib/api";

type Tipo = "documento" | "medicamento" | "imagem" | "exame" | "evidencia" | "estudo";

export default function BotaoFavorito({ itemType, itemId }: { itemType: Tipo; itemId: number }) {
  const [favoritado, setFavoritado] = useState<boolean | null>(null);

  useEffect(() => {
    api.get<any[]>("/favorites").then((lista) => {
      setFavoritado(lista.some((f) => f.item_type === itemType && f.item_id === itemId));
    }).catch(() => setFavoritado(false));
  }, [itemType, itemId]);

  async function alternar() {
    if (favoritado) {
      await api.delete(`/favorites/${itemType}/${itemId}`);
      setFavoritado(false);
    } else {
      await api.post("/favorites", { item_type: itemType, item_id: itemId });
      setFavoritado(true);
    }
  }

  if (favoritado === null) return null;

  return (
    <button
      className="botao botao--secundario"
      onClick={alternar}
      aria-pressed={favoritado}
      style={{ padding: "0.35rem 0.75rem", fontSize: "0.86rem" }}
    >
      {favoritado ? "★ Favoritado" : "☆ Favoritar"}
    </button>
  );
}
