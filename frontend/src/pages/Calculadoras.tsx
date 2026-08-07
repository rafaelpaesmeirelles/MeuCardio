import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import { Carregando, SeloRevisao } from "../components/Estado";

type Calc = { slug: string; name: string; theme: string; purpose: string; status: string; kind: string };

const PREFIXO_DOSE = "Doses — ";

function normalizarBusca(valor: string): string {
  return valor
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLocaleLowerCase("pt-BR")
    .replace(/\s+/g, " ")
    .trim();
}

function Cartao({ c }: { c: Calc }) {
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
    <Link to={`/calculadoras/${c.slug}`} className="cartao cartao--clinico" style={{ color: "inherit" }}>
      {corpo}
    </Link>
  ) : (
    <div className="cartao" style={{ opacity: 0.7 }}>{corpo}</div>
  );
}

export default function Calculadoras() {
  const [lista, setLista] = useState<Calc[] | null>(null);
  const [busca, setBusca] = useState("");
  // Pedido do Rafael, 07/08/2026: toda busca do site precisa de pelo menos
  // duas formas de refinar — mesmo padrão já usado em Apresentação e Modo
  // Emergência. Aqui: texto livre + tema, 100% client-side (a lista inteira
  // já está carregada).
  const [tema, setTema] = useState("");

  useEffect(() => { api.get<Calc[]>("/calculators").then(setLista); }, []);

  const temas = useMemo(() => {
    const contagem = new Map<string, number>();
    (lista || []).forEach((c) => contagem.set(c.theme, (contagem.get(c.theme) ?? 0) + 1));
    return [...contagem.entries()].sort((a, b) => a[0].localeCompare(b[0], "pt-BR"));
  }, [lista]);

  const filtradas = useMemo(() => {
    const termos = normalizarBusca(busca).split(" ").filter(Boolean);
    return (lista || []).filter((c) => {
      if (tema && c.theme !== tema) return false;
      if (termos.length === 0) return true;
      const texto = normalizarBusca([c.name, c.theme, c.purpose].join(" "));
      return termos.every((t) => texto.includes(t));
    });
  }, [lista, busca, tema]);

  if (!lista) return <Carregando />;

  const doses = filtradas.filter((c) => c.kind === "dose");
  const escores = filtradas.filter((c) => c.kind !== "dose");

  // Agrupa as calculadoras de dose por área (Cardiologia Geral, Cardiologia
  // Pediátrica, Medicina Intensiva — cobertura inicial pedida pelo Rafael),
  // extraindo a área do próprio `theme` ("Doses — <Área>"), sem precisar de
  // campo novo no schema.
  const dosesPorArea = new Map<string, Calc[]>();
  for (const c of doses) {
    const area = c.theme.startsWith(PREFIXO_DOSE) ? c.theme.slice(PREFIXO_DOSE.length) : c.theme;
    dosesPorArea.set(area, [...(dosesPorArea.get(area) ?? []), c]);
  }

  return (
    <>
      <p className="eyebrow">Escores clínicos e doses</p>
      <h1>Calculadoras</h1>
      <p style={{ color: "var(--texto-secundario)", maxWidth: "60ch" }}>
        Cada escore mostra a referência original e as limitações de aplicação. Escores cujos
        coeficientes oficiais ainda não foram conferidos ficam bloqueados até a validação.
      </p>

      <div className="cartao" style={{ marginTop: "1rem", padding: "1rem" }}>
        <label htmlFor="busca-calculadoras" style={{ display: "block", marginBottom: "0.4rem", fontWeight: 700 }}>
          Buscar calculadora
        </label>
        <div style={{ display: "flex", gap: "0.6rem", flexWrap: "wrap" }}>
          <input
            id="busca-calculadoras"
            type="search"
            value={busca}
            onChange={(e) => setBusca(e.target.value)}
            placeholder="Ex.: TIMI, TFG, noradrenalina, pediátrica"
            autoComplete="off"
            spellCheck={false}
            style={{ flex: "1 1 260px", minWidth: 0 }}
          />
          <select
            id="tema-calculadoras"
            aria-label="Filtrar por tema"
            value={tema}
            onChange={(e) => setTema(e.target.value)}
            style={{ flex: "1 1 220px", minWidth: 0 }}
          >
            <option value="">Todos os temas ({lista.length})</option>
            {temas.map(([nome, contagem]) => (
              <option key={nome} value={nome}>{nome} ({contagem})</option>
            ))}
          </select>
        </div>
        <small style={{ display: "block", marginTop: "0.5rem", color: "var(--texto-secundario)" }}>
          {filtradas.length} de {lista.length} calculadora(s)
        </small>
      </div>

      {doses.length > 0 && (
        <section style={{ marginTop: "1.6rem" }}>
          <p className="eyebrow" style={{ marginBottom: "0.2rem" }}>Função nova</p>
          <h2 style={{ margin: "0 0 0.3rem" }}>Calculadora de Doses Cardiológicas</h2>
          <p style={{ color: "var(--texto-secundario)", maxWidth: "70ch", marginTop: 0 }}>
            Dose, taxa de infusão (mL/h e gotas/min) e energia de choque a partir do peso do
            paciente e da diluição preparada — cobertura inicial em Cardiologia Geral,
            Cardiologia Pediátrica e Medicina Intensiva. Cada resultado avisa quando a dose
            informada sai da faixa usual, mas nunca bloqueia: a decisão é sempre do médico.
          </p>
          {[...dosesPorArea.entries()].map(([area, itens]) => (
            <div key={area} style={{ marginTop: "1rem" }}>
              <h3 style={{ fontSize: "1rem", margin: "0 0 0.6rem" }}>{area}</h3>
              <div className="grade grade--2">
                {itens.map((c) => <Cartao key={c.slug} c={c} />)}
              </div>
            </div>
          ))}
        </section>
      )}

      <section style={{ marginTop: "1.8rem" }}>
        {doses.length > 0 && <h2 style={{ fontSize: "1.05rem" }}>Escores clínicos</h2>}
        <div className="grade grade--2" style={{ marginTop: "1.2rem" }}>
          {escores.map((c) => <Cartao key={c.slug} c={c} />)}
        </div>
        {filtradas.length === 0 && (
          <p className="aviso" style={{ marginTop: "1rem" }}>
            Nenhuma calculadora encontrada para “{busca.trim()}”{tema ? ` em ${tema}` : ""}.
          </p>
        )}
      </section>
    </>
  );
}
