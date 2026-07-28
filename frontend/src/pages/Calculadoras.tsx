import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import { Carregando, SeloRevisao } from "../components/Estado";

type Calc = { slug: string; name: string; theme: string; purpose: string; status: string };

export default function Calculadoras() {
  const [lista, setLista] = useState<Calc[] | null>(null);
  useEffect(() => { api.get<Calc[]>("/calculators").then(setLista); }, []);

  if (!lista) return <Carregando />;

  return (
    <>
      <p className="eyebrow">Escores clínicos</p>
      <h1>Calculadoras</h1>
      <p style={{ color: "var(--texto-secundario)", maxWidth: "60ch" }}>
        Cada escore mostra a referência original e as limitações de aplicação. Escores cujos
        coeficientes oficiais ainda não foram conferidos ficam bloqueados até a validação.
      </p>

      <div className="grade grade--2" style={{ marginTop: "1.2rem" }}>
        {lista.map((c) => {
          const liberada = c.status === "implementada";
          const corpo = (
            <>
              <p className="eyebrow">{c.theme}</p>
              <h3>{c.name}</h3>
              <p style={{ color: "var(--texto-secundario)", fontSize: "0.88rem" }}>{c.purpose}</p>
              {!liberada && <SeloRevisao status={c.status} />}
            </>
          );
          return liberada ? (
            <Link key={c.slug} to={`/calculadoras/${c.slug}`} className="cartao cartao--clinico"
                  style={{ color: "inherit" }}>{corpo}</Link>
          ) : (
            <div key={c.slug} className="cartao" style={{ opacity: 0.7 }}>{corpo}</div>
          );
        })}
      </div>
    </>
  );
}
