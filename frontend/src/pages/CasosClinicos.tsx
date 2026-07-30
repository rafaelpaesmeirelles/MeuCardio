import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";

type Caso = {
  slug: string;
  titulo: string;
  tema: string | null;
  nivel: string | null;
  tentativas: number;
  acertou_na_ultima: boolean | null;
};

export default function CasosClinicos() {
  const [casos, setCasos] = useState<Caso[] | null>(null);

  useEffect(() => {
    api.get<Caso[]>("/casos-clinicos").then(setCasos).catch(() => setCasos([]));
  }, []);

  if (casos === null) return <p>Carregando…</p>;

  return (
    <div>
      <h1>Casos clínicos interativos</h1>
      <p className="subtitulo">
        Um caso, a sua decisão, e depois a conduta correta com a evidência que a sustenta.
      </p>

      {casos.length === 0 ? (
        <p className="curso__vazio">
          Nenhum caso publicado ainda. Eles aparecem aqui depois da revisão.
        </p>
      ) : (
        <div className="painel__funcoes">
          {casos.map((c) => (
            <Link key={c.slug} to={`/casos-clinicos/${c.slug}`} className="cartao painel__funcao">
              <strong>{c.titulo}</strong>
              <span>
                {c.tema}
                {c.nivel && ` · ${c.nivel}`}
              </span>
              {c.tentativas > 0 && (
                <span className="dado">
                  {c.tentativas} tentativa{c.tentativas > 1 ? "s" : ""}
                  {c.acertou_na_ultima !== null &&
                    (c.acertou_na_ultima ? " · última: acertou" : " · última: errou")}
                </span>
              )}
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
