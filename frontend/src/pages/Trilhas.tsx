import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";

type Trilha = {
  slug: string;
  titulo: string;
  tema: string | null;
  objetivo: string | null;
  nivel: string | null;
  total_etapas: number;
  concluidas: number;
  finalizada_em: string | null;
};

export default function Trilhas() {
  const [ts, setTs] = useState<Trilha[] | null>(null);

  useEffect(() => {
    api.get<Trilha[]>("/api/trilhas").then(setTs).catch(() => setTs([]));
  }, []);

  if (ts === null) return <p>Carregando…</p>;

  return (
    <div>
      <h1>Trilhas de estudo</h1>
      <p className="subtitulo">
        Sequências guiadas do conteúdo que já está na plataforma. Cada etapa diz por
        que vem naquele ponto — a trilha organiza, não repete.
      </p>

      {ts.length === 0 ? (
        <p className="curso__vazio">
          Nenhuma trilha publicada ainda. Elas aparecem aqui depois da revisão.
        </p>
      ) : (
        <div className="painel__funcoes">
          {ts.map((t) => {
            const pct = t.total_etapas ? Math.round((t.concluidas / t.total_etapas) * 100) : 0;
            return (
              <Link key={t.slug} to={`/trilhas/${t.slug}`} className="cartao painel__funcao">
                <strong>{t.titulo}</strong>
                <span>{t.objetivo}</span>
                <span className="trilha__barra" aria-label={`${pct}% concluído`}>
                  <span style={{ width: `${pct}%` }} />
                </span>
                <span className="dado">
                  {t.concluidas}/{t.total_etapas} etapas
                  {t.finalizada_em && " · concluída"}
                </span>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
