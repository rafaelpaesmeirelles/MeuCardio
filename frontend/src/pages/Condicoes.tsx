import { useEffect, useState } from "react";
import { api } from "../lib/api";
import { Carregando, Erro } from "../components/Estado";

type Item = { slug: string; nome: string };

type Achado = {
  farmaco: Item;
  condicao: string;
  condicao_rotulo: string;
  campo_proprio: string | null;
  contraindicacoes_citando: string[];
  review_status: string;
};

type Ausencia = { farmaco: Item; condicao: string; condicao_rotulo: string };

type Resultado = { achados: Achado[]; sem_informacao: Ausencia[]; aviso: string };

const CONDICOES = [
  { id: "gestacao", rotulo: "Gestação" },
  { id: "lactacao", rotulo: "Lactação" },
  { id: "renal", rotulo: "Doença renal crônica" },
  { id: "hepatica", rotulo: "Hepatopatia" },
];

export default function Condicoes() {
  const [lista, setLista] = useState<Item[] | null>(null);
  const [farmacos, setFarmacos] = useState<string[]>([]);
  const [condicoes, setCondicoes] = useState<string[]>([]);
  const [busca, setBusca] = useState("");
  const [resultado, setResultado] = useState<Resultado | null>(null);
  const [erro, setErro] = useState("");
  const [checando, setChecando] = useState(false);

  useEffect(() => {
    api.get<{ slug: string; generic_name: string }[]>("/drugs")
      .then((l) => setLista(l.map((d) => ({ slug: d.slug, nome: d.generic_name }))))
      .catch((e) => setErro(e.message));
  }, []);

  function alternar(lst: string[], set: (v: string[]) => void, v: string) {
    setResultado(null);
    set(lst.includes(v) ? lst.filter((x) => x !== v) : [...lst, v]);
  }

  async function checar() {
    setChecando(true);
    setErro("");
    try {
      setResultado(
        await api.post<Resultado>("/drugs/condicoes", { slugs: farmacos, condicoes }),
      );
    } catch (e: any) {
      setErro(e.message);
    } finally {
      setChecando(false);
    }
  }

  if (erro && !lista) return <Erro mensagem={erro} />;
  if (!lista) return <Carregando />;

  const filtrada = busca
    ? lista.filter((d) => d.nome.toLowerCase().includes(busca.toLowerCase()))
    : lista;
  const nomeDe = (s: string) => lista.find((d) => d.slug === s)?.nome ?? s;

  return (
    <>
      <p className="eyebrow">Medicamentos</p>
      <h1>Alerta por condição especial</h1>
      <p style={{ maxWidth: "68ch", color: "var(--texto-secundario)" }}>
        Cruza o que você vai prescrever com a condição do paciente. Diferente do
        checador de interação, que é fármaco × fármaco, aqui é{" "}
        <strong>fármaco × condição</strong>.
      </p>

      <div className="cartao" style={{ marginTop: "1rem" }}>
        <strong>Condições do paciente</strong>
        <div className="painel__temas" style={{ marginTop: "0.4rem" }}>
          {CONDICOES.map((c) => (
            <button
              key={c.id}
              className="painel__tema"
              onClick={() => alternar(condicoes, setCondicoes, c.id)}
              style={condicoes.includes(c.id) ? { borderColor: "var(--acento)" } : undefined}
            >
              {c.rotulo}
            </button>
          ))}
        </div>

        <label htmlFor="busca-cond" style={{ display: "block", marginTop: "0.9rem" }}>
          <strong>Medicamentos</strong>
        </label>
        <input
          id="busca-cond"
          value={busca}
          onChange={(e) => setBusca(e.target.value)}
          placeholder="Filtrar pelo nome…"
          style={{ marginTop: "0.4rem" }}
        />
        {farmacos.length > 0 && (
          <div className="painel__temas" style={{ marginTop: "0.6rem" }}>
            {farmacos.map((s) => (
              <button key={s} className="painel__tema" onClick={() => alternar(farmacos, setFarmacos, s)}>
                {nomeDe(s)} <span className="dado">✕</span>
              </button>
            ))}
          </div>
        )}
        <div
          style={{
            marginTop: "0.6rem", maxHeight: "12rem", overflowY: "auto",
            display: "flex", flexWrap: "wrap", gap: "0.35rem",
          }}
        >
          {filtrada.map((d) => (
            <button
              key={d.slug}
              className="painel__tema"
              onClick={() => alternar(farmacos, setFarmacos, d.slug)}
              style={farmacos.includes(d.slug) ? { borderColor: "var(--acento)" } : undefined}
            >
              {d.nome}
            </button>
          ))}
        </div>

        <button
          className="botao"
          style={{ marginTop: "0.8rem" }}
          disabled={!farmacos.length || !condicoes.length || checando}
          onClick={checar}
        >
          {checando ? "Checando…" : "Checar"}
        </button>
      </div>

      {erro && <Erro mensagem={erro} />}

      {resultado && (
        <>
          <section className="painel__grupo">
            <h2>O que os verbetes dizem</h2>
            {resultado.achados.length === 0 ? (
              <p style={{ fontSize: "0.88rem", color: "var(--texto-secundario)" }}>
                Nenhum achado — veja o bloco abaixo antes de concluir qualquer coisa.
              </p>
            ) : (
              <div style={{ display: "grid", gap: "0.7rem" }}>
                {resultado.achados.map((a, i) => (
                  <article key={i} className="cartao painel__funcao painel__funcao--destaque">
                    <strong>
                      {a.farmaco.nome} · {a.condicao_rotulo}
                    </strong>
                    {a.campo_proprio && <span>{a.campo_proprio}</span>}
                    {a.contraindicacoes_citando.map((t, j) => (
                      <span key={j}>
                        <strong>Contraindicação:</strong> {t}
                      </span>
                    ))}
                    {a.review_status !== "revisado" && (
                      <span style={{ fontSize: "0.78rem" }}>
                        Verbete com revisão <strong>{a.review_status}</strong>.
                      </span>
                    )}
                  </article>
                ))}
              </div>
            )}
          </section>

          {resultado.sem_informacao.length > 0 && (
            <section className="painel__grupo">
              <h2>Sem informação no verbete</h2>
              <p className="painel__grupo-sub">
                <strong>Isto não é atestado de segurança.</strong> É ausência de dado —
                ninguém afirmou que pode usar.
              </p>
              <div className="painel__temas">
                {resultado.sem_informacao.map((s, i) => (
                  <span key={i} className="painel__tema">
                    {s.farmaco.nome} · {s.condicao_rotulo}
                  </span>
                ))}
              </div>
            </section>
          )}

          <p
            className="cartao"
            style={{ marginTop: "1rem", fontSize: "0.85rem", color: "var(--texto-secundario)" }}
          >
            {resultado.aviso}
          </p>
        </>
      )}
    </>
  );
}
